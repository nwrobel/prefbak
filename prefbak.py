'''
Script that performs a "prefbak" routine: that is, performs a backup of a machine according to the
backup rules defined in that machine's prefbak config file.
'''

import subprocess
import tarfile
import glob
import os
import socket
import fnmatch


from com.nwrobel import mypycommons
import com.nwrobel.mypycommons.file
import com.nwrobel.mypycommons.time
import com.nwrobel.mypycommons.logger

# Module-wide global variables, used by many of the helper functions below
archiveInternalFileContainerName = "archiveInternalFileContainer.tar"
archiveFileNameSuffix = ".archive.tar.7z"
runningWindowsOS = False
sevenZipExeFilepath = ''
powershellExeFilepath = ''

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

def getMostRecentArchiveFile(archivePartialFilename, archiveDir):
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

def getFileHash(filepath):
    if (runningWindowsOS):
        powershellCommand = "(Get-FileHash {} -Algorithm SHA256).Hash".format(filepath)
        result = subprocess.run([powershellExeFilepath, powershellCommand], stdout=subprocess.PIPE)
        hashString = result.stdout.decode('utf-8')
    else:
        result = subprocess.run(['sha256sum', filepath], stdout=subprocess.PIPE)
        output = result.stdout.decode('utf-8')
        hashString = output.split(" ")[0].strip()

    return hashString.upper()


    
def get7zArchiveItemsNameAndType(archiveFilepath):
    if (runningWindowsOS):
        sevenZipCommand = sevenZipExeFilepath
    else:
        sevenZipCommand = '7z'

    runArgs = [sevenZipCommand] + ['l', '-slt', '-ba', archiveFilepath]
    runResult = subprocess.run(runArgs, stdout=subprocess.PIPE)
    
    output = runResult.stdout.decode('utf-8')
    outputLines = output.split('\n')
    itemNameLines = fnmatch.filter(outputLines, 'Path = *')
    itemAttrLines = fnmatch.filter(outputLines, 'Attributes = *')
    
    archiveItemsNames = []
    for index, itemNameLine in enumerate(itemNameLines):
        itemName = itemNameLine.replace('Path = ', '')
        itemAttrs = itemAttrLines[index].replace('Attributes = ', '')

        if ('D_' in itemAttrs): 
            itemType = 'directory'
        else:
            itemType = 'file'

        archiveItemsNames.append({
            'pathName': itemName,
            'type': itemType
        })

    return archiveItemsNames
    
def get7zArchiveItemHash(archiveFilepath, archiveItemName):
    if (runningWindowsOS):
        sevenZipCommand = sevenZipExeFilepath
    else:
        sevenZipCommand = '7z'

    runArgs = [sevenZipCommand] + ['t', '-scrcsha256', archiveFilepath, archiveItemName]
    runResult = subprocess.run(runArgs, stdout=subprocess.PIPE)

    output = runResult.stdout.decode('utf-8')
    itemHash = output.split('SHA256 for data:')[1].strip()

    return itemHash

def _getContentChecksumInfoFor7zArchive(archiveFilepath):
    archiveItemsNameAndType = get7zArchiveItemsNameAndType(archiveFilepath)
    archiveContentInfo = []

    for item in archiveItemsNameAndType:
        if (item['type'] == 'file'):
            itemHash = get7zArchiveItemHash(archiveFilepath, item['pathName'])
        else:
            itemHash = None

        itemInfo = {
            'pathName': item['pathName'],
            'type': item['type'],
            'hash': itemHash
        }
        archiveContentInfo.append(itemInfo)
    
    return archiveContentInfo

def _getContentChecksumInfoForPath(filepath):
    allItemsPaths = mypycommons.file.GetAllFilesAndDirectoriesRecursive(rootPath=filepath)
    allItemsPaths += [filepath]

    baseFilename = mypycommons.file.GetFilename(filepath)
    trimThisFromPaths = filepath.replace(baseFilename, '')

    itemRelativePaths = []
    for itemPath in allItemsPaths:
        relativePath = itemPath.replace(trimThisFromPaths, '')
        itemRelativePaths.append(relativePath)

    itemRelativePaths.sort()

    pathContentsInfo = []
    for itemRelativePath in itemRelativePaths:
        itemAbsolutePath = trimThisFromPaths + itemRelativePath
        
        if (mypycommons.file.fileExists(itemAbsolutePath)):
            itemType = 'file'
            itemHash = getFileHash(itemAbsolutePath)
        elif (mypycommons.file.directoryExists(itemAbsolutePath)):
            itemType = 'directory'
            itemHash = None
        else:
            raise "Error: the given path does not exist: {}".format(itemAbsolutePath)
        
        itemInfo = {
            'pathName': itemRelativePath,
            'type': itemType,
            'hash': itemHash
        }
        pathContentsInfo.append(itemInfo)

    return pathContentsInfo
    



def sourceDataMatchesExistingArchive(sourcePath, archiveFilepath):
    archiveFileInfo = _getContentChecksumInfoFor7zArchive(archiveFilepath)
    pathFileInfo = _getContentChecksumInfoForPath(sourcePath)

    archiveFileInfoSorted = sorted(archiveFileInfo, key=lambda k: k['pathName']) 
    pathFileInfoSorted = sorted(pathFileInfo, key=lambda k: k['pathName']) 

    print(archiveFileInfoSorted)
    print()
    print(pathFileInfoSorted)

    if (archiveFileInfoSorted == pathFileInfoSorted):
        return True
    else:
        return False
            


def getThisMachineName():
    return socket.gethostname()

def thisMachineIsWindowsOS():
    if (os.name == 'nt'):
        return True
    else:
        return False


def create7zArchive(sourcePath, archiveFilepath):
    if (runningWindowsOS):
        sevenZipCommand = sevenZipExeFilepath
    else:
        sevenZipCommand = '7z'

    runArgs = [sevenZipCommand] + ['a', '-t7z', '-mx=9', '-mfb=64', '-md=64m', archiveFilepath, sourcePath]
    subprocess.call(runArgs)    

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

    mostRecentArchiveFile = getMostRecentArchiveFile(archivePartialFilename=mypycommons.file.GetFilename(sourcePath), archiveDir=destinationPath)
    if (mostRecentArchiveFile):
        logger.info("Pre-scan found the latest pre-existing archive file of the source path in this destination dir: {}".format(mostRecentArchiveFile))
    else:
        logger.info("No pre-existing archive file found in this destination dir: it must be empty")

    if (mostRecentArchiveFile and sourceDataMatchesExistingArchive(sourcePath, mostRecentArchiveFile)):
        logger.info("An archive with the same data as the source already exists in the destination: no new backup archive will be created")

    else:
        logger.info("Latest archive doesn't contain the latest source data: a new backup archive will be created")

        archiveName = '[{}] {}{}'.format(
            mypycommons.time.getCurrentTimestampForFilename(), 
            mypycommons.file.GetFilename(sourcePath),
            archiveFileNameSuffix
        ) 
        archiveFilepath = mypycommons.file.JoinPaths(destinationPath, archiveName)

        logger.info("Creating new backup archive now at {}".format(archiveFilepath))
        create7zArchive(sourcePath, archiveFilepath)

def performBackup(configData):
    '''
    Reads the given backup config file and performs each backup from the definitions.

    Params:
        configFile: the Json prefbak config file
    '''
    backupDataPermissions = configData['backupDataPermissions']
    backupRules = configData['backupRules']

    for backupRule in backupRules:
        sourcePath = backupRule['sourcePath']
        destinationPath = backupRule['backupDestDir']

        logger.info("Performing backup step for rule: {} -> {}".format(sourcePath, destinationPath))
        performBackupStep(sourcePath, destinationPath)

        # Set the permissions on the destination path and the archive file within so that the user can read the backup
        if (not runningWindowsOS):
            logger.info("Updating file permissions for backup destination directory {}".format(destinationPath))
            mypycommons.file.applyPermissionToPath(path=destinationPath, owner=backupDataPermissions['owner'], group=backupDataPermissions['group'], mask=backupDataPermissions['mask'], recursive=True)



# ------------------------------------ Script 'main' execution -------------------------------------
if __name__ == "__main__":

    thisProjectDir = mypycommons.file.getThisScriptCurrentDirectory()
    thisProjectLogsDir = getProjectLogsDir()
    thisProjectConfigDir = mypycommons.file.JoinPaths(thisProjectDir, 'machine-config')
    thisProjectPrepScriptsDir = mypycommons.file.JoinPaths(thisProjectDir, 'machine-backup-prep-scripts')

    # Setup logging for this script
    logFilename = 'prefbak.log'
    mypycommons.logger.initSharedLogger(logFilename=logFilename, logDir=thisProjectLogsDir)
    mypycommons.logger.setSharedLoggerConsoleOutputLogLevel('debug')
    logger = mypycommons.logger.getSharedLogger()

    machineName = getThisMachineName()
    runningWindowsOS = thisMachineIsWindowsOS()

    if (runningWindowsOS):
        sevenZipExeFilepath = "C:\\Program Files\\7-Zip\\7z.exe"
        powershellExeFilepath = "C:\\Windows\\System32\\WindowsPowerShell\\v1.0\\powershell.exe"

        if (mypycommons.file.fileExists(sevenZipExeFilepath)):
            logger.info("Using the 7zip executable program located at {}".format(sevenZipExeFilepath))
        else:
            raise FileNotFoundError("7zip executable program was not found at the default location on this system ({} does not exist)".format(sevenZipExeFilepath))

    backupConfigName = '{}.config.json'.format(machineName)
    backupConfigFilepath = mypycommons.file.JoinPaths(thisProjectConfigDir, backupConfigName)

    # x = getFileHash('/datastore/nick/Temp/archive.tar')
    # print(x)
    # x = getFileHash('/datastore/nick/Temp/archive2.tar')
    # print(x)

    # x= get7zArchiveItemsNameAndType('/datastore/nick/Temp/archive3.7z')
    # print(x)
    # x = get7zArchiveItemHash('/datastore/nick/Temp/archive3.7z', 'test')
    # print(x)

    # x = get7zArchiveContentInfo('/datastore/nick/Temp/archive2.7z')
    # print(x)


    y = sourceDataMatchesExistingArchive('/home/nick/.vim', '/datastore/nick/Temp/archive2.7z')
    print(y)


    # create7zArchive('/home/nick/.vim', '/datastore/nick/Temp/archive10.7z')

    #x = getTarArchiveContentsChecksum('/datastore/nick/Temp/archive.tar')




    # logger.info("Starting prefbak backup routine script for machine '{}'".format(machineName))

    # logger.info("Loading this machine's prefbak config file: {}".format(backupConfigFilepath))
    # configData = mypycommons.file.readJsonFile(backupConfigFilepath)

    # # Change permission on the log file to whatever permissions are configured in the machine config file
    # # so that the user can read the log file (if the log file is created when running this script as
    # # sudo, it will not be readable by other users)
    # if (not runningWindowsOS):
    #     logger.info("Setting the log file permissions to those set in the machine's config file")
    #     logFilepath = mypycommons.file.JoinPaths(thisProjectLogsDir, logFilename)
    #     backupDataPermissions = configData['backupDataPermissions']
    #     mypycommons.file.applyPermissionToPath(path=logFilepath, owner=backupDataPermissions['owner'], group=backupDataPermissions['group'], mask=backupDataPermissions['mask'])

    # # Run the prep script, if this is configured for the machine
    # if (configData['prepScript'] == 'true'):
    #     if (runningWindowsOS):
    #         prepScriptName = "backup-prep-{}.ps1".format(machineName)
    #     else:
    #         prepScriptName = "backup-prep-{}.sh".format(machineName)

    #     prepScriptFilepath = mypycommons.file.JoinPaths(thisProjectPrepScriptsDir, prepScriptName)

    #     if (runningWindowsOS):
    #         runArgs = [powershellExeFilepath, prepScriptFilepath]
    #     else:
    #         runArgs = [prepScriptFilepath]

    #     logger.info("Prep script configured for this machine: running script before doing the backup: {}".format(prepScriptFilepath))
    #     subprocess.call(runArgs, shell=True)
    #     logger.info("Prep script execution complete".format(prepScriptFilepath))
        

    # logger.info("Beginning prefbak backup routine according to backup rules")
    # performBackup(configData)

    # logger.info("Backup routine completed successfully, script complete")




    