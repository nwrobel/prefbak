import com.nwrobel.mypycommons.file


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

def getProjectScriptsDir():
    currentDir = mypycommons.file.getThisScriptCurrentDirectory()
    scriptsDir = mypycommons.file.joinPaths(currentDir, 'machine-scripts')

    if (not mypycommons.file.pathExists(scriptsDir)):
        raise FileNotFoundError("Project Scripts dir machine-scripts not found")
    
    return scriptsDir

def getProjectConfigDir():
    currentDir = mypycommons.file.getThisScriptCurrentDirectory()
    configDir = mypycommons.file.joinPaths(currentDir, 'machine-config')

    if (not mypycommons.file.pathExists(configDir)):
        raise FileNotFoundError("Project config dir machine-config' not found")
    
    return configDir

def getProjectBinDir():
    currentDir = mypycommons.file.getThisScriptCurrentDirectory()
    binDir = mypycommons.file.joinPaths(currentDir, 'bin')

    if (not mypycommons.file.pathExists(binDir)):
        raise FileNotFoundError("Project bin dir not found")
    
    return binDir