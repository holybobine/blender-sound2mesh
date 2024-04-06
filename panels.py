import bpy
import os
from bpy.types import Panel
from bpy.types import UIList, PropertyGroup
import textwrap
from . import funcs
# from . funcs import *


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



def poll_draw_spectrogram_settings(context, require_image=True):
    if not context.object:
        return
    if context.object.stm_spectro.stm_type != 'spectrogram':
        return
    if require_image:
        if context.object.stm_spectro.image_file == None:
            return

    return True

def poll_draw_waveform_settings(context):
    if not context.object:
        return
    if context.object.stm_spectro.stm_type != 'waveform':
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
                row = layout.row(align=True)
                row.label(text='', icon='DOT')
                row.prop(item, "name", icon=custom_icon, emboss=False, text="")

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
        return bool(poll_draw_spectrogram_settings(context, require_image=False) or poll_draw_waveform_settings(context))

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


        row_audio = layout.row()

        col = row_audio.column(align=True)
        col.enabled = scn.stm_settings.progress == 0
        
        row = col.row(align=True)
        # row.scale_y = 1.5

        if stm_obj.stm_spectro.audio_file == None:
            row.operator('stm.import_audio_file', text='Select Audio', icon='FILE_SOUND')
            
        else:
            ccol1 = row.column(align=True)
            ccol1.enabled = False
            ccol2 = row.column(align=True)

            ccol1.prop(stm_obj.stm_spectro, 'audio_filename', text='', icon='FILE_SOUND')

            row = ccol2.row(align=True)
            row.operator('stm.import_audio_file', text='', icon='FILEBROWSER')
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
        rrow1.enabled = obj.stm_spectro.audio_file != None
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

            if stm_obj.stm_spectro.audio_filename != stm_obj.modifiers['STM_spectrogram']['Input_60']:
                row = rrow2.row(align=True)
                row.alert = True
                row.operator('stm.alert_audio_change', icon='ERROR')
                

            rrow2.operator('stm.prompt_spectrogram_popup', text='', icon='FILE_REFRESH', depress=False)
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

        


        row_audio.menu('STM_MT_audio_menu', text='', icon='DOWNARROW_HLT')
        row_image.menu('STM_MT_image_menu', text='', icon='DOWNARROW_HLT')


class STM_PT_geometry_nodes_spectrogram(STM_Panel, bpy.types.Panel):
    bl_label = ""
    bl_idname = "STM_PT_geometry_nodes_spectrogram"
    bl_parent_id = 'STM_PT_spectrogram_settings'

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

        row = layout.row(align=True)
        prop_geonode(row, obj.modifiers['STM_spectrogram'], 'doCylinder', icon='MESH_GRID', label_name='Plane', toggle=1, invert_checkbox=True)
        prop_geonode(row, obj.modifiers['STM_spectrogram'], 'doCylinder', icon='MESH_CYLINDER', label_name='Cylinder', toggle=1)

        split = layout.split(factor=split_fac)
        col1 = split.column(align=True)
        col1.alignment = 'RIGHT'
        col2 = split.column(align=True)

        


        col1.label(text='Show Title')

        row = col2.row(align=True)
        prop_geonode(row, obj.modifiers['STM_spectrogram'], 'showTitle', label=False)

        ccol = row.column(align=True)
        ccol.enabled = context.object.modifiers["STM_spectrogram"]["Socket_16"]
        prop_geonode(ccol, obj.modifiers['STM_spectrogram'], 'Audio Filename', label=False)

        col1.separator()
        col2.separator()

        col1.label(text='Show Grid')

        row = col2.row(align=True)
        prop_geonode(row, obj.modifiers['STM_spectrogram'], 'showGridFull', label=False)
        
        row = row.row(align=True)
        row.enabled = context.object.modifiers["STM_spectrogram"]["Socket_18"]
        prop_geonode(row, obj.modifiers['STM_spectrogram'], 'showGridX', label_name='X', toggle=1)
        prop_geonode(row, obj.modifiers['STM_spectrogram'], 'showGridY', label_name='Y', toggle=1)
        prop_geonode(row, obj.modifiers['STM_spectrogram'], 'showGridZ', label_name='Z', toggle=1)

        # col1.separator()
        # col2.separator()  

        # col1.label(text='Preset')

        # row = col2.row(align=True)
        # row.prop(obj, "presets_geonodes", text='')

        layout.prop(obj, "presets_geonodes", text='', icon='OPTIONS')

        
        
        

        box = layout.box()
        row = box.row()
        row.prop(scn.stm_settings, 'bool_main_settings', text='Audio Settings', icon='TRIA_DOWN' if scn.stm_settings.bool_main_settings else 'TRIA_RIGHT', emboss=False)
        row.operator('stm.reset_spectrogram_main_settings', text='', icon='LOOP_BACK')


        

        if scn.stm_settings.bool_main_settings:


            split = box.split(factor=split_fac)
            col1 = split.column(align=True)
            col1.alignment = 'RIGHT'
            col2 = split.column(align=True)

            
            
            
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

            col1.label(text='EQ Curve')

            row = col2.row(align=True)
            prop_geonode(row, obj.modifiers['STM_spectrogram'], 'doEQCurve', label=False)

            ccol = row.column(align=True)
            ccol.enabled = context.object.modifiers["STM_spectrogram"]["Socket_19"]
            prop_geonode(ccol, obj.modifiers['STM_spectrogram'], 'EQ Curve Factor', label=False)
            ccol.prop(obj, "presets_eq_curve", text='')

        

        box = layout.box()
        row = box.row()
        row.prop(scn.stm_settings, 'bool_geometry_settings', text='Geometry Settings', icon='TRIA_DOWN' if scn.stm_settings.bool_geometry_settings else 'TRIA_RIGHT', emboss=False)
        row.operator('stm.reset_spectrogram_geometry_values', text='', icon='LOOP_BACK')


        if scn.stm_settings.bool_geometry_settings:

            split = box.split(factor=split_fac)
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
            
            prop_geonode(row, obj.modifiers['STM_spectrogram'], 'flipCylinderX', label_name='X', toggle=1)
            prop_geonode(row, obj.modifiers['STM_spectrogram'], 'flipCylinderY', label_name='Y', toggle=1)
            prop_geonode(row, obj.modifiers['STM_spectrogram'], 'flipCylinderOutside', label_name='Z', toggle=1)

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
                prop_geonode(ccol, obj.modifiers['STM_spectrogram'], 'Base Height', label=False)


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

        box = layout.box()
        row = box.row(align=True)
        row.prop(scn.stm_settings, 'bool_curve_deform', text='Curve Deform', icon='TRIA_DOWN' if scn.stm_settings.bool_curve_deform else 'TRIA_RIGHT', emboss=False)
        row.operator('stm.reset_spectrogram_geometry_values', text='', icon='LOOP_BACK')


        if scn.stm_settings.bool_curve_deform:

            split = box.split(factor=split_fac)
            col1 = split.column(align=True)
            col1.alignment = 'RIGHT'
            col2 = split.column(align=True)

            col1.label(text='Curve Object')

            row = col2.row(align=True)
            prop_geonode(row, obj.modifiers['STM_spectrogram'], 'doCurve', label=False)

            ccol = row.column(align=True)
            ccol.enabled = context.object.modifiers["STM_spectrogram"]["Socket_17"]
            ccol.prop(obj.stm_spectro, 'curve_object', text='')

            col1.separator()
            col2.separator()

            row = col1.row(align=True)
            row.alignment = 'RIGHT'
            row.enabled = not obj.modifiers['STM_spectrogram']['Socket_15']
            row.label(text='Deform Axis')

            row = col2.row(align=True)
            
            ccol = row.column(align=True)
            ccol.enabled = context.object.modifiers["STM_spectrogram"]["Socket_17"] and not obj.modifiers['STM_spectrogram']['Socket_15']
            ccol.prop(obj.stm_spectro, 'curve_deform_axis', text='')       



class STM_PT_material_spectrogram(STM_Panel, bpy.types.Panel):
    bl_label = ""
    bl_idname = "STM_PT_material_spectrogram"
    bl_parent_id = 'STM_PT_spectrogram_settings'

    @classmethod
    def poll(self, context):
        return poll_draw_spectrogram_settings(context)

    def draw_header(self, context):
        layout = self.layout
        layout.label(text='Material', icon='MATERIAL')

    def draw(self, context):
        layout = self.layout
        scn = context.scene

        obj = context.object
        stm_obj = funcs.get_stm_object(context)
        obj_type = ''

        raw_texture = obj.modifiers['STM_spectrogram']['Input_2']

        layout.enabled = raw_texture != None and  scn.stm_settings.progress == 0

        row = layout.row(align=True)
        # row.scale_y = 1.5

        row.prop(obj.stm_spectro, 'material_type', expand=True)


        split_fac = 0.3



        # if obj.stm_spectro.material_type == 'gradient' or obj.stm_spectro.material_type == 'raw':
        #     row = layout.row()
        #     row.scale_y = 1.5
        #     row.enabled = False
        #     prop_geonode(row, obj.modifiers['STM_spectrogram'], 'Material', label=False)

        # if obj.stm_spectro.material_type == 'raw':

        #     box = layout.box()

        #     split = box.split(factor=split_fac)
        #     split.scale_y = 1.5
        #     col1 = split.column()
        #     col2 = split.column()

        #     col1.label(text='Image')

        #     row = col2.row(align=True)
        #     ccol1 = row.column(align=True)
        #     ccol2 = row.column(align=True)

        #     row = ccol1.row(align=True)
        #     row.enabled = False
        #     prop_geonode(row, obj.modifiers['STM_spectrogram'], 'Image', label=False)

        #     row = ccol2.row(align=True)
        #     row.operator('stm.open_image', text='Open', icon='FILE_IMAGE')
        #     row.enabled = raw_texture != None



        #     split = box.split(factor=split_fac)
        #     split.scale_y = 1
        #     col1 = split.column()
        #     col2 = split.column()

        #     col1.label(text='Folder')

        #     row = col2.row(align=True)
        #     ccol1 = row.column(align=True)
        #     ccol2 = row.column(align=True)
        #     ccol2.scale_y = 1.5

        #     if raw_texture != None:
        #         filepath = os.path.dirname(raw_texture.filepath)
        #     else:
        #         filepath = ''

        #     row = ccol1.row(align=True)
        #     row.enabled = False
        #     bbox = row.box()
        #     bbox.label(text=f'{filepath}')

        #     row = ccol2.row(align=True)
        #     row.operator('stm.open_image_folder', text='Open', icon='FILEBROWSER')
        #     row.enabled = raw_texture != None

        #     split = box.split(factor=split_fac)
        #     split.scale_y = 1
        #     col1 = split.column()
        #     col2 = split.column()


        #     col1.label(text='Resolution')

        #     resolution = f"{raw_texture.size[0]}x{raw_texture.size[1]}px" if raw_texture != None else ''
        #     col2.label(text=resolution)

        #     split = box.split(factor=split_fac)
        #     split.scale_y = 1
        #     col1 = split.column()
        #     col2 = split.column()

        #     col1.label(text='File Size')
        #     filesize = funcs.convert_size(os.path.getsize(raw_texture.filepath)) if raw_texture != None else ''
        #     col2.label(text=f'{filesize}')


        if obj.stm_spectro.material_type == 'raw':

            box = layout.box()

            col = box.column()

            # row = layout.row()
            # row.emboss = 'NORMAL'
            col.template_icon_view(stm_obj, "preview_image_enum", show_labels=True, scale=6.0, scale_popup=17.0)

            row = col.row()
            row.enabled = False
            rowL = row.row()
            rowL.alignment = 'LEFT'
            rowR = row.row()
            rowR.alignment = 'RIGHT'
            
            rowL.label(text=f"{stm_obj.stm_spectro.image_file.size[0]}x{stm_obj.stm_spectro.image_file.size[1]}")
            rowR.label(text=funcs.convert_size(os.path.getsize(stm_obj.stm_spectro.image_file.filepath)))

        if obj.stm_spectro.material_type == 'custom':
            row = layout.row()
            row.scale_y = 1.5
            row.prop(obj.stm_spectro, 'material_custom', text='')



        if obj.stm_spectro.material_type == 'gradient':
            


            box = layout.box()
            # col = layout.column(align=True)
            
            row = box.row(align=True)
            row.scale_x = 10

            for item in stm_obj.bl_rna.properties['presets_gradient'].enum_items:
                row.prop_enum(stm_obj, 'presets_gradient', item.identifier, text='')

            # row.prop(stm_obj, 'presets_gradient', expand=True, icon_only=True)

            mat = context.object.data.materials[0]
            cr_node = mat.node_tree.nodes['STM_gradient']
            box.template_color_ramp(cr_node, "color_ramp", expand=True)



class STM_PT_waveform_settings(STM_Panel, bpy.types.Panel):
    bl_label = ""
    bl_idname = "STM_PT_waveform_settings"
    bl_parent_id = 'STM_PT_spectrogram_settings'

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



class STM_PT_geometry_nodes_waveform(STM_Panel, bpy.types.Panel):
    bl_label = ""
    bl_idname = "STM_PT_geometry_nodes_waveform"
    bl_parent_id = 'STM_PT_spectrogram_settings'

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

        row = layout.row(align=True)
        row.prop_enum(obj, "presets_waveform_style", '1-line.png')
        row.prop_enum(obj, "presets_waveform_style", '2-dots.png')
        row.prop_enum(obj, "presets_waveform_style", '3-bars.png')

        split_fac = 0.4

        split = layout.split(factor=split_fac)
        col1 = split.column(align=True)
        col1.alignment = 'RIGHT'
        col2 = split.column(align=True)


        

        # col1.label(text='Spectrogram Object')

        
        # row = col2.row(align=True)
        # prop_geonode(row, modifier, 'Object', label=False)

        # col1.separator()
        # col2.separator()

        # col1.label(text='Follow Spectrogram')
        # prop_geonode(col2, obj.modifiers['STM_waveform'], 'Follow Spectrogram', label=False)

        # col1.separator()
        # col2.separator()

        col1.label(text='Offset')
        prop_geonode(col2, obj.modifiers['STM_waveform'], 'Offset', label=False)

        col1.separator()
        col2.separator()

        col1.label(text='Thickness')
        prop_geonode(col2, obj.modifiers['STM_waveform'], 'Thickness', label=False)

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

       

class STM_PT_material_waveform(STM_Panel, bpy.types.Panel):
    bl_label = ""
    bl_idname = "STM_PT_material_waveform"
    bl_parent_id = 'STM_PT_spectrogram_settings'

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


        box = layout.box()

        box.template_color_picker(modifier, '["Socket_3"]')

        prop_geonode(box, modifier, 'emission_strength', label_name='Emission')
        



classes = [
    STM_PT_spectrogram,
    STM_UL_draw_items,
    STM_PT_spectrogram_settings,
    STM_PT_material_spectrogram,
    STM_PT_geometry_nodes_spectrogram,

    STM_PT_material_waveform,
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