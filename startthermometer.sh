#!/bin/sh
# /etc/init.d/startthermometer.sh

### BEGIN INIT INFO
# Provides:          start7seg.sh
# Required-Start:    $remote_fs $syslog
# Required-Stop:     $remote_fs $syslog
# Default-Start:     2 3 4 5
# Default-Stop:      0 1 6
# Short-Description: Example initscript
# Description:       This service is used to start clock display
### END INIT INFO

sleep 30

case "$1" in
  start)
    echo "Starting thermometer.py"
    # run application you want to start
	python /home/pi/master/thermometer/thermometer.py &
    ;;
  stop)
    echo "Stopping thermometer.py"
    # kill application you want to stop
    killall thermometer.py
    ;;
  *)
    echo "Usage: /etc/init.d/startthermometer.sh {start|stop}"
    exit 1
    ;;
esac
 
exit 0
