
from DBOps import DBOps
import os
from google.cloud import bigquery
import multiprocessing

os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = os.getcwd() + \
    '/resources/google.json'
client = bigquery.Client()


def pushRows(p_tableID, p_rows, p_timeout=60):
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
        errors = client.insert_rows_json(table_id, p_rows, timeout=30)
        if errors == []:
            print('pushed rows to BigQuery:' +
                  p_tableID + ': ' + str(len(p_rows)))
        else:
            raise Exception(
                p_tableID + ": Encountered errors while inserting rows: {}".format(errors))


def extractSubpages(rows):
    for item in rows:
        subpages = item[3]

        page_list = []

        # for root site

        page_obj = {}
        page_obj['site_id'] = item[0]
        page_obj['page'] = item[4] + item[2]
        page_obj['site'] = item[2]
        page_obj['subpage_id'] = 0
        page_obj['visit_id'] = str(
            page_obj['site_id']) + "_" + str(page_obj['subpage_id'])
        page_list.append(page_obj)

        if subpages is None:
            pushRows('webmeasurement.data.pages', page_list)
            page_list = []
            continue
        else:
            subpages_splitted = subpages.split('\n')

        for index, s in enumerate(subpages_splitted):
            page_obj = {}
            page_obj['site_id'] = item[0]
            page_obj['page'] = s
            page_obj['site'] = item[2]
            page_obj['subpage_id'] = index+1
            page_obj['visit_id'] = str(
                page_obj['site_id']) + "_" + str(page_obj['subpage_id'])

            page_list.append(page_obj)

        pushRows('webmeasurement.data.pages', page_list)
        page_list = []


def startAnalyse(thread_count=10):
    db = DBOps()
    rows = db.select(
        "select id, rank, site, subpages, scheme from sites order by id")

    totalRow = len(rows)
    print("Total Rows: ", totalRow)
    avarageRows = int(totalRow/thread_count)

    splittedRows = []
    for i in range(thread_count):
        if i == len(range(thread_count)) - 1:
            splittedRows.append(rows)
        else:
            splittedRows.append(rows[0:avarageRows])
            del rows[0:avarageRows]

        print("splittedRows count: " + str(len(splittedRows)))
        print("row count: " + str(len(rows)))

    for item in splittedRows:
        p1 = multiprocessing.Process(
            target=extractSubpages, args=(item,))
        p1.start()


if __name__ == '__main__':
    startAnalyse()
