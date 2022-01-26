from selenium.common.exceptions import TimeoutException
from PushOps import pushError
from CrawlerOpenWPM import runOpenWPMInstance
from CrawlerChrome import runChromeInstance
from Ops import editLogQueue, lessMemory, list2str, getMemory
from setup import getConfig, getMode
from DBOps import DBOps
from Objects import QueueItem, SiteData
import time
import queue
import threading
from collections import deque
import sys
from func_timeout import func_timeout, FunctionTimedOut, func_set_timeout
import os
import datetime
import json
import requests
import subprocess
import urllib.request

# Params
max_thread = getConfig('thread_count')
modes = ["chrome_desktop_eu", "openwpm_desktop_eu"]
report = ''
# vars
#queue_sites = queue.LifoQueue(maxsize=max_thread)
queue_sites = deque(maxlen=max_thread)
db = DBOps()
restart_requested = False
last_item_added = datetime.datetime.now()
last_vpn_check = datetime.datetime.now()
time_to_restart = False


def worker():
    findSuspended()
    while True:
        reportQueue()
        try:
            processQueue()
        except:
            pushError(-1, 'processQueue')
        time.sleep(3)


def isQueueFull():
    if len(queue_sites) >= max_thread:
        return True
    else:
        return False


def getNextJob():
    q_item = -1
    q_item = siteWaitForMe()
    if q_item == -1:
        q_item = pullNextSite()
        if q_item == -1:
            return -1  # No more site.
        elif q_item == -3:
            return -3  # no internet
        elif q_item == -4:
            return -4  # no internet
        else:
            return q_item
    else:
        return q_item


# Entries that should be in query, but not in query (after crashes it'd be useful)
def findSuspended():
    query_and = getQueryElements(True)
    query = "UPDATE sites SET state_" + getMode() + "=-1  WHERE state_" + \
        getMode() + "=0 " + query_and
    db.exec(query)


def siteWaitForMe():
    global time_to_restart
    if time_to_restart:
        return -4
    if lessMemory():
        return -2
    if has_internet() == False:
        pushError('-1', 'no_internet')
        return -3

    query_and = getQueryElements(True)
    # query = "SELECT id, concat('http://',site), subpages FROM sites WHERE site_state='in_queue' AND state_" +
    #  getMode() + " = -1 " + query_and + " ORDER BY id ASC LIMIT 1"   # TABLE sites
    query = "SELECT id, concat(scheme, site), subpages FROM sites WHERE site_state='in_queue' AND state_" + \
        getMode() + " = -1 " + query_and + " ORDER BY id ASC LIMIT 1"

    print(query)
    rows = db.select(query)
    if len(rows) == 0:
        return -1
    else:
        q_item = QueueItem(rows[0][0], rows[0][1], None,
                           rows[0][2], None, None, None)
        return q_item


def pullNextSite():
    global time_to_restart
    if lessMemory():
        return -2

    if has_internet() == False:
        pushError('-1', 'no_internet')
        return -3
    if time_to_restart:
        return -4

    # query = "SELECT id, concat('http://',site), subpages FROM sites WHERE site_state IS NULL AND state_" + \
    #        getMode() + " = -1  ORDER BY id ASC LIMIT 1"    #SITE sites
    query = "SELECT id, concat(scheme, site), subpages FROM sites WHERE site_state IS NULL AND state_" + \
            getMode() + " = -1  ORDER BY id ASC LIMIT 1"
    rows = db.select(query)
    if len(rows) > 0:
        site_ID = str(rows[0][0])
        query = "UPDATE sites SET site_state ='in_queue', state_" + getMode() + \
            " = 0 WHERE id=" + site_ID
        db.exec(query)
        q_item = QueueItem(rows[0][0], rows[0][1], None,
                           rows[0][2], None, None, None)
        return q_item
    else:
        return -1


def getQueryElements(p_for_database=False):
    if p_for_database is False:
        return list(queue_sites)
    elif p_for_database is True:
        text = ''
        if len(queue_sites) > 0:
            for item in queue_sites:
                text = text + ',' + str(item.site_ID)
            text = " AND ID NOT IN (" + text[1:] + ")"
        return text


def getQueryElements2(queue):
    text = ''
    if len(queue) > 0:
        for item in queue:
            text = text + ',' + str(item)
        text = " AND ID NOT IN (" + text[1:] + ")"
    return text


def queueManager(p_q_item, p_OP):

    global restart_requested
    global last_item_added
    global time_to_restart

    p_site_id = p_q_item.site_ID
    p_site_url = p_q_item.url
    p_subpages = p_q_item.subpages

    if p_OP == 'waiting':
        if restart_requested or time_to_restart:
            return
        queue_item = QueueItem(p_site_id, p_site_url,
                               'waiting', p_subpages, None, None, None)
        for i, q_value in enumerate(list(queue_sites)):
            q_item = queue_sites[i]
            q_site_id = q_item.site_ID
            if q_site_id == p_site_id:
                return False
        if time_to_restart == False:
            queue_sites.append(queue_item)
            last_item_added = datetime.datetime.now()

        if p_site_id % 150 == 0:
            time_to_restart = True

        query = "UPDATE sites SET state_" + getMode() + "= 0 WHERE id=" + \
            str(p_site_id)
        db.exec(query)

        query = "SELECT 1 FROM sites WHERE state_chrome_desktop_ger = 0  AND state_chrome_desktop_usa = 0  AND state_chrome_desktop_jp = 0  AND state_chrome_interaction_ger = 0  AND state_chrome_interaction_usa = 0  AND state_chrome_interaction_jp = 0  AND state_chromeheadless_desktop_ger = 0  AND state_chromeheadless_desktop_usa = 0  AND state_chromeheadless_desktop_jp = 0  AND state_chromeheadless_interaction_ger = 0  AND state_chromeheadless_interaction_usa = 0  AND state_chromeheadless_interaction_jp = 0  AND state_openwpm_desktop_ger = 0  AND state_openwpm_desktop_usa = 0  AND state_openwpm_desktop_jp = 0  AND state_openwpm_interaction_ger = 0  AND state_openwpm_interaction_usa = 0  AND state_openwpm_interaction_jp = 0  AND state_openwpmheadless_desktop_ger = 0  AND state_openwpmheadless_desktop_usa = 0  AND state_openwpmheadless_desktop_jp = 0  AND state_openwpmheadless_interaction_ger = 0  AND state_openwpmheadless_interaction_usa = 0  AND state_openwpmheadless_interaction_jp = 0 AND id=" + \
            str(p_site_id)
        rows = db.select(query)
        if len(rows) != 0:
            query = "UPDATE sites SET ready=true WHERE id=" + \
                str(p_site_id)
            db.exec(query)

    elif p_OP == 'crawling':
        for i, q_value in enumerate(list(queue_sites)):
            q_item = queue_sites[i]
            q_site_id = q_item.site_ID
            if q_site_id == p_site_id:
                queue_item = QueueItem(
                    p_site_id, p_site_url, 'crawling', p_subpages, None, None, None)
                queue_sites[i] = queue_item

    elif p_OP == 'completed':
        items_to_delete = []
        for i, q_value in enumerate(list(queue_sites)):
            q_item = queue_sites[i]
            q_site_id = q_item.site_ID
            if q_site_id == p_site_id:
                queue_item = QueueItem(
                    p_site_id, p_site_url, 'completed', p_subpages, None, None, None)
                queue_sites[i] = queue_item
                reportQueue()
                items_to_delete.append(i)
        # delete items from queue here, to avoid out of range errors.
        for item in items_to_delete:
            del queue_sites[item]


def vpn_Connected(): 
    
    try:
        url = "http://ip-api.com/json/"
        response = json.loads((requests.request("GET", url)).text)
        s = getMode()
        c_code = None
        if s.endswith('_ger'):
            c_code = 'DE'
        elif s.endswith('_jp'):
            c_code = 'JP'
        else:
            c_code = 'US' 

        if response['countryCode'] != c_code:
            return False
        else:
            return True
    except:
            return False     


def processQueue():

    global last_item_added
    global time_to_restart
    global restart_requested
    final = (datetime.datetime.now() - last_item_added)
    print('Last item added ', str(final.total_seconds()/60), ' min. ago.')
    if final.total_seconds() > getConfig('timeout_site'):
        restart()

    if lessMemory() or time_to_restart:
        checkForRestart()
    if getMemory() > 2500:
        restart_requested = False
    vpn_Connected()
    if restart_requested or time_to_restart:
        print('restart requested, waiting for other jobs to be done.')

    if not isQueueFull():
        q_item = getNextJob()
        if q_item == -1:
            print("Analyze has been finished, no more site.")
        elif q_item == -2:
            print("WAIT FOR RESTART")
        elif q_item == -3:
            print('NO INTERNET!')
        elif q_item == -4:
            print('restart requested!')
        else:
            queueManager(q_item, 'waiting')

    for i, q_value in enumerate(list(queue_sites)):
        if i >= len(queue_sites):
            break
        q_item = queue_sites[i]
        q_site_id = q_item.site_ID
        q_state = q_item.state

        if q_state == 'waiting':
            if restart_requested:
                continue
            if isSiteReady(q_site_id):
                queueManager(q_item, 'crawling')
                t = threading.Thread(target=startThread,
                                     args=(queue_sites, q_item))
                t.start()
                time.sleep(3)

        elif q_state == 'completed':
            queueManager(q_item, 'waiting')
        """if q_state == 'completed':
            getNextJob()"""


def checkForRestart():

    shallRestart = True
    for i, q_value in enumerate(list(queue_sites)):
        q_item = queue_sites[i]
        if q_item.state == 'crawling' or q_item.state == 'completed':
            shallRestart = False
    if shallRestart:
        print('I RESTARt\n\n\n"')

        restart()

    global restart_requested
    if restart_requested == False:
        restart_requested = True
        t = threading.Thread(target=forceRestart)
        t.start()
        print('\n\n\n\RESTART COUTDOWN STARTED!')
    else:
        print('WAIT FOR RESTART: THREAD EXISTS!')


def forceRestart(timeout_for_restart=1500):
    time.sleep(timeout_for_restart)
    global restart_requested
    if getMemory() > 2500:
        restart_requested = False
        return

    restart()


def restart():
    try:
        pushError(-1, 'restarted')
    except:
        pass
    try:
        import subprocess
        import os
        subprocess = subprocess.Popen(['ps', '-A'], stdout=subprocess.PIPE)
        output, error = subprocess.communicate()

        target_process1 = "firefox"
        target_process2 = "chrome"
        target_process3 = "geckodriver"

        for line in output.splitlines():
            if target_process1 in str(line) or target_process2 in str(line) or target_process3 in str(line):
                pid = int(line.split(None, 1)[0])
                os.kill(pid, 9)
                print('killed', line)
    except Exception as e:
        print('error', str(e))
    try:
        import ctypes
        libc = ctypes.CDLL("libc.so.6")
        libc.malloc_trim(0)
        import gc
        gc.collect()
    except:
        pass
    time.sleep(1)
    #os.execl('/home/user/miniconda3/envs/openwpm/bin/python3', os.path.abspath(__file__), *sys.argv)
    try:
        import subprocess
        # , shell=True)
        subprocess.call(
            '/home/user/Desktop/repo/2021-webMeasurements/restart.sh')
    except:
        os.execl('/home/user/miniconda3/envs/openwpm/bin/python3',
                 os.path.abspath(__file__), *sys.argv)
        print('CANT RESTART!')


def isSiteReady(p_site_id):
    query = "SELECT 1 FROM sites WHERE ready IS TRUE and id=" + \
        str(p_site_id)
    rows = db.select(query)
    if len(rows) > 0:
        return True
    else:
        return False


def startThread(p_queue, p_queue_item):
    print('starting: ', p_queue_item.url, ' - mode: ', getMode())

    siteData = SiteData()
    siteData.state_text = 'initialized'
    siteData.state = -1
    siteData.timeout = 0

    # if getMode().startswith('chrome'):
    try:
        queueManager(p_queue_item, 'crawling')
        changeSiteState(p_queue_item.site_ID, 1)
        try:
            if getMode().startswith('chrome'):
                siteData = func_timeout(
                    getConfig('timeout_site'), runChromeInstance, args=(p_queue, p_queue_item))
            elif getMode().startswith('openwpm'):
                siteData = func_timeout(
                    getConfig('timeout_site'), runOpenWPMInstance, args=(p_queue, p_queue_item))
            siteData.state = 2
            siteData.timeout = 0
        except (FunctionTimedOut, TimeoutException):
            siteData.timeout = 1
            siteData.state = 3
    except:
        pushError(p_queue_item.site_ID, 'startThread')
    try:
        completeVisit(siteData, p_queue_item, 'completed')
    except:
        pushError(p_queue_item.site_ID, 'completeVisit')

    del siteData
    sys.exit()
    return None


"""
    elif getMode().startswith('openwpm'):
        try:
            queueManager(p_queue_item, 'crawling')
            changeSiteState(p_queue_item.site_ID, 1)
            visitData = runOpenWPMInstance(p_queue, p_queue_item)
            if visitData.state_text == 'successful':
                queueManager(p_queue_item, 'completed')
                changeSiteState(p_queue_item.site_ID, 2)
            else:
                queueManager(p_queue_item, 'completed')
                changeSiteState(p_queue_item.site_ID, 3)  # error
        except:
            pushError(p_queue_item.site_id, 'startThread')
            queueManager(p_queue_item, 'completed')
            changeSiteState(p_queue_item.site_ID, 3)  # error"""


def completeVisit(siteData, p_queue_item, ops):
    changeSiteState(p_queue_item.site_ID, siteData.state, siteData.timeout)
    queueManager(p_queue_item, ops)


def changeSiteState(siteID, state, timeout=0):
    query = "UPDATE sites SET state_{} = {}, timeout={}  where id = {} ".format(
        getMode(), state, timeout, siteID)
    print(query)
    db.exec(query)


def reportQueue():
    global report
    r = '############\nurl:state\n'
    for q in queue_sites:
        if q == None:
            r = r+" null\n"
        else:
            r = r + str(q.site_ID) + ': ' + str(q.url) + \
                ' - ' + str(q.state) + '\n'
    r = r + '############'
    if report != r:
        report = r

    print(r)


def has_internet():
    state = True
    try:
        import socket
        """host = socket.gethostbyname('google.com')
        s = socket.create_connection((host, 80), 2)
        s.close()"""
        urllib.request.urlopen('http://google.com')
        return True
    except Exception as e:
        return False

# def getRuningCrawlers():


def processStartedSites():
    import os
    all_processes = [(int(p), c) for p, c in [x.rstrip('\n').split(' ', 1)
                                              for x in os.popen('ps h -eo pid:1,etime:1,command')]]
    output('##########################################################################################')
    output("Time: " + str(datetime.datetime.now()))
    output("Memory: " + str(getMemory()))
    crawlers = []
    for item in all_processes:
        process_name = None
        if getMode().startswith('chrome'):
            process_name = 'process_name_chrome'
        else:
            process_name = 'process_name_openwpm'
        if getConfig(process_name) in item[1]:
            crawlers.append(item)

    my_list = []
    # kill crawlers that are timed-out
    for item in crawlers:
        output(item)
        pid = item[0]
        process = item[1].split(' ')
        minutes = process[0].split(':')
        if len(minutes) > 2:
            # if it took hours :)
            minutes = int(minutes[0])*60 + int(minutes[1])
        else:
            minutes = int(minutes[0])

        site_id = process[3]
        is_ready = process[4]
        my_list.append(site_id)

        # if is_ready:
        if minutes > getConfig('timeout_site_min'):
            # get state if 0, set -1, if 2 nothing, if 1, 4
            db = DBOps()
            state = db.select('select state_' + getMode() +
                              ' from sites where id=' + str(site_id))[0][0]
            if state == 1:
                changeSiteState(site_id, '4')
            elif state == 0:
                changeSiteState(site_id, '-1')
            os.system('kill %d' % pid)
    crawlers = list(dict.fromkeys(my_list))
    output(str(len(crawlers)) + ' crawlers running... #SITE_ID: ' + str(crawlers))
    output('##########################################################################################')
    return crawlers


def isReadyForRestart():
    if len(processStartedSites()) > 0:
        return

    try:
        pushError(-1, 'restarted')
    except:
        pass
    try:
        import subprocess
        import os
        subprocess = subprocess.Popen(['ps', '-A'], stdout=subprocess.PIPE)
        output, error = subprocess.communicate()

        target_process1 = "firefox"
        target_process2 = "chrome"
        target_process3 = "geckodriver"

        for line in output.splitlines():
            if target_process1 in str(line) or target_process2 in str(line) or target_process3 in str(line):
                pid = int(line.split(None, 1)[0])
                os.kill(pid, 9)
                print('killed', line)
    except Exception as e:
        print('error', str(e))
    try:
        import ctypes
        libc = ctypes.CDLL("libc.so.6")
        libc.malloc_trim(0)
        import gc
        gc.collect()
    except:
        pass
    time.sleep(1)
    #os.execl('/home/user/miniconda3/envs/openwpm/bin/python3', os.path.abspath(__file__), *sys.argv)
    try:
        import subprocess
        # , shell=True)
        subprocess.call(
            '/home/user/Desktop/repo/2021-webMeasurements/restart.sh')
    except:
        os.execl('/home/user/miniconda3/envs/openwpm/bin/python3',
                 os.path.abspath(__file__), *sys.argv)
        print('CANT RESTART!')


def processQueue2():
    global time_to_restart

    in_queue = processStartedSites()
    if time_to_restart:
        isReadyForRestart()
        return

    # report2()
    total_items = len(in_queue)

    if total_items >= getConfig('thread_count'):
        return
    else:
        # get sites wait for me
        query_and = getQueryElements2(in_queue)
        query = "SELECT id FROM sites WHERE site_state='in_queue' AND state_" + \
            getMode() + " = -1 " + query_and + " ORDER BY id ASC LIMIT 1"
        rows = db.select(query)

        if len(rows) > 0:
            print('new site pulled (waited): ', rows[0][0])
            startNewCrawler(rows[0][0])
        else:
            # set a new site in queue for all
            query = "SELECT id FROM sites WHERE site_state IS NULL AND state_" + \
                    getMode() + " = -1  " + query_and + " ORDER BY id ASC LIMIT 1"
            rows = db.select(query)
            if len(rows) > 0:
                print('new site pulled: ', rows[0][0])
                startNewCrawler(rows[0][0])
                query = "UPDATE sites SET site_state ='in_queue', state_" + getMode() + \
                    " = 0 WHERE id=" + str(rows[0][0])
                db.exec(query)
            else:
                print('no more site, measurement finished!')
                exit()


def output(text):
    print("\033[38;2;{};{};{}m{} \033[38;2;255;255;255m".format(255, 0, 0, text))


def startNewCrawler(id):

    if has_internet() == False:
        output('ERROR: NO INTERNET CONNECTION!')
        pushError('-1', 'no_internet')
        return

    if vpn_Connected() == False:
        output('ERROR: NO VPN CONNECTION!')
        pushError('-1', 'no_vpn')
        return

    global time_to_restart
    time.sleep(5)
    if id in processStartedSites():
        return
    else:
        msg = str(id) + ' not in' + str(processStartedSites()) + \
            ' - so i start new.'
        output(msg)
    if getMemory() < 2000:
        time_to_restart = True
        return

    if id % 250 == 0:
        time_to_restart = True

    changeSiteState(id, 0)
    query = "SELECT 1 FROM sites WHERE state_chrome_desktop_ger = 0  AND state_chrome_desktop_usa = 0  AND state_chrome_desktop_jp = 0  AND state_chrome_interaction_ger = 0  AND state_chrome_interaction_usa = 0  AND state_chrome_interaction_jp = 0  AND state_chromeheadless_desktop_ger = 0  AND state_chromeheadless_desktop_usa = 0  AND state_chromeheadless_desktop_jp = 0  AND state_chromeheadless_interaction_ger = 0  AND state_chromeheadless_interaction_usa = 0  AND state_chromeheadless_interaction_jp = 0  AND state_openwpm_desktop_ger = 0  AND state_openwpm_desktop_usa = 0  AND state_openwpm_desktop_jp = 0  AND state_openwpm_interaction_ger = 0  AND state_openwpm_interaction_usa = 0  AND state_openwpm_interaction_jp = 0  AND state_openwpmheadless_desktop_ger = 0  AND state_openwpmheadless_desktop_usa = 0  AND state_openwpmheadless_desktop_jp = 0  AND state_openwpmheadless_interaction_ger = 0  AND state_openwpmheadless_interaction_usa = 0  AND state_openwpmheadless_interaction_jp = 0 AND id=" + \
        str(id)
    rows = db.select(query)
    if len(rows) != 0:
        query = "UPDATE sites SET ready=true WHERE id=" + \
            str(id)
        db.exec(query)
    """"
    for item in queue_waiting:
        if item == id:
            return

    queue_waiting.append(id)
    print(queue_waiting)"""

    ready = False
    query = "SELECT 1 FROM sites WHERE ready IS TRUE and id=" + \
        str(id)
    rows = db.select(query)
    print(query)
    if len(rows) > 0:
        ready = True

    print(str(id), ' starts')
    if getMode().startswith('chrome'):
        processName = 'CrawlerChrome.py'
    else:
        processName = 'CrawlerOpenWPM.py'
    subprocess.Popen(['/home/user/miniconda3/envs/openwpm/bin/python3',
                      processName, str(id), str(ready),  str(datetime.datetime.now())])


def worker2():
    findSuspended()
    while True:
        # reportQueue()
        try:
            processQueue2()
        except Exception as e:
            raise e
            pushError(-1, 'processQueue')
        time.sleep(3)


if __name__ == "__main__":
    # worker()
    worker2()
