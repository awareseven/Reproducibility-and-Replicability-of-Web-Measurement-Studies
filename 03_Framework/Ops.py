import os
from setup import getConfig, getMode
import shutil
from DBOps import DBOps
import tldextract

import dateutil.parser
from datetime import datetime, timedelta

def list2str(myList):
    if myList is None:
        return ''
    myString = ''
    for item in myList:
        myString = myString+item + ','
    return myString[:-1]

def lessMemory():  
    if os.name == 'nt':
        return False
    tot_m, used_m, free_m, s, buf, av = map(int, os.popen('free -m').readlines()[-2].split()[1:])
     
    print(av)
    if av<1750:
        return True
    else:
        return False

def getMemory():  
    if os.name == 'nt':
        return False
    tot_m, used_m, free_m, s, buf, av = map(int, os.popen('free -m').readlines()[-2].split()[1:])
    return av

def delProfileFolder(path):
    my_list = next(os.walk(path))[1]
    for folder in my_list:
        if folder.startswith('commander_'):
            full_path = path+"/" + folder
            try:
                shutil.rmtree(full_path)
            except OSError as e:
                print(e)
                continue

def delFolder(path):
    full_path = path
    try:
        shutil.rmtree(full_path)
    except OSError as e:
        pass
    
def isThirdParty(url1, url2):
    tld1 = tldextract.extract(url1)
    tld2 = tldextract.extract(url2)

    site1 = tld1.domain + tld1.suffix
    site2 = tld2.domain + tld2.suffix
    if site1 == site2:
        return 0
    else:
        return 1



def chunkList(lst, n):
    if lst is None:
        return None
    for i in range(0, len(lst), n):
        yield lst[i:i + n]

def addTime2Datetime(input_date, input_time, type='hour'): 
    if input_date.endswith('Z'):
        input_date=input_date[:-1]
    try:
        my_date = dateutil.parser.parse(input_date)
        if type == 'hour':
            add_hour = timedelta(hours=input_time)
        elif type == 'millisecond':
            add_hour = timedelta(milliseconds=input_time) 

        final_date = my_date + add_hour
        return str(final_date)
    except Exception as e:
        if 'Unknown string format' in str(e):
            return '9999-12-31 23:59:59'
        else:
            return input_date 
    
            
def timestamp2Datetime(stamp): 
#code adapted and modified slightly from https://github.com/borisbabic/browser_cookie3/blob/master/__init__.py#L279

    epoch_start = datetime(1601, 1, 1)
    utc_2=timedelta(hours=2)
    try:
        offset = min(int(stamp), 265000000000000000)
        delta = timedelta(microseconds=offset)
        expires = epoch_start + delta + utc_2
        expires = expires.timestamp()
        expires=datetime.fromtimestamp(expires)  
    except OSError as e:
        print(e) 
        offset = min(int(stamp), 32536799999000000)
        delta = timedelta(microseconds=offset)
        expires = epoch_start + delta + utc_2
        expires = expires.timestamp()  
        expires=datetime.fromtimestamp(expires) 
    return str(expires)


class LocalStorage:

    def __init__(self, driver) :
        self.driver = driver

    def __len__(self):
        return self.driver.execute_script("return window.localStorage.length;")

    def items(self) :
        return self.driver.execute_script( \
            "var ls = window.localStorage, items = {}; " \
            "for (var i = 0, k; i < ls.length; ++i) " \
            "  items[k = ls.key(i)] = ls.getItem(k); " \
            "return items; ")

    def keys(self) :
        return self.driver.execute_script( \
            "var ls = window.localStorage, keys = []; " \
            "for (var i = 0; i < ls.length; ++i) " \
            "  keys[i] = ls.key(i); " \
            "return keys; ")

    def get(self, key):
        return self.driver.execute_script("return window.localStorage.getItem(arguments[0]);", key)

    def set(self, key, value):
        self.driver.execute_script("window.localStorage.setItem(arguments[0], arguments[1]);", key, value)

    def has(self, key):
        return key in self.keys()

    def remove(self, key):
        self.driver.execute_script("window.localStorage.removeItem(arguments[0]);", key)

    def clear(self):
        self.driver.execute_script("window.localStorage.clear();")

    def __getitem__(self, key) :
        value = self.get(key)
        if value is None :
          raise KeyError(key)
        return value

    def __setitem__(self, key, value):
        self.set(key, value)

    def __contains__(self, key):
        return key in self.keys()

    def __iter__(self):
        return self.items().__iter__()

    def __repr__(self):
        return self.items().__str__()

def visitLogNew(site_id, url, subpage_id):  
    db = DBOps()
    visit_id = str(site_id) + '_' + str(subpage_id)
    query="INSERT INTO visits (site_id, url, subpage_id, visit_id, browser_id, start_time) values(" + str(site_id) + ", '"+ str(url) + "', "+ str(subpage_id) + ", '" + visit_id +  "', '"+ getMode() + "', '" + str(datetime.now()) + "')"
    print(query)
    db.exec(query)

def visitLogNew_Full(site_id, url, subpage_id, init_date, finish_date, timeout, state):  
    db = DBOps()
    visit_id = str(site_id) + '_' + str(subpage_id)
    query="INSERT INTO visits (site_id, url, subpage_id, visit_id, browser_id, start_time, finish_time, timeout, state) values(" + str(site_id) + ", '"+ str(url) + "', "+ str(subpage_id) + ", '" + visit_id +  "', '"+ getMode() + "', '" + str(init_date) + "', '" + str(finish_date) + "', '" + str(timeout) + "', " + str(state) + ")"
    print(query)
    db.exec(query)

def visitLogUpdate(site_id, subpage_id, state, dontChangeTime=False, timeout = 0):
    db = DBOps()
    if dontChangeTime:
        query= "UPDATE visits SET state=" + str(state) + ", timeout=" + str(timeout) + " WHERE site_id=" + str(site_id) + " AND subpage_id=" + str( subpage_id) + " AND browser_id= '"+ getMode() + "'"
    else:
        query = "UPDATE visits SET state=" + str(state) + ", finish_time='"+ str(datetime.now()) +"', timeout=" + str(timeout) + "  WHERE site_id=" + str(site_id) + " AND subpage_id=" + str( subpage_id) + " AND browser_id= '"+ getMode() + "'"
    db.exec(query)

def visitLog_ReqRes(visit_id, push_request, push_response):
    db = DBOps()
    query= "UPDATE visits SET push_request = " + str(push_request) + ", push_response= " + str(push_response) + " WHERE visit_id='" + str(visit_id) + "' and browser_id='"+ getMode() +"'" 
    db.exec(query)

def visitLog_CookieLocalStorage(site_id, push_cookie, push_localstorage):
    db = DBOps()
    query= "UPDATE visits SET push_cookie = " + str(push_cookie) + ", push_localstorage= " + str(push_localstorage) + " WHERE site_id='" + str(site_id) + "' and browser_id='"+ getMode() +"'" 
    db.exec(query)


# DEPRACATED
def newLogQueue(p_queue, p_site_id, log): 
    p_site_id=int(p_site_id)
    for i, q_value in enumerate(list(p_queue)): 
        print('p_queue[i].site_ID == p_site_id.', type(p_queue[i].site_ID) , type(p_site_id), (p_queue[i].site_ID == p_site_id))
        if p_queue[i].site_ID == p_site_id:
            p_queue[i].logs.append(log)
            print('added log: ' )
            #p_queue[i].logs=
            print(p_queue[i].logs)
            print('req log: ', log)

# DEPRACATED
def editLogQueue(p_queue, p_site_id, p_subpage_id, p_ops, p_value): 
    return True 
    p_site_id=int(p_site_id) 
    p_subpage_id=int(p_subpage_id)
    print('you called an edit', p_site_id, 'subpage', p_subpage_id, p_ops, p_value)
    for i, q_value in enumerate(list(p_queue)):    
        if p_queue[i].site_ID == p_site_id: #check if same site
            for z, log_value in enumerate(list(p_queue[i].logs)): # get all logs 
                print('I found the logs')
                #log seq.: #site_id, url, subpage_id, start_time, finish_time, state
                if p_queue[i].logs[z][2] == p_subpage_id: #check if same subpage_id
                    if p_ops=='start_time':
                        print('I changed ', p_queue[i].logs[z])
                        p_queue[i].logs[z][3] = p_value
                    elif p_ops == 'finish_time':
                        print('I changed 2', p_queue[i].logs[z])
                        p_queue[i].logs[z][4] = p_value
                        print('I fin', p_value)
                    elif p_ops == 'state':
                        print('I changed 3', p_queue[i].logs[z])
                        p_queue[i].logs[z][5] = p_value 
                        print('I state', p_value) 
                    print('I found the logs', p_queue[i].logs[z])

def terminateProcessBySiteID(id):
    import os
    all_processes = [(int(p), c) for p, c in [x.rstrip('\n').split(' ', 1) \
        for x in os.popen('ps h -eo pid:1,etime:1,command')]] 
    crawlers =[] 
    for item in all_processes:
        process_name=None
        if getMode().startswith('chrome'):
            process_name='process_name_chrome'
        else:
            process_name='process_name_openwpm' 
        if getConfig(process_name) in item[1]: 
            crawlers.append(item)

    my_list=[] 
    #kill crawlers that are timed-out
    for item in crawlers: 
        pid=item[0]
        process=item[1].split(' ')  
        site_id = process[3] 
        my_list.append(site_id) 
        if site_id==id:
            os.system('kill %d' % pid)
            #os.kill(pid)