'''
Script that performs a "prefbak" routine: that is, performs a backup of a machine according to the
backup rules defined in that machine's prefbak config file.
'''

from com.nwrobel import mypycommons
import com.nwrobel.mypycommons.file
import prefbak


# ------------------------------------ Script 'main' execution -------------------------------------
if __name__ == "__main__":

    # fs = mypycommons.file.GetAllFilesAndDirectoriesRecursive(rootPath="C:\\ProgramData\\Microsoft\\Windows\\Start Menu", includeRootPath=True)
    # for f in fs:
    #     print(f)
    print(prefbak.runningWindowsOS)
    prefbak.sourceDataMatchesExistingArchive("C:\\ProgramData\\Microsoft\\Windows\\Start Menu", "D:\\Temp\\[2020-10-29 18_24_10] Start Menu.archive.7z")
    #print(prefbak._getContentInfoForPath("C:\\ProgramData\\Microsoft\\Windows\\Start Menu"))
    #prefbak._getContentInfoFor7zArchive("Z:\\Device & App Backups\\copper\\AppData\\Start Menu\\[2020-10-29 17_09_09] Start Menu.archive.7z")
    
   




    