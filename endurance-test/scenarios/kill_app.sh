#!/bin/sh
echo "start ..."
running_apps=$(dumpsys activity activities | grep "Hist" | grep -oE "[^ ]+/[^ ]+" | awk -F/ '{print $1}' | sort | uniq)
for app in $running_apps;do
    echo "Closing $app"
    am force-stop $app
done

