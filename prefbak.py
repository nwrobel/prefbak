'''
Script that performs a "prefbak" routine: that is, performs a backup of a machine according to the
backup rules defined in that machine's prefbak config file.
'''

from com.nwrobel import mypycommons
import com.nwrobel.mypycommons.file

def performBackupStep(sourcePath, destinationPath, compress=False):
    '''
    Performs a single backup operation. Files can either be mirrored/copied from the source path to 
    the destination path, or an archive file at the desintation path can be made from the source
    file.

    Params:
        sourcePath: single filepath (file or directory) to use as the backup source
        destinationPath: single filepath (file or directory) to use as the destination/backup 
            location. Use the name of the archive file if also using the 'compress' param
        compress: whether or not to create an archive from the source path. Default is False
    '''
    if (compress):
        archiveName = '[{}] {}.backup.7z'.format(
            mypycommons.time.getCurrentTimestampForFilename(), 
            mypycommons.file.getFileBaseName(sourcePath)
        ) 
        archiveDestFilepath = mypycommons.file.joinPaths(destinationPath, archiveName)
        mypycommons.file.compressToArchive(sourcePath, archiveDestFilepath)

    else:
        subprocess.call(['rsync', '-avh', '--delete', sourcePath, destinationPath])

def performBackup(configFile):
    '''
    Reads the given backup config file and performs each backup from the definitions.

    Params:
        configFile: the Json prefbak config file
    '''
    for backupConfigEntry in backupConfig:
        sourcePath = backupConfigEntry['sourcePath']
        destinationPath = joinPaths(backupRootDir, backupConfigEntry['backupPath'])
        compressBackup = backupConfigEntry['compress']

        if (compressBackup == 'yes'):
            performBackupStep(sourcePath, destinationPath, compress=True)
        else:
            performBackupStep(sourcePath, destinationPath)

if __name__ == "__main__":

    # For now, set the computer name here along with the backup destination dir
    # This will be a script param and a part of the backup config file, respectfully (TODO)
    computerName = 'zinc'
    backupRootDir = '/datastore/nick/Device & App Backups/zinc'

    backupConfigName = '{}.config.json'.format(computerName)
    backupConfigFilePath = mypycommons.file.readJsonFile(mypycommons.file.joinPaths('machine-config', backupConfigName))

    performBackup(backupConfigFilePath)









    