'''
Script that performs a "prefbak" routine: that is, performs a backup of a machine according to the
backup rules defined in that machine's prefbak config file.
'''

import tarfile
import subprocess
import glob
import os

from com.nwrobel import mypycommons
import com.nwrobel.mypycommons.file
import com.nwrobel.mypycommons.time
import com.nwrobel.mypycommons.logger

archiveInternalFileContainerName = "archiveInternalFileContainer.tar"
archiveFileNameSuffix = ".archive.tar.7z"

def getProjectLogsDir():
    currentDir = mypycommons.file.getThisScriptCurrentDirectory()
    logsDir = mypycommons.file.JoinPaths(currentDir, '~logs')

    if (not mypycommons.file.directoryExists(logsDir)):
        mypycommons.file.createDirectory(logsDir)
    
    return logsDir

mypycommons.logger.initSharedLogger(logFilename='prefbak.log', logDir=getProjectLogsDir())
mypycommons.logger.setSharedLoggerConsoleOutputLogLevel('info')
logger = mypycommons.logger.getSharedLogger()

def getProjectCacheDir():
    currentDir = mypycommons.file.getThisScriptCurrentDirectory()
    cacheDir = mypycommons.file.JoinPaths(currentDir, '~cache')

    if (not mypycommons.file.directoryExists(cacheDir)):
        mypycommons.file.createDirectory(cacheDir)
    
    return cacheDir



# https://stackoverflow.com/questions/39327032/how-to-get-the-latest-file-in-a-folder-using-python
def getMostRecentArchiveFile(archiveDir):
    fileSearchPattern = mypycommons.file.JoinPaths(archiveDir, ('*' + archiveFileNameSuffix))
    allArchiveFiles = glob.glob(fileSearchPattern)

    if (allArchiveFiles):
        mostRecentFile = max(allArchiveFiles, key=os.path.getmtime)
    else:
        mostRecentFile = None

    return mostRecentFile

def getArchiveInternalFileContainerHash(archiveFilepath):
    sevenZipArgs = ['7z', 't', archiveFilepath, archiveInternalFileContainerName, '-scrcsha256']
    result = subprocess.run(sevenZipArgs, stdout=subprocess.PIPE)
    outputString = result.stdout.decode('utf-8')

    tarHash = outputString.split('SHA256 for data:')[1].strip()
    return tarHash

def archiveFilesAreIdentical(archiveFile1, archiveFile2):
    return (getArchiveInternalFileContainerHash(archiveFile1) == getArchiveInternalFileContainerHash(archiveFile2))

def compressPathToArchive(inputFilePath):
    '''
    Compresses the given files and/or directories to a tar archive, then compresses this tar into
    a 7zip archive, given the input filepath(s) and filepath for the archive file. This method 
    preserves the owner:group permissions on the files while allowing them to be compressed with 7z.
    7zip must be installed on the system and 7z must be in the path.

    Params:
        inputFilePath: single path of the file or directory to compress, or a list of paths
        archiveOutFilePath: filepath of the archive file to output to, filename should not include
            the .tar.gz extension
    '''
    archiveName = '[{}] {}{}'.format(
        mypycommons.time.getCurrentTimestampForFilename(), 
        mypycommons.file.GetFilename(inputFilePath),
        archiveFileNameSuffix
    ) 

    archiveInternalFileContainerFilepath = mypycommons.file.JoinPaths(getProjectCacheDir(), archiveInternalFileContainerName)
    archiveFilepath = mypycommons.file.JoinPaths(getProjectCacheDir(), archiveName)

    with tarfile.open(archiveInternalFileContainerFilepath, 'w') as archive:
        archive.add(inputFilePath, arcname=mypycommons.file.GetFilename(inputFilePath))
    
    sevenZipArgs = ['7z', 'a', '-t7z', '-mx=9', '-mfb=64', '-md=64m', archiveFilepath, archiveInternalFileContainerFilepath]
    subprocess.call(sevenZipArgs)

    mypycommons.file.DeleteFile(archiveInternalFileContainerFilepath)

    return archiveFilepath

def performBackupStep(sourcePath, destinationPath):
    '''
    Performs a single backup operation. Files can either be mirrored/copied from the source path to 
    the destination path, or an archive file at the destination path can be made from the source
    file.

    Params:
        sourcePath: single filepath (file or directory) to use as the backup source
        destinationPath: single filepath (file or directory) to use as the destination/backup 
            location. Use the name of the archive file if also using the 'compress' param
    '''
    if (not mypycommons.file.directoryExists(destinationPath)):
        logger.info("Backup destination path '{}' does not exist: creating it".format(destinationPath))
        mypycommons.file.createDirectory(destinationPath)

    mostRecentArchiveFile = getMostRecentArchiveFile(destinationPath)
    if (mostRecentArchiveFile):
        logger.info("Pre-scan found the current most recent archive file in this destination dir: {}".format(mostRecentArchiveFile))
    else:
        logger.info("No most recent archive file found in this destination dir: it must be empty")

    logger.info("Compressing new archive from source data and writing it to ~cache")
    newArchiveFile = compressPathToArchive(sourcePath)
    logger.info("Finished compresing archive, created file: {}".format(newArchiveFile))

    if (mostRecentArchiveFile and archiveFilesAreIdentical(mostRecentArchiveFile, newArchiveFile)):
        logger.info("An archive with the same data as the newly created archive exists in the destination: discarding new archive file")
        mypycommons.file.DeleteFile(newArchiveFile)

    else:
        logger.info("The newly created archive has unique data: no duplicate archives found in destination - moving new archive file from ~cache to destination")
        mypycommons.file.moveFileToDirectory(newArchiveFile, destinationPath)

def performBackup(configData):
    '''
    Reads the given backup config file and performs each backup from the definitions.

    Params:
        configFile: the Json prefbak config file
    '''
    backupRootDir = configData['backupRootDir']
    backupRules = configData['backupRules']

    for backupRule in backupRules:
        sourcePath = backupRule['sourcePath']
        destinationPath = mypycommons.file.JoinPaths(backupRootDir, backupRule['backupPath'])

        logger.info("Performing backup step for rule: {} -> {}".format(sourcePath, destinationPath))
        performBackupStep(sourcePath, destinationPath)

if __name__ == "__main__":

    # For now, set the computer name here
    computerName = 'zinc'

    backupConfigName = '{}.config.json'.format(computerName)
    backupConfigFilepath = mypycommons.file.JoinPaths('machine-config', backupConfigName)

    logger.info("Loading prefbak config file for current machine: {}".format(backupConfigFilepath))
    configData = mypycommons.file.readJsonFile(backupConfigFilepath)

    logger.info("Config file loaded, beginning prefbak backup routine according to backup rules")
    performBackup(configData)

    logger.info("Backup routine completed successfully")








    