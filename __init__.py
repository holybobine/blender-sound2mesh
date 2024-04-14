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


def stm_handler_depsgraph_update(scene):

    # print('depsgraph_update')

    if bpy.context.screen.is_animation_playing:
        pass
    elif not bpy.context.object:
        pass
    elif bpy.context.object.stm_spectro.stm_type in ['spectrogram', 'waveform']:
        funcs.check_if_new_waveform(bpy.context.object)
        funcs.check_for_deleted_items(bpy.context.object)
        funcs.update_obj_in_list(bpy.context.object)


def stm_handler_playback(scene):
    if bpy.context.object:
        if bpy.context.object.stm_spectro.stm_type in ['spectrogram', 'waveform']:
            funcs.update_obj_in_list(bpy.context.object)

# def stm_handler_playback_pre(scene):
#     scene.stm_settings.is_scene_playing = True
#     funcs.redraw_all_viewports()

# def stm_handler_playback_post(scene):
#     scene.stm_settings.is_scene_playing = False

#     if bpy.context.object:
#         if bpy.context.object.stm_spectro.stm_type in ['spectrogram', 'waveform']:
#             funcs.update_obj_in_list(bpy.context.object)
#             pass


def register():
    
    previews.register()
    property_groups.register()
    operators.register()
    panels.register()

    bpy.app.handlers.depsgraph_update_post.append(stm_handler_depsgraph_update)
    # bpy.app.handlers.animation_playback_pre.append(stm_handler_playback_pre)
    # bpy.app.handlers.animation_playback_post.append(stm_handler_playback_post)
    bpy.app.handlers.frame_change_post.append(stm_handler_playback)



def unregister():

    previews.unregister()
    property_groups.unregister()
    operators.unregister()
    panels.unregister()

    bpy.app.handlers.depsgraph_update_post.clear()
    bpy.app.handlers.animation_playback_pre.clear()
    bpy.app.handlers.animation_playback_post.clear()
    bpy.app.handlers.frame_change_post.clear()


if __name__ == "__main__":
    register()
