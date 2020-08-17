## Chizuhoru - screenshot tool for Linux  

![Paint preview](https://i.imgur.com/FM00k78.png)  

### Easy install  

```
git clone https://github.com/sertraline/chizuhoru && cd chizuhoru
./install.sh
```

`install.sh` will gather all required modules and will generate a `chizuhoru` launch script for you.  

You can bind PrtScr to it in your window manager to make use of global hotkey.

### Manual install  

Clone:  
`git clone https://github.com/sertraline/chizuhoru && cd chizuhoru`  

Install modules:  
`python3 -m pip install -r requirements.txt`  

Create launch script with following contents:
```
#!/bin/bash
python3 PATH/py/main.py \$* &
exit 0
```
Where `PATH` must be replaced with actual path to this directory.  

## Usage
 
- Run in GUI:
    ```shell
    ./chizuhoru
    ```   
- Make a silent screenshot, save to default directory:
    ```shell
    ./chizuhoru -s
    ```  
- Make a silent screenshot, save to directory provided:
    ```shell
    ./chizuhoru -s -dir /home/user/Pictures
    ```  
- Select display to grab. Default: -1 (all displays):
    ```shell
    ./chizuhoru -s -dis 0
    ```  
 
## Hotkeys

|  Keys                                                  |  Description                          |
|---                                                     |---                                    |
| <kbd>T</kbd> / <kbd>Right Mouse Button</kbd>           | Show/hide main panel                  |
| <kbd>Mouse wheel</kbd>                                 | Show/hide paint settings window       |
| <kbd>Esc</kbd>                                         | Cancel and close the window           |
| <kbd>Enter</kbd>                                       | Copy image or selection to clipboard  |
| <kbd>S</kbd>                                           | Save image or selection               |
| <kbd>A</kbd>                                           | Select window under the mouse pointer |
| <kbd>Ctrl</kbd> + <kbd>Z</kbd>                         | Undo                                  |
  

