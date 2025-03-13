# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTIBILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.

bl_info = {
    "name" : "Sound To Mesh",
    "author" : "holybobine",
    "description" : "",
    "blender" : (4, 0, 0),
    "version" : (0, 0, 4),
    "location" : "",
    "warning" : "",
    "category" : "3D View"
}

import bpy
from bpy.props import *
from sys import path

from . import previews
from . import property_groups
from . import operators
from . import panels
from . import funcs
from bpy.app.handlers import persistent


@persistent
def stm_handler_functions(dummy):

    funcs.find_spectrogram_objects()
    # funcs.find_waveform_objects()
    funcs.remove_orphan_sounds()
    funcs.update_active_audio_in_scene()

def register():
    
    previews.register()
    property_groups.register()
    operators.register()
    panels.register()

    bpy.app.handlers.load_post.append(stm_handler_functions)
    bpy.app.handlers.depsgraph_update_post.append(stm_handler_functions)
    bpy.app.handlers.frame_change_post.append(stm_handler_functions)

    # bpy.app.handlers.depsgraph_update_post.append(stm_handler_depsgraph_update)
    # bpy.app.handlers.frame_change_post.append(stm_handler_playback)



def unregister():

    previews.unregister()
    property_groups.unregister()
    operators.unregister()
    panels.unregister()

    # bpy.app.handlers.depsgraph_update_post.remove(funcs.find_spectrogram_objects)
    # bpy.app.handlers.depsgraph_update_post.remove(funcs.find_waveform_objects)

    bpy.app.handlers.load_post.remove(stm_handler_functions)
    bpy.app.handlers.depsgraph_update_post.remove(stm_handler_functions)
    bpy.app.handlers.frame_change_post.remove(stm_handler_functions)


if __name__ == "__main__":
    register()
