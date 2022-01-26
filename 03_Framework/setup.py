from abc import get_cache_token
from time import time
from DBOps import DBOps
import os
import json
from requests import get
import socket

config_path = os.getcwd() + '/resources/params.json'


def registerMachine():
    db = DBOps()

    if getConfig('browser_mode') == None:
        query = 'SELECT name,has_command FROM modes WHERE state = 0 LIMIT 1'
        row = db.select(query)
        browser_mode = row[0][0]
        has_command = row[0][1]
        setConfig('browser_mode', browser_mode)
        setConfig('has_command', has_command)
        ip_adress = get('https://api.ipify.org').text
        query = "UPDATE modes SET state=1, IP='" + \
            ip_adress + "' WHERE name='" + browser_mode + "'"
        db.exec(query)
    else:
        print('Machine already registered!')


def getMode():

    if os.name == 'nt':
        # return "chrome_interaction_ger"
        return "windows"

    if socket.gethostname() == "measurement-1":
        return "chrome_desktop_ger"
    if socket.gethostname() == "measurement-2":
        return "chrome_desktop_usa"
    if socket.gethostname() == "measurement-3":
        return "chrome_desktop_jp"
    if socket.gethostname() == "measurement-4":
        return "chrome_interaction_ger"
    if socket.gethostname() == "measurement-5":
        return "chrome_interaction_usa"
    if socket.gethostname() == "measurement-6":
        return "chrome_interaction_jp"
    if socket.gethostname() == "measurement-7":
        return "chromeheadless_desktop_ger"
    if socket.gethostname() == "measurement-8":
        return "chromeheadless_desktop_usa"
    if socket.gethostname() == "measurement-9":
        return "chromeheadless_desktop_jp"
    if socket.gethostname() == "measurement-10":
        return "chromeheadless_interaction_ger"
    if socket.gethostname() == "measurement-11":
        return "chromeheadless_interaction_usa"
    if socket.gethostname() == "measurement-12":
        return "chromeheadless_interaction_jp"
    if socket.gethostname() == "measurement-13":
        return "openwpm_desktop_ger"
    if socket.gethostname() == "measurement-14":
        return "openwpm_desktop_usa"
    if socket.gethostname() == "measurement-15":
        return "openwpm_desktop_jp"
    if socket.gethostname() == "measurement-16":
        return "openwpm_interaction_ger"
    if socket.gethostname() == "measurement-17":
        return "openwpm_interaction_usa"
    if socket.gethostname() == "measurement-18":
        return "openwpm_interaction_jp"
    if socket.gethostname() == "measurement-19":
        return "openwpmheadless_desktop_ger"
    if socket.gethostname() == "measurement-20":
        return "openwpmheadless_desktop_usa"
    if socket.gethostname() == "measurement-21":
        return "openwpmheadless_desktop_jp"
    if socket.gethostname() == "measurement-22":
        return "openwpmheadless_interaction_ger"
    if socket.gethostname() == "measurement-23":
        return "openwpmheadless_interaction_usa"
    if socket.gethostname() == "measurement-24":
        return "openwpmheadless_interaction_jp"
    if socket.gethostname() == "measurement-25":
        return "openwpmheadless_interaction_jp"
    return 0
    # return getConfig('browser_mode')


def getConfig(name):
    params = {
        "bigquery_insert_rows": 500,
        "has_command": False,
        "thread_count": 12,
        "browser_mode_": "openwpm_desktop_ger",
        "browser_mode": "chrome_desktop_ger",
        "subpage_to_visit": 25,
        "timeout": 30,
        "timeout_site": 1800,
        "timeout_site_min": 30,
        "time_to_sleep": 1,
        "process_name_chrome": "/home/user/miniconda3/envs/openwpm/bin/python3 CrawlerChrome.py",
        "process_name_openwpm": "/home/user/miniconda3/envs/openwpm/bin/python3 CrawlerOpenWPM.py",
        "resolution": [1366, 768],
        "resolution_mobile_openwpm": [760, 360],
        "user_agent_chrome":"Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.77 Safari/537.36",
        "user_agent_openwpm":"Mozilla/5.0 (X11; Linux x86_64; rv:88.0) Gecko/20100101 Firefox/88.0",
        "user_agent_mobile_openwpm": "Mozilla/5.0 (Android 11; Mobile; rv:87.0) Gecko/87.0 Firefox/87.0",
        "user_agent_mobile_chrome": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.96 Safari/537.36",
        "modes": [
            "chrome_desktop_ger",
            "chrome_desktop_usa",
            "chrome_desktop_jp",
            "chrome_interaction_ger",
            "chrome_interaction_usa",
            "chrome_interaction_jp",
            "chrome-headless_desktop_ger",
            "chrome-headless_desktop_usa",
            "chrome-headless_desktop_jp",
            "chrome-headless_interaction_ger",
            "chrome-headless_interaction_usa",
            "chrome-headless_interaction_jp",
            "openwpm_desktop_ger",
            "openwpm_desktop_usa",
            "openwpm_desktop_jp",
            "openwpm_interaction_ger",
            "openwpm_interaction_usa",
            "openwpm_interaction_jp",
            "openwpm-headless_desktop_ger",
            "openwpm-headless_desktop_usa",
            "openwpm-headless_desktop_jp",
            "openwpm-headless_interaction_ger",
            "openwpm-headless_interaction_usa",
            "openwpm-headless_interaction_jp"
        ]
    }
    return params[name]
    """
    if name=='timeout':
        return 30
    try:
        with open(config_path) as f:
            configs = json.load(f)
            return configs[name]
    except:
        time.sleep(2)
        with open(config_path) as f:
            configs = json.load(f)
            return configs[name]
    """


def setConfig(name, value):
    with open(config_path) as f:
        configs = json.load(f)
    configs[name] = value
    with open(config_path, 'w') as f:
        json.dump(configs, f)


def getDriverPath():
    path = ''
    if os.name == 'nt':
        path = os.getcwd() + '/drivers/chromedriver.exe'
    else:
        path = os.getcwd() + '/drivers/chromedriver'
    return path


"""
10.0.12.170	chrome_desktop_ger
10.0.12.171	chrome_desktop_usa
10.0.12.172	chrome_desktop_jp
10.0.12.173	chrome_interaction_ger
10.0.12.174	chrome_interaction_usa
10.0.12.175	chrome_interaction_jp
10.0.12.176	chrome-headless_desktop_ger
10.0.12.177	chrome-headless_desktop_usa
10.0.12.178	chrome-headless_desktop_jp
10.0.12.179	chrome-headless_interaction_ger
10.0.12.180	chrome-headless_interaction_usa
10.0.12.181	chrome-headless_interaction_jp
10.0.12.182	openwpm_desktop_ger
10.0.12.183	openwpm_desktop_usa
10.0.12.184	openwpm_desktop_jp
10.0.12.185	openwpm_interaction_ger
10.0.12.186	openwpm_interaction_usa
10.0.12.187	openwpm_interaction_jp
10.0.12.188	openwpm-headless_desktop_ger
10.0.12.189	openwpm-headless_desktop_usa
10.0.12.190	openwpm-headless_desktop_jp
10.0.12.191	openwpm-headless_interaction_ger
10.0.12.192	openwpm-headless_interaction_usa
10.0.12.193	openwpm-headless_interaction_jp
"""
