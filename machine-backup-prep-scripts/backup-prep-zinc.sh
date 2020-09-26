#!/bin/bash

# Backup crontabs
crontab -l > /home/nick/Temp/Backup/crontab-nick
sudo crontab -l > /home/nick/Temp/Backup/crontab-root

# Backup ZFS zpool properties
sudo zfs get all datastore > /home/nick/Temp/Backup/datastore-zfs-zpool-properties.txt

# Backup Piwigo database
mysqldump -r /home/nick/Temp/Backup/piwigo-database.sql -u piwigouser --databases piwigo

# Remove cache data from Plex appdata so it won't get backed up
sudo service plexmediaserver stop
sudo rm -rf /var/lib/plexmediaserver/Library/Application\ Support/Plex\ Media\ Server/Cache/
sudo service plexmediaserver start

# Clean up backups copied to Temp dir earlier
# sudo rm /home/nick/Temp/Backup/*