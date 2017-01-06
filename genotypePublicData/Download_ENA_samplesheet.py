import logging
import sys
format = '%(asctime)s - %(levelname)s - %(funcName)s - %(message)s'
logging.basicConfig(stream=sys.stdout, level=logging.INFO,
                    format=format)
from pyvirtualdisplay import Display
from selenium import webdriver
import time
import os
import shutil

class Download_ENA_samplesheet:
    def __init__(self,tax_id='9606', library_strategy='RNA-seq'):
        '''Initiate download_ENA_samplesheet class by setting tax_id and library_strategy

        tax_id(str)    Organism to download samplesheet for (def: 9606 <homo sapiens>)
        library_strategy(str)    type of data to download (def: RNA-seq)
        '''
        self.tax_id = tax_id
        self.library_strategy = library_strategy
        self.samplesheet_file = None
        
    def __page_loaded(self, *arg, sleep = 1):
        '''Check if the javascript page has loaded by giving a text to search that is only in the html source when finished loading
           It uses the current page the driver is on
        
           arg*(string) Variable number of text html_source needs to contain before continuing
           sleep(int)   Seconds to wait before trying source again (def: 1)
        '''
        if len(arg) == 0:
            RuntimeError('Need at least one argument')
        html_source = self.driver.page_source
        x = 0
        def __check_if_text_in_html_source(arg, html_source):
            all_text_in_source = True
            for text in arg:
                if text not in html_source:
                    all_text_in_source = False
            return all_text_in_source
        while not __check_if_text_in_html_source(arg, html_source):
            html_source = self.driver.page_source
            time.sleep(sleep)
            x+=1
            if x==360:
                raise RuntimeError('Waited for page to load correctly '+str(360*sleep)+' seconds, did not find the text '+str(text))
        return html_source
    
    def __fully_downloaded(self, element, file_path, sleep=5):
        '''Check if a file has fully downloaded by checking between intervals if file size has changed
        
           element(WebElement)    Element that needs to be clicked to start the download
           file_path(str)   path of file to check if it's finished downloading
           sleep(int)    interval time for checking if file size changed
        '''
        # remove file if it already exists or it becomes impossible to check if it's finished downloading
        if os.path.exists(file_path):
            os.remove(file_path)
        if os.path.exists(file_path+'.part'):
            os.remove(file_path+'.part')
        element.click()
        time.sleep(2)
        logging.info('Checking if a .part file is used: '+file_path+'.part')
        # some filesystems first download a .part file, check if this happens
        if os.path.exists(file_path+'.part'):
            logging.info('Check if '+str(file_path)+'.part finished downloading')
            time.sleep(sleep)
            x = 0
            while os.path.exists(file_path+'.part'):
                logging.info('Still downloading, sleep '+str(sleep)+' seconds...')
                time.sleep(sleep)
                x += 1
                if x == 100:
                    raise RuntimeError('Part file did not get removed after '+str(sleep*x)+' seconds, clean up download folder and try again')
            logging.info(file_path+'.part does not exist anymore, download should be finished')
            assert os.path.exists(file_path)
        else:
            # if .part is not used, we need to wait to see if the file sizes are the same between intervals
            old_size = os.stat(file_path).st_size
            time.sleep(sleep)
            new_size = os.stat(file_path).st_size
            while new_size > old_size:
                old_size = new_size
                logging.info('Still downloading, sleep '+str(sleep)+' seconds...')
                time.sleep(sleep)
                new_size = os.stat(file_path).st_size
            logging.info('File size did not change the last '+str(sleep)+' seconds, file should be done downloading')
            assert new_size == old_size
            if new_size < old_size:
                logging.error('During downloading the size of downloaded file became smaller than before. Clean up download folder and try again')
                raise RuntimeError('New size of downloaded file should never be larger than old size')
        return True
         
    def __prevent_download_dialog(self, output_directory):
        '''Set Firefox profile such that it automatically downloads txt files to output_directory
        
           output_directory(str)    Directory to download files to
        '''
        profile = webdriver.FirefoxProfile()
        profile.set_preference("browser.download.panel.shown", False)
        profile.set_preference("browser.helperApps.neverAsk.saveToDisk", "text/plain")
        profile.set_preference("browser.download.folderList", 2);
        profile.set_preference("browser.download.dir", output_directory)
        return profile
           
    def __select_all_checkboxes(self):
        '''Select all checkboxes on a page'''
        checkboxes = self.driver.find_elements_by_css_selector('.gwt-CheckBox > input')
        for checkbox in checkboxes:
            if not checkbox.is_selected():
                checkbox.click()
    
    def download_samplesheet(self, output_directory, tax_id='9606',library_strategy='RNA-Seq'):
        '''Download samplesheet from ENA
        output_file(str)    output file name for samplesheet    
        '''
        # To prevent download dialog

        display = Display(visible=0, size=(1024, 768))
        display.start()
        
        self.driver = webdriver.Firefox(self.__prevent_download_dialog(output_directory))
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
            html_source = self.__page_loaded('>TEXT<', '>Select columns<')
            element = self.driver.find_element_by_xpath('//div[@class="html-face" and contains(text(), "Select columns")]')
            element.click()
            html_source = self.__page_loaded('>TEXT<', '>Hide Select columns<')
            self.__select_all_checkboxes()
            
            element = self.driver.find_element_by_xpath('//*[@title="Download files and save to disk" and contains(text(), "TEXT")]')
            logging.info('Downloading to '+output_directory+'/ena.txt')
            if self.__fully_downloaded(element, output_directory+'/ena.txt'):
                current_datetime = time.strftime("d%dm%my%Y_h%Hm%Ms%S")
                logging.info('Renaming '+output_directory+'/ena.txt to '+output_directory+'/ena_'+current_datetime+'.txt')
                shutil.move(output_directory+'/ena.txt', output_directory+'/ena_'+current_datetime+'.txt')
                self.samplesheet_file = output_directory+'/ena_'+current_datetime+'.txt'
            else:
                logging.error('Downloading samplesheet did not succeed. Clean up download folder and try again.')
                raise RuntimeError('__fully_downloaded() did not return True')
            self.quit_browser()
            display.stop()
        except:
            self.quit_browser()
            logging.error('Downloading samplesheet did not succeed. Clean up download folder and try again.')
            display.stop()
            raise
        
    def set_tax_id(self,taxid):
        self.tax_id = tax_id

    def set_library_strategy(self,library_strategy):
        self.library_strategy = library_strategy
    
    def get_samplesheet_file(self):
        if self.samplesheet_file:
            return self.samplesheet_file
        else:
            logging.error('Can not get samplesheet location without downloading samplesheet first.')
            raise RuntimeError('Need to run download_samplesheet first')
        
    def quit_browser(self):
        self.driver.quit()
