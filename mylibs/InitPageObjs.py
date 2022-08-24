import sys, os, csv
import itertools

import GUIPageClass

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../')))

import ui_styles


def initPageObjs(_mainWindow=""):
    pages_d={}

    ### Initialize page objects here    

    ########### Zones ##############
    page_obj=GUIPageClass.GUIPage()
    pages_d["zones"]=page_obj
    page_obj.name="zones"
    if _mainWindow:
        page_obj.qtable_widget=_mainWindow.ui.tableWidget_zones
    page_obj.db_table="zones"
    page_obj.page_opened_flag=False
    page_obj.qtable_widget_btns_l=[]

    mappingQtableDb_zones={}
    page_obj.mapping_qtable_db_d=mappingQtableDb_zones 
    mappingQtableDb_zones["name"]="name"
    mappingQtableDb_zones["networks_list"]="networks" 
    mappingQtableDb_zones["description"]="description"

    validation_patterns_d={}
    page_obj.data_validation_patterns_d=validation_patterns_d
    validation_patterns_d["name"]="^[a-zA-Z0-9]+$"  
    #validation_patterns_d["networks_list"]="^[0-9-/.,]+$" 
    validation_patterns_d["networks_list"]="^.*$" 
    validation_patterns_d["description"]="^[a-zA-Z0-9-_\s]+$"  

    page_obj.ip_address_columns_l=["networks_list"]


    ########### Policy packages ##############
    page_obj=GUIPageClass.GUIPage()
    pages_d["policy_packages"]=page_obj
    page_obj.name="policy_packages"
    if _mainWindow:
        page_obj.qtable_widget=_mainWindow.ui.tableWidget_fw_policies
    page_obj.db_table="policy_packages_zones"
    page_obj.page_opened_flag=False
    page_obj.qtable_widget_btns_l=[]

    page_obj.qtable_columns_show_window_on_clicked_d["zones"]=[5]

    mappingQtableDb_policy_packages={}
    page_obj.mapping_qtable_db_d=mappingQtableDb_policy_packages 
    # mappingQtableDb_policy_packages["policy_management"]="policy_mgmt"
    # mappingQtableDb_policy_packages["policy_vendor"]="policy_mgmt_vendor"
    # mappingQtableDb_policy_packages["policy_domain"]="policy_domain"
    # mappingQtableDb_policy_packages["policy_name"]="policy_name"
    # mappingQtableDb_policy_packages["policy_comments"]="policy_comments"
    # mappingQtableDb_policy_packages["zones"]="zones"
    #
    mappingQtableDb_policy_packages["policy_management"]="policy_mgmt"
    mappingQtableDb_policy_packages["policy_vendor"]="policy_mgmt_vendor"
    mappingQtableDb_policy_packages["policy_domain"]="policy_domain"
    mappingQtableDb_policy_packages["policy_name"]="policy_name"
    mappingQtableDb_policy_packages["policy_comments"]="policy_comments"
    mappingQtableDb_policy_packages["zones"]="zones"
    
    validation_patterns_d={}
    page_obj.data_validation_patterns_d=validation_patterns_d
    # Key must have the same names as column names in qtable (space replaced with _)
    validation_patterns_d["policy_management"]="^.*$"
    validation_patterns_d["policy_vendor"]="^.*$"
    validation_patterns_d["policy_domain"]="^.*$"
    validation_patterns_d["policy_name"]="^.*$"
    validation_patterns_d["policy_comments"]="^.*$"
    validation_patterns_d["zones"]="^.*$"
    
    page_obj.columns_where_zones_to_be_validated_l=["zones"]
    
    ########### Reports ##############
    page_obj=GUIPageClass.GUIPage()
    pages_d["reports"]=page_obj
    page_obj.name="reports"
    if _mainWindow:
        page_obj.qtable_widget=_mainWindow.ui.tableWidget_reports
    page_obj.db_table="reports"
    page_obj.page_opened_flag=False
    page_obj.qtable_widget_btns_l=[]
    
    page_obj.qtable_columns_show_window_on_clicked_d["zones"]=[1,2]

    validation_patterns_d={}
    page_obj.data_validation_patterns_d=validation_patterns_d
    validation_patterns_d["name"]="^[\w\d_\s]+$"
    validation_patterns_d["source_zones"]="^[\w\d_,\s]+$"
    validation_patterns_d["destination_zones"]="^[\w\d_,\s]+$"
    validation_patterns_d["create_report"]="^.*$"
    validation_patterns_d["regular_report"]="^[\w\d_]+$"

    mappingQtableDb_reports={}
    page_obj.mapping_qtable_db_d=mappingQtableDb_reports 
    mappingQtableDb_reports["name"]="name"
    mappingQtableDb_reports["source_zones"]="source_zones"
    mappingQtableDb_reports["destination_zones"]="destination_zones"
    mappingQtableDb_reports["create_report"]="create_report"
    mappingQtableDb_reports["regular_report"]="regular_report_time"

    page_obj.columns_where_zones_to_be_validated_l=["source_zones", "destination_zones"]

    btn_d={}
    btn_d["dbtable_column"]="create_report"
    btn_d["text"]="Create now"
    if _mainWindow:
        btn_d["btn_clicked_func"]=_mainWindow.btn_reports_clicked
    page_obj.qtable_widget_btns_l.append(btn_d)

    
    ########### Import ##############
    page_obj=GUIPageClass.GUIPage()
    pages_d["import"]=page_obj
    page_obj.name="import"
    if _mainWindow:
        page_obj.qtable_widget=_mainWindow.ui.tableWidget_import
    page_obj.db_table="fw_mgmt_servers"
    page_obj.page_opened_flag=False
    page_obj.qtable_widget_btns_l=[]

    btn_d={}
    btn_d["dbtable_column"]="import"
    btn_d["text"]="Import now"
    if _mainWindow:
        btn_d["btn_clicked_func"]=_mainWindow.btn_import_clicked
    pages_d["import"].qtable_widget_btns_l.append(btn_d)

    mappingQtableDb_fw_mgmt_servers={}
    page_obj.mapping_qtable_db_d=mappingQtableDb_fw_mgmt_servers 
    mappingQtableDb_fw_mgmt_servers["management_name"]="name"
    mappingQtableDb_fw_mgmt_servers["vendor"]="vendor"
    mappingQtableDb_fw_mgmt_servers["ip"]="ip"
    mappingQtableDb_fw_mgmt_servers["user_name"]="username"
    mappingQtableDb_fw_mgmt_servers["password"]="pwd"
    mappingQtableDb_fw_mgmt_servers["import"]="import_btn"
    mappingQtableDb_fw_mgmt_servers["regular_import"]="regular_import_time"

    validation_patterns_d={}
    page_obj.data_validation_patterns_d=validation_patterns_d
    validation_patterns_d["management_name"]="^[\w\d_]+$"
    validation_patterns_d["vendor"]="^[\w\d_]+$"
    validation_patterns_d["ip"]="^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$"
    validation_patterns_d["user_name"]="^[\w\d_]+$"
    validation_patterns_d["password"]="^[\w\d_]+$"
    validation_patterns_d["import"]="^.*$"
    validation_patterns_d["regular_import"]="^[\w\d_]+$"

    return pages_d



        