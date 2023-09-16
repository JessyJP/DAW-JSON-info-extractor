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

from get_file_lists_by_type_module import get_all_DAW_extensions, get_list_of_audio_files, \
                                          get_list_of_video_files, get_list_of_score_files


## =-------------------------------------------------------------------=##


def get_filepath_list(rootPath, followlinks=False):
    filepaths = []

    # os.walk yields a tuple containing the path to the directory, 
    # as well as lists of its subdirectories and files
    for dirpath, dirnames, filenames in os.walk(rootPath, followlinks=followlinks):
        dirpath = dirpath.replace(rootPath,'')
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

def get_relative_path(prjPath):
    # Get the relative path of a prjPath with respect to the script path.
    script_path = os.path.dirname(os.path.realpath(__file__))
    try:
        return os.path.relpath(prjPath, script_path).replace("\\", "/")
    except ValueError:
        # If a relative path cannot be calculated (e.g., across different drives),
        # return the absolute path instead.
        return prjPath.replace("\\", "/")#os.path.abspath(prjPath)
    #end
#end

## =-------------------------------------------------------------------=##

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

def get_project_root(prjPath):
    # Get the project root name from a prjPath directory path.
    return os.path.basename(prjPath)
#end

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