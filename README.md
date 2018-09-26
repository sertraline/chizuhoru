## Chizuhoru - screenshot tool for Linux

## Features:

- Edit screenshots!
- Silent screenshots with CLI
- Shadows!
- Anonymous upload to Imgur
- Custom uploads!

## Satisfying dependencies

### Packages

- Python **3.7**
- XClip (read [Clipboard persistence](https://wiki.ubuntu.com/ClipboardPersistence) )
  + `apt install xclip` for Ubuntu/Debian
  + `pacman -S xclip` for Arch Linux
- PyQt5
  + `apt install python3-pyqt5 pyqt5-dev-tools` for Ubuntu/Debian
  + `pacman -S pyqt5-common python-pyqt5` for Arch Linux

### Modules

- Python Image Library
  + `python3 -m pip install Pillow`
- [Python MSS](https://github.com/BoboTiG/python-mss)
  + `python3 -m pip install mss`
- Python Aggdraw
  + `python3 -m pip install aggdraw` 
- Requests
  + `python3 -m pip install requests`  
  
You can also easily install these modules by running `python3 -m pip install -r requirements.txt`.

Also it needs a composer to support transparency effects. If you are running DE, you will have one already. I'm running only WM, so I use compton.

## Usage

- Run in GUI:
    ```shell
    nohup python3 main.py
    ```  
- Make a silent fullscreen shot, copy to clipboard:
    ```shell
    python3 main.py -s
    ```  
- Set default directory:
    ```shell
    python3 main.py -d /home/user/Pictures
    ```  
- Make a silent fullscreen shot, save to the directory:
    ```shell
    python3 main.py -s -d /home/user/Pictures
    ```  
- Launch from tray with hotkey: just re-run main.py script. More convenient way would be to make a shell script, i.e Chizuhoru.sh, with these lines inside:
    ```shell
    #!/bin/sh
    nohup python3 main.py
    ```  
`Nohup` grants you that application will keep up running after closing your terminal emulator session. Then, you need to configure your DE to set your hotkey to launch this script. I use Openbox, so I need to put following contents inside my rc.xml:  

   ```shell
    $ nano ~/.config/openbox/rc.xml  
    <keybind key="Print">  
      <action name="Execute">  
        <command>/usr/bin/Chizuhoru.sh</command>  
      </action>  
    </keybind>  
   ```  

Now I can call Chizuhoru with PrintScreen hotkey.  

## Hotkeys

|  Keys                                                                     |  Description                     |
|---                                                                        |---                               |
| <kbd>T</kbd>                                                              | Show toolkit                     |
| <kbd>S</kbd>                                                              | Open save / upload dialog        |
| <kbd>Esc</kbd>                                                            | Exit                             |
| <kbd>Enter</kbd> | Copy selected rectangle to clipboard. If there is no selection, fullscreen will be copied |
| <kbd>Ctrl</kbd> + <kbd>Z</kbd>                                            | Undo                             |

## Compiling

Compiling python script saves some time at its first launch. You can do that by making:  
  ```shell
  python3 -m py_compile main.py overlay.py processing.py  
  ```  
  
Now you can check your `__pycache__` directory for the .pyc files.

## Where it works

I don't know, except for Arch Xfce/Openbox and Linux Mint Xfce. Neither I don't know if custom uploads work: I tested it only with plain text and html response.

## TODO

- [ ] Webdav uploads
- [ ] Remove spaghetti
- [x] Being not sure if I can accomplish that option above

## Frequently asked questions

**Q**: Why Python?  
**A**: uhhhhhhhhhhh...  


Icon is not mine, so all rights to this art belong to the [owner](http://theawkwardyeti.com/about/).
