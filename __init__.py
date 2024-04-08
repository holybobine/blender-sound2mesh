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


def my_handler(scene):
    if bpy.context.object:
        funcs.update_obj_in_list(bpy.context.object)
        pass


def register():
    
    previews.register()
    property_groups.register()
    operators.register()
    panels.register()

    bpy.app.handlers.depsgraph_update_post.append(my_handler)
    bpy.app.handlers.frame_change_post.append(my_handler)



def unregister():

    previews.unregister()
    property_groups.unregister()
    operators.unregister()
    panels.unregister()

    bpy.app.handlers.depsgraph_update_post.clear()
    bpy.app.handlers.frame_change_post.clear()


if __name__ == "__main__":
    register()
