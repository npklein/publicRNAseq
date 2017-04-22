import logging
import sys

format = '%(asctime)s - %(levelname)s - %(funcName)s - %(message)s'
logging.basicConfig(stream=sys.stdout, level=logging.INFO,
                    format=format)
class Utils:
    '''Class with utility functions shared by multiple classes'''
    @staticmethod
    def get_all_indices(list_to_index):
        '''Get the indexes of all the items in a list and put them in a dict with key: element, value: index
        
           list_to_index(list)    List to get index from all elements from
        '''
        list_indexes = {}
        i = 0
        for element in list_to_index:
            list_indexes[element] = i
            i += 1
        return list_indexes
    
    @staticmethod
    @contextmanager
    def cd(newdir):
        prevdir = os.getcwd()
        os.chdir(os.path.expanduser(newdir))
        try:
            yield
        finally:
            os.chdir(prevdir)