# prefbak
## Overview
=

## System Requirements



## Installation
- Clone/download this repo to your local machine
- cd to the directory of the downloaded project repo
- Run the script `setup-linux.sh` or `setup-windows.ps1` 

## Configuration
All files will be stored in the backupRootDir. A subfolder is created in the root dir with the name 
of rule as set in the config.

rsync: path given with be copied/synced to the rule subfolder, overwriting existing files

tar: path will be archived to tar file and named like: "[YYYY-MM-dd HH.mm.ss] file-or-folder-name.tar" 
Use this option to preserve file permissions.

Set the "backupFilePermissions" to change permissions on the backed up files after backup is complete.


Config file components:
- global
--- powershellFilepath
--- 7zipFilepath
- rules

## Use
cd to the directory of the downloaded project repo and run the backup script with the following:

### For Linux systems:
```
sudo py-venv-linux/bin/python3 sudo prefbak.py machineName
```

### For Windows systems:
```
.\py-venv-windows\Scripts\python.exe prefbak.py copper
```

Replace "machineName" with the name of the machine to run the backup routine for. This is the same name you used in the name of the machine's backup config file name.
We run the Python script as sudo so that backups can be made of any file or directory on the machine regardless of file permissions.

Prerun scripts can optionally be written. Place them in the `machine-backup-prep-scripts` dir in this project, named like `backup-prep-hostname.sh` (Linux) or `backup-prep-hostname.ps1` (Windows). They will be automatically run before the backup tasks. These scripts are optional: create and use them if you need to perform some tasks in advance of the backup, such as creation of SQL dumps that you'd like to backup, for example. 