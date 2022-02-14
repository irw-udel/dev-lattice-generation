"""Converts an input primitive to a mesh for lattice generation and provides tools for trimming the lattice with planes.
    Inputs:
        primitive: Base shape to populate with lattice geometry
    Output:
        primitive: The primitive as a closed mesh
        cut_surfaces: Top and bottom surfaces, oriented for trimming the lattice
        symmetry_surfaces: Surfaces for octant-based symmetry
        octant: Primitive mesh octant (-1, -1, -1)"""

__author__ = "irw"
__version__ = "20220124"

from ghpythonlib.componentbase import executingcomponent as component
import Grasshopper, GhPython
import System
import Rhino
import rhinoscriptsyntax as rs

def clean_primitive(primitive):
    if (primitive.ObjectType == Rhino.DocObjects.ObjectType.Brep):
        meshed_brep = Rhino.Geometry.Mesh.CreateFromBrep(primitive, Rhino.Geometry.MeshingParameters(1))
        meshed_primitive = Rhino.Geometry.Mesh()
        for mesh in meshed_brep:
            meshed_primitive.Append(mesh)

        meshed_primitive.HealNakedEdges(0.01)
    else:
        meshed_primitive = primitive

    meshed_primitive.UnifyNormals()
    meshed_primitive.Weld(3.1415)
    if(meshed_primitive.Volume() < 0):
        meshed_primitive.Flip(True, True, True)

    return meshed_primitive

def get_cut_planes(primitive):
    primitive = rs.coercegeometry(primitive)
    bbox = primitive.GetBoundingBox(True)
    scaled_bbox = bbox
    center = bbox.Center
    center_plane = Rhino.Geometry.Plane(center, Rhino.Geometry.Vector3d(0,0,1))
    scaled_bbox.Transform(Rhino.Geometry.Transform.Scale(center_plane, 1.2, 1.2, 1))

    x_length = scaled_bbox.Max[0] - scaled_bbox.Min[0]
    x_interval = Rhino.Geometry.Interval(-x_length/2, x_length/2)

    y_length = scaled_bbox.Max[1] - scaled_bbox.Min[1]
    y_interval = Rhino.Geometry.Interval(-y_length/2, y_length/2)

    z_vector = Rhino.Geometry.Vector3d(0,0,1)

    top_point = Rhino.Geometry.Point3d(center[0],center[1],bbox.Max[2])
    top_plane = Rhino.Geometry.Plane(top_point, -z_vector)
    top_surface = Rhino.Geometry.PlaneSurface(top_plane, x_interval, y_interval)

    bottom_point = Rhino.Geometry.Point3d(center[0],center[1],bbox.Min[2])
    bottom_plane = Rhino.Geometry.Plane(bottom_point, z_vector)
    bottom_surface = Rhino.Geometry.PlaneSurface(bottom_plane, x_interval, y_interval)

    return top_surface, bottom_surface

def get_symmetry_planes(primitive):
    bbox = primitive.GetBoundingBox(True)

    min_coord_x = bbox.Min[0]*1.2
    max_coord_x = bbox.Max[0]*1.2
    x_interval = Rhino.Geometry.Interval(min_coord_x, max_coord_x)
    
    min_coord_y = bbox.Min[1]*1.2
    max_coord_y = bbox.Max[1]*1.2
    y_interval = Rhino.Geometry.Interval(min_coord_y, max_coord_y)
    
    min_coord_z = bbox.Min[2]*1.2
    max_coord_z = bbox.Max[2]*1.2
    z_interval = Rhino.Geometry.Interval(min_coord_z, max_coord_z)

    zx_x_interval = Rhino.Geometry.Interval(bbox.Min[0]*1.2, bbox.Max[0]*1.2)
    zx_z_interval = Rhino.Geometry.Interval((bbox.Min[2]-bbox.Center[2])*1.2, (bbox.Max[2]-bbox.Center[2])*1.2)
    yz_y_interval = Rhino.Geometry.Interval(bbox.Min[1]*1.2, bbox.Max[1]*1.2)
    yz_z_interval = Rhino.Geometry.Interval((bbox.Min[2]-bbox.Center[2])*1.2, (bbox.Max[2]-bbox.Center[2])*1.2)

    plane_point = bbox.Center

    XY_cut = Rhino.Geometry.PlaneSurface(Rhino.Geometry.Plane(plane_point, Rhino.Geometry.Vector3d(0,0,-1)), x_interval, y_interval)
    YZ_cut = Rhino.Geometry.PlaneSurface(Rhino.Geometry.Plane(plane_point, Rhino.Geometry.Vector3d(-1,0,0)), yz_y_interval, yz_z_interval)
    ZX_cut = Rhino.Geometry.PlaneSurface(Rhino.Geometry.Plane(plane_point, Rhino.Geometry.Vector3d(0,-1,0)), zx_z_interval, zx_x_interval)

    return XY_cut, YZ_cut, ZX_cut

def split_mesh(primitive, surfaces):
    planes = set()
    for surface in surfaces:
        planes.add(Rhino.Geometry.Mesh.CreateFromSurface(surface, Rhino.Geometry.MeshingParameters(1)))
    octant = Rhino.Geometry.Mesh.CreateBooleanDifference({primitive}, planes)

    return octant

class Primitive(component):
    def RunScript(self, primitive):
        primitive = clean_primitive(primitive)
        cut_surfaces = get_cut_planes(primitive)
        symmetry_surfaces = get_symmetry_planes(primitive)
        octant = split_mesh(primitive, symmetry_surfaces)
        
        return primitive, cut_surfaces, symmetry_surfaces, octant
