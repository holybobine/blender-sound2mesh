import bpy
import os
import json

from bpy.props import *
from sys import path

from . import funcs



addon_path = os.path.dirname(__file__)
preview_collections = {}

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
            thumb = pcoll.load(image, filepath, 'IMAGE')
            enum_items.append((image, item_name.capitalize(), item_name.capitalize(), thumb.icon_id, i))

    return enum_items

def get_spectrogram_preview(self, context):
    pcoll = preview_collections["preview_image_enum"]

    stm_obj = funcs.get_stm_object(context.object)

    

    if stm_obj.stm_spectro.image_file == None:
        item_name = 'no image'
        filepath = os.path.join(addon_path, './icons/misc/no_image.png')
    else:
        item_name = stm_obj.stm_spectro.image_file.name
        filepath = stm_obj.stm_spectro.image_file.filepath

    enum_items = []        

    if filepath in pcoll:
        thumb = pcoll[filepath]
    else:
        thumb = pcoll.load(filepath, filepath, 'IMAGE', force_reload=True)

    enum_items.append((item_name, item_name, "", thumb.icon_id, 0))

    return enum_items

def generate_items_from_presets(self, context):

    scn = context.scene

    with open(r'%s'%scn.stm_settings.presets_json_file,'r') as f:
        presets=json.load(f)

    enum_items = []

    for p in presets:
        enum_items.append((p, presets[p]["name"], ""))

    # print(enum_items)

    return enum_items





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
    setup_new_preview_collection(name="presets_waveform_style_AB", dir=r'.\icons\icons_waveform_style_AB')
    
    setup_new_preview_collection(name="icons", dir=r'.\icons')
    generate_previews('icons')

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
            # update=funcs.apply_spectrogram_preset,
        )
    
    

    bpy.types.Object.presets_eq_curve = bpy.props.EnumProperty( # type: ignore
            name='presets_eq_curve',
            items=generate_previews('presets_eq_curve'),
            update=funcs.apply_eq_curve_preset_proper,
        )

    bpy.types.Object.presets_gradient = bpy.props.EnumProperty(
            name='presets_gradient',
            items=generate_previews('presets_gradient'),
            update=funcs.apply_gradient_preset,
            # default='1-FFmpeg_intensity.png'
        )

    bpy.types.Object.presets_waveform_style = bpy.props.EnumProperty( # type: ignore
            name='Waveform Shape',
            items=generate_previews('presets_waveform_style'),
            update=funcs.apply_waveform_style,
        )
    
    bpy.types.Scene.presets_waveform_style_AB = bpy.props.EnumProperty( # type: ignore
            name='Waveform Shape',
            items=generate_previews('presets_waveform_style_AB'),
            update=funcs.apply_waveform_style,
        )
    

def unregister():
    for pcoll in preview_collections.values():
            bpy.utils.previews.remove(pcoll)

    preview_collections.clear()