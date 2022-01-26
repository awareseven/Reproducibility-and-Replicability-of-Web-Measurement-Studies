from base64 import encode
from re import A
from Ops import chunkList, visitLog_CookieLocalStorage, visitLog_ReqRes
from setup import getConfig, getMode
from DBOps import DBOps
from google.cloud import bigquery
import os
db = DBOps()


def execBQRows(p_tableID, p_rows, p_timeout=45):
    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = os.getcwd() + \
        '/resources/google.json'
    client = bigquery.Client()
    table_id = p_tableID

    try:
        errors = client.insert_rows_json(table_id, p_rows, timeout=p_timeout)
        if errors == []:
            print('pushed rows to BigQuery:' +
                  p_tableID + ': ' + str(len(p_rows)))
        else:
            raise Exception(
                p_tableID + ": Encountered errors while inserting rows: {}".format(errors))
    except:
        print('error while pushing.. retry..')
        errors = client.insert_rows_json(table_id, p_rows, timeout=15)
        if errors == []:
            print('pushed rows to BigQuery:' +
                  p_tableID + ': ' + str(len(p_rows)))
        else:
            raise Exception(
                p_tableID + ": Encountered errors while inserting rows: {}".format(errors))


def stream2BQ(p_siteData):
    try:
        siteData = p_siteData

        max_row = getConfig('bigquery_insert_rows')

        push_cookie = 0
        push_localstorage = 0

        # push cookies
        if siteData.cookies:
            cookies = chunkList(siteData.cookies, max_row)
            if cookies is not None:
                for item in cookies:
                    push_cookie = push_cookie + len(item)
                    try:
                        print(siteData.site_id, ': pushing cookies: ', len(item))
                        execBQRows('webmeasurement.data.cookies', item, 25)
                    except Exception as e:
                        pushError(siteData.site_id,
                                  'push_cookie', backup_json=item)
                        push_cookie = -1 * push_cookie
                        pass

        # push localStorage
        if siteData.localStorage:
            localStorage = chunkList(siteData.localStorage, max_row)
            if localStorage is not None:
                for item in localStorage:
                    push_localstorage = push_localstorage + len(item)
                    try:
                        print(siteData.site_id,
                              ': pushing localStorage:', len(item))
                        execBQRows(
                            'webmeasurement.data.localstorage', item, 25)
                    except Exception as e:
                        pushError(siteData.site_id,
                                  ': bq_localStorage', backup_json=item)
                        push_localstorage = -1 * push_localstorage
                        pass

        visitLog_CookieLocalStorage(
            siteData.site_id, push_cookie, push_localstorage)

        # BEGIN REQUESTS
        # first try to push all
        all_requests = []
        all_response = []
        stats_req_resp = {}
        for visit in siteData.visitData:
            len_req = 0
            len_res = 0
            if visit.requests is not None:
                for item in visit.requests:
                    all_requests.append(item)
                len_req = len(visit.requests)
            if visit.responses is not None:
                for item in visit.responses:
                    all_response.append(item)
                len_res = len(visit.responses)
            # .append[[visit.visit_id, len(item.requests), len(item.responses)]]
            stats_req_resp[visit.visit_id] = [len_req, len_res]

        all_pushed_req = False
        try:
            execBQRows('webmeasurement.data.requests', all_requests, 45)
            all_pushed_req = True
        except:
            all_pushed_req = False
            pushError(siteData.site_id, 'push_bulk_req')
            #push_request = -1 * push_request

        if all_pushed_req:
            str()  # update stats
        else:
            str()  # push one-by-one
            for visit in siteData.visitData:
                push_request = 0
                # push requests
                requests = chunkList(visit.requests, max_row)
                if requests is not None:
                    for item in requests:
                        print(siteData.site_id,
                              ': pushing chunked req: ', str(len(item)))
                        push_request = push_request + len(item)

                        try:
                            execBQRows(
                                'webmeasurement.data.requests', item, 15)
                        except:
                            stats_req_resp[visit.visit_id] = -1 * push_request
                            pushError(siteData.site_id,
                                      ': push_request', backup_json=item)
        # END REQUESTS

        # BEGIN RESPONSES

        all_pushed_res = False
        try:
            execBQRows('webmeasurement.data.responses', all_response, 45)
            all_pushed_res = True
        except:
            all_pushed_res = False
            pushError(siteData.site_id, 'push_bulk_resp')
            #push_request = -1 * push_request
        if all_pushed_res:
            str()  # update stats
        else:
            for visit in siteData.visitData:
                push_response = 0
                # push requests
                # push responses
                responses = chunkList(visit.responses, max_row)
                if responses is not None:
                    for item in responses:
                        push_response = push_response + len(item)
                        print(siteData.site_id,
                              ': pushing chunked res: ', str(len(item)))
                        try:
                            execBQRows(
                                'webmeasurement.data.responses', item, 15)
                        except:
                            stats_req_resp[visit.visit_id] = -1 * push_response
                            pushError(siteData.site_id,
                                      'push_response', backup_json=item)
        for item in stats_req_resp:
            try:
                visitLog_ReqRes(
                    item, stats_req_resp[item][0], stats_req_resp[item][1])
            except:
                pushError(siteData.site_id, 'update_stats-' + item)

        # END RESPONSES
        """"
        for visit in siteData.visitData:  
            push_request = 0
            push_response = 0
            # push requests 
            requests = chunkList(visit.requests, max_row)
            if requests is not None:  
                for item in requests:
                    print('pushing chunked req: ', str(len(item)))
                    push_request = push_request + len(item)
                    try:
                        execBQRows('webmeasurement.data.requests', item) 
                    except:
                        pushError(siteData.site_id, 'push_request', backup_json=item)
                        push_request = -1 * push_request
                        print(item) 
                
            
            # push responses
            if responses is not None:
                responses = chunkList(visit.responses, max_row)    
                for item in responses:
                    push_response = push_response + len(item)
                    print('pushing chunked res: ', str(len(item)))
                    try:
                        execBQRows('webmeasurement.data.responses', item) 
                    except:
                        print(item)
                        push_response = -1 * push_response
                        pushError(siteData.site_id, 'push_response', backup_json=item)     
            visitLog_ReqRes(visit.visit_id, push_request, push_response) 
        """

    except:
        pushError(siteData.site_id, 'pushBQ')

    # Deprecated, delete if any test is successful.
    """
        # push localStorage


    ##

    if siteData.crawlData != None:
        # stream root & subpages
        allReq = []
        allRes = []
        for site in siteData.crawlData:
            allReq = allReq + site.requests
            allRes = allRes + site.responses

        print('total requests: ', len(allReq))
        print('total responses: ', len(allRes))

        allReq = chunkList(allReq, getConfig('bigquery_insert_rows'))
        allRes = chunkList(allRes, getConfig('bigquery_insert_rows'))

        for item in allReq:
            print('pushing chunked req: ', str(len(item)))
            try:
                execBQRows('webmeasurement.data.http_request',
                           item)
                push_request=1
            except:
                pushError(siteData.site_id, 'bq_request')
                push_request=-1
                print(item)

        for item in allRes:
            print('pushing chunked res: ', str(len(item)))
            try:
                execBQRows('webmeasurement.data.http_response',
                       item)
                push_response=1
            except:
                print(item)
                push_response=-1
                pushError(siteData.site_id, 'bq_response')
        
        if siteData.cookies:
            try:
                print('pushing cookies: ', len(siteData.cookies))
                execBQRows('webmeasurement.data.cookies', siteData.cookies)
                push_cookie=1
            except Exception as e:
                pushError(siteData.site_id, 'bq_cookie')
                print(item)
                push_cookie=-1
                pass

        if siteData.localStorage:
            try:
                print('pushing localStorage:', len(siteData.localStorage))
                execBQRows('webmeasurement.data.localstorage',
                            siteData.localStorage)
                push_localstorage=1
            except Exception as e:
                pushError(siteData.site_id, 'bq_localStorage') 
                push_localstorage=-1
                pass
    """

    return True


def pushError(site_id, source, params=None, backup_json=None):

    if backup_json == None:
        backup_json = "null"
    else:
        import json
        import base64
        encoded = base64.b64encode(
            str(json.dumps(backup_json)).encode('utf-8')).decode('utf-8')
        # encoded=str(backup_json).encode('utf-8')
        backup_json = "'" + str(encoded) + "'"
        #backup_json = str(encoded)[1:]

    try:
        import sys
        import os
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        err = str(fname) + ':' + str(exc_tb.tb_lineno) + ' - ' + \
            str(exc_obj) + ' - ' + str(exc_type)  # str(exc_type)
    except:
        err = 'UNKNOWN!'
    try:
        query = "INSERT into errors (source, site_id, message, browser_id, backup) values ( '" + source + "', '" + str(
            site_id) + "', '" + err.replace("'", "") + "', '" + getMode() + "'," + backup_json + ")"

        db.exec(query)
    except Exception as e:
        print(e)
        import time
        time.sleep(2)
        try:
            query = "INSERT into errors (source, site_id, message, browser_id) values ( '" + source + "', '" + str(
                site_id) + "', '" + err.replace("'", "") + "', '" + getMode() + "' )"
            db.exec(query)
        except Exception as e:
            print(e)
            print('cant connect DB')


def generateInsertRows(p_queries, dataList, table, columns):

    if dataList is None:
        return p_queries
    if len(dataList) == 0:
        return p_queries

    max_number = getConfig('sql_insert_multiple_rows')
    queries = p_queries
    query_insert = "INSERT INTO " + table + \
        " (" + str(list(columns)
                   ).replace('[', '').replace(']', '').replace('\'', '') + ") VALUES "

    query_sub = ''
    i = 0
    for item in dataList:
        query_value = '('
        for x in columns:
            val = str(item[x])

            if item[x] == None:
                val = 'Null'
            else:
                val = "'" + val + "'"

            if query_value != '(':
                val = ',' + val

            query_value = query_value + val

        query_value = query_value + ' )'
        query_value = query_value

        if i == 0:
            query_sub = query_sub + query_value
        else:
            query_sub = query_sub + ", " + query_value

        if (i % max_number == 0 and i != 0) or i == len(dataList)-1:
            query_sub = query_insert + query_sub
            query_sub = query_sub.replace('VALUES ,', ' VALUES')
            queries.append(query_sub)
            query_sub = ''
        i = i + 1
    return queries


def execQueries(queries):
    # OLD DML BIGQUERY
    from google.cloud import bigquery
    import os
    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = os.getcwd() + \
        '/resources/google.json'

    print('Import job started, total rows:' + str(len(queries)))
    client = bigquery.Client()
    for q in queries:
        results = client.query(q)
        for err in results:
            print(err)
