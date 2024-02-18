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
import os
import json

from bpy.props import *

from sys import path

# path.append(bpy.path.abspath("//"))



# import operators
# import panels
# import funcs

# from importlib import reload

# reload(operators)
# reload(panels)
# reload(funcs)

from .operators import *
from .panels import *
from .funcs import *



# -------------------------------------------------------------------
#   Register & Unregister
# -------------------------------------------------------------------

classes = [
    STM_OT_import_audio_file,
    STM_OT_reset_audio_file,
    STM_OT_reset_spectrogram_settings,
    STM_OT_add_audio_to_scene,
    STM_OT_open_image_folder,
    STM_OT_open_image,
    STM_OT_prompt_spectrogram_popup,
    STM_OT_generate_spectrogram_modal,
    STM_OT_select_stm_in_viewport,
    STM_OT_add_waveform,
    STM_OT_add_spectrogram,
    STM_OT_remove_waveform,
    STM_OT_reset_spectrogram_full,
    STM_OT_reset_spectrogram_main_settings,
    STM_OT_reset_spectrogram_geometry_values,
    STM_OT_reset_eq_curve,
    STM_OT_reset_gradient,
    STM_OT_hello,
    STM_PT_spectrogram,
    STM_PT_geometry_nodes,
    STM_PT_material,
    STM_OT_dummy_op,
    STM_OT_reload_previews,
    THUMB_OT_next_waveform_style,
    THUMB_OT_previous_waveform_style,
]




def generate_previews(pcoll_name):
    pcoll = preview_collections[pcoll_name]
    image_location = pcoll.images_location
    VALID_EXTENSIONS = ('.png', '.jpg', '.jpeg')

    enum_items = []

    # Generate the thumbnails
    for i, image in enumerate(os.listdir(image_location)):
        if image.endswith(VALID_EXTENSIONS):

            item_name = image.replace('.png', '').replace('_', ' ')

            filepath = os.path.join(image_location, image)
            thumb = pcoll.load(filepath, filepath, 'IMAGE')
            enum_items.append((image, item_name, "", thumb.icon_id, i))

    return enum_items

preview_collections = {}

def register():

    import bpy.utils.previews

    for c in classes:
        try:
            bpy.utils.register_class(c)
        except:
            print('-ERR- %s skipped'%c)


    addon_path = os.path.dirname(__file__)

    dir_gradient_icons = r'.\icons\icons_gradient_presets'
    dir_stm_icons = r'.\icons\icons_stm_presets'
    dir_eq_icons = r'.\icons\icons_eq_presets'
    dir_waveform_icons = r'.\icons\icons_waveform_style'

    

    preview_collections["presets_spectrogram"] = bpy.utils.previews.new()
    preview_collections["presets_spectrogram"].images_location = os.path.join(addon_path, dir_stm_icons)

    preview_collections["presets_gradient"] = bpy.utils.previews.new()
    preview_collections["presets_gradient"].images_location = os.path.join(addon_path, dir_gradient_icons)

    preview_collections["presets_eq_curve"] = bpy.utils.previews.new()
    preview_collections["presets_eq_curve"].images_location = os.path.join(addon_path, dir_eq_icons)

    preview_collections["presets_waveform_style"] = bpy.utils.previews.new()
    preview_collections["presets_waveform_style"].images_location = os.path.join(addon_path, dir_waveform_icons)


    bpy.types.Scene.ffmpegPath = StringProperty(
            default=os.path.join(addon_path, 'ffmpeg', 'ffmpeg.exe')
        )
    bpy.types.Scene.outputPath = StringProperty(
            default=os.path.join(addon_path, '.\output'),
            subtype="DIR_PATH"
        )
    bpy.types.Scene.assetFilePath = StringProperty(
            default=os.path.join(addon_path, 'asset_files', 'asset_files_v07.blend')
        )

    bpy.types.Scene.presets_json_file = StringProperty(default=os.path.join(addon_path, 'presets_spectrogram.json'))
    bpy.types.Scene.eq_curve_presets_json_file = StringProperty(default=os.path.join(addon_path, 'presets_eq_curve.json'))
    bpy.types.Scene.gradient_presets_json_file = StringProperty(default=os.path.join(addon_path, 'presets_gradients.json'))


    bpy.types.Scene.presets_spectrogram = bpy.props.EnumProperty(
            name='presets_spectrogram',
            items=generate_previews('presets_spectrogram'),
            update=apply_spectrogram_preset
        )
    bpy.types.Object.presets_gradient = bpy.props.EnumProperty(
            name='presets_gradient',
            items=generate_previews('presets_gradient'),
            update=apply_gradient_preset,
        )

    bpy.types.Scene.presets_eq_curve = bpy.props.EnumProperty(
            name='presets_eq_curve',
            items=generate_previews('presets_eq_curve'),
            update=apply_eq_curve_preset,
        )

    bpy.types.Object.presets_waveform_style = bpy.props.EnumProperty(
            name='presets_waveform_style',
            items=generate_previews('presets_waveform_style'),
            update=apply_waveform_style,
        )

    bpy.types.Object.progress = bpy.props.FloatProperty(
            name="Progress",
            subtype="PERCENTAGE",
            default=0,
            soft_min=0,
            soft_max=100,
            precision=0,
        )

    bpy.types.Object.progress_label = bpy.props.StringProperty()
    bpy.types.Scene.stm_progress = bpy.props.FloatProperty(
            name="Progress",
            subtype="PERCENTAGE",
            soft_min=0,
            soft_max=100,
            precision=0,
            default=0,
        )




    bpy.types.Scene.stm_obj_list_index = IntProperty(update=select_obj_from_list)

    bpy.types.Scene.audio_file_path = StringProperty(name = "", description="path to audio file")
    bpy.types.Scene.audio_filename = StringProperty(name = "", description="audio file")

    bpy.types.Scene.force_standard_view_transform = BoolProperty(name='Set scene view tranform to "Standard"', default=True)
    bpy.types.Scene.force_eevee_AO = BoolProperty(name='Enable EEVEE Ambient Occlusion', default=True)
    bpy.types.Scene.force_eevee_BLOOM = BoolProperty(name='Enable EEVEE Bloom', default=True)
    bpy.types.Scene.disable_eevee_viewport_denoising = BoolProperty(name='Disable EEVEE Viewport Denoising', default=True)

    bpy.types.Scene.title = StringProperty()
    bpy.types.Scene.album = StringProperty()
    bpy.types.Scene.artist = StringProperty()
    bpy.types.Scene.duration_seconds = FloatProperty()
    bpy.types.Scene.duration_format = StringProperty()



    bpy.types.Scene.stm_object = PointerProperty(name='Spectrogram Object', type=bpy.types.Object)

    bpy.types.Scene.bool_advanced_spectrogram_settings = bpy.props.BoolProperty(default=False)
    bpy.types.Scene.bool_spectrogram_scene_settings = bpy.props.BoolProperty(default=False)

    bpy.types.Scene.spectro_scale = bpy.props.EnumProperty(
            items= (
                        ('lin', "Lin", ""),
                        ('sqrt', "sqrt", ""),
                        ('cbrt', "cbrt", ""),
                        ('log', "Log", ""),
                        ('4thrt', "4thrt", ""),
                        ('5thrt', "5thrt", "")
                    ),
            description = "Set intensity scale to use to generate spectrogram",
            name = "Intensity scale",
            default='log'
        )

    bpy.types.Scene.spectro_fscale = bpy.props.EnumProperty(
            items= (
                        ('lin', "Lin", ""),
                        ('log', "Log", "")
                    ),
            description = "Set frequency scale to use to generate spectrogram",
            name = "Frequency scale",
            default='lin'
        )

    bpy.types.Scene.spectro_colorMode = bpy.props.EnumProperty(
            items= (
                        ('channel', "channel", ""),
                        ('intensity', "intensity", ""),
                        ('rainbow', "rainbow", ""),
                        ('moreland', "moreland", ""),
                        ('nebulae', "nebulae", ""),
                        ('fire', "fire", ""),
                        ('fiery', "fiery", ""),
                        ('fruit', "fruit", ""),
                        ('cool', "cool", ""),
                        ('magma', "magma", ""),
                        ('green', "green", ""),
                        ('viridis', "viridis", ""),
                        ('plasma', "plasma", ""),
                        ('cividis', "cividis", ""),
                        ('terrain', "terrain", "")
                    ),
            description = "Set style used to generate spectrogram",
            name = "color mode",
            default='intensity'
        )

    bpy.types.Scene.spectro_drange = bpy.props.IntProperty(default=120, min=0, max=120)

    bpy.types.Scene.resolutionPreset = bpy.props.EnumProperty(
            items= (
                        ('1024x512', "1K", "1024x512"),
                        ('2048x1024', "2K", "2048x1024"),
                        ('4096x2048', "4K", "4096x2048"),
                        ('8192x4096', "8K", "8192x4096"),
                        ('16384x8192', "16K", "16384x8192"),
                        ('custom', "Custom", "")
                    ),
            name = "Resolution Preset",
            default='4096x2048'
        )


    bpy.types.Scene.userWidth = bpy.props.IntProperty(default=4096)
    bpy.types.Scene.userHeight = bpy.props.IntProperty(default=2048)

    # bpy.types.Scene.bool_output_path = bpy.props.BoolProperty(default=False)

    bpy.types.Scene.bool_output_path = bpy.props.EnumProperty(
            items= (
                        ("default", "Default", ""),
                        ("custom", "Custom", "")
                    ),
            default="default",
        )


    bpy.types.Scene.bool_main_settings = bpy.props.BoolProperty(default=False)
    bpy.types.Scene.bool_geometry_settings = bpy.props.BoolProperty(default=False)
    bpy.types.Scene.bool_eq_curve_settings = bpy.props.BoolProperty(default=False)
    bpy.types.Scene.bool_custom_gradient = bpy.props.BoolProperty(default=False)


    bpy.types.Object.material_type = bpy.props.EnumProperty(
            items= (
                        ('raw', "Raw Texture", ""),
                        ('gradient', "Gradient", ""),
                        ('custom', "Custom", "")
                    ),
            description = "Choose material type",
            default='raw',
            update=update_stm_material
        )

    bpy.types.Object.material_custom =  bpy.props.PointerProperty(
        type=bpy.types.Material,
        update=update_stm_material
    )

    bpy.types.Object.geometry_type = bpy.props.EnumProperty(
            items= (
                        ('plane', "Plane", ""),
                        ('cylinder', "Cylinder", ""),
                        ('curve', "Curve", "")
                    ),
            description = "Choose geometry type for the spectrogram",
            name = "Geometry type",
            default='plane',
            update=set_geometry_type
        )

    bpy.types.Object.doExtrude = bpy.props.EnumProperty(
            items= (
                        ("on", "ON", ""),
                        ("off", "OFF", "")
                    ),
            default="on",
            update=set_doExtrude
        )
    
    bpy.types.Object.curveAlignment = bpy.props.EnumProperty(
            items= (
                        ("center", "CENTER", ""),
                        ("edge", "EDGE", "")
                    ),
            default="center",
            update=set_curveAlignment
        )
    
    bpy.types.Object.doFlip = bpy.props.EnumProperty(
            items= (
                        ("on", "ON", ""),
                        ("off", "OFF", "")
                    ),
            default="off",
            update=set_doFlip
        )

    bpy.types.Object.showGrid = bpy.props.EnumProperty(
            items= (
                        ("on", "ON", ""),
                        ("off", "OFF", "")
                    ),
            default="on",
            update=set_showGrid
        )

    bpy.types.Object.waveform_resolution_choice = bpy.props.EnumProperty(
            items= (
                        ("default", "Default", ""),
                        ("custom", "Custom", "")
                    ),
            default="default",
            update=set_waveform_resolution_choice
        )

    bpy.types.Object.waveform_style = bpy.props.EnumProperty(
            items= (
                        ('line', "Line", ""),
                        ('dots', "Dots", ""),
                        ('plane', "Plane", ""),
                        ('cubes', "Cubes", ""),
                        ('tubes', "Tubes", ""),
                        ('zigzag', "Zigzag", ""),
                        ('zigzag_smooth', "Smooth Zigzag", "")
                    ),
            default='line',
            update=set_waveform_style
        )



def unregister():
    #class_unregister()

    for pcoll in preview_collections.values():
        bpy.utils.previews.remove(pcoll)

    preview_collections.clear()

    for c in classes:
        try:
            bpy.utils.unregister_class(c)
        except:
            print('-ERR- %s skipped'%c)

    # del bpy.types.Scene.preset_spectrogram

    # del bpy.types.Scene.stm_obj_list_index
    # del bpy.types.Scene.audio_file_path

    # del bpy.types.Scene.presets_json_file


    # del bpy.types.Scene.stm_show_file_data
    # del bpy.types.Scene.stm_show_main_settings
    # del bpy.types.Scene.stm_show_audio_settings
    # del bpy.types.Scene.stm_show_curve_settings
    # del bpy.types.Scene.stm_show_geometry_settings

if __name__ == "__main__":
    register()
