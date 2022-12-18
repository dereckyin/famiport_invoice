import os
import cx_Oracle
import multiprocessing
from multiprocessing import Process
from abc import ABC, abstractmethod

class Category(ABC):    
    
    def __init__(self, **kwargs):
        self.cat_id = self.get_value(kwargs, 'CAT_ID', None)
        self.prod_cat_id = self.get_value(kwargs, 'PROD_CAT_ID', None)
        self.cat_nm = self.get_value(kwargs, 'CAT_NM', None)
        self.yahoo_cat_id = self.get_value(kwargs, 'YAHOO_CAT_ID', None)
        self.yahoo_cat_nm = self.get_value(kwargs, 'YAHOO_CAT_NM', None)
        self.status_flg = self.get_value(kwargs, 'STATUS_FLG', None)
      
