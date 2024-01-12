from com.nwrobel import mypycommons
from com.nwrobel.mypycommons import file


# ----------------------------- Script helper functions --------------------------------------------
def getProjectRootDir():
    currentDir = mypycommons.file.getThisScriptCurrentDirectory()
    return mypycommons.file.joinPaths(currentDir, '..')

def getProjectLogsDir():
    logsDir = mypycommons.file.joinPaths(getProjectRootDir(), '~logs')

    if (not mypycommons.file.pathExists(logsDir)):
        mypycommons.file.createDirectory(logsDir)
    
    return logsDir

def getProjectCacheDir():
    cacheDir = mypycommons.file.joinPaths(getProjectRootDir(), '~cache')

    if (not mypycommons.file.pathExists(cacheDir)):
        mypycommons.file.createDirectory(cacheDir)
    
    return cacheDir

def getProjectScriptsDir():
    scriptsDir = mypycommons.file.joinPaths(getProjectRootDir(), 'machine-scripts')

    if (not mypycommons.file.pathExists(scriptsDir)):
        raise FileNotFoundError("Project Scripts dir machine-scripts not found")
    
    return scriptsDir

def getProjectConfigDir():
    configDir = mypycommons.file.joinPaths(getProjectRootDir(), 'machine-config')

    if (not mypycommons.file.pathExists(configDir)):
        raise FileNotFoundError("Project config dir machine-config' not found")
    
    return configDir