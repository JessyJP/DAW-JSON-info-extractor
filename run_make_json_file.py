import os
import subprocess

# Set the name of the script file to call
script_name = "make_json_dtb_file.py"

# Get the directory where this script is located
script_directory = os.path.dirname(os.path.abspath(__file__))

# Construct the full path to the script file
script_path = os.path.join(script_directory, script_name)

# Set the directories to process
input_directories = ["./Reaper-Projects/", "./Test-DAW-Projects/"]
output_directory = "./database_files"

# Loop over the directories
for directory in input_directories:
    # Call the script file as a subprocess with the specified arguments
    subprocess.call(["python", script_path, "--outdir", output_directory, "--autolist", directory])
#end