# -*- coding:utf-8 -*-

import json
import logging
import csv
import datetime


def saveData(data, device, interval, dev=False):
    if dev:
        # dev
        APP_PATH = ''
        MYAPP_NAME = ''
    else:
        # production
        APP_PATH = "/usr/pyuser/app/"
        MYAPP_NAME = "sdmo_parser/"

    try:
        with open(APP_PATH + MYAPP_NAME + str(device) + ".csv", "r") as f:
            reader = csv.reader(f)
            records = []
            for row in reader:
                # if row[0] !
                date = datetime.datetime.strptime(row[0],  '%Y-%m-%d %H:%M:%S.%f')
                curDate = datetime.datetime.now()
                diffDate = (curDate - date).days
                # print (diffDate)
                if diffDate < interval:
                    # print (diffDate)
                    records.append(row)
                # print (row[0])
            # print (records)
            records.append([curDate, data])
            with open(APP_PATH + MYAPP_NAME + str(device) + ".csv", "w") as f:
                writer = csv.writer(f)
                writer.writerows(records)
    except Exception as e:
        # print(e)
        logging.info(e)
        records = []
        curDate = datetime.datetime.now()
        records.append([curDate, data])
        with open(APP_PATH + MYAPP_NAME + str(device) + ".csv", "w") as f:
            writer = csv.writer(f)
            writer.writerows(records)

    return True


def upload(device, dev=False):
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
        with open(APP_PATH + MYAPP_NAME + str(device) + ".csv", "r") as f:
            reader = csv.reader(f)
            records = []
            for row in reader:
                records.append(row)

            with open(APP_PATH + MYAPP_NAME + str(device) + ".csv", "w") as f:
                blank = []
                writer = csv.writer(f)
                writer.writerows(blank)
        return records
    except Exception as e:
        logging.info(e)
        # print(e)

    return False
