#!/bin/bash

version=$(python3 -V 2>&1 | grep -Po '(?<=Python )(.+)')
try_another=$(python3.7 -V 2>&1 | grep -Po '(?<=Python )(.+)')
pyt="python3"
if [[ -z "$version" ]];
then
    echo "python3 -V: Python was not found.";
    exit 1;
fi;
parsedVersion=$(echo "${version//./}")
if [[ "$parsedVersion" -gt "370" ]];
then 
    echo "Python is fine:" $version;
    pyt="python3";
else
    parsedVersion=$(echo "${try_another//./}");
    if [[ "$parsedVersion" -gt "370" ]];
    then
        echo "Python is fine:" $try_another;
	pyt="python3.7";
    else
        echo "Abort: Python 3.7+ is required. Your version is" $version;
        exit 1;
    fi;
fi;
# using virtualenv we lose 'Breeze' system style
$pyt -m pip install mss requests PyQt5 Xlib setproctitle --user
SCRIPT_PATH=$(dirname $(realpath -s $0))
echo "Creating chizuhoru.sh..."
echo """#!/bin/bash
$pyt $SCRIPT_PATH/py/main.py \$* &
exit 0
""" > chizuhoru
chmod +x chizuhoru
exit 0

