#
# Minecraft Maze: Export a 2D or 3D mazes for Minecraft using Mazecraft
# 
# (c) 2011 Lee Supe, Shea Watson
#

import nbt
import os

from mazecraft import Maze

MINECRAFT_WORLDPATH = os.path.expanduser ('~lainproliant/Library/Application Support/minecraft/saves/World5/')
MINECRAFT_BRICK     = chr (45)
MINECRAFT_GLOWSTONE = chr (89)
MINECRAFT_EMPTY     = chr (0)

MINECRAFT_MAZE_PATH_EAST      = 2 ** 0
MINECRAFT_MAZE_PATH_WEST      = 2 ** 1
MINECRAFT_MAZE_PATH_NORTH     = 2 ** 2
MINECRAFT_MAZE_PATH_SOUTH     = 2 ** 3
MINECRAFT_MAZE_PATH_DOWN      = 2 ** 4
MINECRAFT_MAZE_PATH_UP        = 2 ** 5

MINECRAFT_MAZE_ROOM_WIDTH     = 2

def toBase36(number):

   alphabet='0123456789abcdefghijklmnopqrstuvwxyz'
   newn = abs(number)

        # Special case for zero
   if number == 0:
      return '0'

   # Basic base36 alg
   base36 = ''
   while newn != 0:
      newn, i = divmod(newn, len(alphabet))
      base36 = alphabet[i] + base36

   if number < 0:
      return "-" + base36
   else:
      return base36


def getNBTFileFromChunk(worldPath, chunk):

   nb = None

   (Xc, Zc) = chunk

   fileName = "c." + toBase36(Xc) + "." + toBase36(Zc) + ".dat"
   firstFolder = toBase36(Xc % 64)
   secondFolder = toBase36(Zc % 64)
   chunkPath = worldPath +  firstFolder + '/' + secondFolder + '/' + fileName;
   nbtFile = nbt.NBTFile(chunkPath,'rb')
   blockdata = list(nbtFile['Level']['Blocks'].value)
   return (nbtFile,blockdata,fileName)


def chunkIndex (x, z, y):
   """
      Convert the given world coordinates to chunk coordinates
      and block data indices.
   """

   xC = x / 16
   zC = z / 16
   xP = x % 16
   zP = z % 16

   return ((xC, zC), y + (zP * 128) + (xP * 128 * 16))


def blockSet (chunks, x, z, y, blockChar):
   """
      Sets the block at the given offset in a set of
      edited chunks.
   """

   chunk, idx = chunkIndex (x, z, y)

   if not chunks.has_key (chunk):
      chunks [chunk] = []

   chunks [chunk].append ((idx, blockChar))


def editChunk (worldPath, chunk, blocks, backup = False):
   """
      Edits the given chunk with the given list of modifications.
   """
   
   nbtfile, blockString, fileName = getNBTFileFromChunk (worldPath, chunk)
   blockdata = list (blockString)

   print 'LRS-DEBUG: Writing Chunk %s @ %s' % (str (chunk), fileName)

   for idx, block in blocks:
      blockdata [idx] = block

   nbtfile ['Level']['Blocks'].value = ''.join (blockdata)
   nbtfile.write_file ()


def debug_renderColumn (x, z):
   """
      LRS-DEBUG
      Renders a column at the given x and z coordinates.
   """
   
   chunks = {}

   for y in range (128):
      chunk, idx = chunkIndex (x, z, y)

      if not chunks.has_key (chunk):
         chunks [chunk] = []

      chunks [chunk].append ((idx, MINECRAFT_BRICK))

   for chunk, blocks in chunks.iteritems ():
      editChunk (chunk, blocks)


class MinecraftMaze (Maze):
   """
      A 3D Maze for Minecraft.
   """

   def __init__ (self, roomWidth, xWidth, zBreadth, yHeight = 1):
      """
         Initializes a new MinecraftMaze.
      """

      Maze.__init__ (self, (xWidth, zBreadth, yHeight))
      self.roomWidth = roomWidth


   def clearMaze (self, worldPath, clearBlock, x0, z0, y0):
      """
         This is a false renderer.  It simply draws a large
         rectangle the size of the maze.
      """

      # LRS-TODO: This is a false renderer.  It simply draws
      # a large rectangle, the size of the maze.

      chunks = {}

      for x in range (self.dimensions [0] * (self.roomWidth + 1) + 1):
         for z in range (self.dimensions [1] * (self.roomWidth + 1) + 1):
            for y in range (self.dimensions [2] * (self.roomWidth + 1) + 1):
               chunk, idx = chunkIndex (x + x0, z + z0, y + y0)

               if not chunks.has_key (chunk):
                  chunks [chunk] = set ()

               chunks [chunk].add ((idx, clearBlock))
      
      print 'LRS-DEBUG: chunks = %s' % str (chunks.keys ())

      for chunk, blocks in chunks.iteritems ():
         editChunk (worldPath, chunk, blocks)

   
   def renderMaze (self, worldPath, x0, z0, y0):
      """
         Render a maze in Minecraft level data with the origin
         about (x, z, y).
      """

      chunks = {}

      for x in range (self.dimensions [0]):
         for z in range (self.dimensions [1]):
            for y in range (self.dimensions [2]):
               self._renderMazeRoom (chunks, (x, z, y), x0, z0, y0)
      
      print 'LRS-DEBUG: chunks = %s' % str (chunks.keys ())

      for chunk, blocks in chunks.iteritems ():
         editChunk (worldPath, chunk, blocks)
   

   def _renderMazeRoom (self, chunks, roomCoords, x0, z0, y0):
      """
         Render the given cell of the maze to the chunks
         dictionary provided.

         For internal use only.  Does not save to Minecraft level data.
      """

      # Draw the walls of the room based on the path flags for the cell.
      cell = self.cellAt (roomCoords)
      
      x = x0 + (roomCoords [0] * (self.roomWidth + 1))
      z = z0 + (roomCoords [1] * (self.roomWidth + 1))
      y = y0 + (roomCoords [2] * (self.roomWidth + 1))

      #blockSet (chunks, x, z, y, MINECRAFT_GLOWSTONE)
      
      if not cell.paths & MINECRAFT_MAZE_PATH_WEST:
         for dz in range (self.roomWidth + 2):
            for dy in range (self.roomWidth + 2):
               blockSet (chunks, x, z + dz, y + dy, MINECRAFT_GLOWSTONE)

      if not cell.paths & MINECRAFT_MAZE_PATH_EAST:
         for dz in range (self.roomWidth + 2):
            for dy in range (self.roomWidth + 2):
               blockSet (chunks, x + self.roomWidth + 1, z + dz, y + dy, MINECRAFT_GLOWSTONE)

      if not cell.paths & MINECRAFT_MAZE_PATH_SOUTH:
         for dx in range (self.roomWidth + 2):
            for dy in range (self.roomWidth + 2):
               blockSet (chunks, x + dx, z, y + dy, MINECRAFT_GLOWSTONE)
         
      if not cell.paths & MINECRAFT_MAZE_PATH_NORTH:
         for dx in range (self.roomWidth + 2):
            for dy in range (self.roomWidth + 2):
               blockSet (chunks, x + dx, z + self.roomWidth + 1, y + dy, MINECRAFT_GLOWSTONE)

      if not cell.paths & MINECRAFT_MAZE_PATH_UP:
         for dz in range (self.roomWidth + 2):
            for dx in range (self.roomWidth + 2):
               blockSet (chunks, x + dx, z + dz, y, MINECRAFT_GLOWSTONE)
         
      if not cell.paths & MINECRAFT_MAZE_PATH_DOWN:
         for dz in range (self.roomWidth + 2):
            for dx in range (self.roomWidth + 2):
               blockSet (chunks, x + dx, z + dz, y + self.roomWidth + 1, MINECRAFT_GLOWSTONE)


def main (argv):
   # LRS-TEST: Let's generate fixed mazes for now.
   # Then, we can try some other things.

   mazeOrigin = (280, 197, 65)
   
   maze = MinecraftMaze (MINECRAFT_MAZE_ROOM_WIDTH, 5, 5, 5)
   maze.clearMaze (MINECRAFT_WORLDPATH, MINECRAFT_EMPTY, *mazeOrigin)
   if not 'just_clear' in argv:
      maze.growingTree ()
      maze.renderMaze (MINECRAFT_WORLDPATH, *mazeOrigin)

if __name__ == "__main__":
   import sys
   main (sys.argv [1:])

