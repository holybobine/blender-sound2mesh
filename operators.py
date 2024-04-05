import bpy

from bpy.types import Operator
from bpy_extras.io_utils import ImportHelper
from bpy.props import *

import datetime
import json
import os
from . import funcs
# from . funcs import *

class STM_OT_hello(bpy.types.Operator):
    """Hello"""
    bl_idname = 'stm.hello'
    bl_label='Hello'

    bl_options = {'UNDO'}

    def execute(self, context):
        print('hello there my dude')


        return {'FINISHED'}

class STM_OT_dummy_op(bpy.types.Operator):
    """"""
    bl_idname = 'stm.dummy'
    bl_label=''


    def execute(self, context):
        print('dummy')


        return {'FINISHED'}
    
class STM_OT_reload_previews(bpy.types.Operator):
    """"""
    bl_idname = 'stm.reload_previews'
    bl_label=''


    def execute(self, context):
        print('-INF- reload previews')

        funcs.generate_previews()


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
    ) # type: ignore

    def execute(self, context):

        scn = context.scene
        obj = context.object
        filepath = self.filepath

        # obj.audio_file_path = self.filepath
        

        sound = bpy.data.sounds.load(self.filepath, check_existing=True)

        obj.stm_spectro.audio_file = sound
        obj.stm_spectro.audio_filename = os.path.basename(self.filepath)

        funcs.update_metadata(self, context)

        # mdata = funcs.ffmetadata(scn.ffmpegPath, sound)

        # title = funcs.get_first_match_from_metadata(mdata['metadata'], match='title')
        # album = funcs.get_first_match_from_metadata(mdata['metadata'], match='album', exclude='artist')
        # artist = funcs.get_first_match_from_metadata(mdata['metadata'], match='artist')
        # duration = mdata['duration']


        # obj.title = os.path.basename(obj.audio_file_path) if title == '' else title
        # obj.album = '[unkown]' if album == '' else album
        # obj.artist = '[unkown]' if artist == '' else artist
        # # scn.duration = str(datetime.timedelta(seconds=round(duration)))
        # obj.duration_seconds = duration
        # obj.duration_format = funcs.seconds_to_timestring(duration)

        # # print(f'{duration = }')

        # funcs.redraw_all_viewports()

        return {'FINISHED'}

class STM_OT_reset_audio_file(Operator):
    """Reset audio file"""
    bl_idname = "stm.reset_audio_file"  # important since its how bpy.ops.import_test.some_data is constructed
    bl_label = "Reset audio file"
    bl_options = {'UNDO'}



    def execute(self, context):

        scn = context.scene
        obj = context.object

        obj.stm_spectro.audio_file = None


        # seq = scn.sequence_editor

        # if not seq:
        #     scn.sequence_editor_create()
        # for strip in seq.sequences:
        #     seq.sequences.remove(strip)

        funcs.redraw_all_viewports()

        return {'FINISHED'}
    
class STM_OT_reset_image_file(Operator):
    """Clear Image File"""
    bl_idname = "stm.reset_image_file"
    bl_label = "Clear Image"
    bl_options = {'UNDO'}



    def execute(self, context):

        obj = context.object
        obj.stm_spectro.image_file = None
        stm_modifier = obj.modifiers["STM_spectrogram"]


        stm_modifier["Input_2"] = None
        stm_modifier["Input_12"] = None

        stm_modifier.show_viewport = False
        stm_modifier.show_viewport = True

        funcs.redraw_all_viewports()

        return {'FINISHED'}

class STM_OT_reset_spectrogram_settings(Operator):
    """Reset spectrogram_settings"""
    bl_idname = "stm.reset_spectrogram_settings"  # important since its how bpy.ops.import_test.some_data is constructed
    bl_label = "Reset spectrogram_settings"



    def execute(self, context):

        print('-INF- reset spectrogram settings')
        scn = context.scene

        scn.spectro_scale = 'log'
        scn.spectro_fscale = 'lin'
        scn.spectro_colorMode = 'intensity'
        scn.spectro_drange = 120

        return {'FINISHED'}

class STM_OT_add_audio_to_scene(Operator):
    """Set sound in scene"""
    bl_idname = "stm.set_sound_in_scene"
    bl_label = "Set sound in scene"
    bl_options = {'UNDO'}

    def execute(self, context):

        print('-INF- add audio to scene')

        funcs.set_sound_in_scene(
            filepath=context.object.audio_file_path,
            offset=0
        )

        funcs.frame_clip_in_sequencer()

        return {'FINISHED'}

class STM_OT_open_image_folder(Operator):
    """Open image folder"""
    bl_idname = "stm.open_image_folder"
    bl_label = ""
    bl_options = {'UNDO'}

    def execute(self, context):
        image_path = context.object.modifiers['STM_spectrogram']['Input_2'].filepath

        if os.path.exists(image_path):
            print('-INF- open image folder')
            dir_path = os.path.dirname(image_path)
            os.startfile(dir_path)
        else:
            print(f'-ERR- can\'t open folder for file "{image_path}"')

        return {'FINISHED'}

class STM_OT_open_image(Operator):
    """Open image"""
    bl_idname = "stm.open_image"
    bl_label = ""
    bl_options = {'UNDO'}

    def execute(self, context):
        image_path = context.object.modifiers['STM_spectrogram']['Input_2'].filepath

        if os.path.exists(image_path):
            print('-INF- open image')
            os.startfile(image_path)
        else:
            print(f'-ERR- can\'t open file "{image_path}"')

        return {'FINISHED'}
    

class STM_OT_set_resolution_preset(Operator):
    """1024x512"""
    bl_idname = "stm.set_resolution_preset"
    bl_label = ""

    resolution: bpy.props.StringProperty() # type: ignore

    def execute(self, context):

        width = int(self.resolution.split('x')[0])
        height = int(self.resolution.split('x')[1])

        # print(f'-INF- set resolution to ({width}x{height})')
        context.scene.stm_settings.userWidth = width
        context.scene.stm_settings.userHeight = height

        return {'FINISHED'}

class STM_OT_prompt_spectrogram_popup(Operator):
    """Generate spectrogram"""
    bl_idname = "stm.prompt_spectrogram_popup"
    bl_label = "Generate spectrogram"
    bl_options = {'UNDO'}


    def draw(self, context):

        layout = self.layout
        scn = context.scene
        obj = context.object

        layout.separator()

        split_fac = 0.3

        split = layout.split(factor=split_fac)
        col_L = split.column()
        col_R = split.column()


        col_L.label(text='Audio file :', icon='FILE_SOUND')

        box = col_R.box()
        split = box.split(factor=split_fac)
        col1 = split.column(align=True)
        col2 = split.column(align=True)
        col1.label(text='Title :')
        col2.label(text=obj.stm_spectro.meta_title)
        col1.label(text='Artist :')
        col2.label(text=obj.stm_spectro.meta_artist)
        col1.label(text='Album :')
        col2.label(text=obj.stm_spectro.meta_album)
        col1.label(text='Duration :')
        col2.label(text=obj.stm_spectro.meta_duration_format)
        col1.enabled = False

        if obj.stm_spectro.meta_duration_seconds > 1200:
            bbox = box.box()
            row = bbox.row()
            col1=row.column(align=True)
            col2=row.column(align=True)
            col1.label(text='', icon='ERROR')
            col1.scale_y = 2
            col2.label(text='Long audio file.')
            col2.label(text='Generation may take a while...')


        layout.separator()

        split = layout.split(factor=split_fac)
        col_L = split.column()
        col_R = split.column(align=True)


        col_L.label(text='Spectrogram:', icon='TEXTURE')


        

        split = col_R.split(factor=0.3)
        col1 = split.column(align=True)
        col1.alignment = 'RIGHT'
        col2 = split.column(align=True)

        
        row = col1.row()
        row.scale_y = 1.5
        row.label(text='')
        col1.label(text='Resolution X')
        col1.label(text='Y')

        row = col2.row(align=True)
        row.scale_y = 1.5
        row.operator('stm.set_resolution_preset', text='1K').resolution = '1024x512'
        row.operator('stm.set_resolution_preset', text='2K').resolution = '2048x1024'
        row.operator('stm.set_resolution_preset', text='4K').resolution = '4096x2048'
        row.operator('stm.set_resolution_preset', text='8K').resolution = '8192x4096'
        row.operator('stm.set_resolution_preset', text='16K').resolution = '16384x8192'

        ccol = col2.column(align=True)
        ccol.prop(scn.stm_settings, 'userWidth', text='')
        ccol.prop(scn.stm_settings, 'userHeight', text='')

        col_R.separator()

        box = col_R.box()
        row = box.row()
        # row.label(text='Main Settings', icon='OPTIONS')
        row.prop(scn.stm_settings, 'bool_advanced_spectrogram_settings', text='Advanced Settings', icon='TRIA_DOWN' if scn.stm_settings.bool_advanced_spectrogram_settings else 'TRIA_RIGHT', emboss=False)
        row.operator('stm.reset_spectrogram_settings', text='', icon='FILE_REFRESH')
        if scn.stm_settings.bool_advanced_spectrogram_settings:
            split = box.split(factor=0.5)
            col1 = split.column()
            col2 = split.column()
            col1.label(text='Intensity Scale :')
            col2.prop(scn.stm_settings, 'spectro_scale', text='')
            col1.label(text='Frequency Scale :')
            col2.prop(scn.stm_settings, 'spectro_fscale', text='')
            col1.label(text='Color Mode :')
            col2.prop(scn.stm_settings, 'spectro_colorMode', text='')
            col1.label(text='Dynamic Range :')
            col2.prop(scn.stm_settings, 'spectro_drange', text='')

            col1.enabled = False


        layout.separator()

        split = layout.split(factor=split_fac)
        col_L = split.column()
        col_R = split.column(align=True)

        col_L.label(text='Scene settings :', icon='SCENE_DATA')

        box = col_R.box()
        row = box.row()
        row.prop(scn.stm_settings, 'bool_spectrogram_scene_settings', text='Scene Settings', icon='TRIA_DOWN' if scn.stm_settings.bool_spectrogram_scene_settings else 'TRIA_RIGHT', emboss=False)
        # row.operator('stm.reset_spectrogram_settings', text='', icon='FILE_REFRESH')
        if scn.stm_settings.bool_spectrogram_scene_settings:
            box.prop(scn.stm_settings, 'force_standard_view_transform')
            box.prop(scn.stm_settings, 'force_eevee_AO')
            box.prop(scn.stm_settings, 'force_eevee_BLOOM')
            box.prop(scn.stm_settings, 'disable_eevee_viewport_denoising')

        

        layout.separator()

    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self, width=400)

    def execute(self, context):

        bpy.ops.stm.generate_spectrogram_modal('INVOKE_DEFAULT')

        return {'FINISHED'}


Operations = {
    "Retrieve metadata...":funcs.stm_00_ffmetadata,
    "Analyze audio...":funcs.stm_01_volume_data,
    "Generating spectrogram image...":funcs.stm_02_generate_spectrogram_img,
    "Building spectrogram...":funcs.stm_03_build_spectrogram,
    "Cleanup...":funcs.stm_04_cleanup,
    "Done !":funcs.stm_05_sleep,
}

class STM_OT_generate_spectrogram_modal(Operator):
    """Generate spectrogram"""
    bl_idname = "stm.generate_spectrogram_modal"
    bl_label = "Generate spectrogram (modal)"
    # bl_options = {'REGISTER', 'UNDO'}
    bl_options = {'UNDO'}

    def __init__(self):
        self.step = 0
        self.timer = None
        self.done = False
        self.max_step = None

        self.timer_count = 0 #timer count, need to let a little bit of space between updates otherwise gui will not have time to update

    def modal(self, context, event):

        global Operations
        
        scn = context.scene

        #update progress bar
        if not self.done:
            # print(f"Updating: {self.step+1}/{self.max_step}")

            progress_value = [10,20,35,75,95, 100]

            # context.object.progress = ((self.step+1)/(self.max_step))*100           #update progess bar
            scn.stm_settings.progress = progress_value[self.step]                     #update progess bar
            scn.stm_settings.progress_label = list(Operations.keys())[self.step]      #update label
            context.area.tag_redraw()                                               #send update signal


        #by running a timer at the same time of our modal operator
        #we are guaranteed that update is done correctly in the interface

        if event.type == 'TIMER':

            #but wee need a little time off between timers to ensure that blender have time to breath, so we have updated inteface
            self.timer_count +=1
            if self.timer_count==10:
                self.timer_count=0

                if self.done:
                    process_time = funcs.end_time()
                    print(f"\n------------------ Done in {process_time} ----------------------\n")
                    self.step = 0
                    scn.stm_settings.progress = 0
                    context.window_manager.event_timer_remove(self.timer)
                    context.area.tag_redraw()

                    return {'FINISHED'}

                if self.step < self.max_step:

                    #run step function
                    list(Operations.values())[self.step]()

                    self.step += 1
                    if self.step==self.max_step:
                        self.done=True

                    return {'RUNNING_MODAL'}

        return {'RUNNING_MODAL'}

    def invoke(self, context, event):
        print("\n------------------ GENERATING SPECTROGRAM ----------------------\n")

        funcs.start_time()

        #terermine max step
        global Operations
        if self.max_step == None:
            self.max_step = len(Operations.keys())

        context.window_manager.modal_handler_add(self)

        #run timer
        self.timer = context.window_manager.event_timer_add(0.05, window=context.window)



        return {'RUNNING_MODAL'}



class WM_OT_newSpectrogram(bpy.types.Operator, ImportHelper):
    """Select audio file to be used"""
    bl_idname = 'wm.new_spectrogram'
    bl_label = 'Select Audio File'

    #queue = bpy.props.StringProperty(None)

    def execute(self, context):

        #by default, create new spectrogram
        context.scene.userAction='createNew'

        #if object already selected, and contains 'STM_spectrogram' or 'STM_waveform' modifier, rebuild
        if funcs.check_if_only_active_obj_selected():
            if funcs.check_for_modifier('STM_spectrogram') or funcs.check_for_modifier('STM_waveform'):
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

        dirSize = funcs.get_dir_size(outputPath)
        dirSize = funcs.bytesto(dirSize, 'm')

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

class STM_OT_import_spectrogram_setup(Operator):
    """Import selected setup"""
    bl_idname = "stm.import_spectrogram_setup"
    bl_label = ''
    bl_options = {'UNDO'}

    def execute(self, context):

        scn = context.scene
        preset = scn.presets_setup

        print(preset)

        if preset == "1-waveform_simple.png":
            stm_obj = funcs.add_spectrogram_object()
            funcs.add_waveform_object(stm_obj)

            funcs.select_object_solo(stm_obj)

        elif preset == "2-waveform_complex.png":
            stm_obj = funcs.add_spectrogram_object()
            funcs.add_waveform_object(stm_obj, style=4, offset=-0.05)
            funcs.add_waveform_object(stm_obj, style=1, offset=0.0)
            funcs.add_waveform_object(stm_obj, style=2, offset=0.05)

            funcs.select_object_solo(stm_obj)


        return {'FINISHED'}

class STM_OT_add_spectrogram(Operator):
    """Add a new spectrogram object"""
    bl_idname = "stm.add_spectrogram"
    bl_label = ''
    bl_options = {'UNDO'}

    def execute(self, context):

        print('-INF- add spectrogram object')

        assetFile = bpy.context.scene.assetFilePath

        # obj = append_from_blend_file(assetFile, 'Object', 'STM_spectrogram', forceImport=True)
        funcs.append_from_blend_file(assetFile, 'NodeTree', 'STM_spectrogram')

        me = bpy.data.meshes.new('STM_spectrogram')
        obj = bpy.data.objects.new('STM_spectrogram', me)
        context.collection.objects.link(obj)

        mod = obj.modifiers.new("STM_spectrogram", 'NODES')
        mod.node_group = bpy.data.node_groups['STM_spectrogram']


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

        assetFile = bpy.context.scene.stm_settings.assetFilePath
        
        funcs.append_from_blend_file(assetFile, 'NodeTree', 'STM_waveform')
        

        mesh = bpy.data.meshes.new('STM_waveform')
        obj = bpy.data.objects.new("STM_waveform", mesh)
        bpy.context.collection.objects.link(obj)

        mod = obj.modifiers.new("STM_waveform", 'NODES')
        mod.node_group = bpy.data.node_groups['STM_waveform']


        mat = funcs.append_from_blend_file(assetFile, 'Material', 'STM_waveform', forceImport=False)
        if mat == None:
            mat = bpy.data.materials['STM_waveform']
        # mat.name = obj.name
        # mat['stm_obj'] = obj
        # audioPath = context.object.audio_file_path
        # audioName = funcs.sanitize_input(os.path.basename(audioPath))
        # mat.name = f'STM_waveform_{audioName}'

        mod["Input_15"] = mat

        if obj.data.materials:
            obj.data.materials[0] = mat
        else:
            obj.data.materials.append(mat)


        stm_obj = context.object
        
        if context.object.stm_spectro.stm_type == 'waveform':
            stm_obj = context.object.stm_spectro.spectrogram_object

        

        obj.stm_spectro.stm_type = 'waveform'
        obj.stm_spectro.stm_status = 'done'
        obj.stm_spectro.spectrogram_object = stm_obj
        # obj.stm_spectro.waveform_type = self.waveform_type
            
        stm_items = stm_obj.stm_spectro.stm_items

        item = stm_items.add()
        item.name = obj.name
        item.id = len(stm_items)
        item.stm_type = 'waveform'

        new_idx = len(stm_items)-1
        
        stm_obj.stm_spectro.stm_items_active_index = new_idx

        
        mod["Input_16"] = stm_obj
        mod["Input_14"] = (new_idx-1)/20

        
        obj.hide_viewport = True
        obj.hide_viewport = False
        

        funcs.select_object_solo(obj)


        print('-INF- added waveform object <%s>'%obj.name)

        return {'FINISHED'}

class STM_OT_delete_waveform(Operator):
    """Remove waveform"""
    bl_idname = "stm.delete_waveform"
    bl_label = 'Remove ?'
    bl_options = {'UNDO'}


    @classmethod
    def poll(cls, context):
        stm_obj = context.object.stm_spectro.spectrogram_object if context.object.stm_spectro.stm_type == 'waveform' else context.object
        return bool(stm_obj.stm_spectro.stm_items_active_index>0)

    def execute(self, context):

        obj = context.object
        stm_obj = obj
        
        if obj.stm_spectro.stm_type == 'waveform':
            stm_obj = obj.stm_spectro.spectrogram_object
        
        idx = stm_obj.stm_spectro.stm_items_active_index
        
        obj = bpy.data.objects[stm_obj.stm_spectro.stm_items[idx].name]
        obj.stm_spectro.stm_status = 'delete'
        
        new_index = stm_obj.stm_spectro.stm_items_active_index - 1
        
        stm_obj.stm_spectro.stm_items_active_index = new_index
        stm_obj.stm_spectro.stm_items.remove(idx)
        
        bpy.data.objects.remove(obj, do_unlink=True)
        
        stm_obj.stm_spectro.stm_items_active_index = new_index



        return {'FINISHED'}


class STM_OT_spectrogram_preset_popup(Operator):
    """Apply spectrogram preset"""
    bl_idname = "stm.spectrogram_preset_popup"
    bl_label = "Choose spectrogram preset"
    bl_options = {'UNDO'}


    def draw(self, context):

        layout = self.layout
        scn = context.scene



        with open(r'%s'%scn.presets_json_file,'r') as f:
            presets=json.load(f)

            p = scn.presets_geonodes.replace('.png', '')
            p = p.split('-')[1]


        preset_name = presets[p]['name']
        preset_desc = presets[p]['desc']


        row = layout.row()

        colL = row.column(align=True)

        colL.label(text=preset_name)

        colR = row.column(align=True)

        row = colR.row(align=True)
        
        gallery_scale = 8.0

        col1 = row.column(align=True)
        col2 = row.column(align=True)
        col3 = row.column(align=True)

        col1.scale_x = 1
        col3.scale_x = 1

        col1.scale_y=gallery_scale
        col3.scale_y=gallery_scale

        col1.operator('stm.previous_spectrogram_style', text='', icon='TRIA_LEFT')
        col2.template_icon_view(scn, "presets_geonodes", show_labels=True, scale=gallery_scale, scale_popup=6.0)
        col3.operator('stm.next_spectrogram_style', text='', icon='TRIA_RIGHT')

        box = colL.box()
        box.label(text=preset_desc)

        # layout.template_list("STM_UL_presets_geonodes", "", scn, "presets_geonodes", scn, "presets_geonodes")

        layout.separator()

    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self, width=400)

    def execute(self, context):

        preset = context.scene.presets_geonodes
        print(f'-INF- apply spectrogram preset "{preset}"')

        funcs.apply_spectrogram_preset(self, context)

        return {'FINISHED'}

class STM_OT_apply_gradient_preset(Operator):
    """Apply gradient preset"""
    bl_idname = 'stm.apply_gradient_preset'
    bl_label=''

    bl_options = {'UNDO'}

    def execute(self, context):

        funcs.apply_gradient_preset(self, context)

        return {'FINISHED'}

class STM_OT_apply_spectrogram_preset(Operator):
    """Apply spectrogram preset"""
    bl_idname = 'stm.apply_spectrogram_preset'
    bl_label=''

    bl_options = {'UNDO'}

    def execute(self, context):
        
        preset = context.scene.presets_geonodes
        print(f'-INF- apply spectrogram preset "{preset}"')

        funcs.apply_spectrogram_preset(self, context)


        return {'FINISHED'}

class STM_OT_reset_spectrogram_full(Operator):
    """Reset All Settings"""
    bl_idname = 'stm.reset_spectrogram_full'
    bl_label=''

    bl_options = {'UNDO'}

    def execute(self, context):

        funcs.reset_spectrogram_values(resetAll=True)
        # context.scene.presets_eq_curve = '0-reset.png'

        context.object.showGrid = 'on'
        context.object.doExtrude = 'on'


        return {'FINISHED'}

class STM_OT_reset_spectrogram_main_settings(Operator):
    """Reset Main Settings"""
    bl_idname = 'stm.reset_spectrogram_main_settings'
    bl_label=''

    bl_options = {'UNDO'}

    def execute(self, context):
        values = [
            'Freq Min (Hz)',
            'Freq Max (Hz)',
            'Lin To Log',
            'Audio Sample (s)',
            'Gain',
        ]

        funcs.reset_spectrogram_values(values=values)


        return {'FINISHED'}

class STM_OT_reset_spectrogram_geometry_values(Operator):
    """Reset Geometry Settings"""
    bl_idname = 'stm.reset_spectrogram_geometry_values'
    bl_label=''

    bl_options = {'UNDO'}

    def execute(self, context):
        values = [
            'showGrid',
            'doExtrude',
            'Resolution X',
            'Resolution Y',
            'Base Height',
            'Smooth',
            'Smooth Level',
            'Noise',
            'Noise Scale',
            'Height Multiplier',
            'Contrast',
        ]

        funcs.reset_spectrogram_values(values=values)

        context.object.showGrid = 'on'
        context.object.doExtrude = 'on'

        return {'FINISHED'}

class STM_OT_reset_eq_curve(Operator):
    """Reset EQ curve Settings"""
    bl_idname = 'stm.reset_stm_curve'
    bl_label=''

    bl_options = {'UNDO'}


    def execute(self, context):

        context.scene.presets_eq_curve = '0-reset.png'
        stm_modifier = context.object.modifiers["STM_spectrogram"]

        for i in stm_modifier.node_group.interface.items_tree:
            if i.name == 'EQ Curve Factor':
                funcs.set_geonode_value(stm_modifier, i, i.default_value)

        # funcs.apply_eq_curve_preset(self, context)

        return {'FINISHED'}

class STM_OT_reset_gradient(Operator):
    """Reset gradient"""
    bl_idname = 'stm.reset_gradient'
    bl_label ='Reset gradient'

    bl_options = {'UNDO'}

    def execute(self, context):
        print('-INF- Reset gradient')

        cr_node = bpy.data.materials['STM_gradient'].node_tree.nodes['STM_gradient']
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

class THUMB_OT_next_waveform_style(Operator):
    """Tooltip"""
    bl_idname = "stm.next_waveform_style"
    bl_label = "Move to next item in property list"

    def execute(self, context):

        items = [item.identifier for item in context.object.bl_rna.properties['presets_waveform_style'].enum_items]
        idx = items.index(context.object.presets_waveform_style)

        idx += 1
        if idx == len(items):
            idx = 0

        context.object.presets_waveform_style = items[idx]


        return {'FINISHED'}

class THUMB_OT_previous_waveform_style(Operator):
    """Tooltip"""
    bl_idname = "stm.previous_waveform_style"
    bl_label = "Move to previous item in property list"

    def execute(self, context):

        items = [item.identifier for item in context.object.bl_rna.properties['presets_waveform_style'].enum_items]
        idx = items.index(context.object.presets_waveform_style)

        idx -= 1
        if idx < 0:
            idx = len(items)-1

        context.object.presets_waveform_style = items[idx]


        return {'FINISHED'}
    

class THUMB_OT_next_spectrogram_style(Operator):
    """Next preset"""
    bl_idname = "stm.next_spectrogram_style"
    bl_label = ""

    def execute(self, context):

        items = [item.identifier for item in context.scene.bl_rna.properties['presets_geonodes'].enum_items]
        idx = items.index(context.scene.presets_geonodes)

        idx += 1
        if idx == len(items):
            idx = 0

        context.scene.presets_geonodes = items[idx]


        return {'FINISHED'}

class THUMB_OT_previous_spectrogram_style(Operator):
    """Previous preset"""
    bl_idname = "stm.previous_spectrogram_style"
    bl_label = ""

    def execute(self, context):

        items = [item.identifier for item in context.scene.bl_rna.properties['presets_geonodes'].enum_items]
        idx = items.index(context.scene.presets_geonodes)

        idx -= 1
        if idx < 0:
            idx = len(items)-1

        context.scene.presets_geonodes = items[idx]


        return {'FINISHED'}
    

class THUMB_OT_next_spectrogram_style_cylinder(Operator):
    """Next preset"""
    bl_idname = "stm.next_spectrogram_style_cylinder"
    bl_label = ""

    def execute(self, context):

        items = [item.identifier for item in context.scene.bl_rna.properties['presets_geonodes_cylinder'].enum_items]
        idx = items.index(context.scene.presets_geonodes_cylinder)

        idx += 1
        if idx == len(items):
            idx = 0

        context.scene.presets_geonodes_cylinder = items[idx]


        return {'FINISHED'}

class THUMB_OT_previous_spectrogram_style_cylinder(Operator):
    """Previous preset"""
    bl_idname = "stm.previous_spectrogram_style_cylinder"
    bl_label = ""

    def execute(self, context):

        items = [item.identifier for item in context.scene.bl_rna.properties['presets_geonodes_cylinder'].enum_items]
        idx = items.index(context.scene.presets_geonodes_cylinder)

        idx -= 1
        if idx < 0:
            idx = len(items)-1

        context.scene.presets_geonodes_cylinder = items[idx]


        return {'FINISHED'}


class THUMB_OT_next_spectrogram_setup(Operator):
    """Next preset"""
    bl_idname = "stm.next_spectrogram_setup"
    bl_label = ""

    def execute(self, context):

        items = [item.identifier for item in context.scene.bl_rna.properties['presets_setup'].enum_items]
        idx = items.index(context.scene.presets_setup)

        idx += 1
        if idx == len(items):
            idx = 0

        context.scene.presets_setup = items[idx]


        return {'FINISHED'}

class THUMB_OT_previous_spectrogram_setup(Operator):
    """Previous preset"""
    bl_idname = "stm.previous_spectrogram_setup"
    bl_label = ""

    def execute(self, context):

        items = [item.identifier for item in context.scene.bl_rna.properties['presets_setup'].enum_items]
        idx = items.index(context.scene.presets_setup)

        idx -= 1
        if idx < 0:
            idx = len(items)-1

        context.scene.presets_setup = items[idx]


        return {'FINISHED'}
    
class STM_OT_refresh_stm_objects(Operator):
    """Previous preset"""
    bl_idname = "stm.refresh_stm_objects"
    bl_label = ""

    def execute(self, context):
        
        scn = context.scene
        obj = context.object

        funcs.update_stm_objects(self, context)

        stm_obj = obj

        if obj.stm_spectro.stm_type == 'waveform':
            if obj.stm_spectro.spectrogram_object != None:
                stm_obj = obj.stm_spectro.spectrogram_object

        idx = stm_obj.stm_spectro.stm_items_active_index
        item = stm_obj.stm_spectro.stm_items[idx]
        
        for o in context.scene.objects:
            
            stm_obj = None
            
            if o.stm_spectro:
                if o.stm_spectro.stm_type == 'spectrogram':

                    stm_items = obj.stm_spectro.stm_items

                    stm_items.clear()
            
                    item = stm_items.add()
                    item.name = o.name
                    item.id = len(stm_items)
                    item.stm_type = 'spectrogram'
                    
                    stm_obj = o
            
            for o in context.scene.objects:
                if o.stm_spectro.stm_type == 'waveform':
                    if stm_obj != None and o.stm_spectro.spectrogram_object == stm_obj:

                        stm_items = stm_obj.stm_spectro.stm_items

                        if o.name not in stm_items:
                            item = stm_items.add()
                            item.name = o.name
                            item.id = len(stm_items)
                            item.stm_type = 'waveform'



        return {'FINISHED'}
