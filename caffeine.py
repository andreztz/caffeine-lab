#!/usr/bin/env python

import sys
import time
import itertools
import threading

from configparser import ConfigParser
from functools import partial
from pathlib import Path

import appdirs
from pyautogui import press

APPNAME = "caffeine-lab"

DEFAULTS = {
    "animation_chars": r"/-\|",
    "keys": "ctrl",
    "inhibitor_time": 60,
    "animation_sleep": 0.1,
}


class Signal:
    terminate = False


class Config(ConfigParser):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.read(self.get_config_file())

    def get_config_file(self):
        config_file = Path(appdirs.user_config_dir(appname=APPNAME)).joinpath(
            "config.ini"
        )
        return str(config_file)


def animate(chars, sleep, signal):

    for c in itertools.cycle(chars):
        msg = c
        sys.stdout.write(msg)
        sys.stdout.flush()
        sys.stdout.write("\x08" * len(msg))
        if signal.terminate:
            break
        time.sleep(sleep)


def inhibitor(seconds, keys):
    func = partial(press, keys)
    while True:
        func()
        time.sleep(seconds)


def main():
    config = Config(defaults=DEFAULTS, default_section="default")
    signal = Signal()

    chars = config.get("default", "animation_chars")
    sleep = config.getfloat("default", "animation_sleep")

    t = threading.Thread(
        name="animate", target=animate, args=(chars, sleep, signal)
    )
    t.start()

    seconds = config.getfloat("default", "inhibitor_time")
    keys = config.get("default", "keys")

    try:
        inhibitor(seconds, keys)
    except KeyboardInterrupt:
        print(" ")
        print("bye!")
    finally:
        signal.terminate = True
        t.join()
        sys.exit(0)


if __name__ == "__main__":
    main()
