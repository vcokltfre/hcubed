#!/bin/bash

git pull origin master

pm2 restart hcubed

# This script assumes you are on unix, running the bot using PM2 with the name hcubed.