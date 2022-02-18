"""Provides a scripting component.
    Inputs:
        refresh: Recalculate the component
        project_dir: The project's main directory
        save_directory: Folder to save the STL and log output
        id_properties: Key features of the part. Takes single value or list of properties
    Output:
        part_id: A unique ID for the generated part. Takes the format (date)-(properties fragment)-(instance fragment)
        date_utc: The UTC date and time at which computation was performed
        mesh_path: Full path for the STL output
        log_path: Full path for the log output
        gh_file: Path and name of the Grasshopper definition
        base_unit: Base unit of the Rhino and Grasshopper file (e.g. millimeter)
        device: Device used for computation
        rhino_build: Rhino software version
        rhino_date: Rhino software version release date
        gh_build: Grasshopper software version
        gh_date: Grasshopper software version release date
        core_dependencies: Default libraries used in this definition
        addon_dependencies: Installed libraries used in this definition"""

__author__ = "irw"
# Includes script components from Giulio Piacentino, source: https://www.grasshopper3d.com/forum/topics/gh-filename-is-python
__version__ = "20220124"

from ghpythonlib.componentbase import executingcomponent as component
import Grasshopper, GhPython
import System
import Rhino
import rhinoscriptsyntax as rs
import scriptcontext
import os
import hashlib
from datetime import datetime

def make_id(properties):
    properties_string = ','.join(map(str, properties))
    properties_fragment = (hashlib.md5(properties_string.encode("UTF-8")).hexdigest())[:3]

    date_info = datetime.now().strftime("%y%m%d")
    date_utc = datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S")
    instance_fragment = (hashlib.sha256(date_utc.encode("UTF-8")).hexdigest())[:2]

    unique_id = '-'.join([date_info, properties_fragment, instance_fragment])
    
    return unique_id, date_utc

def get_libraries(self):
    core_libraries = {}
    addon_libraries = {}
    objids = {}
    
    server = Grasshopper.Instances.ComponentServer
    for obj in self.OnPingDocument().Objects:
        if obj == self: continue #Ignore this component.
        
        objId = obj.ComponentGuid
        if objids.has_key(objId): continue
        objids[objId] = ""
        
        lib = server.FindAssemblyByObject(obj)
        if lib == None: continue
        if core_libraries.has_key(lib.Id) or addon_libraries.has_key(lib.Id): continue
        
        if lib.IsCoreLibrary:
            core_libraries[lib.Id] = lib
        else:
            addon_libraries[lib.Id] = lib
    
    return core_libraries, addon_libraries

def get_units(ghdoc):
    scriptcontext.doc = Rhino.RhinoDoc.ActiveDoc
    base_units = rs.UnitSystemName()
    scriptcontext.doc = ghdoc
    
    return base_units

def get_device():
    device = Rhino.Runtime.HostUtils.DeviceId.ToString()

    return device

def get_software_build():
    rhino_build = str(Rhino.RhinoApp.Version)
    rhino_date = Rhino.RhinoApp.BuildDate
    gh_build = str(Grasshopper.Versioning.Version)
    gh_date = Grasshopper.Versioning.BuildDate

    return rhino_build, rhino_date, gh_build, gh_date

class SystemInfo(component):
    def RunScript(self, refresh, project_dir, save_directory, id_properties):
        ghdoc = scriptcontext.doc
        part_id = None
        date_utc = None
        gh_file = None
        base_unit = None
        device = None
        rhino_build = None
        rhino_date = None
        gh_build = None
        gh_date = None
        core_dependencies = None
        addon_dependencies = None


        part_id, date_utc = make_id(id_properties)
        gh_path = os.path.realpath(ghdoc.Path)

        if not save_directory:
            save_directory = os.path.dirname(ghdoc.Path)

        file_name_base = "\\".join([save_directory, part_id])
        mesh_path = "\"{}.stl\"".format(file_name_base)
        log_path = "{}.txt".format(file_name_base)

        if project_dir:
            gh_file = gh_path.split(project_dir)[1]
        else:
            gh_file = gh_path

        base_unit = get_units(ghdoc)
        device = get_device()
        rhino_build, rhino_date, gh_build, gh_date = get_software_build()


        core_libraries, addon_libraries = get_libraries(self)

        core_dependencies = []
        for id, lib in core_libraries.iteritems():
            core_dependencies.append("{0} {1}".format(lib.Name, lib.Version))

        addon_dependencies = []
        for id, lib in addon_libraries.iteritems():
            addon_dependencies.append("{0} {1}".format(lib.Name, lib.Version))
        
        return part_id, date_utc, mesh_path, log_path, gh_file, base_unit, device, rhino_build, rhino_date, gh_build, gh_date, core_dependencies, addon_dependencies