class SiteData(object):
    def __init__(self, browser_id=None, site_id=None, localStorage=None, cookies=None, visitData=None, state=None, state_text=None, timeout=None):
        self.browser_id = browser_id
        #self.visit_id = visit_id
        self.site_id = site_id
        self.localStorage = localStorage
        self.cookies = cookies
        self.visitData = visitData 
        self.state = state
        self.state_text = state_text
        self.timeout = timeout
        
class VisitData(object):
    def __init__(self, url, subpage=None, root_url=None, requests=None, responses=None, visit_id=None, subpage_id=None, timeout=None, cookieList=None, state=None, localStorage=None):
        self.url = url
        self.subpage = subpage
        self.requests = requests
        self.responses = responses
        self.root_url = root_url
        self.visit_id = visit_id
        self.subpage_id = subpage_id
        self.timeout = timeout
        self.cookieList = cookieList
        self.state = state
        self.localStorage = localStorage


class QueueItem(object):
    def __init__(self, site_ID, url, state, subpages, start_time, finish_time, logs):
        self.site_ID = site_ID
        self.url = url
        self.state = state
        self.start_time = start_time
        self.finish_time = finish_time
        self.subpages = subpages
        if logs is None:
            self.logs = []
        else:
            self.logs = logs
