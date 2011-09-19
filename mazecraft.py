#
# Mazecraft: 2D and 3D Maze Generation for Minecraft
#
# (c) 2011 Lee Supe (lain_proliant)
# Released for the GNU General Public License
#

import random

def pathFlagsFromDiffCoords (diffCoords):
   """
      Computes forward and backward path flags for the given
      difference between coordinates.
   """

   pathFlags = 0
   invFlags = 0

   for R, n in enumerate (diffCoords):
      if n > 0:
         pathFlags |= (2 ** (2 * R))
         invFlags |= (2 ** (2 * R + 1))

      elif n < 0:
         pathFlags |= (2 ** (2 * R + 1))
         invFlags |= (2 ** (2 * R))


   return pathFlags, invFlags


class Cell (object):

   def __init__ (self, maze, coords):

      self.maze = maze
      self.coords = coords
      self.paths = 0
      self.visited = False


   def adjacent (self):
      """
         Returns a list of all adjacent cells.
      """

      cells = []
      
      for R, coord in enumerate (self.coords):
         if coord + 1 < self.maze.dimensions [R]:
            adjCoords = list (self.coords)
            adjCoords [R] = coord + 1

            cells.append (self.maze.cellAt (adjCoords))

         if coord - 1 >= 0:
            adjCoords = list (self.coords)
            adjCoords [R] = coord - 1

            cells.append (self.maze.cellAt (adjCoords))

      return cells


   def adjacentUnvisited (self):
      """
         Returns a list of all adjacent, unvisited cells.
      """

      return [c for c in self.adjacent () if not c.visited]


   def diffCoords (self, cell):
      """
         Computes the component difference between this cell and the
         specified cell.
      """

      return [b - a for a, b in zip (self.coords, cell.coords)]


   def carveTo (self, destCell):
      """
         Adds paths to this cell and the destination to allow for passage.
      """
      
      diffCoords = self.diffCoords (destCell)
      pathFlags, invFlags = pathFlagsFromDiffCoords (diffCoords)

      self.paths |= pathFlags
      destCell.paths |= invFlags
               

   def __repr__ (self):

      return '<Cell %s %s>' % (str (self.coords), bin (self.paths))


class Maze (list):
   
   def __init__ (self, dimensions, ancestor = None, subdimension = ()):

      self.dimensions = dimensions

      for n in range (dimensions [0]):
         if ancestor is not None:
            maze = ancestor

         else:
            maze = self
               
         if len (dimensions) > 1:
            self.append (Maze (dimensions [1:], maze, subdimension + (n,)))

         else:
            self.append (Cell (maze, subdimension + (n,)))


   def cellAt (self, coords):
      """
         Retrieves the cell at the given coordinates.
      """
      
      if len (self.dimensions) > 1:
         return self [coords [0]].cellAt (coords [1:])

      else:
         return self [coords [0]]


   def randomCell (self):
      """
         Returns a random cell from the maze.
      """

      return self.cellAt ([random.randint (0, n - 1) for n in self.dimensions])


   def chaoticPath (self):
      """
         Carves a random chaotic path from 0,0 center until reaching a dead end. 
      """
      
      cell = self.cellAt ([0 for x in self.dimensions])
      
      while cell.adjacentUnvisited ():
         nextCell = random.choice (cell.adjacentUnvisited ())
         cell.carveTo (nextCell)

         cell = nextCell
         cell.visited = True

   
   def growingTree (self, probabilityNew = 1.0):
      """
         Carves a maze using the growing tree algorithm
         with the specified parameters.
      """
      
      cell = self.randomCell ()
      cell.visited = True
      stack = [cell]

      while stack:
         if random.random () > probabilityNew:
            cell = random.choice (stack)

         else:
            cell = stack [-1]


         adjacentCells = cell.adjacentUnvisited ()

         if not adjacentCells:
            stack.remove (cell)
            continue

         destCell = random.choice (adjacentCells)
         destCell.visited = True
         cell.carveTo (destCell)
         stack.append (destCell)


   def print2D (self):
      """
         Prints the maze as text.  It must be in two dimensions.
      """

      if not len (self.dimensions) == 2:
         raise Exception, "Maze is not two-dimensional."
      
      # Print the top line.
      line = ' '
      for x in range (self.dimensions [0]):
         cell = self.cellAt ((x, 0))

         if cell.paths & (2 ** (2 + 1)):
            line += '  '

         else:
            line += '_ '

      print line

      for y in range (self.dimensions [1]):
         line = ''

         for x in range (self.dimensions [0]):
            cell = self.cellAt ((x, y))
            
            if cell.paths & (2 ** (0 + 1)):
               line += ' '

            else:
               line += '|'
            
            if y == self.dimensions [1] - 1:
               if cell.paths & (2 ** 2):
                  line += ' '

               else:
                  line += '_'

            else:
               below = self.cellAt ((x, y + 1))

               if below.paths & 2 ** (2 + 1):
                  line += ' '

               else:
                  line += '_'

            if x == self.dimensions [0] - 1:
               if cell.paths & (2 ** 0):
                  line += ' '

               else:
                  line += '|'

         print line
         line = ' '

