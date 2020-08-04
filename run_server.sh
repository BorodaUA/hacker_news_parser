#!/bin/sh
if pgrep scrapyd; then pkill scrapyd; fi
if pgrep scrapydweb; then pkill scrapydweb; fi
rm -f twistd.pid
nohup scrapyd > /dev/null 2>&1 &
sleep 5
scrapydweb