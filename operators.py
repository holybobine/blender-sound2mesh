from typing import Set
import bpy

from bpy.types import Context, Operator
from bpy_extras.io_utils import ImportHelper
from bpy.props import *

import datetime
import json
import os
from . import funcs
# from . funcs import *

    
class STM_OT_reload_previews(bpy.types.Operator):
    """"""
    bl_idname = 'stm.reload_previews'
    bl_label=''


    def execute(self, context):
        print('-INF- reload previews')

        funcs.generate_previews()


        return {'FINISHED'}

class STM_OT_select_audio_file(Operator, ImportHelper):
    """Select an audio file to import"""
    bl_idname = "stm.select_audio_file"  # important since its how bpy.ops.import_test.some_data is constructed
    bl_label = "Select audio file"

    # ImportHelper mixin class uses this
    filename_ext = ".txt"

    filter_glob: StringProperty(
        default="*" + ";*".join(bpy.path.extensions_audio),
        options={'HIDDEN'},
        maxlen=255,  # Max internal buffer length, longer would be clamped.
    ) # type: ignore

    def execute(self, context):

        stm_obj = funcs.get_stm_object(context.object)

        sound = bpy.data.sounds.load(self.filepath, check_existing=True)

        stm_obj.stm_spectro.audio_file = sound
        stm_obj.stm_spectro.audio_filename = os.path.basename(self.filepath)

        funcs.update_metadata(self, context)

        return {'FINISHED'}

class STM_OT_reset_audio_file(Operator):
    """Reset audio file"""
    bl_idname = "stm.reset_audio_file"  # important since its how bpy.ops.import_test.some_data is constructed
    bl_label = "Reset audio file"
    bl_options = {'UNDO'}



    def execute(self, context):

        stm_obj = funcs.get_stm_object(context.object)

        stm_obj.stm_spectro.audio_file = None


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

        stm_obj = funcs.get_stm_object(context.object)
        stm_obj.stm_spectro.image_file = None
        stm_modifier = stm_obj.modifiers["STM_spectrogram"]


        stm_modifier["Input_2"] = None

        if stm_obj.stm_spectro.material_type == 'raw':
            mat = stm_modifier["Input_12"]
            mat.node_tree.nodes['spectro_image'].image = None
            # stm_modifier["Input_12"] = None

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

class STM_OT_use_audio_in_scene(Operator):
    """Use audio in scene"""
    bl_idname = "stm.use_audio_in_scene"
    bl_label = "Use audio in scene"
    bl_options = {'UNDO'}

    def execute(self, context):

        print('-INF- add audio to scene')

        funcs.use_audio_in_scene(context)

        funcs.frame_clip_in_sequencer(context)

        return {'FINISHED'}

class STM_OT_open_image_folder(Operator):
    """Open image folder"""
    bl_idname = "stm.open_image_folder"
    bl_label = ""
    bl_options = {'UNDO'}

    def execute(self, context):

        stm_obj = funcs.get_stm_object(context.object)

        image_path = stm_obj.modifiers['STM_spectrogram']['Input_2'].filepath

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

        stm_obj = funcs.get_stm_object(context.object)

        image_path = stm_obj.modifiers['STM_spectrogram']['Input_2'].filepath

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

    
class STM_OT_adjust_resolution(Operator):
    """Next/previous power of 2"""
    bl_idname = "stm.adjust_resolution"
    bl_label = ""

    prop_name: bpy.props.StringProperty()  # type: ignore
    operation: bpy.props.EnumProperty( # type: ignore
        items= (
                    ("SUBSTRACT", "Substract", ""),
                    ("ADD", "Add", "")
                ),
    )

    def execute(self, context):
        prop = context.scene.stm_settings[self.prop_name]

        if self.operation == 'SUBSTRACT':
            new_value = funcs.next_power_of_2(int(prop/2))
        elif self.operation == 'ADD':
             new_value = funcs.next_power_of_2(int(prop+1))

        if 512 <= new_value <= 32768:
            context.scene.stm_settings[self.prop_name] = new_value

        return {'FINISHED'}


class STM_OT_bake_resolution_up(Operator):
    """"""
    bl_idname = "stm.bake_resolution_up"
    bl_label = ""

    prop_name: bpy.props.StringProperty()  # type: ignore

    def execute(self, context):
        from math import ceil
        prop = context.scene.stm_settings[self.prop_name] + 1
        base = 512 if prop < 1024 else 1024 if prop < 2048 else 2048 if prop < 8192 else 8192
        # base = 512 if prop < 1024 else 1024 if prop < 4096 else 2048
        new_value = base * ceil(prop/base)

        if 512 <= new_value <= 32768:
            context.scene.stm_settings[self.prop_name] = new_value

        return {'FINISHED'}
    

class STM_OT_bake_resolution_down(Operator):
    """"""
    bl_idname = "stm.bake_resolution_down"
    bl_label = ""

    prop_name: bpy.props.StringProperty()  # type: ignore

    def execute(self, context):
        from math import floor
        prop = context.scene.stm_settings[self.prop_name] - 1
        base = 512 if prop < 1024 else 1024 if prop < 2048 else 2048 if prop < 8192 else 8192
        new_value = base * floor(prop/base)

        if 512 <= new_value <= 32768:
            context.scene.stm_settings[self.prop_name] = new_value

        return {'FINISHED'}

class STM_OT_prompt_spectrogram_popup(Operator):
    """Bake Spectrogram Image"""
    bl_idname = "stm.prompt_spectrogram_popup"
    bl_label = "Generate spectrogram"
    bl_options = {'UNDO'}


    def draw(self, context):

        layout = self.layout
        scn = context.scene
        obj = funcs.get_stm_object(context.object)

        layout.separator()

        split_fac = 0.35

        split = layout.split(factor=split_fac)
        col1 = split.column()
        col1.alignment = 'RIGHT'
        col2 = split.column()


        col1.label(text='Audio')
        col2.prop(scn.stm_settings, 'bool_use_audio_in_scene', text='Use in Scene')

        if obj.stm_spectro.meta_duration_seconds > 1200:
            col1.separator()
            col1.separator()
            col1.separator()
            col1.separator()
            col1.separator()
            box = col2.box()
            row = box.row()
            ccol1=row.column(align=True)
            ccol2=row.column(align=True)
            ccol1.label(text='', icon='ERROR')
            ccol2.label(text='Long audio file.')

        # col1.separator()
        # col2.separator()

        

        col1.label(text='Image')
        col2.prop(scn.stm_settings, 'overwrite_image', text='Overwrite') 

        
        

        

        split = layout.split(factor=split_fac)
        
        col1 = split.column()
        col1.alignment = 'RIGHT'
        col2 = split.column(align=True)

        col1.label(text='Resolution')
        row = col2.row(align=True)
        row.prop(scn.stm_settings, 'bool_resolution', text='Auto', toggle=1, invert_checkbox=True)
        row.prop(scn.stm_settings, 'bool_resolution', text='Manual', toggle=1)

        
        col1.label(text='')
        # col2.prop(scn.stm_settings, 'bake_image_width', text='')
        box = col2.box()
        col = box.column()
        box.enabled = scn.stm_settings.bool_resolution
        row = col.row()
        row.prop(scn.stm_settings, 'userWidth', text='')
        rrow = row.row(align=True)

        
        rrow.operator('stm.bake_resolution_down', text='', icon='TRIA_DOWN').prop_name = 'userWidth'
        rrow.operator('stm.bake_resolution_up', text='', icon='TRIA_UP').prop_name = 'userWidth'

        # col1.separator()
        # col2.separator()

        # row = col2.row()
        # op = row.operator('stm.adjust_resolution', text='', icon='REMOVE')
        # op.prop_name = 'userWidth'
        # op.operation = 'SUBSTRACT'
        # row.prop(scn.stm_settings, 'userWidth', text='')
        # op = row.operator('stm.adjust_resolution', text='', icon='ADD')
        # op.prop_name = 'userWidth'
        # op.operation = 'ADD'

        # col1.separator()
        # col2.separator()

        col1.label(text='')
        # col2.prop(scn.stm_settings, 'bake_image_height', text='')
        row = col.row()
        row.prop(scn.stm_settings, 'userHeight', text='')
        rrow = row.row(align=True)

        
        rrow.operator('stm.bake_resolution_down', text='', icon='TRIA_DOWN').prop_name = 'userHeight'
        rrow.operator('stm.bake_resolution_up', text='', icon='TRIA_UP').prop_name = 'userHeight'

        

        # row = col2.row()
        # op = row.operator('stm.adjust_resolution', text='', icon='REMOVE')
        # op.prop_name = 'userHeight'
        # op.operation = 'SUBSTRACT'
        # row.prop(scn.stm_settings, 'userHeight', text='')
        # op = row.operator('stm.adjust_resolution', text='', icon='ADD')
        # op.prop_name = 'userHeight'
        # op.operation = 'ADD'

        # col_R.separator()

        # box = col_R.box()
        # row = box.row()
        # row.prop(scn.stm_settings, 'bool_advanced_spectrogram_settings', text='Advanced Settings', icon='TRIA_DOWN' if scn.stm_settings.bool_advanced_spectrogram_settings else 'TRIA_RIGHT', emboss=False)
        # row.operator('stm.reset_spectrogram_settings', text='', icon='FILE_REFRESH')
        # if scn.stm_settings.bool_advanced_spectrogram_settings:
        #     split = box.split(factor=0.5)
        #     col1 = split.column()
        #     col2 = split.column()
        #     col1.label(text='Intensity Scale :')
        #     col2.prop(scn.stm_settings, 'spectro_scale', text='')
            
        #     col1.label(text='Frequency Scale :')
        #     row = col2.row(align=True)
        #     row.prop_enum(scn.stm_settings, 'spectro_fscale', 'lin')
        #     row.prop_enum(scn.stm_settings, 'spectro_fscale', 'log')

        #     col1.label(text='Color Mode :')
        #     col2.prop(scn.stm_settings, 'spectro_colorMode', text='')
        #     col1.label(text='Dynamic Range :')
        #     col2.prop(scn.stm_settings, 'spectro_drange', text='')

        #     col1.enabled = False


        # layout.separator()

        # col = layout.column()

        # col1.separator()
        # col2.separator()



        split = layout.split(factor=split_fac)
        col1 = split.column()
        col1.alignment = 'RIGHT'
        col2 = split.column()


        col1.label(text='EEVEE Settings')

        row = col2.row(align=True)
        
        row.prop(scn.stm_settings, 'bool_eevee_settings', text='Auto', toggle=1, invert_checkbox=True)
        row.prop(scn.stm_settings, 'bool_eevee_settings', text='Manual', toggle=1)

        if scn.stm_settings.bool_eevee_settings:

            ccol = col2.column()
            ccol.prop(scn.stm_settings, 'force_eevee_AO')
            ccol.prop(scn.stm_settings, 'force_eevee_BLOOM')
            ccol.prop(scn.stm_settings, 'disable_eevee_viewport_denoising')
            ccol.prop(scn.stm_settings, 'force_standard_view_transform')

        layout.separator()


        # box = layout.box()
        # row = box.row()
        # row.prop(scn.stm_settings, 'bool_spectrogram_scene_settings', text='Scene Settings', icon='TRIA_DOWN' if scn.stm_settings.bool_spectrogram_scene_settings else 'TRIA_RIGHT', emboss=False)
        # # row.operator('stm.reset_spectrogram_settings', text='', icon='FILE_REFRESH')
        # if scn.stm_settings.bool_spectrogram_scene_settings:
            
        #     split = box.split(factor=split_fac)
        #     col1 = split.column()
        #     col1.alignment = 'RIGHT'
        #     col1.enabled = False
        #     col2 = split.column()

        #     col1.label(text='EEVEE settings')

            
        #     col2.prop(scn.stm_settings, 'force_eevee_AO')
        #     col2.prop(scn.stm_settings, 'force_eevee_BLOOM')
        #     col2.prop(scn.stm_settings, 'disable_eevee_viewport_denoising')
        #     col2.prop(scn.stm_settings, 'force_standard_view_transform')


    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self, width=300)

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
                    list(Operations.values())[self.step](self, context)

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
        
        stm_obj = funcs.add_spectrogram_object(context)
        stm_wave = funcs.add_waveform_object(context, stm_obj)
        funcs.select_object_solo(context, stm_obj)


        stm_items = stm_obj.stm_spectro.stm_items
        stm_items.clear()

        item = stm_items.add()
        # item.name = stm_obj.name
        # item.id = len(stm_items)
        # item.stm_type = 'spectrogram'
        item.object = bpy.data.objects[stm_obj.name]

        item = stm_items.add()
        # item.name = stm_wave.name
        # item.id = len(stm_items)
        # item.stm_type = 'waveform'
        item.object = bpy.data.objects[stm_wave.name]

        # funcs.update_stm_objects(context)

        # preset = scn.presets_setup

        # print(preset)

        # if preset == "1-waveform_simple.png":
        #     stm_obj = funcs.add_spectrogram_object()
        #     funcs.add_waveform_object(stm_obj)

        #     funcs.select_object_solo(context, stm_obj)

        # elif preset == "2-waveform_complex.png":
        #     stm_obj = funcs.add_spectrogram_object()
        #     funcs.add_waveform_object(stm_obj, style=4, offset=-0.05)
        #     funcs.add_waveform_object(stm_obj, style=1, offset=0.0)
        #     funcs.add_waveform_object(stm_obj, style=2, offset=0.05)

        #     funcs.select_object_solo(context, stm_obj)


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

    @classmethod
    def poll(cls, context):
        stm_obj = funcs.get_stm_object(context.object)

        return bool(len(stm_obj.stm_spectro.stm_items) <= 10)

    def execute(self, context):

        stm_obj = funcs.get_stm_object(context.object)
        stm_items = stm_obj.stm_spectro.stm_items

        wave_offset = funcs.get_wave_offset(context)
        wave_obj = funcs.add_waveform_object(context, stm_obj, wave_offset)
        funcs.select_object_solo(context, wave_obj)
        # funcs.add_waveform_to_stm_obj(stm_obj, wave_obj)


        # print(f'-INF- added waveform object {wave_obj.name}')

        return {'FINISHED'}

class STM_OT_delete_waveform(Operator):
    """Remove waveform"""
    bl_idname = "stm.delete_waveform"
    bl_label = 'Remove ?'
    bl_options = {'UNDO'}


    @classmethod
    def poll(cls, context):
        stm_obj = funcs.get_stm_object(context.object)
        return bool(stm_obj.stm_spectro.stm_items[stm_obj.stm_spectro.stm_items_active_index].object != stm_obj)

    def execute(self, context):

        stm_obj = funcs.get_stm_object(context.object)
        
        idx = stm_obj.stm_spectro.stm_items_active_index
        obj = stm_obj.stm_spectro.stm_items[idx].object
        
        
        new_index = stm_obj.stm_spectro.stm_items_active_index - 1
        
        # stm_obj.stm_spectro.stm_items_active_index = new_index
        stm_obj.stm_spectro.stm_status = 'deleting_from_list'
        stm_obj.stm_spectro.stm_items.remove(idx)
        stm_obj.stm_spectro.stm_items_active_index = new_index
        stm_obj.stm_spectro.stm_status = 'done'

        bpy.data.objects.remove(obj)

        



        return {'FINISHED'}


class STM_OT_write_spectrogram_preset_to_file(Operator):
    """Save preset"""
    bl_idname = "stm.write_spectrogram_preset_to_file"
    bl_label = "Save spectrogram preset"
    bl_options = {'UNDO'}


    def execute(self, context):
        funcs.write_spectrogram_preset_to_file(self, context)

        return {'FINISHED'}


class STM_OT_apply_spectrogram_preset_proper(Operator):
    """Apply preset"""
    bl_idname = "stm.apply_spectrogram_preset_proper"
    bl_label = "Apply spectrogram preset"
    bl_options = {'UNDO'}


    def execute(self, context):
        funcs.apply_spectrogram_preset_proper(self, context)

        return {'FINISHED'}

class STM_OT_detect_key_pressed(Operator):
    """"""
    bl_idname = "stm.detect_key_pressed"
    bl_label = ""

    key: bpy.props.EnumProperty(
        items=(
            ('CTRL', 'ctrl', ''),
            ('SHIFT', 'shift', ''),
            ('ALT', 'alt', ''),
        )
    ) # type: ignore

    def invoke(self, context, event):
        # ev = []
        # if event.ctrl:
        #     ev.append("Ctrl")
        # if event.shift:
        #     ev.append("Shift")
        # if event.alt:
        #     ev.append("Alt")
        # if event.oskey:
        #     ev.append("OS")
        # ev.append("Click")

        # self.report({'INFO'}, "+".join(ev))

        context.scene.stm_settings.is_ctrl_pressed = bool(event.ctrl)
        context.scene.stm_settings.is_shift_pressed = bool(event.shift)
        context.scene.stm_settings.is_alt_pressed = bool(event.alt)
        

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
    """Refresh list"""
    bl_idname = "stm.refresh_stm_objects"
    bl_label = ""

    def execute(self, context):
        
        scn = context.scene
        obj = context.object

        funcs.update_stm_objects(context)


        return {'FINISHED'}



class STM_OT_alert_audio_change(Operator):
    """Audio seems to have changed."""

    custom_label : StringProperty() # type: ignore

    bl_idname = "stm.alert_audio_change"
    bl_label = ''

    def execute(self, context):
        pass

        return {'FINISHED'}
    

class STM_OT_open_sequencer(bpy.types.Operator):
    """Open sequencer area"""
    bl_idname = 'stm.open_sequencer'
    bl_label=''

    bl_options = {'UNDO'}
    
    def open_sequencer_area(self, context):

        areas = context.screen.areas
        is_sequencer_open = bool(any([a.type == 'SEQUENCE_EDITOR' for a in areas]))

        if is_sequencer_open:
            return next(a for a in areas if a.type == 'SEQUENCE_EDITOR')
        else:
            area_view_3D = next(a for a in areas if a.type == 'VIEW_3D')
            with context.temp_override(area=area_view_3D):
                bpy.ops.screen.area_split(direction='HORIZONTAL', factor=0.15)

            
            context.screen.areas[-1].type = 'SEQUENCE_EDITOR'
            return context.screen.areas[-1]

    def frame_all_in_sequencer(self, context, area_seq_editor):
        for region in area_seq_editor.regions:
            if region.type == 'WINDOW':
                with context.temp_override(
                    window = context.window,
                    area = area_seq_editor,
                    region = region,
                ):
                    context.space_data.show_region_channels = False
                    context.space_data.show_region_toolbar = False

                    bpy.ops.sequencer.view_all()
                    bpy.ops.view2d.zoom(deltax=0.0, deltay=30, use_cursor_init=False)
                    bpy.ops.view2d.pan(deltax=0, deltay=-99999999)
                    bpy.ops.view2d.pan(deltax=0, deltay=125)
                    bpy.ops.view2d.zoom(deltax=0.0, deltay=-0.5, use_cursor_init=False)
                    

    def execute(self, context):
        area_seq_editor = self.open_sequencer_area(context)
        self.frame_all_in_sequencer(context, area_seq_editor)

        # context.scene.stm_settings.is_sequencer_open = True

        return {'FINISHED'}
        
        
class STM_OT_close_sequencer(bpy.types.Operator):
    """Close sequencer area"""
    bl_idname = 'stm.close_sequencer'
    bl_label=''

    bl_options = {'UNDO'}
    
    def close_sequencer(self, context):
        
        for area in context.screen.areas:
            if area.type == 'SEQUENCE_EDITOR': # 'VIEW_3D', 'CONSOLE', 'INFO' etc. 
                with context.temp_override(area=area):
                    bpy.ops.screen.area_close()

                break



    def execute(self, context):
        self.close_sequencer(context)
        context.scene.stm_settings.is_sequencer_open = False
        return {'FINISHED'}


class STM_OT_view_spectrogram_settings(Operator):
    """"""
    bl_idname = "stm.view_spectrogram_settings"
    bl_label = 'Open settings'
    bl_options = {'UNDO'}

    def execute(self, context):

        area_properties = next(a for a in context.window.screen.areas if a.type == 'PROPERTIES')

        for my_region in area_properties.regions:

            if my_region.type == 'WINDOW':
                with bpy.context.temp_override(
                    window = bpy.context.window,
                    area = area_properties,
                    region = my_region,
                ):
                    
                    context.space_data.context = 'OBJECT'


        return {'FINISHED'}
        


classes = [
    STM_OT_select_audio_file,
    STM_OT_reset_audio_file,
    STM_OT_reset_image_file,
    STM_OT_reset_spectrogram_settings,
    STM_OT_set_resolution_preset,
    STM_OT_use_audio_in_scene,
    STM_OT_open_image_folder,
    STM_OT_open_image,
    STM_OT_prompt_spectrogram_popup,
    STM_OT_generate_spectrogram_modal,
    STM_OT_select_stm_in_viewport,
    STM_OT_import_spectrogram_setup,
    STM_OT_add_waveform,
    STM_OT_add_spectrogram,
    STM_OT_delete_waveform,
    STM_OT_spectrogram_preset_popup,
    STM_OT_apply_spectrogram_preset,
    STM_OT_reset_spectrogram_full,
    STM_OT_reset_spectrogram_main_settings,
    STM_OT_reset_spectrogram_geometry_values,
    STM_OT_reset_eq_curve,
    STM_OT_reset_gradient,
    STM_OT_refresh_stm_objects,

    STM_OT_open_sequencer,
    STM_OT_close_sequencer,

    STM_OT_adjust_resolution,
    STM_OT_bake_resolution_up,
    STM_OT_bake_resolution_down,
    
    STM_OT_write_spectrogram_preset_to_file,
    STM_OT_apply_spectrogram_preset_proper,

    STM_OT_detect_key_pressed,

    STM_OT_view_spectrogram_settings,



    STM_OT_alert_audio_change,
    # STM_OT_reload_previews,


    THUMB_OT_next_waveform_style,
    THUMB_OT_previous_waveform_style,
    THUMB_OT_next_spectrogram_style,
    THUMB_OT_previous_spectrogram_style,
    THUMB_OT_next_spectrogram_style_cylinder,
    THUMB_OT_previous_spectrogram_style_cylinder,
    THUMB_OT_next_spectrogram_setup,
    THUMB_OT_previous_spectrogram_setup,
]

def register():
    for c in classes:
        bpy.utils.register_class(c)


def unregister():
    for c in classes:
        bpy.utils.unregister_class(c)