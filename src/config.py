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
rsyncDefaultFilepathLinux = 'rsync'

class PrefbackConfig_Global():
    def __init__(self, destinationRootDir: str, powershellFilepath: str = None, rsyncFilepath: str = None, initScriptName: str = None, postScriptName: str = None):
        # Set default powershell path if not provided
        if (not powershellFilepath):
            self.powershellFilepath = powershellDefaultFilepath
        else:    
            self.powershellFilepath = powershellFilepath 

        # Set the default rsync path, if not set, depending on OS
        runningWindows = mypycommons.system.thisMachineIsWindowsOS()
        if (not rsyncFilepath and runningWindows):
            raise ValueError("rsync filepath is required for windows")

        if (not rsyncFilepath and not runningWindows):
            self.rsyncFilepath = rsyncDefaultFilepathLinux
        else:
            self.rsyncFilepath = rsyncFilepath
             
        self.initScriptName = initScriptName
        self.postScriptName = postScriptName
        
        if (not destinationRootDir):
            raise ValueError("Parameter destinationRootDir is required")

        if (not mypycommons.file.pathExists(destinationRootDir)):
            logger.info("Backup destination directory '{}' does not exist: creating it".format(destinationRootDir))
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
    def __init__(self, sourcePath: str, destinationSubDir: str, operation: Literal['rsync', 'tar']):
        if (not sourcePath):
            raise ValueError("Parameter sourcePath is required")

        if (operation != 'rsync' and operation != 'tar'):
            raise ValueError("Parameter operation must be rsync or tar")

        runningWindows = mypycommons.system.thisMachineIsWindowsOS()
        if (runningWindows and operation == 'tar'):
            raise ValueError("tar operation is not yet supported on windows")
        
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
            powershellFilepath=self.getConfigKeyValue(globalConfigJson, 'powershellFilepath'),
            rsyncFilepath=self.getConfigKeyValue(globalConfigJson, 'rsyncFilepath'),
            initScriptName=self.getConfigKeyValue(globalConfigJson, 'initScript'),
            postScriptName=self.getConfigKeyValue(globalConfigJson, 'postScript'),
            destinationRootDir=self.getConfigKeyValue(globalConfigJson, 'destinationRootDir')
        )

        for ruleJson in rulesConfigJson:
            ruleFilesConfigs = []
            
            for ruleFileJson in ruleJson['files']:
                ruleFilesConfigs.append(
                    PrefbackConfig_Rule_File(
                        sourcePath=self.getConfigKeyValue(ruleFileJson, 'sourcePath'), 
                        destinationSubDir=self.getConfigKeyValue(ruleFileJson, 'destinationSubDir'),
                        operation=self.getConfigKeyValue(ruleFileJson, 'operation')
                    )
                )

            self.rulesConfig.append(
                PrefbackConfig_Rule(
                    name=self.getConfigKeyValue(ruleJson, 'name'), 
                    initScriptName=self.getConfigKeyValue(ruleJson, 'initScript'), 
                    postScriptName=self.getConfigKeyValue(ruleJson, 'postScript'), 
                    fileConfigs=ruleFilesConfigs)
            )
    
    def getConfigKeyValue(self, jsonDict, keyName):
        try:
            return jsonDict[keyName]
        except KeyError:
            return None