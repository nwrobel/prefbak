#!/bin/bash

echo "Prefbak Init Script: starting script"
BACKUP_DIR=/home/nick/Temp/Prefbak-Backup

# reset backup dir
rm -rf $BACKUP_DIR
mkdir $BACKUP_DIR
sudo chown nick:nick $BACKUP_DIR
sudo chmod 770 $BACKUP_DIR

# Backup crontabs
crontab -l -u nick > $BACKUP_DIR/crontab-nick
sudo crontab -l > $BACKUP_DIR/crontab-root

# Backup ZFS zpool properties
sudo zfs get all datastore > $BACKUP_DIR/datastore-zfs-zpool-properties.txt

# Backup Piwigo database
mysqldump -r $BACKUP_DIR/piwigo-database.sql -u piwigouser --databases piwigo

# Remove cache data from Plex appdata so it won't get backed up
sudo service plexmediaserver stop
sudo rm -rf /var/lib/plexmediaserver/Library/Application\ Support/Plex\ Media\ Server/Cache/
sudo service plexmediaserver start

echo "Prefbak Init Script: all steps completed, exiting"