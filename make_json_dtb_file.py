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
import imghdr
import fnmatch
import shutil

from get_file_lists_by_type_module import *
from daw_file_processor import *

## =-------------------------------------------------------------------=##

def get_project_root(prjPath):
    # Get the project root name from a prjPath directory path.
    return os.path.basename(prjPath)
#end

def get_project_name(prjPath):
    # Get the project name from a prjPath directory path.
    extensions = get_all_DAW_extensions()
    for filename in os.listdir(prjPath):
        filename_lower = filename.lower()
        for ext in extensions:
            if filename_lower.endswith(ext):
                return filename
            #end
        #end
    #end
    return ""
#end

def get_stems(prjPath, subdir_names):
    for name in os.listdir(prjPath):
        full_path = os.path.join(prjPath, name)
        if os.path.isdir(full_path):
            if name.lower() in subdir_names:
                return name#full_path.replace("\\", "/")
            #end
        #end
    #end
    # TODO: improve this function
    return ""
#end

def get_directory_tree_asDictionary(rootPath):
    # Get a dictionary representing the directory tree of a directory path.
    tree = {"": []}
    for f in os.listdir(rootPath):
        full_path = os.path.join(rootPath, f)
        if os.path.isfile(full_path):
            # Add file to the current directory's list of files
            tree[""].append(os.path.relpath(full_path, rootPath))
        elif os.path.isdir(full_path):
            # Recursively add subdirectory tree
            subtree = get_directory_tree_asDictionary(full_path)
            # Add subdirectory tree to the current directory's dictionary
            tree[f] = subtree
        #end
    #end
    return tree
#end

def get_filepath_list(rootPath, followlinks=False):
    filepaths = []

    # os.walk yields a tuple containing the path to the directory, 
    # as well as lists of its subdirectories and files
    for dirpath, dirnames, filenames in os.walk(rootPath, followlinks=followlinks):
        for file in filenames:
            # os.path.join() creates the full relative path
            full_path = os.path.join(dirpath, file)
            filepaths.append(full_path)
        #end
    #end
    return filepaths
#end

def get_directory_tree_asList(rootPath):
    """
    Get a nested list representing the directory tree of a directory path.
    """
    tree = []
    for f in os.listdir(rootPath):
        full_path = os.path.join(rootPath, f)
        if os.path.isfile(full_path):
            # Add file to the current directory's list of files
            tree.append(f)
        elif os.path.isdir(full_path):
            # Recursively add subdirectory tree
            subtree = get_directory_tree_asList(full_path)
            # Add subdirectory tree to the current directory's list
            tree.append({f : subtree})
        #end
    #end
    return tree
#end

def get_project_thumbnail(prjPath):
    # Get the project thumbnail file path from a prjPath directory.
    image_files = [f for f in os.listdir(prjPath) if os.path.isfile(os.path.join(prjPath, f)) and imghdr.what(os.path.join(prjPath, f)) is not None]
    thumbnail_files = [f for f in image_files if "thumbnail" in f.lower()]
    if thumbnail_files:
        return thumbnail_files[0]
    elif image_files:
        return image_files[0]
    else:
        return ""
    #end
#end

def get_relative_path(prjPath):
    # Get the relative path of a prjPath with respect to the script path.
    script_path = os.path.dirname(os.path.realpath(__file__))
    try:
        return os.path.relpath(prjPath, script_path)
    except ValueError:
        # If a relative path cannot be calculated (e.g., across different drives),
        # return the absolute path instead.
        return prjPath#os.path.abspath(prjPath)
    #end
#end

def get_stereo_mix(prjPath,extraKeywords):
    audio_files = get_list_of_audio_files(prjPath)
    keywords = set(['mix', 'stereo', 'render']+extraKeywords)
    for filename in audio_files:
        if any(keyword in filename.lower() for keyword in keywords):
            return filename
        #end
    #end
    return ""
#end

def get_video_file_with_keywords(prjPath, keywords=""):
    # Get a list of all video files in the prjPath
    video_files = get_list_of_video_files(prjPath)

    # Look for video files that match the criteria
    for filename in video_files:
        if any(keyword in filename.lower() for keyword in keywords):
            return filename
        #end
    #end

    if len(video_files) == 1:
        return video_files[0]
    #end

    if len(video_files) > 1:
        return video_files
    #end

    # Look for video.url file and get the link from it
    video_url_file = os.path.join(prjPath, "video.url")
    if os.path.isfile(video_url_file):
        with open(video_url_file, 'r') as f:
            video_url = f.read().strip()
            video_url = "http" + video_url.split("http")[1]
            if video_url:
                return video_url
            #end
        #end
    #end

    # If no video files match the criteria or video.url file is found, return an empty string
    return ""
#end

def get_score_file(prjPath):
    # Get a list of all score files in the prjPath
    score_files = get_list_of_score_files(prjPath)

    # If there are multiple score files, return the list of files
    if len(score_files) > 1:
        return score_files

    # If there is only one score file, return it as a single string
    elif len(score_files) == 1:
        return score_files[0]
    #end

    # If no score files are found, return an empty string
    return ""
#end

def find_existing_uuid(directory, pattern):
    for filename in os.listdir(directory):
        if fnmatch.fnmatch(filename, pattern):
            # Assuming UUID is after the second dot and before the extension
            uuid = filename.split('.')[2]
            return uuid
        #end
    #end
    return None
#end

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

def check_for_project_directory(prjPath, daw_info):
    # This function checks if the prjPath contains a file with a DAW extension.
    for filename in os.listdir(prjPath):
        _, extension = os.path.splitext(filename)
        extension = extension.lower()  # consider extensions in any capitalization
        for daw_extensions in daw_info.values():
            if extension in daw_extensions:
                return True
            #end
        #end
    #end
    return False
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