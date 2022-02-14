"""Writes text input to a file.
    Inputs:
        file_path: Path to the file to write. Relative to the GH definition directory
        content: Content to write to the file
        write_file: Write the file?"""

__author__ = "ianrw"
__version__ = "20220124"

from ghpythonlib.componentbase import executingcomponent as component
import Grasshopper, GhPython
import System
import Rhino
import rhinoscriptsyntax as rs
import scriptcontext
import os

def write_lines(file, content):
    for line in content:
        file.write(line)
    file.close()

class Logger(component):
    def RunScript(self, file_path, content, write_file):
        ghdoc = scriptcontext.doc

        if write_file and file_path:
            working_dir = os.path.dirname(os.path.realpath(ghdoc.Path))
            file_path = os.path.join(working_dir, file_path)

            if (os.path.exists(file_path)):
                file = open(file_path, "a")
                if (os.stat(file_path).st_size != 0):
                    file.write("," + "\n")           
                write_lines(file, content)

            else:
                file = open(file_path, "w")
                write_lines(file, content)