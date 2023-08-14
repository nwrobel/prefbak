# prefbak
## Overview
This is a tool that allows you to properly backup your application data and other desired files for one or more machines. 
It allows desired backups for each machine to be configured in advance so that backup routines of all critical files can be run easily with few commands.
Backups will preserve the original Unix file permissions (owner, group, mask) of each source file or directory.
The tool will create an archive file for each file or folder configured to be backed up and store it at the configured location. The archive file consists of the file/directory compressed as a .tar archive, which is then compressed as a 7z archive. 
The inner .tar archive is necessary to preserve the file permissions.

## System Requirements
- OS: Linux or Windows (tested on Ubuntu 18.04 and Windows 10)
- 7zip must be installed and added to the system path


## Installation
- Clone/download this repo to your local machine
- cd to the directory of the downloaded project repo
- Run the script `setup-linux.sh` or `setup-windows.ps1` 

## Configuration
This tool can be configured to perform backups for one or more machines. Files to include in the backup of a machine are managed by a Json config file for that machine. For each machine that you want backed up, create a file in the `machine-config` dir of the project named "hostname.config.json", where "hostname" is the name of the machine.
See the example template backup config file `yourMachineName.config.json`, included by default with the project, for reference on how to structure the JSON file.

"prepScript" - true/false whether or not a prerun script exists and should be run for this machine ()
"backupDataPermissions" - file permissions that the backup files, stored in backupRootDir, should be set to so that they can be accessed - do not include this value(s) if backing up a Windows system
"backupRules" - array of rules, each one has 2 values: "sourcePath" for the path of the source file or directory on the machine, and "backupPath" for the path of where the backup of the source path should be stored

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