# prefbak
## Overview
Tool that allows you to automate backups of your application data and other desired files.

## System Requirements
- OS: Linux or Windows (tested on Ubuntu and Windows 10)
Make sure python3 is installed

If Windows, script will use robocopy to sync files.
Otherwise, uses rsync

## Installation
- Clone/download this repo to your local machine
- cd to the directory of the downloaded project repo
- Run the script `setup-linux.sh` or `setup-windows.ps1` 

## Configuration
Create your config file in `(project-root)/machine-config`
Use `hostname.config.json` for template.

Create additional Powershell (Windows) or bash (Linux) script files that you want to run, to reference in your config (optional) - place them in `(project-root)/machine-scripts`

set config file values: 
- `destinationRootDir`: default root directory of your backups
- `powershellFilepath`: set if you have a non-default powershell exe path
- `rsyncFilepath`: set if you have a non-default rsync binary path
- `initScript`: script to run before any rules process (name/subpath of script file in machine-scripts) 
- `postScript`: script to run after rules process (name/subpath of script file in machine-scripts) 
- `rules`: array of rule objects specifying a file copy process
  - `name`: identifier to give to the rule
  - `initScript`: script to run before this rule process (name/subpath of script file in machine-scripts) 
  - `postScript`: script to run after this rule process (name/subpath of script file in machine-scripts) 
  - `files`: array of source/dest configs
    - `sourcePath`: any path - if file, it is copied (overwrite) - if dir, the contents are copied (mirror)
    - `destinationSubDir`: store in the default root dir in this subdir (name or partial path)
    - `destinationDir`: store in this exact dir 


## Use
Make sure to activate the virtualenv:
- Windows
```
.\py-venv-windows\Scripts\activate
```

- Linux
```
source py-venv-linux/bin/activate
```

To list configured rules:
```
python main.py "hostname.config.json" --list-rules
```

To run all configured rules:
```
python main.py "hostname.config.json" --run-all
```

To run specific rules:
```
python main.py "hostname.config.json" --run-rules bashrc vim
```