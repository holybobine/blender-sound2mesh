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
    """This appears in the tooltip of the operator and in the generated docs"""
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

        bpy.context.scene.audio_file_path = self.filepath

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
    bl_options = {'UNDO'}

    def execute(self, context):

        audioPath = bpy.context.scene.audio_file_path
        outputPath = "C:/tmp/23_spectrogram/___output/"

        ffmpegPath = bpy.path.abspath("//ffmpeg/ffmpeg.exe")

        data_raw = funcs.ffmetadata(ffmpegPath, audioPath)
        volume_data_raw = funcs.ffvolumedetect(ffmpegPath, audioPath)

        artist = funcs.get_first_match_from_metadata(data_raw['metadata'], match='artist')
        album = funcs.get_first_match_from_metadata(data_raw['metadata'], match='album', exclude='artist')
        title = funcs.get_first_match_from_metadata(data_raw['metadata'], match='title')

        max_volume_dB = float(volume_data_raw['max_volume'])
        mean_volume_dB = float(volume_data_raw['mean_volume'])

        print('artist :', artist)
        print('album :', album)
        print('title :', title)
        print('max_volume_dB :', max_volume_dB)
        print('mean_volume_dB :', mean_volume_dB)


        spectrogram_filepath = funcs.ffshowspectrumpic(ffmpegPath, audioPath, outputPath)

        if spectrogram_filepath is not None:

            fps = bpy.context.scene.render.fps

            # generate soundstrip
            soundstrip = add_new_sound(context, audioPath, 0)
            duration_frames = soundstrip.frame_final_duration
            duration_seconds = duration_frames/fps

            # generate stm_obj
            action =  'GENERATE' if bpy.context.scene.stm_object == None else 'UPDATE'
            stm_obj = funcs.generate_spectrogram(audioPath, spectrogram_filepath, duration_seconds, max_volume_dB, action)


            context.scene.frame_end = duration_frames + fps
            set_playback_to_audioSync(context)
            frame_clip_in_sequencer()
            frame_all_timeline()





        return {'FINISHED'}

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

class STM_OT_add_waveform(Operator):
    """Add waveform"""
    bl_idname = "stm.add_waveform"
    bl_label = ''
    bl_options = {'UNDO'}

    def execute(self, context):

        print('-INF- add waveform')

        mesh = bpy.data.meshes.new('STM_waveform')
        obj = bpy.data.objects.new("STM_waveform", mesh)
        bpy.context.collection.objects.link(obj)

        mod = obj.modifiers.new("STM_waveform", 'NODES')
        mod.node_group = bpy.data.node_groups['STM_waveform']

        mod["Input_16"] = context.scene.stm_object
        mod["Input_15"] = bpy.data.materials['_waveform']

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

            p = bpy.context.scene.preset_spectrogram

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


        return {'FINISHED'}

class STM_OT_reset_stm_curve(Operator):
    """Reset STM curve"""
    bl_idname = 'stm.reset_stm_curve'
    bl_label='Reset STM curve'

    bl_options = {'UNDO'}

    def execute(self, context):
        print('-INF- reste STM curve')

        curve_node = bpy.data.node_groups['STM_spectrogram'].nodes['MACURVE']

        points = curve_node.mapping.curves[0].points

        # Keep only 2
        while len(points) > 2:
            points.remove(points[1]) #Can't remove at 0 (don't know why)

        while len(points) < 5:
            points.new(0,0)

        # Reset locations
        points[0].location = (0,0.5)
        points[1].location = (0.25,0.5)
        points[2].location = (0.5,0.5)
        points[3].location = (0.75,0.5)
        points[4].location = (1,0.5)

        curve_node.mapping.update()
        curve_node.update()


        return {'FINISHED'}
