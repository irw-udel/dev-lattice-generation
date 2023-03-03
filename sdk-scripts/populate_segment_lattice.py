"""Convert lattice to points for meshing
    Inputs:
        curves: Curves that make up the lattice
        radius: Minimum radius value for generating mesh
    Output:
        points: Points to input to lattice meshing component"""

__author__ = "irw"
__version__ = "2022.03.23"

from ghpythonlib.componentbase import executingcomponent as component
import Grasshopper, GhPython
import System
import Rhino
import rhinoscriptsyntax as rs
import ghpythonlib.components as ghcomp
import ghpythonlib.parallel
import ghpythonlib.treehelpers as th

def segment_curves_parallel(curve):
    params = curve.DivideByLength(segment_length, False)
    points = []
    points.append(curve.PointAtStart)
    try:
        for t in params:
            points.append(curve.PointAt(t))
    except:
        pass
    points.append(curve.PointAtEnd)
    return points

class SegmentLattice(component):
    def RunScript(self, curves, radius):
        global segment_length 
        segment_length = float(radius)/5
        
        if curves:
            points = ghpythonlib.parallel.run(segment_curves_parallel, curves, True)

        return points