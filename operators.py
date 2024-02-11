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
    """Apply preset"""
    bl_idname = "stm.set_sound_in_scene"
    bl_label = "Set sound in scene"
    bl_options = {'UNDO'}

    def execute(self, context):

        print('-INF- add audio to scene')

        set_sound_in_scene(
            filepath=context.scene.audio_file_path,
            offset=0
        )

        frame_clip_in_sequencer()

        return {'FINISHED'}

class STM_OT_open_image_folder(Operator):
    """Apply preset"""
    bl_idname = "stm.open_image_folder"
    bl_label = "Open image folder"
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
    """Apply preset"""
    bl_idname = "stm.open_image"
    bl_label = "Open image"
    bl_options = {'UNDO'}

    def execute(self, context):
        image_path = context.object.modifiers['STM_spectrogram']['Input_2'].filepath

        if os.path.exists(image_path):
            print('-INF- open image')
            os.startfile(image_path)
        else:
            print(f'-ERR- can\'t open file "{image_path}"')

        return {'FINISHED'}

class STM_OT_prompt_spectrogram_popup(Operator):
    """Generate spectrogram"""
    bl_idname = "stm.prompt_spectrogram_popup"
    bl_label = "Generate spectrogram"
    bl_options = {'UNDO'}


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
        row.operator('stm.reset_spectrogram_settings', text='', icon='FILE_REFRESH')
        if scn.bool_advanced_spectrogram_settings:
            split = box.split(factor=0.5)
            col1 = split.column()
            col2 = split.column()
            col1.label(text='Intensity Scale :')
            col2.prop(scn, 'spectro_scale', text='')
            col1.label(text='Frequency Scale :')
            col2.prop(scn, 'spectro_fscale', text='')
            col1.label(text='Color Mode :')
            col2.prop(scn, 'spectro_colorMode', text='')
            col1.label(text='Dynamic Range :')
            col2.prop(scn, 'spectro_drange', text='')


        layout.separator()

    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self, width=350)

    def execute(self, context):

        bpy.ops.stm.generate_spectrogram_modal('INVOKE_DEFAULT')

        return {'FINISHED'}


Operations = {
    "Retrieve metadata 1/2":stm_00_ffmetadata,
    "Retrieve metadata 2/2":stm_01_volume_data,
    "Generating spectrogram image":stm_02_generate_spectrogram_img,
    "Building spectrogram":stm_03_build_spectrogram,
    "Cleanup":stm_04_cleanup,
    "Done !":stm_05_sleep,
}

class STM_OT_generate_spectrogram_modal(Operator):
    """Generate spectrogram"""
    bl_idname = "stm.generate_spectrogram_modal"
    bl_label = "Generate spectrogram (modal)"
    # bl_options = {'REGISTER', 'UNDO'}
    bl_options = {'UNDO'}

    interval : bpy.props.FloatProperty(default=0.1)

    def __init__(self):
        self.step = 0
        self.timer = None
        self.done = False
        self.max_step = None

        self.timer_count = 0 #timer count, need to let a little bit of space between updates otherwise gui will not have time to update

    def modal(self, context, event):

        global Operations

        #update progress bar
        if not self.done:
            # print(f"Updating: {self.step+1}/{self.max_step}")

            progress_value = [10,20,35,75,95, 100]

            # context.object.progress = ((self.step+1)/(self.max_step))*100           #update progess bar
            context.object.progress = progress_value[self.step]                     #update progess bar
            context.object.progress_label = list(Operations.keys())[self.step]      #update label
            context.area.tag_redraw()                                               #send update signal


        #by running a timer at the same time of our modal operator
        #we are guaranteed that update is done correctly in the interface

        if event.type == 'TIMER':

            #but wee need a little time off between timers to ensure that blender have time to breath, so we have updated inteface
            self.timer_count +=1
            if self.timer_count==10:
                self.timer_count=0

                if self.done:

                    print("\n------------------         DONE !         ----------------------")
                    self.step = 0
                    context.object.progress = 0
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

# class STM_OT_add_spectrogram(Operator):
#     """Add a new spectrogram object"""
#     bl_idname = "stm.add_spectrogram"
#     bl_label = ''
#     bl_options = {'UNDO'}
#
#     def execute(self, context):
#
#         print('-INF- add spectrogram object')
#
#         assetFile = bpy.context.scene.assetFilePath
#
#         append_from_blend_file(assetFile, 'NodeTree', 'STM_spectrogram')
#
#         mesh = bpy.data.meshes.new('STM_spectrogram')
#         obj = bpy.data.objects.new("STM_spectrogram", mesh)
#         bpy.context.collection.objects.link(obj)
#
#         mod = obj.modifiers.new("STM_spectrogram", 'NODES')
#         mod.node_group = bpy.data.node_groups['STM_spectrogram']
#
#         # mod["Input_12"] = bpy.data.materials['STM_rawTexture']
#
#         bpy.ops.object.select_all(action='DESELECT')
#
#         obj.select_set(True)
#         bpy.context.view_layer.objects.active = obj
#
#         print('-INF- added spectrogram object <%s>'%obj.name)
#
#         return {'FINISHED'}

class STM_OT_add_spectrogram(Operator):
    """Add a new spectrogram object"""
    bl_idname = "stm.add_spectrogram"
    bl_label = ''
    bl_options = {'UNDO'}

    def execute(self, context):

        print('-INF- add spectrogram object')

        assetFile = bpy.context.scene.assetFilePath

        obj = append_from_blend_file(assetFile, 'Object', 'STM_spectrogram')


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

class STM_OT_apply_gradient_preset(Operator):
    """Apply gradient preset"""
    bl_idname = 'stm.apply_gradient_preset'
    bl_label='Apply gradient preset'

    bl_options = {'UNDO'}

    def execute(self, context):

        apply_gradient_preset(self, context)

        return {'FINISHED'}

class STM_OT_reset_spectrogram_full(Operator):
    """Reset"""
    bl_idname = 'stm.reset_spectrogram_full'
    bl_label='Reset'

    bl_options = {'UNDO'}

    def execute(self, context):

        funcs.reset_spectrogram_values(resetAll=True)
        context.scene.presets_eq_curve = 'flat_5.png'

        funcs.apply_eq_curve_preset(self, context)

        context.object.showGrid = 'on'
        context.object.doExtrude = 'on'


        return {'FINISHED'}

class STM_OT_reset_spectrogram_main_settings(Operator):
    """Reset main settings"""
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
    """Reset geometry values"""
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
    """Apply EQ curve preset"""
    bl_idname = 'stm.reset_stm_curve'
    bl_label='Reset STM curve'

    bl_options = {'UNDO'}


    def execute(self, context):

        context.scene.presets_eq_curve = 'flat_5.png'

        funcs.apply_eq_curve_preset(self, context)

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
