import os
import math
import random
import ctypes
import logging
import numpy as np
import itertools
import matplotlib.pyplot as plt
from IPython import embed
import ROOT

path = os.path.abspath(os.path.dirname(__file__))
ROOT.gInterpreter.ProcessLine(f'#include "{os.path.join(path,"th1fmorph_2param.cc")}"')

class Interpolation:
    def __init__(self,p1,p2,p3,pinterp):
        if isinstance(p1,list) or isinstance(p1,tuple):
            assert len(p1) == 2
            self.p1 = np.array(p1,np.float64)
        elif isinstance(p1,np.ndarray):
            self.p1 = p1.astype(np.float64)
        else:
            raise RuntimeError(f'p1 must be either a list of numpy array, you provided {type(p1)}')
        if isinstance(p2,list) or isinstance(p2,tuple):
            assert len(p2) == 2
            self.p2 = np.array(p2,np.float64)
        elif isinstance(p2,np.ndarray):
            self.p2 = p2.astype(np.float64)
        else:
            raise RuntimeError(f'p2 must be either a list of numpy array, you provided {type(p2)}')
        if isinstance(p3,list) or isinstance(p3,tuple):
            assert len(p3) == 2
            self.p3 = np.array(p3,np.float64)
        elif isinstance(p3,np.ndarray):
            self.p3 = p3.astype(np.float64)
        else:
            raise RuntimeError(f'p3 must be either a list of numpy array, you provided {type(p3)}')

        if isinstance(pinterp,list) or isinstance(pinterp,tuple):
            assert len(pinterp) == 2
            self.pinterp = np.array(pinterp,np.float64)
        elif isinstance(pinterp,np.ndarray):
            self.pinterp = pinterp.astype(np.float64)
        else:
            raise RuntimeError(f'pinterp must be either a list of numpy array, you provided {type(pinterp)}')


    def __call__(self,h1,h2,h3,name):
        if h1.__class__.__name__.startswith('TH1') and h2.__class__.__name__.startswith('TH1') and h3.__class__.__name__.startswith('TH1'):
            # Interpolate 1D #
            hinterp = ROOT.th1fmorph_2param(name,name, h1, h2, h3, self.p1, self.p2, self.p3, self.pinterp, -1,0)
            # Adapt errors #
            NBins = hinterp.GetXaxis().GetNbins()
            for i in range(NBins):
                print(i+1, hinterp.GetBinContent(i))
            error = ctypes.c_double(0.)
            norm = hinterp.IntegralAndError(1,hinterp.GetNbinsX(),error)
            
            return hinterp
        else:
            raise RuntimeError(f"Could not find interpolation method for h1 of class {h1.__class__.__name__} and h2 of class {h2.__class__.__name__}")



INT_MAX = 1000000
class Polygon:
    """
        Adapted from https://www.geeksforgeeks.org/how-to-check-if-a-given-point-lies-inside-a-polygon/
    """
    def __init__(self,points):
        self.points = points
        self.trials = []
        self.results = []

    def onSegment(self,p:tuple, q:tuple, r:tuple) -> bool:
        """
            Given three collinear points p, q, r,
            the function checks if point q lies
            on line segment 'pr'
        """
        if ((q[0] <= max(p[0], r[0])) &
            (q[0] >= min(p[0], r[0])) &
            (q[1] <= max(p[1], r[1])) &
            (q[1] >= min(p[1], r[1]))):
            return True

        return False

    def orientation(self,p:tuple, q:tuple, r:tuple) -> int:
        """
            To find orientation of ordered triplet (p, q, r). 
            The function returns following values
            0 --> p, q and r are collinear
            1 --> Clockwise
            2 --> Counterclockwise
        """
        val = (((q[1] - p[1]) * (r[0] - q[0])) - ((q[0] - p[0]) * (r[1] - q[1])))

        if val == 0:
            return 0
        if val > 0:
            return 1 # Collinear
        else:
            return 2 # Clock or counterclock

    def doIntersect(self,p1, q1, p2, q2):

        # Find the four orientations needed for
        # general and special cases
        o1 = self.orientation(p1, q1, p2)
        o2 = self.orientation(p1, q1, q2)
        o3 = self.orientation(p2, q2, p1)
        o4 = self.orientation(p2, q2, q1)

        # General case
        if (o1 != o2) and (o3 != o4):
            return True

        # Special Cases
        # p1, q1 and p2 are collinear and
        # p2 lies on segment p1q1
        if (o1 == 0) and (self.onSegment(p1, p2, q1)):
            return True

        # p1, q1 and p2 are collinear and
        # q2 lies on segment p1q1
        if (o2 == 0) and (self.onSegment(p1, q2, q1)):
            return True

        # p2, q2 and p1 are collinear and
        # p1 lies on segment p2q2
        if (o3 == 0) and (self.onSegment(p2, p1, q2)):
            return True

        # p2, q2 and q1 are collinear and
        # q1 lies on segment p2q2
        if (o4 == 0) and (self.onSegment(p2, q1, q2)):
            return True

        return False

    def is_inside(self, point:tuple) -> bool:
        self.trials.append(point)
        result = self._is_inside(point)
        self.results.append(result)
        return result

    def _is_inside(self, point:tuple) -> bool:
        """
            Returns true if the point p lies
            inside the polygon with n vertices
        """
        n = len(self.points)

        # There must be at least 3 vertices
        # in polygon
        if n < 3:
            return False

        # Create a point for line segment
        # from p to infinite
        extreme = (INT_MAX, point[1])
        count = i = 0

        while True:
            next = (i + 1) % n

            # Check if the line segment from 'point' to
            # 'extreme' intersects with the line
            # segment from 'polygon[i]' to 'polygon[next]'
            if (self.doIntersect(self.points[i],self.points[next],point, extreme)):

                # If the point 'point' is collinear with line
                # segment 'i-next', then check if it lies
                # on segment. If it lies, return true, otherwise false
                if self.orientation(self.points[i], point, self.points[next]) == 0:
                    return self.onSegment(self.points[i], point, self.points[next])
            count += 1
            i = next
            if (i == 0):
                break

        # Return true if count is odd, false otherwise
        return (count % 2 == 1)

    def draw(self,name):
        fig = plt.figure(figsize=(9,9))
        plt.scatter(x      = [p[0] for p in self.points],
                    y      = [p[1] for p in self.points],
                    color  = 'b',
                    marker = 'o',
                    facecolors = 'none',
                    s      = 100)
        for p,r in zip(self.trials,self.results):
            if r:
                color = 'g'
            else:
                color= 'r'
            plt.scatter(p[0],p[1],color=color,s=20)
        fig.savefig(name)
        


class Triangle(Polygon):
    def _is_inside(self, point:tuple) -> bool:
        assert len(self.points) == 3
        x1 = self.points[0][0]
        y1 = self.points[0][1]
        x2 = self.points[1][0]
        y2 = self.points[1][1]
        x3 = self.points[2][0]
        y3 = self.points[2][1]
        x = point[0]
        y = point[1]
        # If two same points, return False #
        if (x1 == x2 and y1 == y2) or (x2 == x3 and y2 == y3) or (x1 == x3 and y1 == y3):
            return False
        # If same x or y, return False #
        if (x1 == x2 and x2 == x3) or (y1 == y2 and y2 == y3):
            return False
        # Check if points are on a line #
        m12 = abs((y2-y1)/(x2-x1)) if x2 != x1 else np.inf
        m23 = abs((y3-y2)/(x3-x2)) if x3 != x2 else np.inf
        if np.isclose(m12,m23): 
            return False

        # Compute coefficients #
        a = round(((y2 - y3)*(x - x3) + (x3 - x2)*(y - y3)) / ((y2 - y3)*(x1 - x3) + (x3 - x2)*(y1 - y3)),9)
        b = round(((y3 - y1)*(x - x3) + (x1 - x3)*(y - y3)) / ((y2 - y3)*(x1 - x3) + (x3 - x2)*(y1 - y3)),9)
        c = round(1 - a - b,9)
    
        return a >= 0 and b >= 0 and c >= 0 and a <= 1 and b <= 1 and c <= 1
        


class PointFinder:
    def __init__(self,points,verbose=False):
        self.points = np.array(points)
        assert self.points.ndim == 2
        assert self.points.shape[1] == 2
        self.triplet = None
        self.point = None
        self.verbose = verbose

    def find_triangle(self,point):
        self.point = point
        try:
            self.triplet = self._find_triangle(point) 
        except Exception as e:
            self.triplet = None
            raise e

        return self.triplet        

    def _find_triangle(self,point):
        if self.verbose:
            print (f'Looking at point {point}')
        point = np.array(point)
        # Compute distances #
        distances = np.sqrt(((self.points-point)**2).sum(axis=1))
        # Order the points #
        order = np.argsort(distances)
        points = self.points[order]
        distances = distances[order]
        # Start the loop #
        N_edges = 3 # start with the first 3 points 
        final_triplet = None
        while final_triplet is None:
            # Check for infinite loop #
            if N_edges > points.shape[0]:
                raise RuntimeError(f'Could not find triangle for point {point}')
            # Make triplets of points, then triangles #
            test_points = points[:N_edges] # test points
            triplets = list(itertools.combinations(test_points,3))
            if self.verbose:
                print (f'Attempt with {N_edges} points -> {len(triplets)} combinations')
                for p,dist in zip(test_points,distances[:N_edges]):
                    print (f'... {p} -> dist : {dist}')
            # Check which triangles contain the point #
            triplets_passing = [triplet for triplet in triplets     
                                if Triangle(triplet).is_inside(point)] 
            # Check if any, take the best #
            if len(triplets_passing) > 0:
                # Get total distance from point #
                tri_dist = [sum([np.sqrt((((edge-point)**2).sum())) for edge in triplet])
                                for triplet in triplets_passing]
                if self.verbose:
                    print (f'-> Found {len(triplets_passing)} triangle candidates')
                    for triplet,dist in zip(triplets_passing,tri_dist):
                        print (f'... {triplet} -> total distance = {dist}')
                # Find the triple with minimal total distance #
                final_triplet = triplets_passing[np.argsort(tri_dist)[0]]

            # In case not found, check larger number of edges #
            N_edges += 1

        if final_triplet is None:
            raise RuntimeError('Something is wrong here ...')

        if self.verbose:
            print (f'Final selected triplet : {final_triplet}')

        return final_triplet
    
    def draw(self,name):
        fig = plt.figure(figsize=(9,9))
        # draw all grid of points #
        plt.scatter(x      = [p[0] for p in self.points],
                    y      = [p[1] for p in self.points],
                    color  = 'b',
                    marker = 'o',
                    label  = 'All points',
                    s      = 50)
        # Emphasize the chosen ones #
        if self.triplet is not None:
            plt.scatter(x      = [p[0] for p in self.triplet],
                        y      = [p[1] for p in self.triplet],
                        color  = 'g',
                        marker = 'o',
                        facecolors='none',
                        label  = 'Triangle',
                        s      = 200)
        # Plot requested point #
        plt.scatter(x      = self.point[0],
                    y      = self.point[1],
                    color  = 'r',
                    marker = 'o',
                    label  = 'Requested point',
                    s      = 100)
        # Compute min-max ranges #
        # Legend and save #
        plt.legend()
        fig.savefig(name)
        


# Driver code
if __name__ == '__main__':

    # Test of finder #
    masspoints = [[200,50], [300,50], [350,50], [400,50], [200,100], [300,100], [400,100], [300,200], [400,200] , [400,300]]

    finder = PointFinder(masspoints)
    print (finder.find_triangle([250,70]))
    finder.draw("test_finder.png")

    # Test of triangle and polynom #
    triangle = Triangle([ (0, 0), (10,0), (5,10) ])
    polygon = Polygon([ (0, 0), (10, 0), (10, 10), (0, 10) ])
    for _ in range(1000):
        x = random.randrange(-5,15)
        y = random.randrange(-5,15)
        polygon.is_inside((x,y))
        triangle.is_inside((x,y))
    polygon.draw('test_polygon.png')
    triangle.draw('test_triangle.png')
