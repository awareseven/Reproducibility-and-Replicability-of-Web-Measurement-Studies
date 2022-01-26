
from datetime import datetime
from setup import getConfig, getMode
from Ops import LocalStorage, editLogQueue, visitLogNew, visitLogUpdate
import logging
import os
import json
from selenium.webdriver import Firefox
from selenium.webdriver.common.by import By

from openwpm.commands.types import BaseCommand
from openwpm.config import BrowserParams, ManagerParams
from openwpm.socket_interface import ClientSocket
import time


class DoInteraction(BaseCommand):
    def __init__(self) -> None:
        self.logger = logging.getLogger("openwpm")

    # While this is not strictly necessary, we use the repr of a command for logging
    # So not having a proper repr will make your logs a lot less useful
    def __repr__(self) -> str:
        return "DoInteraction"

    # Have a look at openwpm.commands.types.BaseCommand.execute to see
    # an explanation of each parameter
    def execute(
        self,
        webdriver: Firefox,
        browser_params: BrowserParams,
        manager_params: ManagerParams,
        extension_socket: ClientSocket,
    ) -> None:
        from selenium.common.exceptions import TimeoutException
        from selenium.webdriver.common.keys import Keys
        from selenium.webdriver.support.ui import WebDriverWait

        
        element_id = 'body'  
        try:
            webdriver.find_element_by_css_selector(
            element_id).send_keys(Keys.PAGE_DOWN)
        except:
            element_id = 'html'
        try:
            # simulate human interactions
            webdriver.find_element_by_css_selector(
                element_id).send_keys(Keys.PAGE_DOWN)
            time.sleep(0.3)
            webdriver.find_element_by_css_selector(
                element_id).send_keys(Keys.PAGE_DOWN)
            time.sleep(0.7)
            webdriver.find_element_by_css_selector(
                element_id).send_keys(Keys.PAGE_DOWN)
            time.sleep(0.2)
            webdriver.find_element_by_css_selector(
                element_id).send_keys(Keys.TAB)
            time.sleep(0.3)
            webdriver.find_element_by_css_selector(
                element_id).send_keys(Keys.TAB)
            time.sleep(0.3)
            webdriver.find_element_by_css_selector(
                element_id).send_keys(Keys.TAB)
            time.sleep(0.5)
            webdriver.find_element_by_css_selector(
                element_id).send_keys(Keys.END)
            time.sleep(1.3)
        except:
            pass


class LoadMobileConfigs(BaseCommand):
    def __init__(self) -> None:
        self.logger = logging.getLogger("openwpm")

    def __repr__(self) -> str:
        return "LoadMobileConfigs"

    def execute(
        self,
        webdriver: Firefox,
        browser_params: BrowserParams,
        manager_params: ManagerParams,
        extension_socket: ClientSocket,
    ) -> None:
        webdriver.set_window_size(360, 760)


class LoadLocalStorage(BaseCommand):
    def __init__(self) -> None:
        self.logger = logging.getLogger("openwpm")

    def __repr__(self) -> str:
        return "LoadLocalStorage"

    def execute(
        self,
        webdriver: Firefox,
        browser_params: BrowserParams,
        manager_params: ManagerParams,
        extension_socket: ClientSocket,
    ) -> None:

        # webdriver.execute_script("return window.localStorage;")
        storage = LocalStorage(webdriver)

        filePath = str(manager_params.data_directory.absolute()
                       ) + "/localStorage.txt"

        with open(filePath, 'w') as f:
            print(storage, file=f)


class LogVisit(BaseCommand):
    def __init__(self, p_queue, p_site_id, p_site_url, p_subpage_id, p_ops) -> None:
        self.logger = logging.getLogger("openwpm")
        self.p_queue = p_queue
        self.p_site_id = p_site_id
        self.p_site_url = p_site_url
        self.p_subpage_id = p_subpage_id
        self.p_ops = p_ops

    def __repr__(self) -> str:
        return "LogVisit"

    def execute(
        self,
        webdriver: Firefox,
        browser_params: BrowserParams,
        manager_params: ManagerParams,
        extension_socket: ClientSocket,
    ) -> None:
        if self.p_ops == 0:
            str()#visitLogNew(self.p_site_id, self.p_site_url, self.p_subpage_id,)
        else:
            str()#visitLogUpdate(self.p_site_id, self.p_subpage_id, self.p_ops)
            # editLogQueue(self.p_queue,self.p_site_id,self.p_subpage_id,self.p_ops, datetime.now()) #p_queue, p_site_id, p_subpage_id, p_ops, p_value
            #print('self.p_subpage_id', self.p_subpage_id)


class ChangeRes(BaseCommand): 

    def __init__(self) -> None:
        self.logger = logging.getLogger("openwpm")
 
    def __repr__(self) -> str:
        return "ChangeRes"
 
    def execute(
        self,
        webdriver: Firefox,
        browser_params: BrowserParams,
        manager_params: ManagerParams,
        extension_socket: ClientSocket,
    ) -> None:   
    
        resolution= getConfig('resolution') 
        webdriver.set_window_size(resolution[0], resolution[1])