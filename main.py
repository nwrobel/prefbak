import logging
import subprocess
import argparse
import sys
from typing import Literal, List

from com.nwrobel import mypycommons
import com.nwrobel.mypycommons.file
import com.nwrobel.mypycommons.time
import com.nwrobel.mypycommons.logger
import com.nwrobel.mypycommons.system
import com.nwrobel.mypycommons.archive

from src import helpers, config, prefbak

# Setup logging for this entire module/script
loggerName = 'prefbak-logger'
logger = mypycommons.logger.getLogger(loggerName)

# ------------------------------------ Script 'main' execution -------------------------------------
if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    group = parser.add_mutually_exclusive_group()

    parser.add_argument('configFilename', 
        type=str,
        help="Name of the config file to use, located in this project's machine-config directory"
    )
    group.add_argument('-l', '--list-rules', 
        action='store_true',
        dest='listRules',
        help="Print the rules names from the config file that can be run"
    )
    group.add_argument('-r', '--run-rules', 
        nargs='+', 
        default=[],
        dest='runRuleNames',
        help="One or more specific rule names, seperated by [space], of the rules you want to run"
    )
    group.add_argument("-a", "--run-all", 
        action='store_true',
        dest='runAllRules',
        help="Run all the rules set up in the config file"
    )

    args = parser.parse_args()

    # Configure logger
    mypycommons.logger.configureLoggerWithBasicSettings(loggerName=loggerName, logDir=helpers.getProjectLogsDir())

    # Get config
    configFilepath = mypycommons.file.joinPaths(helpers.getProjectConfigDir(), args.configFilename)
    app = prefbak.PrefbakApp(configFilepath)

    # # ---------------------------
    # # List rules, if arg is set
    # if (args.listRules):
    #     for rule in prefbackConfig.rulesConfig:
    #         print(rule.name)
    #     sys.exit(0)

    # logger.info("Starting prefbak backup routine")

    # # ---------------------------
    # # Run init script
    # if (prefbackConfig.globalConfig.initScriptName):
    #     logger.info("Running the configured global init script")
    #     scriptFilepath = mypycommons.file.joinPaths(helpers.getProjectScriptsDir(), prefbackConfig.globalConfig.initScriptName)
    #     runScript(scriptFilepath, prefbackConfig)

    # # ----------------------------
    # # Perform backup
    # if (args.runAllRules):
    #     backupRulesToRunConfig = prefbackConfig.rulesConfig
    # else:
    #     backupRulesToRunConfig = [ruleCfg for ruleCfg in prefbackConfig.rulesConfig if (ruleCfg.name in args.runRuleNames)]
    
    # backupRulesToRunNames = [rule.name for rule in backupRulesToRunConfig]
    # logger.info("Starting routine for the given ({}) configured backup rules: {}".format(str(len(backupRulesToRunConfig)), str(backupRulesToRunNames)))

    # for backupRuleConfig in backupRulesToRunConfig:
    #     runBackupRule(backupRuleConfig, prefbackConfig.globalConfig.destinationRootDir, prefbackConfig.globalConfig.rsyncFilepath)

    # logger.info("Backup routine completed successfully")

    # # ---------------------------
    # # Run postrun script
    # if (prefbackConfig.globalConfig.postScriptName):
    #     logger.info("Running the configured global post script")
    #     scriptFilepath = mypycommons.file.joinPaths(helpers.getProjectScriptsDir(), prefbackConfig.globalConfig.postScriptName)
    #     runScript(scriptFilepath, prefbackConfig)

    # logger.info("All processes complete: prefbak operation finished successfully")