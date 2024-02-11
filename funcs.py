import bpy
import os
import subprocess
import math
import json
import time
import datetime

_start_time = time.time()

def start_time():
    global _start_time
    _start_time = time.time()
    print(f'{_start_time = }')

def end_time():
    endtime = seconds_to_timestring(time.time() - _start_time)
    return endtime



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

def select_obj_from_list(self, context):
    scn = context.scene
    idx = scn.stm_obj_list_index

    name = scn.objects[idx].name
    obj = scn.objects.get(name, None)
    try:
        bpy.ops.object.select_all(action='DESELECT')

        obj.select_set(True)
        bpy.context.view_layer.objects.active = obj
    except:
        pass

def match_list_to_active_object():
    scn = bpy.context.scene

    objs = [o for o in scn.objects]
    idx = objs.index(bpy.context.active_object)


    scn.stm_obj_list_index = idx

def _create_prop_from_list(context, data, list, name, icon='NONE', emboss=True):
    context.prop(data, list[name][1], text=list[name][0], icon=icon, emboss=emboss)

def refresh_all_areas():
    for wm in bpy.data.window_managers:
        for w in wm.windows:
            for area in w.screen.areas:
                area.tag_redraw()

def redraw_all_viewports():
    for area in bpy.context.screen.areas:
        if area.type == 'VIEW_3D':
            area.tag_redraw()

def apply_spectrogram_preset(self, context):
    print('-INF- apply GN preset')

    with open(r'%s'%bpy.context.scene.presets_json_file,'r') as f:
        presets=json.load(f)

        p = bpy.context.scene.presets_spectrogram.replace('.png', '')


    preset = presets[p]["preset"]


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
    ]

    for i in stm_modifier.node_group.interface.items_tree:
        if i.name in preset:
            value = preset[i.name]

            if value == 'reset':
                set_geonode_value(stm_modifier, i, i.default_value)
            else:
                set_geonode_value(stm_modifier, i, value)


    stm_modifier.show_viewport = False
    stm_modifier.show_viewport = True

def apply_waveform_style(self, context):
    print('-INF- apply GN preset')


    style = context.object.presets_waveform_style.split('_')[0]

    stm_modifier = context.object.modifiers['STM_waveform']
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
        print('-INF- import cancelled. '+section+' "'+target+'" already in scene')
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
            print(f'-INF- successfully imported {new_datablock}')
            result = new_datablock

        bpy.ops.object.select_all(action='DESELECT')
        for o in obj_selection:
            o.select_set(True)

        bpy.context.view_layer.objects.active = obj_active

        for lib in bpy.data.libraries:
            if lib.name == os.path.basename(blendfile):
                print(f'-INF- removing lib {lib}')
                bpy.data.batch_remove(ids=(lib,))

        return result

def ffshowspectrumpic(ffmpegPath, audioPath, outputPath, width=1024, height=512, scale='log', fscale='lin', colorMode='intensity', drange=120, limit=0):

    imagePath = outputPath + os.path.basename(audioPath)+'_%ix%i_%s_%s.png'%(width, height, scale, colorMode)

    if os.path.exists(imagePath):
        print('-INF- spectrogram image already exists with these parameters, skipping generation')
        return imagePath
    else:

        print('-INF- launching ffmpeg')
        try:
            #build ffmpeg command
            ffmCMD = ''.join((
                                ffmpegPath,
                                ' -y -i "',
                                audioPath,
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

def ffmetadata(ffmpegPath, audioPath):


    print(ffmpegPath)
    print(audioPath)

    try:
        ffmCMD = '%s -i "%s" -f ffmetadata -hide_banner -'%(ffmpegPath, audioPath)
        ffmCMD_out = subprocess.run(ffmCMD, check=True, capture_output=True).stderr.decode('utf-8')
        #subprocess.call(ffmCMD)


        sub1 = os.path.basename(audioPath) + "':"
        sub2 = "Output #0, ffmetadata, to 'pipe:':"
        json_output = {}

        metadata_output = str(ffmCMD_out).split(sub1)[1].split(sub2)[0]

        metadata = metadata_output.split('Metadata:')[1].split('Duration:')[0]
        metadata = [line for line in metadata.strip().split('\n')]

        metadata_list = {}

        for i, m in enumerate(metadata):
            name = m.split(':')[0].strip()
            value = m.split(':')[1].strip()

            metadata_list[name] = value

        duration = metadata_output.split('Duration:')[1].split('Stream #0:0:')[0].split(',')[0]
        try:
            duration = timestring_to_seconds(duration.strip())
        except:
            pass

        bitrate = metadata_output.split('bitrate:')[1].split('Stream #0:0:')[0]

        stream0 = metadata_output.split('Stream #0:0:')[1].split('\n')[0]
        # stream1 = metadata_output.split('Stream #0:1:')[1].split('\n')[0]

        json_output = {}

        json_output['filepath'] = audioPath
        json_output['filename'] = os.path.basename(audioPath)
        json_output['metadata'] = metadata_list
        json_output['duration'] = duration
        json_output['bitrate'] = bitrate.strip()
        json_output['stream0'] = stream0.strip()
        # json_output['stream1'] = stream1.strip()

        return json_output
    except:
        print('-ERR- failed to retrieve metadata')

        return None

def ffvolumedetect(ffmpegPath, audioPath):
    ffmCMD = '%s -i "%s" -af volumedetect -f null /dev/null -hide_banner'%(ffmpegPath, audioPath)
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

def ffastats(ffmpegPath, audioPath):
    ffmCMD = '%s -i "%s" -af astats=measure_perchannel=none -f null -'%(ffmpegPath, audioPath)

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

def set_sound_in_scene(filepath, offset=0):

    context = bpy.context

    filename = os.path.basename(filepath)

    scene = context.scene
    seq = scene.sequence_editor

    if not seq:
        scene.sequence_editor_create()
    for strip in seq.sequences:
        seq.sequences.remove(strip)

    #Will create duplicate datablocks if the same sound is imported multiple times.
    #the "new_sound" command is the only one I could find.
    soundstrip = scene.sequence_editor.sequences.new_sound(filename, filepath, 1, offset)
    soundstrip.show_waveform = True

    return soundstrip

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

def frame_clip_in_sequencer():

    print('-INF- frame_clip_in_sequencer()')

    for my_area in bpy.context.window.screen.areas:


        if my_area.type == 'SEQUENCE_EDITOR':
            for my_region in my_area.regions:

                if my_region.type == 'WINDOW':
                    with bpy.context.temp_override(
                        window = bpy.context.window,
                        area = my_area,
                        region = my_region,
                    ):
                        bpy.ops.sequencer.view_all()
                        bpy.ops.view2d.zoom(deltax=0.0, deltay=30, use_cursor_init=False)
                        bpy.ops.view2d.pan(deltax=0, deltay=-99999999)
                        bpy.ops.view2d.pan(deltax=0, deltay=125)
                        bpy.ops.view2d.zoom(deltax=0.0, deltay=-0.5, use_cursor_init=False)

def create_new_object(name, coll=bpy.context.scene.collection):
    mesh = bpy.data.meshes.new(name)
    obj = bpy.data.objects.new(name, mesh)
    coll.objects.link( obj )

    return obj

def generate_spectrogram(stm_obj, audioPath, imagePath, duration_seconds, max_volume_dB, peak_brightness=0):

    print('-INF- updating spectrogram')


    assetFile = bpy.context.scene.assetFilePath

    append_from_blend_file(assetFile, 'NodeTree', 'STM_spectrogram')

    print(f'{stm_obj =}')

    spectro_image = bpy.data.images.load(imagePath, check_existing=True)
    spectro_image.colorspace_settings.name = "sRGB"

    stm_GN = stm_obj.modifiers['STM_spectrogram']
    stm_GN.node_group = bpy.data.node_groups['STM_spectrogram']



    stm_GN["Input_2"] = spectro_image
    stm_GN["Input_45"] = duration_seconds
    stm_GN["Input_60"] = os.path.basename(audioPath)
    stm_GN["Input_64"] = max_volume_dB
    stm_GN["Input_75"] = peak_brightness




    mat_raw = get_stm_material(stm_obj, 'STM_rawTexture')
    mat_gradient = get_stm_material(stm_obj, 'STM_gradient')

    mat = mat_raw if stm_obj.material_type == 'raw' else mat_gradient if stm_obj.material_type == 'gradient' else stm_obj.material_custom

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

    with open(r'%s'%scn.gradient_presets_json_file,'r') as f:
        presets=json.load(f)

        # p = scn.gradient_preset
        p = context.object.presets_gradient.replace('.png', '')
        preset = presets[p]

        mat_gradient = None

        for m in bpy.data.materials:
            if m.get('STM_material_type') and m.get('STM_object'):
                if m['STM_material_type'] == 'STM_gradient' and m['STM_object'] == context.object:
                    mat_gradient = m

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
    print('-INF- reset STM curve')

    with open(r'%s'%bpy.context.scene.eq_curve_presets_json_file,'r') as f:
        presets=json.load(f)


    preset_name = context.scene.presets_eq_curve.replace('.png', '')
    preset = presets[preset_name]



    curve_node = bpy.data.node_groups['STM_spectrogram'].nodes['MACURVE']
    points = curve_node.mapping.curves[0].points

    preset_points = [preset[value] for value in preset]

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

def is_stm_object_selected():

    is_stm = False

    if bpy.context.selected_objects != []:
        if bpy.context.object.type == 'MESH':
            # if bpy.context.object.modifiers.get('STM_spectrogram'):
            if any([m.name.startswith('STM_spectrogram') for m in bpy.context.object.modifiers]):
                is_stm = True

    return is_stm

def update_stm_material(self, context):

    obj = context.object
    assetFile = bpy.context.scene.assetFilePath
    mat = None

    if obj.material_type == 'gradient':
        mat = get_stm_material(obj, 'STM_gradient')

    elif obj.material_type == 'raw':
        mat = get_stm_material(obj, 'STM_rawTexture')

    elif obj.material_type == 'custom':
        mat = obj.material_custom

    obj.modifiers['STM_spectrogram']["Input_12"] = mat

    if obj.data.materials:                      # if obj has slots
        obj.data.materials[0] = mat             # assign to 1st material slot
    else:                                       # else
        obj.data.materials.append(mat)          # append mat

def set_geometry_type(self, context):
    obj = context.object
    obj.modifiers['STM_spectrogram']['Input_48'] = True if obj.geometry_type == 'cylinder' else False

def set_doExtrude(self, context):
    obj = context.object
    obj.modifiers['STM_spectrogram']['Input_52'] = True if obj.doExtrude == 'on' else False

def set_showGrid(self, context):
    obj = context.object
    obj.modifiers['STM_spectrogram']['Input_58'] = True if obj.showGrid == 'on' else False

def set_waveform_style(self, context):
    obj = context.object
    style = obj.waveform_style
    style_arr = ['line', 'dots', 'plane', 'cubes', 'tubes', 'zigzag', 'zigzag_smooth']
    obj.modifiers['STM_waveform']['Input_8'] = style_arr.index(style)

def set_waveform_resolution_choice(self, context):
    obj = context.object

    obj.modifiers['STM_waveform']['Input_17'] = True if obj.waveform_resolution_choice == 'custom' else False

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

    assetFile = bpy.context.scene.assetFilePath
    mat = None

    for m in bpy.data.materials:
        if m.get('STM_material_type') and m.get('STM_object'):
            if m['STM_material_type'] == mat_name and m['STM_object'] == stm_obj:

                print('-INF- found matching rawTexture material to apply, skipping import')
                mat = m

    if mat is None:
        print('-INF- importing new rawTexture material')

        mat = append_from_blend_file(assetFile, 'Material', mat_name, forceImport=True)
        mat['STM_object'] = stm_obj

    if mat_name == 'STM_rawTexture':
        mat.node_tree.nodes['spectro_image'].image = stm_obj.modifiers['STM_spectrogram']['Input_2']


    return mat



def stm_00_ffmetadata():
    obj = bpy.context.object
    scn = bpy.context.scene

    data_raw = ffmetadata(scn.ffmpegPath, scn.audio_file_path)

    if data_raw != None:
        artist = get_first_match_from_metadata(data_raw['metadata'], match='artist')
        album = get_first_match_from_metadata(data_raw['metadata'], match='album', exclude='artist')
        title = get_first_match_from_metadata(data_raw['metadata'], match='title')

    print('artist :', artist)
    print('album :', album)
    print('title :', title)

    scn['title'] = title
    scn['artist'] = artist
    scn['album'] = album

    scn.title = title if title != '' else os.path.basename(scn.audio_file_path)
    scn.album = album if scn.album != '' else '[unkown]'
    scn.artist = artist if artist != '' else '[unkown]'

def stm_01_volume_data():

    obj = bpy.context.object
    scn = bpy.context.scene

    # get peak volume using ffvolumedetect() (less accurate but quicker)

    volume_data_raw = ffvolumedetect(scn.ffmpegPath, scn.audio_file_path)
    max_volume_dB = float(volume_data_raw['max_volume'])
    obj['max_volume_dB'] = max_volume_dB
    print(f'{max_volume_dB = }')



    # get peak volume using ffastats() (more accurate but longer)

    # astats = ffastats(scn.ffmpegPath, scn.audio_file_path)
    # peak_level_dB = round(float(astats['Peak level dB']), 2)
    # obj['peak_level_dB'] = peak_level_dB
    # print(f'{peak_level_dB = }')

def stm_02_generate_spectrogram_img():

    scn = bpy.context.scene
    obj = bpy.context.object

    ffmpegPath = scn.ffmpegPath
    audioPath = scn.audio_file_path
    outputPath = scn.outputPath

    w = 0
    h = 0

    if scn.resolutionPreset == 'custom':
        w = scn.userWidth
        h = scn.userHeight
    else:
        w = int(scn.resolutionPreset.split('x')[0])
        h = int(scn.resolutionPreset.split('x')[1])


    spectrogram_image_path = ffshowspectrumpic(
        ffmpegPath,
        audioPath,
        outputPath,
        width=w,
        height=h,
        scale=scn.spectro_scale,
        fscale=scn.spectro_fscale,
        colorMode=scn.spectro_colorMode,
        drange=scn.spectro_drange,
        limit=obj['max_volume_dB']
    )


    obj['spectrogram_file_path'] = spectrogram_image_path

def stm_03_build_spectrogram():

    scn = bpy.context.scene
    obj = bpy.context.object

    ffmpegPath = scn.ffmpegPath
    audioPath = scn.audio_file_path
    outputPath = scn.outputPath

    # I used to analyze the image brightness to normalize the displacement
    # but I don't need it anymore. Now I just analyze the max volume, and gives it
    # to the ffshowspectrumpic() function.

    # peak_brightness = int(ffsignalstats(scn.ffmpegPath, obj['spectrogram_file_path'], 'YMAX'))
    # obj['peak_brightness'] = peak_brightness

    fps = bpy.context.scene.render.fps

    # generate soundstrip
    soundstrip = set_sound_in_scene(audioPath, 0)
    duration_frames = soundstrip.frame_final_duration
    duration_seconds = duration_frames/fps

    scn.frame_end = duration_frames + fps

    # generate stm_obj
    generate_spectrogram(
            stm_obj=obj,
            audioPath=audioPath,
            imagePath=obj['spectrogram_file_path'],
            duration_seconds=duration_seconds,
            max_volume_dB=obj['max_volume_dB'],
            # peak_brightness=obj['peak_brightness']
        )

def stm_04_cleanup():
    scn = bpy.context.scene

    if scn.force_standard_view_transform:
        print('-INF- setting scene view transform to "Standard"')
        scn.view_settings.view_transform = 'Standard'

    if scn.force_eevee_AO:
        scn.eevee.use_gtao = True


    set_playback_to_audioSync(bpy.context)
    frame_clip_in_sequencer()
    frame_all_timeline()

def stm_05_sleep():
    time.sleep(0.5)
