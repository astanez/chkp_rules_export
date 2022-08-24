import sys, os, csv
import sqlite3
import itertools
import ipaddress
import re
import pathlib
import glob
import json
from time import gmtime, strftime
from datetime import datetime
import pprint
import copy
from collections import OrderedDict

from PySide2 import QtCore, QtGui, QtWidgets
from PySide2.QtWidgets import *


DatabaseName = "data/fwPoliciesAnalyser.db"

validation_patterns_zones=[]  
validation_patterns_zones.append("^[a-zA-Z0-9]+$")  
validation_patterns_zones.append("^[0-9-/.,]+$")  
validation_patterns_zones.append("^[a-zA-Z0-9-_\s]+$")  

mappingQtableDb_zones={}
mappingQtableDb_zones["name"]="name"
mappingQtableDb_zones["networks list"]="networks"
mappingQtableDb_zones["description"]="description"

mappingQtableDb_secMatr={}
mappingQtableDb_secMatr["src_zone"]="src_zone"
mappingQtableDb_secMatr["dest_zone"]="dest_zone"
mappingQtableDb_secMatr["exceptions"]="exceptions"
mappingQtableDb_secMatr["action"]="action"
mappingQtableDb_secMatr["cell_indexes"]="cell_indexes"

mappingDictDb_conversations={}
mappingDictDb_conversations["policy_name"]="policy_name"
mappingDictDb_conversations["policy_import_date"]="policy_import_date"
mappingDictDb_conversations["policy_vendor"]="policy_vendor"
mappingDictDb_conversations["policy_mgmt"]="policy_mgmt"
mappingDictDb_conversations["policy_domain"]="policy_domain"
mappingDictDb_conversations["rid"]="rid"
mappingDictDb_conversations["rule_conv_id"]="rid"
mappingDictDb_conversations["name"]="name"
mappingDictDb_conversations["src_obj_name"]="src_obj_name" 
mappingDictDb_conversations["src_start"]="src_start"
mappingDictDb_conversations["src_end"]="src_end"
mappingDictDb_conversations["dest_obj_name"]="dest_obj_name" 
mappingDictDb_conversations["dest_start"]="dest_start"
mappingDictDb_conversations["dest_end"]="dest_end"    
mappingDictDb_conversations["service_obj_name"]="service_obj_name"
mappingDictDb_conversations["service_protocol"]="service_protocol"
mappingDictDb_conversations["service_number_start"]="service_number_start"
mappingDictDb_conversations["service_number_end"]="service_number_end"
mappingDictDb_conversations["action"]="action"
mappingDictDb_conversations["comments"]="comments"

validation_pattern_sec_matrix="^[a-zA-Z0-9-_:;,\n]+$"

bg_color_sec_matr_cell_block=QtGui.QColor(183,32,21)
bg_color_sec_matr_cell_allow=QtGui.QColor(38,127,32)


def executeSqlCmd(_dbConn, _sqlCmd):    
    result="ok"
    dbCursor = _dbConn.cursor()
    #sqlCmd="DELETE FROM "+_table  
    print("sqlCmd:" + _sqlCmd)
    try:
        dbCursor.execute(_sqlCmd)    
        rsltRowsList = dbCursor.fetchall()
        print("rsltRowsList: "+str(rsltRowsList))     
        for row in rsltRowsList:      
            print("slt: "+row)
        _dbConn.commit()    
    except Exception as e:
        result="ERROR. Database error: "+str(e)
        print(result)        
    return result


def fill_qtablewidget(_tableWidget, _vertical_headers_list, _horizontal_headers_list, _rows_from_db):
    # For Securiry matrix
    print("Fill qtablewidget")
    print("Set headers")
    _tableWidget.setRowCount(len(_vertical_headers_list))
    _tableWidget.setColumnCount(len(_horizontal_headers_list))   
    _tableWidget.setVerticalHeaderLabels(_vertical_headers_list)
    _tableWidget.setHorizontalHeaderLabels(_vertical_headers_list)

    print("Set content")
    for row in _rows_from_db:
        print("indexes: "+row["cell_indexes"])
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





    
    #_tableWidget.setHorizontalHeaderLabels() 
    # Set vertical headers
    # for counter, header in enumerate(_vertical_headers_list):
    #     qtablewidgetitem = QTableWidgetItem()        
    #     qtablewidgetitem.setText(zone.strip())                        
    #     _tableWidget.setHorizontalHeaderItem(counter, qtablewidgetitem)
    #     _tableWidget.setVerticalHeaderItem(counter, qtablewidgetitem2)                
    # Set horizontal headers

def getDbCon():
    ## Connect to Database
    try:
        # TODO: protect db with password            
        databaseConn = sqlite3.connect(DatabaseName)
        return databaseConn
    except Error as e:
        print("Error: Connection to database failed"+str(e))    
        exit()
    

def create_empty_secmatrix(_dbCon, _tableWidget, _cells_background_action):    
    zonesDictsList=getAllDataFromDbTable(_dbCon, "zones")            
    print("ZonesDictsList:")
    print(zonesDictsList)                  
    zones_list=[d['name'] for d in zonesDictsList if 'name' in d]
    zones_list.sort()
    print("zones_list: "+str(zones_list))
    ## Build table
    # Set headers
    _tableWidget.setColumnCount(len(zones_list))
    _tableWidget.setRowCount(len(zones_list))
    for counter, zone in enumerate(zones_list):
        qtablewidgetitem = QTableWidgetItem()
        qtablewidgetitem2 = QTableWidgetItem()                
        qtablewidgetitem.setText(zone.strip())                
        qtablewidgetitem2.setText(zone.strip())                                
        _tableWidget.setHorizontalHeaderItem(counter, qtablewidgetitem)
        _tableWidget.setVerticalHeaderItem(counter, qtablewidgetitem2)                
    # Set rows
    for counter_row in range(len(zones_list)):
        for counter_column in range(len(zones_list)):
            myTextEdit=QTextEdit()
            myTextEdit.setText("")
            qtablewidgetitem = QTableWidgetItem()
            if counter_row!=counter_column:
                _tableWidget.setItem(counter_row, counter_column, qtablewidgetitem) 
                #_tableWidget.item(counter_row, counter_column).setBackground(QtGui.QColor(183,32,21)) 
                _tableWidget.setCellWidget(counter_row, counter_column, myTextEdit) 
                _tableWidget.item(counter_row, counter_column).setBackground(_cells_background_action)
            else:
                #myTextEdit=QTextEdit()
                qtablewidgetitem.setFlags(QtCore.Qt.ItemIsEnabled)             
                _tableWidget.setItem(counter_row, counter_column, qtablewidgetitem)
                _tableWidget.item(counter_row, counter_column).setBackground(QtGui.QColor(39, 44, 54))  


def getAllDataFromDbTable(_dbCon, _table):
    # Get all data from a table as list of dicts
    resultDictList = []   
    _dbCon.row_factory = sqlite3.Row
    dbCursor = _dbCon.cursor()
    sqlCmd="SELECT * FROM "+_table  
    print("sqlCmd:" + sqlCmd)
    dbCursor.execute(sqlCmd)    
    rowsList = dbCursor.fetchall()
    print(rowsList)     
    for row in rowsList:      
      dictContainer = dict(zip(row.keys(), row))      
      resultDictList.append(dictContainer)    
    dbCursor.close()

    return resultDictList  

def truncate_db_table(_dbConn, _table):    
    result="ok"
    dbCursor = _dbConn.cursor()
    sqlCmd="DELETE FROM "+_table  
    print("sqlCmd:" + sqlCmd)
    try:
        dbCursor.execute(sqlCmd)    
        rsltRowsList = dbCursor.fetchall()
        print("rsltRowsList: "+str(rsltRowsList))     
        for row in rsltRowsList:      
            print("slt: "+row)
        _dbConn.commit()    
    except Exception as e:
        result="ERROR. Database error: "+str(e)
        print(result)        
    return result


def sec_matrix_qtable_to_dicts(_tableWidget, _bg_color_sec_matr_cell_block):
    print("Validate data from qTableWidget, Save data into a list of dicts")      
    data_valid=True
    table_data_dicts_list=[]      
    ## Get headers
    #print("Headers") 
    vertical_headers_list=[]
    for row_counter in range(_tableWidget.rowCount()):
        print(row_counter)
        
        vertical_headers_list.append(_tableWidget.verticalHeaderItem(row_counter).text())    
        row_name=_tableWidget.verticalHeaderItem(row_counter).text()    
        for column_counter in range(_tableWidget.columnCount()):            
            table_data_dict={}
            # Set cells background default color
            #if _tableWidget.item(row_counter, column_counter):
            #    _tableWidget.item(row_counter, column_counter).setBackground(QtGui.QColor(39, 44, 54)) 
                #print("cell color before check: "+str(_tableWidget_copy.item(row_counter, column_counter).background().color()))              
                #cell_background_color=_tableWidget_copy.item(row_counter, column_counter).background().color()
                #_tableWidget.item(row_counter, column_counter).setBackground(cell_background_color)                  
            #continue        

            if row_counter==column_counter:                           
                print("nothing to do here")
                continue

            column_name=_tableWidget.horizontalHeaderItem(column_counter).text()
            
            # Get and check cell value
            cell_value=""
            cell_action=""
            if _tableWidget.item(row_counter, column_counter):
                #cell_value=_tableWidget.item(row_counter, column_counter).text()  
                cell_value=_tableWidget.cellWidget(row_counter, column_counter).toPlainText()
                cell_color=_tableWidget.item(row_counter, column_counter).background().color()                
                if cell_color==_bg_color_sec_matr_cell_block:
                    print("cell color is red")
                    cell_action="block"                
                else: 
                    print("cell color is green")
                    cell_action="allow"                     
            
            print("Validate cell value")             
            if not cell_value or re.search(validation_pattern_sec_matrix, cell_value):                
                print("data valid: "+cell_value)             
                print(" cell action: "+str(cell_action))                
            else:
                print("!!! data INVALID: "+cell_value)            
                data_valid=False
                if _tableWidget.item(row_counter, column_counter):            
                    #_tableWidget.item(row_counter, column_counter).setBackground(QtGui.QColor(255,51,51)) 
                    _tableWidget.item(row_counter, column_counter).setSelected(True)                                       
            table_data_dict["src_zone"]=row_name
            table_data_dict["dest_zone"]=column_name
            table_data_dict["exceptions"]=cell_value
            table_data_dict["action"]=cell_action
            table_data_dict["cell_indexes"]=str(row_counter)+","+str(column_counter)
            # Check cell color

        
            table_data_dicts_list.append(table_data_dict)  

    if not data_valid:
        table_data_dicts_list.clear()
    #print("table_data_dicts_list: "+str(table_data_dicts_list))

    return table_data_dicts_list


def put_table_data_into_dists_list(_tableWidget, _validation_patterns_list):
    print("Validate data from qTableWidget, Save data into a list of dicts")      
    data_valid=True
    table_data_dicts_list=[]      
    ## Get headers
    #print("Headers") 
    for row_counter in range(_tableWidget.rowCount()):
        print(row_counter)
        table_data_dict={}
        for column_counter in range(_tableWidget.columnCount()): 
            if _tableWidget.item(row_counter, column_counter):
                _tableWidget.item(row_counter, column_counter).setBackground(QtGui.QColor(39, 44, 54))  
                
            #_tableWidget.item(row_counter, column_counter).background)    
            header=_tableWidget.horizontalHeaderItem(column_counter).text().lower()
            if _tableWidget.item(row_counter, column_counter):
                cell_value=_tableWidget.item(row_counter, column_counter).text()                   
            else:
                cell_value=""
            print("Validate cell value")                
            #if re.search(validation_patterns_zones[column_counter], cell_value):
            if re.search(_validation_patterns_list[column_counter], cell_value):
                print("data valid: "+cell_value)             
                _tableWidget.item(row_counter, column_counter).setSelected(False)  
            else:
                print("data INVALID: "+cell_value)            
                data_valid=False
                if _tableWidget.item(row_counter, column_counter):            
                    #_tableWidget.item(row_counter, column_counter).setBackground(QtGui.QColor(255,51,51))            
                    _tableWidget.item(row_counter, column_counter).setSelected(True)  
                #break 

            print("header "+header)
            print("data "+cell_value)            
            table_data_dict[header]=cell_value

        table_data_dicts_list.append(table_data_dict)    

    if not data_valid:
        table_data_dicts_list.clear()

    return table_data_dicts_list


# Write data into database if valid
def writeDictsListToDatabase_wrapper(_dbCon, _table, _dataDictsList, _statusLabel, _mappingQtable_to_Db, _flushTable="True"):
    save_to_db_rslt=""
    status_label_text=""
    if _dataDictsList:  
        print("Data valid")        
        #print("Write data into database")            
        #print("Data from qTableWidget: "+str(_dataDictsList))  
        #for column_counter in range(_tableWidget.columnCount()):        
        save_to_db_rslt=writeDictsListToDatabase(_dbCon, _table, _dataDictsList, _mappingQtable_to_Db, _flushTable)
        
        if save_to_db_rslt=="success":            
            status_label_text="Data stored into the database."
        else: 
            _statusLabel.setText("ERROR. "+save_to_db_rslt)            
            status_label_text="ERROR. "+save_to_db_rslt
    else: 
        print("Data INVALID")                                
        status_label_text="ERROR. Invalid table values. Please correct values in highligted cells.  Data haven't been stored into the database."

    if _statusLabel:
        _statusLabel.setText(status_label_text)        


def flushTable(_dbCon, _table):
    sql="delete from "+_table
    _dbCon.cursor().execute(sql)        
    _dbCon.commit()


# Write data from dict into database
def writeDictsListToDatabase(_dbCon, _table, _dataDictsList, _mappingQtable_to_Db, _flushTable):
    print("from helper database")        
    result="success"

    # Mapping QTableWidget columns to database table columns
    mappingQtableDb_zones={}
    mappingQtableDb_zones["name"]="name"
    mappingQtableDb_zones["networks list"]="networks"
    mappingQtableDb_zones["description"]="description"

    
   
    # For db table, get columns and placeholders
    # columns=', '.join(mappingQtableDb_zones.values())
    # placeholders=', '.join('?' * len(mappingQtableDb_zones))     
    columns=', '.join(_mappingQtable_to_Db.values())
    placeholders=', '.join('?' * len(_mappingQtable_to_Db))     

    if _flushTable:
        # Flush table
        sql="delete from "+_table
        _dbCon.cursor().execute(sql)        
        #_dbCon.commit()

    for data_dict in _dataDictsList:        
        # Compare mapping table with provided dataDict
        if data_dict.keys()!=_mappingQtable_to_Db.keys():
            print("Mapping table is different from provided.")
            exit()

        #sql='insert into zones ({}) values ({})'.format(columns, placeholders)
        sql='insert into '+_table+' ({}) values ({})'.format(columns, placeholders)
        print("--- sql "+sql)
        print("--- data_dict.values(): "+str(data_dict.values()))
        #sql="insert into zones (name, networks, description) values (?, ?, ?)"
        #_dbCon.cursor().execute(sql, list(data_dict.values()))   
        
        try:
            _dbCon.cursor().execute(sql, list(data_dict.values()))
        except Exception as err: 
            result=str(err)
            print("err: "+result)
    _dbCon.commit()
    
    return result


def getServiceObjects(_service_ranges_dict, _objects_dict):
    result_list=[]
    print("_service_ranges_dict:")
    pprint.pprint(_service_ranges_dict)

    # Collect tcp services
    if _service_ranges_dict["tcp"]:
        for tcp_serv in _service_ranges_dict["tcp"]:
            result_list.append("tcp_"+tcp_serv["start"]+"-"+tcp_serv["end"])
    if _service_ranges_dict["udp"]:
        for tcp_serv in _service_ranges_dict["udp"]:
            result_list.append("udp_"+tcp_serv["start"]+"-"+tcp_serv["end"])    

    # Resolve and collect others services
    if _service_ranges_dict["others"]:
        for serv in _service_ranges_dict["others"]:
            if _objects_dict[serv]["type"]=="service-tcp":
                type="tcp"
            elif _objects_dict[serv]["type"]=="service-udp":
                type="udp"
            else:    
                type=serv["type"]
            result_list.append(type+"_"+_objects_dict[serv]["port"])
    print("result_list")

    if "tcp_0-65535" and "udp_0-65535" in result_list:    
        result_list.remove("tcp_0-65535")
        result_list.remove("udp_0-65535")
        result_list.append("any")
    
    pprint.pprint(result_list)
   
    return result_list

def printErrorAndStop(_err_mgs=""):
    print("ERROR: "+str(_err_mgs))
    exit()    

def fillServiceFields(_service_range, _conversation_dict):
    # Process on service

    if _service_range=="any":
        _conversation_dict["service_protocol"]="any"
        _conversation_dict["service_number_start"]=""
        _conversation_dict["service_number_end"]=""
        return

    service_parts=_service_range.split("_")
    print(service_parts)
    if len(service_parts)!=2:
        printErrorAndStop()
        
    service_protocol=service_parts[0]
    service_number=service_parts[1]
    _conversation_dict["service_protocol"]=service_protocol

    # Check if we have a range
    if "-" in service_number:
        service_number_parts=service_number.split("-")      
        if len(service_number_parts)!=2:
            printErrorAndStop()
        _conversation_dict["service_number_start"]=service_number_parts[0]
        _conversation_dict["service_number_end"]=service_number_parts[1]
    else:
        _conversation_dict["service_number_start"]=service_number
        _conversation_dict["service_number_end"]=service_number


def getConversationDictsLists(_rule):
    #print("")
    conversation_dicts_list=[]
    conversation_tmpl_dict={}
    conversation_tmpl_dict = copy.deepcopy(_rule)
    conversation_tmpl_dict.pop("src_ranges", "none")
    conversation_tmpl_dict.pop("dest_ranges", "none")
    conversation_tmpl_dict.pop("service_ranges", "none")
    print("Get conversations list out of a rule")
    i=0
    for src_range in _rule["src_ranges"]:
        for dest_range in _rule["dest_ranges"]:
            for service_range in _rule["service_ranges"]:
                i=i+1
                #conversation_dict={}
                conversation_dict = copy.deepcopy(conversation_tmpl_dict)
                conversation_dict["rule_conv_id"]=i
                # TBD
                conversation_dict["src_obj_name"]=""
                conversation_dict["src_start"]=src_range["start"]
                conversation_dict["src_end"]=src_range["end"]
                conversation_dict["dest_obj_name"]=""
                conversation_dict["dest_start"]=dest_range["start"]
                conversation_dict["dest_end"]=dest_range["end"]
                conversation_dict["service_obj_name"]=service_range    

                fillServiceFields(service_range, conversation_dict) 

                conversation_dicts_list.append(conversation_dict)

    return conversation_dicts_list
    

def saveRuleBaseConversationsToDb(_rulebase_json, _dbCon, _QLabel_status):
    print("--- 1. Put all objects (networks, hosts, ranges, services) in a dict")
    objects_dict={}
    for obj in _rulebase_json["objects-dictionary"]:
        objects_dict[obj["uid"]]=obj
    pprint.pprint("objects_dict:")
    pprint.pprint(objects_dict)    

    
    print("--- 2. Delete conversations of that policy in the database") 
    # TBD


    print("--- 3. Get rule base into a dict")
    rulebase_prepared_for_db=[]
    for rule in _rulebase_json["rulebase"]:
        #pprint.pprint(" ####### rule: ")
        #pprint.pprint(rule) 
        rule_prepared=OrderedDict()
        rule_prepared["policy_name"]=_rulebase_json["name"]        
        rule_prepared["policy_import_date"]=datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]
        rule_prepared["policy_vendor"]="CHKP"
        rule_prepared["policy_mgmt"]="CHKP_MGMT_FRA"
        rule_prepared["policy_domain"]=rule["domain"]["name"]        
        rule_prepared["rid"]=rule["rule-number"] 
        rule_prepared["name"]=rule["name"]
        rule_prepared["src_ranges"]=rule["source-ranges"]["ipv4"]
        rule_prepared["dest_ranges"]=rule["destination-ranges"]["ipv4"]
        rule_prepared["service_ranges"]=getServiceObjects(rule["service-ranges"], objects_dict)
        rule_prepared["action"]=objects_dict[rule["action"]]["name"].lower()	
        rule_prepared["comments"]=rule["comments"]
        rulebase_prepared_for_db.append(rule_prepared)
        
    print("\nrulebase_prepared_for_db: ")
    pprint.pprint(rulebase_prepared_for_db)
    #print(datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3])


    print("\n--- 4. Create conversations and save them into db one by one")
    
    for rule in rulebase_prepared_for_db:
        print("--rule: ")
        pprint.pprint(rule)
        conversation_dicts_list=[]

        print("Create conversation dict here")
        conversation_dicts_list=getConversationDictsLists(rule)
        print("\nConversation dict list:")   
        pprint.pprint(conversation_dicts_list) 
        
        #exit()
       
        print("Save conversations of one rule into database")
        #saveConversationsIntoDB(conversation_dicts_list)   
        writeDictsListToDatabase_wrapper(_dbCon, "access_rules_conversations", conversation_dicts_list, _QLabel_status, mappingDictDb_conversations, False)
 



def ImportDataCHKP(_dbCon, _QLabel_status):
#def ImportDataCHKP():
    print("Import chkp data: firewalls, rulebases")

    import_data_folder="data/data_for_import/chkp/"

    print("--- 0. Get project path")   
    # FIXME: move it to a sort of global function        
    #script_path=pathlib.Path().absolute()
    script_path=os.path.dirname(os.path.realpath(__file__))
    project_path=str(script_path)+"/../"    
    print("project_path: "+project_path)
    import_files_folder_abs=project_path+import_data_folder
    print("import_files_folder: "+import_files_folder_abs)

    print("--- 1. Read import files location from configuration file")
    rulebase_files_list=glob.glob(import_files_folder_abs+"*_pol.json")
    rulebase_json=""
    for rulebase_file in rulebase_files_list:
        print("rulebase_file: "+rulebase_file)

        # Load to json
        with open(rulebase_file) as json_file:
            rulebase_json = json.load(json_file)

            #print("rulebase_json:")
            #pprint.pprint(rulebase_json)    
            print("rulebase_json name: "+str(rulebase_json["name"]))

            saveRuleBaseConversationsToDb(rulebase_json, _dbCon, _QLabel_status)

    exit()

    print("--- 2. Put all objects (networks, hosts, ranges, services) in a dict")
    objects_dict={}
    for obj in rulebase_json["objects-dictionary"]:
        objects_dict[obj["uid"]]=obj
    pprint.pprint("objects_dict:")
    pprint.pprint(objects_dict)    

   
    print("Delete conversations of that policy in the database") 
    # TBD


    print("--- 3. Get rule base in to a dict")
    rulebase_prepared_for_db=[]
    for rule in rulebase_json["rulebase"]:
        #pprint.pprint(" ####### rule: ")
        #pprint.pprint(rule) 
        rule_prepared=OrderedDict()
        rule_prepared["policy_name"]=rulebase_json["name"]        
        rule_prepared["policy_import_date"]=datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]
        rule_prepared["policy_vendor"]="CHKP"
        rule_prepared["policy_mgmt"]="CHKP_MGMT_FRA"
        rule_prepared["policy_domain"]=rule["domain"]["name"]        
        rule_prepared["rid"]=rule["rule-number"] 
        rule_prepared["name"]=rule["name"]
        rule_prepared["src_ranges"]=rule["source-ranges"]["ipv4"]
        rule_prepared["dest_ranges"]=rule["destination-ranges"]["ipv4"]
        rule_prepared["service_ranges"]=getServiceObjects(rule["service-ranges"], objects_dict)
        rule_prepared["action"]=objects_dict[rule["action"]]["name"].lower()	
        rule_prepared["comments"]=rule["comments"]
        rulebase_prepared_for_db.append(rule_prepared)
        
    print("\nrulebase_prepared_for_db: ")
    pprint.pprint(rulebase_prepared_for_db)
    #print(datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3])
    
    print("\n--- 4. Create conversations and save them into db one by one")

    
    for rule in rulebase_prepared_for_db:
        print("--rule: ")
        pprint.pprint(rule)
        conversation_dicts_list=[]

        print("Create conversation dict here")
        conversation_dicts_list=getConversationDictsLists(rule)
        print("\nConversation dict list:")   
        pprint.pprint(conversation_dicts_list) 
        
        #exit()
               

        print("Save conversations of one rule into database")
        #saveConversationsIntoDB(conversation_dicts_list)   
        writeDictsListToDatabase_wrapper(_dbCon, "access_rules_conversations", conversation_dicts_list, _QLabel_status, mappingDictDb_conversations, False)
 

        #exit()





        #exit()

    # Get list of following dicts        
    # CREATE TABLE "access_rules" (
	# "policy_name"	TEXT,	
	# "policy_import_date"	TEXT,
	# "policy_mgmt"	TEXT,
	# "policy_domain" TEXT,
	# "rid"	TEXT,
	# "name"  TEXT,
	# "src_ranges"	TEXT, 
	# "dest_ranges"	TEXT,
	# "service_ranges" TEXT,
	# "action"	TEXT, 	
	# "comment"	TEXT
    # );
    
    #exit()

    # Import gateways

    # Import rulebases


    #print()

if __name__ == "__main__":
    print("Start HelperDatabase")   
    print("We will use it to test helper functions.")

    dbCon=getDbCon()

    ImportDataCHKP(dbCon, "")

