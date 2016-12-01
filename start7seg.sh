#!/bin/sh
# /etc/init.d/start7seg.sh

### BEGIN INIT INFO
# Provides:          start7seg.sh
# Required-Start:    $remote_fs $syslog
# Required-Stop:     $remote_fs $syslog
# Default-Start:     2 3 4 5
# Default-Stop:      0 1 6
# Short-Description: Example initscript
# Description:       This service is used to start clock display
### END INIT INFO

case "$1" in
  start)
    echo "Starting 7seg.py"
    # run application you want to start
	python /home/pi/master/7seg/7seg.py
    ;;
  stop)
    echo "Stopping 7seg.py"
    # kill application you want to stop
    killall 7seg.py
    ;;
  *)
    echo "Usage: /etc/init.d/start7seg.sh {start|stop}"
    exit 1
    ;;
esac
 
exit 0
