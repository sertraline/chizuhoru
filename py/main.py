#!/usr/bin/python3
from argparse import ArgumentParser

from screenshot import ScreenshotCLI
from config import Config

from datetime import datetime
from os.path import join

from PyQt5 import QtWidgets
import setproctitle
import sys

if __name__ == '__main__':
    setproctitle.setproctitle('chizuhoru')

    ap = ArgumentParser()
    ap.add_argument("-s", "--screenshot", required=False, action='store_true',
                    help=("Take a screenshot, save to default directory. "
                          "Use -d to provide custom directory for saving."))
    ap.add_argument("-dir", "--directory", required=False,
                    help=("Save screenshot to path provided."))
    ap.add_argument("-dis", "--display", required=False,
                    help=("Select a display to grab. "
                          "[-1, 0, 1, 2, n] Default: -1 (all displays)"))
    args = vars(ap.parse_args())

    app_config = Config()

    display = -1 if not args["display"] else int(args["display"])
    if args["directory"]:
        app_config.changeConfig("default_dir", value=f"{args['directory']}",
                                save_changes=False)
    
    app = QtWidgets.QApplication(sys.argv)
    screen_unit = ScreenshotCLI()

    if args["screenshot"] == True:
        save_dir = app_config.parse['config']['default_dir']
        filename_format = app_config.parse['config']['filename_format']
        filename = "{}.png".format(datetime.now().strftime(filename_format))
        filepath = join(save_dir, filename)

        image = screen_unit.shot(mon=display)
        screen_unit.save(image, filepath)
        sys.exit()
    else:
        from chizuhoru import ChzInit
        ChzInit(app, app_config)