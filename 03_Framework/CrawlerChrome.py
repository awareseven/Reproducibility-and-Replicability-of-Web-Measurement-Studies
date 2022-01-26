from func_timeout import func_timeout, FunctionTimedOut, func_set_timeout
from logging import root
from tmp.path import find_cookies_path
from Ops import delFolder, delProfileFolder, editLogQueue, isThirdParty, newLogQueue, terminateProcessBySiteID, timestamp2Datetime, LocalStorage, visitLogNew, visitLogUpdate
from re import split, sub
from setup import getConfig, getMode,  getDriverPath
from PushOps import execBQRows, pushError, stream2BQ
from Objects import VisitData, SiteData, QueueItem
#from selenium import webdriver
from seleniumwire import webdriver  # Import from seleniumwire, to get requests
import time
from selenium.webdriver.chrome.options import Options
import sqlite3
import os
from DBOps import DBOps
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
import tldextract
from urllib.parse import urlparse, unquote
import random
from datetime import datetime, timedelta
from selenium.common.exceptions import (
    MoveTargetOutOfBoundsException,
    TimeoutException,
    WebDriverException,
)
import threading
from chrome_cookiejar import ChromeCookieJar


#from DataPreProcessingOps import getEasyListRules
from adblockparser import AdblockRules

rules = None
""""
def loadRules():
    global rules
    rules=AdblockRules(getEasyListRules(), use_re2=True,
                     max_mem=512*1024*1024)
"""
#rules = AdblockRules(getEasyListRules(), use_re2=True,                    max_mem=512*1024*1024)


param_root_site_url = ''
param_root_site_id = ''


def loadBrowser(root_site_id):

    p_mode = getMode()

    # wire_options = {
    #     'enable_har': True,
    #    'disable_encoding': True  # Ask the server not to compress the response
    # }
    browser_type = p_mode.split('_')[0]
    browser_config = p_mode.split('_')[1]

    profile_path = getSeleniumProfilePath(root_site_id)
    options = Options()
    options.add_argument("--log-level=3")
    options.add_argument("user-data-dir=" + profile_path)

    options_wire = {
        'request_storage_base_dir': getSeleniumProfilePath(root_site_id) + '/.storage/'}

    # CHROME: normal
    if browser_type == 'chrome':
        pass
    elif browser_type == 'chromeheadless':
        options.add_argument("no-sandbox")
        options.add_argument("headless")
        
    options.add_argument("user-agent="+ getConfig('user_agent_chrome'))

    resolution = getConfig('resolution')
    try:
        driver = webdriver.Chrome(
            executable_path=getDriverPath(), chrome_options=options, seleniumwire_options=options_wire)
        driver.set_window_size(resolution[0], resolution[1])
        # driver.set_page_load_timeout(getConfig('timeout'))
        # driver.implicitly_wait(30)
    except:
        time.sleep(2)
        driver = webdriver.Chrome(
            executable_path=getDriverPath(), chrome_options=options, seleniumwire_options=options_wire)
        driver.set_window_size(resolution[0], resolution[1])
        # driver.set_page_load_timeout(getConfig('timeout'))
        #  driver.implicitly_wait(30)

    return driver

    """
    elif browser_type == 'chrome-headless':
        options = Options()
        options.add_argument("--log-level=3")
         if browser_config == 'mobile':
            mobile_emulation = {"deviceName": "iPhone X"}
            options.add_experimental_option(
                "mobileEmulation", mobile_emulation) 
         elif browser_config == 'accept-cookies':
            options.add_extension(
                os.getcwd() + '/resources/extensions/accept_cookies.crx') 
        options.add_argument("user-data-dir=" +
                                getSeleniumProfilePath(root_site_id))
        driver = webdriver.Chrome(
            executable_path=getDriverPath(), chrome_options=options)
    """


def getRequest(input_driver, current_url, root_site_url, root_site_id, subpage_id):
    reqList = []
    for r in input_driver.requests:
        req = {}
        req['method'] = r.method

        # parse headers
        headers = str(r.headers)
        splitted_headers = headers.split('\n')
        list_headers = []
        host = ['host',  urlparse(r.url).netloc]
        list_headers.append(host)
        for item in splitted_headers:
            item_split = item.split(':')
            header_name = item_split[0]
            header_value = ':'.join(item_split[1:])
            header_pair = [header_name, header_value]
            if header_pair != ['', '']:
                list_headers.append(header_pair)
        req['headers'] = str(list_headers)

        req['url'] = r.url
        req['time_stamp'] = str(r.date)

        if r.headers.get('X-Requested-With'):
            req['is_XHR'] = 1
        else:
            req['is_XHR'] = 0

        if r.headers.get('Referer'):
            req['referrer'] = r.headers.get('Referer')
        else:
            req['referrer'] = None

        if r.headers['Upgrade'] == 'websocket':
            req['is_websocket'] = 1
        else:
            req['is_websocket'] = 0

        content_hash = None
        try:
            import hashlib
            content_hash = hashlib.sha1(
                input_driver.page_source.encode()).hexdigest()
        except:
            pass

        req['content_hash'] = content_hash
        req['browser_id'] = getMode()
        req['is_third_party_channel'] = isThirdParty(root_site_url, r.url)
        req['is_third_party_to_top_window'] = None
        req['resource_type'] = None
        req['top_level_url'] = current_url  # input_driver.current_url
        req['site_id'] = root_site_id
        req['visit_id'] = str(root_site_id) + '-' + str(subpage_id)
        req['subpage_id'] = subpage_id

        """"
        while(rules==None):
            time.sleep(0.3)
            
        try:
            req['is_tracker'] = int(rules.should_block(r.url))
        except:
            pass"""

        etld = tldextract.extract(r.url)
        req['etld'] = etld.domain + '.' + etld.suffix

        reqList.append(req)
    return reqList


def getResponses(input_driver, root_site_id, subpage_id):
    resList = []
    for r in input_driver.requests:
        if r.response:
            res = {}

            res['method'] = r.method

            # parse headers
            headers = str(r.response.headers)
            splitted_headers = headers.split('\n')
            list_headers = []
            for item in splitted_headers:
                item_split = item.split(':')
                header_name = item_split[0]
                header_value = ':'.join(item_split[1:])
                header_pair = [header_name, header_value]
                if header_pair != ['', '']:
                    list_headers.append(header_pair)

            res['headers'] = str(list_headers)

            res['url'] = r.url
            res['time_stamp'] = str(r.response.date)
            res['response_status'] = r.response.status_code
            res['browser_id'] = getMode()
            res['response_status_text'] = r.response.reason
            # r.response.body  # FIXME: delivered as byte and can't always be decoded (e.g., gzip etc...)
            res['content_hash'] = None
            res['site_id'] = root_site_id
            res['subpage_id'] = subpage_id
            res['visit_id'] = str(root_site_id) + '-' + str(subpage_id)

            etld = tldextract.extract(r.url)
            res['etld'] = etld.domain + '.' + etld.suffix

            resList.append(res)
    return resList


def getCookies(root_site_id, root_site_url, cookiesFromVisits=None, onlyName=False):
    global param_root_site_id
    path = getSeleniumProfilePath(root_site_id) + '/Default/Cookies'

    try:
        sqliteConnection = sqlite3.connect(path)
        cursor = sqliteConnection.cursor()
        rows = cursor.execute(
            "SELECT expires_utc, is_secure, is_httponly, samesite, name, host_key, path,creation_utc, encrypted_value FROM cookies").fetchall()
    except:
        pushError(root_site_id, 'cookie_sql')

    sqliteConnection.close()

    if onlyName:
        cookieList = []
        for r in rows:
            cookieList.append(r[4])
        return cookieList
    else:
        cookieList = []
        try:
            cookiejar = ChromeCookieJar(path)
            for r in rows:
                try:
                    cookie = {}
                    cookie['expiry'] = timestamp2Datetime(r[0])
                    cookie['is_secure'] = r[1]
                    cookie['is_http_only'] = r[2]
                    cookie['same_site'] = r[3]
                    cookie['name'] = r[4]
                    cookie['host'] = r[5]
                    cookie['path'] = r[6]

                    cookie['time_stamp'] = timestamp2Datetime(r[7])

                    cookie['browser_id'] = getMode()
                    cookie['site_id'] = root_site_id
                    cookie['is_host_only'] = None  # FIXME:
                    cookie['is_session'] = None  # FIXME:
                    # cookie['first_party_domain'] =  None  # FIXME:
                    cookie['is_third_party'] = isThirdParty(
                        root_site_url, r[5])

                    cookie['value'] = ''
                    try:
                        for c in cookiejar:
                            if c.name == cookie['name'] and c.domain == cookie['host']:
                                cookie['value'] = c.value
                    except:
                        cookie['value'] = '[error]'
                        pass

                    if cookiesFromVisits is None:
                        cookie['visit_id'] = str(root_site_id) + '_0'

                    else:
                        try:
                            for item in cookiesFromVisits:
                                if r[4] in item[1]:
                                    cookie['visit_id'] = str(
                                        root_site_id) + '_' + str(item[0])
                                    break
                        except:
                            cookie['visit_id'] = str(root_site_id) + '_0'

                    cookieList.append(cookie)
                except Exception as e:
                    print('err_cookie', e)
                    pushError(root_site_id, 'cookie')
                finally:
                    continue
        except:
            pushError(root_site_id, 'cookie_extract')
        return cookieList


def getLocalStorage(root_site_id, driver):
    """
    try:
        driver=loadBrowser(root_site_id)
    except:
        pass
    try:
        func_timeout(3, getURL, args=(driver,root_site_url)) 
    except (FunctionTimedOut, TimeoutException):  
        driver.execute_script("window.stop();") 
        tab_restart_browser(driver)
        pass
    except Exception as e: 
        pass 
    """
    locList = []
    try:
        storage = LocalStorage(driver)

        for key in storage.items():
            ls = {}
            ls['browser_id'] = getMode()
            ls['key'] = key
            ls['value'] = storage.get(key)
            ls['site_id'] = root_site_id
            locList.append(ls)
    except:
        # pushError(root_site_id,'getLocalStorage_chrome')
        # driver.quit()
        str()
    return locList


def doInteraction(input_driver):
    from selenium.webdriver.common.keys import Keys

    element_id = 'body'
    try:
        input_driver.find_element_by_css_selector(
            element_id).send_keys(Keys.PAGE_DOWN)
    except:
        element_id = 'html'
    try:
        # simulate human interactions
        input_driver.find_element_by_css_selector(
            element_id).send_keys(Keys.PAGE_DOWN)
        time.sleep(0.3)
        input_driver.find_element_by_css_selector(
            element_id).send_keys(Keys.PAGE_DOWN)
        time.sleep(0.7)
        input_driver.find_element_by_css_selector(
            element_id).send_keys(Keys.PAGE_DOWN)
        time.sleep(0.2)
        input_driver.find_element_by_css_selector(
            element_id).send_keys(Keys.TAB)
        time.sleep(0.3)
        input_driver.find_element_by_css_selector(
            element_id).send_keys(Keys.TAB)
        time.sleep(0.3)
        input_driver.find_element_by_css_selector(
            element_id).send_keys(Keys.TAB)
        time.sleep(0.5)
        input_driver.find_element_by_css_selector(
            element_id).send_keys(Keys.END)
        time.sleep(1.3)
    except:
        pass

    """
https://
http://
    """


def getUrl2(driver, url, state):
    #print('I HAVE')
    # print(driver.requests)
    # print('DELETED!')
    del driver.requests  # deletes default chrome

    driver.get(url)

    try:
        WebDriverWait(driver, 0.5).until(EC.alert_is_present())
        alert = driver.switch_to.alert
        alert.dismiss()
        time.sleep(1)
    except (TimeoutException, WebDriverException):
        pass
    #print('URL loaded! ', url)
    state[0] = True


def getURL(driver, url):
    from collections import deque
    state = deque(maxlen=1)
    state.append(False)

    visit_start = datetime.now()
    t = threading.Thread(target=getUrl2,
                         args=(driver, url, state))
    t.start()
    while(True):
        if state[0] == True:
            return
        else:
            final = (datetime.now() - visit_start)
            total_sec = final.total_seconds()
           # print(str(visit_start), ' - ', str(total_sec),
            #      ' took and url loading... ', url,)
            #print('URL still loading - ', str(total_sec),'sec. - ', url)
            if total_sec >= getConfig('timeout'):
                # driver.execute_script("window.stop();")
                print('Raise TimeoutException! ', url)
                del state
                raise TimeoutException
            else:
                pass
        time.sleep(1)


def visitSite(url, root_site_url, root_site_id, is_subpage, p_visit_id, subpage_id, is_last_visit):
    # We follow OpenWPM visit-strategy here! (s. GetCommand & browser_commands)
    visit = VisitData(url)
    visit.timeout = 0

    try:
        driver = loadBrowser(root_site_id)
        visit.state = 1
    except:
        pushError(root_site_id, 'loadBrowser')
        visit.state = -1

    try:
        visitLogNew(root_site_id, url, subpage_id)
        #func_timeout(getConfig('timeout'), getURL, args=(driver, url))
        getURL(driver, url)
    except (FunctionTimedOut, TimeoutException):
        visit.timeout = 1
    except Exception as e:
        pushError(root_site_id, 'getURL-Timeout')
        visit.state = -1
    finally:
        visitLogUpdate(root_site_id, subpage_id,
                       state=visit.state, timeout=visit.timeout)

    try:
        try:
            if '_interaction' in getMode():
                doInteraction(driver)
        except:
            pushError(root_site_id, 'doInteraction')

        if is_last_visit:
            visit.localStorage = getLocalStorage(root_site_id, driver)

        try:
            current_url = driver.current_url
            tab_restart_browser(driver)
        except:
            pass

        visit.visit_id = p_visit_id

        try:
            visit.requests = getRequest(
                driver, current_url, root_site_url=root_site_url, root_site_id=root_site_id, subpage_id=subpage_id)
        except:
            pass

        try:
            visit.responses = getResponses(
                driver, root_site_id=root_site_id, subpage_id=subpage_id)
        except:
            pass

        visit.subpage = is_subpage

        print('visit ID ', p_visit_id)
        # crawlItem.visit_id = p_visit_id
        if visit.subpage is True:
            visit.root_url = root_site_url

        #del driver.requests

        driver.quit()
        time.sleep(1)

        try:
            visit.cookieList = getCookies(
                root_site_id, root_site_url, onlyName=True)
        except:
            pushError(root_site_id, 'cookies_only_name')
    except:
        driver.quit()
        time.sleep(1)
        pushError(root_site_id, 'visitSite')

    return visit

# code adopted from openwpm


def tab_restart_browser(webdriver):
    close_other_windows(webdriver)
    if webdriver.current_url.lower() == "about:blank":
        return
    # webdriver.execute_script("window.open('')")
    webdriver.close()
    assert len(webdriver.window_handles) == 1
    webdriver.switch_to.window(webdriver.window_handles[0])

# code adopted from openwpm


def close_other_windows(input_driver):
    main_handle = input_driver.current_window_handle
    windows = input_driver.window_handles
    if len(windows) > 1:
        for window in windows:
            if window != main_handle:
                input_driver.switch_to.window(window)
                input_driver.close()
        input_driver.switch_to.window(main_handle)


def visitSubpages(root_site_id, root_site_url, subpages, p_crawlDataList):
    print('visiting subpages for ', root_site_url)
    root_site_id = root_site_id
    crawlDataList = p_crawlDataList

    if subpages is None:
        return crawlDataList

    is_last_visit = False
    for index, sub in enumerate(subpages):
        visit_id = str(root_site_id) + '_' + str(index + 1)
        subpage_id = index + 1
        if subpage_id == len(subpages):
            is_last_visit = True
        try:
            visitData = visitSite(root_site_url=root_site_url, url=sub,
                                  root_site_id=root_site_id, is_subpage=True, p_visit_id=visit_id, subpage_id=subpage_id, is_last_visit=is_last_visit)
            crawlDataList.append(visitData)
        except:
            pushError(root_site_id, 'visitSubpages')
            #visitLogUpdate(root_site_id, subpage_id, state=-1)

    return crawlDataList


def getSeleniumProfilePath(root_site_id):
    path = ''
    if os.name == 'nt':
        path = os.getcwd() + '/profiles/chrome/' + str(root_site_id) + '/'
    else:
        path = os.getcwd() + '/profiles/chrome/' + str(root_site_id) + '/'
    return path


def changeSiteState(siteID, state, timeout=0):
    query = "UPDATE sites SET state_{} = {}, timeout={}  where id = {} ".format(
        getMode(), state, timeout, siteID)
    print(query)
    db.exec(query)


def runChromeInstance(p_queue, p_queue_item):
    """
    t = threading.Thread(target=loadRules)
    t.start()
    """
    print('\n\n\n\n I RUN A CHROME INSTANCE\n\n\n\n')
    root_site_url = p_queue_item.url
    root_site_id = p_queue_item.site_ID

    try:
        delFolder(getSeleniumProfilePath(root_site_id))
    except Exception as e:
        print(e)
        pass

    try:
        siteData = SiteData()
        siteData.browser_id = getMode()
        siteData.site_id = root_site_id

        visitList = []

        is_last_visit = False

        if p_queue_item.subpages == None:
            is_last_visit = True
        try:
            #visitLogNew(root_site_id, root_site_url, 0)
            visit_id = str(root_site_id) + "_0"
            visitData = visitSite(root_site_url, root_site_url, root_site_id, is_subpage=False,
                                  p_visit_id=visit_id, subpage_id=0, is_last_visit=is_last_visit)
            if is_last_visit:
                siteData.localStorage = visitData.localStorage
            visitList.append(visitData)  # crawl root site
        except:
            pushError(root_site_id, 'runChromeInstance')

        # crawl subpages
        if p_queue_item.subpages != None:
            subpages = p_queue_item.subpages.split('\n')
            visitList = visitSubpages(
                root_site_id, root_site_url, subpages, visitList)
            siteData.localStorage = visitList[len(visitList)-1].localStorage

        siteData.visitData = visitList
        # driver.quit()

        cookieList = []
        for item in visitList:
            cookieList.append(
                [int((item.visit_id).split('_')[1]), item.cookieList])
        cookieList.sort(key=lambda x: x[0])

        siteData.cookies = getCookies(
            root_site_id, root_site_url, cookiesFromVisits=cookieList)

        """#2768 - 11
        try:
            siteData.localStorage = getLocalStorage(root_site_url, root_site_id)
        except:
            pushError(root_site_id,'chrome_localStorage')
            pass
        """

        stream2BQ(siteData)

        try:
            delFolder(getSeleniumProfilePath(root_site_id))
            # str() #TODO: Activate it!
        except:
            pushError(root_site_id, 'delFolder')
            pass

        siteData.state = 2
        siteData.state_text = 'successful'

    except (FunctionTimedOut, TimeoutException):
        siteData.timeout = 1
        siteData.state = 4
        siteData.state_text = 'timeout'
        pushError(root_site_id, 'timeout')
    except:
        # -1: not startet, 0:waiting , 1: crawling , 2: success, 3: error, 4: timeout
        siteData.state = 3
        siteData.state_text = 'error'  # fixme: unsuccess :)
        pushError(root_site_id, 'chrome_crawler')
    finally:
        changeSiteState(root_site_id, siteData.state)

    return siteData


if __name__ == "__main__":
    import sys
    id = sys.argv[1]
    ready = False
    try:
        ready = eval(sys.argv[2])
    except:
        pass
    import sys
    db = DBOps()
    while(not ready):
        query = "SELECT 1 FROM sites WHERE ready IS TRUE and id=" + \
            str(id)
        rows = db.select(query)
        if len(rows) > 0:
            print('Site ready, so i restart!')
             import subprocess
            subprocess.Popen(['/home/user/miniconda3/envs/openwpm/bin/python3',
                              'CrawlerChrome.py', str(id), str(True), str(datetime.now())])
            os.system('kill %d' % os.getpid())
        else:
            query = "SELECT 1 FROM sites WHERE state_chrome_desktop_ger = 0  AND state_chrome_desktop_usa = 0  AND state_chrome_desktop_jp = 0  AND state_chrome_interaction_ger = 0  AND state_chrome_interaction_usa = 0  AND state_chrome_interaction_jp = 0  AND state_chromeheadless_desktop_ger = 0  AND state_chromeheadless_desktop_usa = 0  AND state_chromeheadless_desktop_jp = 0  AND state_chromeheadless_interaction_ger = 0  AND state_chromeheadless_interaction_usa = 0  AND state_chromeheadless_interaction_jp = 0  AND state_openwpm_desktop_ger = 0  AND state_openwpm_desktop_usa = 0  AND state_openwpm_desktop_jp = 0  AND state_openwpm_interaction_ger = 0  AND state_openwpm_interaction_usa = 0  AND state_openwpm_interaction_jp = 0  AND state_openwpmheadless_desktop_ger = 0  AND state_openwpmheadless_desktop_usa = 0  AND state_openwpmheadless_desktop_jp = 0  AND state_openwpmheadless_interaction_ger = 0  AND state_openwpmheadless_interaction_usa = 0  AND state_openwpmheadless_interaction_jp = 0 AND id=" + \
                str(id)
            rows = db.select(query)
            if len(rows) != 0:
                query = "UPDATE sites SET ready=true WHERE id=" + \
                    str(id)
                db.exec(query)
            time.sleep(3)
            continue

    r = db.select(
        'select id,  concat(scheme, site), subpages from sites where id= '+str(sys.argv[1]))[0]  # TODO: ADD state for 2. try
    queue_item = QueueItem(r[0], r[1], 'waiting', r[2], None, None, None)
    changeSiteState(id, 1)
    runChromeInstance(None, queue_item)
    print('finish:', queue_item.url)
    os.system('kill %d' % os.getpid())

 