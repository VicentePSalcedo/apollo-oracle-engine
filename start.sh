#!/bin/sh

touch /var/log/syslog

rsyslogd

cron

tail -f /var/log/syslog
