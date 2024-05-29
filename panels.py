import bpy
import os
from bpy.types import Panel
from bpy.types import UIList, PropertyGroup
import textwrap
import json
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
    if funcs.get_stm_object(context.object).stm_spectro.image_file == None:
        return
    
    return True





class STM_UL_draw_items(UIList):
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
        if not item.object:
            pass
        elif item.object.name in context.scene.objects:
            obj = item.object
            
            if obj.stm_spectro.stm_type == 'spectrogram':
                row = layout.row(align=True)
                row.prop(obj, "name", icon='SEQ_HISTOGRAM', emboss=False, text="")
                # row.prop(item, "name", icon='OBJECT_DATAMODE', emboss=False, text="")
                # rrow = row.row(align=True)
                row.prop(obj, "hide_viewport", text="", emboss=False)
                # row.prop(obj, "hide_render", text="", emboss=False)
                
            elif obj.stm_spectro.stm_type == 'waveform':
                side_values = ['A', 'B', 'AB']
                side = side_values[int(funcs.get_geonode_value_proper(obj.modifiers['STM_waveform'], 'Side'))]
                custom_icon_name = obj.presets_waveform_style.replace('.png', f'_{side}.png')

                custom_icon = preview_collections['presets_waveform_style_AB'][custom_icon_name].icon_id
                select_icon = 'LAYER_ACTIVE' if obj in context.selected_objects else 'LAYER_USED'
                parent_icon = 'LINKED' if obj.stm_spectro.is_parented_to_spectrogram else 'UNLINKED'

                row = layout.row(align=True)
                # row.emboss = 'NONE'
                # row.alert = bool(obj in context.selected_objects)
                
                # row.label(text='', icon=select_icon)
                row.prop(obj, "name", icon_value=custom_icon, emboss=False, text="")
                # row.prop(obj.stm_spectro, 'is_parented_to_spectrogram', text='', icon=parent_icon, emboss=False)
                row.prop(obj, "hide_viewport", text="", emboss=False)
                # row.prop(obj, "hide_render", text="", emboss=False)

                

    def invoke(self, context, event):
        pass



class STM_MT_audio_menu(bpy.types.Menu):
    bl_idname = "STM_MT_audio_menu"
    bl_label = "Select"

    def draw(self, context):
        layout = self.layout


        layout.label(text='Audio Options')
        layout.separator()
        layout.operator("stm.use_audio_in_scene", text='Import Audio in Scene', icon='IMPORT')
        layout.operator('stm.open_sequencer', text='Open Sequencer', icon='SEQUENCE')

class STM_MT_image_menu(bpy.types.Menu):
    bl_idname = "STM_MT_image_menu"
    bl_label = "Select"

    def draw(self, context):
        layout = self.layout

        layout.label(text='Image Options')
        layout.separator()
        layout.operator('stm.open_image', text='Open Image', icon='IMAGE_DATA')
        layout.operator('stm.open_image_folder', text='Open Image Folder', icon='FILEBROWSER')


class STM_PT_spectrogram_menu(bpy.types.Panel):
    bl_idname = "STM_PT_spectrogram_menu"
    bl_description = "Select preset"
    bl_label = "Select"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'WINDOW'
    # bl_options = {'INSTANCED'}

    def draw(self, context):
        layout = self.layout
        layout.emboss='PULLDOWN_MENU'

        col = layout.column()

        presets_dir = os.path.join(os.path.dirname(__file__), './geonodes_presets')

        for file in os.listdir(presets_dir):
            
            preset_fpath = os.path.join(presets_dir, file)

            with open(r'%s'%preset_fpath,'r') as f:
                preset_json=json.load(f)
            
            
            preset_name = preset_json['name']

            row = col.row()

            row.operator(
                operator='stm.apply_spectrogram_preset_proper', 
                text=preset_name
                            ).preset_fpath = preset_fpath


class STM_Panel:
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "STM"


class STM_Object_Panel:
    # bl_space_type = 'PROPERTIES'
    # bl_region_type = 'WINDOW'
    # bl_context = "object"

    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "STM"

class STM_Modifier_Panel:
    # bl_space_type = 'PROPERTIES'
    # bl_region_type = 'WINDOW'
    # bl_context = "object"

    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "STM"

    # @classmethod
    # def poll(self, context):
    #     return context.object.modifiers['STM_spectrogram']['Socket_42']






class STM_PT_spectrogram(STM_Panel, bpy.types.Panel):
    bl_label = "Sound To Mesh"
    bl_idname = "STM_PT_spectrogram"

    @classmethod
    def poll(self, context):
        return not bool(poll_draw_spectrogram_tab(context))

    def draw(self, context):
        layout = self.layout
        scn = context.scene
        obj = context.object

        # stm_logo = preview_collections['stm_logo']['6-stm_logo.png'].icon_id
        # layout.template_icon(stm_logo, scale=6.0)

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
        # layout.label(text='Spectrogram Settings', icon='SEQ_HISTOGRAM')
        layout.label(text='Spectrogram Settings', icon='NONE')

    def draw(self, context):
        

        layout = self.layout
        scn = context.scene
        obj = context.object

        stm_obj = funcs.get_stm_object(context.object)

        # row = layout.row()
        # row.enabled = scn.stm_settings.progress == 0

        # row.template_list("STM_UL_draw_items", "", stm_obj.stm_spectro, "stm_items", stm_obj.stm_spectro, "stm_items_active_index", rows=5, sort_lock=True)

        # col = row.column(align=True)
        # col.operator("stm.add_waveform", icon='ADD', text="")
        # col.operator("stm.delete_waveform", icon='REMOVE', text="")

        
        # col.separator()
        
        # prop_geonode(col, stm_obj.modifiers['STM_spectrogram'], 'doOverlays', label=False, icon='OVERLAY', toggle=1)
        # col.menu('STM_MT_spectrogram_menu', text='', icon='DOWNARROW_HLT')

        # if scn.stm_settings.is_sequencer_open:
        #     col.operator('stm.close_sequencer', text='', icon='SEQUENCE')
        # else:
        #     col.operator('stm.open_sequencer', text='', icon='SEQUENCE')


        # layout.prop(obj.stm_spectro, 'max_volume_dB')
        






        box = layout.box()
        box.enabled = scn.stm_settings.progress == 0
        col = box.column()
        # col.enabled = False
        # box.emboss = 'PULLDOWN_MENU'

        audio_label = '- no audio -' if stm_obj.stm_spectro.audio_file == None else stm_obj.stm_spectro.meta_duration_format
        audio_icon = 'ERROR' if stm_obj.stm_spectro.audio_file == None else 'FILE_SOUND'
        image_label = '- no image -' if stm_obj.stm_spectro.image_file == None else f"{stm_obj.stm_spectro.image_file.size[0]}x{stm_obj.stm_spectro.image_file.size[1]}"
        image_icon = 'ERROR' if stm_obj.stm_spectro.image_file == None else 'IMAGE_DATA'



        audio_icon = 'NONE'
        image_icon = 'NONE'

        split_fac = 0.4

        split = col.split(factor=split_fac)
        col1 = split.column(align=True)
        col1.alignment = 'RIGHT'
        col1.enabled = False
        
        col2 = split.column(align=True)
        
        col1.label(text='Audio File')

        row = col2.row()
        row.alert = bool(stm_obj.stm_spectro.audio_file == None)
        row.enabled = bool(stm_obj.stm_spectro.audio_file == None)

        row.label(text=audio_label, icon=audio_icon)
        
        # if stm_obj.stm_spectro.audio_file != None:
        #     col1.label(text='')
        #     col2.label(text=stm_obj.stm_spectro.meta_duration_format)

        col1.label(text='Image Size')

        row = col2.row()
        row.alert = bool(stm_obj.stm_spectro.image_file == None)
        row.enabled = bool(stm_obj.stm_spectro.image_file == None)

        row.label(text=image_label, icon=image_icon)


        
        if not stm_obj.stm_spectro.image_file:
            pass
        elif not funcs.is_audio_in_sequencer(context, stm_obj.stm_spectro.audio_file):
            row = col.row()
            row.alert = True
            row.operator('stm.use_audio_in_scene', text='Audio not in scene (click to fix)', icon='ERROR')

        #     box = layout.box()

        #     split_fac = 0.7

        #     split = box.split(factor=split_fac)
        #     col1 = split.column(align=True)
        #     col2 = split.column(align=True)
        #     col2.operator('stm.use_audio_in_scene', text='Fix', icon='IMPORT')
        #     col1.label(text='Audio not in scene', icon='ERROR')





            


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
            # if not funcs.is_audio_in_sequencer(context, stm_obj.stm_spectro.audio_file):
            #     rrow = row.row(align=True)
            #     rrow.alert = True
            #     rrow.operator('stm.use_audio_in_scene', text='Re-import', icon='IMPORT')
            row.operator('stm.select_audio_file', text='', icon='FILEBROWSER')
            row.operator('stm.reset_audio_file', text='', icon='PANEL_CLOSE')


            # box = layout.box()
            # col = box.column(align=True)

            # split_fac = 0.4

            # split = col.split(factor=split_fac)
            # split.enabled = False
            # col1 = split.column(align=True)
            # col1.alignment = 'RIGHT'
            
            # col2 = split.column(align=True)

            # col1.label(text='Title')
            # col2.label(text=stm_obj.stm_spectro.meta_title)

            # col1.label(text='Duration')
            # col2.label(text=stm_obj.stm_spectro.meta_duration_format)

            # if not funcs.is_audio_in_sequencer(context, stm_obj.stm_spectro.audio_file):
            #     row = col.row()
            #     row.alert = True
            #     row.operator('stm.use_audio_in_scene', text='Audio not in scene (click to fix)', icon='ERROR')
        
        
        

        

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



            # box = layout.box()

            # split_fac = 0.4

            # split = box.split(factor=split_fac)
            # split.enabled = False
            # col1 = split.column(align=True)
            # col1.alignment = 'RIGHT'
            
            # col2 = split.column(align=True)

            # col1.label(text='File Size')
            # col2.label(text=funcs.convert_size(os.path.getsize(stm_obj.stm_spectro.image_file.filepath)))

            # col1.label(text='Resolution')
            # col2.label(text=f"{stm_obj.stm_spectro.image_file.size[0]}x{stm_obj.stm_spectro.image_file.size[1]}")
            
            # box = col.box()

            # row = box.row()
            # row.enabled = False
            # row.scale_y = 0.5

            # rowL, rowR = row.row(), row.row()
            # rowL.alignment, rowR.alignment = 'LEFT', 'RIGHT'

            
            # rowL.label(text=f"{stm_obj.stm_spectro.image_file.size[0]}x{stm_obj.stm_spectro.image_file.size[1]}")
            # rowR.label(text=funcs.convert_size(os.path.getsize(stm_obj.stm_spectro.image_file.filepath)))


        



        if stm_obj.stm_spectro.audio_file:
            row_audio.menu('STM_MT_audio_menu', text='', icon='DOWNARROW_HLT')

        if stm_obj.stm_spectro.image_file:
            row_image.menu('STM_MT_image_menu', text='', icon='DOWNARROW_HLT')


        # layout.operator('stm.view_spectrogram_settings', icon='PROPERTIES')

        


        
                  
class STM_PT_spectrogram_overlay_settings(STM_Object_Panel, bpy.types.Panel):
    bl_label = ""
    bl_idname = "STM_PT_spectrogram_overlay_settings"
    bl_parent_id = 'STM_PT_spectrogram_settings'
    bl_options = {'DEFAULT_CLOSED'}

    @classmethod
    def poll(self, context):
        return bool(poll_draw_spectrogram_settings(context) or poll_draw_waveform_settings(context))


    def draw_header(self, context):
        # prop_geonode(self.layout, context.object.modifiers['STM_spectrogram'], 'doOverlays', label=False)
        self.layout.label(text='Overlays', icon='OVERLAY')

    def draw(self, context):
        layout = self.layout
        scn = context.scene
        obj = funcs.get_stm_object(context.object)

        layout.enabled = obj.modifiers['STM_spectrogram']['Socket_39']
 

        split_fac = 0.4

        split = layout.split(factor=split_fac)
        col1 = split.column(align=True)
        col1.alignment = 'RIGHT'
        col2 = split.column(align=True)

        col1.label(text='Title')

        row = col2.row(align=True)
        prop_geonode(row, obj.modifiers['STM_spectrogram'], 'showTitle', label=False)

        ccol = row.column(align=True)
        ccol.enabled = obj.modifiers["STM_spectrogram"]["Socket_16"]
        prop_geonode(ccol, obj.modifiers['STM_spectrogram'], 'Title', label=False)

        col1.separator()
        col2.separator()

        col1.label(text='Grid')

        row = col2.row(align=True)
        prop_geonode(row, obj.modifiers['STM_spectrogram'], 'showGridFull', label=False)
        
        row = row.row(align=True)
        row.enabled = obj.modifiers["STM_spectrogram"]["Socket_18"]
        prop_geonode(row, obj.modifiers['STM_spectrogram'], 'showGridX', label_name='X', toggle=1)
        prop_geonode(row, obj.modifiers['STM_spectrogram'], 'showGridY', label_name='Y', toggle=1)
        prop_geonode(row, obj.modifiers['STM_spectrogram'], 'showGridZ', label_name='Z', toggle=1)

class STM_PT_material_spectrogram(STM_Panel, bpy.types.Panel):
    bl_label = ""
    bl_idname = "STM_PT_material_spectrogram"
    bl_parent_id = 'STM_PT_spectrogram_settings'
    bl_options = {'DEFAULT_CLOSED'}

    @classmethod
    def poll(self, context):
        return bool(poll_draw_spectrogram_settings(context) or poll_draw_waveform_settings(context))

    def draw_header(self, context):
        layout = self.layout
        layout.label(text='Material', icon='MATERIAL')

    def draw(self, context):
        layout = self.layout
        scn = context.scene

        layout.enabled = scn.stm_settings.progress == 0

        obj = context.object
        stm_obj = funcs.get_stm_object(context.object)

            
            
        row = layout.row(align=True)

        # row.prop(obj.stm_spectro, 'material_type', expand=True)
        row.prop_enum(stm_obj.stm_spectro, 'material_type', 'raw')
        row.prop_enum(stm_obj.stm_spectro, 'material_type', 'gradient')
        row.prop_enum(stm_obj.stm_spectro, 'material_type', 'custom')

        split_fac = 0.3

        if stm_obj.stm_spectro.material_type == 'raw':

            box = layout.box()

            col = box.column()

            # row = layout.row()
            # row.emboss = 'NORMAL'
            col.template_icon_view(stm_obj, "preview_image_enum", show_labels=True, scale=6.0, scale_popup=17.0)

            row = col.row()
            row.scale_y=0.9
            # row = col.row()
            row.enabled = False
            rowL = row.row()
            rowL.alignment = 'LEFT'
            rowR = row.row()
            rowR.alignment = 'RIGHT'
            
            rowL.label(text=f"{stm_obj.stm_spectro.image_file.size[0]}x{stm_obj.stm_spectro.image_file.size[1]}")
            rowR.label(text=funcs.convert_size(os.path.getsize(stm_obj.stm_spectro.image_file.filepath)))


        if stm_obj.stm_spectro.material_type == 'gradient':
            
            # col = layout.column(align=True)
            # layout.prop(stm_obj.stm_spectro, 'gradient_custom', text='Customize Gradient', icon='OPTIONS' if not obj.stm_spectro.gradient_custom else 'X', toggle=1)
            # row = col.row(align=True)
            # row.prop(stm_obj.stm_spectro, 'gradient_type', text='Customize Gradient', expand=True)

            # box = col.box()
            
            # if stm_obj.stm_spectro.gradient_type == 'preset':
            #     box.template_icon_view(stm_obj, "presets_gradient", show_labels=True, scale=6.0, scale_popup=6.0)
            # else:
            #     mat = stm_obj.data.materials[0]
            #     cr_node = mat.node_tree.nodes['STM_gradient']
            #     box.template_color_ramp(cr_node, "color_ramp", expand=False)


            layout.prop(stm_obj, "presets_gradient", text='', icon='OPTIONS')

            mat = stm_obj.data.materials[0]
            cr_node = mat.node_tree.nodes['STM_gradient']
            layout.template_color_ramp(cr_node, "color_ramp", expand=False)


                


        if stm_obj.stm_spectro.material_type == 'custom':
            if stm_obj.active_material:
                # box = layout.box()
                # box.template_ID_preview(stm_obj.stm_spectro, "material_custom", hide_buttons=False)
                # layout.template_ID(stm_obj, "active_material", new="material.new")

                layout.prop(stm_obj.stm_spectro, "material_custom", text='')

            else:
                # col = layout.column(align=True)
                # box = col.box()
                # # box.scale_y = 20
                # # box.separator()

                # row = box.row()
                # row.label(text='')
                # row.scale_y =5.6
                # box.template_ID(stm_obj.stm_spectro, "material_custom", new="material.new",)

                layout.template_ID(stm_obj.stm_spectro, "material_custom", new="material.new",)

                
                
                # row = layout.row()
                # row.scale_y = 1.5
                # row.prop(stm_obj.stm_spectro, 'material_custom', text='')

class STM_PT_geometry_nodes_spectrogram(STM_Object_Panel, bpy.types.Panel):
    bl_label = ""
    bl_idname = "STM_PT_geometry_nodes_spectrogram"
    bl_parent_id = 'STM_PT_spectrogram_settings'

    @classmethod
    def poll(self, context):
        return bool(poll_draw_spectrogram_settings(context) or poll_draw_waveform_settings(context))

    def draw_header(self, context):
        layout = self.layout
        layout.label(text='Geometry Nodes', icon='GEOMETRY_NODES')
        

    def draw(self, context):
        layout = self.layout
        scn = context.scene

        stm_obj = funcs.get_stm_object(context.object)
        modifier = stm_obj.modifiers['STM_spectrogram']

        layout.enabled = stm_obj.modifiers["STM_spectrogram"]["Input_2"] != None and scn.stm_settings.progress == 0

        # row = layout.row()
        # row.enabled = False
        # row.prop(stm_obj, 'name', text='', icon='OBJECT_DATA')

        # layout.separator()

        row = layout.row(align=True)
        prop_geonode(row, stm_obj.modifiers['STM_spectrogram'], 'doCylinder', icon='NONE', label_name='Plane', toggle=1, invert_checkbox=True)
        prop_geonode(row, stm_obj.modifiers['STM_spectrogram'], 'doCylinder', icon='NONE', label_name='Cylinder', toggle=1)
        layout.popover('STM_PT_spectrogram_menu', text=stm_obj.stm_spectro.presets_geonodes_proper, icon='OPTIONS')


        # split_fac = 0.4

        # split = layout.split(factor=split_fac)
        # col1 = split.column(align=True)
        # col1.alignment = 'RIGHT'
        # col2 = split.column(align=True)   

        # col1.label(text='Shape')
        # row = col2.row(align=True)
        # prop_geonode(row, stm_obj.modifiers['STM_spectrogram'], 'doCylinder', icon='NONE', label_name='Plane', toggle=1, invert_checkbox=True)
        # prop_geonode(row, stm_obj.modifiers['STM_spectrogram'], 'doCylinder', icon='NONE', label_name='Cylinder', toggle=1)

        # col1.separator()
        # col2.separator()   

        # col1.label(text='Preset')
        # col2.popover('STM_PT_spectrogram_menu', text=stm_obj.stm_spectro.presets_geonodes_proper, icon='NONE')


        if modifier.node_group.users > 1:
            row = layout.row()
            row.alert = True
            row.operator('stm.fix_multiple_users', text='Multiple users (click to fix)', icon='ERROR')




        modifier = stm_obj.modifiers['STM_spectrogram']

        split_fac = 0.4

        split = layout.split(factor=split_fac)
        col1 = split.column(align=True)
        col1.alignment = 'RIGHT'
        col2 = split.column(align=True)

        

        col1.label(text='Log Scale')

        row = col2.row(align=True)
        prop_geonode(row, modifier, 'doLogScale', label=False)

        rrow = row.row()
        rrow.enabled = stm_obj.modifiers["STM_spectrogram"]["Socket_9"]
        prop_geonode(rrow, modifier, 'Lin To Log', label=False)

        col1.separator()
        col2.separator()

        col1.label(text='(Frequency) X')
        row = col2.row(align=True)
        prop_geonode(row, modifier, 'Freq Min (Hz)', label=False)
        prop_geonode(row, modifier, 'Freq Max (Hz)', label=False)
        col1.label(text='(Time) Y')
        prop_geonode(col2, modifier, 'Audio Sample (s)', label=False)
        col1.label(text='(Gain) Z')
        row = col2.row(align=True)
        prop_geonode(row, modifier, 'Gain', label=False)
        prop_geonode(row, modifier, 'doClamp', label=False, icon='LOCKED' if modifier['Socket_38'] else 'UNLOCKED')

        col1.separator()
        col2.separator()
        col1.separator()
        col2.separator()

        # if modifier['Socket_15'] == True:
        #     col1.label(text='Radius')
        #     prop_geonode(col2, modifier, 'Cylinder Radius', label=False)

        # else:
        col1.label(text='Extrude')

        row = col2.row(align=True)
        prop_geonode(row, modifier, 'doExtrude', label=False)

        ccol = row.column(align=True)
        ccol.enabled = stm_obj.modifiers["STM_spectrogram"]["Input_52"]
        prop_geonode(ccol, modifier, 'extrudeHeight', label=False)

        col1.separator()
        col2.separator()

        col1.label(text='Resolution X')
        col1.label(text='Y')                   
        prop_geonode(col2, modifier, 'Resolution X', label=False)
        prop_geonode(col2, modifier, 'Resolution Y', label=False)

        

        col1.separator()
        col2.separator()

        col1.label(text='Flip')
        row = col2.row(align=True)
        
        prop_geonode(row, modifier, 'flip_X', label_name='X', toggle=1)
        prop_geonode(row, modifier, 'flip_Y', label_name='Y', toggle=1)
        prop_geonode(row, modifier, 'flip_Z', label_name='Z', toggle=1)





class STM_PT_spectrogram_audio_settings(STM_Object_Panel, bpy.types.Panel):
    bl_label = ""
    bl_idname = "STM_PT_spectrogram_audio_settings"
    bl_parent_id = 'STM_PT_geometry_nodes_spectrogram'
    # bl_options = {'DEFAULT_CLOSED'}

    def draw_header(self, context):
        self.layout.label(text='Audio Mapping', icon='NONE')
        # self.layout.operator('stm.reset_spectrogram_main_settings', text='', icon='LOOP_BACK')

    # def draw_header_preset(self, context):
    #     self.layout.operator('stm.reset_spectrogram_main_settings', text='', icon='LOOP_BACK')

    def draw(self, context):
        layout = self.layout
        scn = context.scene
        stm_obj = funcs.get_stm_object(context.object)

        layout.enabled = scn.stm_settings.progress == 0

        modifier = stm_obj.modifiers['STM_spectrogram']

        split_fac = 0.4

        split = layout.split(factor=split_fac)
        col1 = split.column(align=True)
        col1.alignment = 'RIGHT'
        col2 = split.column(align=True)

        

        col1.label(text='Log Scale')

        row = col2.row(align=True)
        prop_geonode(row, modifier, 'doLogScale', label=False)

        rrow = row.row()
        rrow.enabled = stm_obj.modifiers["STM_spectrogram"]["Socket_9"]
        prop_geonode(rrow, modifier, 'Lin To Log', label=False)

        col1.separator()
        col2.separator()

        col1.label(text='(Frequency) X')
        row = col2.row(align=True)
        prop_geonode(row, modifier, 'Freq Min (Hz)', label=False)
        prop_geonode(row, modifier, 'Freq Max (Hz)', label=False)
        col1.label(text='(Time) Y')
        prop_geonode(col2, modifier, 'Audio Sample (s)', label=False)
        col1.label(text='(Gain) Z')
        row = col2.row(align=True)
        prop_geonode(row, modifier, 'Gain', label=False)
        prop_geonode(row, modifier, 'doClamp', label=False, icon='LOCKED' if modifier['Socket_38'] else 'UNLOCKED')

class STM_PT_spectrogram_geometry_settings(STM_Object_Panel, bpy.types.Panel):
    bl_label = ""
    bl_idname = "STM_PT_spectrogram_geometry_settings"
    bl_parent_id = 'STM_PT_geometry_nodes_spectrogram'
    bl_options = {'DEFAULT_CLOSED'}

    def draw_header(self, context):
        self.layout.label(text='Geometry', icon='NONE')
        # self.layout.operator('stm.reset_spectrogram_main_settings', text='', icon='LOOP_BACK')

    # def draw_header_preset(self, context):
    #     self.layout.operator('stm.reset_spectrogram_main_settings', text='', icon='LOOP_BACK')

    def draw(self, context):
        layout = self.layout
        scn = context.scene
        stm_obj = funcs.get_stm_object(context.object)

        layout.enabled = scn.stm_settings.progress == 0

        modifier = stm_obj.modifiers['STM_spectrogram']

        split_fac = 0.4

        split = layout.split(factor=split_fac)
        col1 = split.column(align=True)
        col1.alignment = 'RIGHT'
        col2 = split.column(align=True)


        if modifier['Socket_15'] == True:
            col1.label(text='Radius')
            prop_geonode(col2, modifier, 'Cylinder Radius', label=False)

        else:
            col1.label(text='Extrude')

            row = col2.row(align=True)
            prop_geonode(row, modifier, 'doExtrude', label=False)

            ccol = row.column(align=True)
            ccol.enabled = stm_obj.modifiers["STM_spectrogram"]["Input_52"]
            prop_geonode(ccol, modifier, 'extrudeHeight', label=False)

        col1.separator()
        col2.separator()

        col1.label(text='Resolution X')
        col1.label(text='Y')                   
        prop_geonode(col2, modifier, 'Resolution X', label=False)
        prop_geonode(col2, modifier, 'Resolution Y', label=False)

        

        col1.separator()
        col2.separator()

        col1.label(text='Flip')
        row = col2.row(align=True)
        
        prop_geonode(row, modifier, 'flip_X', label_name='X', toggle=1)
        prop_geonode(row, modifier, 'flip_Y', label_name='Y', toggle=1)
        prop_geonode(row, modifier, 'flip_Z', label_name='Z', toggle=1)


class STM_PT_spectrogram_modifiers_settings(STM_Object_Panel, bpy.types.Panel):
    bl_label = ""
    bl_idname = "STM_PT_spectrogram_modifiers_settings"
    # bl_parent_id = 'STM_PT_geometry_nodes_spectrogram'
    bl_parent_id = 'STM_PT_spectrogram_settings'
    bl_options = {'DEFAULT_CLOSED'}

    def draw_header(self, context):

        layout = self.layout
        layout.label(text='Modifiers', icon='MODIFIER')


    def draw(self, context):
        layout = self.layout
        scn = context.scene
        # layout.enabled = cont<ext.object.modifiers['STM_spectrogram']['Socket_42']

        layout.enabled = scn.stm_settings.progress == 0

        stm_obj = funcs.get_stm_object(context.object)
        modifier = stm_obj.modifiers['STM_spectrogram']

        button_text = 'Enable Modifiers' if not modifier['Socket_42'] else 'Disable Modifiers'
        button_icon = 'MODIFIER' if not modifier['Socket_42'] else 'PANEL_CLOSE'
        prop_geonode(self.layout, stm_obj.modifiers['STM_spectrogram'], 'doModifiers', label_name=button_text, icon=button_icon, toggle=1)

class STM_PT_spectrogram_contrast_settings(STM_Modifier_Panel, bpy.types.Panel):
    bl_label = ""
    bl_idname = "STM_PT_spectrogram_contrast_settings"
    bl_parent_id = 'STM_PT_spectrogram_modifiers_settings'
    bl_options = {'DEFAULT_CLOSED'}


    def draw_header(self, context):
        stm_obj = funcs.get_stm_object(context.object)
        self.layout.enabled = stm_obj.modifiers['STM_spectrogram']['Socket_42']
        

        prop_geonode(self.layout, stm_obj.modifiers['STM_spectrogram'], 'doContrast', label=False)
        self.layout.label(text='Contrast', icon='NONE')
        

    def draw(self, context):
        layout = self.layout
        scn = context.scene
        stm_obj = funcs.get_stm_object(context.object)

        layout.enabled = stm_obj.modifiers['STM_spectrogram']['Socket_12']

        split_fac = 0.4

        split = layout.split(factor=split_fac)
        col1 = split.column(align=True)
        col1.alignment = 'RIGHT'
        col2 = split.column(align=True)

        
        
        col1.label(text='Factor')                
        prop_geonode(col2, stm_obj.modifiers['STM_spectrogram'], 'Contrast', label=False)

class STM_PT_spectrogram_smooth_settings(STM_Modifier_Panel, bpy.types.Panel):
    bl_label = ""
    bl_idname = "STM_PT_spectrogram_smooth_settings"
    bl_parent_id = 'STM_PT_spectrogram_modifiers_settings'
    bl_options = {'DEFAULT_CLOSED'}


    def draw_header(self, context):
        
        stm_obj = funcs.get_stm_object(context.object)
        self.layout.enabled = stm_obj.modifiers['STM_spectrogram']['Socket_42']

        prop_geonode(self.layout, stm_obj.modifiers['STM_spectrogram'], 'doSmooth', label=False)
        self.layout.label(text='Smooth', icon='NONE')
        

    def draw(self, context):
        layout = self.layout
        scn = context.scene
        stm_obj = funcs.get_stm_object(context.object)

        layout.enabled = stm_obj.modifiers['STM_spectrogram']['Socket_10']

        split_fac = 0.4

        split = layout.split(factor=split_fac)
        col1 = split.column(align=True)
        col1.alignment = 'RIGHT'
        col2 = split.column(align=True)

        
        
        col1.label(text='Factor')                
        prop_geonode(col2, stm_obj.modifiers['STM_spectrogram'], 'Smooth Factor', label=False)

        col1.separator()
        col2.separator()

        col1.label(text='Level')
        prop_geonode(col2, stm_obj.modifiers['STM_spectrogram'], 'Smooth Level', label=False)

class STM_PT_spectrogram_noise_settings(STM_Modifier_Panel, bpy.types.Panel):
    bl_label = ""
    bl_idname = "STM_PT_spectrogram_noise_settings"
    bl_parent_id = 'STM_PT_spectrogram_modifiers_settings'
    bl_options = {'DEFAULT_CLOSED'}


    def draw_header(self, context):
        stm_obj = funcs.get_stm_object(context.object)
        self.layout.enabled = stm_obj.modifiers['STM_spectrogram']['Socket_42']

        prop_geonode(self.layout, stm_obj.modifiers['STM_spectrogram'], 'doNoise', label=False)
        self.layout.label(text='Noise', icon='NONE')

    def draw(self, context):
        layout = self.layout
        scn = context.scene
        stm_obj = funcs.get_stm_object(context.object)

        layout.enabled = stm_obj.modifiers['STM_spectrogram']['Socket_11']
 

        split_fac = 0.4

        split = layout.split(factor=split_fac)
        col1 = split.column(align=True)
        col1.alignment = 'RIGHT'
        col2 = split.column(align=True)

        col1.label(text='Strength')                
        prop_geonode(col2, stm_obj.modifiers['STM_spectrogram'], 'Noise Factor', label=False)

        col1.separator()
        col2.separator()

        col1.label(text='Scale')
        prop_geonode(col2, stm_obj.modifiers['STM_spectrogram'], 'Noise Scale', label=False)

class STM_PT_spectrogram_eqcurve_settings(STM_Modifier_Panel, bpy.types.Panel):
    bl_label = ""
    bl_idname = "STM_PT_spectrogram_eqcurve_settings"
    bl_parent_id = 'STM_PT_spectrogram_modifiers_settings'
    bl_options = {'DEFAULT_CLOSED'}


    def draw_header(self, context):
        stm_obj = funcs.get_stm_object(context.object)
        self.layout.enabled = stm_obj.modifiers['STM_spectrogram']['Socket_42']

        prop_geonode(self.layout, stm_obj.modifiers['STM_spectrogram'], 'doEQCurve', label=False)
        self.layout.label(text='EQ Curve', icon='NONE')

    def draw(self, context):
        layout = self.layout
        scn = context.scene
        stm_obj = funcs.get_stm_object(context.object)

        layout.enabled = stm_obj.modifiers['STM_spectrogram']['Socket_19']

        # layout.prop(obj, "presets_eq_curve", text='')

        split_fac = 0.4

        split = layout.split(factor=split_fac)
        col1 = split.column(align=True)
        col1.alignment = 'RIGHT'
        col2 = split.column(align=True)

        col1.label(text='Factor')
        prop_geonode(col2, stm_obj.modifiers['STM_spectrogram'], 'EQ Curve Factor', label=False)

        col1.separator()
        col2.separator()

        col1.label(text='Preset')
        row = col2.row(align=True)
        row.scale_x=5
        row.operator(
            operator='stm.apply_eq_curve_preset',
            text='',
            icon_value=preview_collections['presets_eq_curve']['0-reset.png'].icon_id
        ).preset_name='reset'
        row.operator(
            operator='stm.apply_eq_curve_preset',
            text='',
            icon_value=preview_collections['presets_eq_curve']['3-flatten_edges.png'].icon_id
        ).preset_name='flatten_edges'
        row.operator(
            operator='stm.apply_eq_curve_preset',
            text='',
            icon_value=preview_collections['presets_eq_curve']['1-lowpass.png'].icon_id
        ).preset_name='lowpass'
        row.operator(
            operator='stm.apply_eq_curve_preset',
            text='',
            icon_value=preview_collections['presets_eq_curve']['2-hipass.png'].icon_id
        ).preset_name='hipass'
        

        box = layout.box()

        curve = bpy.data.node_groups['STM_spectrogram'].nodes['MACURVE']
        box.template_curve_mapping(
            data=curve,
            property="mapping",
            type='NONE',
            levels=False,
            brush=False,
            show_tone=False,
        )

class STM_PT_spectrogram_curve_settings(STM_Modifier_Panel, bpy.types.Panel):
    bl_label = ""
    bl_idname = "STM_PT_spectrogram_curve_settings"
    bl_parent_id = 'STM_PT_spectrogram_modifiers_settings'
    bl_options = {'DEFAULT_CLOSED'}

    def draw_header(self, context):
        stm_obj = funcs.get_stm_object(context.object)
        self.layout.enabled = stm_obj.modifiers['STM_spectrogram']['Socket_42']

        prop_geonode(self.layout, stm_obj.modifiers['STM_spectrogram'], 'doCurve', label=False)
        self.layout.label(text='Curve Deform', icon='NONE')
        

    def draw(self, context):
        layout = self.layout
        scn = context.scene
        stm_obj = funcs.get_stm_object(context.object)

        layout.enabled = stm_obj.modifiers['STM_spectrogram']['Socket_17']

        split_fac = 0.4

        split = layout.split(factor=split_fac)
        col1 = split.column(align=True)
        col1.alignment = 'RIGHT'
        col2 = split.column(align=True)

        col1.label(text='Curve Object')
        col2.prop(stm_obj.stm_spectro, 'curve_object', text='')

        col1.separator()
        col2.separator()

        row = col1.row(align=True)
        row.alignment = 'RIGHT'
        row.enabled = not stm_obj.modifiers['STM_spectrogram']['Socket_15']
        row.label(text='Deform Axis')

        row = col2.row(align=True)
        row.enabled = not stm_obj.modifiers['STM_spectrogram']['Socket_15']
        row.prop(stm_obj.stm_spectro, 'curve_deform_axis', text='')       

class STM_PT_waveform_settings(STM_Panel, bpy.types.Panel):
    bl_label = ""
    bl_idname = "STM_PT_waveform_settings"
    # bl_parent_id = 'STM_PT_spectrogram_settings'

    @classmethod
    def poll(self, context):
        return bool(poll_draw_spectrogram_settings(context) or poll_draw_waveform_settings(context))

    def draw_header(self, context):
        layout = self.layout
        # layout.label(text='Waveform Settings', icon='RNDCURVE')
        layout.label(text='Waveform Settings', icon='NONE')

    def draw(self, context):
        layout = self.layout
        scn = context.scene
        stm_obj = funcs.get_stm_object(context.object)
        

        row = layout.row()
        row.enabled = scn.stm_settings.progress == 0

        row.template_list("STM_UL_draw_items", "", stm_obj.stm_spectro, "stm_items", stm_obj.stm_spectro, "stm_items_active_index", rows=3, sort_lock=True)

        col = row.column(align=True)
        col.operator("stm.add_waveform", icon='ADD', text="")
        col.operator("stm.delete_waveform", icon='REMOVE', text="")

        # row = layout.row(align=True)
        # row.prop_enum(obj.stm_spectro, 'material_type', 'emission')
        # row.prop_enum(obj.stm_spectro, 'material_type', 'custom')


class STM_PT_material_waveform(STM_Panel, bpy.types.Panel):
    bl_label = ""
    bl_idname = "STM_PT_material_waveform"
    bl_parent_id = 'STM_PT_waveform_settings'
    bl_options = {'DEFAULT_CLOSED'}

    @classmethod
    def poll(self, context):
        return bool(poll_draw_waveform_settings(context) and len(funcs.get_stm_object(context.object).stm_spectro.stm_items) > 0)

    def draw_header(self, context):
        layout = self.layout
        layout.label(text='Material', icon='MATERIAL')

    def draw(self, context):
        layout = self.layout
        scn = context.scene
        stm_obj = funcs.get_stm_object(context.object)
        obj = stm_obj.stm_spectro.stm_items[stm_obj.stm_spectro.stm_items_active_index].object

        modifier = obj.modifiers['STM_waveform']

        


    
        row = layout.row(align=True)
        row.prop_enum(obj.stm_spectro, 'material_type', 'emission')
        row.prop_enum(obj.stm_spectro, 'material_type', 'custom')


        

        if obj.stm_spectro.material_type == 'emission':


            split_fac = 0.4

            split = layout.split(factor=split_fac)
            col1 = split.column(align=True)
            col1.alignment = 'RIGHT'
            col2 = split.column(align=True)

            col1.label(text='Color')
            prop_geonode(col2, modifier, 'waveform_color', label=False)

            col1.separator()
            col2.separator()

            col1.label(text='Emission')
            prop_geonode(col2, modifier, 'emission_strength', label=False)


        if obj.stm_spectro.material_type == 'custom':
            if obj.active_material:
                layout.prop(obj.stm_spectro, 'material_custom', text='')
            else:
                layout.template_ID(obj.stm_spectro, "material_custom", new="material.new")

class STM_PT_geometry_nodes_waveform(STM_Object_Panel, bpy.types.Panel):
    bl_label = ""
    bl_idname = "STM_PT_geometry_nodes_waveform"
    bl_parent_id = 'STM_PT_waveform_settings'

    @classmethod
    def poll(self, context):
        # return bool(len(funcs.get_stm_object(context.object).stm_spectro.stm_items) > 0)
        return poll_draw_waveform_settings(context)
    
    def draw_header(self, context):
        layout = self.layout
        # layout.label(text='Waveform Settings', icon='RNDCURVE')
        layout.label(text='Geometry Nodes', icon='GEOMETRY_NODES')

    def draw(self, context):
        layout = self.layout
        scn = context.scene
        stm_obj = funcs.get_stm_object(context.object)
        obj = stm_obj.stm_spectro.stm_items[stm_obj.stm_spectro.stm_items_active_index].object
        

        modifier = obj.modifiers['STM_waveform']

        # row = layout.row()
        # row.enabled = False
        # row.prop(obj, 'name', text='', icon='OBJECT_DATA')

        # layout.separator()

        split_fac = 0.4


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

        col1.label(text='Shape')
        row =col2.row(align=True)
        row.scale_x = 5
        row.prop(obj, "presets_waveform_style", text='', expand=False)

class STM_PT_waveform_main_settings(STM_Object_Panel, bpy.types.Panel):
    bl_label = ""
    bl_idname = "STM_PT_waveform_main_settings"
    bl_parent_id = 'STM_PT_geometry_nodes_waveform'
    # bl_options = {'DEFAULT_CLOSED'}

    def draw_header(self, context):

        layout = self.layout
        layout.label(text='Settings', icon='NONE')

    def draw(self, context):
        layout = self.layout
        scn = context.scene
        stm_obj = funcs.get_stm_object(context.object)
        obj = stm_obj.stm_spectro.stm_items[stm_obj.stm_spectro.stm_items_active_index].object
        

        modifier = obj.modifiers['STM_waveform']


        split_fac = 0.4


        split = layout.split(factor=split_fac)
        col1 = split.column(align=True)
        col1.alignment = 'RIGHT'
        col2 = split.column(align=True)

        col1.label(text='Resample')

        row = col2.row(align=True)
        prop_geonode(row, modifier, 'doResample', label=False)

        ccol = row.column(align=True)
        ccol.enabled = modifier["Input_17"]
        prop_geonode(ccol, modifier, 'Resample Resolution', label=False)

        col1.separator()
        col2.separator()

        col1.label(text='Offset')
        prop_geonode(col2, modifier, 'Offset', label=False)

        col1.separator()
        col2.separator()

        if funcs.get_geonode_value_proper(modifier, 'waveform_style') == 0:

            col1.label(text='Handle Type')
            row = col2.row(align=True)
            prop_geonode(row, modifier, 'doHandleAuto', icon='HANDLE_VECTOR', label_name='Vector', toggle=1, invert_checkbox=True)
            prop_geonode(row, modifier, 'doHandleAuto', icon='HANDLE_AUTO', label_name='Auto', toggle=1)

            col1.separator()
            col2.separator()

        if funcs.get_geonode_value_proper(modifier, 'waveform_style') == 2:

            col1.label(text='Ends')
            row = col2.row(align=True)
            prop_geonode(row, modifier, 'doRoundBars', icon='GP_CAPS_FLAT', label_name='Flat', toggle=1, invert_checkbox=True)
            prop_geonode(row, modifier, 'doRoundBars', icon='GP_CAPS_ROUND', label_name='Round', toggle=1)

            col1.separator()
            col2.separator()

        


        

        if funcs.get_geonode_value_proper(modifier, 'waveform_style') == 2:

            col1.label(text='Width')
            prop_geonode(col2, modifier, 'Width', label=False)

            col1.separator()
            col2.separator()

        col1.label(text='Thickness')
        prop_geonode(col2, modifier, 'Thickness', label=False)

        

        col1.separator()
        col2.separator()


        

        col1.label(text='Smooth')
        col1.label(text='')
        row = col2.row(align=True)
        prop_geonode(row, modifier, 'doSmooth', label=False)

        ccol = row.column(align=True)
        ccol.enabled = modifier["Socket_8"]
        prop_geonode(ccol, modifier, 'Smooth Factor', label=False)
        prop_geonode(ccol, modifier, 'Smooth Level', label_name='Level')

        
        # row = col1.row()
        # row.alignment = 'RIGHT'
        # # row.scale_y = 1.5
        # row.label(text='Shape')
        
        # row = col2.row(align=True)
        # row.scale_x = 5
        # # row.scale_y = 1.5
        # row.prop(obj, "presets_waveform_style", text='', icon_only=True, expand=True)

        # col1.separator()
        # col2.separator()


classes = [

    STM_PT_spectrogram_menu,
    STM_MT_audio_menu,
    STM_MT_image_menu,

    STM_PT_spectrogram,
    STM_UL_draw_items,


    STM_PT_spectrogram_settings,
    
    STM_PT_spectrogram_overlay_settings,
    STM_PT_material_spectrogram,
    STM_PT_geometry_nodes_spectrogram,

    # STM_PT_spectrogram_audio_settings,
    # STM_PT_spectrogram_geometry_settings,

    STM_PT_spectrogram_modifiers_settings,
    
    STM_PT_spectrogram_contrast_settings,
    STM_PT_spectrogram_smooth_settings,
    STM_PT_spectrogram_noise_settings,
    STM_PT_spectrogram_eqcurve_settings,
    STM_PT_spectrogram_curve_settings,


    
    STM_PT_waveform_settings,

    STM_PT_material_waveform,    
    STM_PT_geometry_nodes_waveform,
    STM_PT_waveform_main_settings,
    

    

]


def register():
    for c in classes:
        bpy.utils.register_class(c)

def unregister():
    for c in classes:
        bpy.utils.unregister_class(c)