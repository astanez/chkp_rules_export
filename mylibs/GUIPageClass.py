import sys, os
import pprint

class GUIPage():
  def __init__(self):
    self.name=""
    self.page_opened_flag=""
    self.qtable_widget=""
    self.db_table=""
  
    self.qtable_widget_btns_l=[]
    self.qtable_widget_dropDownLists_l=[]

    # Qtable_widget columns to open a window with select list on click
    self.qtable_columns_show_window_on_clicked_d={}

    self.data_validation_patterns_d={}
    self.columns_where_zones_to_be_validated_l=[]

    self.mapping_qtable_db_d={}

    # Columns containing ip addressess. We will validate them.
    self.ip_address_columns_l=[]
      
  def toStr(self):
    # d={}
    # for k, v in self.__dict__:
    #     d[k] = v
    pprint.pprint(self.__dict__)

    
    