import os
import csv

def get_daw_name(daw_project_filename):
    # Get the DAW name based on the project file extension.

    # Get the directory where this script is located
    dawINFO_csv = os.path.dirname(os.path.abspath(__file__))
    dawINFO_csv = os.path.join(dawINFO_csv,'daw_info.csv')

    extension = os.path.splitext(daw_project_filename)[1].lower()
    with open(dawINFO_csv, 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            if extension in row['extension'].split(','):
                return row['name']
            #end
        #end
    #end
    return 'Unknown'
#end


def get_daw_project_info(daw_project_file):
    # Get information about a DAW project file.
    daw_name = get_daw_name(daw_project_file)

    if daw_name == 'Reaper':
        return get_reaper_info(daw_project_file)
    elif daw_name == 'Pro Tools':
        return get_pro_tools_info(daw_project_file)
    elif daw_name == 'Ableton Live':
        return get_ableton_live_info(daw_project_file)
    elif daw_name == 'Logic Pro X':
        return get_logic_pro_x_info(daw_project_file)
    elif daw_name == 'Cubase':
        return get_cubase_info(daw_project_file)
    elif daw_name == 'FL Studio':
        return get_fl_studio_info(daw_project_file)
    elif daw_name == 'Reason':
        return get_reason_info(daw_project_file)
    elif daw_name == 'Nuendo':
        return get_nuendo_info(daw_project_file)
    elif daw_name == 'Bitwig Studio':
        return get_bitwig_studio_info(daw_project_file)
    elif daw_name == 'GarageBand':
        return get_garageband_info(daw_project_file)
    elif daw_name == 'Studio One':
        return get_studio_one_info(daw_project_file)
    elif daw_name == 'Mixcraft':
        return get_mixcraft_info(daw_project_file)
    elif daw_name == 'Cakewalk Sonar':
        return get_sonar_info(daw_project_file)
    elif daw_name == 'Digital Performer':
        return get_digital_performer_info(daw_project_file)
    elif daw_name == 'Ardour':
        return get_ardour_info(daw_project_file)
    elif daw_name == 'Magix Music Maker':
        return get_music_maker_info(daw_project_file)
    elif daw_name == 'MuLab':
        return get_mulab_info(daw_project_file)
    elif daw_name == 'Audacity':
        return get_audacity_info(daw_project_file)
    elif daw_name == 'N-Track Studio':
        return get_n_track_info(daw_project_file)
    elif daw_name == 'OpenMPT':
        return get_openmpt_info(daw_project_file)
    elif daw_name == 'Renoise':
        return get_renoise_info(daw_project_file)
    elif daw_name == 'Rosegarden':
        return get_rosegarden_info(daw_project_file)
    elif daw_name == 'Samplitude':
        return get_samplitude_info(daw_project_file)
    elif daw_name == 'Sibelius':
        return get_sibelius_info(daw_project_file)
    elif daw_name == 'Tracktion':
        return get_tracktion_info(daw_project_file)
    elif daw_name == 'Zune Playlist':
        return get_zune_playlist_info(daw_project_file)
    else:
        # If the DAW is not supported, return a field indicating that it is
        return {"daw_not_supported": "yes"}
    #end
#end


## ==================== Supported DAW(s) ================================
# Reaper 
def get_reaper_info(daw_project_file):
    # Get information about a Reaper project file.
    if not daw_project_file.lower().endswith('.rpp'):
        return {}
    #end

    # Parse the project file using the SWS/S&M extension for Reaper.
    try:
        import reapy
    except ImportError:
        return {}
    #end
    # TODO: due to error for now return this 
    return {"daw_name": "Reaper","notes":"FILE NOT SUPPORTED!"}
    with reapy.Project(daw_project_file) as project:
        if not project.is_open():
            return {}
        #end

        # Get the tempo and time signature of the project.
        tempo = project.tempo
        time_signature = f"{project.time_signature_numerator}/{project.time_signature_denominator}"

        # Get the markers of the project.
        markers = []
        for i, marker in enumerate(project.markers):
            markers.append({"name": marker.name, "time": marker.position})
        #end
        for i, region in enumerate(project.regions):
            markers.append({"name": region.name, "time": region.position})
        #end

        # Get a list of all FX in the project.
        fx_list = []
        for track in project.tracks:
            for fx in track.fx:
                fx_list.append({"name": fx.name, "parameters": fx.parameters})
            #end
        #end

        return {"daw_name": "Reaper", "tempo": tempo, "time_signature": time_signature, "markers": markers, "fx_list": fx_list}
    #end
#end


# Pro Tools
def get_pro_tools_info(daw_project_file):
    # Get information about a Pro Tools project file.
    if not daw_project_file.lower().endswith('.ptx'):
        return {}
    #end

    # Parse the project file using the AAF SDK for Pro Tools.
    try:
        import aaf2
    except ImportError:
        return {}
    #end

    with aaf2.open(daw_project_file, 'r') as f:
        if not f:
            return {}
        #end

        # Get the tempo and time signature of the project.
        tempo = f.metadict()['Application Tape Name'].value
        time_signature = f.metadict()['Start Time'].value

        # Get the markers of the project.
        markers = []
        for track in f.content.toplevel()['Timecode Tracks'].values():
            for edit in track['Segment'].values():
                if 'Comment' in edit['ComponentData'].keys():
                    markers.append({"name": edit['ComponentData']['Comment'].value, "time": edit['ComponentData']['Position'].value})
                #end
            #end
        #end

        return {"daw_name": "Pro Tools", "tempo": tempo, "time_signature": time_signature, "markers": markers}
    #end
#end


# Pro Tools
def get_pro_tools_info2(daw_project_file):
    # Get information about a Pro Tools project file.
    if not daw_project_file.lower().endswith('.ptx'):
        return {}
    #end

    # Parse the project file using the Pro Tools SDK.
    try:
        import avid
    except ImportError:
        return {}
    #end

    project = avid.AvidProject()
    if not project.load(daw_project_file):
        return {}
    #end

    # Get the tempo and time signature of the project.
    tempo = project.get_tempo()
    time_signature = f"{project.get_time_signature_numerator()}/{project.get_time_signature_denominator()}"

    # Get the markers of the project.
    markers = []
    for i in range(project.get_num_markers()):
        marker_name = project.get_marker_name(i)
        marker_time = project.get_marker_time(i)
        markers.append({"name": marker_name, "time": marker_time})
    #end

    # Get a list of all plugins in the project.
    plugin_list = []
    for i in range(project.get_num_plugins()):
        plugin_name = project.get_plugin_name(i)
        plugin_params = project.get_plugin_parameters(i)
        plugin_list.append({"name": plugin_name, "parameters": plugin_params})
    #end

    return {"daw_name": "Pro Tools", "tempo": tempo, "time_signature": time_signature, "markers": markers, "plugin_list": plugin_list}
#end


# Ableton Live
def get_ableton_live_info(daw_project_file):
    # Get information about an Ableton Live project file.
    if not daw_project_file.lower().endswith('.als'):
        return {}
    #end

    # Parse the project file using the Live API.
    try:
        import ableton
    except ImportError:
        return {}
    #end

    project = ableton.AbletonProject()
    if not project.load(daw_project_file):
        return {}
    #end

    # Get the tempo and time signature of the project.
    tempo = project.get_tempo()
    time_signature = f"{project.get_time_signature_numerator()}/{project.get_time_signature_denominator()}"

    # Get the markers of the project.
    markers = []
    for i in range(project.get_num_markers()):
        marker_name = project.get_marker_name(i)
        marker_time = project.get_marker_time(i)
        markers.append({"name": marker_name, "time": marker_time})
    #end

    # Get a list of all devices in the project.
    device_list = []
    for track in project.get_tracks():
        for device in track.get_devices():
            device_name = device.get_name()
            device_params = device.get_parameters()
            device_list.append({"name": device_name, "parameters": device_params})
        #end
    #end

    return {"daw_name": "Ableton Live", "tempo": tempo, "time_signature": time_signature, "markers": markers, "device_list": device_list}
#end


def get_ableton_live_info2(daw_project_file):
    # Get information about an Ableton Live project file.
    if not daw_project_file.lower().endswith('.als'):
        return {}
    #end

    try:
        from ableton_project import AbletonProject
    except ImportError:
        return {}
    #end

    with AbletonProject(daw_project_file) as project:
        if not project.is_valid():
            return {}
        #end

        # Get the tempo and time signature of the project.
        tempo = project.tempo
        time_signature = f"{project.time_signature_numerator}/{project.time_signature_denominator}"

        # Get the markers of the project.
        markers = []
        for marker in project.markers:
            markers.append({"name": marker.name, "time": marker.time})
        #end

        # Get a list of all devices in the project.
        device_list = []
        for device in project.devices:
            device_list.append({"name": device.name, "parameters": device.parameters})
        #end

        return {"daw_name": "Ableton Live", "tempo": tempo, "time_signature": time_signature, "markers": markers, "device_list": device_list}
    #end
#end


# Logic Pro X
def get_logic_pro_x_info(daw_project_file):
    # Get information about a Logic Pro X project file.
    if not daw_project_file.lower().endswith('.logicx'):
        return {}
    #end

    # Parse the project file using the plistlib module.
    try:
        import plistlib
    except ImportError:
        return {}
    #end

    with open(daw_project_file, 'rb') as f:
        plist = plistlib.load(f)

        # Get the tempo and time signature of the project.
        tempo = plist['Tempo']
        time_signature = f"{plist['NumericalTimeSignature'][0]}/{plist['NumericalTimeSignature'][1]}"

        # Get the markers of the project.
        markers = []
        for marker in plist['Markers']:
            markers.append({"name": marker['Name'], "time": marker['Time']})
        #end

        return {"daw_name": "Logic Pro X", "tempo": tempo, "time_signature": time_signature, "markers": markers}
    #end
#end


# Cubase
def get_cubase_info(daw_project_file):
    # Get information about a Cubase project file.
    if not daw_project_file.lower().endswith('.cpr'):
        return {}
    #end

    # Parse the project file using the xml.etree.ElementTree module.
    try:
        import xml.etree.ElementTree as ET
    except ImportError:
        return {}
    #end

    with open(daw_project_file, 'r') as f:
        tree = ET.parse(f)
        root = tree.getroot()

        # Get the tempo and time signature of the project.
        tempo_node = root.find(".//Tempo[@UseMusicalTimeBase='true']")
        tempo = float(tempo_node.get('Value'))
        time_signature_node = root.find(".//TimeSignature[@UseMusicalTimeBase='true']")
        time_signature = f"{time_signature_node.get('Numerator')}/{time_signature_node.get('Denominator')}"

        # Get the markers of the project.
        markers = []
        for marker_node in root.findall(".//Marker[@UseMusicalTimeBase='true']"):
            markers.append({"name": marker_node.get('Name'), "time": float(marker_node.get('Position'))})
        #end

        return {"daw_name": "Cubase", "tempo": tempo, "time_signature": time_signature, "markers": markers}
    #end
#end


# FL Studio
def get_fl_studio_info(daw_project_file):
    # Get information about a FL Studio project file.
    if not daw_project_file.lower().endswith('.flp'):
        return {}
    #end

    # Parse the project file using the xml.etree.ElementTree module.
    try:
        import xml.etree.ElementTree as ET
    except ImportError:
        return {}
    #end

    with open(daw_project_file, 'r') as f:
        tree = ET.parse(f)
        root = tree.getroot()

        # Get the tempo and time signature of the project.
        tempo = float(root.find("./MasterTrack/Tempo").text)
        time_signature_node = root.find("./MasterTrack/TimeSignature")
        time_signature = f"{time_signature_node.get('Num')}/{time_signature_node.get('Den')}"

        # Get the markers of the project.
        markers = []
        for marker_node in root.findall("./Playlist/Pattern/Channel[@name='Marker']"):
            markers.append({"name": marker_node.get('text'), "time": float(marker_node.get('pos'))})
        #end

        return {"daw_name": "FL Studio", "tempo": tempo, "time_signature": time_signature, "markers":markers}
    #end
#end