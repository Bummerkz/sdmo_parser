# -*- coding:utf-8 -*-

import json
import logging

def get_new_device(dev_type='fc', dev=False):
    if dev:
        # dev
        APP_PATH = ''
        MYAPP_NAME = ''
    else:
        # production
        APP_PATH = "/usr/pyuser/app/"
        MYAPP_NAME = "sdmo_parser/"

    if dev_type.lower() == 'fc':
        try:
            # production
            with open(APP_PATH + MYAPP_NAME + "src/fc.json", "r") as f:
                config = json.loads("".join(f.readlines()))
        except Exception as e:
            logging.info(e)
        return config        
    elif dev_type.lower() == 'mercury':
        try:
            # production
            with open(APP_PATH + MYAPP_NAME + "src/mercury.json", "r") as f:
                config = json.loads("".join(f.readlines()))
        except Exception as e:
            logging.info(e)
        return config
    else:
        return "No such device!"

def get_config(dev=False):
    if dev:
        # dev
        APP_PATH = ''
        MYAPP_NAME = ''
    else:
        # production
        APP_PATH = "/usr/pyuser/app/"
        MYAPP_NAME = "sdmo_parser/"

    try:
        # production
        with open(APP_PATH + MYAPP_NAME + "config.json", "r") as f:
            config = json.loads("".join(f.readlines()))
        return config
    except Exception as e:
        logging.info(e)

    return False
    

def update_config(config, dev=False, dev_type='config'):
    if dev:
        # dev
        APP_PATH = ''
        MYAPP_NAME = ''
    else:
        # production
        APP_PATH = "/usr/pyuser/app/"
        MYAPP_NAME = "sdmo_parser/"
        
    if dev_type.lower() == 'config':
        try:
            with open(APP_PATH + MYAPP_NAME + "config.json", "w") as f:
                json.dump(config, f, indent=4)
        except Exception as e:
            logging.info(e)

        return True
    else:
        return False