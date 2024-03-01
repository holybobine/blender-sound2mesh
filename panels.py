import bpy
import os
from bpy.types import Panel
from bpy.types import UIList
import textwrap
from . import funcs
# from . funcs import *


def prop_geonode(context, gn_modifier, input_name, label_name='', enabled=True, label=True, icon='NONE'):

    # input_id = next(i.identifier for i in gn_modifier.node_group.inputs if i.name == input_name)                  # 3.6
    input_id = next(i.identifier for i in gn_modifier.node_group.interface.items_tree if i.name == input_name)      # 4.0

    # print(input_id)

    if input_id:
        row = context.row(align=True)
        row.prop(
            data = gn_modifier,
            text = label_name if label_name != '' else input_name if label else '',
            property = '["%s"]'%input_id,
            icon = icon,
            emboss = True
        )

        # row.prop(
        #     data = gn_modifier,
        #     text = input_name,
        #     property = '["%s"]'%input_id,
        #     icon = icon,
        #     emboss = True
        # )

        row.enabled = enabled


 
def _label_multiline(context, text, parent, icon='NONE'):
    chars = int(context.region.width / 8)   # 7 pix on 1 character
    wrapper = textwrap.TextWrapper(width=chars)
    text_lines = wrapper.wrap(text=text)

    if icon != 'NONE':
        row = parent.row()
        row.label(text='', icon=icon)
        col = row.column(align=True)
    else:
        col = parent.column(align=True)

    for text_line in text_lines:
        col.label(text=text_line)

class STM_PT_spectrogram(Panel):
    bl_label = "Sound To Mesh"
    bl_idname = "STM_PT_spectrogram"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "STM"

    # def draw_header(self, context):
    #     layout = self.layout
    #     layout.label(text='Sound To Mesh', icon='NONE')

    def draw(self, context):
        layout = self.layout
        scn = context.scene
        obj = context.object


        # row = layout.row()
        # row.operator('stm.reload_previews', text='Reload Previews', icon='FILE_REFRESH')


        

        # layout.separator()

        


        # box = layout.box()
        # row = box.row()
        # split = row.split(factor=0.5)
        # split.scale_y = 1.5
        #
        # split.label(text='Output Path :', icon='FILEBROWSER')
        # row = split.row(align=True)
        # row.prop_enum(scn, 'bool_output_path', 'default', icon='NONE')
        # row.prop_enum(scn, 'bool_output_path', 'custom', icon='NONE')
        #
        # if scn.bool_output_path == 'custom':
        #     row = box.row()
        #     row.scale_y = 1.5
        #     row.prop(scn, 'outputPath', text='')
        #
        #     dirSize_bit = funcs.get_dir_size(scn.outputPath)
        #     # if dirSize_bit > 1073741824:
        #     dirSize = funcs.convert_size(dirSize_bit)
        #     row = box.row()
        #     row.label(text=f"Disk space used : {dirSize}", icon='INFO')
        #     row.enabled = False
            


        box = layout.box()

        # box.label(text='1. Add STM object :', icon='NONE')

        

        split = box.split(factor=0.6)
        split.scale_y = 1.2
        col1 = split.column()
        col2 = split.column()
        col1.label(text='Spectrogram', icon='SEQ_HISTOGRAM')
        col2.operator('stm.add_spectrogram', text='New', icon='ADD')

        spectro_is_selected = False

        if context.object in context.selected_objects:
            if any([m.name.startswith('STM_spectrogram') for m in context.object.modifiers]):
                spectro_is_selected = True

        
        col1.label(text='Waveform', icon='RNDCURVE')
        row = col2.row()
        row.operator('stm.add_waveform', text='New', icon='ADD')
        row.enabled = spectro_is_selected



class STM_PT_spectrogram_settings(Panel):
    bl_label = ""
    bl_idname = "STM_PT_spectrogram_settings"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "STM"
    # bl_parent_id = 'STM_PT_spectrogram'

    @classmethod
    def poll(self, context):
        do_draw = False

        try:
            if context.object in context.selected_objects:
                if any([m.name.startswith('STM_spectrogram') for m in context.object.modifiers]):
                    do_draw = True
        except:
            pass


        return do_draw

    def draw_header(self, context):
        layout = self.layout
        layout.label(text='Spectrogram Settings', icon='SEQ_HISTOGRAM')

    def draw(self, context):
        layout = self.layout
        scn = context.scene
        obj = context.object

        layout.enabled = obj.progress == 0



        layout = layout.box()

        audio_ok = False

        if obj.audio_file_path == '':
            info_audio = '[no audio selected]'
        elif not os.path.isfile(obj.audio_file_path):
            info_audio = '[invalid file path]'
        else:
            info_audio = obj.audio_file_path
            audio_ok = True

        # layout = layout.box()

        split_fac = 0.2


        split = layout.split(factor=split_fac)
        col1 = split.column(align=True)
        col2 = split.column(align=True)

        col1.alignment = 'RIGHT'
        col1.label(text='Audio')
        col1.scale_y = 1.5

        row = col2.row(align=True)
        
        ccol1 = row.column(align=True)
        ccol2 = row.column(align=True)
        ccol2.scale_y = 1.5

        

        box = ccol1.box()
        row = box.row()
        row.label(text=info_audio, icon='FILE_SOUND')
        row.enabled = False

        row = ccol2.row(align=True)
        row.operator('stm.import_audio_file', text='', icon='FILEBROWSER')
        row.operator('stm.reset_audio_file', text='', icon='PANEL_CLOSE')

        # box = col2.box()
        

        # split = box.split(factor=0.3)
        # col1 = split.column(align=True)
        # col1.alignment = 'RIGHT'
        # col2 = split.column(align=True)
        # col1.label(text='Title :')
        # col2.label(text=obj.title)
        # # col1.label(text='Artist :')
        # # col2.label(text=obj.artist)
        # # col1.label(text='Album :')
        # # col2.label(text=obj.album)
        # col1.label(text='Duration :')
        # col2.label(text=obj.duration_format)
        # col1.enabled = False

        # if obj.duration_seconds > 1200:
        #     box = col2.box()
        #     row = box.row()
        #     col1=row.column(align=True)
        #     # col1.scale_y = 2
        #     col2=row.column(align=True)
        #     col1.label(text='', icon='ERROR')
        #     col2.label(text='Long audio file.')
        #     # col2.label(text='Generation may take a while...')


        

        split = layout.split(factor=split_fac)
        split.scale_y = 1
        
        col1 = split.column()
        col2 = split.column(align=True)
        # col2.scale_y = 1.5
        # row = col2.row(align=True)

        col1.alignment = 'RIGHT'
        col1.scale_y = 1.5
        col1.label(text='Image')


        row = col2.row(align=True)
        row.scale_y = 1.5
        
        if obj.progress != 0:
            label = bpy.context.object.progress_label
            row.prop(bpy.context.object,"progress", text=label)
        else:
            row.operator('stm.prompt_spectrogram_popup', text='Bake From Audio', icon='IMPORT', depress=False)
            row.enabled = audio_ok

        

        row = col2.row(align=True)

        ccol1 = row.column(align=True)
        ccol2 = row.column(align=True)
        ccol2.scale_y = 1.5

        box = ccol1.box()
        row = box.row()
        row.enabled = False

        raw_texture = obj.modifiers['STM_spectrogram']['Input_2']

        row.label(text='[no image]' if raw_texture == None else raw_texture.name, 
                    icon='IMAGE_DATA'
                    )
        
        row = ccol2.row(align=True)
        row.operator('stm.reset_image_file', text='', icon='PANEL_CLOSE')


        # row = layout.row()
        # row.operator('stm.open_image', text='Open Image', icon='IMAGE_DATA')
        # row.operator('stm.open_image_folder', text='Image Folder', icon='FILEBROWSER')

        # row = layout.row()
        # row.operator('stm.set_sound_in_scene', text='Use sound in scene', icon='FILE_SOUND')

        # box = col2.box()

        # split = box.split(factor=0.3)

        # col1 = split.column(align=True)
        # col1.enabled = False
        # col1.alignment = 'RIGHT'
        # col2 = split.column(align=True)

        # col1.label(text='Resolution :')

        # resolution = f"{raw_texture.size[0]} x {raw_texture.size[1]}" if raw_texture != None else ''
        # col2.label(text=resolution)

        # box = layout.box()
        # box.label(text='Spectrogram OK !', icon='CHECKBOX_HLT')


class STM_PT_geometry_nodes_spectrogram(Panel):
    bl_label = ""
    bl_idname = "STM_PT_geometry_nodes_spectrogram"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "STM"
    bl_parent_id = 'STM_PT_spectrogram_settings'

    @classmethod
    def poll(self, context):
        do_draw = False

        try:
            if context.object in context.selected_objects:
                if any([m.name.startswith('STM_spectrogram') for m in context.object.modifiers]):
                    if context.object.modifiers["STM_spectrogram"]["Input_2"] != None:
                        do_draw = True
        except:
            pass


        return do_draw

    def draw_header(self, context):
        layout = self.layout
        layout.label(text='Geometry Nodes', icon='GEOMETRY_NODES')

    def draw(self, context):
        layout = self.layout
        scn = context.scene

        obj = context.object
        obj_allowed_types = ["MESH","CURVE","EMPTY"]

        
        layout.enabled = obj.progress == 0



        row = layout.row(align=True)
        row.scale_y = 1.5
        row.prop_enum(obj, 'geometry_type', 'plane', icon='MESH_GRID')
        row.prop_enum(obj, 'geometry_type', 'curve', icon='CURVE_DATA')
        row.prop_enum(obj, 'geometry_type', 'cylinder', icon='MESH_CYLINDER')

        # row = ccol2.row(align=True)
        # row.operator('stm.open_image_folder', text='', icon='FILEBROWSER')
        # row.enabled = obj.modifiers['STM_spectrogram']['Input_2'] != None


        row = layout.row()
        row.operator('stm.spectrogram_preset_popup', text='Apply Preset', icon='IMPORT')
        row.operator('stm.reset_spectrogram_full', text='Reset All', icon='LOOP_BACK')

        box = layout.box()
        row = box.row()
        row.prop(scn, 'bool_mode_settings', text='Mode Settings', icon='TRIA_DOWN' if scn.bool_mode_settings else 'TRIA_RIGHT', emboss=False)
        
        row.prop(scn, 'bool_mode_settings', text='', icon='MESH_GRID' if obj.geometry_type == 'plane' else 'CURVE_DATA' if obj.geometry_type == 'curve' else 'MESH_CYLINDER', emboss=False)
        # row.operator('stm.reset_spectrogram_main_settings', text='', icon='LOOP_BACK')


        if scn.bool_mode_settings:
            split_fac = 0.3

            if obj.geometry_type == 'plane':
                

                # prop_geonode(col, obj.modifiers['STM_spectrogram'], 'showGrid')

                split = box.split(factor=split_fac)
                row1 = split.row(align=True)
                row1.alignment = 'RIGHT'
                row2 = split.row(align=True)
                row1.label(text='Grid')
                row2.prop_enum(obj, 'showGrid', 'off')
                row2.prop_enum(obj, 'showGrid', 'on')

                

                split = box.split(factor=split_fac)
                col1 = split.column(align=True)
                col1.alignment = 'RIGHT'
                col2 = split.column(align=True)
                col1.label(text='Extrude')
                row = col2.row(align=True)
                row.prop_enum(obj, 'doExtrude', 'off')
                row.prop_enum(obj, 'doExtrude', 'on')

                row1 = col1.row(align=True)
                row1.alignment = 'RIGHT'
                row1.label(text='Height')
                row2 = col2.row(align=True)
                prop_geonode(row2, obj.modifiers['STM_spectrogram'], 'Base Height', label_name='', label=False)
                row1.enabled = True if obj.doExtrude == 'on' else False
                row2.enabled = True if obj.doExtrude == 'on' else False

            if obj.geometry_type == 'curve':
                
                split = box.split(factor=split_fac)
                col1 = split.column()
                col1.alignment = 'RIGHT'
                col2 = split.column()
                
                col1.label(text='Curve')
                prop_geonode(col2, obj.modifiers['STM_spectrogram'], 'Curve', label=False)

                col1.separator()
                col2.separator()
                
                # col1.label(text='Align')
                # row = col2.row(align=True)
                # row.prop_enum(obj, 'curveAlignment', 'center')
                # row.prop_enum(obj, 'curveAlignment', 'edge')

                col1.label(text='')
                prop_geonode(col2, obj.modifiers['STM_spectrogram'], 'Follow Curve', label_name='Follow Curve')

                split = box.split(factor=split_fac)
                # col1 = split.column(align=True)
                # col1.alignment = 'RIGHT'
                # col2 = split.column(align=True)
                # col1.label(text='Extrude')
                # row = col2.row(align=True)
                # row.prop_enum(obj, 'doExtrude', 'off')
                # row.prop_enum(obj, 'doExtrude', 'on')

                row1 = col1.row(align=True)
                row1.alignment = 'RIGHT'
                row1.label(text='Height')
                row2 = col2.row(align=True)
                prop_geonode(row2, obj.modifiers['STM_spectrogram'], 'Base Height', label_name='', label=False)

            if obj.geometry_type == 'cylinder':

                split = box.split(factor=split_fac)
                row1 = split.row(align=True)
                row1.alignment = 'RIGHT'
                row2 = split.row(align=True)
                row1.label(text='Displace')
                row2.prop_enum(obj, 'doFlipCylinderOut', 'in')
                row2.prop_enum(obj, 'doFlipCylinderOut', 'out')

                split = box.split(factor=split_fac)
                row1 = split.row(align=True)
                row1.alignment = 'RIGHT'
                row2 = split.row(align=True)
                row1.label(text='Flip X')
                prop_geonode(row2, obj.modifiers['STM_spectrogram'], 'flipCylinderX', label=False)

                split = box.split(factor=split_fac)
                row1 = split.row(align=True)
                row1.alignment = 'RIGHT'
                row2 = split.row(align=True)
                row1.label(text='Flip Y')
                prop_geonode(row2, obj.modifiers['STM_spectrogram'], 'flipCylinderY', label=False)



        
        

        box = layout.box()
        row = box.row()
        row.prop(scn, 'bool_main_settings', text='Audio Settings', icon='TRIA_DOWN' if scn.bool_main_settings else 'TRIA_RIGHT', emboss=False)
        row.operator('stm.reset_spectrogram_main_settings', text='', icon='LOOP_BACK')


        if scn.bool_main_settings:

            col = box.column(align=True)
            prop_geonode(col, obj.modifiers['STM_spectrogram'], 'Freq Min (Hz)')
            prop_geonode(col, obj.modifiers['STM_spectrogram'], 'Freq Max (Hz)')

            col = box.column(align=True)
            prop_geonode(col, obj.modifiers['STM_spectrogram'], 'Lin To Log')

            col = box.column(align=True)
            prop_geonode(col, obj.modifiers['STM_spectrogram'], 'Audio Sample (s)')

            col = box.column(align=True)
            prop_geonode(col, obj.modifiers['STM_spectrogram'], 'Gain')
            #
            # col = box.column(align=True)
            # prop_geonode(col, obj.modifiers['STM_spectrogram'], 'Intensity Lin / Log')

            # col = box.column(align=True)
            # prop_geonode(col, obj.modifiers['STM_spectrogram'], 'Clip Lows')
            # prop_geonode(col, obj.modifiers['STM_spectrogram'], 'Clip Highs')

        

        box = layout.box()
        row = box.row()
        row.prop(scn, 'bool_geometry_settings', text='Geometry Settings', icon='TRIA_DOWN' if scn.bool_geometry_settings else 'TRIA_RIGHT', emboss=False)
        row.operator('stm.reset_spectrogram_geometry_values', text='', icon='LOOP_BACK')


        if scn.bool_geometry_settings:

            col = box.column(align=True)                    
            prop_geonode(col, obj.modifiers['STM_spectrogram'], 'Resolution X')
            prop_geonode(col, obj.modifiers['STM_spectrogram'], 'Resolution Y')

            col = box.column(align=True)
            prop_geonode(col, obj.modifiers['STM_spectrogram'], 'Height Multiplier')
            prop_geonode(col, obj.modifiers['STM_spectrogram'], 'Contrast')

            col = box.column(align=True)
            prop_geonode(col, obj.modifiers['STM_spectrogram'], 'Smooth')
            prop_geonode(col, obj.modifiers['STM_spectrogram'], 'Smooth Level')

            col = box.column(align=True)
            prop_geonode(col, obj.modifiers['STM_spectrogram'], 'Noise')
            prop_geonode(col, obj.modifiers['STM_spectrogram'], 'Noise Scale')

        box = layout.box()
        row = box.row()
        row.prop(scn, 'bool_eq_curve_settings', text='EQ Curve', icon='TRIA_DOWN' if scn.bool_eq_curve_settings else 'TRIA_RIGHT', emboss=False)
        row.operator('stm.reset_stm_curve', text='', icon='LOOP_BACK')

        if scn.bool_eq_curve_settings:

            # row = box.row()
            # row.label(text='EQ Curve', icon='NORMALIZE_FCURVES')

            split = box.split(factor=0.4)
            split.scale_y = 1.2
            split.label(text='Apply Preset :')
            # split.template_icon_view(context.scene, "presets_eq_curve", show_labels=True, scale=3.0, scale_popup=5.0)
            split.prop(context.scene, "presets_eq_curve", text='')

            col = box.column(align=True)

            bbox = col.box()
            curve = bpy.data.node_groups['STM_spectrogram'].nodes['MACURVE']
            bbox.template_curve_mapping(
                data=curve,
                property="mapping",
                type='NONE',
                levels=False,
                brush=False,
                show_tone=False,
            )

            row = col.row(align=True)
            prop_geonode(row, obj.modifiers['STM_spectrogram'], 'EQ Curve Factor', label_name='Factor', label=True)



class STM_PT_material_spectrogram(Panel):
    bl_label = ""
    bl_idname = "STM_PT_material_spectrogram"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "STM"
    bl_parent_id = 'STM_PT_spectrogram_settings'

    @classmethod
    def poll(self, context):
        do_draw = False

        try:
            if context.object in context.selected_objects:
                if any([m.name.startswith('STM_spectrogram') for m in context.object.modifiers]):
                    if context.object.modifiers["STM_spectrogram"]["Input_2"] != None:
                        do_draw = True
        except:
            pass


        return do_draw

    def draw_header(self, context):
        layout = self.layout
        layout.label(text='Material', icon='MATERIAL')

    def draw(self, context):
        layout = self.layout
        scn = context.scene

        # layout = layout.box()

        obj = bpy.context.active_object
        obj_type = ''

        raw_texture = obj.modifiers['STM_spectrogram']['Input_2']

        layout.enabled = raw_texture != None and  obj.progress == 0

        row = layout.row(align=True)
        row.scale_y = 1.5

        row.prop(context.object, 'material_type', expand=True)


        split_fac = 0.3



        if obj.material_type == 'gradient' or obj.material_type == 'raw':
            split = layout.split(factor=split_fac)
            split.scale_y = 1.5


            split.label(text='Material')
            prop_geonode(split, obj.modifiers['STM_spectrogram'], 'Material', label=False)

        if obj.material_type == 'raw':


            box = layout.box()
            # box.enabled = False



            split = box.split(factor=split_fac)
            split.scale_y = 1.5
            col1 = split.column()
            col2 = split.column()

            col1.label(text='Image')

            row = col2.row(align=True)
            ccol1 = row.column(align=True)
            ccol2 = row.column(align=True)

            row = ccol1.row(align=True)
            row.enabled = False
            prop_geonode(row, obj.modifiers['STM_spectrogram'], 'Image', label=False)

            row = ccol2.row(align=True)
            row.operator('stm.open_image', text='Open', icon='FILE_IMAGE')
            row.enabled = raw_texture != None



            split = box.split(factor=split_fac)
            split.scale_y = 1
            col1 = split.column()
            col2 = split.column()

            col1.label(text='Folder')

            row = col2.row(align=True)
            ccol1 = row.column(align=True)
            ccol2 = row.column(align=True)
            ccol2.scale_y = 1.5

            if raw_texture != None:
                filepath = os.path.dirname(raw_texture.filepath)
            else:
                filepath = ''

            row = ccol1.row(align=True)
            row.enabled = False
            bbox = row.box()
            bbox.label(text=f'{filepath}')

            row = ccol2.row(align=True)
            row.operator('stm.open_image_folder', text='Open', icon='FILEBROWSER')
            row.enabled = raw_texture != None

            split = box.split(factor=split_fac)
            split.scale_y = 1
            col1 = split.column()
            col2 = split.column()


            col1.label(text='Resolution')

            resolution = f"{raw_texture.size[0]}x{raw_texture.size[1]}px" if raw_texture != None else ''
            col2.label(text=resolution)

            split = box.split(factor=split_fac)
            split.scale_y = 1
            col1 = split.column()
            col2 = split.column()

            col1.label(text='File Size')
            filesize = funcs.convert_size(os.path.getsize(raw_texture.filepath)) if raw_texture != None else ''
            col2.label(text=f'{filesize}')

        if obj.material_type == 'custom':
            split = layout.split(factor=split_fac)
            split.scale_y = 1.5

            split.label(text='Material')
            split.prop(context.object, 'material_custom', text='')



        if obj.material_type == 'gradient':

            col = layout.column(align=True)

            box = col.box()

            split = box.split(factor=0.4)
            split.scale_y = 1.5
            split.label(text='Preset :')                
            split.prop(context.object, "presets_gradient", text='')
            # split.template_icon_view(context.object, "presets_gradient", show_labels=True, scale=5.0, scale_popup=6.0)

            mat = context.object.data.materials[0]
            cr_node = mat.node_tree.nodes['STM_gradient']
            box.template_color_ramp(cr_node, "color_ramp", expand=False)


     



class STM_PT_waveform_settings(Panel):
    bl_label = ""
    bl_idname = "STM_PT_waveform_settings"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "STM"
    # bl_parent_id = 'STM_PT_spectrogram'

    @classmethod
    def poll(self, context):
        do_draw = False

        try:
            if context.object in context.selected_objects:
                if any([m.name.startswith('STM_waveform') for m in context.object.modifiers]):
                    do_draw = True
        except:
            pass


        return do_draw

    def draw_header(self, context):
        layout = self.layout
        layout.label(text='Waveform Settings', icon='RNDCURVE')

    def draw(self, context):
        layout = self.layout
        scn = context.scene
        obj = context.object

        modifier = obj.modifiers['STM_waveform']

        split_fac = 0.2

        

        box = layout.box()

        split = box.split(factor=split_fac)

        col1 = split.column()
        col1.scale_y = 1.5
        col1.alignment = 'RIGHT'
        col2 = split.column()


        col1.label(text='Target')

        
        row = col2.row(align=True)
        row.scale_x = 1
        row.scale_y = 1.5
        prop_geonode(row, modifier, 'Object', label=False)

        if modifier['Input_16'] != None:
            row.prop(modifier['Input_16'], 'hide_viewport', text='', invert_checkbox=False)
            row.prop(modifier['Input_16'], 'hide_render', text='', invert_checkbox=False)
        else:
            rrow = row.row(align=True)
            rrow.operator('stm.dummy', text='', icon='RESTRICT_VIEW_OFF')
            rrow.operator('stm.dummy', text='', icon='RESTRICT_RENDER_OFF')
            rrow.enabled=False



class STM_PT_geometry_nodes_waveform(Panel):
    bl_label = ""
    bl_idname = "STM_PT_geometry_nodes_waveform"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "STM"
    bl_parent_id = 'STM_PT_waveform_settings'

    @classmethod
    def poll(self, context):
        do_draw = False

        try:
            if context.object in context.selected_objects:
                if any([m.name.startswith('STM_waveform') for m in context.object.modifiers]):
                    do_draw = True
        except:
            pass


        return do_draw

    def draw_header(self, context):
        layout = self.layout
        layout.label(text='Geometry Nodes', icon='GEOMETRY_NODES')

    def draw(self, context):
        layout = self.layout
        scn = context.scene

        obj = context.object
        

        modifier = obj.modifiers['STM_waveform']

        split_fac = 0.5


        stm_ok = False

        if modifier['Input_16']:
            if modifier['Input_16'].modifiers:
                if modifier['Input_16'].modifiers.get('STM_spectrogram'):
                    stm_ok = True

        
        # box.prop(modifier, '["Socket_5"]')
        # box.prop_enum(modifier, '["Socket_5"]', 'True')

        # bpy.data.objects["STM_waveform"].modifiers["STM_waveform"]["Socket_5"]
            


        layout = layout.box()
        layout.enabled = stm_ok

        split = layout.split(factor=split_fac)
        split.label(text='Waveform Style :')

        

        gallery_scale = 5.0

        row = split.row(align=True)

        col1 = row.column(align=True)
        col2 = row.column(align=True)
        col3 = row.column(align=True)

        col1.scale_y=gallery_scale
        col3.scale_y=gallery_scale

        col1.operator('stm.previous_waveform_style', text='', icon='TRIA_LEFT')
        col2.template_icon_view(context.object, "presets_waveform_style", show_labels=True, scale=gallery_scale, scale_popup=6.0)
        col3.operator('stm.next_waveform_style', text='', icon='TRIA_RIGHT')


        col = layout.column(align=True)
        prop_geonode(col, modifier, 'Follow Spectrogram')



        col = layout.column(align=True)
        col.scale_y = 1.5
        prop_geonode(col, modifier, 'Offset')

        col = layout.column(align=True)
        prop_geonode(col, modifier, 'Thickness')
        

        if stm_ok:
            if modifier['Input_16'].modifiers['STM_spectrogram']['Socket_4'] == 1:
                if modifier['Input_8'] == 3 or modifier['Input_8'] == 4:
                    
                        prop_geonode(col, modifier, 'Bar Height')
        

        col = layout.column()
        # prop_geonode(col, modifier, 'Resolution Choice')
        row = col.row()

        # row = col.row(align=True)
        # prop_geonode(row, modifier, 'Resolution')
        # row.enabled = True if obj.waveform_resolution_choice == 'custom' else False

        split = col.split(factor=0.49)
        col1 = split.column(align=True)
        col2 = split.column(align=True)

        row = col1.row()
        row.scale_y = 1.5
        row.label(text='Resolution :')
        row = col2.row(align=True)
        row.scale_y = 1.5
        row.prop(obj, 'waveform_resolution_choice', expand=True)


        row2 = col2.row(align=True)
        prop_geonode(row2, modifier, 'Resolution', label_name='', label=False)
        row2.enabled = True if obj.waveform_resolution_choice == 'custom' else False

        if stm_ok:
            if modifier['Input_16'].modifiers['STM_spectrogram']['Socket_4'] == 2 :
                col = layout.column(align=True)
                prop_geonode(col, modifier, 'Curve Tilt')

        col = layout.column(align=True)
        prop_geonode(col, modifier, 'Smooth')
        prop_geonode(col, modifier, 'Smooth Level')

        # col = layout.column()
        # prop_geonode(col, modifier, 'Merge Ends')
        # prop_geonode(col, modifier, 'Threshold')

       

class STM_PT_material_waveform(Panel):
    bl_label = ""
    bl_idname = "STM_PT_material_waveform"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "STM"
    bl_parent_id = 'STM_PT_waveform_settings'

    @classmethod
    def poll(self, context):
        do_draw = False

        try:
            if context.object in context.selected_objects:
                if any([m.name.startswith('STM_waveform') for m in context.object.modifiers]):
                    do_draw = True
        except:
            pass


        return do_draw

    def draw_header(self, context):
        layout = self.layout
        layout.label(text='Material', icon='MATERIAL')

    def draw(self, context):
        layout = self.layout
        scn = context.scene

        # layout = layout.box()

        obj = bpy.context.active_object


        modifier = obj.modifiers['STM_waveform']

            

        col = layout.column()
        col.scale_y = 1.5
        prop_geonode(col, modifier, 'Material')


        col = layout.column()

        row = col.row()
        row.label(text='Color')
        prop_geonode(row, modifier, 'waveform_color', label=False)

        row = col.row()
        row.label(text='Emission')
        prop_geonode(row, modifier, 'emission_strength', label=False)