import com.nwrobel.mypycommons.file
import com.nwrobel.mypycommons.system

import helpers

loggerName = 'prefbak-logger'
logger = mypycommons.logger.getLogger(loggerName)
runningWindowsOS = mypycommons.system.thisMachineIsWindowsOS()


class PrefbackConfig_Global:
    powershellDefaultFilepath = "C:\\Windows\\System32\\WindowsPowerShell\\v1.0\\powershell.exe"
    rsyncDefaultFilepathLinux = 'rsync'

    def __init__(self, destinationRootDir: str, powershellFilepath: str = None, rsyncFilepath: str = None, initScriptName: str = None, postScriptName: str = None):
        self.runningWindowsOS = runningWindowsOS

        # Set default powershell path if not provided
        if (not powershellFilepath):
            self.powershellFilepath = powershellDefaultFilepath
        else:    
            self.powershellFilepath = powershellFilepath 

        # Set the default rsync path, if not set, depending on OS
        if (not rsyncFilepath and self.runningWindowsOS):
            raise ValueError("rsync filepath is required for windows")

        if (not rsyncFilepath and not self.runningWindowsOS):
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

class PrefbackConfig_Rule:
    def __init__(self, name, initScript, postScript, files):
        if (not name):
            raise ValueError("Parameter name is required")
        if (not files):
            raise ValueError("Parameter files is required")
        
        self.name = name
        self.initScript = initScript
        self.postScript = postScript
        self.files = files

class PrefbackConfig_Rule_File:
    def __init__(self, sourcePath: str, operation: Literal['rsync', 'tar'], destinationSubDir: str = None):
        if (not sourcePath):
            raise ValueError("Parameter sourcePath is required")

        if (not mypycommons.file.pathExists(sourcePath)):
            raise FileNotFoundError("Parameter sourcePath does not exist")

        if (operation != 'rsync' and operation != 'tar'):
            raise ValueError("Parameter operation must be rsync or tar")

        if (runningWindowsOS and operation == 'tar'):
            raise ValueError("tar operation is not yet supported on windows")
        
        self.sourcePath = sourcePath
        self.operation = operation 
        self.destinationSubDir = destinationSubDir 

class PrefbakConfig:
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
            jsonDict['powershellFilepath'], 
            jsonDict['rsyncFilepath'], 
            jsonDict['initScript'], 
            jsonDict['postScript'], 
            jsonDict['destinationRootDir']
        )

        for ruleJson in rulesConfigJson:
            ruleFilesConfigs = []
            
            for ruleFileJson in ruleJson['files']:
                ruleFilesConfigs.append(
                    PrefbackConfig_Rule_File(ruleFileJson['sourcePath'], ruleFileJson['operation'], ruleFileJson['destinationSubDir'])
                )

            self.rulesConfig.append(
                PrefbackConfig_Rule(ruleJson['name'], ruleJson['initScript'], ruleJson['postScript'], ruleFilesConfigs)
            )