import bpy
import os
from bpy.types import Panel
from bpy.types import UIList, PropertyGroup
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


def poll_draw_spectrogram_tab(context):
    if not context.object:
        return
    if context.object.stm_spectro.stm_type not in ['spectrogram', 'waveform']:
        return


    return True

def poll_draw_spectrogram_main_settings(context):
    if not context.object:
        return
    
    

    # if context.object.stm_spectro.stm_type != 'spectrogram':
    #     return
    if context.scene.stm_settings.stm_settings_tab != 'spectrogram':
        return

    return True

def poll_draw_spectrogram_settings(context):
    if not context.object:
        return
    
    if context.object.stm_spectro.stm_type != 'spectrogram':
        return

    return True

def poll_draw_waveform_settings(context):
    if not context.object:
        return
    if context.object.stm_spectro.stm_type != 'waveform':
        return
    
    return True

def draw_spectro_item(context, layout, obj):
    row = layout.row(align=True)
    row.prop(obj.stm_spectro, "panel_expand", icon='DOWNARROW_HLT' if obj.stm_spectro.panel_expand else 'RIGHTARROW', emboss=False, text="")
    row.prop(obj, "name", icon='SEQ_HISTOGRAM', emboss=False, text="")
    if obj.stm_spectro.audio_file:
        is_audio_active = False

        seq = context.scene.sequence_editor
        if seq:
            for s in seq.sequences:
                if s.stm_settings.spectrogram_object == obj:
                    is_audio_active = not s.mute

        if context.scene.stm_settings.enable_audio_in_scene:
            rrow = row.row()
            rrow.prop(
                obj.stm_spectro,
                'audio_toggle', 
                text='', 
                icon='OUTLINER_OB_SPEAKER' if is_audio_active else 'OUTLINER_DATA_SPEAKER', 
                emboss=False
            )

    if context.scene.stm_settings.show_display_viewport_icon:
        row.prop(obj.stm_spectro, 'hide_viewport_base', icon_only=True, emboss=False, icon='HIDE_ON' if obj.stm_spectro.hide_viewport_base else 'HIDE_OFF')
    if context.scene.stm_settings.show_disable_viewport_icon:
        row.prop(obj, "hide_viewport", text="", emboss=False)
    if context.scene.stm_settings.show_disable_render_icon:
        row.prop(obj, "hide_render", text="", emboss=False)


def draw_waveform_item(context, layout, obj):
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
    row.label(text='', icon='BLANK1')
    row.prop(obj, "name", icon_value=custom_icon, emboss=False, text="")
    # row.prop(obj.stm_spectro, 'is_parented_to_spectrogram', text='', icon=parent_icon, emboss=False)

    if context.scene.stm_settings.show_display_viewport_icon:
        row.prop(obj.stm_spectro, 'hide_viewport_base', icon_only=True, emboss=False, icon='HIDE_ON' if obj.stm_spectro.hide_viewport_base else 'HIDE_OFF')
    if context.scene.stm_settings.show_disable_viewport_icon:
        row.prop(obj, "hide_viewport", text="", emboss=False)
    if context.scene.stm_settings.show_disable_render_icon:
        row.prop(obj, "hide_render", text="", emboss=False)

class STM_UL_draw_spectro_list(UIList):
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
        obj = item.object

        if obj.stm_spectro.stm_type == 'spectrogram':
            draw_spectro_item(context, layout, obj)

        elif obj.stm_spectro.stm_type == 'waveform':
            draw_waveform_item(context, layout, obj)
                

    def invoke(self, context, event):
        pass

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

class STM_MT_spectro_list_menu(bpy.types.Menu):
    bl_idname = "STM_MT_spectro_list_menu"
    bl_label = "Add element"

    def draw(self, context):
        layout = self.layout

        layout.operator('stm.duplicate_waveform', text='Duplicate Waveform', icon='DUPLICATE')

        layout.separator()
        
        layout.operator('stm.open_image', text='Open image', icon='IMAGE_DATA')
        layout.operator('stm.open_image_folder', text='Open image folder', icon='FILEBROWSER')

        layout.separator()

        layout.prop(context.scene.stm_settings, 'doLiveSyncAudio', text='Live Sync Audio', icon='UV_SYNC_SELECT')

        # for i in preview_collections['presets_waveform_style_AB']:
        #     print(i)


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

class STM_MT_eq_curve_menu(bpy.types.Menu):
    bl_idname = "STM_MT_eq_curve_menu"
    bl_label = "Select"

    def draw(self, context):
        layout = self.layout


        layout.label(text='EQ Curve Preset')
        layout.separator()
        
        layout.operator(
            operator='stm.apply_eq_curve_preset',
            text='Flat',
            icon_value=preview_collections['presets_eq_curve']['0-reset.png'].icon_id
        ).preset_name='reset'
        layout.operator(
            operator='stm.apply_eq_curve_preset',
            text='Flatten edges',
            icon_value=preview_collections['presets_eq_curve']['3-flatten_edges.png'].icon_id
        ).preset_name='flatten_edges'
        layout.operator(
            operator='stm.apply_eq_curve_preset',
            text='Lowpass',
            icon_value=preview_collections['presets_eq_curve']['1-lowpass.png'].icon_id
        ).preset_name='lowpass'
        layout.operator(
            operator='stm.apply_eq_curve_preset',
            text='Hipass',
            icon_value=preview_collections['presets_eq_curve']['2-hipass.png'].icon_id
        ).preset_name='hipass'

class STM_PT_eq_curve_popover(bpy.types.Panel):
    bl_idname = "STM_PT_eq_curve_popover"
    bl_description = "Select preset"
    bl_label = "Select"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'WINDOW'
    # bl_options = {'INSTANCED'}
    bl_ui_units_x = 5

    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self, width=100)

    def draw(self, context):
        layout = self.layout
        layout.emboss='PULLDOWN_MENU'

        layout.label(text='Preset')
        layout.separator()

        row = layout.row()
        row.alignment = 'LEFT'
        row.operator(
            operator='stm.apply_eq_curve_preset',
            text='Flat',
            icon_value=preview_collections['presets_eq_curve']['0-reset.png'].icon_id
        ).preset_name='reset'

        row = layout.row()
        row.alignment = 'LEFT'
        row.operator(
            operator='stm.apply_eq_curve_preset',
            text='Flatten Edges',
            icon_value=preview_collections['presets_eq_curve']['3-flatten_edges.png'].icon_id
        ).preset_name='flatten_edges'

        row = layout.row()
        row.alignment = 'LEFT'
        row.operator(
            operator='stm.apply_eq_curve_preset',
            text='Lowpass',
            icon_value=preview_collections['presets_eq_curve']['1-lowpass.png'].icon_id
        ).preset_name='lowpass'

        row = layout.row()
        row.alignment = 'LEFT'
        row.operator(
            operator='stm.apply_eq_curve_preset',
            text='Hipass',
            icon_value=preview_collections['presets_eq_curve']['2-hipass.png'].icon_id
        ).preset_name='hipass'


class STM_PT_spectrogram_presets_menu(bpy.types.Panel):
    bl_idname = "STM_PT_spectrogram_presets_menu"
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



class STM_PT_add_new_panel(STM_Panel, bpy.types.Panel):
    bl_label = "Sound To Mesh"
    bl_idname = "STM_PT_add_new_panel"

    # @classmethod
    # def poll(self, context):
    #     return not bool(poll_draw_spectrogram_tab(context))

    

    def draw(self, context):
        layout = self.layout
        scn = context.scene
        obj = context.object

        # stm_logo = preview_collections['stm_logo']['6-stm_logo.png'].icon_id
        # layout.template_icon(stm_logo, scale=6.0)

        

        # layout.operator('stm.refresh_stm_objects', text='Refresh STM objects', icon='FILE_REFRESH')

        # row = layout.row(align=True)
        # row.operator('stm.add_spectrogram', text='Spectrogram', icon='SEQ_HISTOGRAM')
        # row.operator('stm.add_waveform', text='Waveform', icon='RNDCURVE')

        # row = layout.row()
        # row.emboss = 'NONE'
        # row.template_icon_view(scn, "icons_ui", show_labels=True, scale=6.0, scale_popup=17.0)

        # row = layout.row()
        # row.alignment = 'RIGHT'
        # row.popover(
        #         panel='STM_PT_settings_popover_menu',
        #         # text='',
        #         icon='PREFERENCES',
                
        #     )
        

        row = layout.row()
        row.alignment = 'RIGHT'
        
        row1 = row.row(align=True)
        row2 = row.row(align=True)

        row1.prop(scn.stm_settings, 'enable_audio_in_scene', icon='OUTLINER_OB_SPEAKER', icon_only=True)
        sub_row = row1.row(align=True)
        sub_row.enabled = scn.stm_settings.enable_audio_in_scene
        sub_row.prop(context.scene.stm_settings, 'doLiveSyncAudio', icon='UV_SYNC_SELECT', icon_only=True)
        sub_row.prop(scn.stm_settings, 'audio_volume')

        row2.prop(scn.stm_settings, 'show_display_viewport_icon', icon='HIDE_OFF', icon_only=True)
        row2.prop(scn.stm_settings, 'show_disable_viewport_icon', icon='RESTRICT_VIEW_OFF', icon_only=True)
        row2.prop(scn.stm_settings, 'show_disable_render_icon', icon='RESTRICT_RENDER_OFF', icon_only=True)

        

        row = layout.row()
        row.enabled = scn.stm_settings.progress == 0
        list_length = 5 if len(scn.stm_settings.stm_objects_list) < 5 else len(scn.stm_settings.stm_objects_list) + 1
        row.template_list("STM_UL_draw_spectro_list", "", scn.stm_settings, "stm_objects_list", scn.stm_settings, "stm_objects_list_active_index", rows=list_length, sort_lock=True)
        

        col = row.column(align=True)

        # col.operator('stm.add_spectrogram', text='', icon_value=preview_collections['icons_ui']['add_spectrogram.png'].icon_id)
        # col.operator('stm.add_waveform', text='', icon_value=preview_collections['icons_ui']['add_waveform.png'].icon_id)
        col.operator('stm.add_waveform', text='', icon='ADD')
        col.operator('stm.delete_element', text='', icon='REMOVE')
        

        col.separator()

        col.menu('STM_MT_spectro_list_menu', text='', icon='DOWNARROW_HLT')

        col.separator()

        col.operator('stm.move_waveform_up', text='', icon='TRIA_UP')           
        col.operator('stm.move_waveform_down', text='', icon='TRIA_DOWN')           


        # layout.progress(text='ouhlala', factor = 0.66, type = 'BAR')

         # layout.operator('stm.mute_all_spectrogram', text='Mute All', icon='QUIT')

        row = layout.row(align=True)
        row.scale_y = 1.5

        if scn.stm_settings.progress != 0:
            row.prop(scn.stm_settings,"progress", text=scn.stm_settings.progress_label)
            return

        if bool(poll_draw_spectrogram_settings(context)):
            row1 = row.row(align=True)
            row2 = row.row(align=True)

            row1.scale_x = 1.1

            row1.operator('stm.add_spectrogram', text='', icon='ADD')
            row2.operator('stm.update_spectrogram', text='Update Spectrogram', icon='FILE_REFRESH')
            
        else:
            row.operator('stm.add_spectrogram', text='New Spectrogram', icon='ADD')

        
       
    
class STM_PT_viewport_settings(STM_Panel, bpy.types.Panel):
    bl_label = "Viewport & Rendering"
    bl_idname = "STM_PT_viewport_settings"
    bl_parent_id = 'STM_PT_add_new_panel'
    bl_options = {'DEFAULT_CLOSED'}

    def draw(self, context):

        layout = self.layout

        layout.label(text=('hello'))


class STM_PT_spectrogram_panel(STM_Panel, bpy.types.Panel):
    bl_label = "Spectrogram Settings"
    bl_idname = "STM_PT_spectrogram_panel"
    # bl_parent_id = 'STM_PT_add_new_panel'

    updater = True

    @classmethod
    def poll(self, context):
        return poll_draw_spectrogram_settings(context)

    def draw(self, context):
        

        layout = self.layout
        scn = context.scene

        layout.enabled = bool(scn.stm_settings.progress == 0)
        

        stm_obj = funcs.get_stm_object(context.object)

        row = layout.row(align=True)
        row.enabled = False
        row.template_ID(context.view_layer.objects, 'active', text='')

        box = layout.box()

        ccol = box.column()
        ccol.template_icon_view(stm_obj, "preview_image_enum", show_labels=True, scale=6.0, scale_popup=17.0)

        row_title = ccol.row()
        row_title.enabled = False

        row_info = ccol.row()
        row_info.enabled = False
        rowL = row_info.row()
        rowL.alignment = 'LEFT'
        rowR = row_info.row()
        rowR.alignment = 'RIGHT'

        
        
        if stm_obj.stm_spectro.image_file == None:
            row_title.label(text='no audio')
            rowL.label(text='---')
            rowR.label(text='---')
        else:
            row_title.label(text=stm_obj.stm_spectro.audio_filename)
            rowL.label(text=f"{stm_obj.stm_spectro.image_file.size[0]}x{stm_obj.stm_spectro.image_file.size[1]}")
            if os.path.exists(stm_obj.stm_spectro.image_file.filepath):
                rowR.label(text=funcs.convert_size(os.path.getsize(stm_obj.stm_spectro.image_file.filepath)))

            



                  
class STM_PT_waveform_panel(STM_Panel, bpy.types.Panel):
    bl_label = "Waveform Settings"
    bl_idname = "STM_PT_waveform_panel"
    # bl_parent_id = 'STM_PT_spectrogram'

    updater = True

    @classmethod
    def poll(self, context):
        return poll_draw_waveform_settings(context)

    def draw(self, context):
        

        layout = self.layout
        scn = context.scene
        obj = context.object

        

        stm_obj = funcs.get_stm_object(context.object)   
        

        modifier = obj.modifiers['STM_waveform']

        # row = layout.row()
        # row.enabled = False
        # row.prop(obj, 'name', text='', icon='OBJECT_DATA')

        # layout.separator()


        row = layout.row()
        row.enabled = False
        row.template_ID(context.view_layer.objects, 'active', text='')

        split_fac = 0.4


        split = layout.split(factor=split_fac)
        col1 = split.column(align=True)
        col1.alignment = 'RIGHT'
        col2 = split.column(align=True)

        col1.label(text='Type')
        row =col2.row(align=True)
        row.scale_x = 5
        row.prop(obj, "presets_waveform_style", text='', expand=False)



class STM_PT_modifiers_spectrogram(STM_Panel, bpy.types.Panel):
    bl_label = "Modifiers"
    bl_idname = "STM_PT_modifiers_spectrogram"
    bl_parent_id = 'STM_PT_spectrogram_panel'
    bl_options = {'DEFAULT_CLOSED'}

    @classmethod
    def poll(self, context):
        return poll_draw_spectrogram_settings(context)

    def draw_header(self, context):
        layout = self.layout
        prop_geonode(layout, context.object.modifiers['STM_spectrogram'], 'doModifiers', label=False)

        

    def draw(self, context):
        layout = self.layout
        scn = context.scene

        layout.enabled = bool(scn.stm_settings.progress == 0 and context.object.modifiers['STM_spectrogram']["Socket_42"])

        stm_obj = funcs.get_stm_object(context.object)
        modifier = stm_obj.modifiers['STM_spectrogram']

        split_fac = 0.4

        split = layout.split(factor=split_fac)
        col1 = split.column(align=True)
        col1.alignment = 'RIGHT'
        col2 = split.column(align=True)

        col1.label(text='Contrast')
        row = col2.row(align=True)
        prop_geonode(row, modifier, 'doContrast', label=False)   

        ccol = row.column(align=True)
        ccol.enabled = modifier["Socket_12"]
        prop_geonode(ccol, modifier, 'Contrast', label=False)


        col1.separator()
        col2.separator()
        

        col1.label(text='Smooth')
        row = col2.row(align=True)
        prop_geonode(row, modifier, 'doSmooth', label=False)   

        ccol = row.column(align=True)
        ccol.enabled = modifier["Socket_10"]
        prop_geonode(ccol, modifier, 'Smooth Factor', label=False)
        if ccol.enabled:
            col1.label(text='')
            prop_geonode(ccol, modifier, 'Smooth Level', label=True, label_name='Level')


        col1.separator()
        col2.separator()



        col1.label(text='Follow Curve')
        row = col2.row(align=True)
        prop_geonode(row, modifier, 'doCurve', label=False)   

        ccol = row.column(align=True)
        ccol.enabled = modifier["Socket_17"]
        prop_geonode(ccol, modifier, 'Curve Object', label=False)

        if ccol.enabled:
            col1.label(text='')
            rrow = ccol.row(align=True)      
            rrow.prop_enum(stm_obj.stm_spectro, 'curve_deform_axis', '1')
            rrow.prop_enum(stm_obj.stm_spectro, 'curve_deform_axis', '2')

        col1.separator()
        col2.separator()


        col1.label(text='EQ Curve')
        row = col2.row(align=True)
        prop_geonode(row, modifier, 'doEQCurve', label=False)   

        ccol = row.column(align=True)
        ccol.enabled = modifier["Socket_19"]
        rrow = ccol.row(align=True)
        prop_geonode(rrow, modifier, 'EQ Curve Factor', label=False)
        rrow.menu('STM_MT_eq_curve_menu', text='', icon='DOWNARROW_HLT')
        # rrow.popover('STM_PT_eq_curve_popover', text='', icon='DOWNARROW_HLT')

        if ccol.enabled:          

            bbox = layout.box()

            curve = modifier.node_group.nodes['MACURVE']
            bbox.template_curve_mapping(
                data=curve,
                property="mapping",
                type='NONE',
                levels=False,
                brush=False,
                show_tone=False,
            )

class STM_PT_overlays_spectrogram(STM_Panel, bpy.types.Panel):
    bl_label = "Overlays"
    bl_idname = "STM_PT_overlays_spectrogram"
    bl_parent_id = 'STM_PT_spectrogram_panel'
    bl_options = {'DEFAULT_CLOSED'}

    @classmethod
    def poll(self, context):
        return poll_draw_spectrogram_settings(context)

    def draw_header(self, context):
        layout = self.layout
        prop_geonode(layout, context.object.modifiers['STM_spectrogram'], 'doOverlays', label=False)

        

    def draw(self, context):
        layout = self.layout
        scn = context.scene

        layout.enabled = bool(scn.stm_settings.progress == 0 and context.object.modifiers['STM_spectrogram']["Socket_39"])

        stm_obj = funcs.get_stm_object(context.object)

        split_fac = 0.4

        split = layout.split(factor=split_fac)
        col1 = split.column(align=True)
        col1.alignment = 'RIGHT'
        col2 = split.column(align=True)

        col1.label(text='Title')

        row = col2.row(align=True)
        prop_geonode(row, stm_obj.modifiers['STM_spectrogram'], 'showTitle', label=False)

        ccol = row.column(align=True)
        ccol.enabled = stm_obj.modifiers["STM_spectrogram"]["Socket_16"]
        prop_geonode(ccol, stm_obj.modifiers['STM_spectrogram'], 'Title', label=False)

        col1.separator()
        col2.separator()

        col1.label(text='Grid')

        row = col2.row(align=True)
        prop_geonode(row, stm_obj.modifiers['STM_spectrogram'], 'showGridFull', label=False)
        
        row = row.row(align=True)
        row.enabled = stm_obj.modifiers["STM_spectrogram"]["Socket_18"]
        prop_geonode(row, stm_obj.modifiers['STM_spectrogram'], 'showGridX', label_name='X', toggle=1)
        prop_geonode(row, stm_obj.modifiers['STM_spectrogram'], 'showGridY', label_name='Y', toggle=1)
        prop_geonode(row, stm_obj.modifiers['STM_spectrogram'], 'showGridZ', label_name='Z', toggle=1)


class STM_PT_spectrogram_main_settings(STM_Object_Panel, bpy.types.Panel):
    bl_label = "Settings"
    bl_idname = "STM_PT_spectrogram_main_settings"
    bl_parent_id = 'STM_PT_spectrogram_panel'

    @classmethod
    def poll(self, context):
        return poll_draw_spectrogram_settings(context)

    # def draw_header(self, context):
    #     layout = self.layout
    #     # layout.label(text='Geometry Nodes', icon='GEOMETRY_NODES')
    #     layout.label(text='Settings', icon='NONE')
    #     layout.enabled = bool(funcs.get_stm_object(context.object).stm_spectro.image_file != None)

    def draw_header_preset(self, context):
        layout = self.layout
        # self.layout.operator('stm.reset_spectrogram_main_settings', text='', icon='LOOP_BACK')
        layout.emboss = 'NONE'
        layout.popover('STM_PT_spectrogram_presets_menu', text='', icon='PRESET')
        layout.enabled = bool(funcs.get_stm_object(context.object).stm_spectro.image_file != None)
        

    def draw(self, context):
        layout = self.layout
        scn = context.scene

        stm_obj = funcs.get_stm_object(context.object)
        modifier = stm_obj.modifiers['STM_spectrogram']

        layout.enabled = stm_obj.modifiers["STM_spectrogram"]["Input_2"] != None and scn.stm_settings.progress == 0


        if modifier.node_group.users > 1:
            row = layout.row()
            row.alert = True
            row.operator('stm.fix_multiple_users', text='Multiple users (click to fix)', icon='ERROR')


        split_fac = 0.4

        split = layout.split(factor=split_fac)
        col1 = split.column(align=True)
        col1.alignment = 'RIGHT'
        col2 = split.column(align=True)
        

        col1.label(text='Frequency')
        row = col2.row(align=True)
        prop_geonode(row, modifier, 'Freq Min (Hz)', label=False)
        prop_geonode(row, modifier, 'Freq Max (Hz)', label=False)
        col1.label(text='Time')
        prop_geonode(col2, modifier, 'Audio Sample (s)', label=False)
        col1.label(text='Gain')
        row = col2.row(align=True)
        prop_geonode(row, modifier, 'Gain', label=False)
        prop_geonode(row, modifier, 'doClamp', label=False, icon='LOCKED' if modifier['Socket_38'] else 'UNLOCKED')

        col1.separator()
        col2.separator()


        col1.label(text='Log Scale')

        row = col2.row(align=True)
        prop_geonode(row, modifier, 'doLogScale', label=False)

        rrow = row.row()
        rrow.enabled = stm_obj.modifiers["STM_spectrogram"]["Socket_9"]
        prop_geonode(rrow, modifier, 'Lin To Log', label=False)    

        

        

class STM_PT_spectrogram_geometry_settings(STM_Object_Panel, bpy.types.Panel):
    bl_label = "Geometry"
    bl_idname = "STM_PT_spectrogram_geometry_settings"
    bl_parent_id = 'STM_PT_spectrogram_panel'
    # bl_options = {'DEFAULT_CLOSED'}

    @classmethod
    def poll(self, context):
        return poll_draw_spectrogram_settings(context)

    # def draw_header(self, context):
        # self.layout.label(text='Geometry', icon='MESH_DATA')

    def draw(self, context):
        layout = self.layout
        scn = context.scene
        stm_obj = funcs.get_stm_object(context.object)

        layout.enabled = scn.stm_settings.progress == 0

        modifier = stm_obj.modifiers['STM_spectrogram']

        split_fac = 0.4

        split = layout.split(factor=split_fac)
        split.enabled = bool(stm_obj.stm_spectro.image_file != None)

        col1 = split.column(align=True)
        col1.alignment = 'RIGHT'
        col2 = split.column(align=True)


        col1.label(text='Shape')
        row = col2.row(align=True)
        prop_geonode(row, modifier, 'doCylinder', icon='NONE', label_name='Plane', toggle=1, invert_checkbox=True)
        prop_geonode(row, modifier, 'doCylinder', icon='NONE', label_name='Cylinder', toggle=1)

        col1.separator()
        col2.separator()
        
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
          
class STM_PT_material_spectrogram(STM_Panel, bpy.types.Panel):
    bl_label = "Material"
    bl_idname = "STM_PT_material_spectrogram"
    bl_parent_id = 'STM_PT_spectrogram_panel'
    bl_options = {'DEFAULT_CLOSED'}

    @classmethod
    def poll(self, context):
        return poll_draw_spectrogram_settings(context)

    def draw_header(self, context):
        layout = self.layout
        layout.label(text='', icon='MATERIAL')

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

            col.template_icon_view(stm_obj, "preview_image_enum", show_labels=True, scale=6.0, scale_popup=17.0)

            row = col.row()
            row.scale_y=0.9
            row.enabled = False
            rowL = row.row()
            rowL.alignment = 'LEFT'
            rowR = row.row()
            rowR.alignment = 'RIGHT'
            
            if stm_obj.stm_spectro.image_file == None:
                rowL.label(text='---')
                rowR.label(text='---')
            else:
                rowL.label(text=f"{stm_obj.stm_spectro.image_file.size[0]}x{stm_obj.stm_spectro.image_file.size[1]}")
                rowR.label(text=funcs.convert_size(os.path.getsize(stm_obj.stm_spectro.image_file.filepath)))

            
            row = layout.row()
            row.operator('stm.open_image', text='Open Image', icon='IMAGE_DATA')
            row.operator('stm.open_image_folder', text='Open Folder', icon='FILEBROWSER')
            # layout.operator('stm.prompt_spectrogram_popup', text='Re-bake Texture', icon='FILE_REFRESH', depress=False)


        if stm_obj.stm_spectro.material_type == 'gradient':

            layout.prop(stm_obj, "presets_gradient", text='', icon='OPTIONS')

            mat = stm_obj.data.materials[0]
            cr_node = mat.node_tree.nodes['STM_gradient']
            layout.template_color_ramp(cr_node, "color_ramp", expand=False)


                


        if stm_obj.stm_spectro.material_type == 'custom':
            if stm_obj.active_material:
                layout.prop(stm_obj.stm_spectro, "material_custom", text='')

            else:
                layout.template_ID(stm_obj.stm_spectro, "material_custom", new="material.new",)




class STM_PT_waveform_main_settings(STM_Object_Panel, bpy.types.Panel):
    bl_label = ""
    bl_idname = "STM_PT_waveform_main_settings"
    bl_parent_id = 'STM_PT_waveform_panel'
    # bl_options = {'DEFAULT_CLOSED'}

    @classmethod
    def poll(self, context):
        return poll_draw_waveform_settings(context)

    def draw_header(self, context):

        layout = self.layout
        layout.label(text='Settings', icon='NONE')

    def draw(self, context):
        layout = self.layout
        scn = context.scene
        stm_obj = funcs.get_stm_object(context.object)

        obj = context.object
        

        modifier = obj.modifiers['STM_waveform']


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

        

        col1.label(text='Offset')
        prop_geonode(col2, modifier, 'Offset', label=False)


        col1.separator()
        col2.separator()

        col1.label(text='Thickness')
        prop_geonode(col2, modifier, 'Thickness', label=False)

        

        col1.separator()
        col2.separator()

        col1.label(text='Resample')

        row = col2.row(align=True)
        prop_geonode(row, modifier, 'doResample', label=False)

        ccol = row.column(align=True)
        ccol.enabled = modifier["Input_17"]
        prop_geonode(ccol, modifier, 'Resample Resolution', label=False)

        col1.separator()
        col2.separator()


        

        col1.label(text='Smooth')
        
        row = col2.row(align=True)
        prop_geonode(row, modifier, 'doSmooth', label=False)
        ccol = row.column(align=True)
        ccol.enabled = modifier["Socket_8"]
        prop_geonode(ccol, modifier, 'Smooth Factor', label=False)

        if modifier["Socket_8"]:
            col1.label(text='')
            prop_geonode(ccol, modifier, 'Smooth Level', label_name='Level')

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

class STM_PT_material_waveform(STM_Panel, bpy.types.Panel):
    bl_label = ""
    bl_idname = "STM_PT_material_waveform"
    bl_parent_id = 'STM_PT_waveform_panel'
    # bl_options = {'DEFAULT_CLOSED'}

    @classmethod
    def poll(self, context):
        return poll_draw_waveform_settings(context)

    def draw_header(self, context):
        layout = self.layout
        layout.label(text='Material', icon='MATERIAL')

    def draw(self, context):
        layout = self.layout
        scn = context.scene
        stm_obj = funcs.get_stm_object(context.object)


        # if stm_obj.stm_spectro.stm_items_active_index >= len(stm_obj.stm_spectro.stm_items):
        #     return

        obj = context.object

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



classes = [

    STM_PT_spectrogram_presets_menu,
    STM_MT_spectro_list_menu,
    STM_MT_audio_menu,
    STM_MT_image_menu,

    STM_MT_eq_curve_menu,
    STM_PT_eq_curve_popover,

    STM_PT_add_new_panel,
    # STM_PT_viewport_settings,
    STM_UL_draw_spectro_list,
    STM_UL_draw_items,


    STM_PT_spectrogram_panel,
    STM_PT_waveform_panel,

    
    STM_PT_spectrogram_main_settings,
    STM_PT_spectrogram_geometry_settings,
    STM_PT_modifiers_spectrogram,
    STM_PT_overlays_spectrogram,
    STM_PT_material_spectrogram,
    

    STM_PT_waveform_main_settings,
    STM_PT_material_waveform,   
    

    

]


def register():
    for c in classes:
        bpy.utils.register_class(c)

def unregister():
    for c in classes:
        bpy.utils.unregister_class(c)