#!/bin/bash

version=$(python3 -V 2>&1 | grep -Po '(?<=Python )(.+)')
if [[ -z "$version" ]]
then
    echo "python3 -V: Python was not found." 
    exit 1
fi
parsedVersion=$(echo "${version//./}")
if [[ "$parsedVersion" -gt "370" ]]
then 
    echo "Python is fine:" $version
else
    echo "Abort: Python 3.7+ is required. Your version is" $version
    exit 1
fi
if python3 -c "import venv" &> /dev/null; then
    echo "virtualenv found."
else
    echo "no virtualenv found: installing..."
    python3 -m pip install virtualenv
fi
echo "Installing modules..."
python3 -m venv env
source env/bin/activate
python3 -m pip install -r requirements.txt
deactivate
SCRIPT_PATH=$(dirname $(realpath -s $0))
echo "Creating chizuhoru.sh..."
echo """
#!/bin/bash
source $SCRIPT_PATH/env/bin/activate
python3 $SCRIPT_PATH/py/main.py \$* &
deactivate
exit 0
""" > chizuhoru
chmod +x chizuhoru
exit 0
