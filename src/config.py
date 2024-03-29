from typing import Literal, List

from com.nwrobel import mypycommons
from com.nwrobel.mypycommons import (
    file,
    logger,
    system
)

from src import helpers

powershellDefaultFilepath = "C:\\Windows\\System32\\WindowsPowerShell\\v1.0\\powershell.exe"
rsyncDefaultFilepath = 'rsync'

class PrefbackConfig_Global():
    def __init__(self, destinationRootDir: str, powershellFilepath: str = None, rsyncFilepath: str = None, initScriptName: str = None, postScriptName: str = None):
        # Set defaults if not provided
        if (not powershellFilepath):
            self.powershellFilepath = powershellDefaultFilepath
        else:    
            self.powershellFilepath = powershellFilepath

        if (not rsyncFilepath):
            self.rsyncFilepath = rsyncDefaultFilepath
        else:
            self.rsyncFilepath = rsyncFilepath
             
        self.initScriptName = initScriptName
        self.postScriptName = postScriptName
        
        if (not destinationRootDir):
            raise ValueError("Parameter destinationRootDir is required")

        if (not mypycommons.file.pathExists(destinationRootDir)):
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
    def __init__(self, sourcePath: str, destinationDir: str, destinationSubDir: str):
        if (not sourcePath):
            raise ValueError("Parameter sourcePath is required") 

        if (not destinationDir and not destinationSubDir):
            raise ValueError("either destinationDir or destinationSubDir params are required")

        if (destinationDir and destinationSubDir):
            raise ValueError("destinationDir and destinationSubDir params cannot be used together")          
        
        self.sourcePath = sourcePath
        self.destinationDir = destinationDir
        self.destinationSubDir = destinationSubDir

class PrefbakConfig():
    def __init__(self, configFilepath):
        if (not mypycommons.file.pathExists(configFilepath)):
            raise FileNotFoundError("Config file not found")

        self.configFilepath = configFilepath
        self.globalConfig = None
        self.rulesConfig = []

        self._loadConfigFile()

    def _loadConfigFile(self):
        jsonDict = mypycommons.file.readJsonFile(self.configFilepath)

        globalConfigJson = jsonDict['global']
        rulesConfigJson = jsonDict['rules']

        self.globalConfig = PrefbackConfig_Global(
            powershellFilepath=self._getConfigKeyValue(globalConfigJson, 'powershellFilepath'),
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
                        destinationDir=self._getConfigKeyValue(ruleFileJson, 'destinationDir'),
                        destinationSubDir=self._getConfigKeyValue(ruleFileJson, 'destinationSubDir'),
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