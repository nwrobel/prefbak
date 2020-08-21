#!/bin/bash

crontab -l > /home/nick/Temp/crontab-nick
sudo crontab -l > /home/nick/Temp/crontab-root

sudo zfs get all datastore > /home/nick/Temp/datastore-zfs-zpool-properties.txt

mysqldump -r /home/nick/Temp/piwigo-database.sql -u piwigouser --databases piwigo