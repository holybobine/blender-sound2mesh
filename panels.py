import bpy
import os
from bpy.types import Panel
from bpy.types import UIList
import funcs
from funcs import *


def prop_geonode(context, gn_modifier, input_name, label_name='', enabled=True, label=True,icon='NONE'):

    # input_id = next(i.identifier for i in gn_modifier.node_group.inputs if i.name == input_name)                  # 3.6
    input_id = next(i.identifier for i in gn_modifier.node_group.interface.items_tree if i.name == input_name)      # 4.0

    # print(input_id)

    if input_id:
        row = context.row(align=True)
        if label:
            col = row.column(align=True)
            col.label(text=input_name)
            col.enabled = False

            row = row.row(align=True)
        row.prop(
            data = gn_modifier,
            text = label_name if label_name != '' else input_name if not label else '',
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

        box = layout.box()
        col = box.column()
        col.scale_y = 1.2
        row = col.row()
        row.label(text='Spectrogram', icon='SEQ_HISTOGRAM')
        row.operator('stm.add_spectrogram', text='New', icon='ADD')

        row = col.row()
        row.label(text='Waveform', icon='RNDCURVE')
        row.operator('stm.add_waveform', text='New', icon='ADD')

        layout.separator()

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
        box.label(text='Audio file :', icon='FILE_SOUND')

        row = box.row(align=True)
        # row.scale_y = 1.5
        col1 = row.column(align=True)
        col2 = row.column(align=True)
        col2.scale_y = 1.5

        bbox = col1.box()
        row = bbox.row()
        row.label(text=info_audio)
        row.enabled = False

        row = col2.row(align=True)
        row.operator('stm.import_audio_file', text='', icon='FILEBROWSER')
        row.operator('stm.reset_audio_file', text='', icon='PANEL_CLOSE')

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


        row = layout.row()
        row.scale_y = 2
        row.operator('stm.generate_spectrogram', text=info_operator, icon='SHADERFX')
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
            obj = bpy.context.active_object

            if obj.modifiers:
                if any([m.name.startswith('STM_') for m in obj.modifiers]):
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

        if obj and obj.type in obj_allowed_types:
            if any([m.name.startswith('STM_spectrogram') for m in obj.modifiers]):

                gn_node_tree = bpy.data.node_groups['STM_spectrogram']
                exclude_inputs = ['Geometry']

                # row = layout.row(align=True)
                # row.operator('stm.apply_preset_spectrogram_gn', text='Apply')
                # row.prop(scn, 'preset_spectrogram')
                # row = layout.row(align=True)
                # row.operator('stm.reset_spectrogram_gn', text='Reset All')

                # box = layout.box()
                # row = box.row(align=True)
                # row.prop(scn, 'stm_show_file_data', text='File Data', icon='FILEBROWSER', emboss=False)
                # row.prop(scn, 'stm_show_file_data', text='', icon='TRIA_DOWN' if scn.stm_show_file_data else 'TRIA_LEFT', emboss=False)
                #
                #
                # if scn.stm_show_file_data:
                #     col = box.column(align=True)
                #     prop_geonode(col, obj.modifiers['STM_spectrogram'], 'Audio Filename', enabled=False)
                #     prop_geonode(col, obj.modifiers['STM_spectrogram'], 'Image')
                #     prop_geonode(col, obj.modifiers['STM_spectrogram'], 'Material')
                #     prop_geonode(col, obj.modifiers['STM_spectrogram'], 'Audio Duration', enabled=False)




                col = layout.column(align=True)
                col.scale_y=1.5
                row = col.row(align=True)
                #row.scale_y=5

                col1 = row.column(align=True)
                col2 = row.column(align=True)
                col3 = row.column(align=True)

                col1.scale_y=6
                col3.scale_y=6


                #row.prop(context.scene, 'preset_thumbnails')
                col1.operator('preset.prev', text='', icon='TRIA_LEFT')
                col2.template_icon_view(context.scene, "preset_thumbnails", show_labels=True, scale_popup=8.0)
                col3.operator('preset.next', text='', icon='TRIA_RIGHT')

                row = col.row(align=True)
                row.operator('stm.apply_preset_spectrogram_gn', text='Apply Preset', icon='IMPORT')
                row.operator('stm.reset_spectrogram_gn', text='Reset All', icon='FILE_REFRESH')


                box = layout.box()
                row = box.row()
                # row.label(text='Main Settings', icon='OPTIONS')
                row.prop(scn, 'bool_main_settings', text='Main Settings', icon='TRIA_DOWN' if scn.bool_main_settings else 'TRIA_RIGHT', emboss=False)

                if scn.bool_main_settings:

                    col = box.column(align=True)
                    prop_geonode(col, obj.modifiers['STM_spectrogram'], 'Freq Min (Hz)')
                    prop_geonode(col, obj.modifiers['STM_spectrogram'], 'Freq Max (Hz)')

                    col = box.column(align=True)
                    prop_geonode(col, obj.modifiers['STM_spectrogram'], 'Audio Sample (s)')

                    col = box.column(align=True)
                    prop_geonode(col, obj.modifiers['STM_spectrogram'], 'Gain')
                    #
                    # col = box.column(align=True)
                    # prop_geonode(col, obj.modifiers['STM_spectrogram'], 'Intensity Lin / Log')

                    col = box.column(align=True)
                    prop_geonode(col, obj.modifiers['STM_spectrogram'], 'Clip Lows')
                    prop_geonode(col, obj.modifiers['STM_spectrogram'], 'Clip Highs')

                box = layout.box()
                row = box.row()
                # row.label(text='Main Settings', icon='OPTIONS')
                row.prop(scn, 'bool_geometry_settings', text='Geometry', icon='TRIA_DOWN' if scn.bool_geometry_settings else 'TRIA_RIGHT', emboss=False)
                row.operator('stm.reset_gn_geometry_values', text='', icon='FILE_REFRESH')


                if scn.bool_geometry_settings:

                    col = box.column(align=True)
                    prop_geonode(col, obj.modifiers['STM_spectrogram'], 'Size X')
                    prop_geonode(col, obj.modifiers['STM_spectrogram'], 'Size Y')

                    col = box.column(align=True)
                    prop_geonode(col, obj.modifiers['STM_spectrogram'], 'Resolution X')
                    prop_geonode(col, obj.modifiers['STM_spectrogram'], 'Resolution Y')



                    col = box.column(align=True)
                    prop_geonode(col, obj.modifiers['STM_spectrogram'], 'Base Height')
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
                # row.label(text='Main Settings', icon='OPTIONS')
                row.prop(scn, 'bool_eqcurve_settings', text='EQ Curve', icon='TRIA_DOWN' if scn.bool_eqcurve_settings else 'TRIA_RIGHT', emboss=False)
                row.operator('stm.reset_stm_curve', text='', icon='FILE_REFRESH')

                if scn.bool_eqcurve_settings:

                    # row = box.row()
                    # row.label(text='EQ Curve', icon='NORMALIZE_FCURVES')


                    col = box.column(align=True)
                    curve = bpy.data.node_groups['STM_spectrogram'].nodes['MACURVE']
                    col.template_curve_mapping(
                        data=curve,
                        property="mapping",
                        levels=False,
                        brush=False,
                        show_tone=False,
                    )

                    col = box.column(align=True)

                    eq_preset = ['reset_5', 'reset_10', 'flatten_edges', 'lowpass', 'highpass']

                    for p in eq_preset:
                        row = col.row()
                        op = row.operator('stm.reset_stm_curve', text=p)
                        op.eq_curve_preset = p



                box = layout.box()
                row = box.row()
                # row.label(text='Main Settings', icon='OPTIONS')
                row.prop(scn, 'bool_material_settings', text='Material', icon='TRIA_DOWN' if scn.bool_material_settings else 'TRIA_RIGHT', emboss=False)

                if scn.bool_material_settings:

                    row = box.row()
                    row.prop(context.object, 'material_type', expand=True)
                    row.scale_y = 1.5



                    if context.object.material_type == 'gradient':
                        bbox = box.box()
                        row = bbox.row()

                        split = row.split(factor=0.25)
                        col_1 = split.column()
                        col_2 = split.column()


                        col_1.label(text='Preset :')
                        col_2.prop(context.scene, 'gradient_preset', text='')

                        cr_node = bpy.data.materials['STM_rawTexture'].node_tree.nodes['STM_gradient']
                        bbox.template_color_ramp(cr_node, "color_ramp", expand=False)

                        row = box.row()
                        row.operator('stm.reset_gradient', text='Reset Gradient', icon='FILE_REFRESH')



                    else:
                        # box.label(text='Custom Material :')
                        row = box.row()
                        row.scale_y = 1.5
                        row.prop(context.object, 'material_custom', text='')

                        box.separator()
                        box.separator()
                        box.separator()
                        box.separator()
                        box.separator()
                        box.separator()
                        box.separator()
                        box.separator()
                        box.separator()
                        box.separator()
                        box.separator()








            elif any([m.name.startswith('STM_waveform') for m in obj.modifiers]):

                col = layout.column()

                modifier = obj.modifiers['STM_waveform']

                prop_geonode(col, modifier, 'Style')

                col = layout.column()
                prop_geonode(col, modifier, 'Thickness')
                prop_geonode(col, modifier, 'Offset')

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
            obj = bpy.context.active_object

            if obj.modifiers:
                if any([m.name.startswith('STM_') for m in obj.modifiers]):
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

        obj = bpy.context.active_object
        obj_type = ''

        if obj.modifiers:
            if any([m.name.startswith('STM_spectrogram') for m in obj.modifiers]):
                obj_type = 'spectrogram'
            elif any([m.name.startswith('STM_waveform') for m in obj.modifiers]):
                obj_type = 'waveform'

        if obj_type == 'spectrogram':
            box = layout.box()
            box.label(text='Spectrogram mat', icon='SEQ_HISTOGRAM')

            box = layout.box()


            # col = box.column(align=True)
            #
            # row = col.row(align=True)
            # row.scale_y = 1.5
            # row.prop_enum(context.object, 'userStyle', 'rawTexture', text='Raw Texture', icon='OUTLINER_OB_IMAGE')
            # row.prop_enum(context.object, 'userStyle', 'custom', text='Custom', icon='SOLO_ON')
            #
            # matBox = col.box()
            #
            # row = matBox.row(align=True)
            #
            # split = row.split(factor=0.3)
            # col_1 = split.column()
            # col_2 = split.column()
            #
            # col_1.label(text='Material : ')
            #
            # if context.object.userStyle == 'custom':
            #     col_2.prop(obj, 'pointerCustomMaterial', text='')
            # else:
            #     col_2.prop(obj, 'pointerCustomMaterialDummy', text='')
            #
            # matBox.enabled = True if context.object.userStyle == 'custom' else False


            row = box.row()

            split = row.split(factor=0.25)
            col_1 = split.column()
            col_2 = split.column()


            col_1.label(text='Preset :')
            col_2.prop(context.scene, 'gradientPreset', text='')

            cr_node = bpy.data.materials['STM_rawTexture'].node_tree.nodes['STM_gradient']
            box.template_color_ramp(cr_node, "color_ramp", expand=False)

            row = box.row()
            row.operator('stm.reset_gradient', text='Reset Gradient', icon='FILE_REFRESH')



        elif obj_type == 'waveform':
            box = layout.box()
            box.label(text='Waveform mat', icon='RNDCURVE')
