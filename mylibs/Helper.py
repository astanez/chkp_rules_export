import sys, os, csv
import sqlite3
import itertools
import ipaddress
from functools import partial
import pprint
import re
import json

import GUIPageClass
import HelperDatabase
import my_logger_func

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../')))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), 'classes/')))


import ui_styles
import Class_ZonesConversation

from PySide2 import QtCore, QtGui, QtWidgets
from PySide2.QtWidgets import *
from PySide2.QtWidgets import (
    QMainWindow,    
    QMessageBox,
    QTableWidgetItem, 
    QPushButton
)

global log
log=my_logger_func.get_logger("helper")

validation_pattern_sec_matrix="^[a-zA-Z0-9-_:;,\n\./\s]+$"
bg_color_sec_matr_cell_block=QtGui.QColor(183,32,21)
bg_color_sec_matr_cell_allow=QtGui.QColor(38,127,32)
reports_folder="fpa_reports"


def saveListOfDictsToCSV(policy_conv_violating_l, _report_file_name_csv):
    result=True
    if not policy_conv_violating_l:
        log.error("policy_conv_violating_l is empty")
        return False
    keys = policy_conv_violating_l[0].keys()
    try:
        with open(_report_file_name_csv, 'w', newline='')  as output_file:
            dict_writer = csv.DictWriter(output_file, keys, delimiter=';')
            dict_writer.writeheader()
            dict_writer.writerows(policy_conv_violating_l)
        log.debug("CSV report has been wrtitten into "+_report_file_name_csv)
    except Exception as e:
        log.error("Saving violating conversations into csv file failed: "+str(e))
        result=False
    return result    


def saveListOfDictsToJson(policy_conv_violating_l, report_file_name_json): 
    result=True
    report_d={}
    report_d["conversations"]=policy_conv_violating_l
    policy_conv_violating_l
    try: 
        with open(report_file_name_json, 'w') as f:
            json.dump(report_d, f, indent = 4, ensure_ascii=False)
    except Exception as e:
        log.error("Saving violating conversations into csv file failed: "+str(e))
        result=False
    return result


def ip_valid(_ip, _varName):
    result = True
    ip=""
    try:
        ip = ipaddress.ip_address(_ip)
    except:
        msg = QMessageBox()
        msg.setWindowTitle("IP validation")
        msg.setText(
            "Provided " + _varName + " is invalid. Please correct them and try again."
        )
        msg.setIcon(QMessageBox.Critical)
        x = msg.exec_()  # this will show our messagebox
        result = False

    return result

def validate_ip_list(_iplist_str, _separator):
    res=True
    log.debug("_iplist_str: "+_iplist_str)
    ip_l=_iplist_str.split(_separator)
    log.debug("ip_l: "+str(ip_l))

    if not ip_l:
        return False

    for ip in ip_l:
        if "/" in ip:
            # Network
            try:
                ip = ipaddress.ip_network(ip)
            except:
                log.debug("ip network not valid: "+ip)
                return False
        elif "-" in ip:
            # Range        
            ip_addr_l=ip.split("-")
            try:
                ip1 = ipaddress.ip_address(ip_addr_l[0])
                ip2 = ipaddress.ip_address(ip_addr_l[1])
            except:
                log.info("ip range not valid: "+ip)
                return False    
        else:
            # IP address
            try:
                ip = ipaddress.ip_address(ip)
            except:
                log.info("ip address not valid: "+ip)
                return False    
    return res
    

def validate_sec_matrix_data(_qtable_widget, _sec_matrix_d_l):
    res=True
    #pprint.pprint(_sec_matrix_rows_l)
   
    log.debug("Validate exceptions fields")
    for sec_matrix_d in _sec_matrix_d_l:
        if not sec_matrix_d["exceptions"]:
            log.debug("Sec. matrix exception value is valid") 
        elif not re.search(validation_pattern_sec_matrix, sec_matrix_d["exceptions"]):
            log.debug("Sec. matrix exception value is invalid") 
            res=False
            log.debug("Mark cell as selected")
            cell_ind_l=sec_matrix_d["cell_indexes"].split(",")
            if len(cell_ind_l)==2:
                if _qtable_widget.item(int(cell_ind_l[0]), int(cell_ind_l[1])):            
                    _qtable_widget.item(int(cell_ind_l[0]), int(cell_ind_l[1])).setSelected(True)     
                 
    if res==False:
        return res

    log.debug("Validate zones")

    return res


def validate_sec_matrix_zones(_dbConn, _qtable_widget, _sec_matrix_d_l):
    res=True
    
    log.debug("Get list of zones from db")
    zones_d_l=HelperDatabase.getAllDataFromDbTable(_dbConn, "zones")            
    zones_l=[d['name'] for d in zones_d_l if 'name' in d]
    zones_l.sort()
    log.debug("zones_list: "+str(zones_l))
    
    log.debug("Validate zones")
    for sec_matrix_d in _sec_matrix_d_l:
        if not sec_matrix_d["src_zone"] in zones_l or \
            not sec_matrix_d["dest_zone"] in zones_l:
            return False

    return res


def get_sec_matrix_conversations(_sec_matrix_dicts_list, _databaseConn):
    sec_matr_conv_l=[]
    res=sec_matr_conv_l

    log.debug("Get zones list")
    zones_d_l=HelperDatabase.getAllDataFromDbTable(_databaseConn, "zones")
    
    log.info("Get sec matrix conversations")
    for sec_matrix_row_d in _sec_matrix_dicts_list:
        log.debug("Create parent conversation")
        log.debug("Parent conversation: "+str(sec_matrix_row_d))
       
        buff=next((item["networks"] for item in zones_d_l if item["name"] == sec_matrix_row_d["src_zone"]), None)
        src_ip_l=buff.split(";")
        buff=next((item["networks"] for item in zones_d_l if item["name"] == sec_matrix_row_d["dest_zone"]), None)
        dest_ip_l=buff.split(";")
        
        log.debug("src_ip_l: "+str(src_ip_l))
        log.debug("dest_ip_l: "+str(dest_ip_l))

        for src_ip in src_ip_l:
            for dest_ip in dest_ip_l:
                log.debug("--- Create child conversation")
                sm_conv_o=Class_ZonesConversation.ZonesConversation()
                sec_matr_conv_l.append(sm_conv_o)
                sm_conv_o.src_zone=sec_matrix_row_d["src_zone"]
                sm_conv_o.dest_zone=sec_matrix_row_d["dest_zone"]
                sm_conv_o.action=sec_matrix_row_d["action"]
                sm_conv_o.src_ip=src_ip
                sm_conv_o.dest_ip=dest_ip
                log.debug("Child conversation: ")
                #print(sm_conv_o)
       
    log.debug("Translate ip_addresses into decimal ip_addresses")
    for conv_o in sec_matr_conv_l:
        if "-" in conv_o.src_ip:
            # Process on ip range
            ip_l=conv_o.src_ip.split("-")
            conv_o.src_ip_start_dec=int(ipaddress.IPv4Network(ip_l[0].strip()).network_address)
            conv_o.src_ip_end_dec=int(ipaddress.IPv4Network(ip_l[1].strip()).network_address)
        else:
            # Process on ip address or network
            ip=ipaddress.IPv4Network(conv_o.src_ip)
            conv_o.src_ip_start_dec=int(ip.network_address)
            conv_o.src_ip_end_dec=int(ip.broadcast_address)
        #
        if "-" in conv_o.dest_ip:
            # Process on ip range
            ip_l=conv_o.dest_ip.split("-")
            conv_o.dest_ip_start_dec=int(ipaddress.IPv4Network(ip_l[0].strip()).network_address)
            conv_o.dest_ip_end_dec=int(ipaddress.IPv4Network(ip_l[1].strip()).network_address)
        else:
            # Process on ip address or network
            ip=ipaddress.IPv4Network(conv_o.dest_ip)
            conv_o.dest_ip_start_dec=int(ip.network_address)
            conv_o.dest_ip_end_dec=int(ip.broadcast_address)

    log.debug("Convert objects to dicts")
    sec_matr_conv_d_l=[]
    for conv_o in sec_matr_conv_l:
        sec_matr_conv_d_l.append(vars(conv_o))

    return sec_matr_conv_d_l




def fill_qtablewidget(_main_window_o, _databaseConn, page_o):

    if page_o.page_opened_flag==False:
        print("Get data from database")
        db_data_d_l=HelperDatabase.getAllDataFromDbTable(_databaseConn, page_o.db_table)            
        print("db_data_d_l:")
        print(db_data_d_l)
        
        print("Put data from database into qTable")
        for row_id, row_d in enumerate(db_data_d_l): 
            #page_opened_flag=True
            page_o.page_opened_flag=True
            page_o.qtable_widget.insertRow(row_id)
            i=0
            for k, v in row_d.items():
                if k=="id":
                    continue
                print("k v {} {}".format(k, v))
                page_o.qtable_widget.setItem(row_id, i, QTableWidgetItem(v))
                i=i+1 
            
        print("Set buttons")    
        if len(page_o.qtable_widget_btns_l)>0:
            #print("Set buttons 2")    
            for row_id, row_d in enumerate(db_data_d_l):
                for btn_d in page_o.qtable_widget_btns_l:
                    print(btn_d)
                    btn=QPushButton(btn_d["text"])
                    #btn.clicked.connect(partial(_main_window_o.btn_reports_clicked, row_id))
                    btn.clicked.connect(partial(btn_d["btn_clicked_func"], row_id, page_o))
                    btn.setStyleSheet(ui_styles.Style.style_bt_qtable)
                    page_o.qtable_widget.setCellWidget(row_id, list(page_o.mapping_qtable_db_d).index(btn_d["dbtable_column"]), btn)
        
        print("Set on-clicked window for required columns")
        if page_o.qtable_columns_show_window_on_clicked_d:
            page_o.qtable_widget.cellDoubleClicked.connect(partial(_main_window_o.show_window_on_clicked, page_o))
           

def fill_qtablewidget_sec_matrix(_tableWidget, _vertical_headers_list, _horizontal_headers_list, _rows_from_db):
    # For Securiry matrix
    log.debug("Fill qtablewidget")
    log.debug("Set headers")
    _tableWidget.setRowCount(len(_vertical_headers_list))
    _tableWidget.setColumnCount(len(_horizontal_headers_list))   
    _tableWidget.setVerticalHeaderLabels(_vertical_headers_list)
    _tableWidget.setHorizontalHeaderLabels(_vertical_headers_list)

    log.debug("Set content")
    for row in _rows_from_db:
        log.debug("indexes: "+row["cell_indexes"])
        indexes=row["cell_indexes"].split(",")  
        row_id=int(indexes[0])
        col_id=int(indexes[1])

        if row["action"]=="allow":
            cells_background_action=bg_color_sec_matr_cell_allow
        elif row["action"]=="block":
            cells_background_action=bg_color_sec_matr_cell_block
        # FIXME
        else:
            cells_background_action=bg_color_sec_matr_cell_block

        myTextEdit=QTextEdit()
        myTextEdit.setText(row["exceptions"])
        #myTextEdit.toolTip("Allowed format: ")
        qtablewidgetitem = QTableWidgetItem()
        if row_id!=col_id:
            _tableWidget.setItem(row_id, col_id, qtablewidgetitem)             
            _tableWidget.setCellWidget(row_id, col_id, myTextEdit) 
            _tableWidget.item(row_id, col_id).setBackground(cells_background_action)
        else:            
            qtablewidgetitem.setFlags(QtCore.Qt.ItemIsEnabled)             
            _tableWidget.setItem(row_id, col_id, qtablewidgetitem)
            _tableWidget.item(row_id, col_id).setBackground(QtGui.QColor(39, 44, 54))  


