'''
Script that performs a "prefbak" routine: that is, performs a backup of a machine according to the
backup rules defined in that machine's prefbak config file.
'''

import subprocess
import glob
import os
import socket

from com.nwrobel import mypycommons
import com.nwrobel.mypycommons.file
import com.nwrobel.mypycommons.time
import com.nwrobel.mypycommons.logger

# Module-wide global variables, used by many of the helper functions below
archiveInternalFileContainerName = "archiveInternalFileContainer.tar"
archiveFileNameSuffix = ".archive.tar.7z"
runningWindowsOS = False
sevenZipExeFilepath = ''

# ----------------------------- Script helper functions --------------------------------------------
def getProjectLogsDir():
    currentDir = mypycommons.file.getThisScriptCurrentDirectory()
    logsDir = mypycommons.file.JoinPaths(currentDir, '~logs')

    if (not mypycommons.file.directoryExists(logsDir)):
        mypycommons.file.createDirectory(logsDir)
    
    return logsDir

def getProjectCacheDir():
    currentDir = mypycommons.file.getThisScriptCurrentDirectory()
    cacheDir = mypycommons.file.JoinPaths(currentDir, '~cache')

    if (not mypycommons.file.directoryExists(cacheDir)):
        mypycommons.file.createDirectory(cacheDir)
    
    return cacheDir

def getMostRecentArchiveFile(archiveFilename, archiveDir):
    fileSearchPattern = mypycommons.file.JoinPaths(
        archiveDir, 
        ('*' + archiveFilename + archiveFileNameSuffix)
    )
    allArchiveFiles = glob.glob(fileSearchPattern)

    if (allArchiveFiles):
        mostRecentFile = max(allArchiveFiles, key=os.path.getmtime)
    else:
        mostRecentFile = None

    return mostRecentFile

def getArchiveInternalFileContainerHash(archiveFilepath):
    if (runningWindowsOS):
        sevenZipCommand = sevenZipExeFilepath
    else:
        sevenZipCommand = '7z'

    runArgs = [sevenZipCommand] + ['t', archiveFilepath, archiveInternalFileContainerName, '-scrcsha256']

    result = subprocess.run(runArgs, stdout=subprocess.PIPE)
    outputString = result.stdout.decode('utf-8')

    tarHash = outputString.split('SHA256 for data:')[1].strip()
    return tarHash

def archiveFilesAreIdentical(archiveFile1, archiveFile2):
    return (getArchiveInternalFileContainerHash(archiveFile1) == getArchiveInternalFileContainerHash(archiveFile2))

def getThisMachineName():
    return socket.gethostname()

def thisMachineIsWindowsOS():
    if (os.name == 'nt'):
        return True
    else:
        return False

def createTarArchive(inputFilepath, archiveFilepath):
    if (runningWindowsOS):
        sevenZipCommand = sevenZipExeFilepath
    else:
        sevenZipCommand = '7z'

    runArgs = [sevenZipCommand] + ['a', '-ttar', archiveFilepath, inputFilepath]
    subprocess.call(runArgs)    

def createSevenZipArchive(inputFilepath, archiveFilepath):
    if (runningWindowsOS):
        sevenZipCommand = sevenZipExeFilepath
    else:
        sevenZipCommand = '7z'

    runArgs = [sevenZipCommand] + ['a', '-t7z', '-mx=9', '-mfb=64', '-md=64m', archiveFilepath, inputFilepath]
    subprocess.call(runArgs)    

def compressPathToArchive(inputFilepath):
    '''
    Compresses the given files and/or directories to a tar archive, then compresses this tar into
    a 7zip archive, given the input filepath(s) and filepath for the archive file. This method 
    preserves the owner:group permissions on the files while allowing them to be compressed with 7z.
    7zip must be installed on the system and 7z must be in the path.

    Params:
        inputFilepath: single path of the file or directory to compress, or a list of paths
        archiveOutFilePath: filepath of the archive file to output to, filename should not include
            the .tar.gz extension
    '''
    archiveName = '[{}] {}{}'.format(
        mypycommons.time.getCurrentTimestampForFilename(), 
        mypycommons.file.GetFilename(inputFilepath),
        archiveFileNameSuffix
    ) 

    archiveInternalFileContainerFilepath = mypycommons.file.JoinPaths(getProjectCacheDir(), archiveInternalFileContainerName)
    archiveFilepath = mypycommons.file.JoinPaths(getProjectCacheDir(), archiveName)

    logger.info("Creating internal tar archive file at {}".format(archiveInternalFileContainerFilepath))
    createTarArchive(inputFilepath=inputFilepath, archiveFilepath=archiveInternalFileContainerFilepath)

    logger.info("Creating high compression 7zip archive at {}".format(archiveFilepath))
    createSevenZipArchive(inputFilepath=archiveInternalFileContainerFilepath, archiveFilepath=archiveFilepath)

    logger.info("Removing the temporary tar archive file that was produced")
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

    mostRecentArchiveFile = getMostRecentArchiveFile(archiveFilename=mypycommons.file.GetFilename(sourcePath), archiveDir=destinationPath)
    if (mostRecentArchiveFile):
        logger.info("Pre-scan found the latest pre-existing archive file of the source path in this destination dir: {}".format(mostRecentArchiveFile))
    else:
        logger.info("No most recent archive file found in this destination dir: it must be empty")

    logger.info("Compressing new archive from source data and writing it to ~cache")
    newArchiveFile = compressPathToArchive(sourcePath)

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
    backupDataPermissions = configData['backupDataPermissions']
    backupRules = configData['backupRules']

    for backupRule in backupRules:
        sourcePath = backupRule['sourcePath']
        destinationPath = mypycommons.file.JoinPaths(backupRootDir, backupRule['backupPath'])

        logger.info("Performing backup step for rule: {} -> {}".format(sourcePath, destinationPath))
        performBackupStep(sourcePath, destinationPath)

    # Set the permissions on all backed up files so that the user can read them
    if (not runningWindowsOS):
        logger.info("Updating file permissions on all archive files in the backup root dir, so that they can be accessed")
        mypycommons.file.applyPermissionToPath(path=backupRootDir, owner=backupDataPermissions['owner'], group=backupDataPermissions['group'], mask=backupDataPermissions['mask'])

# ------------------------------------ Script 'main' execution -------------------------------------
if __name__ == "__main__":

    thisProjectDir = mypycommons.file.getThisScriptCurrentDirectory()
    thisProjectLogsDir = getProjectLogsDir()
    thisProjectConfigDir = mypycommons.file.JoinPaths(thisProjectDir, 'machine-config')
    thisProjectPrepScriptsDir = mypycommons.file.JoinPaths(thisProjectDir, 'machine-backup-prep-scripts')

    # Setup logging for this script
    logFilename = 'prefbak.log'
    mypycommons.logger.initSharedLogger(logFilename=logFilename, logDir=thisProjectLogsDir)
    mypycommons.logger.setSharedLoggerConsoleOutputLogLevel('info')
    logger = mypycommons.logger.getSharedLogger()

    machineName = getThisMachineName()
    runningWindowsOS = thisMachineIsWindowsOS()

    if (runningWindowsOS):
        sevenZipExeFilepath = "C:\\Program Files\\7-Zip\\7z.exe"

        if (mypycommons.file.fileExists(sevenZipExeFilepath)):
            logger.info("Using the 7zip executable program located at {}".format(sevenZipExeFilepath))
        else:
            raise FileNotFoundError("7zip executable program was not found at the default location on this system ({} does not exist)".format(sevenZipExeFilepath))

    backupConfigName = '{}.config.json'.format(machineName)
    backupConfigFilepath = mypycommons.file.JoinPaths(thisProjectConfigDir, backupConfigName)

    logger.info("Starting prefbak backup routine script for machine '{}'".format(machineName))

    logger.info("Loading this machine's prefbak config file: {}".format(backupConfigFilepath))
    configData = mypycommons.file.readJsonFile(backupConfigFilepath)

    # Change permission on the log file to whatever permissions are configured in the machine config file
    # so that the user can read the log file (if the log file is created when running this script as
    # sudo, it will not be readable by other users)
    if (not runningWindowsOS):
        logger.info("Setting the log file permissions to those set in the machine's config file")
        logFilepath = mypycommons.file.JoinPaths(thisProjectLogsDir, logFilename)
        backupDataPermissions = configData['backupDataPermissions']
        mypycommons.file.applyPermissionToPath(path=logFilepath, owner=backupDataPermissions['owner'], group=backupDataPermissions['group'], mask=backupDataPermissions['mask'])

    # Run the prep script, if this is configured for the machine
    if (configData['prepScript'] == 'true'):
        if (runningWindowsOS):
            prepScriptName = "backup-prep-{}.ps1".format(machineName)
        else:
            prepScriptName = "backup-prep-{}.sh".format(machineName)

        prepScriptFilepath = mypycommons.file.JoinPaths(thisProjectPrepScriptsDir, prepScriptName)

        if (runningWindowsOS):
            powershellExeFilepath = "C:\\Windows\\System32\\WindowsPowerShell\\v1.0\\powershell.exe"
            runArgs = [powershellExeFilepath, prepScriptFilepath]
        else:
            runArgs = [prepScriptFilepath]

        logger.info("Prep script configured for this machine: running script before doing the backup: {}".format(prepScriptFilepath))
        subprocess.call(runArgs, shell=True)
        logger.info("Prep script execution complete".format(prepScriptFilepath))
        

    logger.info("Beginning prefbak backup routine according to backup rules")
    performBackup(configData)

    logger.info("Backup routine completed successfully, script complete")




    