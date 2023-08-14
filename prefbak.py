'''
Script that performs a "prefbak" routine: that is, performs a backup of a machine according to the
backup rules defined in that machine's prefbak config file.


'''

import logging
import subprocess
import argparse
import sys
from typing import Literal, List

from com.nwrobel import mypycommons
import com.nwrobel.mypycommons.file
import com.nwrobel.mypycommons.time
import com.nwrobel.mypycommons.logger
import com.nwrobel.mypycommons.system
import com.nwrobel.mypycommons.archive

import helpers, config

# Setup logging for this entire module/script
loggerName = 'prefbak-logger'
logger = mypycommons.logger.getLogger(loggerName)


def runScript(scriptFilepath: str, config: config.PrefbakConfig):
    if (not mypycommons.file.pathExists(scriptFilepath)):
        raise FileNotFoundError("Error: The script '{}' does not exist".format(scriptFilepath))

    if (config.globalConfig.runningWindowsOS):
        runArgs = [config.globalConfig.powershellFilepath, scriptFilepath]
    else:
        runArgs = [scriptFilepath]

    logger.info("Starting script: '{}'".format(scriptFilepath))
    subprocess.call(runArgs, shell=True)
    logger.info("Script execution complete")



def rsyncRun(sourcePath: str, destinationDir: str, rsyncFilepath: str):
    logger.info("Performing rsync to destination dir: '{}'".format(destinationDir))

    runArgs = [rsyncFilepath, '-aP', '--delete-after', sourcePath, destinationDir]
    subprocess.call(runArgs, shell=True)

def tarRun(sourcePath: str, destinationDir: str):
    currentTimestampStr = mypycommons.time.getCurrentTimestampForFilename()
    baseArchiveFilename = mypycommons.file.getFilename(sourcePath)

    tarArchiveName = '{} {}.tar'.format(currentTimestampStr, baseArchiveFilename) 
    tarArchiveFilepath = mypycommons.file.joinPaths(destinationDir, tarArchiveName)

    logger.info("Creating TAR archive: '{}'".format(tarArchiveFilepath))
    mypycommons.archive.createTarArchive(sourcePath, tarArchiveFilepath)

def performRuleFileBackupStep(sourcePath: str, fullDestDir: str, operation: Literal['rsync', 'tar'], rsyncFilepath: str):
    '''
    Performs a single backup operation. Files can either be mirrored/copied from the source path to 
    the destination path, or an archive file at the destination path can be made from the source
    file.

    Params:
        sourcePath: single filepath (file or directory) to use as the backup source
        destinationDir: destination dir to use as the destination/backup 
            location. Use the name of the archive file if also using the 'compress' param
    '''


    if (operation == 'tar'):
        tarRun(sourcePath, fullDestDir)

    elif (ruleFileConfig.operation == 'rsync'):
        rsyncRun(sourcePath, fullDestDir, rsyncFilepath)

# def changeDestinationDirectoryPermissions(destinationPath, backupDataPermissionsData):
#     logger.info("Updating file permissions for backup destination directory {}".format(destinationPath))
#     mypycommons.file.applyPermissionToPath(path=destinationPath, owner=backupDataPermissionsData['owner'], group=backupDataPermissionsData['group'], mask=backupDataPermissionsData['mask'], recursive=True)

def getFullDestinationDir(destinationRootDir: str, ruleName: str, destinationSubDir: str) -> str:
    ruleDestinationMainDir = mypycommons.file.joinPaths(destinationRootDir, ruleName)
    
    if (destinationSubDir):
        fullDestDir = mypycommons.file.joinPaths(ruleDestinationMainDir, destinationSubDir)
    else:
        fullDestDir = ruleDestinationMainDir
    
    if (not mypycommons.file.pathExists(fullDestDir)):
        mypycommons.file.createDirectory(fullDestDir)

    return fullDestDir

def runBackupRule(ruleConfig: config.PrefbackConfig_Rule, destinationRootDir: str, rsyncFilepath: str):
    '''
    '''
    logger.info("=====>Beginning Rule: {}".format(ruleConfig.name))

    if (ruleConfig.initScript):
        logger.info("Running the rule's configured init script")
        scriptFilepath = mypycommons.file.joinPaths(helpers.getProjectScriptsDir(), ruleConfig.initScript)
        runScript(scriptFilepath)

    for ruleFileConfig in ruleConfig.files:
        fullDestDir = getFullDestinationDir(destinationRootDir, ruleConfig.name, ruleFileConfig.destinationSubDir)

        logger.info("Starting file backup: '{}' to dir --> '{}'".format(ruleFileConfig.sourcePath, fullDestDir))
        performFileBackupStep(ruleFileConfig.sourcePath, fullDestDir, ruleFileConfig.operation, rsyncFilepath)

        # On Linux only:
        # Set the permissions on the destination path and the archive file within so that the user can read the backup
        # if (not runningWindowsOS):
        #     changeDestinationDirectoryPermissions(destinationDir, backupDataPermissions)

    if (ruleConfig.postScript):
        logger.info("Running the rule's configured post script")
        scriptFilepath = mypycommons.file.joinPaths(helpers.getProjectScriptsDir(), ruleConfig.postScript)
        runScript(scriptFilepath)


        
# ------------------------------------ Script 'main' execution -------------------------------------
if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    group = parser.add_mutually_exclusive_group()

    parser.add_argument("-c", '--config-file', 
        dest='configFilename',
        type=str,
        help="Name of the config file to use, located in this project's machine-config directory"
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
    mypycommons.logger.configureLoggerWithBasicSettings(loggerName=loggerName, logDir=helpers.getProjectLogsDir())

    # Get config
    configFilepath = mypycommons.file.joinPaths(helpers.getProjectConfigDir(), args.configFilename)
    prefbackConfig = config.PrefbakConfig(configFilepath)

    # ---------------------------
    # List rules, if arg is set
    if (args.listRules):
        for rule in prefbackConfig.rulesConfig:
            print(rule.name)
        sys.exit(0)

    logger.info("Starting prefbak backup routine")

    # ---------------------------
    # Run init script
    if (prefbackConfig.globalConfig.initScriptName):
        logger.info("Running the configured global init script")
        scriptFilepath = mypycommons.file.joinPaths(helpers.getProjectScriptsDir(), prefbackConfig.globalConfig.initScriptName)
        runScript(scriptFilepath, prefbackConfig)

    # ----------------------------
    # Perform backup
    if (args.runAllRules):
        backupRulesToRunConfig = prefbackConfig.rulesConfig
    else:
        backupRulesToRunConfig = [ruleCfg for ruleCfg in prefbackConfig.rulesConfig if (ruleCfg.name in args.runRuleNames)]
    
    backupRulesToRunNames = [rule.name for rule in backupRulesToRunConfig]
    logger.info("Starting routine for the given ({}) configured backup rules: {}".format(str(len(backupRulesToRunConfig)), str(backupRulesToRunNames)))

    for backupRuleConfig in backupRulesToRunConfig:
        runBackupRule(backupRuleConfig, prefbackConfig.globalConfig.destinationRootDir, prefbackConfig.globalConfig.rsyncFilepath)

    logger.info("Backup routine completed successfully")

    # ---------------------------
    # Run postrun script
    if (prefbackConfig.globalConfig.postScriptName):
        logger.info("Running the configured global post script")
        scriptFilepath = mypycommons.file.joinPaths(helpers.getProjectScriptsDir(), prefbackConfig.globalConfig.postScriptName)
        runScript(scriptFilepath, prefbackConfig)

    logger.info("All processes complete: prefbak operation finished successfully")




    