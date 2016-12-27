import logging
import sys
logging.basicConfig(stream=sys.stdout, level=logging.INFO)
from selenium import webdriver
import time

class Download_ENA_samplesheet:
    def __init__(self,tax_id='9606', library_strategy='RNA-seq'):
        '''Initiate download_ENA_samplesheet class by setting tax_id and library_strategy

        tax_id(str)    Organism to download samplesheet for (def: 9606 <homo sapiens>)
        library_strategy(str)    type of data to download (def: RNA-seq)
        '''
        self.tax_id = tax_id
        self.library_strategy = library_strategy
    
    def __page_loaded(self, text, sleep = 1):
        '''Check if the javascript page has loaded by giving a text to search that is only in the html source when finished loading
           It uses the current page the driver is on
        
           text(str)    Text source needs to contain before continuing
           sleep(int)   Seconds to wait before trying source again (def: 1)
        '''
        html_source = self.driver.page_source
        x = 0
        while not text in html_source:
            html_source = self.driver.page_source
            time.sleep(sleep)
            x+=1
            if x==360:
                raise RuntimeError('Waited for page to load correctly '+str(360*sleep)+' seconds, did not find the text '+str(text))
        return html_source
        
    def download_samplesheet(self, output_directory, tax_id='9606',library_strategy='RNA-Seq'):
        '''Download samplesheet from ENA
        output_file(str)    output file name for samplesheet    
        '''
        # To prevent download dialog
        profile = webdriver.FirefoxProfile()
        profile.set_preference("browser.download.panel.shown", False)
        profile.set_preference("browser.helperApps.neverAsk.saveToDisk", "text/plain")
        profile.set_preference("browser.download.folderList", 2);
    
        self.driver = webdriver.Firefox(profile)
        logging.info('Downloading samplesheet for tax_id: '+self.tax_id+' and library strategy: '+self.library_strategy)
        url = 'http://www.ebi.ac.uk/ena/data/warehouse/search?query=%22tax_eq%289606%29%20AND%20library_strategy=%22RNA-Seq%22%22&domain=read'
        logging.info('Using url: '+url)
        try:
            self.driver.get(url)
            # can take a bit of time for the javascript to load, wait until it's fully loaded
            html_source = self.__page_loaded('Run')
            # there are 2 domainTextMouseOut, one for Run and one for Experiment. We need the Run one
            element = self.driver.find_element_by_xpath('//div[@class="domainTextMouseOut" and contains(text(), "Run")]')
            element.click()
            html_source = self.__page_loaded('>Reports</div>')
            element = self.driver.find_element_by_xpath('//div[@class="gwt-TabLayoutPanelTab GHVLHNUCH"]')
            element.click()
            html_source = self.__page_loaded('>TEXT<')
            element = self.driver.find_element_by_xpath('//*[@title="Download files and save to disk" and contains(text(), "TEXT")]')
            element.click()
            time.sleep(100)
            self.quit()
        except:
            self.quit()
            raise
        
    def set_tax_id(self,taxid):
        self.tax_id = tax_id

    def set_library_strategy(self,library_strategy):
        self.library_strategy = library_strategy
        
    def quit(self):
        self.driver.quit()