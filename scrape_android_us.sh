#!/bin/bash
SCRIPTNAME=`basename $0`
PIDFILE=${SCRIPTNAME}.pid

if [ -f ${PIDFILE} ]; then
   #verify if the process is actually still running under this pid
   OLDPID=`cat ${PIDFILE}`
   RESULT=`ps -ef | grep ${OLDPID} | grep ${SCRIPTNAME}`

   if [ -n "${RESULT}" ]; then
        echo "Script already running! Exiting"
     exit 255
   fi
fi

#grab pid of this process and update the pid file with it
PID=`ps -ef | grep ${SCRIPTNAME} | head -n1 |  awk ' {print $2;} '`
echo ${PID} > ${PIDFILE}

PHANTOM_PATH='/home/ec2-user/phantomjs-2.1.1-linux-x86_64/bin/phantomjs'
SCRIPT_PATH='/home/ec2-user/think/phantom-grabber/gplay-topgrossing.js'

US_PROXY_STRING=''

# United States
PAID_OUTPUT_FILE='/home/ec2-user/think/phantom-grabber/us_paid_output.html'
FREE_OUTPUT_FILE='/home/ec2-user/think/phantom-grabber/us_free_output.html'
GROSSING_OUTPUT_FILE='/home/ec2-user/think/phantom-grabber/us_grossing_output.html'
${PHANTOM_PATH} ${US_PROXY_STRING} ${SCRIPT_PATH} paid ${PAID_OUTPUT_FILE};
sleep 5;
${PHANTOM_PATH} ${US_PROXY_STRING} ${SCRIPT_PATH} free ${FREE_OUTPUT_FILE};
sleep 8;
${PHANTOM_PATH} ${US_PROXY_STRING} ${SCRIPT_PATH} grossing ${GROSSING_OUTPUT_FILE};
python27 /home/ec2-user/think/manage.py process_gplay_feeds 91 92 93;
