## Chizuhoru - screenshot tool for Linux  

<img align="right" width="400" height="300" src="https://i.imgur.com/T1t3L2x.png">  


## Features:

- Edit screenshots!
- Silent screenshots with CLI
- Shadows!
- Anonymous upload to Imgur
- Custom uploads!

## Satisfying dependencies

### Packages

- Python **3.7+**
- XClip (read [Clipboard persistence](https://wiki.ubuntu.com/ClipboardPersistence))
  + `apt install xclip` for Ubuntu/Debian
  + `pacman -S xclip` for Arch Linux
- PyQt5
  + `apt install python3-pyqt5 pyqt5-dev-tools` for Ubuntu/Debian
  + `pacman -S pyqt5-common python-pyqt5` for Arch Linux
  + as for 2019, `python3 -m pip install PyQt5` also works fine.

### Modules
`python3 -m pip install -r requirements.txt`  

Manually:  
- Python Image Library
  + `python3 -m pip install Pillow`
- [Python MSS](https://github.com/BoboTiG/python-mss)
  + `python3 -m pip install mss`
- Python Aggdraw
  + `python3 -m pip install aggdraw` 
- Requests
  + `python3 -m pip install requests`  
- Notify2
  + `python3 -m pip install notify2`
  
## Usage

- Run in GUI:
    ```shell
    nohup python3 main.py
    ```  
- Make a silent fullscreen shot, copy to clipboard:
    ```shell
    python3 main.py -s
    ```  
- Set default directory instead of `/home/user/`. If present, <kbd>Enter</kbd> and <kbd>U</kbd> hotkeys will copy/upload image AND save it to the directory provided.
    ```shell
    python3 main.py -d /home/user/Pictures
    ```  
- Make a silent fullscreen shot, save to the directory:
    ```shell
    python3 main.py -s -d /home/user/Pictures
    ```  
- Launch from tray with hotkey: just re-run main.py script. A more convenient way would be to make a shell script, i.e Chizuhoru.sh, with these lines inside:
    ```shell
    #!/bin/sh
    python3 main.py &
    exit 0
    ```  
  
## Hotkeys

|  Keys                                                                     |  Description                     |
|---                                                                        |---                               |
| <kbd>T</kbd>                                                              | Show toolkit                     |
| <kbd>S</kbd>                                                              | Open save / upload dialog        |
| <kbd>Esc</kbd>                                                            | Exit                             |
| <kbd>Enter</kbd> | Copy selected rectangle to clipboard. If there is no selection, fullscreen will be copied |
| <kbd>U</kbd>                           | Upload selection to imgur and copy link to clipboard, same as Enter |
| <kbd>Ctrl</kbd> + <kbd>Z</kbd>                                            | Undo                             |
| <kbd>Mouse wheel</kbd>                                                    | Increase/decrease tool thickness |

## Compiling

Compiling python script saves some time at the first launch. You can do that by making:  
  ```shell
  python3 -m py_compile main.py overlay.py processing.py  
  ```  
  
Now you can check your `__pycache__` directory for .pyc files.

## Environments

Environments checked:  

- i3 WM + Compton
- Openbox WM + Compton
- XFCE
- Deepin DE
- KDE

## TODO

- [ ] Webdav uploads
- [ ] Remove spaghetti
- [x] Being not sure if I can accomplish that option above

## Frequently asked questions

**Q**: Why Python?  
**A**: uhhhhhhhhhhh...  
