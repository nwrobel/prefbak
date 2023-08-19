'''
'''

import logging
import subprocess
import argparse
import sys
import pathlib
import os
from typing import Literal, List

from com.nwrobel import mypycommons
from com.nwrobel.mypycommons import (
    file,
    time,
    logger,
    system,
    archive
)

from src import helpers, config

# Setup logging for this entire module/script
loggerName = 'prefbak-logger'
logger = mypycommons.logger.getLogger(loggerName)


class PrefbakApp:
    def __init__(self, configFilepath):
        self.config = config.PrefbakConfig(configFilepath)

    def run(self, ruleNames: List[str]):
        # ---------------------------
        # Run init script
        if (self.config.globalConfig.initScriptName):
            logger.info("Running the configured global init script")
            scriptFilepath = mypycommons.file.joinPaths(helpers.getProjectScriptsDir(), self.config.globalConfig.initScriptName)
            self._runScript(scriptFilepath)

        # ----------------------------
        # Perform backup
        logger.info("Starting routine for the given ({}) configured backup rules: {}".format(str(len(ruleNames)), str(ruleNames)))

        for ruleName in ruleNames:
            self._runBackupRule(ruleName)

        logger.info("Backup routine completed successfully")

        # ---------------------------
        # Run postrun script
        if (self.config.globalConfig.postScriptName):
            logger.info("Running the configured global post script")
            scriptFilepath = mypycommons.file.joinPaths(helpers.getProjectScriptsDir(), self.config.globalConfig.postScriptName)
            self._runScript(scriptFilepath)

    def _getBackupRule(self, ruleName):
        rules = [rule for rule in self.config.rulesConfig if (rule.name == ruleName)]
        if (not rules):
            raise ValueError("rule not found: {}".format(ruleName))
        
        return rules[0]

    def _runBackupRule(self, ruleName: str):
        '''
        '''
        ruleConfig = self._getBackupRule(ruleName)
        logger.info("=====>Beginning Rule: {}".format(ruleConfig.name))

        if (ruleConfig.initScriptName):
            logger.info("Running the rule's configured init script")
            scriptFilepath = mypycommons.file.joinPaths(helpers.getProjectScriptsDir(), ruleConfig.initScriptName)
            self._runScript(scriptFilepath)

        for ruleFileConfig in ruleConfig.fileConfigs:
            fullDestDir = self._getFullDestinationDir(self.config.globalConfig.destinationRootDir, ruleConfig.name, ruleFileConfig.destinationSubDir)

            logger.info("Starting file backup: '{}' to dir --> '{}'".format(ruleFileConfig.sourcePath, fullDestDir))
            self._runFileBackupStep(ruleFileConfig.sourcePath, fullDestDir, ruleFileConfig.operation)

            # On Linux only:
            # Set the permissions on the destination path and the archive file within so that the user can read the backup
            # if (not runningWindowsOS):
            #     changeDestinationDirectoryPermissions(destinationDir, backupDataPermissions)

        if (ruleConfig.postScriptName):
            logger.info("Running the rule's configured post script")
            scriptFilepath = mypycommons.file.joinPaths(helpers.getProjectScriptsDir(), ruleConfig.postScriptName)
            self._runScript(scriptFilepath)

    def _runScript(self, scriptFilepath: str):
        if (not mypycommons.file.pathExists(scriptFilepath)):
            raise FileNotFoundError("Error: The script '{}' does not exist".format(scriptFilepath))

        runningWindows = mypycommons.system.thisMachineIsWindowsOS()
        if (runningWindows):
            runArgs = [self.config.globalConfig.powershellFilepath, scriptFilepath]
        else:
            runArgs = [scriptFilepath]

        logger.info("Starting script: '{}'".format(scriptFilepath))
        subprocess.call(runArgs, shell=True)
        logger.info("Script execution complete")

    def _getFullDestinationDir(self, destinationRootDir: str, ruleName: str, destinationSubDir: str) -> str:
        ruleDestinationMainDir = mypycommons.file.joinPaths(destinationRootDir, ruleName)
        
        if (destinationSubDir):
            fullDestDir = mypycommons.file.joinPaths(ruleDestinationMainDir, destinationSubDir)
        else:
            fullDestDir = ruleDestinationMainDir
        
        if (not mypycommons.file.pathExists(fullDestDir)):
            mypycommons.file.createDirectory(fullDestDir)

        return fullDestDir

    def _rsyncRun(self, sourcePath: str, destinationDir: str):
        logger.info("Performing rsync of path '{}' to destination dir: '{}'".format(sourcePath, destinationDir))

        runArgs = [self.config.globalConfig.rsyncFilepath, '-aP', '--delete-after', sourcePath, destinationDir]
        subprocess.call(runArgs, shell=True)

    def _tarRun(sourcePath: str, destinationDir: str):
        currentTimestampStr = mypycommons.time.getCurrentTimestampForFilename()
        baseArchiveFilename = mypycommons.file.getFilename(sourcePath)

        tarArchiveName = '{} {}.tar'.format(currentTimestampStr, baseArchiveFilename) 
        tarArchiveFilepath = mypycommons.file.joinPaths(destinationDir, tarArchiveName)

        logger.info("Creating TAR archive: '{}'".format(tarArchiveFilepath))
        mypycommons.archive.createTarArchive(sourcePath, tarArchiveFilepath)

    def _teracopyRun(self, sourcePath: str, destinationDir: str):
        logger.info("Performing teracopy of path '{}' to destination dir: '{}'".format(sourcePath, destinationDir))

        runArgs = [self.config.globalConfig.teracopyFilepath, 'Copy', sourcePath, destinationDir, '/OverwriteOlder', '/Close']
        subprocess.call(runArgs, shell=True)

    def _runFileBackupStep(self, sourcePath: str, fullDestDir: str, operation: Literal['rsync', 'tar', 'teracopy']):
        '''
        '''
        if (operation == 'tar'):
            self._tarRun(sourcePath, fullDestDir)

        elif (operation == 'rsync'):
            self._rsyncRun(sourcePath, fullDestDir)

        elif (operation == 'teracopy'):
            self._teracopyRun(sourcePath, fullDestDir)


# # def changeDestinationDirectoryPermissions(destinationPath, backupDataPermissionsData):
# #     logger.info("Updating file permissions for backup destination directory {}".format(destinationPath))
# #     mypycommons.file.applyPermissionToPath(path=destinationPath, owner=backupDataPermissionsData['owner'], group=backupDataPermissionsData['group'], mask=backupDataPermissionsData['mask'], recursive=True)






        





    