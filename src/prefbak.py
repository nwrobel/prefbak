'''
'''

import logging
import subprocess
import argparse
import sys
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


# def runScript(scriptFilepath: str, config: config.PrefbakConfig):
#     if (not mypycommons.file.pathExists(scriptFilepath)):
#         raise FileNotFoundError("Error: The script '{}' does not exist".format(scriptFilepath))

#     if (config.globalConfig.runningWindowsOS):
#         runArgs = [config.globalConfig.powershellFilepath, scriptFilepath]
#     else:
#         runArgs = [scriptFilepath]

#     logger.info("Starting script: '{}'".format(scriptFilepath))
#     subprocess.call(runArgs, shell=True)
#     logger.info("Script execution complete")



# def rsyncRun(sourcePath: str, destinationDir: str, rsyncFilepath: str):
#     logger.info("Performing rsync to destination dir: '{}'".format(destinationDir))

#     runArgs = [rsyncFilepath, '-aP', '--delete-after', sourcePath, destinationDir]
#     subprocess.call(runArgs, shell=True)

# def tarRun(sourcePath: str, destinationDir: str):
#     currentTimestampStr = mypycommons.time.getCurrentTimestampForFilename()
#     baseArchiveFilename = mypycommons.file.getFilename(sourcePath)

#     tarArchiveName = '{} {}.tar'.format(currentTimestampStr, baseArchiveFilename) 
#     tarArchiveFilepath = mypycommons.file.joinPaths(destinationDir, tarArchiveName)

#     logger.info("Creating TAR archive: '{}'".format(tarArchiveFilepath))
#     mypycommons.archive.createTarArchive(sourcePath, tarArchiveFilepath)

# def performRuleFileBackupStep(sourcePath: str, fullDestDir: str, operation: Literal['rsync', 'tar'], rsyncFilepath: str):
#     '''
#     Performs a single backup operation. Files can either be mirrored/copied from the source path to 
#     the destination path, or an archive file at the destination path can be made from the source
#     file.

#     Params:
#         sourcePath: single filepath (file or directory) to use as the backup source
#         destinationDir: destination dir to use as the destination/backup 
#             location. Use the name of the archive file if also using the 'compress' param
#     '''


#     if (operation == 'tar'):
#         tarRun(sourcePath, fullDestDir)

#     elif (ruleFileConfig.operation == 'rsync'):
#         rsyncRun(sourcePath, fullDestDir, rsyncFilepath)

# # def changeDestinationDirectoryPermissions(destinationPath, backupDataPermissionsData):
# #     logger.info("Updating file permissions for backup destination directory {}".format(destinationPath))
# #     mypycommons.file.applyPermissionToPath(path=destinationPath, owner=backupDataPermissionsData['owner'], group=backupDataPermissionsData['group'], mask=backupDataPermissionsData['mask'], recursive=True)

# def getFullDestinationDir(destinationRootDir: str, ruleName: str, destinationSubDir: str) -> str:
#     ruleDestinationMainDir = mypycommons.file.joinPaths(destinationRootDir, ruleName)
    
#     if (destinationSubDir):
#         fullDestDir = mypycommons.file.joinPaths(ruleDestinationMainDir, destinationSubDir)
#     else:
#         fullDestDir = ruleDestinationMainDir
    
#     if (not mypycommons.file.pathExists(fullDestDir)):
#         mypycommons.file.createDirectory(fullDestDir)

#     return fullDestDir

# def runBackupRule(ruleConfig: config.PrefbackConfig_Rule, destinationRootDir: str, rsyncFilepath: str):
#     '''
#     '''
#     logger.info("=====>Beginning Rule: {}".format(ruleConfig.name))

#     if (ruleConfig.initScript):
#         logger.info("Running the rule's configured init script")
#         scriptFilepath = mypycommons.file.joinPaths(helpers.getProjectScriptsDir(), ruleConfig.initScript)
#         runScript(scriptFilepath)

#     for ruleFileConfig in ruleConfig.files:
#         fullDestDir = getFullDestinationDir(destinationRootDir, ruleConfig.name, ruleFileConfig.destinationSubDir)

#         logger.info("Starting file backup: '{}' to dir --> '{}'".format(ruleFileConfig.sourcePath, fullDestDir))
#         performFileBackupStep(ruleFileConfig.sourcePath, fullDestDir, ruleFileConfig.operation, rsyncFilepath)

#         # On Linux only:
#         # Set the permissions on the destination path and the archive file within so that the user can read the backup
#         # if (not runningWindowsOS):
#         #     changeDestinationDirectoryPermissions(destinationDir, backupDataPermissions)

#     if (ruleConfig.postScript):
#         logger.info("Running the rule's configured post script")
#         scriptFilepath = mypycommons.file.joinPaths(helpers.getProjectScriptsDir(), ruleConfig.postScript)
#         runScript(scriptFilepath)


        





    