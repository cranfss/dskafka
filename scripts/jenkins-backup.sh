#!/bin/bash
#
# Copy to /etc/cron.daily and add to crontab -e
# [ec2-user@ip-172-31-19-73 cron.daily]$ crontab -e
# 0 0 * * * /etc/cron.daily/jenkins-backup.sh 

date=`date +%F-%H%M%S`
tar cvfz jenkins-${date}.tgz /var/lib/jenkins
echo "Copy to s3"
aws s3 cp jenkins-${date}.tgz s3://datasink1/jenkins-backup/jenkins-${date}.tgz
rm jenkins-${date}.tgz
