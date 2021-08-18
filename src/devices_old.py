# -*- coding:utf-8 -*-
import config

def add_new_device(param):
    cfg = config.get_config()
    i = len(cfg['Devices']) + 1
    while True:
        if str(i) in cfg["Devices"]:
            i = i + 1
        else:
            break
    params = param.split(',')
    dev_type = params[0]
    # if dev_type == 'No such device!':
    #     return 'Failed to add new device! No such device!'

    device = {i: config.get_new_device(dev_type=dev_type)}

    device[i]['port'] = int(params[3])
    device[i]['addr'] = 1
    device[i]['baudrate'] = int(params[4])
    device[i]['bytesize'] = int(params[5])
    device[i]['parity'] = params[6]
    device[i]['stopbits'] = int(params[7])
    device[i]['send_interval'] = int(params[8])
    device[i]['osc_send_interval'] = int(params[9])
    device[i]['osc_duration'] = int(params[10])
    device[i]['osc_frequency'] = int(params[11])

    cfg['Devices'].update(device)

    status = config.update_config(cfg)

    if status:
        return cfg
    else:
        return None

def clear_device(device_id):
    cfg = config.get_config()

    try:
        del cfg['Devices'][device_id]
    except KeyError:
        return 'no_device'

    status = config.update_config(cfg)

    if status:
        return cfg
    else:
        return None