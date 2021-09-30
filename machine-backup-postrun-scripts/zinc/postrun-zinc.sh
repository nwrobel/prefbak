#!/bin/bash

echo "Prefbak Post Run Script: starting script"

# reset backup dir
BACKUP_DIR=/home/nick/Temp/Prefbak-Backup
rm -rf $BACKUP_DIR

echo "Prefbak Post Run Script: all steps completed, exiting"