from numpy.lib.function_base import average
from sklearn.metrics import jaccard_score
import numpy as np
import os
from google.cloud import bigquery
from adblockparser import AdblockRules
from datetime import datetime
import time
import multiprocessing

os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = os.getcwd() + \
    '/resources/google_t.json'
client = bigquery.Client()

thread_count = 10
chunk_size = 10
limit_size = 10000000

split_type = ','

push_table = 'compare-web-measurements.data.similarity_tracker_details'


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

# 1  profile.chrome_desktop_ger
# 2  profile.chrome_desktop_usa
# 3  profile.chrome_desktop_jp
# 4  profile.chrome_interaction_ger
# 5  profile.chrome_interaction_usa
# 6  profile.chrome_interaction_jp
# 7  profile.chromeheadless_desktop_ger
# 8  profile.chromeheadless_desktop_usa
# 9  profile.chromeheadless_desktop_jp
# 10  profile.chromeheadless_interaction_ger
# 11  profile.chromeheadless_interaction_usa
# 12  profile.chromeheadless_interaction_jp
# 13  profile.openwpm_desktop_ger
# 14  profile.openwpm_desktop_usa
# 15  profile.openwpm_desktop_jp
# 16  profile.openwpm_interaction_ger
# 17  profile.openwpm_interaction_usa
# 18  profile.openwpm_interaction_jp
# 19  profile.openwpmheadless_desktop_ger
# 20  profile.openwpmheadless_desktop_usa
# 21  profile.openwpmheadless_desktop_jp
# 22  profile.openwpmheadless_interaction_ger
# 23 profile.openwpmheadless_interaction_usa
# 24  profile.openwpmheadless_interaction_jp


def start():
    query_tracker = "SELECT visit_id, profile.chrome_desktop_ger  , profile.chrome_desktop_usa, profile.chrome_desktop_jp, profile.chrome_interaction_ger, profile.chrome_interaction_usa, profile.chrome_interaction_jp, profile.chromeheadless_desktop_ger, profile.chromeheadless_desktop_usa, profile.chromeheadless_desktop_jp, profile.chromeheadless_interaction_ger, profile.chromeheadless_interaction_usa, profile.chromeheadless_interaction_jp, profile.openwpm_desktop_ger, profile.openwpm_desktop_usa, profile.openwpm_desktop_jp, profile.openwpm_interaction_ger, profile.openwpm_interaction_usa, profile.openwpm_interaction_jp, profile.openwpmheadless_desktop_ger, profile.openwpmheadless_desktop_usa, profile.openwpmheadless_desktop_jp, profile.openwpmheadless_interaction_ger, profile.openwpmheadless_interaction_usa, profile.openwpmheadless_interaction_jp, browser.chrome, browser.firefox,  location.ger, location.usa, location.jp, mod.desktop, mod.interaction, mod.headless FROM `compare-web-measurements.data.eval_tracker_by_page` WHERE (browser.firefox  is not null or browser.chrome is not null) and in_scope=1"

    query_header = "SELECT visit_id, profile.chrome_desktop_ger  , profile.chrome_desktop_usa, profile.chrome_desktop_jp, profile.chrome_interaction_ger, profile.chrome_interaction_usa, profile.chrome_interaction_jp, profile.chromeheadless_desktop_ger, profile.chromeheadless_desktop_usa, profile.chromeheadless_desktop_jp, profile.chromeheadless_interaction_ger, profile.chromeheadless_interaction_usa, profile.chromeheadless_interaction_jp, profile.openwpm_desktop_ger, profile.openwpm_desktop_usa, profile.openwpm_desktop_jp, profile.openwpm_interaction_ger, profile.openwpm_interaction_usa, profile.openwpm_interaction_jp, profile.openwpmheadless_desktop_ger, profile.openwpmheadless_desktop_usa, profile.openwpmheadless_desktop_jp, profile.openwpmheadless_interaction_ger, profile.openwpmheadless_interaction_usa, profile.openwpmheadless_interaction_jp, browser.chrome, browser.firefox,  location.ger, location.usa, location.jp, mod.desktop, mod.interaction, mod.headless FROM `compare-web-measurements.data.eval_header_by_page` WHERE in_scope=1"

    query_csp = "SELECT visit_id, profile.chrome_desktop_ger  , profile.chrome_desktop_usa, profile.chrome_desktop_jp, profile.chrome_interaction_ger, profile.chrome_interaction_usa, profile.chrome_interaction_jp, profile.chromeheadless_desktop_ger, profile.chromeheadless_desktop_usa, profile.chromeheadless_desktop_jp, profile.chromeheadless_interaction_ger, profile.chromeheadless_interaction_usa, profile.chromeheadless_interaction_jp, profile.openwpm_desktop_ger, profile.openwpm_desktop_usa, profile.openwpm_desktop_jp, profile.openwpm_interaction_ger, profile.openwpm_interaction_usa, profile.openwpm_interaction_jp, profile.openwpmheadless_desktop_ger, profile.openwpmheadless_desktop_usa, profile.openwpmheadless_desktop_jp, profile.openwpmheadless_interaction_ger, profile.openwpmheadless_interaction_usa, profile.openwpmheadless_interaction_jp, browser.chrome, browser.firefox,  location.ger, location.usa, location.jp, mod.desktop, mod.interaction, mod.headless FROM `compare-web-measurements.data.eval_csp_by_page`"

    query_csp_2 = "SELECT visit_id, profile.chrome_desktop_ger  , profile.chrome_desktop_usa, profile.chrome_desktop_jp, profile.chrome_interaction_ger, profile.chrome_interaction_usa, profile.chrome_interaction_jp, profile.chromeheadless_desktop_ger, profile.chromeheadless_desktop_usa, profile.chromeheadless_desktop_jp, profile.chromeheadless_interaction_ger, profile.chromeheadless_interaction_usa, profile.chromeheadless_interaction_jp, profile.openwpm_desktop_ger, profile.openwpm_desktop_usa, profile.openwpm_desktop_jp, profile.openwpm_interaction_ger, profile.openwpm_interaction_usa, profile.openwpm_interaction_jp, profile.openwpmheadless_desktop_ger, profile.openwpmheadless_desktop_usa, profile.openwpmheadless_desktop_jp, profile.openwpmheadless_interaction_ger, profile.openwpmheadless_interaction_usa, profile.openwpmheadless_interaction_jp, browser.chrome, browser.firefox,  location.ger, location.usa, location.jp, mod.desktop, mod.interaction, mod.headless FROM `compare-web-measurements.data.eval_csp_by_page` where profile.chrome_desktop_ger   is not null and profile.chrome_desktop_usa is not null and profile.chrome_desktop_jp is not null and profile.chrome_interaction_ger is not null and profile.chrome_interaction_usa is not null and profile.chrome_interaction_jp is not null and profile.chromeheadless_desktop_ger is not null and profile.chromeheadless_desktop_usa is not null and profile.chromeheadless_desktop_jp is not null and profile.chromeheadless_interaction_ger is not null and profile.chromeheadless_interaction_usa is not null and profile.chromeheadless_interaction_jp is not null and profile.openwpm_desktop_ger is not null and profile.openwpm_desktop_usa is not null and profile.openwpm_desktop_jp is not null and profile.openwpm_interaction_ger is not null and profile.openwpm_interaction_usa is not null and profile.openwpm_interaction_jp is not null and profile.openwpmheadless_desktop_ger is not null and profile.openwpmheadless_desktop_usa is not null and profile.openwpmheadless_desktop_jp is not null and profile.openwpmheadless_interaction_ger is not null and profile.openwpmheadless_interaction_usa is not null and profile.openwpmheadless_interaction_jp is not null"

    query_job = client.query(query_tracker)
    try:
        rows = query_job.result().to_dataframe().values.tolist()
        print('query data loaded.')
    except Exception as e:
        print(e)
        print('error')

    totalRow = len(rows)
    print("Total Rows: ", totalRow)
    avarageRows = int(totalRow/thread_count)

    splittedRows = []
    for i in range(thread_count):
        if i == len(range(thread_count))-1:
            splittedRows.append(rows)
        else:
            splittedRows.append(rows[0:avarageRows])
            del rows[0:avarageRows]

        print("splittedRows count: " + str(len(splittedRows)))
        print("row count: " + str(len(rows)))

    for item in splittedRows:
        p1 = multiprocessing.Process(
            target=doAnalyse, args=(item,))
        p1.start()


def doAnalyse(rows):
    s = []
    for item in rows:
        profileList = []
        sim = {}

        sim['visit_id'] = item[0]

        profileList.append(item[1])
        profileList.append(item[2])
        profileList.append(item[3])
        profileList.append(item[4])
        profileList.append(item[5])
        profileList.append(item[6])
        profileList.append(item[7])
        profileList.append(item[8])
        profileList.append(item[9])
        profileList.append(item[10])
        profileList.append(item[11])
        profileList.append(item[12])
        profileList.append(item[13])
        profileList.append(item[14])
        profileList.append(item[15])
        profileList.append(item[16])
        profileList.append(item[17])
        profileList.append(item[18])
        profileList.append(item[19])
        profileList.append(item[20])
        profileList.append(item[21])
        profileList.append(item[22])
        profileList.append(item[23])
        profileList.append(item[24])

        profiles = []
        for tmp in profileList:
            if tmp is None:
                profiles.append([])
            else:
                profiles.append(tmp.split(split_type))
        sim['profile_similarity'] = compareJaccardMultipleSets(profiles)
        browserList = []
        browserList.append(item[25])
        browserList.append(item[26])
        browsers = []
        for tmp in browserList:
            if tmp is None:
                browsers.append([])
            else:
                browsers.append(tmp.split(split_type))
        sim['browser_similarity'] = compareJaccardMultipleSets(browsers)

        locationList = []
        locationList.append(item[27])
        locationList.append(item[28])
        locationList.append(item[29])
        locations = []
        for tmp in locationList:
            if tmp is None:
                locations.append([])
            else:
                try:
                    locations.append(tmp.split(split_type))
                except Exception as e:
                    print(e)
                    print('s', tmp, locationList)
        sim['location_similarity'] = compareJaccardMultipleSets(locations)

        modList = []
        modList.append(item[30])
        modList.append(item[31])
        modList.append(item[32])
        mods = []
        for tmp in modList:
            if tmp is None:
                mods.append([])
            else:
                mods.append(tmp.split(split_type))
        sim['mod_similarity'] = compareJaccardMultipleSets(mods)

        modHeadlessList = []
        modHeadlessList.append(item[30])  # desktop
        modHeadlessList.append(item[32])  # headless
        mod_headless = []
        for tmp in modHeadlessList:
            if tmp is None:
                mod_headless.append([])
            else:
                mod_headless.append(tmp.split(split_type))
        sim['mod_headless_similarity'] = compareJaccardMultipleSets(
            mod_headless)

        # chrome
        browserList = []
        browserList.append(item[1])
        browserList.append(item[13])

        browser = []
        for tmp in browserList:
            if tmp is None:
                browser.append([])
            else:
                browser.append(tmp.split(split_type))
        sim['browser_desktop_ger'] = compareJaccardMultipleSets(browser)

        browserList = []

        browserList.append(item[2])
        browserList.append(item[14])

        browser = []
        for tmp in browserList:
            if tmp is None:
                browser.append([])
            else:
                browser.append(tmp.split(split_type))
        sim['browser_desktop_usa'] = compareJaccardMultipleSets(browser)
        browserList = []
        browserList.append(item[3])
        browserList.append(item[15])

        browser = []
        for tmp in browserList:
            if tmp is None:
                browser.append([])
            else:
                browser.append(tmp.split(split_type))
        sim['browser_desktop_jp'] = compareJaccardMultipleSets(browser)
        browserList = []
        browserList.append(item[4])
        browserList.append(item[16])

        browser = []
        for tmp in browserList:
            if tmp is None:
                browser.append([])
            else:
                browser.append(tmp.split(split_type))
        sim['browser_interaction_ger'] = compareJaccardMultipleSets(browser)
        browserList = []
        browserList.append(item[5])
        browserList.append(item[17])

        browser = []
        for tmp in browserList:
            if tmp is None:
                browser.append([])
            else:
                browser.append(tmp.split(split_type))
        sim['browser_interaction_usa'] = compareJaccardMultipleSets(browser)

        # finish
        browserList = []

        browserList.append(item[6])
        browserList.append(item[18])

        browser = []
        for tmp in browserList:
            if tmp is None:
                browser.append([])
            else:
                browser.append(tmp.split(split_type))
        sim['browser_interaction_jp'] = compareJaccardMultipleSets(browser)

        # finish
        browserList = []

        browserList.append(item[7])
        browserList.append(item[19])

        browser = []
        for tmp in browserList:
            if tmp is None:
                browser.append([])
            else:
                browser.append(tmp.split(split_type))
        sim['browser_headless_desktop_ger'] = compareJaccardMultipleSets(
            browser)

        # finish
        browserList = []

        browserList.append(item[8])
        browserList.append(item[20])

        browser = []
        for tmp in browserList:
            if tmp is None:
                browser.append([])
            else:
                browser.append(tmp.split(split_type))
        sim['browser_headless_desktop_usa'] = compareJaccardMultipleSets(
            browser)

        # finish
        browserList = []

        browserList.append(item[9])
        browserList.append(item[21])

        browser = []
        for tmp in browserList:
            if tmp is None:
                browser.append([])
            else:
                browser.append(tmp.split(split_type))
        sim['browser_headless_desktop_jp'] = compareJaccardMultipleSets(
            browser)

        # finish
        browserList = []

        browserList.append(item[10])
        browserList.append(item[22])

        browser = []
        for tmp in browserList:
            if tmp is None:
                browser.append([])
            else:
                browser.append(tmp.split(split_type))
        sim['browser_headless_interaction_ger'] = compareJaccardMultipleSets(
            browser)

        # finish
        browserList = []

        browserList.append(item[11])
        browserList.append(item[23])

        browser = []
        for tmp in browserList:
            if tmp is None:
                browser.append([])
            else:
                browser.append(tmp.split(split_type))
        sim['browser_headless_interaction_usa'] = compareJaccardMultipleSets(
            browser)

        # finish
        browserList = []

        browserList.append(item[12])
        browserList.append(item[24])

        browser = []
        for tmp in browserList:
            if tmp is None:
                browser.append([])
            else:
                browser.append(tmp.split(split_type))
        sim['browser_headless_interaction_jp'] = compareJaccardMultipleSets(
            browser)

        sim['browser_avg'] = round(average([sim['browser_desktop_ger'], sim['browser_desktop_usa'], sim['browser_desktop_jp'], sim['browser_interaction_ger'], sim['browser_interaction_usa'], sim['browser_interaction_jp'], sim['browser_headless_desktop_ger'], sim['browser_headless_desktop_usa'], sim['browser_headless_desktop_jp'], sim['browser_headless_interaction_ger'], sim['browser_headless_interaction_usa'], sim['browser_headless_interaction_jp']])

                # HEADLESS
        headlessList=[]
        headlessList.append(item[1])
        headlessList.append(item[7])
        headless=[]
        for tmp in browserList:
            if tmp is None:
                headless.append([])
            else:
                headless.append(tmp.split(split_type))
        sim['headlessC_desktop_ger']=compareJaccardMultipleSets(headless)



        headlessList=[]
        headlessList.append(item[2])
        headlessList.append(item[8])
        headless=[]
        for tmp in browserList:
            if tmp is None:
                headless.append([])
            else:
                headless.append(tmp.split(split_type))
        sim['headlessC_desktop_usa']=compareJaccardMultipleSets(headless)



        headlessList=[]
        headlessList.append(item[3])
        headlessList.append(item[9])
        headless=[]
        for tmp in browserList:
            if tmp is None:
                headless.append([])
            else:
                headless.append(tmp.split(split_type))
        sim['headlessC_desktop_jp']=compareJaccardMultipleSets(headless)



        headlessList=[]
        headlessList.append(item[4])
        headlessList.append(item[10])
        headless=[]
        for tmp in browserList:
            if tmp is None:
                headless.append([])
            else:
                headless.append(tmp.split(split_type))
        sim['headlessC_interaction_ger']=compareJaccardMultipleSets(headless)



        headlessList=[]
        headlessList.append(item[5])
        headlessList.append(item[11])
        headless=[]
        for tmp in browserList:
            if tmp is None:
                headless.append([])
            else:
                headless.append(tmp.split(split_type))
        sim['headlessC_interaction_usa']=compareJaccardMultipleSets(headless)



        headlessList=[]
        headlessList.append(item[6])
        headlessList.append(item[12])
        headless=[]
        for tmp in browserList:
            if tmp is None:
                headless.append([])
            else:
                headless.append(tmp.split(split_type))
        sim['headlessC_interaction_jp']=compareJaccardMultipleSets(headless)



        headlessList=[]
        headlessList.append(item[13])
        headlessList.append(item[19])
        headless=[]
        for tmp in browserList:
            if tmp is None:
                headless.append([])
            else:
                headless.append(tmp.split(split_type))
        sim['headlessF_desktop_ger']=compareJaccardMultipleSets(headless)



        headlessList=[]
        headlessList.append(item[14])
        headlessList.append(item[20])
        headless=[]
        for tmp in browserList:
            if tmp is None:
                headless.append([])
            else:
                headless.append(tmp.split(split_type))
        sim['headlessF_desktop_usa']=compareJaccardMultipleSets(headless)



        headlessList=[]
        headlessList.append(item[15])
        headlessList.append(item[21])
        headless=[]
        for tmp in browserList:
            if tmp is None:
                headless.append([])
            else:
                headless.append(tmp.split(split_type))
        sim['headlessF_desktop_jp']=compareJaccardMultipleSets(headless)



        headlessList=[]
        headlessList.append(item[16])
        headlessList.append(item[22])
        headless=[]
        for tmp in browserList:
            if tmp is None:
                headless.append([])
            else:
                headless.append(tmp.split(split_type))
        sim['headlessF_interaction_ger']=compareJaccardMultipleSets(headless)



        headlessList=[]
        headlessList.append(item[17])
        headlessList.append(item[23])
        headless=[]
        for tmp in browserList:
            if tmp is None:
                headless.append([])
            else:
                headless.append(tmp.split(split_type))
        sim['headlessF_interaction_usa']=compareJaccardMultipleSets(headless)



        headlessList=[]
        headlessList.append(item[18])
        headlessList.append(item[24])
        headless=[]
        for tmp in browserList:
            if tmp is None:
                headless.append([])
            else:
                headless.append(tmp.split(split_type))
        sim['headlessF_interaction_jp']=compareJaccardMultipleSets(headless)

        sim['headless_avg']=round(average([sim['headlessC_desktop_ger'], sim['headlessC_desktop_usa'], sim['headlessC_desktop_jp'], sim['headlessC_interaction_ger'], sim['headlessC_interaction_usa'], sim['headlessC_interaction_jp'],
                                  sim['headlessF_desktop_ger'], sim['headlessF_desktop_usa'], sim['headlessF_desktop_jp'], sim['headlessF_interaction_ger'], sim['headlessF_interaction_usa'], sim['headlessF_interaction_jp']]), 2)

                # interaction
        interactionList=[]
        interactionList.append(item[1])
        interactionList.append(item[4])
        interaction=[]
        for tmp in interactionList:
            if tmp is None:
                interaction.append([])
            else:
                interaction.append(tmp.split(split_type))
        sim['interactionC_desktop_ger']=compareJaccardMultipleSets(interaction)


        interactionList=[]
        interactionList.append(item[2])
        interactionList.append(item[5])
        interaction=[]
        for tmp in interactionList:
            if tmp is None:
                interaction.append([])
            else:
                interaction.append(tmp.split(split_type))
        sim['interactionC_deskop_usa']=compareJaccardMultipleSets(interaction)


        interactionList=[]
        interactionList.append(item[3])
        interactionList.append(item[6])
        interaction=[]
        for tmp in interactionList:
            if tmp is None:
                interaction.append([])
            else:
                interaction.append(tmp.split(split_type))
        sim['interactionC_deskop_jp']=compareJaccardMultipleSets(interaction)


        interactionList=[]
        interactionList.append(item[7])
        interactionList.append(item[10])
        interaction=[]
        for tmp in interactionList:
            if tmp is None:
                interaction.append([])
            else:
                interaction.append(tmp.split(split_type))
        sim['interactionC_headless_ger']=compareJaccardMultipleSets(
            interaction)


        interactionList=[]
        interactionList.append(item[8])
        interactionList.append(item[11])
        interaction=[]
        for tmp in interactionList:
            if tmp is None:
                interaction.append([])
            else:
                interaction.append(tmp.split(split_type))
        sim['interactionC_headless_usa']=compareJaccardMultipleSets(
            interaction)


        interactionList=[]
        interactionList.append(item[9])
        interactionList.append(item[12])
        interaction=[]
        for tmp in interactionList:
            if tmp is None:
                interaction.append([])
            else:
                interaction.append(tmp.split(split_type))
        sim['interactionC_headless_jp']=compareJaccardMultipleSets(interaction)



        interactionList=[]
        interactionList.append(item[13])
        interactionList.append(item[16])
        interaction=[]
        for tmp in interactionList:
            if tmp is None:
                interaction.append([])
            else:
                interaction.append(tmp.split(split_type))
        sim['interactionF_desktop_ger']=compareJaccardMultipleSets(interaction)


        interactionList=[]
        interactionList.append(item[14])
        interactionList.append(item[17])
        interaction=[]
        for tmp in interactionList:
            if tmp is None:
                interaction.append([])
            else:
                interaction.append(tmp.split(split_type))
        sim['interactionF_desktop_usa']=compareJaccardMultipleSets(interaction)


        interactionList=[]
        interactionList.append(item[15])
        interactionList.append(item[18])
        interaction=[]
        for tmp in interactionList:
            if tmp is None:
                interaction.append([])
            else:
                interaction.append(tmp.split(split_type))
        sim['interactionF_desktop_jp']=compareJaccardMultipleSets(interaction)


        interactionList=[]
        interactionList.append(item[19])
        interactionList.append(item[22])
        interaction=[]
        for tmp in interactionList:
            if tmp is None:
                interaction.append([])
            else:
                interaction.append(tmp.split(split_type))
        sim['interactionF_headless_ger']=compareJaccardMultipleSets(
            interaction)


        interactionList=[]
        interactionList.append(item[20])
        interactionList.append(item[23])
        interaction=[]
        for tmp in interactionList:
            if tmp is None:
                interaction.append([])
            else:
                interaction.append(tmp.split(split_type))
        sim['interactionF_headless_usa']=compareJaccardMultipleSets(
            interaction)

        interactionList=[]
        interactionList.append(item[21])
        interactionList.append(item[24])
        interaction=[]
        for tmp in interactionList:
            if tmp is None:
                interaction.append([])
            else:
                interaction.append(tmp.split(split_type))
        sim['interactionF_headless_jp']=compareJaccardMultipleSets(interaction)


        sim['interaction_avg']=round(average([sim['interactionC_desktop_ger'], sim['interactionC_deskop_usa'], sim['interactionC_deskop_jp'], sim['interactionC_headless_ger'], sim['interactionC_headless_usa'], sim['interactionC_headless_jp'],
                                     sim['interactionF_desktop_ger'], sim['interactionF_desktop_usa'], sim['interactionF_desktop_jp'], sim['interactionF_headless_ger'], sim['interactionF_headless_usa'], sim['interactionF_headless_jp']]), 2)

                # LOCATION

        locationList=[]
        locationList.append(item[1])
        locationList.append(item[2])
        locationList.append(item[3])
        location=[]
        for tmp in locationList:
            if tmp is None:
                location.append([])
            else:
                location.append(tmp.split(split_type))
        sim['location_chrome_desktop']=compareJaccardMultipleSets(location)


        locationList=[]
        locationList.append(item[4])
        locationList.append(item[5])
        locationList.append(item[6])
        location=[]
        for tmp in locationList:
            if tmp is None:
                location.append([])
            else:
                location.append(tmp.split(split_type))
        sim['location_chrome_interaction']=compareJaccardMultipleSets(location)


        locationList=[]
        locationList.append(item[7])
        locationList.append(item[8])
        locationList.append(item[9])
        location=[]
        for tmp in locationList:
            if tmp is None:
                location.append([])
            else:
                location.append(tmp.split(split_type))
        sim['location_chromeheadless']=compareJaccardMultipleSets(location)


        locationList=[]
        locationList.append(item[10])
        locationList.append(item[11])
        locationList.append(item[12])
        location=[]
        for tmp in locationList:
            if tmp is None:
                location.append([])
            else:
                location.append(tmp.split(split_type))
        sim['location_chromeheadless_interaction']=compareJaccardMultipleSets(
            location)


        locationList=[]
        locationList.append(item[13])
        locationList.append(item[14])
        locationList.append(item[15])
        location=[]
        for tmp in locationList:
            if tmp is None:
                location.append([])
            else:
                location.append(tmp.split(split_type))
        sim['location_firefox_desktop']=compareJaccardMultipleSets(location)


        locationList=[]
        locationList.append(item[16])
        locationList.append(item[17])
        locationList.append(item[18])
        location=[]
        for tmp in locationList:
            if tmp is None:
                location.append([])
            else:
                location.append(tmp.split(split_type))
        sim['location_firefox_interaction']=compareJaccardMultipleSets(
            location)


        locationList=[]
        locationList.append(item[19])
        locationList.append(item[20])
        locationList.append(item[21])
        location=[]
        for tmp in locationList:
            if tmp is None:
                location.append([])
            else:
                location.append(tmp.split(split_type))
        sim['location_firefoxheadless']=compareJaccardMultipleSets(location)


        locationList=[]
        locationList.append(item[22])
        locationList.append(item[23])
        locationList.append(item[24])
        location=[]
        for tmp in locationList:
            if tmp is None:
                location.append([])
            else:
                location.append(tmp.split(split_type))
        sim['location_firefoxheadless_interaction']=compareJaccardMultipleSets(
            location)

        sim['location_avg']=round(average([sim['location_chrome_desktop'], sim['location_chrome_interaction'], sim['location_chromeheadless'], sim['location_chromeheadless_interaction'],
                                  sim['location_firefox_desktop'], sim['location_firefox_interaction'], sim['location_firefoxheadless'], sim['location_firefoxheadless_interaction']]), 2)


        s.append(sim)
        if len(s) > chunk_size:
            pushRows(push_table, s)
            s=[]

    pushRows(push_table, s)


def compareJaccardMultipleSets(myList):

    master_list=[]
    for item in myList:
        for sub in item:
            master_list.append(sub)

    master_list=list(dict.fromkeys(master_list))

    jaccard_list=[]
    for subList in myList:
        new_jaccard=[]
        analyse_list=dict.fromkeys(subList, True)
        for item in master_list:
            try:
                analyse_list[item]
                new_jaccard.append(1)
            except Exception as e:
                new_jaccard.append(0)
        jaccard_list.append(new_jaccard)

    results=[]

    import itertools
    for a, b in itertools.combinations(jaccard_list, 2):
        results.append(jaccard_score(a, b))
    similarity=round(sum(results) / len(results), 3)
    return similarity


if __name__ == '__main__':
    start()
