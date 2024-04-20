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
def stm_handler_depsgraph_update(scene):

    # print('depsgraph_update')

    if bpy.context.screen.is_animation_playing:
        pass
    elif not bpy.context.object:
        pass
    elif bpy.context.object.stm_spectro.stm_status == 'generating':
        pass
    elif bpy.context.object.stm_spectro.stm_type in ['spectrogram', 'waveform']:
        
        if len(scene.objects) != scene.stm_settings.object_count_tmp:
            # print('update_stm_list()')
            funcs.update_stm_list(bpy.context)
            scene.stm_settings.object_count_tmp = len(scene.objects)

        funcs.select_item_in_list_from_handler(bpy.context)
        # print('select_item_in_list_from_handler()')
        # pass

@persistent
def stm_handler_playback(scene):
    if not bpy.context.object:
        pass
    elif bpy.context.object.stm_spectro.stm_status == 'generating':
        pass
    elif bpy.context.object.stm_spectro.stm_type in ['spectrogram', 'waveform']:
        if len(scene.objects) != scene.stm_settings.object_count_tmp:
            funcs.update_stm_list(bpy.context)
            scene.stm_settings.object_count_tmp = len(scene.objects)

        funcs.select_item_in_list_from_handler(bpy.context)
        pass

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
