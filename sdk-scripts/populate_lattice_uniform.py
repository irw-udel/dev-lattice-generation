"""Population for a uniform strut lattice
    Inputs:
        core_voxels: Voxels to populate with unit cell only
        boundary_voxels: Voxels to populate with unit cell and get connectivity
        unit_cell: Lines and curves making up the repeat unit
        connectivity: Unit cell connectivity
        primitive: Trimming boundary
    Output:
        lattice_core: Core voxels populated with unit cells
        lattice_boundary: Boundary voxels populated with unit cells
        lattice_trimmed: Trimmed lattice within primitive
        lattice_boundary_connect: Boundary voxels populated with connectivity
        lattice_skin: Net skin of the lattice"""

__author__ = "irw"
__version__ = "2022.01.31"

from ghpythonlib.componentbase import executingcomponent as component
import Grasshopper, GhPython
import System
import Rhino
import rhinoscriptsyntax as rs
import ghpythonlib.components as ghcomp
import ghpythonlib.parallel
import ghpythonlib.treehelpers as th

def get_bounding_box(unit_cell):
        precise_box = False
        unit_cell_bounds = unit_cell[0].GetBoundingBox(precise_box)
        for line in unit_cell:
            box = line.GetBoundingBox(precise_box)
            unit_cell_bounds = Rhino.Geometry.BoundingBox.Union(unit_cell_bounds, box)
        return unit_cell_bounds

def check_inclusion(lattice_curve, mesh):
    lattice_curve.Domain = Rhino.Geometry.Interval(0,1)
    midpoint = lattice_curve.PointAt(0.5)
    keep = mesh.IsPointInside(midpoint, 0.001, True)
    return keep

def check_curve_parallel(curve):
    curve = Rhino.Geometry.Curve.TryGetPolyline(curve)[1]
    curve = Rhino.Geometry.PolylineCurve(curve)
    intersection_points = Rhino.Geometry.Intersect.Intersection.MeshPolyline(primitive_global, curve)[0]
    if intersection_points:
        curve_params = []
        for point in intersection_points:
            curve_params.append(curve.ClosestPoint(point)[1])
        split_curve = curve.Split(curve_params)
        for section in split_curve:
            if (check_inclusion(section, primitive_global)):
                lattice_trimmed.append(section)
    else:
        if (check_inclusion(curve, primitive_global)):
            lattice_trimmed.append(curve)

def populate_lattice_parallel(voxels):
    lattice_structure = []
    for curve in unit_cell_global:
        mapped = ghcomp.BoxMapping(curve, unit_cell_bounds, voxels)[0]
        lattice_structure.append(mapped)
    return lattice_structure

def populate_connectivity_parallel(voxels):
    connect = ghcomp.BoxMapping(connectivity_global, unit_cell_bounds, voxels)[0]
    return connect

def populate_skin_parallel(voxels):
    connect = ghcomp.BoxMapping(connectivity_global, unit_cell_bounds, voxels)[0]
    # curves = Rhino.Geometry.Intersect.Intersection.MeshMeshAccurate(connect, primitive,  Rhino.RhinoMath.SqrtEpsilon*10)
    curves = ghcomp.MeshXMesh(primitive_global, connect)
    return curves


class UniformLattice(component):
    def RunScript(self, core_voxels, boundary_voxels, unit_cell, connectivity, primitive):
        global unit_cell_bounds
        global unit_cell_global
        global connectivity_global
        global primitive_global
        global lattice_trimmed

        unit_cell_global = unit_cell
        connectivity_global = connectivity
        primitive_global = primitive
        unit_cell_bounds = get_bounding_box(unit_cell)
        unit_cell = Rhino.Geometry.Curve.JoinCurves(unit_cell)
        if core_voxels:
            lattice_core = ghpythonlib.parallel.run(populate_lattice_parallel, core_voxels, True)
        else:
            lattice_core = []
        if boundary_voxels:
            lattice_boundary = ghpythonlib.parallel.run(populate_lattice_parallel, boundary_voxels, True)
            lattice_boundary_connect = ghpythonlib.parallel.run(populate_connectivity_parallel, boundary_voxels, True)
            lattice_skin = ghpythonlib.parallel.run(populate_skin_parallel, boundary_voxels, True)
        else:
            lattice_boundary = []
            lattice_boundary_connect = []
            lattice_skin = []

        lattice_trimmed = []
        lattice_combined = list(lattice_core) + list(lattice_boundary)
        valid_curves = list(filter(None, lattice_combined))
        ghpythonlib.parallel.run(check_curve_parallel, valid_curves, False)

        return lattice_core, lattice_boundary, lattice_trimmed, lattice_boundary_connect, lattice_skin