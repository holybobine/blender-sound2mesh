import bpy
import os
import json


from bpy.props import *
from bpy.types import PropertyGroup

from . import funcs

def populate_resolution_prop_enum():
    enum_items = []
    for value in [512, 1024, 2048, 4096, 8192, 16384, 32768]:
        enum_items.append((str(value), str(value)+' px', ''))

    return enum_items

def populate_geonodes_presets(self, context):
    scn = context.scene

    presets_dir = os.path.join(addon_path, './geonodes_presets')

    enum_items = []

    for i, file in enumerate(os.listdir(presets_dir)):
        # if image.endswith('.json'):
        preset_fpath = os.path.join(presets_dir, file)

        with open(r'%s'%preset_fpath,'r') as f:
            preset_json=json.load(f)
        
        preset_name = preset_json['name']

        # enum_items.append((preset_fpath, preset_name, "Boob"))
        enum_items.append((preset_name, preset_name, ""))


    return enum_items

class STM_WAVEFORM_list_item(PropertyGroup):
    #name: StringProperty() -> Instantiated by default
    id: bpy.props.IntProperty() # type: ignore
    # stm_type: bpy.props.StringProperty() # type: ignore
    waveform_type: bpy.props.IntProperty() # type: ignore
    object: bpy.props.PointerProperty(type=bpy.types.Object) # type: ignore

class STM_spectrogram_props(PropertyGroup):
    stm_type : StringProperty() # type: ignore
    stm_status : StringProperty(default='init') # type: ignore

    stm_items : CollectionProperty(type=STM_WAVEFORM_list_item) # type: ignore
    # stm_items_active_index : IntProperty(update=funcs.select_in_viewport_from_waveform_list) # type: ignore
    stm_items_active_index : IntProperty(get=funcs.get_active_waveform_list_index, set=funcs.set_active_waveform_list_index) # type: ignore

    hide_viewport_base : BoolProperty(default = False, update=funcs.toggle_hide_viewport_base) # type: ignore

    presets_geonodes_proper : EnumProperty( # type: ignore
            name='Geonodes Presets',
            # items=generate_previews('presets_geonodes'),
            items=populate_geonodes_presets,
            # update=funcs.apply_spectrogram_preset_proper,
        )
    
    preset_geonodes_name : StringProperty() # type: ignore
    

    is_parented_to_spectrogram : BoolProperty(default = True, update=funcs.toggle_parent_spectrogram) # type: ignore

    panel_expand : BoolProperty(default = True) # type: ignore

    audio_file_path : StringProperty() # type: ignore # type: ignore
    audio_filename : StringProperty() # type: ignore
    audio_filename_display : StringProperty() # type: ignore
    audio_file : PointerProperty( # type: ignore
            type=bpy.types.Sound,
            update=funcs.update_audio_filename_display
        )
    
    audio_toggle : BoolProperty(update=funcs.toggle_audio_in_scene) # type: ignore

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

    gradient_custom : BoolProperty(default=False) # type: ignore

    gradient_type : EnumProperty( # type: ignore
            items= (
                        ('preset', "Preset", ""),
                        ('custom', "Custom Gradient", "")
                    ),
            default='preset',
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
    
    waveform_side_options : bpy.props.EnumProperty( # type: ignore
            items= (
                        ('a', "A", ""),
                        ('b', "B", ""),
                        ('ab', "AB", ""),
                    ),
            default='a',
            update=funcs.set_waveform_side_options
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


class STM_sound_sequence_props(PropertyGroup):
    spectrogram_object : PointerProperty(type=bpy.types.Object) # type: ignore

class STM_SPECTROGRAM_list_item(PropertyGroup):
    #name: StringProperty() -> Instantiated by default
    id: bpy.props.IntProperty() # type: ignore
    # stm_type: bpy.props.StringProperty() # type: ignore
    # waveform_type: bpy.props.IntProperty() # type: ignore
    object: bpy.props.PointerProperty(type=bpy.types.Object) # type: ignore

class STM_scene_props(PropertyGroup):

    doHandler : BoolProperty(default=True) # type: ignore
    doLiveSyncAudio : BoolProperty(  # type: ignore
        default=True,
        name='Audio live sync',
        description='Enables audio for selected spectrogram only'
    )

    active_object_tmp : StringProperty() # type: ignore
    
    stm_objects_list : CollectionProperty(type=STM_SPECTROGRAM_list_item) # type: ignore
    # stm_objects_list_active_index : IntProperty(update=funcs.select_in_viewport_from_spectro_list) # type: ignore
    # stm_objects_list_active_index : IntProperty(set=funcs.set_active_spectrogram_list_index) # type: ignore
    stm_objects_list_active_index : IntProperty(get=funcs.get_active_spectrogram_list_index, set=funcs.set_active_spectrogram_list_index) # type: ignore
    
    stm_settings_tab : EnumProperty( # type: ignore
            items= (
                        ('spectrogram', "Spectrogram", ""),
                        ('waveform', "Waveform", "")
                    ),
            name = "Settings tab",
            default='spectrogram'
        )

    ffmpegPath : StringProperty() # type: ignore

    ffmpegPath : StringProperty(default=os.path.join(addon_path, 'ffmpeg', 'ffmpeg.exe')) # type: ignore
    outputPath : StringProperty(default=os.path.join(addon_path, './output'), subtype="DIR_PATH") # type: ignore
    assetFilePath : StringProperty(default=os.path.join(addon_path, 'asset_files', 'asset_files_v49.blend')) # type: ignore

    object_count_tmp : IntProperty() # type: ignore

    is_alt_pressed : BoolProperty() # type: ignore
    is_shift_pressed : BoolProperty() # type: ignore
    is_ctrl_pressed : BoolProperty() # type: ignore

    is_scene_playing : BoolProperty() # type: ignore

    enable_audio_in_scene : BoolProperty( # type: ignore
        default=True, 
        update=funcs.toggle_enable_audio_in_scene,
        name='Enable audio',
        description='Enables audio in scene'
    )
    audio_volume : bpy.props.FloatProperty( # type: ignore
            name="Volume",
            description='Set volume for all audio in scene',
            subtype="PERCENTAGE",
            default=60,
            soft_min=0,
            soft_max=100,
            precision=0,
            update=funcs.update_scene_audio_volume,
        )
    
    show_display_viewport_icon : BoolProperty(default=True) # type: ignore
    show_disable_viewport_icon : BoolProperty(default=True) # type: ignore
    show_disable_render_icon : BoolProperty(default=True) # type: ignore


    presets_json_file : StringProperty(default=os.path.join(addon_path, 'presets_spectrogram.json')) # type: ignore

    presets_folder : StringProperty(default=os.path.join(addon_path, './geonodes_presets'), subtype='DIR_PATH') # type: ignore
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
    
    is_sequencer_open : bpy.props.BoolProperty(default=False) # type: ignore

    # Spectrogram settings

    bool_rename_stm_object : bpy.props.BoolProperty(default=True) # type: ignore


    bool_output_path : bpy.props.EnumProperty( # type: ignore
            items= (
                        ("default", "Default", ""),
                        ("custom", "Custom", "")
                    ),
            default="default",
        )

    bake_image_width : bpy.props.EnumProperty( # type: ignore
            name='',
            items= populate_resolution_prop_enum(),
            default='4096'
        )
    
    bake_image_height : bpy.props.EnumProperty( # type: ignore
            name='',
            items= populate_resolution_prop_enum(),
            default='2048'
        )
    
    bool_resolution : bpy.props.BoolProperty(default=False, update=funcs.set_default_bake_resolution) # type: ignore

    resolutionPreset : bpy.props.EnumProperty( # type: ignore
            items= (
                        ('1024x512', "1K", "1024x512"),
                        ('2048x1024', "2K", "2048x1024"),
                        ('4096x2048', "4K", "4096x2048"),
                        ('8192x2048', "8K", "8192x2048"),
                        ('16384x2048', "16K", "16384x2048"),
                        ('custom', "Custom", "")
                    ),
            name = "Resolution Preset",
            update=funcs.update_user_resolution, 
            default='4096x2048'
        )
    
    bake_image_format : EnumProperty( # type: ignore
            items= (
                        ('JPG', "JPG", "", 'IMAGE_DATA', 0),
                        ('PNG', "PNG", "", 'IMAGE_DATA', 1),
                    ),
            name = "File Format",
            default='PNG'
        )
    
    bake_image_compression : IntProperty(default=15, min=0, max=100, subtype='PERCENTAGE') # type: ignore
    
    bool_custom_resolution : bpy.props.BoolProperty(default=False) # type: ignore

    overwrite_image : bpy.props.BoolProperty(default=True) # type: ignore

    userWidth : bpy.props.IntProperty(default=4096, min=512, subtype="PIXEL") # type: ignore
    userHeight : bpy.props.IntProperty(default=2048, min=512, subtype="PIXEL") # type: ignore

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

    bool_use_audio_in_scene : bpy.props.BoolProperty(name='Import audio in scene', default=True) # type: ignore


    # EEVEE settings
    
    bool_spectrogram_scene_settings : bpy.props.BoolProperty(default=False) # type: ignore

    bool_eevee_settings : bpy.props.BoolProperty(default=False) # type: ignore
    
    force_eevee_AO : BoolProperty(name='Enable AO', default=True) # type: ignore
    # force_eevee_BLOOM : BoolProperty(name='Enable Bloom', default=True) # type: ignore
    disable_eevee_viewport_denoising : BoolProperty(name='Disable Viewport Denoising', default=True) # type: ignore
    force_standard_view_transform : BoolProperty(name='Set View Tranform to "Standard"', default=True) # type: ignore


    # bool_output_path = bpy.props.BoolProperty(default=False)

    bool_main_settings : bpy.props.BoolProperty(default=False) # type: ignore
    bool_geometry_settings : bpy.props.BoolProperty(default=False) # type: ignore
    bool_curve_deform : bpy.props.BoolProperty(default=False) # type: ignore


classes = [
    STM_WAVEFORM_list_item,
    STM_SPECTROGRAM_list_item,
    STM_spectrogram_props,
    STM_scene_props,
    STM_sound_sequence_props,
]


def register():
    for c in classes:
        bpy.utils.register_class(c)


    bpy.types.Scene.stm_settings = PointerProperty(type=STM_scene_props) # type: ignore
    bpy.types.SoundSequence.stm_settings = PointerProperty(type=STM_sound_sequence_props) # type: ignore
    bpy.types.Object.stm_spectro = PointerProperty(type=STM_spectrogram_props) # type: ignore
    # bpy.types.Screen.areas.is_stm_sequencer = BoolProperty(default=False)
    # bpy.types.Object.stm_waveform = PointerProperty(type=STM_waveform_props)


def unregister():
    for c in classes:
        bpy.utils.unregister_class(c)