#!/bin/bash

date=`date +%F-%H%M%S`
tar cvfz jenkins-${date}.tgz /var/lib/jenkins
echo "Copy to s3"
aws s3 cp jenkins-${date}.tgz s3://datasink1/jenkins-backup/jenkins-${date}.tgz
rm jenkins-${date}.tgz
