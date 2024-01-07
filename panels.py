import bpy
import os
from bpy.types import Panel
from bpy.types import UIList


def prop_geonode(context, gn_modifier, input_name, label_name='', enabled=True, label=True,icon='NONE'):

    input_id = next(i.identifier for i in gn_modifier.node_group.inputs if i.name == input_name)

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


class STM_UL_items(UIList):

    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):

        obj = item

        custom_icon = 'SMOOTHCURVE'

        row = layout.row(align=True)
        row.prop(obj, "name", text="", emboss=False, translate=False, icon='SMOOTHCURVE')
        row.prop(obj, "hide_viewport", text="", emboss=False, translate=False)
        row.prop(obj, "hide_render", text="", emboss=False, translate=False)


    def filter_items(self, context, data, propname):
        """
            Filter only items with at leats one modifer which name starts with 'STM_'
        """

        filtered = []
        ordered = []
        items = getattr(data, propname)


        filtered = [self.bitflag_filter_item] * len(items)

        for i, item in enumerate(items):
            if not item.modifiers:                          # if no modifers
                filtered[i] &= ~self.bitflag_filter_item    # exclude item
            else:
                if any([m.name.startswith('STM_waveform') for m in item.modifiers]):    # if any modifier starts with 'STM_'
                    pass                                                        # pass
                else:                                                           # else
                    filtered[i] &= ~self.bitflag_filter_item                    # exclude item


        return filtered, ordered

    def invoke(self, context, event):
        pass

class STM_PT_spectrogram(Panel):
    bl_label = "Spectrogram"
    bl_idname = "STM_PT_spectrogram"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "STM"

    def draw(self, context):
        layout = self.layout
        scn = context.scene

        audio_ok = False
        audio_filename = ''



        # box = layout.box()
        # box.label(text=audio_filename, icon='FILE_SOUND' if audio_ok else 'ERROR')
        #
        # col = box.column(align=True)
        #
        # row = col.row(align=True)
        # row.scale_y = 1.5
        # row.prop(scn,'audio_file_path',)
        # row.operator('stm.import_audio_file', text='', icon='FILEBROWSER')
        #
        # col = box.column(align=True)
        # col.operator('stm.add_audio_to_scene', icon='IMPORT')
        # col.operator('stm.open_image_folder', icon='FILEBROWSER')

        col = layout.column(align=True)
        row = col.row(align=True)
        row.scale_y = 1.5
        row.operator('stm.import_audio_file', text='Select audio file', icon='FILE_SOUND')
        row.operator('stm.reset_audio_file', text='', icon='PANEL_CLOSE')

        box = col.box()

        if scn.audio_file_path == '':
            info_audio = '[no audio selected]'
        elif not os.path.isfile(scn.audio_file_path):
            info_audio = '[invalid file path]'
        else:
            info_audio = os.path.basename(scn.audio_file_path)
            audio_ok = True

        row = box.row()
        row.label(text=info_audio, icon='INFO' if audio_ok else 'ERROR')
        row.enabled = False




        # row = layout.row()
        #
        # split = row.split(factor=0.3)
        # col_1 = split.column()
        # col_2 = split.column(align=True)
        #
        # col_1.label(text='Audio File :', icon='FILE_SOUND')
        # box = col_2.box()
        # box.label(text=os.path.basename(scn.audio_file_path))
        #
        # layout.separator()


        # col = layout.column()
        # split = col.split(factor=0.4)
        # col_1 = split.column()
        # col_2 = split.column()
        #
        # col_1.label(text='Color Mode :')
        # col_2.prop(scn, 'colorMode', text='')
        #
        # col_1.label(text='Intensity Scale :')
        # col_2.prop(scn, 'scale', text='')
        #
        # col_1.label(text='Freq Scale :')
        # col_2.prop(scn, 'fscale', text='')
        #
        # col_1.label(text='drange :')
        # col_2.prop(scn, 'drange', text='')
        #
        # layout.separator()

        # col = layout.column(align=True)
        #
        # split = col.split(factor=0.5)
        #
        #
        # col_1 = split.column(align=True)
        # col_2 = split.column(align=True)
        #
        #
        #
        # row = col_1.row()
        # row.scale_y = 1.5
        # row.label(text='Audio :', icon='FILE_SOUND')
        # row = col_2.row()
        # row.scale_y = 1.5
        # # row.prop(scn,'audio_file_path',)
        # row.operator('stm.import_audio_file', text='Select Audio', icon='NONE')
        #
        # col_1.separator()
        # col_2.separator()

        # col_1.label(text='Resolution :', icon='TEXTURE')
        # row = col_2.row(align=True)
        # row.scale_y=1.5
        # row.prop_enum(scn, 'resolutionPreset', '1024x512')
        # row.prop_enum(scn, 'resolutionPreset', '2048x1024')
        # row.prop_enum(scn, 'resolutionPreset', '4096x2048')
        # row.prop_enum(scn, 'resolutionPreset', '8192x4096')
        # row.prop_enum(scn, 'resolutionPreset', '16384x8192')
        # row = col_2.row(align=True)
        # row.scale_y=1.5
        # row.prop_enum(scn, 'resolutionPreset', 'custom', text='Custom')





        # col_1.label(text='Resolution :', icon='TEXTURE')
        # row = col_2.row(align=True)
        # row.prop(scn, 'resolutionPreset', text='')
        #
        # if scn.resolutionPreset == 'custom':
        #         #col = box.column(align=True)
        #         ccol = col_2.column(align=True)
        #         ccol.scale_y = 1
        #         ccol.prop(scn, 'userWidth', text='Width')
        #         ccol.prop(scn, 'userHeight', text='Height')




        row = layout.row()
        row.scale_y = 2
        row.operator(
            'stm.generate_spectrogram',
            text='Update Spectrogram' if scn.stm_object is not None else 'Generate Spectrogram',
            icon='FILE_REFRESH' if scn.stm_object is not None else 'IMPORT',
        )
        row.enabled = audio_ok

class STM_PT_stm_objects(Panel):
    bl_label = ""
    bl_idname = "STM_PT_stm_objects"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "STM"
    bl_parent_id = 'STM_PT_spectrogram'

    def draw_header(self, context):
        layout = self.layout
        layout.label(text='Spectrogram Objects', icon='OBJECT_DATA')

    def draw(self, context):

        layout = self.layout
        scn = context.scene

        # box.label(text='Spectrogram Object')

        col = layout.column(align=True)
        row = col.row(align=True)
        row.scale_y = 1.5
        row.prop(scn, 'stm_object', text='')

        if scn.stm_object is not None:
            row.prop(scn.stm_object, 'hide_viewport', text='', emboss=True)
            row.prop(scn.stm_object, 'hide_render', text='',  emboss=True)

            row = col.row(align=True)
            row.operator('stm.select_stm_in_viewport', text='Select spectrogram', icon='RESTRICT_SELECT_OFF')

            stm_objs = []

            obj = context.object
            obj_allowed_types = ["MESH","CURVE","EMPTY"]

            if scn.stm_object.modifiers.get('STM_spectrogram'):

                rows = 5
                row = layout.row(align=True)
                row.template_list("STM_UL_items", "", scn, "objects", scn, "stm_obj_list_index", rows=rows)

                col = row.column(align=True)
                col.operator('stm.add_waveform', text='', icon='ADD')
                col.operator('stm.remove_waveform', text='', icon='REMOVE')
            else:
                box = layout.box()
                box.label(text='-ERROR-', icon='ERROR')

                col = box.column()
                col.label(text='Can\'t find STM_spectrogram modifier')
                col.label(text='on selected object.')
        else:
            row = col.row(align=True)
            row.operator('stm.select_stm_in_viewport', text='Select spectrogram', icon='RESTRICT_SELECT_OFF')
            row.enabled = True if scn.stm_object is not None else False

class STM_PT_geometry_nodes(Panel):
    bl_label = ""
    bl_idname = "STM_PT_geometry_nodes"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "STM"
    bl_parent_id = 'STM_PT_spectrogram'

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

                row = layout.row(align=True)
                row.operator('stm.apply_preset_spectrogram_gn', text='Apply')
                row.prop(scn, 'preset_spectrogram')
                row = layout.row(align=True)
                row.operator('stm.reset_spectrogram_gn', text='Reset All')

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


                box = layout.box()


                box.label(text='Main Settings', icon='OPTIONS')


                col = box.column(align=True)
                prop_geonode(col, obj.modifiers['STM_spectrogram'], 'Freq Min (Hz)')
                prop_geonode(col, obj.modifiers['STM_spectrogram'], 'Freq Max (Hz)')

                col = box.column(align=True)
                prop_geonode(col, obj.modifiers['STM_spectrogram'], 'Audio Sample')

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
                row.label(text='Geometry', icon='MESH_DATA')
                row.operator('stm.reset_gn_geometry_values', text='', icon='FILE_REFRESH')

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
                row.label(text='EQ Curve', icon='NORMALIZE_FCURVES')
                # row.operator('stm.reset_stm_curve', text='Reset', icon='PANEL_CLOSE')



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
    bl_parent_id = 'STM_PT_spectrogram'

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
