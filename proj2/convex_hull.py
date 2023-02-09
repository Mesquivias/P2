from which_pyqt import PYQT_VER

if PYQT_VER == 'PYQT5':
    from PyQt5.QtCore import QLineF, QPointF, QObject
else:
    raise Exception('Unsupported Version of PyQt: {}'.format(PYQT_VER))

import time

# Some global color constants that might be useful
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)

# Global variable that controls the speed of the recursion automation, in seconds
#
PAUSE = 0.25


#
# This is the class you have to complete.
#
class ConvexHullSolver(QObject):

    # Class constructor
    def __init__(self):
        super().__init__()
        self.pause = False

    # Some helper methods that make calls to the GUI, allowing us to send updates
    # to be displayed.

    def showTangent(self, line, color):
        self.view.addLines(line, color)
        if self.pause:
            time.sleep(PAUSE)

    def eraseTangent(self, line):
        self.view.clearLines(line)

    def blinkTangent(self, line, color):
        self.showTangent(line, color)
        self.eraseTangent(line)

    def showHull(self, polygon, color):
        self.view.addLines(polygon, color)
        if self.pause:
            time.sleep(PAUSE)

    def eraseHull(self, polygon):
        self.view.clearLines(polygon)

    def showText(self, text):
        self.view.displayStatusText(text)

    # This is the method that gets called by the GUI and actually executes
    # the finding of the hull
    def compute_hull(self, points, pause, view):
        self.pause = pause
        self.view = view
        assert (type(points) == list and type(points[0]) == QPointF)

        t1 = time.time()
        # Sort the points by x-coordinate
        points.sort(key=lambda x: x.x())
        t2 = time.time()

        # I was not sure if I was supposed to put this call here (line 70)
        t3 = time.time()
        final_hull = self.divide_and_conquer(points)
        t4 = time.time()

        # Show the convex hull as a list of QLineF objects
        # I did not know how I would go about animating the solving of the convex hull,
        # that would probably add some more overhead and make things slower. However, I did not
        # go about doing that
        self.showHull([QLineF(final_hull[i], final_hull[(i + 1) % len(final_hull)]) for i in range(len(final_hull))],
                      GREEN)

        self.showText('Time Elapsed (Convex Hull): {:3.3f} sec'.format(t4 - t3))

    # Python was being annoying about making these next two methods static
    @staticmethod
    def cross_product(a, b, c):

        # Use the cross product because you have to
        return (b.x() - a.x()) * (c.y() - a.y()) - (c.x() - a.x()) * (b.y() - a.y())

    @staticmethod
    def calculate_slope(start, points):

        # Calculate slope to find left and right hulls.
        if start.x() == points.x():
            return float('inf')
        else:

            return (points.y() - start.y()) / (points.x() - start.x())

    def divide_and_conquer(self, points):

        # Divide the array in half
        mid = len(points) // 2

        # Set the points to be used for the left and right hulls
        left_hull = points[:mid]
        right_hull = points[mid:]

        # Set the start points for both of them
        left_hull_start = left_hull[0]
        right_hull_start = right_hull[0]

        # Use the slope to find each respective hull
        left_hull = left_hull[:1] + sorted(left_hull[1:], key=lambda p: self.calculate_slope(left_hull_start, p))
        right_hull = right_hull[:1] + sorted(right_hull[1:], key=lambda p: self.calculate_slope(right_hull_start, p))

        # Use the cross_product to compare first 2 points and calculate the third, value is popped off if
        # less than zero.
        Lhull = []

        for i in left_hull:
            while len(Lhull) >= 2 and self.cross_product(Lhull[-2], Lhull[-1], i) < 0:
                Lhull.pop()
            Lhull.append(i)

        Rhull = []

        for i in right_hull:
            while len(Rhull) >= 2 and self.cross_product(Rhull[-2], Rhull[-1], i) < 0:
                Rhull.pop()
            Rhull.append(i)

        # Calls merge to merge the left and right hulls
        final_hull = self.merge(Lhull, Rhull)

        return final_hull

    def merge(self, left_hull, right_hull):

        # Sets the convex hull to be the sum of the left and right hull
        convex_hull = left_hull + right_hull
        convex_hull = sorted(convex_hull, key=lambda p: (p.x(), p.y()))

        # Uses a similar method as in `divide_and_conquer` to compute upper hull
        upper = []

        for i in convex_hull:
            while len(upper) >= 2 and self.cross_product(upper[-2], upper[-1], i) < 0:
                upper.pop()
            upper.append(i)

        # Compute lower hull
        lower = []

        for i in reversed(convex_hull):
            while len(lower) >= 2 and self.cross_product(lower[-2], lower[-1], i) < 0:
                lower.pop()
            lower.append(i)

        # Remove duplicate end point
        return upper + lower
