'''
Script that performs a "prefbak" routine: that is, performs a backup of a machine according to the
backup rules defined in that machine's prefbak config file.
'''

import logging
import subprocess
import argparse
import sys

from com.nwrobel import mypycommons
import com.nwrobel.mypycommons.file
import com.nwrobel.mypycommons.time
import com.nwrobel.mypycommons.logger
import com.nwrobel.mypycommons.system
import com.nwrobel.mypycommons.archive

# Setup logging for this entire module/script
logger = logging.getLogger(__name__)

# Module-wide global variables, used by many of the helper functions below
archiveFileNameSuffix = "backup"
powershellExeFilepath = "C:\\Windows\\System32\\WindowsPowerShell\\v1.0\\powershell.exe"

# ----------------------------- Script helper functions --------------------------------------------
def getProjectLogsDir():
    currentDir = mypycommons.file.getThisScriptCurrentDirectory()
    logsDir = mypycommons.file.joinPaths(currentDir, '~logs')

    if (not mypycommons.file.pathExists(logsDir)):
        mypycommons.file.createDirectory(logsDir)
    
    return logsDir

def getProjectCacheDir():
    currentDir = mypycommons.file.getThisScriptCurrentDirectory()
    cacheDir = mypycommons.file.joinPaths(currentDir, '~cache')

    if (not mypycommons.file.pathExists(cacheDir)):
        mypycommons.file.createDirectory(cacheDir)
    
    return cacheDir

def runScript(scriptFilepath):
    if (not mypycommons.file.pathExists(scriptFilepath)):
        raise FileNotFoundError("Error: The script '{}' does not exist".format(scriptFilepath))

    if (runningWindowsOS):
        runArgs = [powershellExeFilepath, scriptFilepath]
    else:
        runArgs = [scriptFilepath]

    logger.info("Starting script: '{}'".format(scriptFilepath))
    subprocess.call(runArgs, shell=True)
    logger.info("Script execution complete")


def performFileBackupStep(sourcePath, destinationDir):
    '''
    Performs a single backup operation. Files can either be mirrored/copied from the source path to 
    the destination path, or an archive file at the destination path can be made from the source
    file.

    Params:
        sourcePath: single filepath (file or directory) to use as the backup source
        destinationDir: destination dir to use as the destination/backup 
            location. Use the name of the archive file if also using the 'compress' param
    '''
    if (not mypycommons.file.pathExists(destinationDir)):
        logger.info("Backup destination directory '{}' does not exist: creating it".format(destinationDir))
        mypycommons.file.createDirectory(destinationDir)

    currentTimestampStr = mypycommons.time.getCurrentTimestampForFilename()
    baseArchiveFilename = mypycommons.file.getFilename(sourcePath)
    archiveName = ''
    sourcePathFinal = ''

    # If we aren't running Windows, we want to use the 'tar' command, available on non-win systems
    if (not runningWindowsOS):
        tarArchiveName = '{} {}.{}.tar'.format(currentTimestampStr, baseArchiveFilename, archiveFileNameSuffix) 
        tarArchiveFilepath = mypycommons.file.joinPaths(getProjectCacheDir(), tarArchiveName)

        logger.info("Creating inner TAR archive: '{}'".format(tarArchiveFilepath))
        mypycommons.archive.createTarArchive(sourcePath, tarArchiveFilepath)

        archiveName = '{}.7z'.format(tarArchiveName)
        sourcePathFinal = tarArchiveFilepath
    else:
        archiveName = '{} {}.{}.7z'.format(currentTimestampStr, baseArchiveFilename, archiveFileNameSuffix) 
        sourcePathFinal = sourcePath

    archiveFilepath = mypycommons.file.joinPaths(destinationDir, archiveName)

    logger.info("Creating new 7z backup archive now: '{}'".format(archiveFilepath))
    mypycommons.archive.create7zArchive(sourcePathFinal, archiveFilepath)

def changeDestinationDirectoryPermissions(destinationPath, backupDataPermissionsData):
    logger.info("Updating file permissions for backup destination directory {}".format(destinationPath))
    mypycommons.file.applyPermissionToPath(path=destinationPath, owner=backupDataPermissionsData['owner'], group=backupDataPermissionsData['group'], mask=backupDataPermissionsData['mask'], recursive=True)


def runBackupRule(ruleConfig, machineScriptsDir):
    '''
    '''
    ruleName = ruleConfig['name']
    ruleFiles = ruleConfig['files']
    ruleInitScriptName = ruleConfig['initScript']
    rulePostRunScriptName = ruleConfig['postRunScript']
    backupDataPermissions = configData['backupFilesPermissions']

    logger.info("=====>Beginning Rule: {}".format(ruleName))

    if (ruleInitScriptName):
        logger.info("Running the rule's configured init script")
        ruleInitScriptFilepath = mypycommons.file.joinPaths(machineScriptsDir, ruleInitScriptName)
        runScript(ruleInitScriptFilepath)

    logger.info("-->Performing all backup steps for rule: {}".format(ruleName))

    for ruleFile in ruleFiles:
        sourcePath = ruleFile['sourcePath']
        destinationDir = ruleFile['destinationDir']
        logger.info("Starting file backup: '{}' --> '{}'".format(sourcePath, destinationDir))
        performFileBackupStep(sourcePath, destinationDir)

        # On Linux only:
        # Set the permissions on the destination path and the archive file within so that the user can read the backup
        if (not runningWindowsOS):
            changeDestinationDirectoryPermissions(destinationDir, backupDataPermissions)

    if (rulePostRunScriptName):
        logger.info("Running the rule's configured post-run script")
        rulePostRunScriptFilepath = mypycommons.file.joinPaths(machineScriptsDir, rulePostRunScriptName)
        runScript(rulePostRunScriptFilepath)


        
# ------------------------------------ Script 'main' execution -------------------------------------
if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    group = parser.add_mutually_exclusive_group()

    parser.add_argument("--config-file", 
        dest='configFilename',
        type=str,
        help="Name of the config file to use, located in this project's machine-config directory - If not specified, will use the config file named '<hostName>.config.json'"
    )
    group.add_argument('-l', '--list-rules', 
        action='store_true',
        dest='listRules',
        help="Print the rules names from the config file that can be run"
    )
    group.add_argument('-r', '--run-rules', 
        nargs='+', 
        default=[],
        dest='runRuleNames',
        help="One or more specific rule names, seperated by [space], of the rules you want to run"
    )
    group.add_argument("-a", "--run-all", 
        action='store_true',
        dest='runAllRules',
        help="Run all the rules set up in the config file"
    )

    args = parser.parse_args()

    # Configure logger
    projectLogsDir = getProjectLogsDir()
    mypycommons.logger.configureLoggerWithBasicSettings(__name__, projectLogsDir)

    # Get machine name and other values needed
    machineName = mypycommons.system.getThisMachineName()
    runningWindowsOS = mypycommons.system.thisMachineIsWindowsOS()
    logger.info("System properties: MachineName='{}', IsWindows='{}'".format(machineName, runningWindowsOS))

    projectDir = mypycommons.file.getThisScriptCurrentDirectory()
    machineConfigDir = mypycommons.file.joinPaths(projectDir, 'machine-config')

    scriptsDir = mypycommons.file.joinPaths(projectDir, 'machine-scripts')
    machineScriptsDir = mypycommons.file.joinPaths(scriptsDir, machineName)

    if (not mypycommons.file.pathExists(machineScriptsDir)):
        raise FileNotFoundError("Error: The scripts directory for this machine ({}) does not exist".format(machineScriptsDir))

    if (not args.configFilename):
        backupConfigFilename = '{}.config.json'.format(machineName)
        logger.info("Config file name not given: using the config file based on machine name: {}".format(backupConfigFilename))
    else:
        backupConfigFilename = args.configFilename

    backupConfigFilepath = mypycommons.file.joinPaths(machineConfigDir, backupConfigFilename)

    if (not mypycommons.file.pathExists(backupConfigFilepath)):
        raise FileNotFoundError("Error: The backup config file '{}' for this machine does not exist: exiting".format(backupConfigFilepath)) 

    logger.info("Loading prefbak config file: {}".format(backupConfigFilepath))
    configData = mypycommons.file.readJsonFile(backupConfigFilepath)

    # ---------------------------
    # List rules, if arg is set
    allBackupRules = configData['rules']

    if (args.listRules):
        for rule in allBackupRules:
            print(rule['name'])
        sys.exit(0)

    logger.info("Starting prefbak backup routine script for machine '{}'".format(machineName))

    # ---------------------------
    # Run init script
    initScriptName = configData['globalInitScript']
    if (initScriptName):
        logger.info("Running the configured global init script")
        initScriptFilepath = mypycommons.file.joinPaths(machineScriptsDir, initScriptName)
        runScript(initScriptFilepath)

    # ----------------------------
    # Perform backup
    if (args.runAllRules):
        backupRulesToRunConfig = allBackupRules
        logger.info("Starting routine for all ({}) configured backup rules".format(str(len(backupRulesToRunConfig))))
    else:
        backupRulesToRunConfig = [ruleCfg for ruleCfg in allBackupRules if (ruleCfg['name'] in args.runRuleNames)]
        backupRulesToRunNames = [rule['name'] for rule in backupRulesToRunConfig]
        logger.info("Starting routine for the given ({}) configured backup rules: {}".format(str(len(backupRulesToRunConfig)), str(backupRulesToRunNames)))

    for backupRuleConfig in backupRulesToRunConfig:
        runBackupRule(backupRuleConfig, machineScriptsDir)

    logger.info("Backup routine completed successfully")

    # ---------------------------
    # Run postrun script
    postScriptName = configData['globalPostRunScript']
    if (postScriptName):
        logger.info("Running the configured global post-run script")
        postScriptFilepath = mypycommons.file.joinPaths(machineScriptsDir, postScriptName)
        runScript(postScriptFilepath)

    logger.info("All processes complete: prefbak operation finished successfully")




    