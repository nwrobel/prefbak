from typing import Literal, List

from com.nwrobel import mypycommons
from com.nwrobel.mypycommons import (
    file,
    logger,
    system
)

from src import helpers

loggerName = 'prefbak-logger'
logger = mypycommons.logger.getLogger(loggerName)

powershellDefaultFilepath = "C:\\Windows\\System32\\WindowsPowerShell\\v1.0\\powershell.exe"
teracopyDefaultFilepath = "C:\\Program Files\\TeraCopy\\TeraCopy.exe"
rsyncDefaultFilepath = 'rsync'

class PrefbackConfig_Global():
    def __init__(self, destinationRootDir: str, powershellFilepath: str = None, teracopyFilepath: str = None, rsyncFilepath: str = None, initScriptName: str = None, postScriptName: str = None):
        # Set defaults if not provided
        if (not powershellFilepath):
            self.powershellFilepath = powershellDefaultFilepath
        else:    
            self.powershellFilepath = powershellFilepath

        if (not teracopyFilepath):
            self.teracopyFilepath = teracopyDefaultFilepath
        else:    
            self.teracopyFilepath = teracopyFilepath

        if (not rsyncFilepath):
            self.rsyncFilepath = rsyncDefaultFilepath
        else:
            self.rsyncFilepath = rsyncFilepath
             
        self.initScriptName = initScriptName
        self.postScriptName = postScriptName
        
        if (not destinationRootDir):
            raise ValueError("Parameter destinationRootDir is required")

        if (not mypycommons.file.pathExists(destinationRootDir)):
            logger.info("Backup destination root directory '{}' does not exist: creating it".format(destinationRootDir))
            mypycommons.file.createDirectory(destinationRootDir)

        self.destinationRootDir = destinationRootDir

class PrefbackConfig_Rule():
    def __init__(self, name, initScriptName, postScriptName, fileConfigs):
        if (not name):
            raise ValueError("Parameter name is required")
        if (not fileConfigs):
            raise ValueError("Parameter files is required")
        
        self.name = name
        self.initScriptName = initScriptName
        self.postScriptName = postScriptName
        self.fileConfigs = fileConfigs

class PrefbackConfig_Rule_File():
    def __init__(self, sourcePath: str, destinationSubDir: str, operation: Literal['rsync', 'tar', 'teracopy']):
        if (not sourcePath):
            raise ValueError("Parameter sourcePath is required")

        if (operation != 'rsync' and operation != 'tar' and operation != 'teracopy'):
            raise ValueError("Parameter operation must be one of: rsync,tar,teracopy")

        runningWindows = mypycommons.system.thisMachineIsWindowsOS()
        if (runningWindows):
            if (operation == 'tar' or operation == 'rsync'):
                raise ValueError("only teracopy operation is currently supported on windows")
        else:
            if (operation == 'teracopy'):
                raise ValueError("only rsync/tar operation is supported on linux")            
        
        self.sourcePath = sourcePath
        self.operation = operation 
        self.destinationSubDir = destinationSubDir 

class PrefbakConfig():
    def __init__(self, configFilepath):
        if (not mypycommons.file.pathExists(configFilepath)):
            raise FileNotFoundError("Config file not found")

        self.configFilepath = configFilepath
        self.globalConfig = None
        self.rulesConfig = []

        logger.info("Loading prefbak config file: {}".format(configFilepath))
        self._loadConfigFile()

    def _loadConfigFile(self):
        jsonDict = mypycommons.file.readJsonFile(self.configFilepath)

        globalConfigJson = jsonDict['global']
        rulesConfigJson = jsonDict['rules']

        self.globalConfig = PrefbackConfig_Global(
            powershellFilepath=self._getConfigKeyValue(globalConfigJson, 'powershellFilepath'),
            teracopyFilepath=self._getConfigKeyValue(globalConfigJson, 'teracopyFilepath'),
            rsyncFilepath=self._getConfigKeyValue(globalConfigJson, 'rsyncFilepath'),
            initScriptName=self._getConfigKeyValue(globalConfigJson, 'initScript'),
            postScriptName=self._getConfigKeyValue(globalConfigJson, 'postScript'),
            destinationRootDir=self._getConfigKeyValue(globalConfigJson, 'destinationRootDir')
        )

        for ruleJson in rulesConfigJson:
            ruleFilesConfigs = []
            
            for ruleFileJson in ruleJson['files']:
                ruleFilesConfigs.append(
                    PrefbackConfig_Rule_File(
                        sourcePath=self._getConfigKeyValue(ruleFileJson, 'sourcePath'), 
                        destinationSubDir=self._getConfigKeyValue(ruleFileJson, 'destinationSubDir'),
                        operation=self._getConfigKeyValue(ruleFileJson, 'operation')
                    )
                )

            self.rulesConfig.append(
                PrefbackConfig_Rule(
                    name=self._getConfigKeyValue(ruleJson, 'name'), 
                    initScriptName=self._getConfigKeyValue(ruleJson, 'initScript'), 
                    postScriptName=self._getConfigKeyValue(ruleJson, 'postScript'), 
                    fileConfigs=ruleFilesConfigs)
            )
    
    def _getConfigKeyValue(self, jsonDict, keyName):
        try:
            return jsonDict[keyName]
        except KeyError:
            return None