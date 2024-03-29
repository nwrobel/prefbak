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

# ---------------------------------- Script 'main' execution -------------------------------------
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

    try:
        # Get config
        configFilepath = mypycommons.file.joinPaths(helpers.getProjectConfigDir(), args.configFilename)

        # Set up logger
        loggerWrapper = mypycommons.logger.CommonLogger(
            loggerName="prefbak-logger", 
            logDir=helpers.getProjectLogsDir(), 
            logFilename="prefbak.log"
        )
        logger = loggerWrapper.getLogger()
        app = prefbak.PrefbakApp(configFilepath, loggerWrapper)

        # ---------------------------
        # List rules, if arg is set
        if (args.listRules):
            for rule in app.config.rulesConfig:
                print(rule.name)
            sys.exit(0)

        if (args.runAllRules):
            backupRulesToRunConfig = app.config.rulesConfig
        else:
            backupRulesToRunConfig = [ruleCfg for ruleCfg in app.config.rulesConfig if (ruleCfg.name in args.runRuleNames)]
        
        backupRulesToRunNames = [rule.name for rule in backupRulesToRunConfig]
        app.run(backupRulesToRunNames)

        logger.info("All processes complete: prefbak operation finished successfully")

    except Exception as ex:
        logger.exception(ex)
        logger.error("process ended with errors")

