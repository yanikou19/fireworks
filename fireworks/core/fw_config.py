#!/usr/bin/env python

"""
A set of global constants for FireWorks (Python code as a config file)
"""

import os
import yaml

__author__ = 'Anubhav Jain'
__copyright__ = 'Copyright 2012, The Materials Project'
__version__ = '0.1'
__maintainer__ = 'Anubhav Jain'
__email__ = 'ajain@lbl.gov'
__date__ = 'Dec 12, 2012'


def singleton(class_):
    instances = {}

    def getinstance(*args, **kwargs):
        if class_ not in instances:
            instances[class_] = class_(*args, **kwargs)
        return instances[class_]

    return getinstance


@singleton
class FWConfig(object):
    def __init__(self):

        self.USER_PACKAGES = ['fireworks.user_objects', 'fireworks.utilities.tests',
                              'fw_tutorials']  # this is where load_object() looks for serialized objects

        self.FW_NAME_UPDATES = {}  # if you update a _fw_name, you can use this to record the change and maintain
        # deserialization

        self.YAML_STYLE = False  # controls whether YAML documents will be nested as braces or blocks (False = blocks)

        self.FW_BLOCK_FORMAT = '%Y-%m-%d-%H-%M-%S-%f'  # date format for writing block directories in "rapid-fire" mode

        self.FW_LOGGING_FORMAT = '%(asctime)s %(levelname)s %(message)s'  # format for loggers

        self.QUEUE_RETRY_ATTEMPTS = 10  # number of attempts to re-try communicating with queue server in certain cases
        self.QUEUE_UPDATE_INTERVAL = 15  # max interval (seconds) needed for queue to update after submitting a job

        self.SUBMIT_SCRIPT_NAME = 'FW_submit.script'  # name of submit script

        self.PRINT_FW_JSON = True
        self.PRINT_FW_YAML = False

        self.PING_TIME_SECS = 3600  # while Running a job, how often to ping back the server that we're still alive
        self.RUN_EXPIRATION_SECS = self.PING_TIME_SECS * 4  # if a job is not pinged in this much time,
        # we mark it FIZZLED

        self.RESERVATION_EXPIRATION_SECS = 60 * 60 * 24 * 14  # a job can stay in a queue for 14 days before we
        # cancel its reservation

        self.override_user_settings()

    def override_user_settings(self):
        MODULE_DIR = os.path.dirname(os.path.abspath(__file__))
        root_dir = os.path.dirname(os.path.dirname(MODULE_DIR))
        config_path = os.path.join(root_dir, 'FW_config.yaml')

        if os.path.exists(config_path):
            with open(config_path) as f:
                overrides = yaml.load(f.read())
                for key, v in overrides.iteritems():
                    if key == 'ADD_USER_PACKAGES':
                        self.USER_PACKAGES.extend(v)
                    elif key == 'ECHO_TEST':
                        print v
                    elif not getattr(self, key, None):
                        raise ValueError('Invalid FW_config file has unknown parameter: {}'.format(key))
                    else:
                        self.__setattr__(key, v)