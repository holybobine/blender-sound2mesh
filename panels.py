import bpy
import os
from bpy.types import Panel
from bpy.types import UIList
import funcs
from funcs import *


def prop_geonode(context, gn_modifier, input_name, label_name='', enabled=True, label=True, icon='NONE'):

    # input_id = next(i.identifier for i in gn_modifier.node_group.inputs if i.name == input_name)                  # 3.6
    input_id = next(i.identifier for i in gn_modifier.node_group.interface.items_tree if i.name == input_name)      # 4.0

    # print(input_id)

    if input_id:
        row = context.row(align=True)
        if label:
            col = row.column(align=True)
            col.label(text=input_name)
            # col.enabled = False

            row = row.row(align=True)
        row.prop(
            data = gn_modifier,
            text = label_name if label_name != '' else '' if not label else '',
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




        box = layout.box()

        # box.label(text='1. Add STM object :', icon='NONE')

        col = box.column()
        col.scale_y = 1.2
        row = col.row()
        row.label(text='Spectrogram', icon='SEQ_HISTOGRAM')
        row.operator('stm.add_spectrogram', text='New', icon='ADD')

        row = col.row()
        row.label(text='Waveform', icon='RNDCURVE')
        row.operator('stm.add_waveform', text='New', icon='ADD')

        # layout.separator()

        audio_ok = False

        if scn.audio_file_path == '':
            info_audio = '[no audio selected]'
        elif not os.path.isfile(scn.audio_file_path):
            info_audio = '[invalid file path]'
        else:
            info_audio = scn.audio_file_path
            audio_ok = True

        stm_ok = False

        if scn.audio_file_path == '':
            info_operator = '[select audio file]'
        elif not os.path.isfile(scn.audio_file_path):
            info_operator = '[invalid audio file path]'
        elif not funcs.is_stm_object_selected():
            info_operator = '[select spectrogram object]'
        else:
            info_operator = 'Generate'
            stm_ok = True









        box = layout.box()
        row = box.row()
        col1 = row.column()
        col2 = row.column()
        col1.label(text='Audio File :', icon='FILE_SOUND')
        col2.operator('stm.set_sound_in_scene', text='Use in scene', icon='IMPORT')
        col2.enabled = audio_ok


        row = box.row(align=True)
        # row.scale_y = 1.5
        col1 = row.column(align=True)
        col2 = row.column(align=True)
        col2.scale_y = 1.5

        bbox = col1.box()
        row = bbox.row()
        row.label(text=info_audio, icon='NONE')
        row.enabled = False

        row = col2.row(align=True)
        row.operator('stm.import_audio_file', text='', icon='FILEBROWSER')
        row.operator('stm.reset_audio_file', text='', icon='PANEL_CLOSE')
        # bbox = col.box()

        split = box.split(factor=0.2)
        col1 = split.column(align=True)
        col2 = split.column(align=True)
        col1.label(text='Title :')
        col2.label(text=scn.title)
        col1.label(text='Artist :')
        col2.label(text=scn.artist)
        col1.label(text='Album :')
        col2.label(text=scn.album)
        col1.label(text='Duration :')
        col2.label(text=scn.duration_format)
        col1.enabled = False

        if scn.duration_seconds > 1200:
            bbox = box.box()
            row = bbox.row()
            col1=row.column(align=True)
            # col1.scale_y = 2
            col2=row.column(align=True)
            col1.label(text='', icon='ERROR')
            col2.label(text='Long audio file.')
            # col2.label(text='Generation may take a while...')


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


        row = layout.row()
        row.scale_y = 2
        # row.operator('stm.generate_spectrogram', text=info_operator, icon='SHADERFX')

        draw_progress_bar = False

        if obj:
            if obj.progress != 0:
                draw_progress_bar = True

        if draw_progress_bar:
            label = bpy.context.object.progress_label
            row.prop(bpy.context.object,"progress", text=label)
            # row.enabled = False
        else:
            # if scn.duration_seconds > 1200:
            #     row.operator('stm.prompt_audio_warning', text=info_operator, icon='SHADERFX', depress=False)
            # else:
            #     row.operator('stm.prompt_spectrogram_popup', text=info_operator, icon='SHADERFX', depress=False)

            row.operator('stm.prompt_spectrogram_popup', text=info_operator, icon='SHADERFX', depress=False)

            row.enabled = audio_ok and stm_ok






class STM_PT_geometry_nodes(Panel):
    bl_label = ""
    bl_idname = "STM_PT_geometry_nodes"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "STM"
    # bl_parent_id = 'STM_PT_spectrogram'

    @classmethod
    def poll(self, context):
        do_draw = False

        try:
            if context.object in context.selected_objects:
                if any([m.name.startswith('STM_') for m in context.object.modifiers]):
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

        col = layout.column(align=True)

        row = col.row(align=True)
        row.scale_x = 5
        row.scale_y = 1.5

        obj = context.object
        obj_allowed_types = ["MESH","CURVE","EMPTY"]

        layout = layout.box()
        layout.enabled = obj.progress == 0


        if obj and obj.type in obj_allowed_types:
            if any([m.name.startswith('STM_spectrogram') for m in obj.modifiers]):

                gn_node_tree = bpy.data.node_groups['STM_spectrogram']
                exclude_inputs = ['Geometry']




                split = layout.split(factor=0.3)
                split.label(text='Preset :')
                split.template_icon_view(context.scene, "presets_spectrogram", show_labels=True, scale=5.0, scale_popup=6.0)

                box = layout.box()
                box.scale_y = 1.5
                box.operator('stm.reset_spectrogram_full', text='Reset All', icon='FILE_REFRESH')







                box = layout.box()
                row = box.row()
                # row.label(text='Main Settings', icon='OPTIONS')
                row.prop(scn, 'bool_main_settings', text='Main Settings', icon='TRIA_DOWN' if scn.bool_main_settings else 'TRIA_RIGHT', emboss=False)
                row.operator('stm.reset_spectrogram_main_settings', text='', icon='FILE_REFRESH')


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
                # row.label(text='Main Settings', icon='OPTIONS')
                row.prop(scn, 'bool_geometry_settings', text='Geometry', icon='TRIA_DOWN' if scn.bool_geometry_settings else 'TRIA_RIGHT', emboss=False)
                row.operator('stm.reset_spectrogram_geometry_values', text='', icon='FILE_REFRESH')


                if scn.bool_geometry_settings:

                    col = box.column(align=True)
                    row = col.row(align=True)
                    row.scale_y = 2
                    row.prop_enum(obj, 'geometry_type', 'plane', icon='MESH_GRID')
                    row.prop_enum(obj, 'geometry_type', 'cylinder', icon='MESH_CYLINDER')


                    col = box.column(align=True)

                    # prop_geonode(col, obj.modifiers['STM_spectrogram'], 'showGrid')

                    split = col.split(factor=0.495)
                    row1 = split.row(align=True)
                    row2 = split.row(align=True)
                    row1.label(text='Grid')
                    row2.prop_enum(obj, 'showGrid', 'off')
                    row2.prop_enum(obj, 'showGrid', 'on')

                    col.separator()

                    # prop_geonode(col, obj.modifiers['STM_spectrogram'], 'doExtrude')
                    split = col.split(factor=0.495)
                    col1 = split.column(align=True)
                    col2 = split.column(align=True)
                    col1.label(text='Extrude')
                    row = col2.row(align=True)
                    row.prop_enum(obj, 'doExtrude', 'off')
                    row.prop_enum(obj, 'doExtrude', 'on')

                    row1 = col1.row(align=True)
                    row1.label(text='Base Height')
                    row2 = col2.row(align=True)
                    prop_geonode(row2, obj.modifiers['STM_spectrogram'], 'Base Height', label_name='', label=False)
                    row1.enabled = True if obj.doExtrude == 'on' else False
                    row2.enabled = True if obj.doExtrude == 'on' else False








                    col.enabled = True if obj.geometry_type == 'plane' else False

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
                row.operator('stm.reset_stm_curve', text='', icon='FILE_REFRESH')

                if scn.bool_eq_curve_settings:

                    # row = box.row()
                    # row.label(text='EQ Curve', icon='NORMALIZE_FCURVES')

                    split = box.split(factor=0.5)
                    split.label(text='Preset :')
                    split.template_icon_view(context.scene, "presets_eq_curve", show_labels=True, scale=3.0, scale_popup=5.0)

                    prop_geonode(box, obj.modifiers['STM_spectrogram'], 'EQ Curve Factor', label_name='Factor', label=True)

                    bbox = box.box()
                    curve = bpy.data.node_groups['STM_spectrogram'].nodes['MACURVE']
                    bbox.template_curve_mapping(
                        data=curve,
                        property="mapping",
                        levels=False,
                        brush=False,
                        show_tone=False,
                    )










            elif any([m.name.startswith('STM_waveform') for m in obj.modifiers]):

                modifier = obj.modifiers['STM_waveform']


                split_fac = 0.3


                split = layout.split(factor=split_fac)
                split.label(text='Style :')



                gallery_scale = 5.0

                row = split.row(align=True)
                #row.scale_y=5

                col1 = row.column(align=True)
                col2 = row.column(align=True)
                col3 = row.column(align=True)

                col1.scale_y=gallery_scale
                col3.scale_y=gallery_scale


                #row.prop(context.scene, 'preset_thumbnails')
                col1.operator('stm.previous_waveform_style', text='', icon='TRIA_LEFT')
                col2.template_icon_view(context.object, "presets_waveform_style", show_labels=True, scale=gallery_scale, scale_popup=6.0)
                col3.operator('stm.next_waveform_style', text='', icon='TRIA_RIGHT')

                split = layout.split(factor=split_fac)
                split.scale_y = 1.5
                split.label(text='Object')
                prop_geonode(split, modifier, 'Object', label=False)






                col = layout.column(align=True)
                prop_geonode(col, modifier, 'Thickness')
                prop_geonode(col, modifier, 'Offset')

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

                col = layout.column(align=True)
                prop_geonode(col, modifier, 'Smooth')
                prop_geonode(col, modifier, 'Smooth Level')



                col = layout.column()
                prop_geonode(col, modifier, 'Merge Ends')
                prop_geonode(col, modifier, 'Threshold')



class STM_PT_material(Panel):
    bl_label = ""
    bl_idname = "STM_PT_material"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "STM"
    # bl_parent_id = 'STM_PT_spectrogram'

    @classmethod
    def poll(self, context):
        do_draw = False

        try:
            if context.object in context.selected_objects:
                if any([m.name.startswith('STM_') for m in context.object.modifiers]):
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

        layout = layout.box()

        obj = bpy.context.active_object
        obj_type = ''

        if obj.modifiers:
            if any([m.name.startswith('STM_spectrogram') for m in obj.modifiers]):
                obj_type = 'spectrogram'
            elif any([m.name.startswith('STM_waveform') for m in obj.modifiers]):
                obj_type = 'waveform'

        if obj_type == 'spectrogram':

            raw_texture = obj.modifiers['STM_spectrogram']['Input_2']

            layout.enabled = raw_texture != None and  obj.progress == 0

            row = layout.row(align=True)
            row.scale_y = 1.5

            row.prop(context.object, 'material_type', expand=True)


            split_fac = 0.3



            if obj.material_type == 'gradient' or obj.material_type == 'raw':
                split = layout.split(factor=split_fac)
                split.scale_y = 1.5


                split.label(text='Material :')
                prop_geonode(split, obj.modifiers['STM_spectrogram'], 'Material', label=False)

            if obj.material_type == 'raw':


                box = layout.box()
                # box.enabled = False



                split = box.split(factor=split_fac)
                split.scale_y = 1.5
                col1 = split.column()
                col2 = split.column()

                col1.label(text='Image :')

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

                col1.label(text='Folder :')

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


                col1.label(text='Resolution :')

                resolution = f"{raw_texture.size[0]}x{raw_texture.size[1]}px" if raw_texture != None else ''
                col2.label(text=resolution)

                split = box.split(factor=split_fac)
                split.scale_y = 1
                col1 = split.column()
                col2 = split.column()

                col1.label(text='File Size :')
                filesize = convert_size(os.path.getsize(raw_texture.filepath)) if raw_texture != None else ''
                col2.label(text=f'{filesize}')

            if obj.material_type == 'custom':
                split = layout.split(factor=split_fac)
                split.scale_y = 1.5

                split.label(text='Material :')
                split.prop(context.object, 'material_custom', text='')



            if obj.material_type == 'gradient':

                split = layout.split(factor=split_fac)
                split.label(text='Preset :')

                # col1.prop(context.scene, 'gradient_preset', text='')
                split.template_icon_view(context.object, "presets_gradient", show_labels=True, scale=5.0, scale_popup=6.0)


                box = layout.box()
                row = box.row()
                # row.label(text='Main Settings', icon='OPTIONS')
                row.prop(scn, 'bool_custom_gradient', text='Customize Gradient', icon='TRIA_DOWN' if scn.bool_custom_gradient else 'TRIA_RIGHT', emboss=False)
                row.operator('stm.reset_gradient', text='', icon='FILE_REFRESH')
                if scn.bool_custom_gradient:
                    cr_node = bpy.data.materials['STM_gradient'].node_tree.nodes['STM_gradient']
                    box.template_color_ramp(cr_node, "color_ramp", expand=False)



        elif obj_type == 'waveform':

            modifier = obj.modifiers['STM_waveform']

            box = layout.box()
            box.label(text='Waveform mat', icon='RNDCURVE')

            col = layout.column()
            col.scale_y = 1.5
            prop_geonode(col, modifier, 'Material')
