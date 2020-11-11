## Chizuhoru - screenshot tool for Linux  

<p align="center">
  <img src="https://i.imgur.com/UGpRwIs.png" />
</p>

## Features
- Editor: painting, shapes, cropping, blur
- Magnifier
- Standalone uploader: imgur, catbox, uguu
- Screenshot uploads
- History
  - Imgur links are stored with delete hash. Delete hash allows you to remove image from Imgur. You can access it through context menu on any Imgur item.

### Can I see it in action?
[demo](https://i.imgur.com/1PC34J5.gif?raw=True) (gif, 5MB)

### Easy install  

```
git clone https://github.com/sertraline/chizuhoru && cd chizuhoru
./install.sh
```

`install.sh` will gather all required modules and will generate a `chizuhoru` launch script for you. You can bind PrtScr to it in your window manager to make use of global hotkey.

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
| <kbd>T</kbd>                                           | Show/hide main panel                  |
| <kbd>Right Mouse Button</kbd>                          | Show/hide paint settings window       |
| <kbd>Esc</kbd>                                         | Cancel and close the window           |
| <kbd>Enter</kbd>                                       | Copy image or selection to clipboard  |
| <kbd>S</kbd>                                           | Save image or selection               |
| <kbd>A</kbd>                                           | Select window under the mouse pointer |
| <kbd>Z</kbd>                                           | Toggle magnifier                      |
| <kbd>Ctrl</kbd> + <kbd>Z</kbd>                         | Undo                                  |
| <kbd>Hold shift while drawing</kbd>                    | Constraint key: ensure drawn shape has equal sides |
| <kbd>1</kbd>                                           | Selection                             |
| <kbd>2</kbd>                                           | Pen                                   |
| <kbd>3</kbd>                                           | Circle                                |
| <kbd>4</kbd>                                           | Rectangle                             |
| <kbd>5</kbd>                                           | Line                                  |
| <kbd>6</kbd>                                           | Smooth line                           |
| <kbd>7</kbd>                                           | Blur                                  |
