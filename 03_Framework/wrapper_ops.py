from abc import get_cache_token
import os
import json
from requests import get

config_path = os.getcwd() + '/resources/params.json'
 


def getMode():
    return getConfig('browser_mode')


def getConfig(name):
    with open(config_path) as f:
        configs = json.load(f)
        return configs[name]


def setConfig(name, value):
    with open(config_path) as f:
        configs = json.load(f)
    configs[name] = value
    with open(config_path, 'w') as f:
        json.dump(configs, f)


def getSeleniumPath():
    path = ''
    if os.name == 'nt':
        path = os.getcwd() + '/drivers/chromedriver.exe'
    else:
        path = os.getcwd() + '/drivers/chromedriver'
    return path

 