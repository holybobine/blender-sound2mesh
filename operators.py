import bpy

from bpy.types import Operator
from bpy_extras.io_utils import ImportHelper
from bpy.props import (
    IntProperty,
    BoolProperty,
    StringProperty,
    CollectionProperty,
    PointerProperty,
    EnumProperty,
)

import json

import funcs
from funcs import *



class STM_OT_hello(bpy.types.Operator):
    """Hello"""
    bl_idname = 'stm.hello'
    bl_label='Hello'

    bl_options = {'UNDO'}

    def execute(self, context):
        print('hello there my dude')


        return {'FINISHED'}

class STM_OT_import_audio_file(Operator, ImportHelper):
    """Select an audio file to import"""
    bl_idname = "stm.import_audio_file"  # important since its how bpy.ops.import_test.some_data is constructed
    bl_label = "Import audio file"

    # ImportHelper mixin class uses this
    filename_ext = ".txt"

    filter_glob: StringProperty(
        default="*" + ";*".join(bpy.path.extensions_audio),
        options={'HIDDEN'},
        maxlen=255,  # Max internal buffer length, longer would be clamped.
    )

    def execute(self, context):

        scn = context.scene    # print(scn.audio_file_path)
        filepath = self.filepath

        scn.audio_file_path = self.filepath

        mdata = funcs.ffmetadata(scn.ffmpegPath, self.filepath)

        if mdata != None:
            scn.title = funcs.get_first_match_from_metadata(mdata['metadata'], match='title')
            scn.album = funcs.get_first_match_from_metadata(mdata['metadata'], match='album', exclude='artist')
            scn.artist = funcs.get_first_match_from_metadata(mdata['metadata'], match='artist')

            scn.title = os.path.basename(scn.audio_file_path) if scn.title == '' else scn.title
            scn.album = '[unkown]' if scn.album == '' else scn.album
            scn.artist = '[unkown]' if scn.artist == '' else scn.artist

        funcs.redraw_all_viewports()

        return {'FINISHED'}

class STM_OT_reset_audio_file(Operator):
    """Reset audio file"""
    bl_idname = "stm.reset_audio_file"  # important since its how bpy.ops.import_test.some_data is constructed
    bl_label = "Reset audio file"



    def execute(self, context):

        scn = context.scene

        scn.audio_file_path = ''
        scn.title = ''
        scn.album = ''
        scn.artist = ''

        funcs.redraw_all_viewports()

        return {'FINISHED'}

class STM_OT_add_audio_to_scene(Operator):
    """Apply preset"""
    bl_idname = "stm.add_audio_to_scene"
    bl_label = "Add audio to scene"
    bl_options = {'UNDO'}

    def execute(self, context):

        print('-INF- add audio to scene')

        return {'FINISHED'}

class STM_OT_open_image_folder(Operator):
    """Apply preset"""
    bl_idname = "stm.open_image_folder"
    bl_label = "Open image folder"
    bl_options = {'UNDO'}

    def execute(self, context):

        print('-INF- open image folder')

        return {'FINISHED'}


class STM_OT_generate_spectrogram(Operator):
    """Generate spectrogram"""
    bl_idname = "stm.generate_spectrogram"
    bl_label = "Generate spectrogram"
    bl_options = {'REGISTER', 'UNDO'}


    def draw(self, context):

        layout = self.layout
        scn = context.scene

        layout.separator()

        split = layout.split(factor=0.3)
        col_L = split.column()
        col_R = split.column()


        col_L.label(text='Audio file :', icon='FILE_SOUND')

        box = col_R.box()
        split = box.split(factor=0.2)
        col1 = split.column(align=True)
        col2 = split.column(align=True)
        col1.label(text='Title :')
        col2.label(text=scn.title)
        col1.label(text='Artist :')
        col2.label(text=scn.artist)
        col1.label(text='Album :')
        col2.label(text=scn.album)
        col1.enabled = False

        layout.separator()

        split = layout.split(factor=0.3)
        col_L = split.column()
        col_R = split.column(align=True)


        col_L.label(text='Spectrogram:', icon='TEXTURE')


        row = col_R.row(align=True)
        row.scale_y=1.5
        row.prop_enum(scn, 'resolutionPreset', '1024x512')
        row.prop_enum(scn, 'resolutionPreset', '2048x1024')
        row.prop_enum(scn, 'resolutionPreset', '4096x2048')
        row.prop_enum(scn, 'resolutionPreset', '8192x4096')
        row.prop_enum(scn, 'resolutionPreset', '16384x8192')
        row = col_R.row(align=True)
        row.scale_y=1.5
        row.prop_enum(scn, 'resolutionPreset', 'custom', text='Custom Resolution')

        if scn.resolutionPreset == 'custom':
            #col = box.column(align=True)
            ccol = col_R.column(align=True)
            ccol.prop(scn, 'userWidth', text='Width')
            ccol.prop(scn, 'userHeight', text='Height')

        col_R.separator()

        box = col_R.box()
        row = box.row()
        # row.label(text='Main Settings', icon='OPTIONS')
        row.prop(scn, 'bool_advanced_spectrogram_settings', text='Advanced Settings', icon='TRIA_DOWN' if scn.bool_advanced_spectrogram_settings else 'TRIA_RIGHT', emboss=False)

        if scn.bool_advanced_spectrogram_settings:
            split = box.split(factor=0.5)
            col1 = split.column()
            col2 = split.column()
            col1.label(text='Intensity Scale :')
            col2.prop(scn, 'scale', text='')
            col1.label(text='Frequency Scale :')
            col2.prop(scn, 'fscale', text='')
            col1.label(text='Color Mode :')
            col2.prop(scn, 'colorMode', text='')
            col1.label(text='Dynamic Range :')
            col2.prop(scn, 'drange', text='')

        layout.separator()

    def invoke(self, context, event):

        return context.window_manager.invoke_props_dialog(self, width=350)

    def execute(self, context):

        scn = bpy.context.scene

        audioPath = scn.audio_file_path
        outputPath = "C:/tmp/23_spectrogram/___output/"

        ffmpegPath = scn.ffmpegPath

        data_raw = funcs.ffmetadata(ffmpegPath, audioPath)
        volume_data_raw = funcs.ffvolumedetect(ffmpegPath, audioPath)
        astats = funcs.ffastats(ffmpegPath, audioPath)


        artist, album, title = '', '', ''

        if data_raw != None:
            artist = funcs.get_first_match_from_metadata(data_raw['metadata'], match='artist')
            album = funcs.get_first_match_from_metadata(data_raw['metadata'], match='album', exclude='artist')
            title = funcs.get_first_match_from_metadata(data_raw['metadata'], match='title')

        max_volume_dB = float(volume_data_raw['max_volume'])
        mean_volume_dB = float(volume_data_raw['mean_volume'])
        peak_level_dB = round(float(astats['Peak level dB']), 2)

        print('artist :', artist)
        print('album :', album)
        print('title :', title)
        print('max_volume_dB :', peak_level_dB)


        w = 0
        h = 0

        if scn.resolutionPreset == 'custom':
            w = scn.userWidth
            h = scn.userHeight
        else:
            w = int(scn.resolutionPreset.split('x')[0])
            h = int(scn.resolutionPreset.split('x')[1])

        spectrogram_filepath = funcs.ffshowspectrumpic(
            ffmpegPath,
            audioPath,
            outputPath,
            width=w,
            height=h,
            scale=scn.scale,
            fscale=scn.fscale,
            colorMode=scn.colorMode,
            drange=scn.drange,
            limit=max_volume_dB
        )

        if spectrogram_filepath is not None:



            peak_brightness = int(funcs.ffsignalstats(ffmpegPath, spectrogram_filepath, 'YMAX'))

            fps = bpy.context.scene.render.fps

            # generate soundstrip
            soundstrip = add_new_sound(context, audioPath, 0)
            duration_frames = soundstrip.frame_final_duration
            duration_seconds = duration_frames/fps

            # generate stm_obj
            stm_obj = funcs.generate_spectrogram(audioPath, spectrogram_filepath, duration_seconds, peak_level_dB, peak_brightness)


            context.scene.frame_end = duration_frames + fps
            set_playback_to_audioSync(context)
            frame_clip_in_sequencer()
            frame_all_timeline()





        return {'FINISHED'}

class WM_OT_newSpectrogram(bpy.types.Operator, ImportHelper):
    """Select audio file to be used"""
    bl_idname = 'wm.new_spectrogram'
    bl_label = 'Select Audio File'

    #queue = bpy.props.StringProperty(None)

    def execute(self, context):

        #by default, create new spectrogram
        context.scene.userAction='createNew'

        #if object already selected, and contains 'STM_spectrogram' or 'STM_waveform' modifier, rebuild
        if check_if_only_active_obj_selected():
            if check_for_modifier('STM_spectrogram') or check_for_modifier('STM_waveform'):
                context.scene.userAction='rebuild'


        bpy.ops.stm.create_new_stm('INVOKE_DEFAULT')



        return {'FINISHED'}

    def draw(self, context):

        layout = self.layout

        layout.separator()

        row = layout.row()

        split = row.split(factor=0.3)
        col_1 = split.column()
        col_2 = split.column(align=True)

        col_1.label(text='Audio File :', icon='FILE_SOUND')
        box = col_2.box()
        box.label(text=os.path.basename(context.scene.audioFilePath))

        layout.separator()


        col = layout.column()

        split = col.split(factor=0.3)
        col_1 = split.column()
        col_2 = split.column(align=True)

        col_1.label(text='Resolution :', icon='TEXTURE')


        row = col_2.row(align=True)
        row.scale_y=1.5
        row.prop_enum(context.scene, 'resolutionPreset', '1K')
        row.prop_enum(context.scene, 'resolutionPreset', '2K')
        row.prop_enum(context.scene, 'resolutionPreset', '4K')
        row.prop_enum(context.scene, 'resolutionPreset', '8K')
        row.prop_enum(context.scene, 'resolutionPreset', '16K')
        row = col_2.row(align=True)
        row.scale_y=1.5
        row.prop_enum(context.scene, 'resolutionPreset', 'custom', text='Custom')

        if context.scene.resolutionPreset == 'custom':
                #col = box.column(align=True)
                ccol = col_2.column(align=True)
                ccol.prop(context.scene, 'userWidth')
                ccol.prop(context.scene, 'userHeight')

        col_2.separator()

        outputPath = context.scene.outputPath

        dirSize = get_dir_size(outputPath)
        dirSize = bytesto(dirSize, 'm')

        col = col_2.column()

        row = col.row()
        row.label(text='Diskspace used : ')
        row.label(text=dirSize)

        col.operator("user.open_image_folder", icon="FILEBROWSER")

        layout.separator()


    def invoke(self, context, event):

        return context.window_manager.invoke_props_dialog(self)



class STM_OT_select_stm_in_viewport(Operator):
    """"""
    bl_idname = "stm.select_stm_in_viewport"
    bl_label = 'Select Spectrogram in Viewport'
    bl_options = {'UNDO'}

    def execute(self, context):

        obj = context.scene.stm_object

        bpy.ops.object.select_all(action='DESELECT')

        obj.select_set(True)
        bpy.context.view_layer.objects.active = obj

        return {'FINISHED'}

class STM_OT_add_spectrogram(Operator):
    """Add a new spectrogram object"""
    bl_idname = "stm.add_spectrogram"
    bl_label = ''
    bl_options = {'UNDO'}

    def execute(self, context):

        print('-INF- add spectrogram object')

        assetFile = bpy.context.scene.assetFilePath

        append_from_blend_file(assetFile, 'NodeTree', 'STM_spectrogram')
        append_from_blend_file(assetFile, 'Material', 'STM_rawTexture')

        mesh = bpy.data.meshes.new('STM_spectrogram')
        obj = bpy.data.objects.new("STM_spectrogram", mesh)
        bpy.context.collection.objects.link(obj)

        mod = obj.modifiers.new("STM_spectrogram", 'NODES')
        mod.node_group = bpy.data.node_groups['STM_spectrogram']

        mod["Input_12"] = bpy.data.materials['STM_rawTexture']

        bpy.ops.object.select_all(action='DESELECT')

        obj.select_set(True)
        bpy.context.view_layer.objects.active = obj

        print('-INF- added spectrogram object <%s>'%obj.name)

        return {'FINISHED'}

class STM_OT_add_waveform(Operator):
    """Add waveform"""
    bl_idname = "stm.add_waveform"
    bl_label = ''
    bl_options = {'UNDO'}

    def execute(self, context):

        print('-INF- add waveform')

        assetFile = bpy.context.scene.assetFilePath

        stm_object = context.object if is_stm_object_selected() else None


        append_from_blend_file(assetFile, 'NodeTree', 'STM_waveform')
        append_from_blend_file(assetFile, 'Material', '_waveform')

        mesh = bpy.data.meshes.new('STM_waveform')
        obj = bpy.data.objects.new("STM_waveform", mesh)
        bpy.context.collection.objects.link(obj)

        mod = obj.modifiers.new("STM_waveform", 'NODES')
        mod.node_group = bpy.data.node_groups['STM_waveform']


        mod["Input_15"] = bpy.data.materials['_waveform']

        if stm_object != None:
            mod["Input_16"] = stm_object

        bpy.ops.object.select_all(action='DESELECT')

        obj.select_set(True)
        bpy.context.view_layer.objects.active = obj

        print('-INF- added waveform object <%s>'%obj.name)

        return {'FINISHED'}

class STM_OT_remove_waveform(Operator):
    """Remove waveform"""
    bl_idname = "stm.remove_waveform"
    bl_label = 'Remove ?'
    bl_options = {'UNDO'}


    # def invoke(self, context, event):
    #     return context.window_manager.invoke_confirm(self, event)

    def execute(self, context):

        idx = bpy.context.scene.stm_obj_list_index
        obj = context.scene.objects[idx]
        obj_name = obj.name

        bpy.data.objects.remove(bpy.context.scene.objects[idx], do_unlink = True)
        print('-INF- removed waveform object <%s>'%obj_name)



        return {'FINISHED'}

class STM_OT_apply_preset_spectrogram_gn(Operator):
    """Apply preset"""
    bl_idname = 'stm.apply_preset_spectrogram_gn'
    bl_label='Apply preset'

    bl_options = {'UNDO'}

    def execute(self, context):

        with open(r'%s'%bpy.context.scene.presets_json_file,'r') as f:
            presets=json.load(f)

            p = bpy.context.scene.preset_thumbnails.replace('.png', '')


            values = presets[p]["preset"]


            print(values)

        funcs.apply_spectrogram_preset(values)


        return {'FINISHED'}

class STM_OT_reset_spectrogram_gn(Operator):
    """Reset"""
    bl_idname = 'stm.reset_spectrogram_gn'
    bl_label='Reset'

    bl_options = {'UNDO'}

    def execute(self, context):
        preset = {}

        funcs.apply_spectrogram_preset(preset)
        funcs.reset_stm_curve('reset_5')


        return {'FINISHED'}


class STM_OT_reset_gn_geometry_values(Operator):
    """Reset"""
    bl_idname = 'stm.reset_gn_geometry_values'
    bl_label=''

    bl_options = {'UNDO'}

    def execute(self, context):
        preset = {
            'Size X': 'reset',
            'Size Y': 'reset',
            'Resolution X': 'reset',
            'Resolution Y': 'reset',
            'Base Height': 'reset',
            'Smooth': 'reset',
            'Smooth Level': 'reset',
            'Noise': 'reset',
            'Noise Scale': 'reset',
            'Height Multiplier': 'reset',
            'Contrast': 'reset',
        }

        funcs.apply_spectrogram_preset(preset)


        return {'FINISHED'}

class STM_OT_apply_eq_curve_preset(Operator):
    """Apply EQ curve preset"""
    bl_idname = 'stm.reset_stm_curve'
    bl_label='Reset STM curve'

    bl_options = {'UNDO'}

    eq_curve_preset: bpy.props.EnumProperty(
            items= (
                    ('reset_5', "Reset 5", ""),
                    ('reset_10', "Reset 10", ""),
                    ('flatten_edges', "Flatten Edges", ""),
                    ('lowpass', "Low Pass", ""),
                    ('highpass', "High Pass", ""),
                ),
                default='reset_5'
    )

    def execute(self, context):

        with open(r'%s'%bpy.context.scene.eq_curve_presets_json_file,'r') as f:
            presets=json.load(f)

        funcs.reset_stm_curve(self.eq_curve_preset)

        return {'FINISHED'}


class STM_OT_reset_gradient(Operator):
    """Reset gradient"""
    bl_idname = 'stm.reset_gradient'
    bl_label ='Reset gradient'

    bl_options = {'UNDO'}

    def execute(self, context):
        print('-INF- Reset gradient')

        cr_node = bpy.data.materials['STM_rawTexture'].node_tree.nodes['STM_gradient']
        cr = cr_node.color_ramp

        #RESET COLOR RAMP
        #Delete all stops, starting from the end, until 2 remain

        for i in range (0, len(cr.elements)-2):
            cr.elements.remove(cr.elements[len(cr.elements)-1])

        #move and set color for remaining two stops
        cr.elements[0].position = (0)
        cr.elements[0].color = (0,0,0,1)

        cr.elements[1].position = (1)
        cr.elements[1].color = (1,1,1,1)

        return {'FINISHED'}


class THUMB_OT_next_preset(Operator):
    """Tooltip"""
    bl_idname = "preset.next"
    bl_label = "Move to next item in property list"

    def execute(self, context):

        items = [item.identifier for item in context.scene.bl_rna.properties['preset_thumbnails'].enum_items]
        idx = items.index(context.scene.preset_thumbnails)

        idx += 1
        if idx == len(items):
            idx = 0

        context.scene.preset_thumbnails = items[idx]


        return {'FINISHED'}

class THUMB_OT_prev_preset(Operator):
    """Tooltip"""
    bl_idname = "preset.prev"
    bl_label = "Move to previous item in property list"

    def execute(self, context):

        items = [item.identifier for item in context.scene.bl_rna.properties['preset_thumbnails'].enum_items]
        idx = items.index(context.scene.preset_thumbnails)

        idx -= 1
        if idx < 0:
            idx = len(items)-1

        context.scene.preset_thumbnails = items[idx]


        return {'FINISHED'}
