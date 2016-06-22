./createservers.sh

sleep 2

{
	sleep 1
	echo IAMAT martha_hunt -7.607874+110.204051 1451072205.798801
	sleep 1
	echo quit

} | telnet localhost 8000

{
	sleep 1
	echo IAMAT cara_delevingne +20.634281-156.451321 1401077205.798801
	sleep 1
	echo quit
} | telnet localhost 8001

{
	sleep 1
	echo IAMAT yumi_lambert +37.322752-122.030836 1401078305.798801
	sleep 1
	echo quit
} | telnet localhost 8002

{
	sleep 1
	echo WHATSAT martha_hunt 45 5
	sleep 1
	echo quit
} | telnet localhost 8003

{
	sleep 1
	echo WHATSAT cara_delevingne 27 3
	sleep 1
	echo quit
} | telnet localhost 8004

pkill -f 'python server.py Alford'
pkill -f 'python server.py Bolden'
pkill -f 'python server.py Hamilton'
pkill -f 'python server.py Parker'
pkill -f 'python server.py Powell'
