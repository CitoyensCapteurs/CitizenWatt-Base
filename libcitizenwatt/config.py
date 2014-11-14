#!/usr/bin/env python3

"""
Implementation of a config file stored as JSON in ~/.config
"""

import crypt
import errno
import json
import os
import sys
from libcitizenwatt import tools


def make_sure_path_exists(path):
    try:
        os.makedirs(path)
        return False
    except OSError as exception:
        if exception.errno != errno.EEXIST:
            raise
        else:
            return True


class Config():
    def __init__(self, base_config_path="~/.config/citizenwatt/"):
        self.config_path = os.path.expanduser(base_config_path)
        self.config = {}
        self.load()

    def as_dict(self):
        return self.config

    def get(self, param):
        return self.config.get(param, False)

    def set(self, param, value):
        self.config[param] = value

    def unset(self, param):
        del(self.config[param])

    def initialize(self):
        self.set("max_returned_values", 500)
        self.set("database_type", "postgresql+psycopg2")
        self.set("username", "citizenwatt")
        self.set("password", "citizenwatt")
        self.set("database", "citizenwatt")
        self.set("host", "localhost")
        self.set("debug", False)
        self.set("url_energy_providers",
                 "http://dev.citizenwatt.paris/providers/electricity_providers.json")
        self.set("salt", crypt.mksalt())
        self.set("named_fifo", "/tmp/sensor")
        self.set("default_timestep", 8)
        self.set("port", 8080)
        self.set("autoreload", False)
        self.save()

    def load(self):
        try:
            folder_exists = make_sure_path_exists(self.config_path)
            if(folder_exists and
               os.path.isfile(self.config_path + "config.json")):
                initialized = True
            else:
                initialized = False
        except OSError:
            tools.warning("Unable to create ~/.config folder.")
            sys.exit(1)
        if not initialized:
            self.initialize()
        else:
            try:
                with open(self.config_path + "config.json", 'r') as fh:
                    self.config = json.load(fh)
            except (ValueError, IOError):
                tools.warning("Config file could not be read.")
                sys.exit(1)

    def save(self):
        try:
            with open(self.config_path + "config.json", 'w') as fh:
                fh.write(json.dumps(self.config,
                                    sort_keys=True,
                                    indent=4,
                                    separators=(',', ': ')))
        except IOError:
            tools.warning("Could not write config file.")
            sys.exit(1)
