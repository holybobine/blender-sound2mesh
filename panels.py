import bpy
import os
from bpy.types import Panel
from bpy.types import UIList, PropertyGroup
import textwrap
from . import funcs
# from . funcs import *

from .previews import preview_collections


def prop_geonode(context, gn_modifier, input_name, label_name='', enabled=True, label=True, icon='NONE', toggle=-1, invert_checkbox=False):

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
            emboss = True,
            toggle=toggle,
            invert_checkbox=invert_checkbox
        )

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

def poll_draw_spectrogram_tab(context):
    if not context.object:
        return
    if context.object.stm_spectro.stm_type not in ['spectrogram', 'waveform']:
        return


    return True

def poll_draw_spectrogram_settings(context):
    if not context.object:
        return
    if context.object.stm_spectro.stm_type != 'spectrogram':
        return
    if context.object.stm_spectro.image_file == None:
        return

    return True

def poll_draw_waveform_settings(context):
    if not context.object:
        return
    if context.object.stm_spectro.stm_type != 'waveform':
        return
    if funcs.get_stm_object(context).stm_spectro.image_file == None:
        return
    
    return True





class STM_UL_draw_items(UIList):
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):

        if item.name in context.scene.objects:
            obj = context.scene.objects[item.name]
            
            if obj.stm_spectro.stm_type == 'spectrogram':
                row = layout.row()
                row.prop(item, "name", icon='SEQ_HISTOGRAM', emboss=False, text="")
                row.prop(obj, "hide_viewport", text="", emboss=False)
                
            elif obj.stm_spectro.stm_type == 'waveform':
                custom_icon = 'RNDCURVE'

                custom_icon = preview_collections['presets_waveform_style'][obj.presets_waveform_style].icon_id
                
                # print(custom_icoooon)
                # row.prop_enum(obj, "presets_waveform_style", '0-line.png')
                # row.prop_enum(obj, "presets_waveform_style", '1-dots.png')
                # row.prop_enum(obj, "presets_waveform_style", '2-bars.png')
                # row.prop_enum(obj, "presets_waveform_style", '3-full.png')


                row = layout.row(align=True)
                row.label(text='', icon='DOT')
                row.prop(item, "name", icon_value=custom_icon, emboss=False, text="")

                parent_icon = 'LINKED' if obj.parent == obj.stm_spectro.spectrogram_object else 'UNLINKED'
                row.operator('stm.toggle_parent_waveform', text='', icon=parent_icon, emboss=False).waveform_name=item.name

                row.prop(obj, "hide_viewport", text="", emboss=False)

                

    def invoke(self, context, event):
        pass

class STM_MT_audio_menu(bpy.types.Menu):
    bl_idname = "STM_MT_audio_menu"
    bl_label = "Select"

    def draw(self, context):
        layout = self.layout


        layout.label(text='Audio Options')
        layout.separator()
        layout.operator("stm.use_audio_in_scene", icon='IMPORT')

class STM_MT_image_menu(bpy.types.Menu):
    bl_idname = "STM_MT_image_menu"
    bl_label = "Select"

    def draw(self, context):
        layout = self.layout

        layout.label(text='Image Options')
        layout.separator()
        layout.operator('stm.open_image', text='Open Image', icon='IMAGE_DATA')
        layout.operator('stm.open_image_folder', text='Open Image Folder', icon='FILEBROWSER')

class STM_Panel:
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "STM"

class STM_PT_spectrogram(STM_Panel, bpy.types.Panel):
    bl_label = "Sound To Mesh"
    bl_idname = "STM_PT_spectrogram"


    def draw(self, context):
        layout = self.layout
        scn = context.scene
        obj = context.object

        layout.operator('stm.import_spectrogram_setup', text='New', icon='ADD')
        # layout.operator('stm.refresh_stm_objects', text='Refresh STM objects', icon='FILE_REFRESH')


        
class STM_PT_spectrogram_settings(STM_Panel, bpy.types.Panel):
    bl_label = ""
    bl_idname = "STM_PT_spectrogram_settings"
    # bl_parent_id = 'STM_PT_spectrogram'

    updater = True

    @classmethod
    def poll(self, context):
        return poll_draw_spectrogram_tab(context)

    def draw_header(self, context):
        layout = self.layout
        layout.label(text='Spectrogram Settings', icon='SEQ_HISTOGRAM')

    def draw(self, context):
        

        layout = self.layout
        scn = context.scene
        obj = context.object

        stm_obj = funcs.get_stm_object(context)

        row = layout.row()
        row.enabled = scn.stm_settings.progress == 0

        row.template_list("STM_UL_draw_items", "", stm_obj.stm_spectro, "stm_items", stm_obj.stm_spectro, "stm_items_active_index", rows=5, sort_lock=True)

        col = row.column(align=True)
        col.operator("stm.refresh_stm_objects", icon='FILE_REFRESH', text="")
        col.separator()
        col.operator("stm.add_waveform", icon='ADD', text="")
        col.operator("stm.delete_waveform", icon='REMOVE', text="")
        col.separator()
        if scn.stm_settings.is_sequencer_open:
            col.operator('stm.close_sequencer', text='', icon='SEQUENCE')
        else:
            col.operator('stm.open_sequencer', text='', icon='SEQUENCE')


        # layout.prop(obj.stm_spectro, 'max_volume_dB')
        
            


        row_audio = layout.row()

        col = row_audio.column(align=True)
        col.enabled = scn.stm_settings.progress == 0
        
        row = col.row(align=True)
        # row.scale_y = 1.5

        if stm_obj.stm_spectro.audio_file == None:
            row.operator('stm.select_audio_file', text='Select Audio', icon='FILE_SOUND')
            
        else:
            ccol1 = row.column(align=True)
            ccol1.enabled = False
            ccol2 = row.column(align=True)

            ccol1.prop(stm_obj.stm_spectro, 'audio_filename', text='', icon='FILE_SOUND')

            row = ccol2.row(align=True)
            row.operator('stm.select_audio_file', text='', icon='FILEBROWSER')
            row.operator('stm.reset_audio_file', text='', icon='PANEL_CLOSE')

            # box = col.box()
            # box.enabled = scn.stm_settings.progress == 0


            # row = box.row()
            # row.enabled = False
            # rowL = row.row()
            # rowL.alignment = 'LEFT'
            # rowR = row.row()
            # rowR.alignment = 'RIGHT'

            # rowL.label(text=stm_obj.stm_spectro.meta_duration_format)
            # rowR.label(text=funcs.convert_size(os.path.getsize(stm_obj.stm_spectro.audio_file.filepath)))
        
        
        

        

        row_image = layout.row()

        col = row_image.column(align=True)


        row = col.row(align=True)
        # row.scale_y = 1.5
        rrow1 = row.row(align=True)
        rrow1.enabled = stm_obj.stm_spectro.audio_file != None
        rrow2 = row.row(align=True)
        
        if scn.stm_settings.progress != 0:
            label = scn.stm_settings.progress_label
            rrow1.prop(scn.stm_settings,"progress", text=label)
        elif stm_obj.stm_spectro.image_file == None:
            # row.template_ID(stm_obj.stm_spectro, 'image_file', text='')
            rrow1.operator('stm.prompt_spectrogram_popup', text='Bake Spectrogram Image', icon='IMAGE_DATA', depress=False)
        

        else:
            rrow1.prop(stm_obj.stm_spectro, 'image_filename', text='', icon='IMAGE_DATA')
            rrow1.enabled = False

            if stm_obj.stm_spectro.audio_filename == stm_obj.modifiers['STM_spectrogram']['Input_60']:
                rrow2.operator('stm.prompt_spectrogram_popup', text='', icon='FILE_REFRESH', depress=False)
            else:
                
                row = rrow2.row(align=True)
                row.alert = True
                row.operator('stm.prompt_spectrogram_popup', text='Rebake', icon='FILE_REFRESH', depress=False)
                # row.operator('stm.alert_audio_change', icon='ERROR')
                

            
            rrow2.operator('stm.reset_image_file', text='', icon='PANEL_CLOSE')

        # if stm_obj.stm_spectro.image_file != None:
            
            # box = col.box()
            # box.enabled = scn.stm_settings.progress == 0

            # ccol = box.column(align=True)

            
            # row = ccol.row()
            # row.emboss = 'NORMAL'
            # row.template_icon_view(stm_obj, "preview_image_enum", show_labels=True, scale=6.0, scale_popup=17.0)

            # row = ccol.row()
            # row.enabled = False
            # rowL = row.row()
            # rowL.alignment = 'LEFT'
            # rowR = row.row()
            # rowR.alignment = 'RIGHT'
            
            # rowL.label(text=f"{stm_obj.stm_spectro.image_file.size[0]}x{stm_obj.stm_spectro.image_file.size[1]}")
            # rowR.label(text=funcs.convert_size(os.path.getsize(stm_obj.stm_spectro.image_file.filepath)))

            # ccol.operator('stm.open_image', text='Open Image', icon='NONE')
            # ccol.operator('stm.open_image_folder', text='Open Image Folder', icon='NONE')
            
            
            # split = box.split(factor=0.4)
            # ccol1 = split.column(align=True)
            # ccol1.alignment = 'RIGHT'
            # ccol1.enabled = False
            # ccol2 = split.column(align=True)

            # ccol1.label(text='Resolution :')
            # ccol1.label(text='File Size :')

            # if scn.stm_settings.progress == 0:
            #     ccol2.label(text=f"{stm_obj.stm_spectro.image_file.size[0]}x{stm_obj.stm_spectro.image_file.size[1]}")
            #     ccol2.label(text=funcs.convert_size(os.path.getsize(stm_obj.stm_spectro.image_file.filepath)))

            # col = box.column()
            # col.enabled = stm_obj.stm_spectro.image_file != None

            # row = box.row()
            # row.operator('stm.open_image', text='Open Image', icon='IMAGE_DATA')
            # row.operator('stm.open_image_folder', text='Image Folder', icon='FILEBROWSER')



           




            # row = col.row()
            # row.operator('stm.prompt_spectrogram_popup', text='Regenerate Image', icon='FILE_REFRESH', depress=False)

            

            # if stm_obj.stm_spectro.audio_filename != stm_obj.modifiers['STM_spectrogram']['Input_60']:
            #     warning_image = 'different from audio.'
            #     image_icon = 'INFO'

            #     box = col.box()
            #     col = box.column(align=True)
            #     _label_multiline(context, warning_image, col, image_icon)

        

        if stm_obj.stm_spectro.audio_file:
            row_audio.menu('STM_MT_audio_menu', text='', icon='DOWNARROW_HLT')

        if stm_obj.stm_spectro.image_file:
            row_image.menu('STM_MT_image_menu', text='', icon='DOWNARROW_HLT')

        


class STM_PT_material_spectrogram(STM_Panel, bpy.types.Panel):
    bl_label = ""
    bl_idname = "STM_PT_material_spectrogram"
    # bl_parent_id = 'STM_PT_spectrogram_settings'

    @classmethod
    def poll(self, context):
        return bool(poll_draw_spectrogram_settings(context) or poll_draw_waveform_settings(context))

    def draw_header(self, context):
        layout = self.layout
        layout.label(text='Material', icon='MATERIAL')

    def draw(self, context):
        layout = self.layout
        scn = context.scene

        obj = context.object
        stm_obj = funcs.get_stm_object(context)
        obj_type = ''


        if poll_draw_spectrogram_settings(context):

            row = layout.row(align=True)

            # row.prop(obj.stm_spectro, 'material_type', expand=True)
            row.prop_enum(obj.stm_spectro, 'material_type', 'raw')
            row.prop_enum(obj.stm_spectro, 'material_type', 'gradient')
            row.prop_enum(obj.stm_spectro, 'material_type', 'custom')

            split_fac = 0.3

            if obj.stm_spectro.material_type == 'raw':

                box = layout.box()

                col = box.column()

                # row = layout.row()
                # row.emboss = 'NORMAL'
                col.template_icon_view(stm_obj, "preview_image_enum", show_labels=True, scale=6.0, scale_popup=17.0)

                row = col.row()
                row = col.row()
                row.enabled = False
                rowL = row.row()
                rowL.alignment = 'LEFT'
                rowR = row.row()
                rowR.alignment = 'RIGHT'
                
                rowL.label(text=f"{stm_obj.stm_spectro.image_file.size[0]}x{stm_obj.stm_spectro.image_file.size[1]}")
                rowR.label(text=funcs.convert_size(os.path.getsize(stm_obj.stm_spectro.image_file.filepath)))


            if obj.stm_spectro.material_type == 'gradient':
                
                layout.prop(stm_obj, 'presets_gradient', text='')

                box = layout.box()
                # col = layout.column(align=True)
            
                # row = box.row(align=True)
                # row.scale_x = 10

                # for item in stm_obj.bl_rna.properties['presets_gradient'].enum_items:
                #     row.prop_enum(stm_obj, 'presets_gradient', item.identifier, text='')

                # row.prop(stm_obj, 'presets_gradient', expand=True, icon_only=True)

                mat = context.object.data.materials[0]
                cr_node = mat.node_tree.nodes['STM_gradient']
                box.template_color_ramp(cr_node, "color_ramp", expand=False)

            if obj.stm_spectro.material_type == 'custom':
                if obj.active_material:
                    layout.template_ID_preview(obj.stm_spectro, "material_custom", hide_buttons=False)
                    # layout.template_ID(obj, "active_material", new="material.new")

                else:
                    col = layout.column(align=True)
                    box = col.box()
                    box.scale_y = 17
                    box.separator()

                    col.template_ID(obj.stm_spectro, "material_custom", new="material.new")

                
                

                
                

                # row = layout.row()
                # row.scale_y = 1.5
                # row.prop(obj.stm_spectro, 'material_custom', text='')


        if poll_draw_waveform_settings(context):
            
            row = layout.row(align=True)
            row.prop_enum(obj.stm_spectro, 'material_type', 'emission')
            row.prop_enum(obj.stm_spectro, 'material_type', 'custom')

            modifier = obj.modifiers['STM_waveform']

            if obj.stm_spectro.material_type == 'emission':

                row = layout.row()
                layout.template_color_picker(modifier, '["Socket_3"]', value_slider=False)
                row = layout.row()

                col = layout.column(align=True)
                prop_geonode(col, modifier, 'waveform_color', label=False)
                prop_geonode(col, modifier, 'emission_strength', label_name='Emission')


            if obj.stm_spectro.material_type == 'custom':

                

                if obj.active_material:
                    layout.template_ID_preview(obj.stm_spectro, "material_custom", hide_buttons=False)
                    # layout.template_ID(obj, "active_material", new="material.new")

                else:
                    col = layout.column(align=True)
                    box = col.box()
                    box.scale_y = 17
                    box.separator()

                    col.template_ID(obj.stm_spectro, "material_custom", new="material.new")


class STM_PT_geometry_nodes_spectrogram(STM_Panel, bpy.types.Panel):
    bl_label = ""
    bl_idname = "STM_PT_geometry_nodes_spectrogram"
    # bl_parent_id = 'STM_PT_spectrogram_settings'

    @classmethod
    def poll(self, context):
        return poll_draw_spectrogram_settings(context)

    def draw_header(self, context):
        layout = self.layout
        layout.label(text='Geometry Nodes', icon='GEOMETRY_NODES')

    def draw(self, context):
        layout = self.layout
        scn = context.scene

        obj = context.object
        obj_allowed_types = ["MESH","CURVE","EMPTY"]

        layout.enabled = context.object.modifiers["STM_spectrogram"]["Input_2"] != None and scn.stm_settings.progress == 0
        


        split_fac = 0.4

        split = layout.split(factor=split_fac)
        col1 = split.column(align=True)
        col1.alignment = 'RIGHT'
        col2 = split.column(align=True)

        # row = layout.row(align=True)
        # prop_geonode(row, obj.modifiers['STM_spectrogram'], 'doCylinder', icon='MESH_GRID', label_name='Plane', toggle=1, invert_checkbox=True)
        # prop_geonode(row, obj.modifiers['STM_spectrogram'], 'doCylinder', icon='MESH_CYLINDER', label_name='Cylinder', toggle=1)


        col1.label(text='Mode')
        row = col2.row(align=True)
        prop_geonode(row, obj.modifiers['STM_spectrogram'], 'doCylinder', icon='MESH_GRID', label_name='Plane', toggle=1, invert_checkbox=True)
        prop_geonode(row, obj.modifiers['STM_spectrogram'], 'doCylinder', icon='MESH_CYLINDER', label_name='Cylinder', toggle=1)

        col1.separator()
        col2.separator()  

        col1.label(text='Preset')


        # col2.prop(obj, "presets_geonodes", text='', icon='OPTIONS')
        col2.prop(obj.stm_spectro, 'presets_geonodes_proper', text='', icon='OPTIONS')

        # box = layout.box()
        # row = box.row(align=True)
        # row.prop(obj.stm_spectro, 'presets_geonodes_proper', text='')
        # row.operator('stm.write_spectrogram_preset_to_file', text='Save', icon='FILE_TICK')

        # row = box.row()
        # row.prop(obj.stm_spectro, 'preset_geonodes_name', text='Name')



class STM_PT_spectrogram_legend_settings(STM_Panel, bpy.types.Panel):
    bl_label = ""
    bl_idname = "STM_PT_spectrogram_legend_settings"
    bl_parent_id = 'STM_PT_geometry_nodes_spectrogram'
    bl_options = {'DEFAULT_CLOSED'}

    def draw_header(self, context):
        layout = self.layout
        layout.label(text='Info', icon='NONE')

    def draw(self, context):
        layout = self.layout
        scn = context.scene
        obj = context.object

        split_fac = 0.4

        split = layout.split(factor=split_fac)
        col1 = split.column(align=True)
        col1.alignment = 'RIGHT'
        col2 = split.column(align=True)

        col1.label(text='Title')

        row = col2.row(align=True)
        prop_geonode(row, obj.modifiers['STM_spectrogram'], 'showTitle', label=False)

        ccol = row.column(align=True)
        ccol.enabled = context.object.modifiers["STM_spectrogram"]["Socket_16"]
        prop_geonode(ccol, obj.modifiers['STM_spectrogram'], 'Title', label=False)

        col1.separator()
        col2.separator()

        col1.label(text='Grid')

        row = col2.row(align=True)
        prop_geonode(row, obj.modifiers['STM_spectrogram'], 'showGridFull', label=False)
        
        row = row.row(align=True)
        row.enabled = context.object.modifiers["STM_spectrogram"]["Socket_18"]
        prop_geonode(row, obj.modifiers['STM_spectrogram'], 'showGridX', label_name='X', toggle=1)
        prop_geonode(row, obj.modifiers['STM_spectrogram'], 'showGridY', label_name='Y', toggle=1)
        prop_geonode(row, obj.modifiers['STM_spectrogram'], 'showGridZ', label_name='Z', toggle=1)

class STM_PT_spectrogram_audio_settings(STM_Panel, bpy.types.Panel):
    bl_label = ""
    bl_idname = "STM_PT_spectrogram_audio_settings"
    bl_parent_id = 'STM_PT_geometry_nodes_spectrogram'
    bl_options = {'DEFAULT_CLOSED'}

    def draw_header(self, context):
        self.layout.label(text='Audio Settings', icon='NONE')
        self.layout.operator('stm.reset_spectrogram_main_settings', text='', icon='LOOP_BACK')

    def draw(self, context):
        layout = self.layout
        scn = context.scene
        obj = context.object

        split_fac = 0.4

        split = layout.split(factor=split_fac)
        col1 = split.column(align=True)
        col1.alignment = 'RIGHT'
        col2 = split.column(align=True)

        col1.label(text='Title')

        row = col2.row(align=True)
        prop_geonode(row, obj.modifiers['STM_spectrogram'], 'showTitle', label=False)

        ccol = row.column(align=True)
        ccol.enabled = context.object.modifiers["STM_spectrogram"]["Socket_16"]
        prop_geonode(ccol, obj.modifiers['STM_spectrogram'], 'Audio Filename', label=False)

        col1.separator()
        col2.separator()

        col1.label(text='Grid')

        row = col2.row(align=True)
        prop_geonode(row, obj.modifiers['STM_spectrogram'], 'showGridFull', label=False)
        
        row = row.row(align=True)
        row.enabled = context.object.modifiers["STM_spectrogram"]["Socket_18"]
        prop_geonode(row, obj.modifiers['STM_spectrogram'], 'showGridX', label_name='X', toggle=1)
        prop_geonode(row, obj.modifiers['STM_spectrogram'], 'showGridY', label_name='Y', toggle=1)
        prop_geonode(row, obj.modifiers['STM_spectrogram'], 'showGridZ', label_name='Z', toggle=1)

        col1.separator()
        col2.separator()

        col1.label(text='(Frequency) X')
        row = col2.row(align=True)
        prop_geonode(row, obj.modifiers['STM_spectrogram'], 'Freq Min (Hz)', label=False)
        prop_geonode(row, obj.modifiers['STM_spectrogram'], 'Freq Max (Hz)', label=False)
        col1.label(text='(Time) Y')
        prop_geonode(col2, obj.modifiers['STM_spectrogram'], 'Audio Sample (s)', label=False)
        col1.label(text='(Gain) Z')
        prop_geonode(col2, obj.modifiers['STM_spectrogram'], 'Gain', label=False)

        col1.separator()
        col2.separator()

        col1.label(text='Log Scale')

        row = col2.row(align=True)
        prop_geonode(row, obj.modifiers['STM_spectrogram'], 'doLogScale', label=False)

        rrow = row.row()
        rrow.enabled = context.object.modifiers["STM_spectrogram"]["Socket_9"]
        prop_geonode(rrow, obj.modifiers['STM_spectrogram'], 'Lin To Log', label=False)

        col1.separator()
        col2.separator()

        col1.label(text='')
        prop_geonode(col2, obj.modifiers['STM_spectrogram'], 'doClamp', label_name='Clamp Audio')

class STM_PT_spectrogram_geometry_settings(STM_Panel, bpy.types.Panel):
    bl_label = ""
    bl_idname = "STM_PT_spectrogram_geometry_settings"
    bl_parent_id = 'STM_PT_geometry_nodes_spectrogram'
    bl_options = {'DEFAULT_CLOSED'}

    def draw_header(self, context):
        self.layout.label(text='Geometry Settings', icon='NONE')
        self.layout.operator('stm.reset_spectrogram_geometry_values', text='', icon='LOOP_BACK')

    def draw(self, context):
        layout = self.layout
        scn = context.scene
        obj = context.object

        split_fac = 0.4

        split = layout.split(factor=split_fac)
        col1 = split.column(align=True)
        col1.alignment = 'RIGHT'
        col2 = split.column(align=True)

        col1.label(text='Resolution X')
        col1.label(text='Y')                   
        prop_geonode(col2, obj.modifiers['STM_spectrogram'], 'Resolution X', label=False)
        prop_geonode(col2, obj.modifiers['STM_spectrogram'], 'Resolution Y', label=False)

        

        col1.separator()
        col2.separator()

        col1.label(text='Flip')
        row = col2.row(align=True)
        
        prop_geonode(row, obj.modifiers['STM_spectrogram'], 'flip_X', label_name='X', toggle=1)
        prop_geonode(row, obj.modifiers['STM_spectrogram'], 'flip_Y', label_name='Y', toggle=1)
        prop_geonode(row, obj.modifiers['STM_spectrogram'], 'flip_Z', label_name='Z', toggle=1)

        col1.separator()
        col2.separator()

        if obj.modifiers['STM_spectrogram']['Socket_15'] == True:
            col1.label(text='Radius')
            prop_geonode(col2, obj.modifiers['STM_spectrogram'], 'Cylinder Radius', label=False)

        else:
            col1.label(text='Extrude')

            row = col2.row(align=True)
            prop_geonode(row, obj.modifiers['STM_spectrogram'], 'doExtrude', label=False)

            ccol = row.column(align=True)
            ccol.enabled = context.object.modifiers["STM_spectrogram"]["Input_52"]
            prop_geonode(ccol, obj.modifiers['STM_spectrogram'], 'extrudeHeight', label=False)


        col1.separator()
        col2.separator()

        col1.label(text='Contrast')

        row = col2.row(align=True)
        prop_geonode(row, obj.modifiers['STM_spectrogram'], 'doContrast', label=False)

        ccol = row.column(align=True)
        ccol.enabled = context.object.modifiers["STM_spectrogram"]["Socket_12"]
        prop_geonode(ccol, obj.modifiers['STM_spectrogram'], 'Contrast', label=False)

        col1.separator()
        col2.separator()
        
        col1.label(text='Smooth')                

        row = col2.row(align=True)
        prop_geonode(row, obj.modifiers['STM_spectrogram'], 'doSmooth', label=False)

        ccol = row.column(align=True)
        ccol.enabled = context.object.modifiers["STM_spectrogram"]["Socket_10"]
        prop_geonode(ccol, obj.modifiers['STM_spectrogram'], 'Smooth Factor', label=False)

        # if context.object.modifiers["STM_spectrogram"]["Socket_10"]:
        col1.label(text='')
        prop_geonode(ccol, obj.modifiers['STM_spectrogram'], 'Smooth Level', label_name='Level')

        col1.separator()
        col2.separator()

        col1.label(text='Noise')
            

        row = col2.row(align=True)
        prop_geonode(row, obj.modifiers['STM_spectrogram'], 'doNoise', label=False)

        ccol = row.column(align=True)
        ccol.enabled = context.object.modifiers["STM_spectrogram"]["Socket_11"]
        prop_geonode(ccol, obj.modifiers['STM_spectrogram'], 'Noise Factor', label=False)

        col1.label(text='')
        prop_geonode(ccol, obj.modifiers['STM_spectrogram'], 'Noise Scale', label_name='Scale')

class STM_PT_spectrogram_curve_settings(STM_Panel, bpy.types.Panel):
    bl_label = ""
    bl_idname = "STM_PT_spectrogram_curve_settings"
    bl_parent_id = 'STM_PT_geometry_nodes_spectrogram'
    bl_options = {'DEFAULT_CLOSED'}

    def draw_header(self, context):
        prop_geonode(self.layout, context.object.modifiers['STM_spectrogram'], 'doCurve', label=False)
        self.layout.label(text='Curve Deform', icon='NONE')
        

    def draw(self, context):
        layout = self.layout
        scn = context.scene
        obj = context.object

        layout.enabled = context.object.modifiers['STM_spectrogram']['Socket_17']

        split_fac = 0.4

        split = layout.split(factor=split_fac)
        col1 = split.column(align=True)
        col1.alignment = 'RIGHT'
        col2 = split.column(align=True)

        col1.label(text='Curve Object')
        col2.prop(obj.stm_spectro, 'curve_object', text='')

        col1.separator()
        col2.separator()

        row = col1.row(align=True)
        row.alignment = 'RIGHT'
        row.enabled = not obj.modifiers['STM_spectrogram']['Socket_15']
        row.label(text='Deform Axis')

        row = col2.row(align=True)
        row.enabled = not obj.modifiers['STM_spectrogram']['Socket_15']
        row.prop(obj.stm_spectro, 'curve_deform_axis', text='')       

class STM_PT_spectrogram_eqcurve_settings(STM_Panel, bpy.types.Panel):
    bl_label = ""
    bl_idname = "STM_PT_spectrogram_eqcurve_settings"
    bl_parent_id = 'STM_PT_geometry_nodes_spectrogram'
    bl_options = {'DEFAULT_CLOSED'}


    def draw_header(self, context):
        prop_geonode(self.layout, context.object.modifiers['STM_spectrogram'], 'doEQCurve', label=False)
        self.layout.label(text='EQ Curve', icon='NONE')

    def draw(self, context):
        layout = self.layout
        scn = context.scene
        obj = context.object

        layout.enabled = context.object.modifiers['STM_spectrogram']['Socket_19']

        layout.prop(obj, "presets_eq_curve", text='')   

        split_fac = 0.4

        split = layout.split(factor=split_fac)
        col1 = split.column(align=True)
        col1.alignment = 'RIGHT'
        col2 = split.column(align=True)

        col1.label(text='Factor')
        prop_geonode(col2, obj.modifiers['STM_spectrogram'], 'EQ Curve Factor', label=False)
           



          



        



class STM_PT_waveform_settings(STM_Panel, bpy.types.Panel):
    bl_label = ""
    bl_idname = "STM_PT_waveform_settings"
    # bl_parent_id = 'STM_PT_spectrogram_settings'

    @classmethod
    def poll(self, context):
        return poll_draw_waveform_settings(context)

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



class STM_PT_material_waveform(STM_Panel, bpy.types.Panel):
    bl_label = ""
    bl_idname = "STM_PT_material_waveform"
    # bl_parent_id = 'STM_PT_spectrogram_settings'

    @classmethod
    def poll(self, context):
        return poll_draw_waveform_settings(context)

    def draw_header(self, context):
        layout = self.layout
        layout.label(text='Material', icon='MATERIAL')

    def draw(self, context):
        layout = self.layout
        scn = context.scene

        obj = bpy.context.object


        modifier = obj.modifiers['STM_waveform']

            

        col = layout.column()
        col.scale_y = 1.5
        prop_geonode(col, modifier, 'Material', label=False)


        # box = layout.box()
        # box.emboss = 'NORMAL'
        row = layout.row()
        row.scale_y = 1.2
        row.template_color_picker(modifier, '["Socket_3"]', value_slider=True)

        prop_geonode(layout, modifier, 'waveform_color', label=False)
        prop_geonode(layout, modifier, 'emission_strength', label_name='Emission')

class STM_PT_geometry_nodes_waveform(STM_Panel, bpy.types.Panel):
    bl_label = ""
    bl_idname = "STM_PT_geometry_nodes_waveform"
    # bl_parent_id = 'STM_PT_spectrogram_settings'

    @classmethod
    def poll(self, context):
        return poll_draw_waveform_settings(context)

    def draw_header(self, context):
        layout = self.layout
        # layout.label(text='Waveform Settings', icon='RNDCURVE')
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




        split_fac = 0.4

        col = layout.column(align=True)

        row = col.row(align=True)
        row.prop_enum(obj, "presets_waveform_style", '0-line.png')
        row.prop_enum(obj, "presets_waveform_style", '1-dots.png')
        row.prop_enum(obj, "presets_waveform_style", '2-bars.png')
        row.prop_enum(obj, "presets_waveform_style", '3-full.png')

        box = col.box()

        split = box.split(factor=split_fac)
        col1 = split.column(align=True)
        col1.alignment = 'RIGHT'
        col2 = split.column(align=True)

        col1.label(text='Handle Type')
        row = col2.row(align=True)
        prop_geonode(row, obj.modifiers['STM_waveform'], 'doHandleAuto', icon='HANDLE_VECTOR', label_name='Vector', toggle=1, invert_checkbox=True)
        prop_geonode(row, obj.modifiers['STM_waveform'], 'doHandleAuto', icon='HANDLE_AUTO', label_name='Auto', toggle=1)

        col1.separator()
        col2.separator()

        col1.label(text='Thickness')
        prop_geonode(col2, obj.modifiers['STM_waveform'], 'Thickness', label=False)

        col1.separator()
        col2.separator()

        col1.label(text='Ends')
        row = col2.row(align=True)
        prop_geonode(row, obj.modifiers['STM_waveform'], 'doRoundBars', icon='GP_CAPS_FLAT', label_name='Flat', toggle=1, invert_checkbox=True)
        prop_geonode(row, obj.modifiers['STM_waveform'], 'doRoundBars', icon='GP_CAPS_ROUND', label_name='Round', toggle=1)

        col1.separator()
        col2.separator()

        col1.label(text='Width')
        prop_geonode(col2, obj.modifiers['STM_waveform'], 'Width', label=False)

        

        

        split = layout.split(factor=split_fac)
        col1 = split.column(align=True)
        col1.alignment = 'RIGHT'
        col2 = split.column(align=True)




        

        


        col1.label(text='Side')
        row = col2.row(align=True)
        row.prop_enum(obj.stm_spectro, "waveform_side_options", 'a')
        row.prop_enum(obj.stm_spectro, "waveform_side_options", 'b')
        row.prop_enum(obj.stm_spectro, "waveform_side_options", 'ab')


        col1.separator()
        col2.separator()

        # col1.label(text='Spectrogram Object')

        
        # row = col2.row(align=True)
        # prop_geonode(row, modifier, 'Object', label=False)

        # col1.separator()
        # col2.separator()

        # col1.label(text='Follow Spectrogram')
        # prop_geonode(col2, obj.modifiers['STM_waveform'], 'Follow Spectrogram', label=False)

        col1.label(text='Offset')
        prop_geonode(col2, obj.modifiers['STM_waveform'], 'Offset', label=False)

        

        col1.separator()
        col2.separator()

        col1.label(text='Resample')

        row = col2.row(align=True)
        prop_geonode(row, obj.modifiers['STM_waveform'], 'doResample', label=False)

        ccol = row.column(align=True)
        ccol.enabled = context.object.modifiers["STM_waveform"]["Input_17"]
        prop_geonode(ccol, obj.modifiers['STM_waveform'], 'Resample Resolution', label=False)

        col1.separator()
        col2.separator()

        col1.label(text='Smooth')

        row = col2.row(align=True)
        prop_geonode(row, obj.modifiers['STM_waveform'], 'doSmooth', label=False)

        ccol = row.column(align=True)
        ccol.enabled = context.object.modifiers["STM_waveform"]["Socket_8"]
        prop_geonode(ccol, obj.modifiers['STM_waveform'], 'Smooth Factor', label=False)
        prop_geonode(ccol, obj.modifiers['STM_waveform'], 'Smooth Level', label_name='Level')

        col1.separator()
        col2.separator()

        

        

        

        

        

        if stm_ok:
            if modifier['Input_16'].modifiers['STM_spectrogram']['Socket_4'] == 2 :
                col = layout.column(align=True)
                prop_geonode(col, modifier, 'Curve Tilt')

       


        



classes = [
    STM_PT_spectrogram,
    STM_UL_draw_items,
    STM_PT_spectrogram_settings,
    STM_PT_material_spectrogram,
    STM_PT_geometry_nodes_spectrogram,
    # STM_PT_spectrogram_legend_settings,
    STM_PT_spectrogram_audio_settings,
    STM_PT_spectrogram_geometry_settings,
    STM_PT_spectrogram_eqcurve_settings,
    STM_PT_spectrogram_curve_settings,

    # STM_PT_material_waveform,
    STM_PT_geometry_nodes_waveform,
    

    STM_MT_audio_menu,
    STM_MT_image_menu,

]


def register():
    for c in classes:
        bpy.utils.register_class(c)

def unregister():
    for c in classes:
        bpy.utils.unregister_class(c)