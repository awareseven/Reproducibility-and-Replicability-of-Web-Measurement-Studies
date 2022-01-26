import sys
from DBOps import DBOps
from selenium.webdriver.chrome.options import Options
from seleniumwire import webdriver
import os
import tldextract
from urllib.parse import urlparse, unquote
import random
import time
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import (
    MoveTargetOutOfBoundsException,
    TimeoutException,
    WebDriverException,
)
import multiprocessing
from Ops import delFolder
# RUN IT ON WINDOWS!

db = DBOps()

check_ssl = True
extract_subpages = False


def start(multiProcess=1):
    query = "select site, id, scheme from sites where %state%  order by id"
    # query='select site, id from sites where state=1 and subpages_count=0 --%state%'
    state_text = ' '
    if check_ssl:
        state_text = ' state_scheme is null '
        if extract_subpages:
            state_text = state_text + ' and state_subpages is null '
        query = query.replace('%state%', state_text)
    elif extract_subpages:
        state_text = ' state_subpages is null '
        query = query.replace('%state%', state_text)

    rows = db.select(query)
    print(len(rows), ' rows remaning..')

    totalRow = len(rows)
    avarageRows = int(totalRow/multiProcess)
    splittedRows = []
    for i in range(multiProcess):
        if i == len(range(multiProcess))-1:
            splittedRows.append(rows)
        else:
            splittedRows.append(rows[0:avarageRows])
            del rows[0:avarageRows]
        print("splittedRows count: " + str(len(splittedRows)))
        print("row count: " + str(len(rows)))
    for item in splittedRows:
        p1 = multiprocessing.Process(
            target=startAnalyse, args=(item,))
        p1.start()


def startAnalyse(items):
    if extract_subpages:
        browser = loadBrowser()
        driver = browser[0]
        profile_path = browser[1]
    for r in items:
        try:

            print('check for,', r[0])
            query = "update sites set %scheme% %subpages% where id=" + \
                str(r[1])

            scheme = r[2]
            if check_ssl:
                scheme = findHost(r[0])
                query_text = "scheme='" + scheme + "', state_scheme=1 "
                if extract_subpages == True:
                    query_text = query_text+', '
                else:
                    query = query.replace('%subpages%', ' ')

                query = query.replace('%scheme%', query_text)

            if extract_subpages:
                full_url = scheme + r[0]
                subpages = extractSubpagesMain(driver, full_url)

                print(full_url, '\n\n', subpages)
                if subpages is None:
                    query_text = ' subpages=Null, subpages_count=0, state_subpages=1'
                    query = query.replace('%subpages%', query_text)
                else:
                    subpagesCount = len(subpages)
                    sql_subpages = list2str(subpages)
                    query_text = 'subpages=\'' + sql_subpages + '\', subpages_count=' + \
                        str(subpagesCount) + ', state_subpages=1 '
                    query = query.replace('%subpages%', query_text)
                if not check_ssl:
                    query = query.replace('%scheme%', ' ')

            # print(query)
            db.exec(query)
            delFolder(profile_path)
            print(r[1], r[0])
        except Exception as e:
            try:
                query = "INSERT into errors (source, site_id, message) values ( 'subpage', "+ r[1] +" '" + str(e).replace('\'','%quot%')+"' )"
                db.exec(query)
            except:
                query = "INSERT into errors (source, site_id, message) values ( 'subpage', "+ r[1] +" 'error' )"
                db.exec(query)
        finally:
            continue
    sys.exit()


def loadBrowser():

    options = Options()
    options.add_argument("--log-level=3")
    profile_path = getSeleniumProfilePath()
    print(profile_path)
    options.add_argument("user-data-dir=" + profile_path)
    # options.page_load_strategy = 'none'
    options.add_argument("no-sandbox")
    options.add_argument("disable-gpu")
    options.add_argument("disable-browser-side-navigation ")
    options.add_argument("headless")

    """
    """
    driver = webdriver.Chrome(
        executable_path=getDriverPath(), chrome_options=options)
    

    return driver, profile_path


def findHost(url):

    https = 'https://'
    http = 'http://'
    www = 'www.'

    if hostExists(https+url):
        return https
    elif hostExists(https+www+url):
        return https+www
    elif hostExists(http+www+url):
        return http+www
    # elif hostExists(http+url):
    #    return http
    else:
        return http


def hostExists(url):
    import urllib.request
    from urllib.request import urlopen, Request
    custom_header = {
                    'Connection': 'close',
                    'sec-ch-ua': '"Chromium";v="89", ";Not A Brand";v="99"',
                    'sec-ch-ua-mobile': '?0',
                    'Upgrade-Insecure-Requests': '1',
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.128 Safari/537.36',
                    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
                    'Sec-Fetch-Site': 'none',
                    'Sec-Fetch-Mode': 'navigate',
                    'Sec-Fetch-User': '?1',
                    'Sec-Fetch-Dest': 'document',
                    'Accept-Encoding': 'gzip, deflate',
                    'Accept-Language': 'de-DE,de;q=0.9,en-US;q=0.8,en;q=0.7'
                    }
    req = Request(url, headers=custom_header)
    try:
        urllib.request.urlopen(req, timeout=10).getcode()
        return True
    except Exception as e:
        print(e, url)
        if 'HTTP Error' in str(e):  # if it returns an error, the URL exists :)
            return True
        else:
            return False
        # if 'CERTIFICATE_VERIFY_FAILED' in str(e.args):
         #   str()


def extractSubpagesMain(input_driver, url):
    # driver = loadBrowser()
    driver = input_driver

    if check_ssl == False:
        browser = loadBrowser()
        driver = browser[0]
        profile_path = browser[1]

    visitSite(driver, url)

    # driver.get(url)
    subpages = extractSubpages(driver, url, None)

    if subpages != None:
        for i in subpages:
            if len(subpages) < 25:
                # print('No enough link in startpage, visiting: ', i)

                visitSite(driver, i)

                subpages = extractSubpages(driver, url, subpages)
                if len(subpages) >= 25:
                    break
            else:
                break

    driver.close()

    return subpages


def visitSite(driver, url):

    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC

    driver.set_page_load_timeout(15)
    driver.implicitly_wait(1)

    try:
        driver.get(url)
    except TimeoutException:
        pass

    try:
        WebDriverWait(driver, 0.5).until(EC.alert_is_present())
        alert = driver.switch_to.alert
        alert.dismiss()
    except (TimeoutException, WebDriverException):
        pass


def extractSubpages(input_driver, url, list_exists=None):
    root_url = url
    # root_url = url

    current_url = tldextract.extract(root_url)
    print(current_url)

    a_links = input_driver.find_elements_by_xpath("//a[@href]")

    random.shuffle(a_links)

    print('total found links:', len(a_links))
    if list_exists is not None:
        str()  # print('existing list has', len(list_exists))

    if list_exists == None:
        a_list = []
    else:
        a_list = list_exists

    for a in a_links:
        a_list = list(dict.fromkeys(a_list))

        try:
            a_url = a.get_attribute("href")
        except:
            print('Not well formated URL')
            continue

        try:
            sub_url = tldextract.extract(a_url)
        except:
            continue
        if len(a_list) >= 25:
            break

        current_url_parsed = urlparse(root_url)
        sub_url_parsed = urlparse(a_url)

        quoted_sub_url_path = unquote(unquote(
            unquote(unquote(sub_url_parsed.path) + '-' + unquote(sub_url_parsed.query))))

        # print('sub_url:',sub_url,'\n','current_url_parsed:',current_url_parsed,'\n','sub_url_parsed: ',sub_url_parsed,'\n','quoted_sub_url_path: ',quoted_sub_url_path)

        # if path has https://, avoid redirections
        if 'http://' in quoted_sub_url_path or 'https://' in quoted_sub_url_path:
            continue
        if sub_url_parsed.path == '/' and sub_url_parsed.fragment != '':  # ignores URLs like /#anchor
            continue
        if a_url.startswith('javascript:') or a_url.startswith('mailto:') or a_url.startswith('tel:'):
            continue

        # if url starts with https://
        if sub_url_parsed.scheme == 'http' or sub_url_parsed.scheme == 'https':
            if sub_url.domain == current_url.domain and sub_url.suffix == current_url.suffix:
                found_url = a.get_attribute("href")
                if isValid(a_list, found_url):
                    a_list.append(found_url)
        elif sub_url_parsed.scheme == '' and sub_url_parsed.netloc == '':  # if the link is like <a href="/hi.html">
            found_url = current_url_parsed.scheme + '://' + current_url_parsed.netloc
            if sub_url_parsed.path.startswith('/'):
                found_url = found_url + a.get_attribute("href")
            else:
                found_url = found_url + current_url_parsed.path + \
                    '/' + a.get_attribute("href")
            if isValid(a_list, found_url):
                a_list.append(found_url)

    # a_list = random.sample(a_list, getConfig('subpage_to_visit'))

    if len(a_list) == 0:
        a_list = None
    return a_list


def isValid(list, new_url):  
    # if link contains Anchor, this helps good, to eliminate them!
    for a in list:
        new_a = urlparse(new_url)
        a_in_list = urlparse(a)
        if new_a.netloc == a_in_list.netloc and new_a.path == a_in_list.path and new_a.query == a_in_list.query:
            return False
    
    if new_url.endswith('#') or new_url.endswith('/'):
        if new_url[:-1] in list:
            return False
    
    if new_url.endswith('/#'):
        if new_url[:-2] in list:
            return False 

    blacklist_ext=("ods", ".xls", ".xlsx", ".csv", ".ics", ".vcf", ".3dm", ".3ds", ".max", ".bmp", ".dds", ".gif", ".jpg", ".jpeg", ".png", ".psd", ".xcf", ".tga", ".thm", ".tif", ".tiff", ".yuv", ".ai", ".eps", ".ps", ".svg", ".dwg", ".dxf", ".gpx", ".kml", ".kmz", ".webp", ".3g2", ".3gp", ".aaf", ".asf", ".avchd", ".avi", ".drc", ".flv", ".m2v", ".m4p", ".m4v", ".mkv", ".mng", ".mov", ".mp2", ".mp4", ".mpe", ".mpeg", ".mpg", ".mpv", ".mxf", ".nsv", ".ogg", ".ogv", ".ogm", ".qt", ".rm", ".rmvb", ".roq", ".srt", ".svi", ".vob", ".webm", ".wmv", ".yuv", ".aac", ".aiff", ".ape", ".au", ".flac", ".gsm", ".it", ".m3u", ".m4a", ".mid", ".mod", ".mp3", ".mpa", ".pls", ".ra", ".s3m", ".sid", ".wav", ".wma", ".xm", ".7z", ".a", ".apk", ".ar", ".bz2", ".cab", ".cpio", ".deb", ".dmg", ".egg", ".gz", ".iso", ".jar", ".lha", ".mar", ".pea", ".rar", ".rpm", ".s7z", ".shar", ".tar", ".tar.xz", ".tbz2", ".tgz", ".tlz", ".war", ".whl", ".xpi", ".zip", ".zipx", ".xz", ".pak", ".exe", ".msi", ".bin", ".command", ".sh", ".bat", ".crx", ".clj", ".cpp", ".cs", ".cxx", ".el",  "h", ".java", ".lua", ".m", ".m4", ".po", ".py", ".rb", ".rs", ".sh", ".swift", ".vb", ".vcxproj", ".xcodeproj", ".xml", ".diff", ".patch", ".js", ".css", ".js", ".jsx", ".less", ".scss", ".wasm", ".php", ".eot", ".otf", ".ttf", ".woff", ".woff2", ".ppt", ".odp", ".doc", ".docx", ".ebook", ".log", ".md", ".msg", ".odt", ".org", ".pages", ".pdf", ".rtf", ".rst", ".tex", ".txt", ".wpd", ".wps", ".mobi", ".epub", ".azw1", ".azw3", ".azw4", ".azw6", ".azw", ".cbr", ".cbz")

    if new_url.endswith(blacklist_ext):
        return False
    
    blacklist_contains=("'")
    if blacklist_contains in new_url:
        return False

    whitelist_start=('https://','http://')
    if new_url.startswith(whitelist_start): #or  ('\\' in new_url) or ("'" in new_url):
        return True
    else:
        return False


def getSeleniumProfilePath():
    import tempfile
    dirpath=tempfile.mkdtemp()
    return dirpath

    path=''
    if os.name == 'nt':
        path=os.getcwd() + '/profiles/chrome/main_commander/'
    else:
        path=os.getcwd() + '/profiles/chrome/main_commander/'
    return path


def getDriverPath():
    path=''
    if os.name == 'nt':
        path=os.getcwd() + '/drivers/chromedriver.exe'
    else:
        path=os.getcwd() + '/drivers/chromedriver'
    return path


def list2str(myList):
    if myList is None:
        return ' Null'
    myString=''
    for item in myList:
        myString = myString + item.replace('\n','') + '\n'
    return myString[:-1]

if __name__ == "__main__":
    start(30)
