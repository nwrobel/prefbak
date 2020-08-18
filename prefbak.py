import csv
import shutil
import os
import json
import subprocess
from pathlib import Path
import datetime



# TODO: update code to use rsync command to backup/restore data from source to target backup path

# def readCsvFile(filepath):
#     '''
#     Returns a list of dictonaries representing each data row of the CSV file. The key names are 
#     defined by the CSV header row (1st line).
#     '''
#     data = []
#     with open(filepath, 'r') as csvFileHandle:
#         csvFile = csv.DictReader(csvFileHandle)
#         for row in csvFile:
#             data.append(dict(row))

#     return data

# def copyPath(sourcePath, destinationPath):
#     '''
#     Copies the given file or directory to the specified destination location. File metadata is preserved and
#     directories are copied recursively. If the destination currently exists, it will be deleted first (overwritten).
    
#     The destination can be either a directory path or a filepath. If a file is given for the source, the destination
#     must be a filepath. If a directory is given for the source, the desintation must be a directory path.
#     '''
#     # delete existing backup destination if it exists
#     if (os.path.exists(destinationPath)):
#         deletePath(destinationPath)
#         print("Deleting existing file and copying new: {}".format(destinationPath))

#     if (os.path.isdir(sourcePath)):
#         shutil.copytree(sourcePath, destinationPath)
#     else:
#         shutil.copy2(sourcePath, destinationPath)

# def deletePath(path):
#     '''
#     Deletes the given file or directory at the specified path. Directories are deleted recursively.
#     '''
#     if (os.path.isdir(path)):
#         shutil.rmtree(path)
#     else:
#         os.remove(path)

def getCurrentTimestamp():
    """
    Returns the current time as an epoch timestamp.
    """
    dt = datetime.datetime.now()
    return datetime.datetime.timestamp(dt)

def formatTimestampForDisplay(timestamp):
    """
    Converts a given epoch timestamp value to a string timestamp format that can be displayed and 
    easily understood. Output format example: "2012-01-27 02:29:33". Hours will be represented on a
    24-hour clock. 
    
    Since epoch timestamps are given in time relative to GMT, the formatted time 
    returned will be adjusted according to the current timezone by adding hours, so that the correct
    time according to the current location is returned.
    
    If the given epoch timestamp contains a fractional (decimal) part, it will be rounded to remove 
    it so it can be displayed in the output format YYYY-MM-DD HH-MM-SS. 
    Timestamps in this format are not meant to be used for precise calculations. Instead, use the
    original epoch timestamp values, which may include fractional/decimal seconds.
    """
    roundedTimestamp = round(timestamp)
    dt = datetime.datetime.fromtimestamp(roundedTimestamp)
    formattedTime = datetime.datetime.strptime(str(dt), "%Y-%m-%d %H:%M:%S")
    return str(formattedTime)

def getCurrentFormattedTime():
    '''
    Returns the current time, formatted to look pretty for display purposes.
    Output format example: "2012-01-27 02:29:33". Hours will be represented on a
    24-hour clock. 
    
    Since epoch timestamps are given in time relative to GMT, the formatted time 
    returned will be adjusted according to the current timezone by adding hours, so that the correct
    time according to the current location is returned.
    
    If the given epoch timestamp contains a fractional (decimal) part, it will be rounded to remove 
    it so it can be displayed in the output format YYYY-MM-DD HH-MM-SS. 
    Timestamps in this format are not meant to be used for precise calculations. Instead, use the
    original epoch timestamp values, which may include fractional/decimal seconds. 
    '''
    return formatTimestampForDisplay(getCurrentTimestamp())

def getCurrentTimestampForFilename():
    '''
    Returns the current time, formatted in such a way as to allow it to be used as a string in file
    names. This is useful for applying archive timestamps to files through their name.
    '''
    timeForFilename = getCurrentFormattedTime().replace(':', '_')
    return timeForFilename

def compressDirectory(archiveFilepath, dirToCompress):

    sevenZipArgs = ['7z', 'a', '-t7z', '-mx=9', '-mfb=64', '-md=64m', archiveFilepath, dirToCompress]
    subprocess.call(sevenZipArgs)

def getFileBaseName(filePath):
    '''
    Returns the "base" name of the file, given the filepath. The base name is the filename minus the
    file's extension. 
    ex) C:\data\playlist.m3u.tar --> playlist.m3u
    ex) C:\prog\connect.log --> connect
    '''
    filePathObject = Path(filePath)
    return filePathObject.stem

def joinPaths(path1, path2):
    '''
    Given a root absolute filepath and a child relative filepath, returns the effective combination
    of these two paths to make a 3rd filepath.

    ex) JoinPaths("C:\prog\temp", "..\test.txt") --> "C:\prog\test.txt" 
    '''
    joined = os.path.join(path1, path2)
    return os.path.abspath(joined)

def getComputerName():
    pass


def readJsonFile(filepath):
    with open(filepath) as f:
        data = json.load(f)

    return data

def performBackupStep(sourcePath, destinationPath, compress=False):

    if (compress):
        print('compress')
        archiveName = '[{}] {}.backup.7z'.format(getCurrentTimestampForFilename(), getFileBaseName(sourcePath)) 
        archiveDestFilepath = joinPaths(destinationPath, archiveName)
        compressDirectory(archiveDestFilepath, dirToCompress=sourcePath)

    else:
        # sourcePath = '\"' + sourcePath + '\"'
        # destinationPath = '\"' + destinationPath + '\"' 
        subprocess.call(['rsync', '-avh', '--delete', sourcePath, destinationPath])


    # sudo rsync -avz --delete /etc/mpd.conf /datastore/nick/Device\ \&\ App\ Backups/zinc/AppData/_test/

if __name__ == "__main__":

    # push (backup)
    computerName = 'zinc'
    backupRootDir = '/datastore/nick/Device & App Backups/zinc'

    # push (make the backup)
    if (computerName == 'zinc'):
        backupConfig = readJsonFile('zinc.config.json')

        for backupConfigEntry in backupConfig:
            sourcePath = backupConfigEntry['sourcePath']
            destinationPath = joinPaths(backupRootDir, backupConfigEntry['backupPath'])
            compressBackup = backupConfigEntry['compress']

            if (compressBackup == 'yes'):
                performBackupStep(sourcePath, destinationPath, compress=True)
            else:
                performBackupStep(sourcePath, destinationPath)







    