import bpy
import os
import subprocess
import math
import json
import time
import datetime
import textwrap

_start_time = time.time()

def start_time():
    global _start_time
    _start_time = time.time()
    print(f'{_start_time = }')

def end_time():
    endtime = seconds_to_timestring(time.time() - _start_time)
    return endtime

def alert(text = "", title = "Message Box", icon = 'INFO'):

    def draw(self, context):
        self.layout.label(text=text)

    bpy.context.window_manager.popup_menu(draw, title = title, icon = icon)

def _label_multiline(context, text, parent, icon='NONE'):
    chars = int(context.region.width / 6)   # 7 pix on 1 character
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



def sanitize_filename(input_str):
    
    allowed = "_- '"                             # build filter
    getVals = list([
                val for val in input_str if
                val.isalpha() or 
                val.isnumeric() or 
                val in allowed
            ])
            
    result = "".join(getVals)                   # apply filter
    
    return result


def sanitize_input(input_str):
    
    if '.' in input_str:                        # remove extension
        ext = input_str.split('.')[-1]
        input_str = input_str[:-len(ext)]
    
    allowed = "_- "                             # build filter
    getVals = list([
                val for val in input_str if
                val.isalpha() or 
                val.isnumeric() or 
                val in allowed
            ])
            
    result = "".join(getVals)                   # apply filter
    
    result = result.replace(" ", "_")           # replace whitespace with "_"
    
    return result

def timestring_to_seconds(timestring):
    from datetime import datetime
    pt = datetime.strptime(timestring,'%H:%M:%S.%f')
    total_seconds = pt.microsecond/1000000 + pt.second + pt.minute*60 + pt.hour*3600

    return total_seconds

def seconds_to_timestring(seconds):
    if seconds is not None:

        s = seconds % 3600 % 60

        seconds = int(seconds)
        d = seconds // (3600 * 24)
        h = seconds // 3600 % 24
        m = seconds % 3600 // 60

        if d > 0:
            return '{:02d}D {:02d}H {:02d}m {:02d}s'.format(d, h, m, int(s))
        elif h > 0:
            return '{:02d}H {:02d}m {:02d}s'.format(h, m, int(s))
        elif m > 0:
            return '{:02d}m {:02d}s'.format(m, int(s))
        elif s > 0:
            return '{:.2f}s'.format(s)
    return

def refresh_all_areas():
    for wm in bpy.data.window_managers:
        for w in wm.windows:
            for area in w.screen.areas:
                area.tag_redraw()

def redraw_all_viewports():
    for area in bpy.context.screen.areas:
        if area.type == 'VIEW_3D':
            area.tag_redraw()

def get_stm_object(object):
    if object.stm_spectro.stm_type == 'waveform':
        if object.stm_spectro.spectrogram_object != None:
            return object.stm_spectro.spectrogram_object
        
    return object


def apply_spectrogram_preset(preset_name):
    print('-INF- apply GN preset')


    with open(r'%s'%bpy.context.scene.stm_settings.presets_json_file,'r') as f:
        presets=json.load(f)

    #     if context.object.modifiers["STM_spectrogram"]["Socket_15"] == True:
    #         p = bpy.context.scene.presets_geonodes_cylinder.replace('.png', '')
    #         p = p.split('-')[1]
    #     else:
    #         p = bpy.context.scene.presets_geonodes.replace('.png', '')
    #         p = p.split('-')[1]


    preset = presets[preset_name]["preset"]


    stm_obj = bpy.context.active_object
    stm_name = bpy.context.active_object.name

    stm_modifier = stm_obj.modifiers['STM_spectrogram']

    exclude_inputs = [
        'Geometry',
        'Audio Duration',
        'Log to Lin',
        'Audio Filename',
        'Baked Volume',
        'Image',
        'Material',
        'max_volume_dB',
        'max_intensity',
        'geometryType',
        'flipCylinderOutside',
        'flipCylinderX',
        'flipCylinderY',
    ]

    stm_modifier.show_viewport = False

    for i in stm_modifier.node_group.interface.items_tree:
        if i.name in preset:
            value = preset[i.name]

            if value == 'reset':
                set_geonode_value(stm_modifier, i, i.default_value)
            else:
                set_geonode_value(stm_modifier, i, value)

        # if i.name == 'EQCurve_type' and 'EQCurve_type' in preset.keys():
        #     value = preset['EQCurve_type']
        #     curve_presets = stm_obj.bl_rna.properties['presets_eq_curve']
        #     preset_name = curve_presets.enum_items[value-1].identifier
        #     stm_obj.presets_eq_curve = preset_name
        #     apply_eq_curve_preset(self, context)
    


    
    stm_modifier.show_viewport = True


exclude_preset_inputs = [
            'Geometry',
            '---------------------',
            'Image',
            'Material',
            'showTitle',
            'Title',
            'showGridFull',
            'showGridX',
            'showGridY',
            'showGridZ', 
            'Resolution X',
            'Resolution Y',
            'flip_X',            
            'flip_Y',            
            'flip_Z',
            'doExtrude',
            'extrudeHeight',
            'doCylinder',
            'Cylinder Radius',
            'Clip Lows',
            'Clip Highs',
            'Height Multiplier',
            'doCurve',
            'Curve Object',
            'curveDirection',
            'Follow Curve',
            'Audio Duration',
            'Audio Filename',
            'max_volume_dB',
            'Baked Volume',
        ]

def sanitize_string(str):
    return ''.join(c for c in str.lower() if c.isalpha() or c.isdigit() or c==' ').rstrip().replace(' ', '_')

def write_to_json_file(path, fname, content):

    fpath = os.path.join(path, fname + '.json')

    with open(fpath, "w") as outfile:     
        json.dump(content, outfile, indent=4)

    # f = open(fpath, "a")
    # f.write(str(content))
    # f.close()

def write_spectrogram_preset_to_file(self, context):
    scn = context.scene
    obj = context.object

    presets_folder = scn.stm_settings.presets_folder
    preset_fpath = obj.stm_spectro.presets_geonodes_proper
    
    with open(r'%s'%preset_fpath,'r') as f:
        preset_json=json.load(f)

    preset_name = preset_json['name']
    
    preset_values = {}

    modifier = obj.modifiers['STM_spectrogram']
    
    for i in modifier.node_group.interface.items_tree:
        if i.name not in exclude_preset_inputs:

            value = modifier[i.identifier]

            if value != i.default_value:
                preset_values[i.name] = value

    preset = {}
    preset['name'] = preset_name
    preset['values'] = preset_values
    fname = sanitize_string(preset_name)

    # print(fname)

    write_to_json_file(presets_folder, fname, preset)  

def get_enum_items_from_enum_prop(rna_type, prop_str):
    prop = rna_type.bl_rna.properties[prop_str]
    return [e.identifier for e in prop.enum_items]
            
def apply_spectrogram_preset_proper(stm_obj, preset_fpath):
    

    with open(r'%s'%preset_fpath,'r') as f:
        preset_json=json.load(f)

    preset_name = preset_json['name']
    preset_values = preset_json['values']

    stm_obj.stm_spectro.presets_geonodes_proper = preset_name

    # obj.stm_spectro.preset_geonodes_name = preset_name

    # print(preset_name)
    # print(preset_values)
    # print('')

    modifier = stm_obj.modifiers['STM_spectrogram']
    
    for i in modifier.node_group.interface.items_tree:
        if type(i).__name__ != 'NodeTreeInterfaceSocketGeometry':
            if  i.name not in exclude_preset_inputs:
                if not i.name:
                    pass
                elif i.name in preset_values:
                    value = preset_values[i.name]
                    set_geonode_value_proper(modifier, i.name, value)
                else:
                    reset_geonode_value(modifier, i.name)




    
    stm_modifier = stm_obj.modifiers['STM_spectrogram']
    curve_node = stm_modifier.node_group.nodes['MACURVE']
    preset_points_array = [
        [0.00, 0.5],
        [0.25, 0.5],
        [0.50, 0.5],
        [0.75, 0.5],
        [1.00, 0.5]
    ]
    
    for value_name in preset_values:
        if value_name == 'EQCurve_points':
            preset_points = preset_values['EQCurve_points']
            preset_points_array = [preset_points[value] for value in preset_points]

    
    set_points_on_eq_curve(curve_node, preset_points_array)

    
    # for value_name in preset_values:
    #     if value_name == 'EQCurve_points':
    #         stm_modifier = stm_obj.modifiers['STM_spectrogram']
    #         curve_node = stm_modifier.node_group.nodes['MACURVE']
    #         preset_points = preset_values['EQCurve_points']
    #         preset_points_array = [preset_points[value] for value in preset_points]

    
    #         set_points_on_eq_curve(curve_node, preset_points_array)


    refresh_all_areas()

def next_power_of_2(x):  
    return 1 if x == 0 else 2**(x - 1).bit_length()

def apply_waveform_style(self, context):

    bpy.ops.stm.detect_key_pressed('INVOKE_DEFAULT', key='ALT')
    is_alt_pressed = context.scene.stm_settings.is_alt_pressed
    
    if is_alt_pressed:
        selection = context.selected_objects
    else:
        selection = [context.object]

    for obj in selection:
        if obj.stm_spectro.stm_type == 'waveform':
            style = obj.presets_waveform_style.split('-')[0]

            stm_modifier = obj.modifiers['STM_waveform']
            stm_modifier['Input_8'] = int(style)

            stm_modifier.show_viewport = False
            stm_modifier.show_viewport = True


def reset_spectrogram_values(resetAll=False, values=[]):

    exclude_inputs = [
        'Geometry',
        'Audio Duration',
        'Log to Lin',
        'Audio Filename',
        'Baked Volume',
        'Image',
        'Material',
        'max_volume_dB',
        'max_intensity',
        'geometryType',
        'showGrid',
        'doExtrude',
        'Base Height',
        'doCylinder',
        'Alignment',
        'Curve Object'
    ]

    stm_modifier = bpy.context.object.modifiers['STM_spectrogram']

    if resetAll:
        print('-INF- reset all')
        for i in stm_modifier.node_group.interface.items_tree:
            if i.name not in exclude_inputs:
                set_geonode_value(stm_modifier, i, i.default_value)

    else:
        print('-INF- reset values')
        for i in stm_modifier.node_group.interface.items_tree:
            if i.name in values and i.name not in exclude_inputs:
                set_geonode_value(stm_modifier, i, i.default_value)

    stm_modifier.show_viewport = False
    stm_modifier.show_viewport = True

def set_geonode_value(gn_modifier, input, value):

    input_type = type(input.default_value).__name__
    value_type = type(value).__name__

    if input_type == value_type:                    # if input type matches value type
        gn_modifier[input.identifier] = value       # apply value to input

        input.default_value = input.default_value   # "redraw" input by updating its default_value
                                                    # (avoids problems like FACTOR inpus being drawn as floats
                                                    # look into input "subtype" in geometry nodes ?? (factor, percentage...)

    else:
        print('-ERR- invalid type. can\'t apply %s (%s) on input "%s" (%s)'%(value, value_type, input.name, input_type))

def set_geonode_value_proper(modifier, input_name, value):
    for i in modifier.node_group.interface.items_tree:
        if i.name == input_name:

            input_type = type(i.default_value).__name__
            value_type = type(value).__name__

            if input_type == value_type:
                modifier[i.identifier] = value
                i.default_value = i.default_value

def get_geonode_value_proper(modifier, input_name):
    for i in modifier.node_group.interface.items_tree:
        if i.name == input_name:
            return modifier[i.identifier]

def reset_geonode_value(modifier, input_name):
    for i in modifier.node_group.interface.items_tree:
        if i.name == input_name:
            modifier[i.identifier] = i.default_value
            i.default_value = i.default_value


def append_from_blend_file(blendfile, section, target, forceImport=False):

    obj_selection = bpy.context.selected_objects
    obj_active = bpy.context.object

    doAppend = True
    result = True

    dataSet = ''

    #choose correct data set from section name
    if section == 'Object':
        dataSet = bpy.data.objects
    elif section == 'Material':
        dataSet = bpy.data.materials
    elif section == 'NodeTree':
        dataSet = bpy.data.node_groups

    alreadyExist = dataSet.get(target)

    if alreadyExist and not forceImport:
        # print('-INF- '+section+' "'+target+'" already in scene, skipping import.')
        pass
    else:
        #append command, with added backslashes to fit python filepath formating

        new_datablock = None

        old_set = set(dataSet[:])

        result = bpy.ops.wm.append(
                                    filepath=blendfile + "\\"+section+"\\" + target,
                                    directory=blendfile + "\\"+section+"\\",
                                    filename=target
                                )

        new_set = set(dataSet[:]) - old_set

        new_datablock = list(new_set)[0]

        if new_datablock == None:
            print('-ERR- Failed importing '+section+' "'+target+'" from "'+blendfile+'"')
            result = False
        else:
            # print(f'-INF- successfully imported {new_datablock}')
            result = new_datablock

        # bpy.ops.object.select_all(action='DESELECT')

        for o in bpy.data.objects:
            o.select_set(False)

        for o in obj_selection:
            o.select_set(True)

        bpy.context.view_layer.objects.active = obj_active

        for lib in bpy.data.libraries:
            if lib.name == os.path.basename(blendfile):
                # print(f'-INF- removing lib {lib}')
                bpy.data.batch_remove(ids=(lib,))

        return result

def ffshowspectrumpic(ffmpegPath, audio_file, outputPath, width=1024, height=512, scale='log', fscale='lin', colorMode='intensity', drange=120, limit=0, overwrite=False):

    # imagePath = outputPath + os.path.basename(audioPath)+'_%ix%i_%s_%s.png'%(width, height, scale, colorMode)
    audioName = os.path.basename(audio_file.filepath)
    # imageName = f'{audioName}_{width}x{height}_{scale}_{colorMode}.png'
    imageName = f'{audioName}_{width}x{height}.png'
    imagePath = os.path.join(outputPath, imageName)
    imagePath = os.path.abspath(imagePath)
    # imagePath = outputPath + '\\' + imageName

    print(f"{imageName = }")
    print(f"{imagePath = }")

    if not os.path.exists(outputPath):
        os.mkdir(outputPath)

    if os.path.exists(imagePath) and not overwrite:
        print('-INF- spectrogram image already exists with these parameters, skipping generation')
        return imagePath
    else:

        print('-INF- launching ffmpeg')
        try:
            #build ffmpeg command
            ffmCMD = ''.join((
                                ffmpegPath,
                                ' -y -i "',
                                audio_file.filepath,
                                '" -lavfi showspectrumpic=s='+str(width)+'x'+str(height),
                                ':mode=combined:legend=disabled:scale=%s:fscale=%s:color=%s:drange=%s:limit=%s'%(scale, fscale, colorMode, drange, limit)+' -qscale:v 1 "',
                                imagePath,
                                '" -loglevel quiet'
                            ))


            #process ffmpeg command
            subprocess.call(ffmCMD)

            if os.path.exists(imagePath):
                print('-INF- generation successful !')
                return imagePath

            else:
                print('-ERR- failed to generate spectrogram image')
                return None

        except:
            print('-ERR- failed to generate spectrogram image')
            return None

def ffgeneratethumbnail(ffmpegPath, image_path, size_x=128, size_y=-1):
    addon_path = os.path.dirname(__file__)
    outputPath = os.path.join(addon_path, './thumbs')
    image_name = os.path.basename(image_path)
    thumbnail_path = f'{outputPath}/{image_name}'

    ffmCMD = f'{ffmpegPath} -y -i "{image_path}" -vf scale={size_x}:{size_y} "{thumbnail_path}"'
    subprocess.call(ffmCMD)

    return thumbnail_path

def ffmetadata(ffmpegPath, audio_file):


    ffmCMD = '%s -i "%s" -f ffmetadata -hide_banner -'%(ffmpegPath, audio_file.filepath)
    ffmCMD_out = subprocess.run(ffmCMD, check=True, capture_output=True).stderr.decode('utf-8')
    # print(ffmCMD_out)
    #subprocess.call(ffmCMD)


    sub1 = os.path.basename(audio_file.filepath) + "':"
    sub2 = "Output #0, ffmetadata, to 'pipe:':"
    json_output = {}

    metadata_output = str(ffmCMD_out).split(sub1)[1].split(sub2)[0]

    metadata = []

    if 'Metadata:' in metadata_output:
        metadata = metadata_output.split('Metadata:')[1].split('Duration:')[0]
        metadata = [line for line in metadata.strip().split('\n')]
    else:
        print(f'-ERR- couldn\'t decrypt metadata from file <{audio_file.name}>')
        

    metadata_list = {}

    for m in metadata:
        name = m.split(':')[0].strip()
        value = m.split(':')[1].strip()

        metadata_list[name] = value

    duration = metadata_output.split('Duration:')[1].split('Stream #0:0:')[0].split(',')[0]
    try:
        duration = timestring_to_seconds(duration.strip())
    except:
        print('can\'t figure out duration')
        pass

    bitrate = metadata_output.split('bitrate:')[1].split('Stream #0:0:')[0]

    stream0 = metadata_output.split('Stream #0:0:')[1].split('\n')[0]
    # stream1 = metadata_output.split('Stream #0:1:')[1].split('\n')[0]

    json_output = {}

    json_output['filepath'] = audio_file.filepath
    json_output['filename'] = os.path.basename(audio_file.filepath)
    json_output['metadata'] = metadata_list
    json_output['duration'] = duration
    json_output['bitrate'] = bitrate.strip()
    json_output['stream0'] = stream0.strip()
    # json_output['stream1'] = stream1.strip()

    return json_output

def ffvolumedetect(ffmpegPath, audio_file):
    ffmCMD = '%s -i "%s" -af volumedetect -f null /dev/null -hide_banner'%(ffmpegPath, audio_file.filepath)
    try:
        ffmCMD_out = subprocess.run(ffmCMD, check=True, capture_output=True).stderr.decode('utf-8').split('\n')

        #subprocess.call(ffmCMD)

        # --------------------------------------------------
        #                   TODO
        #
        # verify if output is valid,
        # if not set the [max_volume] and [mean_volume] to default values ?


        json_output = {}

        for line in ffmCMD_out:
            if line.startswith('[') and ':' in line:

                name = line.split(']')[1].split(':')[0].strip()
                value = line.split(':')[1].strip().replace(' dB', '')

                json_output[name] = value

        return json_output

    except:
        return None

def ffastats(ffmpegPath, audio_file):
    ffmCMD = '%s -i "%s" -af astats=measure_perchannel=none -f null -'%(ffmpegPath, audio_file.filepath)

    try:
        ffmCMD_out = subprocess.run(ffmCMD, check=True, capture_output=True).stderr.decode('utf-8').split('\n')

        #subprocess.call(ffmCMD)

        json_output = {}

        for line in ffmCMD_out:

            if line.startswith('[') and ':' in line:

                name = line.split(']')[1].split(':')[0].strip()
                value = line.split(':')[1].strip()

                json_output[name] = value

        return json_output

    except:
        return None

def ffsignalstats(ffmpegPath, imagePath, target_key):

    ffmCMD = ''.join((
                        ffmpegPath,
                        ' -y -i "',
                        imagePath,
                        '" -vf "signalstats,metadata=print"'
                        ' -hide_banner -an -f null -'
                        #'" -loglevel quiet'
                    ))

    ffmCMD_out = subprocess.run(ffmCMD, check=True, capture_output=True).stderr.decode('utf-8')
    metadata = [line for line in ffmCMD_out.strip().split('\n')]

    json = {}

    for line in metadata:
        if line.startswith('[Parsed_metadata') and 'lavfi.signalstats.' in line:
            data = line.split('lavfi.signalstats.')[1]
            key = data.split('=')[0]
            value = data.split('=')[1].strip()

            json[key] = value

    return json[target_key]

def get_first_match_from_metadata(metadata, match, exclude=None):

    result = ''

    for m in metadata:
        name = m
        value = metadata[m]

        if exclude is not None and exclude in name.lower():
            pass
        elif match in name.lower():
            result = value
            break

    return result

def update_metadata(self, context):

    scn = context.scene
    obj = get_stm_object(context.object)

    if obj.stm_spectro.audio_file != None:
        mdata = ffmetadata(scn.stm_settings.ffmpegPath, obj.stm_spectro.audio_file)
        # soundstrip.frame_final_duration

        if not mdata:
            obj.stm_spectro.meta_title = '[unkown]'
            obj.stm_spectro.meta_album = '[unkown]'
            obj.stm_spectro.meta_artist = '[unkown]'
            obj.stm_spectro.meta_duration_seconds = 0.0
            obj.stm_spectro.meta_duration_format = ''
            
        else:
            title = get_first_match_from_metadata(mdata['metadata'], match='title')
            album = get_first_match_from_metadata(mdata['metadata'], match='album', exclude='artist')
            artist = get_first_match_from_metadata(mdata['metadata'], match='artist')
            duration = mdata['duration']


            obj.stm_spectro.meta_title = os.path.basename(obj.stm_spectro.audio_file_path) if title == '' else title
            obj.stm_spectro.meta_album = '[unkown]' if album == '' else album
            obj.stm_spectro.meta_artist = '[unkown]' if artist == '' else artist
            # scn.stm_settings.duration = str(datetime.timedelta(seconds=round(duration)))
            obj.stm_spectro.meta_duration_seconds = duration
            obj.stm_spectro.meta_duration_format = seconds_to_timestring(duration)        

        redraw_all_viewports()

def update_curve_object(self, context):
    stm_obj = get_stm_object(context.object)

    stm_obj.modifiers['STM_spectrogram']['Socket_3'] = stm_obj.stm_spectro.curve_object

def update_curve_deform_axis(self, context):
    stm_obj = get_stm_object(context.object)

    stm_obj.modifiers['STM_spectrogram']['Socket_22'] = int(stm_obj.stm_spectro.curve_deform_axis)

def update_audio_filename_display(self, context):
    stm_obj = get_stm_object(context.object)

    if stm_obj.stm_spectro.audio_file:
        audio_filename = os.path.basename(stm_obj.stm_spectro.audio_file.filepath)
        stm_obj.stm_spectro.audio_filename_display = audio_filename


def get_first_empty_channel(seq):
    sequences = seq.sequences
    channels = seq.channels

    used_channels = [s.channel for s in sequences]
    channel_id = 0

    for c in channels:
        id = channels.keys().index(c.name)
        if id > 0 and  id not in used_channels:
            channel_id= id
            break

    return channel_id

def use_audio_in_scene(context, audio_file, offset=0):
    
    scn = context.scene
    stm_obj = get_stm_object(context.object)

    audio_filepath = audio_file.filepath
    audio_filename = os.path.basename(audio_filepath)

    seq = scn.sequence_editor

    if not seq:                                     # create new sequence if there is none
        scn.sequence_editor_create()
    
    

    for s in seq.sequences:                                     # check if the requested sound isn't already loaded
        if s.stm_settings.spectrogram_object == stm_obj:        # and associated to our spectrogram
            if s.sound.filepath == stm_obj.stm_spectro.audio_file.filepath:
                print('-INF- sound already loaded, skipping import')
                return s
            

    # To add a new soundstrip, we're using the command new_sound()
    # From what I understand, I have to give a valid filepath to the command.
    # Sadly this creates a copy of our sound datablock.

    # What follows is a workaround to delete this new datablock 
    # and use our existing one instead.


    sounds_list = [s for s in bpy.data.sounds]                  # list all sounds in scene
    
    soundstrip = seq.sequences.new_sound(                       # create the soundstrip
            name=audio_filename,
            filepath=audio_filepath,
            channel=get_first_empty_channel(seq), 
            frame_start=offset
        )
    
    sounds_list_new = [s for s in bpy.data.sounds]              # list all sounds in scene again

    sounds_to_delete = list(set(sounds_list_new) - set(sounds_list))    # compare the two lists
    if len(sounds_to_delete) > 0:                                       # delete the new datablocks created
        for s in sounds_to_delete:
            print('-INF- Deleting duplicate sound %s'%s.name)
            bpy.data.sounds.remove(s)


    soundstrip.sound = audio_file        # assign the proper sound to the soundstrip
    soundstrip.show_waveform = True
    soundstrip.stm_settings.spectrogram_object = stm_obj

    return soundstrip

def toggle_audio_in_scene(self, context):

    obj = self.id_data
    seq = context.scene.sequence_editor   

    for s in seq.sequences:
        if s.stm_settings.spectrogram_object == obj:
            s.mute = not s.mute

def set_spectrogram_audio_solo(stm_obj):

    if stm_obj.stm_spectro.stm_type in ['spectrogram', 'waveform']:

        seq = bpy.context.scene.sequence_editor

        for s in seq.sequences:
            if s.stm_settings.spectrogram_object != stm_obj:
                s.mute = True
            else:
                s.mute = False

def set_playback_to_audioSync(context):
    if context.scene.sync_mode != 'AUDIO_SYNC':
        context.scene.sync_mode = 'AUDIO_SYNC'
        print("-INF- set sync_mode to 'AUDIO_SYNC'")

def frame_all_timeline():

    print('-INF- frame_all_timeline()')

    for my_area in bpy.context.window.screen.areas:

        if my_area.type == 'DOPESHEET_EDITOR':
            for my_region in my_area.regions:

                if my_region.type == 'WINDOW':
                    with bpy.context.temp_override(
                        window = bpy.context.window,
                        area = my_area,
                        region = my_region,
                    ):
                        bpy.ops.action.view_all()

def frame_clip_in_sequencer(context):

    print('-INF- frame_clip_in_sequencer()')

    for my_area in context.window.screen.areas:
        if my_area.type == 'SEQUENCE_EDITOR':
            for my_region in my_area.regions:

                if my_region.type == 'WINDOW':
                    with bpy.context.temp_override(
                        window = bpy.context.window,
                        area = my_area,
                        region = my_region,
                    ):
                        
                        context.space_data.show_region_channels = False
                        context.space_data.show_region_toolbar = False

                        bpy.ops.sequencer.view_all()
                        bpy.ops.view2d.zoom(deltax=0.0, deltay=30, use_cursor_init=False)
                        bpy.ops.view2d.pan(deltax=0, deltay=-99999999)
                        bpy.ops.view2d.pan(deltax=0, deltay=125)
                        bpy.ops.view2d.zoom(deltax=0.0, deltay=-0.5, use_cursor_init=False)

def is_audio_in_sequencer(context, audio_file):
    if not context.scene.sequence_editor:
        return False
    else:
        return any([strip.sound.filepath == audio_file.filepath for strip in context.scene.sequence_editor.sequences])

def generate_spectrogram(stm_obj, audio_file, image_file, duration_seconds, max_volume_dB=0, peak_brightness=0):

    print('-INF- updating spectrogram')

    scn = bpy.context.scene

    audioName = sanitize_input(os.path.basename(audio_file.filepath))
    # stm_obj.stm_spectro.stm_items[stm_obj.name].name = f'STM_{audioName}'
    # stm_obj.name = f'STM_{audioName}'
    # stm_obj.name = audioName


    assetFile = scn.stm_settings.assetFilePath

    append_from_blend_file(assetFile, 'NodeTree', 'STM_spectrogram')

    # print(f'{stm_obj =}')
    # print(f'{imagePath =}')

    stm_GN = stm_obj.modifiers['STM_spectrogram']
    # stm_GN.node_group = bpy.data.node_groups['STM_spectrogram']

    stm_GN["Input_2"] = image_file
    # stm_GN["Input_60"] = os.path.basename(audio_file.filepath)
    stm_GN["Input_45"] = duration_seconds
    stm_GN["Input_64"] = max_volume_dB
    stm_GN["Input_75"] = peak_brightness
    

    stm_GN.show_viewport = False
    stm_GN.show_viewport = True

    refresh_all_areas()
    redraw_all_viewports()

    image_file.colorspace_settings.name = "sRGB"
    image_file.colorspace_settings.name = "sRGB"

    spectro_texture = bpy.data.textures.new(image_file.name, type='IMAGE')
    spectro_texture.image = image_file
    spectro_texture.extension = 'CLIP'

    stm_obj.stm_spectro.image_texture = spectro_texture
    stm_obj.stm_spectro.image_filename = os.path.basename(image_file.filepath)
    stm_obj.stm_spectro.audio_filename = os.path.basename(stm_obj.stm_spectro.audio_file.filepath)
    # stm_GN["Input_60"] = os.path.basename(stm_obj.stm_spectro.audio_file.filepath)
    


    mat_raw = get_stm_material(stm_obj, 'STM_rawTexture')
    mat_gradient = get_stm_material(stm_obj, 'STM_gradient')

    mat = mat_raw if stm_obj.stm_spectro.material_type == 'raw' else mat_gradient if stm_obj.stm_spectro.material_type == 'gradient' else stm_obj.stm_spectro.material_custom
    
    if stm_obj.stm_spectro.material_type == 'waveform':
        pass
    elif stm_obj.stm_spectro.material_type == 'raw':
        mat.name = f'STM_rawTex_{audioName}'
    elif stm_obj.stm_spectro.material_type == 'gradient':
        mat.name = f'STM_gradient_{audioName}'

    stm_GN["Input_12"] = mat


    if stm_obj.data.materials:
        stm_obj.data.materials[0] = mat
    else:
        stm_obj.data.materials.append(mat)

    stm_GN.show_viewport = False
    stm_GN.show_viewport = True

    

    return True

def apply_gradient_preset(self, context):

    print('-INF- Applying gradient preset')

    scn = bpy.context.scene

    with open(r'%s'%scn.stm_settings.gradient_presets_json_file,'r') as f:
        presets=json.load(f)

        # p = scn.stm_settings.gradient_preset
        p = context.object.presets_gradient.replace('.png', '')
        p = p.split('-')[1]
        preset = presets[p]


        update_stm_material(self, context)

        mat_gradient = None

        for m in bpy.data.materials:
            if m.get('STM_material_type') and m.get('STM_object'):
                if m['STM_material_type'] == 'STM_gradient' and m['STM_object'] == context.object:
                    mat_gradient = m
        
        # if mat_gradient == None:
        #     mat_gradient = get_stm_material(context.object, 'STM_gradient')

        cr_node = mat_gradient.node_tree.nodes['STM_gradient']
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

        for i in range(0,len(preset)):
            position = preset[i][0]
            color = preset[i][1]

            #print(position)

            if position == 0 or position == 1:
                cr.elements[i].color = color
            else:
                cr.elements.new(position)
                cr.elements[i].color = color

    # funcs.apply_spectrogram_preset(values)

def apply_eq_curve_preset(self, context):
    print('-INF- apply eq curve preset')

    obj = context.object
    preset = int(obj.presets_eq_curve.split('-')[0])

    obj.modifiers['STM_spectrogram']["Socket_20"] = preset

    obj.modifiers['STM_spectrogram'].show_viewport = False
    obj.modifiers['STM_spectrogram'].show_viewport = True

    redraw_all_viewports()

def apply_eq_curve_preset_proper(stm_obj, preset_name):
    # print('-INF- apply eq curve preset proper')

    with open(r'%s'%bpy.context.scene.stm_settings.eq_curve_presets_json_file,'r') as f:
        presets=json.load(f)

    # preset_name = stm_obj.presets_eq_curve.replace('.png', '')
    # preset_name = preset_name.split('-')[1]
    preset = presets[preset_name]

    
    # stm_obj = context.object
    stm_modifier = stm_obj.modifiers['STM_spectrogram']
    curve_node = stm_modifier.node_group.nodes['MACURVE']
    preset_points = [preset[value] for value in preset]

    set_points_on_eq_curve(curve_node, preset_points)

def set_points_on_eq_curve(curve_node, preset_points):
    
    # print(preset_points)

    points = curve_node.mapping.curves[0].points

    # Keep only 2
    while len(points) > 2:
        points.remove(points[1]) #Can't remove at 0 (don't know why)

    # create as many points as needed
    while len(points) < len(preset_points):
        points.new(0,0)

    # set location for each point
    for i, p in enumerate(preset_points):
        points[i].location = (p[0], p[1])
        points[i].handle_type = 'AUTO_CLAMPED'

    curve_node.mapping.update()
    curve_node.update()

def is_stm_object_selected(context):

    if not context.object:
        return False
    
    else:
        return context.object.stm_spectro.stm_type in ['spectrogram', 'waveform']

def update_stm_material(self, context):

    obj = self.id_data

    
    audioName = ''
    geonode_name = ''
    geonode_slot = ''

    if obj.stm_spectro.audio_file:
        audioName = sanitize_input(os.path.basename(obj.stm_spectro.audio_file.filepath))

    if obj.stm_spectro.stm_type == 'spectrogram':
        geonode_name = 'STM_spectrogram'
        geonode_slot = "Input_12"

    elif obj.stm_spectro.stm_type == 'waveform':
        geonode_name = 'STM_waveform'
        geonode_slot = "Input_15"

    mat = None


    if obj.stm_spectro.material_type == 'raw':
        mat = get_stm_material(obj, 'STM_rawTexture')
        mat.name = f'STM_rawTex_{audioName}'

    elif obj.stm_spectro.material_type == 'gradient':
        mat = get_stm_material(obj, 'STM_gradient')
        mat.name = f'STM_gradient_{audioName}'

    elif obj.stm_spectro.material_type == 'emission':
        mat = get_stm_material(obj, 'STM_waveform')
        mat.name = f'STM_waveform_{audioName}'
        
    elif obj.stm_spectro.material_type == 'custom':
        mat = obj.stm_spectro.material_custom

    
    obj.modifiers[geonode_name][geonode_slot] = mat


    if obj.data.materials:                      # if obj has slots
        obj.data.materials[0] = mat             # assign to 1st material slot
    else:                                       # else
        obj.data.materials.append(mat)          # append mat

    if mat:
        obj.active_material.preview_render_type = 'FLAT'        # toggle active material 
        obj.active_material.preview_render_type = 'SPHERE'      # to force update in "Material" window

def get_enum_prop_value_from_index(context, enum_prop_name, idx):
    items = context.bl_rna.properties[enum_prop_name].enum_items
    return items[idx]

def get_idx_value_from_enum_prop(context, enum_prop_name, prop_name):
    items = context.bl_rna.properties[enum_prop_name].enum_items
    if prop_name in items:
        return items[prop_name].value

def set_waveform_style(self, context):
    obj = context.object
    style = obj.stm_spectro.waveform_style
    style_arr = ['line', 'dots', 'plane', 'cubes', 'tubes', 'zigzag', 'zigzag_smooth']
    obj.modifiers['STM_waveform']['Input_8'] = style_arr.index(style)

def set_waveform_side_options(self, context):

    bpy.ops.stm.detect_key_pressed('INVOKE_DEFAULT', key='ALT')
    is_alt_pressed = context.scene.stm_settings.is_alt_pressed
    
    if is_alt_pressed:
        selection = context.selected_objects
    else:
        selection = [context.object]

    for obj in selection:
        if obj.stm_spectro.stm_type == 'waveform':
            modifier = obj.modifiers['STM_waveform']
            side_options_value = obj.stm_spectro.waveform_side_options
            idx = get_idx_value_from_enum_prop(obj.stm_spectro, 'waveform_side_options', side_options_value)
            
            set_geonode_value_proper(modifier, 'Side', idx)




def set_curveAlignment(self, context):
    obj = context.object
    obj.modifiers['STM_spectrogram']['Socket_5'] = True if obj.stm_spectro.curveAlignment == 'edge' else False

def set_waveform_resolution_choice(self, context):
    obj = context.object

    obj.modifiers['STM_waveform']['Input_17'] = True if obj.stm_spectro.waveform_resolution_choice == 'custom' else False

def convert_size(size_bytes):
   if size_bytes == 0:
       return "0B"
   size_name = ("B", "KB", "MB", "GB", "TB", "PB", "EB", "ZB", "YB")
   i = int(math.floor(math.log(size_bytes, 1024)))
   p = math.pow(1024, i)
   s = round(size_bytes / p, 2)
   return "%s %s" % (s, size_name[i])

def get_dir_size(path='.'):
    total = 0
    with os.scandir(path) as it:
        for entry in it:
            if entry.is_file():
                total += entry.stat().st_size
            elif entry.is_dir():
                total += get_dir_size(entry.path)

    return total

def get_stm_material(stm_obj, mat_name):

    scn = bpy.context.scene
    assetFile = scn.stm_settings.assetFilePath
    mat = None

    for m in bpy.data.materials:
        if m.get('STM_material_type') and m.get('STM_object'):
            if m['STM_material_type'] == mat_name and m['STM_object'] == stm_obj:

                # print('-INF- found matching rawTexture material to apply, skipping import')
                mat = m

    if mat is None:
        # print('-INF- importing new rawTexture material')

        mat = append_from_blend_file(assetFile, 'Material', mat_name, forceImport=True)
        mat['STM_object'] = stm_obj

    if mat_name == 'STM_rawTexture':
        mat.node_tree.nodes['spectro_image'].image = stm_obj.modifiers['STM_spectrogram']['Input_2']


    return mat

def get_wave_offset(context):
    stm_obj = get_stm_object(context.object)
    stm_objects_list = context.scene.stm_settings.stm_objects_list
    nb_waveforms = 0

    for item in stm_objects_list:
        if item.object.stm_spectro.stm_type == 'waveform' and item.object.stm_spectro.spectrogram_object == stm_obj:
            nb_waveforms += 1

    return float(nb_waveforms/20) if nb_waveforms > 0 else 0



def stm_00_ffmetadata(self, context):
    obj = get_stm_object(context.object)
    scn = bpy.context.scene

    data_raw = ffmetadata(scn.stm_settings.ffmpegPath, obj.stm_spectro.audio_file)
    
    artist = ''
    album = ''
    title = obj.stm_spectro.audio_file.name

    if data_raw != None:
        artist = get_first_match_from_metadata(data_raw['metadata'], match='artist')
        album = get_first_match_from_metadata(data_raw['metadata'], match='album', exclude='artist')
        title = get_first_match_from_metadata(data_raw['metadata'], match='title')
    

    # print('artist :', artist)
    # print('album :', album)
    # print('title :', title)


    obj.stm_spectro.meta_title = title if title != '' else os.path.basename(obj.stm_spectro.audio_file.filepath)
    obj.stm_spectro.meta_album = album if album != '' else '[unkown]'
    obj.stm_spectro.meta_artist = artist if artist != '' else '[unkown]'

    stm_mod = obj.modifiers['STM_spectrogram']
    
    # obj.modifiers['STM_spectrogram']['Input_60'] = obj.stm_spectro.audio_filename
    # obj.modifiers['STM_spectrogram']['Socket_30'] = obj.stm_spectro.audio_filename

    set_geonode_value_proper(stm_mod, 'Audio Filename', obj.stm_spectro.audio_filename)
    set_geonode_value_proper(stm_mod, 'Title', obj.stm_spectro.audio_filename)

def stm_01_volume_data(self, context):

    obj = get_stm_object(context.object)
    scn = bpy.context.scene

    # get peak volume using ffvolumedetect() (less accurate but quicker)

    volume_data_raw = ffvolumedetect(scn.stm_settings.ffmpegPath, obj.stm_spectro.audio_file)
    max_volume_dB = float(volume_data_raw['max_volume'])
    obj.stm_spectro.max_volume_dB = max_volume_dB
    print(f'{max_volume_dB = }')

    # get peak volume using ffastats() (more accurate but longer)

    # astats = ffastats(scn.stm_settings.ffmpegPath, obj.stm_spectro.audio_file.filepath)
    # peak_level_dB = round(float(astats['Peak level dB']), 2)
    # obj['peak_level_dB'] = peak_level_dB
    # print(f'{peak_level_dB = }')

def stm_02_generate_spectrogram_img(self, context):

    scn = bpy.context.scene
    obj = get_stm_object(context.object)

    ffmpegPath = scn.stm_settings.ffmpegPath
    audio_file = obj.stm_spectro.audio_file
    outputPath = scn.stm_settings.outputPath

    w = scn.stm_settings.userWidth
    h = scn.stm_settings.userHeight

    spectrogram_image_path = ffshowspectrumpic(
        ffmpegPath,
        audio_file,
        outputPath,
        width=w,
        height=h,
        scale=scn.stm_settings.spectro_scale,
        fscale=scn.stm_settings.spectro_fscale,
        colorMode=scn.stm_settings.spectro_colorMode,
        drange=scn.stm_settings.spectro_drange,
        limit=obj.stm_spectro.max_volume_dB,
        overwrite=scn.stm_settings.overwrite_image,
    )



    # obj['spectrogram_file_path'] = spectrogram_image_path
    obj.stm_spectro.image_file = bpy.data.images.load(spectrogram_image_path, check_existing=True)

def get_timeline_length_from_audio_duration(duration_seconds):
    
    fps = bpy.context.scene.render.fps
    duration_frames = duration_seconds * fps

    return int(duration_frames + fps)

def add_new_speaker(name, audio_file):
    speaker_data = bpy.data.speakers.new(name)
    speaker_data.sound = audio_file
    speaker_obj = bpy.data.objects.new(name, speaker_data)
    bpy.context.scene.collection.objects.link(speaker_obj)

    return speaker_obj


def adapt_timeline_length(context):
    print('ADAPT TIMELINE LENGTH')
    stm_obj = get_stm_object(context.object)
    duration_seconds = get_geonode_value_proper(stm_obj.modifiers['STM_spectrogram'], 'Audio Duration')
    timeline_end = get_timeline_length_from_audio_duration(duration_seconds)

    context.scene.frame_start = 1
    context.scene.frame_end = timeline_end

def stm_03_build_spectrogram(self, context):

    scn = bpy.context.scene
    obj = get_stm_object(context.object)

    if scn.stm_settings.bool_rename_stm_object:
        obj.name = obj.stm_spectro.audio_filename

    ffmpegPath = scn.stm_settings.ffmpegPath
    outputPath = scn.stm_settings.outputPath

    # I used to analyze the image brightness to normalize the displacement
    # but I don't need it anymore. Now I just analyze the max volume, and gives it
    # to the ffshowspectrumpic() function.

    # peak_brightness = int(ffsignalstats(scn.stm_settings.ffmpegPath, obj['spectrogram_file_path'], 'YMAX'))
    # obj['peak_brightness'] = peak_brightness

    # generate soundstrip
    soundstrip = use_audio_in_scene(context, obj.stm_spectro.audio_file)
    duration_seconds = soundstrip.frame_final_duration/bpy.context.scene.render.fps

    # audio_file = obj.stm_spectro.audio_file
    # audio_filename = os.path.basename(audio_file.filepath)
    # speaker = add_new_speaker(audio_filename, audio_file)

    timeline_end = get_timeline_length_from_audio_duration(duration_seconds)

    scn.frame_start = 1
    scn.frame_end = timeline_end

    
    
    

    

    # generate stm_obj
    generate_spectrogram(
            stm_obj=obj,
            audio_file=obj.stm_spectro.audio_file,
            image_file=obj.stm_spectro.image_file,
            duration_seconds=duration_seconds,
            max_volume_dB=obj.stm_spectro.max_volume_dB,
            # peak_brightness=obj['peak_brightness']
        )

def stm_04_cleanup(self, context):
    scn = bpy.context.scene

    if scn.stm_settings.force_standard_view_transform:
        print('-INF- setting scene view transform to "Standard"')
        scn.view_settings.view_transform = 'Standard'

    if scn.stm_settings.force_eevee_AO:
        scn.eevee.use_gtao = True
        
    # if scn.stm_settings.force_eevee_BLOOM:
    #     scn.eevee.use_bloom = True

    if scn.stm_settings.disable_eevee_viewport_denoising:
        scn.eevee.use_taa_reprojection = False


    set_playback_to_audioSync(context)
    # frame_clip_in_sequencer(context)
    # update_stm_objects(context)
    adapt_timeline_length(context)
    frame_all_timeline()

def stm_05_sleep(self, context):
    time.sleep(0.5)

def add_spectrogram_object(context):
    print('-INF- add spectrogram object')


    scn = context.scene
    assetFile = scn.stm_settings.assetFilePath

    # obj = append_from_blend_file(assetFile, 'Object', 'STM_spectrogram', forceImport=True)
    append_from_blend_file(assetFile, 'NodeTree', 'STM_spectrogram', forceImport=False)

    # print(len(context.scene.objects))

    me = bpy.data.meshes.new('Spectrogram')
    obj = bpy.data.objects.new('Spectrogram', me)
    obj.stm_spectro.stm_status = 'generating'

    

    # stm_coll = create_collection('Spectrogram')
    # stm_coll.objects.link(obj)

    scn.collection.objects.link(obj)
    
    # print(len(context.scene.objects))


    mod = obj.modifiers.new("STM_spectrogram", 'NODES')
    mod.node_group = bpy.data.node_groups['STM_spectrogram'].copy()
    

    # mat_gradient = get_stm_material(obj, 'STM_gradient')
    # set_geonode_value_proper(mod, 'Material', mat_gradient)

    mat_raw = get_stm_material(obj, 'STM_rawTexture')
    set_geonode_value_proper(mod, 'Material', mat_raw)
    
    mat = mat_raw

    if obj.data.materials:
        obj.data.materials[0] = mat
    else:
        obj.data.materials.append(mat)


    obj.stm_spectro.stm_type = 'spectrogram'
    obj.stm_spectro.material_type = 'raw'
    obj.stm_spectro.stm_status = 'done'
    

    print('-INF- added spectrogram object <%s>'%obj.name)

    return obj

def add_waveform_object(context, stm_obj, wave_offset=0.0):
    # print('-INF- add waveform')

    scn = context.scene
    assetFile = scn.stm_settings.assetFilePath


    append_from_blend_file(assetFile, 'NodeTree', 'STM_waveform')
    

    # mesh = bpy.data.meshes.new('Waveform')
    # obj = bpy.data.objects.new("Waveform", mesh)
    curve = bpy.data.curves.new('Waveform', type='CURVE')
    obj = bpy.data.objects.new("Waveform", curve)
    mod = obj.modifiers.new("STM_waveform", 'NODES')
    mod.node_group = bpy.data.node_groups['STM_waveform']

    obj.stm_spectro.stm_type = 'waveform'
    obj.stm_spectro.spectrogram_object = stm_obj

    for coll in stm_obj.users_collection:
        coll.objects.link(obj)


    obj.stm_spectro.material_type = 'emission'
    obj.parent = stm_obj
    
    

    mat = append_from_blend_file(assetFile, 'Material', 'STM_waveform', forceImport=False)

    if mat == None:
        mat = bpy.data.materials['STM_waveform']    

    if obj.data.materials:
        obj.data.materials[0] = mat
    else:
        obj.data.materials.append(mat)

    mod["Input_15"] = mat
    mod["Input_14"] = wave_offset
    mod["Input_16"] = stm_obj

    

    obj.hide_viewport = True
    obj.hide_viewport = False

    # print('-INF- added waveform object <%s>'%obj.name)

    return obj

def add_waveform_to_stm_obj(stm_obj, wave_obj):
    stm_items = stm_obj.stm_spectro.stm_items

    item = stm_items.add()
    # item.name = wave_obj.name
    # item.id = len(stm_items)
    # item.stm_type = 'waveform'
    item.object = bpy.data.objects[wave_obj.name]

    new_idx = len(stm_items)-1
    stm_obj.stm_spectro.stm_items_active_index = new_idx

def reload_spectrogram_thumbnail(self, context):
    pcoll = bpy.utils.previews['preview_thumb_folder']
    image_location = pcoll.images_location
    current_image = context.object.stm_spectro.image_file

    # print(image_location)

    enum_items = []

    # Generate the thumbnails
    for i, image in enumerate(os.listdir(image_location)):
        # print(image)
        # print(current_image.name)

        item_name = image
        filepath = os.path.join(image_location, image)

        # if image == current_image.name:
        #     filepath = current_image.filepath
        if filepath in pcoll:
            thumb = pcoll[filepath]
        else:
            thumb = pcoll.load(filepath, filepath, 'IMAGE', force_reload=True)
            
        enum_items.append((image, item_name, "", thumb.icon_id, i))

        # print(thumb.icon_id)

    return enum_items

def stm_curve_object_poll(self, object):
    return object.type == 'CURVE'


# ----------------------------------------------------------------------------------------------------------------


def find_spectrogram_objects():
    # print('OUPDATÉ')

    context = bpy.context
    settings = context.scene.stm_settings

    len_prev = len(settings.stm_objects_list)
    name_prev = settings.stm_objects_list[settings.stm_objects_list_active_index].name if settings.stm_objects_list_active_index < len_prev else ''
    idx = settings.stm_objects_list_active_index

    # identify context spectrogram objects
    for el in range (len(settings.stm_objects_list)):
        settings.stm_objects_list.remove(0)    

    for o in context.scene.objects:
        if o.stm_spectro.stm_type not in ['spectrogram', 'waveform']:
            continue

        # if o.stm_spectro.stm_type == 'waveform' and not o.stm_spectro.spectrogram_object.stm_spectro.panel_expand:
        #     continue

        if o.stm_spectro.stm_type == 'spectrogram':

            item = settings.stm_objects_list.add()
            item.name = o.name
            item.object = o

            if o.stm_spectro.panel_expand:
                for stm_wave in context.scene.objects:
                    if stm_wave.stm_spectro.stm_type == 'waveform':
                        if stm_wave.stm_spectro.spectrogram_object == o:
                            if stm_wave.name not in settings.stm_objects_list:

                                item = settings.stm_objects_list.add()
                                item.name = stm_wave.name
                                item.object = stm_wave

        if name_prev == o.name:
            idx = len(settings.stm_objects_list)-1

    if context.object:
        if context.object.stm_spectro.stm_type not in ['spectrogram', 'waveform']:
            settings.doHandler = False
            settings.stm_objects_list_active_index = 9999
            settings.doHandler = True

        # stm_obj = get_stm_object(context.object)
        stm_obj = context.object
        for i, item in enumerate(settings.stm_objects_list):
            if item.name == stm_obj.name:
                settings.doHandler = False
                settings.stm_objects_list_active_index = i
                settings.doHandler = True

    # elif len_prev == len(settings.stm_objects_list):
    #     settings.doHandler = False
    #     settings.stm_objects_list_active_index = idx
    #     settings.doHandler = True

def get_active_spectrogram_list_index(self):
    if not self.get('stm_objects_list_active_index'):
        return 0
    return self["stm_objects_list_active_index"]
    

def set_active_spectrogram_list_index(self, value):
    context = bpy.context
    settings = context.scene.stm_settings

    prev = self.get('stm_objects_list_active_index')

    if prev == abs(value):
        return
    
    self['stm_objects_list_active_index'] = abs(value)

    if not settings.doHandler:
        return
    if not context.object:
        return
    
    stm_obj = context.scene.objects.get(settings.stm_objects_list[value].name)

    for o in context.scene.objects:
        o.select_set(False)
        
    stm_obj.select_set(True)
    context.view_layer.objects.active = stm_obj




def find_waveform_objects():
    # print('OUPDATÉ')

    context = bpy.context
    
    if not context.object:
        return

    stm_obj = get_stm_object(context.object)
    settings = stm_obj.stm_spectro

    len_prev = len(settings.stm_items)
    name_prev = settings.stm_items[settings.stm_items_active_index].name if settings.stm_items_active_index < len_prev else ''
    idx = settings.stm_items_active_index

    # identify context spectrogram objects
    for el in range (len(settings.stm_items)):
        settings.stm_items.remove(0)    

    for o in context.scene.objects:
        if o.stm_spectro.stm_type != 'waveform':
            continue
        if o.stm_spectro.spectrogram_object != stm_obj:
            continue

        item = settings.stm_items.add()
        item.name = o.name
        item.object = o

        if name_prev == o.name:
            idx = len(settings.stm_items)-1



    if context.object.stm_spectro.stm_type == 'spectrogram':
        settings.doHandler = False
        settings.stm_items_active_index = 9999
        settings.doHandler = True
    elif context.object.stm_spectro.stm_type == 'waveform':
        for i, item in enumerate(settings.stm_items):
            if item.name == context.object.name:
                settings.doHandler = False
                settings.stm_items_active_index = i
                settings.doHandler = True

    # elif len_prev == len(settings.stm_objects_list):
    #     settings.doHandler = False
    #     settings.stm_objects_list_active_index = idx
    #     settings.doHandler = True

def get_active_waveform_list_index(self):
    if not self.get('stm_items_active_index'):
        return 0
    return self["stm_items_active_index"]

def set_active_waveform_list_index(self, value):
    context = bpy.context
    stm_obj = get_stm_object(context.object)
    settings = stm_obj.stm_spectro

    prev = self.get('stm_items_active_index')

    if prev == abs(value):
        return
    
    self['stm_items_active_index'] = abs(value)

    if not context.scene.stm_settings.doHandler:
        return
    if not context.object:
        return
    if value not in range(0, len(settings.stm_items)):
        return


    wave_obj = context.scene.objects.get(settings.stm_items[value].name)

    for o in context.scene.objects:
        o.select_set(False)
        
    wave_obj.select_set(True)
    context.view_layer.objects.active = wave_obj

def remove_orphan_sounds():

    

    seq = bpy.context.scene.sequence_editor
    for s in seq.sequences:

        if s.stm_settings.spectrogram_object.name not in bpy.context.scene.objects:
            seq.sequences.remove(s)

        elif s.stm_settings.spectrogram_object.stm_spectro.audio_file.filepath != s.sound.filepath:
            seq.sequences.remove(s)

def update_active_audio_in_scene():
    if not bpy.context.object:
        return
    if not bpy.context.scene.stm_settings.doLiveSyncAudio:
        return

    stm_obj = get_stm_object(bpy.context.object)
    audio_file = stm_obj.stm_spectro.audio_file

    if audio_file:
        seq = bpy.context.scene.sequence_editor
        for s in seq.sequences:
            if s.stm_settings.spectrogram_object == stm_obj:
                s.mute = False
            else:
                s.mute = True











def select_object_solo(context, obj):

    for o in context.scene.objects:
        o.select_set(False)

    obj.select_set(True)
    context.view_layer.objects.active = obj





def update_user_resolution(self, context):
    scn = context.scene
    preset = scn.stm_settings.resolutionPreset

    if preset != 'custom':
        width = preset.split('x')[0]
        height = preset.split('x')[1]

        print(width, height)

        scn.stm_settings.userWidth = int(width)
        scn.stm_settings.userHeight = int(height)


def toggle_parent_spectrogram(self, context):
    obj = self.id_data
    modifier = obj.modifiers['STM_waveform']

    stm_obj = get_stm_object(obj)
    follow_spectrogram = get_geonode_value_proper(modifier, 'Follow Spectrogram')
    

    if not follow_spectrogram:
        # obj.parent = stm_obj
        set_geonode_value_proper(modifier, 'Follow Spectrogram', True)
        
    else:
        # obj.parent = None
        set_geonode_value_proper(modifier, 'Follow Spectrogram', False)

def set_default_bake_resolution(self, context):
    context.scene.stm_settings.userWidth = 4096
    context.scene.stm_settings.userHeight = 2048

def create_collection(coll_name):
    coll = bpy.data.collections.new(coll_name)
    bpy.context.scene.collection.children.link(coll)

    return coll

def toggle_hide_viewport_base(self, context):
    obj = self.id_data
    obj.hide_set(obj.stm_spectro.hide_viewport_base)
