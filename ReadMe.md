# DAW Project Processor

This repository contains a Python script for processing directories that contain Digital Audio Workstation (DAW) projects. For each identified project, it generates a JSON file capturing the project's metadata. This includes project UUID, file structure, project name, associated media files, and additional details extracted directly from the DAW project file.

## Key Features

- Generate a unique UUID for each project
- Extract metadata from DAW project files
- Generate a list of all files in the project directory
- Locate associated media files (e.g., audio, video, score)
- Generate JSON output files for each processed directory
- Option to consolidate all JSON outputs into a single file

## Usage

The script can be executed from the command line with the following options:

- `--outdir [directory]`: Specify the output directory for the generated JSON files
- `--onefile [filename]`: Consolidate all JSON data into a single file
- `--autolist [directory]`: Automatically process all subdirectories of the given directory

If no directory is provided, the script will process the current working directory.

```bash
python3 daw_project_processor.py --outdir database_files --autolist /path/to/your/daw/projects
```

## License
Author: JessyJP  
This project is licensed under the terms of the MIT License.