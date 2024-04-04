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


global preview_collections
preview_collections = {}

addon_path = os.path.dirname(__file__)


def generate_previews(pcoll_name):

    pcoll = preview_collections[pcoll_name]
    image_location = pcoll.images_location
    VALID_EXTENSIONS = ('.png', '.jpg', '.jpeg')

    enum_items = []

    for i, image in enumerate(os.listdir(image_location)):
        if image.endswith(VALID_EXTENSIONS):
            
            item_name = image.replace('.png', '')
            item_name = item_name.split('-')[1]
            item_name = item_name.replace('_', ' ')

            filepath = os.path.join(image_location, image)
            thumb = pcoll.load(filepath, filepath, 'IMAGE')
            enum_items.append((image, item_name, "", thumb.icon_id, i))

    return enum_items

def get_spectrogram_preview(self, context):
    pcoll = preview_collections["preview_image_enum"]
    thumbs_folder = os.path.join(os.path.dirname(__file__), './thumbs')

    current_image = context.object.stm_spectro.image_file
    enum_items = []

    if current_image != None:

        item_name = current_image.name
        filepath = current_image.filepath

        if filepath in pcoll:
            thumb = pcoll[filepath]
        else:
            thumb = pcoll.load(filepath, filepath, 'IMAGE', force_reload=True)

        enum_items.append((item_name, item_name, "", thumb.icon_id, 0))

    return enum_items

def generate_items_from_presets(self, context):

    scn = bpy.context.scene

    with open(r'%s'%scn.stm_settings.presets_json_file,'r') as f:
        presets=json.load(f)

    enum_items = []

    for p in presets:
        enum_items.append((p, presets[p]["name"], ""))

    # print(enum_items)

    return enum_items


class STM_spectrogram_props(bpy.types.PropertyGroup):
    stm_type : StringProperty() # type: ignore

    audio_file_path : StringProperty() # type: ignore # type: ignore
    audio_filename : StringProperty() # type: ignore
    audio_file : PointerProperty(type=bpy.types.Sound, update=update_metadata) # type: ignore

    meta_title : StringProperty() # type: ignore
    meta_album : StringProperty() # type: ignore
    meta_artist : StringProperty() # type: ignore
    meta_duration_seconds : FloatProperty() # type: ignore
    meta_duration_format : StringProperty() # type: ignore

    max_volume_dB : FloatProperty() # type: ignore

    image_file : PointerProperty(type=bpy.types.Image) # type: ignore
    image_filename : StringProperty() # type: ignore
    image_texture : PointerProperty(type=bpy.types.Texture) # type: ignore
    
    curve_object : PointerProperty( # type: ignore
            type=bpy.types.Object, 
            poll=funcs.stm_curve_object_poll, 
            update=update_curve_object
        )
    
    curve_deform_axis : EnumProperty( # type: ignore
            items= (
                        ('1', "X", ""),
                        ('2', "Y", "")
                    ),
            default='2',
            update=update_curve_deform_axis
        )
    
    material_type : bpy.props.EnumProperty( # type: ignore
            items= (
                        ('raw', "Raw Texture", ""),
                        ('gradient', "Gradient", ""),
                        ('custom', "Custom", "")
                    ),
            description = "Choose material type",
            default='raw',
            update=update_stm_material
        )
    
    material_custom :  bpy.props.PointerProperty( # type: ignore
        type=bpy.types.Material,
        update=update_stm_material
    )
    
    
    

class STM_waveform_props(bpy.types.PropertyGroup): 

    stm_type : StringProperty() # type: ignore

    spectrogram_object : PointerProperty(type=bpy.types.Object) # type: ignore

    waveform_style : bpy.props.EnumProperty( # type: ignore
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

    

    waveform_resolution_choice : bpy.props.EnumProperty( # type: ignore
            items= (
                        ("default", "Default", ""),
                        ("custom", "Custom", "")
                    ),
            default="default",
            update=set_waveform_resolution_choice
        )

class STM_scene_props(bpy.types.PropertyGroup):

    ffmpegPath : StringProperty(default=os.path.join(addon_path, 'ffmpeg', 'ffmpeg.exe')) # type: ignore
    outputPath : StringProperty(default=os.path.join(addon_path, './output'), subtype="DIR_PATH") # type: ignore
    assetFilePath : StringProperty(default=os.path.join(addon_path, 'asset_files', 'asset_files_v41.blend')) # type: ignore

    presets_json_file : StringProperty(default=os.path.join(addon_path, 'presets_spectrogram.json')) # type: ignore
    eq_curve_presets_json_file : StringProperty(default=os.path.join(addon_path, 'presets_eq_curve.json')) # type: ignore
    gradient_presets_json_file : StringProperty(default=os.path.join(addon_path, 'presets_gradients.json')) # type: ignore
    # presets_geonodes : EnumProperty(  # type: ignore
    #         name='Choose a preset',
    #         items=generate_items_from_presets,
    #         update=apply_spectrogram_preset
    #     )
    
    

    # Progress
    progress : bpy.props.FloatProperty( # type: ignore
            name="Progress",
            subtype="PERCENTAGE",
            default=0,
            soft_min=0,
            soft_max=100,
            precision=0,
        )

    progress_label : bpy.props.StringProperty() # type: ignore


    stm_progress : bpy.props.FloatProperty( # type: ignore
            name="Progress",
            subtype="PERCENTAGE",
            soft_min=0,
            soft_max=100,
            precision=0,
            default=0,
        )

    # Spectrogram settings


    bool_output_path : bpy.props.EnumProperty( # type: ignore
            items= (
                        ("default", "Default", ""),
                        ("custom", "Custom", "")
                    ),
            default="default",
        )

    resolutionPreset : bpy.props.EnumProperty( # type: ignore
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
    userWidth : bpy.props.IntProperty(default=4096, subtype="PIXEL") # type: ignore
    userHeight : bpy.props.IntProperty(default=2048, subtype="PIXEL") # type: ignore

    bool_advanced_spectrogram_settings : bpy.props.BoolProperty(default=False) # type: ignore
    
    spectro_scale : bpy.props.EnumProperty( # type: ignore
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

    spectro_fscale : bpy.props.EnumProperty( # type: ignore
            items= (
                        ('lin', "Lin", ""),
                        ('log', "Log", "")
                    ),
            description = "Set frequency scale to use to generate spectrogram",
            name = "Frequency scale",
            default='lin'
        )

    spectro_colorMode : bpy.props.EnumProperty( # type: ignore
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

    spectro_drange : bpy.props.IntProperty(default=120, min=0, max=120)  # type: ignore


    # EEVEE settings
    bool_spectrogram_scene_settings : bpy.props.BoolProperty(default=False) # type: ignore
    force_standard_view_transform : BoolProperty(name='Set scene view tranform to "Standard"', default=True) # type: ignore
    force_eevee_AO : BoolProperty(name='Enable EEVEE Ambient Occlusion', default=True) # type: ignore
    force_eevee_BLOOM : BoolProperty(name='Enable EEVEE Bloom', default=True) # type: ignore
    disable_eevee_viewport_denoising : BoolProperty(name='Disable EEVEE Viewport Denoising', default=True) # type: ignore


    # bool_output_path = bpy.props.BoolProperty(default=False)

    bool_main_settings : bpy.props.BoolProperty(default=False) # type: ignore
    bool_geometry_settings : bpy.props.BoolProperty(default=False) # type: ignore
    bool_curve_deform : bpy.props.BoolProperty(default=False) # type: ignore


# -------------------------------------------------------------------
#   Register & Unregister
# -------------------------------------------------------------------


classes = [
    STM_OT_import_audio_file,
    STM_OT_reset_audio_file,
    STM_OT_reset_image_file,
    STM_OT_reset_spectrogram_settings,
    STM_OT_set_resolution_preset,
    STM_OT_add_audio_to_scene,
    STM_OT_open_image_folder,
    STM_OT_open_image,
    STM_OT_prompt_spectrogram_popup,
    STM_OT_generate_spectrogram_modal,
    STM_OT_select_stm_in_viewport,
    STM_OT_import_spectrogram_setup,
    STM_OT_add_waveform,
    STM_OT_add_spectrogram,
    STM_OT_remove_waveform,
    STM_OT_spectrogram_preset_popup,
    STM_OT_apply_spectrogram_preset,
    STM_OT_reset_spectrogram_full,
    STM_OT_reset_spectrogram_main_settings,
    STM_OT_reset_spectrogram_geometry_values,
    STM_OT_reset_eq_curve,
    STM_OT_reset_gradient,
    STM_OT_hello,
    STM_OT_refresh_stm_objects,

    STM_PT_spectrogram,
    STM_PT_spectrogram_settings,
    STM_PT_geometry_nodes_spectrogram,
    STM_PT_geometry_nodes_waveform,
    STM_PT_material_spectrogram,
    STM_PT_material_waveform,
    # STM_OT_dummy_op,
    # STM_OT_reload_previews,


    THUMB_OT_next_waveform_style,
    THUMB_OT_previous_waveform_style,
    THUMB_OT_next_spectrogram_style,
    THUMB_OT_previous_spectrogram_style,
    THUMB_OT_next_spectrogram_style_cylinder,
    THUMB_OT_previous_spectrogram_style_cylinder,
    THUMB_OT_next_spectrogram_setup,
    THUMB_OT_previous_spectrogram_setup,

    STM_spectrogram_props,
    STM_waveform_props,
    STM_scene_props,
]











def setup_new_preview_collection(name, dir):
    preview_collections[name] = bpy.utils.previews.new()
    preview_collections[name].images_location = os.path.join(addon_path, dir)



def register():

    import bpy.utils.previews

    

    setup_new_preview_collection(name="presets_setup", dir=r'.\icons\icons_setup_presets')
    setup_new_preview_collection(name="presets_geonodes", dir=r'.\icons\icons_geonode_presets')
    setup_new_preview_collection(name="presets_gradient", dir=r'.\icons\icons_gradient_presets')
    setup_new_preview_collection(name="presets_eq_curve", dir=r'.\icons\icons_eq_presets')
    setup_new_preview_collection(name="presets_waveform_style", dir=r'.\icons\icons_waveform_style')

    preview_collections["preview_image_enum"] = bpy.utils.previews.new()



    bpy.types.Scene.presets_setup = bpy.props.EnumProperty( # type: ignore
            name='Choose a preset',
            items=generate_previews('presets_setup'),
            # update=apply_spectrogram_preset
        )
    
    bpy.types.Object.preview_image_enum = EnumProperty( # type: ignore
            name='preview_image_enum',
            items=get_spectrogram_preview
        )
    
    bpy.types.Object.presets_geonodes = bpy.props.EnumProperty( # type: ignore
            name='presets_geonodes',
            # items=generate_previews('presets_geonodes'),
            items=generate_items_from_presets,
            update=apply_spectrogram_preset,
        )

    bpy.types.Object.presets_eq_curve = bpy.props.EnumProperty( # type: ignore
            name='presets_eq_curve',
            items=generate_previews('presets_eq_curve'),
            update=apply_eq_curve_preset,
        )

    bpy.types.Object.presets_gradient = bpy.props.EnumProperty(
            name='presets_gradient',
            items=generate_previews('presets_gradient'),
            update=apply_gradient_preset,
            # default='1-FFmpeg_intensity.png'
        )
    
    bpy.types.Object.presets_waveform_style = bpy.props.EnumProperty( # type: ignore
            name='presets_waveform_style',
            items=generate_previews('presets_waveform_style'),
            update=apply_waveform_style,
        )

    # for p in preview_collections:
    #     print(preview_collections[p])

    # print('01', preview_collections)

    for c in classes:
        bpy.utils.register_class(c)


    bpy.types.Scene.stm_settings = PointerProperty(type=STM_scene_props)
    bpy.types.Object.stm_spectro = PointerProperty(type=STM_spectrogram_props)
    bpy.types.Object.stm_waveform = PointerProperty(type=STM_waveform_props)


    
    
    



def unregister():

    for pcoll in preview_collections.values():
        bpy.utils.previews.remove(pcoll)

    preview_collections.clear()

    for c in classes:
        bpy.utils.unregister_class(c)


if __name__ == "__main__":
    register()
