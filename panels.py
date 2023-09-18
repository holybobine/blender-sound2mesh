import bpy
import os
from bpy.types import Panel
from bpy.types import UIList


def prop_geonode(context, gn_modifier, input_name, enabled=True, label=True,icon='NONE'):

    input_id = next(i.identifier for i in gn_modifier.node_group.inputs if i.name == input_name)

    row = context.row(align=True)
    if label:
        col = row.column(align=True)
        col.label(text=input_name)
        col.enabled = False

        row = row.row(align=True)
    row.prop(
        data = gn_modifier,
        text = input_name if not label else '',
        property = '["%s"]'%input_id,
        icon = icon,
        emboss = True
    )

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

        if scn.audio_file_path == '':
            audio_filename = '[no audio selected]'
        elif not os.path.isfile(scn.audio_file_path):
            audio_filename = '[invalid file path]'
        else:
            audio_filename = os.path.basename(scn.audio_file_path)
            audio_ok = True

        box = layout.box()
        box.label(text=audio_filename, icon='FILE_SOUND' if audio_ok else 'ERROR')

        col = box.column(align=True)

        row = col.row(align=True)
        row.scale_y = 1.5
        row.prop(scn,'audio_file_path',)
        row.operator('stm.import_audio_file', text='', icon='FILEBROWSER')

        # col = box.column(align=True)
        # col.operator('stm.add_audio_to_scene', icon='IMPORT')
        # col.operator('stm.open_image_folder', icon='FILEBROWSER')


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
                row.operator('stm.reset_spectrogram_gn')

                box = layout.box()
                row = box.row(align=True)
                row.prop(scn, 'stm_show_file_data', text='File Data', icon='FILEBROWSER', emboss=False)
                row.prop(scn, 'stm_show_file_data', text='', icon='TRIA_DOWN' if scn.stm_show_file_data else 'TRIA_LEFT', emboss=False)


                if scn.stm_show_file_data:
                    col = box.column(align=True)
                    prop_geonode(col, obj.modifiers['STM_spectrogram'], 'Audio Filename', enabled=False)
                    prop_geonode(col, obj.modifiers['STM_spectrogram'], 'Image')
                    prop_geonode(col, obj.modifiers['STM_spectrogram'], 'Material')
                    prop_geonode(col, obj.modifiers['STM_spectrogram'], 'Audio Duration', enabled=False)





                box = layout.box()
                row = box.row(align=True)
                row.prop(scn, 'stm_show_main_settings', text='Main Settings', icon='OPTIONS', emboss=False)
                row.prop(scn, 'stm_show_main_settings', text='', icon='TRIA_DOWN' if scn.stm_show_main_settings else 'TRIA_LEFT', emboss=False)

                if scn.stm_show_main_settings:
                    col = box.column(align=True)
                    prop_geonode(col, obj.modifiers['STM_spectrogram'], 'Freq Min (Hz)')
                    prop_geonode(col, obj.modifiers['STM_spectrogram'], 'Freq Max (Hz)')

                    col = box.column(align=True)
                    prop_geonode(col, obj.modifiers['STM_spectrogram'], 'Audio Sample (s)')




                box = layout.box()
                row = box.row(align=True)
                row.prop(scn, 'stm_show_audio_settings', text='Audio Settings', icon='FILE_SOUND', emboss=False)
                row.prop(scn, 'stm_show_audio_settings', text='', icon='TRIA_DOWN' if scn.stm_show_audio_settings else 'TRIA_LEFT', emboss=False)


                if scn.stm_show_audio_settings:
                    col = box.column(align=True)
                    col.scale_y = 1.5
                    prop_geonode(col, obj.modifiers['STM_spectrogram'], 'Gain')

                    col = box.column(align=True)

                    prop_geonode(col, obj.modifiers['STM_spectrogram'], 'Main')
                    prop_geonode(col, obj.modifiers['STM_spectrogram'], 'Peaks')
                    prop_geonode(col, obj.modifiers['STM_spectrogram'], 'Lows')



                box = layout.box()
                row = box.row(align=True)
                row.prop(scn, 'stm_show_curve_settings', text='Custom Curve', icon='RNDCURVE', emboss=False)
                row.prop(scn, 'stm_show_curve_settings', text='', icon='TRIA_DOWN' if scn.stm_show_curve_settings else 'TRIA_LEFT', emboss=False)


                if scn.stm_show_curve_settings:
                    col = box.column(align=True)

                    curve = bpy.data.node_groups['STM_spectrogram'].nodes['MACURVE']
                    col.template_curve_mapping(curve, "mapping")

                    box.operator('stm.reset_stm_curve', icon='CANCEL')

                box = layout.box()
                row = box.row(align=True)
                row.prop(scn, 'stm_show_geometry_settings', text='Geometry', icon='MESH_DATA', emboss=False)
                row.prop(scn, 'stm_show_geometry_settings', text='', icon='TRIA_DOWN' if scn.stm_show_geometry_settings else 'TRIA_LEFT', emboss=False)

                if scn.stm_show_geometry_settings:
                    col = box.column(align=True)
                    prop_geonode(col, obj.modifiers['STM_spectrogram'], 'Resolution X', label=True)
                    prop_geonode(col, obj.modifiers['STM_spectrogram'], 'Resolution Y')

                    col = box.column(align=True)
                    prop_geonode(col, obj.modifiers['STM_spectrogram'], 'Smooth')
                    prop_geonode(col, obj.modifiers['STM_spectrogram'], 'Smooth Level')

                    col = box.column(align=True)
                    prop_geonode(col, obj.modifiers['STM_spectrogram'], 'Noise')
                    prop_geonode(col, obj.modifiers['STM_spectrogram'], 'Noise Scale')


            elif any([m.name.startswith('STM_waveform') for m in obj.modifiers]):

                col = layout.column()

                modifier = obj.modifiers['STM_waveform']

                prop_geonode(col, modifier, 'Style')

                col = layout.column()
                prop_geonode(col, modifier, 'Thickness')
                prop_geonode(col, modifier, 'Offset')


        layout.operator('stm.hello')

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

        elif obj_type == 'waveform':
            box = layout.box()
            box.label(text='Waveform mat', icon='RNDCURVE')
