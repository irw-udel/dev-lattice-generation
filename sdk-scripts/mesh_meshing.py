"""Convert a lattice frame to a printable mesh. Includes options to save with modifications for 3D printing.
    Inputs:
        curves: The lattice curves for meshing
        radius: Radius of the lattice curves
        dendroSettings: Settings provided by the Dendro component
        cut_surfaces: Cutting surfaces for trimming the lattice
        bake: Bake the part into Rhino?
        save: Save the part?
        delete: Delete the part after saving?
    Output:
        out_mesh: Dendro-generated mesh of lattice
        original_report: Mesh report for original lattice
        mod_report: Mesh report for modified lattice, with minimal alterations
        cut_report: Mesh report for trimmed lattice
        volume: Volume of the final lattice in document units
        area: Surface area of the final lattice in document units"""

__author__ = "irw"
__version__ = "20220124"

from ghpythonlib.componentbase import executingcomponent as component
import Grasshopper, GhPython
import System
import Rhino
import rhinoscriptsyntax as rs
import ghpythonlib.components as ghcomp

out_mesh = None

def to_json(key, value):
    return '"{}" : "{}"'.format(key, value)

def to_json_value_object_pair(key, value):
    return '"{}" : {{{}}}'.format(key, value)

def get_mesh_report(report_instance, additional_params = None):
    naked_count = 0
    naked_edges = out_mesh.GetNakedEdges()
    if naked_edges is not None:
        naked_count = len(naked_edges)
        
    properties = []
    report = to_json("report_version", report_instance)
    valid = to_json("valid_mesh", out_mesh.IsValid)
    naked = to_json("naked_edges", naked_count)
    closed = to_json("closed_mesh", out_mesh.IsClosed)
    manifold = to_json("manifold_mesh", out_mesh.IsManifold(True))
    disjoint = to_json("disjoint_count", out_mesh.DisjointMeshCount)
    vertices = to_json("vertex_count", out_mesh.Vertices.Count)
    memory = to_json("memory_estimate_mb", out_mesh.MemoryEstimate()*1e-6)
    log = to_json("log_invalid", out_mesh.IsValidWithLog()[1])
    
    properties.extend([report, valid, naked, closed, manifold, disjoint, vertices, memory, log])
    if additional_params:
        properties.extend(additional_params)

    properties_json = '{{{}}}'.format(to_json_value_object_pair(report_instance, ','.join(properties)))

    return properties_json

def get_cut_planes(surfaces, translation_factor = 0):
    planes = set()
    for surface in surfaces:
        normal_vector = surface.NormalAt(u = 0, v = 0)
        surface.Translate(translation_factor*normal_vector)
        planes.add(Rhino.Geometry.Mesh.CreateFromSurface(surface, Rhino.Geometry.MeshingParameters(1)))

    return planes

class MeshLattice(component):
    def RunScript(self, curves, radius, dendroSettings, cut_surfaces, bake, save, file_name, delete):
        global out_mesh
        original_report = None
        cut_report = None
        volume = None
        area = None
        
        #   Generate lattice volume and mesh
        out_mesh = ghcomp.DendroGH.CurveToVolume(curves = curves, curve_radius = radius, settings = dendroSettings)
        out_mesh = ghcomp.DendroGH.VolumetoMesh(volume = out_mesh, volume_settings = dendroSettings)

        original_bounds = out_mesh.GetBoundingBox(True)
        original_report = get_mesh_report(report_instance = "original_report")

        #   Make checks and first repairs
        degenerate_faces = to_json("degenerate_faces", out_mesh.Faces.RemoveZeroAreaFaces(0))
        quads_to_tris = to_json("quads_to_tris", out_mesh.Faces.ConvertQuadsToTriangles())
        out_mesh.UnifyNormals()
        mesh_flipped = False
        if(out_mesh.Volume() < 0):
            out_mesh.Flip(True, True, True)
            mesh_flipped = True
        mesh_flipped = to_json("mesh_flipped", mesh_flipped)
        mod_report = get_mesh_report(report_instance = "modified_report", additional_params=[degenerate_faces, quads_to_tris, mesh_flipped])

        #    Split mesh
        if cut_surfaces:
            revised_cut = False
            planes = get_cut_planes(cut_surfaces)
            cut_mesh = Rhino.Geometry.Mesh.CreateBooleanDifference({out_mesh}, planes)[0]
            cut_bounds = cut_mesh.GetBoundingBox(True)

            if (cut_bounds.Volume/original_bounds.Volume < 0.01):
                revised_cut = True
                planes = get_cut_planes(cut_surfaces, translation_factor = 0.01)
                out_mesh = Rhino.Geometry.Mesh.CreateBooleanDifference({out_mesh}, planes)[0]
            else:
                out_mesh = cut_mesh

            # out_mesh.Weld(3.1415)
            revised_cut = to_json("revised_cut", revised_cut)
            face_count_cut = to_json("face_count_cut", out_mesh.Faces.Count)
            fill_success = to_json("fill_success", out_mesh.FillHoles())
            face_count_filled = to_json("face_count_filled", out_mesh.Faces.Count)
            cut_report = get_mesh_report(report_instance = "cut_report", additional_params=[revised_cut, face_count_cut, fill_success, face_count_filled])

        #   Keep until main script is validated
        #    if (a.GetNakedEdges()):
        #        print a.GetNakedEdges()
        #        print a.Vertices.Align(distance = 1e-1, whichVertices = a.GetNakedEdgePointStatus())
        #        a.ExtractNonManifoldEdges(False)
        #        a.Faces.ExtractDuplicateFaces()
        #        print a.Vertices.Align(distance = 1e-1, whichVertices = a.GetNakedEdgePointStatus()) 

        #   Calculate mesh properties
        volume = out_mesh.Volume()
        areaMassProperties = Rhino.Geometry.AreaMassProperties.Compute(out_mesh)
        area = areaMassProperties.Area

        #   Export
        if bake or save:
            id = Rhino.RhinoDoc.ActiveDoc.Objects.Add(out_mesh)
            id = str(id)

            if save:
                rs.Command("SelID " + id)
                rs.Command("-Export " + file_name + ".stl Enter")
            
                if delete:
                    rs.Command("SelID " + id)
                    rs.Command("Delete")
            
        rs.Command("ClearUndo")
        return out_mesh, original_report, mod_report, cut_report, volume, area