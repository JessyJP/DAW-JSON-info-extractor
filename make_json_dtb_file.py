"""
Author: JessyJP
Date: May 18, 2023

Summary:
This script is designed to process directories that contain Digital Audio Workstation (DAW) projects. 
For each identified project, it generates a JSON file capturing the project's metadata including UUID, 
file structure, project name, associated media files, and additional information extracted from the DAW project file.
The script supports customization through command-line arguments to specify the output directory for JSON files, 
process a specific directory, and consolidate all generated metadata into a single JSON file.

License: MIT License
"""

import os
import json
import argparse
import csv
import time
import uuid
import shutil

from daw_file_processor import *
from repository_handling import *


## =-------------------------------------------------------------------=##

def update_or_create_json_file(prjPath):

    # Locate or create the database file name
    prefix = "DAW-REPO"
    rood_dir = get_project_root(prjPath)
    ext = "json"
    # Create a JSON file containing information about a prjPath directory.
    UID = find_existing_uuid(prjPath, f'{prefix}.{rood_dir}.*.{ext}')
    if not UID:
        UID = str(uuid.uuid4())
    #end
    json_filename = os.path.join(args.outdir, f'{prefix}.{rood_dir}.{UID}.{ext}')

    # Get other Parameters
    mod_time = os.path.getmtime(prjPath)
    upload_date = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(mod_time))
    daw_project_filename = get_project_name(prjPath)
    full_project_file_path = (os.path.join(prjPath, daw_project_filename))#os.path.abspath
    full_project_file_path = full_project_file_path.replace("\\", "/")

    # Compose the dictionary for the database file
    data = {
        "uuid": UID, # Add this line to generate a unique identifier
        "language": "english",
        "author": "current-user",#author_or_songwriter or composer
        "album": "no album",# Album/Opus/Group etc
        "song": rood_dir,# Or piece name
        "style": "generic",
        "upload_date": upload_date,
        "thumbnail": get_project_thumbnail(prjPath),
        "intention": "",
        "root": rood_dir,
        "daw_project_filename": daw_project_filename,
        "relative_path": get_relative_path(prjPath),
        "directory_tree": get_directory_tree_asDictionary(prjPath),
        "filepath_list":  get_filepath_list(prjPath),
        "stereo_mixdown": get_stereo_mix(prjPath,[rood_dir,daw_project_filename.split(".")[0]]),
        "stems": get_stems(prjPath, ["stems", "render"]),
        "video": get_video_file_with_keywords(prjPath),
        "score": get_score_file(prjPath),
        "lyrics":"",
        "daw_project_info": get_daw_project_info(full_project_file_path)
    }
    
    # Open and save the file
    with open(json_filename, 'w') as f:
        json.dump(data, f, indent=4)
        f.write("\n")
    #end

    # Copy the JSON file to the original project directory
    destination_filename = os.path.join(prjPath, f'{prefix}.{rood_dir}.{UID}.{ext}')
    shutil.copy2(json_filename, destination_filename)
    
    print(f'Processed directory: {prjPath}    <+==+>    {json_filename}')
#end

## =-------------------------------------------------------------------=##

def read_daw_info():
    # This function reads the daw_info.csv and returns a dictionary
    # where the key is the DAW name and the value is a list of extensions for that DAW.
    
    # Get the directory where this script is located
    dawINFO_csv = os.path.dirname(os.path.abspath(__file__))
    dawINFO_csv = os.path.join(dawINFO_csv,'daw_info.csv')

    daw_info = {}
    with open(dawINFO_csv, 'r') as file:
        reader = csv.reader(file)
        next(reader)  # skip header
        for row in reader:
            daw_name = row[0]
            extensions = [ext.lower() for ext in row[1:]]
            daw_info[daw_name] = extensions
        #end
    #end
    return daw_info
#end

def locate_project_directories(directories):
    # Prune a list of directory paths based on certain criteria.
    pruned_directories = []
    daw_info = read_daw_info()
    for directory in directories:
        # Check if the deepest directory level is hidden
        deepest_directory = os.path.basename(directory)
        # deepest_directory = directory.split('/')[-1]
        if deepest_directory.startswith('.'):
            # Ignore hidden directories
            continue
        # Ignore directories specified in the user-defined list
        elif deepest_directory.lower() in ['backup', 'backups', 'do_not_process']:
            continue
        #end
        # Check if the directory contains a project file
        if check_for_project_directory(directory, daw_info):
            pruned_directories.append(directory)
        #end
    #end
    return pruned_directories
#end

## =-------------------------------------------------------------------=##
if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Process directories.')
    parser.add_argument('--outdir', metavar='dir', type=str, default='database_files',
                        help='output directory for the database files')
    parser.add_argument('--onefile', metavar='filename', type=str,
                        help='save all JSON data to a single file')
    parser.add_argument('--autolist', metavar='dir', type=str,
                        help='automatically find subdirectories of the given path')
    args = parser.parse_args()

    # Create the output directory if it doesn't exist
    os.makedirs(args.outdir, exist_ok=True)

    if args.autolist:
        directories = [os.path.join(args.autolist, d) for d in os.listdir(args.autolist) if os.path.isdir(os.path.join(args.autolist, d))]
        pruned_directories = locate_project_directories(directories)
    else:
        parser.add_argument('directories', metavar='dir', type=str, nargs='+',
                            help='an integer for the accumulator')
        args = parser.parse_args()
        pruned_directories = locate_project_directories(args.directories)
    #end

    for directory in pruned_directories:
        # Create a new JSON file or update it for each directory
        update_or_create_json_file(directory)
    #end

    if args.onefile:
        # Combine all JSON data into a single file
        output_filename = os.path.join(args.outdir, args.onefile)
        json_data = []
        for directory in pruned_directories:
            json_filename = os.path.join(args.outdir, f'{get_project_root(directory)}.json')
            with open(json_filename, 'r') as f:
                data = json.load(f)
                json_data.append(data)
            #end
        #end
        with open(output_filename, 'w') as f:
            json.dump(json_data, f, indent=4)
            f.write("\n")
        #end
    #end
#end