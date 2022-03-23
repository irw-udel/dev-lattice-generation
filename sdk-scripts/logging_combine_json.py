"""Combines a list of JSON inputs into a single JSON object for output.
    Inputs:
        input_json: JSON objects to combine
    Output:
       combined_json: Combined inputs"""

__author__ = "irw"
__version__ = "20220126"

from ghpythonlib.componentbase import executingcomponent as component
import Grasshopper, GhPython
import System
import Rhino
import json
from collections import OrderedDict

def combine_inputs(input_json):
    m = OrderedDict()
    for item in input_json:
        if item:
            item = str(item).replace("\n", "")
            m.update(json.loads(item, object_pairs_hook=OrderedDict))
    return m

class CombineJson(component):
    def RunScript(self, input_json):
        merged = combine_inputs(input_json)
        combined_json = json.dumps(merged, sort_keys=False, indent=4, separators=(',', ': '))

        return combined_json