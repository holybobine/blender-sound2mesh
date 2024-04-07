import bpy
import os


from bpy.props import *
from bpy.types import PropertyGroup

from . import funcs


class STM_UL_list_item(PropertyGroup):
    #name: StringProperty() -> Instantiated by default
    id: bpy.props.IntProperty() # type: ignore
    stm_type: bpy.props.StringProperty() # type: ignore
    waveform_type: bpy.props.IntProperty() # type: ignore

class STM_spectrogram_props(PropertyGroup):
    stm_type : StringProperty() # type: ignore
    stm_status : StringProperty() # type: ignore

    stm_items : CollectionProperty(type=STM_UL_list_item) # type: ignore
    stm_items_active_index : IntProperty(update=funcs.select_obj_from_list) # type: ignore

    audio_file_path : StringProperty() # type: ignore # type: ignore
    audio_filename : StringProperty() # type: ignore
    audio_file : PointerProperty(type=bpy.types.Sound, update=funcs.update_metadata) # type: ignore

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
            update=funcs.update_curve_object
        )
    
    curve_deform_axis : EnumProperty( # type: ignore
            items= (
                        ('1', "X", ""),
                        ('2', "Y", "")
                    ),
            default='2',
            update=funcs.update_curve_deform_axis
        )
    
    material_type : bpy.props.EnumProperty( # type: ignore
            items= (
                        ('raw', "Image", ""),
                        ('gradient', "Gradient", ""),
                        ('emission', "Emission", ""),
                        ('custom', "Custom", "")
                    ),
            description = "Choose material type",
            default='raw',
            update=funcs.update_stm_material
        )
    
    material_custom :  PointerProperty( # type: ignore
        type=bpy.types.Material,
        update=funcs.update_stm_material
    )

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
            update=funcs.set_waveform_style
        )

    

    waveform_resolution_choice : bpy.props.EnumProperty( # type: ignore
            items= (
                        ("default", "Default", ""),
                        ("custom", "Custom", "")
                    ),
            default="default",
            update=funcs.set_waveform_resolution_choice
        )
    

addon_path = os.path.dirname(__file__)

class STM_scene_props(PropertyGroup):

    ffmpegPath : StringProperty() # type: ignore

    ffmpegPath : StringProperty(default=os.path.join(addon_path, 'ffmpeg', 'ffmpeg.exe')) # type: ignore
    outputPath : StringProperty(default=os.path.join(addon_path, './output'), subtype="DIR_PATH") # type: ignore
    assetFilePath : StringProperty(default=os.path.join(addon_path, 'asset_files', 'asset_files_v43.blend')) # type: ignore

    presets_json_file : StringProperty(default=os.path.join(addon_path, 'presets_spectrogram.json')) # type: ignore
    eq_curve_presets_json_file : StringProperty(default=os.path.join(addon_path, 'presets_eq_curve.json')) # type: ignore
    gradient_presets_json_file : StringProperty(default=os.path.join(addon_path, 'presets_gradients.json')) # type: ignore    

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


classes = [
    STM_UL_list_item,
    STM_spectrogram_props,
    STM_scene_props,
]


def register():
    for c in classes:
        bpy.utils.register_class(c)


    bpy.types.Scene.stm_settings = PointerProperty(type=STM_scene_props)
    bpy.types.Object.stm_spectro = PointerProperty(type=STM_spectrogram_props)
    # bpy.types.Object.stm_waveform = PointerProperty(type=STM_waveform_props)


def unregister():
    for c in classes:
        bpy.utils.unregister_class(c)