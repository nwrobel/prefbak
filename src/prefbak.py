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

class PrefbakApp:
    def __init__(self, configFilepath, loggerWrapper: mypycommons.logger.CommonLogger):
        self.config = config.PrefbakConfig(configFilepath)
        self._logger = loggerWrapper.getLogger()

    def run(self, ruleNames: List[str]):
        # ---------------------------
        # Run init script
        if (self.config.globalConfig.initScriptName):
            self._logger.info("Running the configured global init script")
            scriptFilepath = mypycommons.file.joinPaths(helpers.getProjectScriptsDir(), self.config.globalConfig.initScriptName)
            self._runScript(scriptFilepath)

        # ----------------------------
        # Perform backup
        self._logger.info("Starting routine for the given ({}) configured backup rules: {}".format(str(len(ruleNames)), str(ruleNames)))

        for ruleName in ruleNames:
            self._runBackupRule(ruleName)

        self._logger.info("Backup routine completed successfully")

        # ---------------------------
        # Run postrun script
        if (self.config.globalConfig.postScriptName):
            self._logger.info("Running the configured global post script")
            scriptFilepath = mypycommons.file.joinPaths(helpers.getProjectScriptsDir(), self.config.globalConfig.postScriptName)
            self._runScript(scriptFilepath)

    def _getBackupRule(self, ruleName) -> config.PrefbackConfig_Rule:
        rules = [rule for rule in self.config.rulesConfig if (rule.name == ruleName)]
        if (not rules):
            raise ValueError("rule not found: {}".format(ruleName))
        
        return rules[0]

    def _runBackupRule(self, ruleName: str):
        '''
        '''
        ruleConfig = self._getBackupRule(ruleName)
        self._logger.info("=====>Beginning Rule: {}".format(ruleConfig.name))

        if (ruleConfig.initScriptName):
            self._logger.info("Running the rule's configured init script")
            scriptFilepath = mypycommons.file.joinPaths(helpers.getProjectScriptsDir(), ruleConfig.initScriptName)
            self._runScript(scriptFilepath)

        for ruleFileConfig in ruleConfig.fileConfigs:
            # Check source path
            if (not mypycommons.file.pathExists(ruleFileConfig.sourcePath)):
                raise FileExistsError("source path not found: rule '{}', {}".format(ruleConfig.name, ruleFileConfig.sourcePath))

            if (ruleFileConfig.destinationDir):
                fullDestDir = ruleFileConfig.destinationDir
            else:
                fullDestDir = mypycommons.file.joinPaths(self.config.globalConfig.destinationRootDir, ruleFileConfig.destinationSubDir)

            if (not mypycommons.file.pathExists(fullDestDir)):
                mypycommons.file.createDirectory(fullDestDir)

            self._logger.info("Starting file backup: '{}' to dir --> '{}'".format(ruleFileConfig.sourcePath, fullDestDir))
            self._runFileBackupStep(ruleFileConfig.sourcePath, fullDestDir)

        if (ruleConfig.postScriptName):
            self._logger.info("Running the rule's configured post script")
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

        self._logger.info("Starting script: '{}'".format(scriptFilepath))
        subprocess.call(runArgs, shell=True)
        self._logger.info("Script execution complete")

    def _runFileBackupStep(self, sourcePath: str, fullDestDir: str):
        '''
        '''
        runningWindows = mypycommons.system.thisMachineIsWindowsOS()
        if (runningWindows):
            self._robocopyRun(sourcePath, fullDestDir)        
        else:
            self._rsyncRun(sourcePath, fullDestDir)

    def _rsyncRun(self, sourcePath: str, destinationDir: str):
        self._logger.info("Performing rsync of path '{}' to destination dir: '{}'".format(sourcePath, destinationDir))

        # If source path is directory, we want to copy the contents of that dir (not the dir itself)
        # so we add a trailing / to the dir name
        if (mypycommons.file.isDirectory(sourcePath) and sourcePath[-1] != '/'):
            sourcePath += '/'

        runArgs = [self.config.globalConfig.rsyncFilepath, '-aP', '--delete-after', sourcePath, destinationDir]
        subprocess.call(runArgs)

    def _robocopyRun(self, sourcePath: str, destinationDir: str):
        self._logger.info("Performing robocopy of path '{}' to destination dir: '{}'".format(sourcePath, destinationDir))

        if (mypycommons.file.isFile(sourcePath)):
            sourceFilename = mypycommons.file.getFilename(sourcePath)
            sourceFileDir = sourcePath.replace(sourceFilename, '')
            runArgs = ['robocopy', sourceFileDir, destinationDir, sourceFilename, '/COPY:DT', '/NFL', '/NDL', '/r:0', '/w:0']

        else:
            runArgs = ['robocopy', sourcePath, destinationDir, '/mir', '/COPY:DT', '/NFL', '/NDL', '/r:0', '/w:0']

        subprocess.call(runArgs, shell=True)
            




        





    