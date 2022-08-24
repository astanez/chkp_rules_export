# Required: Python >= 3.6



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
from pathlib import Path
import os.path as path

from PySide2 import QtCore, QtGui, QtWidgets
from PySide2.QtWidgets import *

this_script_path = path.abspath(path.join(__file__, ".."))
mylibs_path=this_script_path+"/../../mylibs/"
sys.path.append(mylibs_path)

import my_logger_func
import HelperDatabase as hlprDb


# Global vars
DatabaseName = "data/fwPoliciesAnalyser.db"
g_vendor_name="CHKP"
g_policy_conv_db_table="policy_package_conversations"
g_service_groups_file="service-groups"


def getServiceObjects_old(_service_ranges_dict, _objects_dict):
  result_list=[]
  log.debug("getServiceObjects: _service_ranges_dict:")
  pprint.pprint(_service_ranges_dict)

  # Collect tcp/udp services
  if _service_ranges_dict["tcp"]:
    for tcp_serv in _service_ranges_dict["tcp"]:      
      result_list.append("tcp_"+tcp_serv["start"]+"-"+tcp_serv["end"])
  if _service_ranges_dict["udp"]:
    for tcp_serv in _service_ranges_dict["udp"]:
      result_list.append("udp_"+tcp_serv["start"]+"-"+tcp_serv["end"])    

  # Resolve and collect others services
  if _service_ranges_dict["others"]:
    for serv_uid in _service_ranges_dict["others"]:
      log.debug("serv_uid: "+str(serv_uid))
      if _objects_dict[serv_uid]["type"]=="service-tcp":
        type="tcp"
        result_list.append(type+"_"+_objects_dict[serv_uid]["port"])
      elif _objects_dict[serv_uid]["type"]=="service-udp":
        type="udp"
        result_list.append(type+"_"+_objects_dict[serv_uid]["port"])
      elif _objects_dict[serv_uid]["type"]=="service-icmp":
        type="icmp"
        result_list.append(type+"_"+str(_objects_dict[serv_uid]["icmp-type"]))
      elif _objects_dict[serv_uid]["type"]=="service-other":
        type="other"
        result_list.append(type+"_"+str(_objects_dict[serv_uid]["ip-protocol"]))
      # ToDo: consided all service types
      else: 
        type=_objects_dict[serv_uid]["type"]            

  if "tcp_0-65535" and "udp_0-65535" in result_list:    
      result_list.remove("tcp_0-65535")
      result_list.remove("udp_0-65535")
      result_list.append("any")

  print("services result_list")
  pprint.pprint(result_list)
  exit()           
  
  return result_list

def getServiceObjects(_service_ranges_dict, _objects_dict):
  result_list=[]
  log.debug("getServiceObjects: _service_ranges_dict:")
  pprint.pprint(_service_ranges_dict)

  # Collect tcp/udp services
  if "tcp" in _service_ranges_dict:
    for tcp_serv in _service_ranges_dict["tcp"]:     
      srv_d={}
      srv_d["service_obj_name"]=

      result_list.append("tcp_"+tcp_serv["start"]+"-"+tcp_serv["end"])
  if _service_ranges_dict["udp"]:
    for tcp_serv in _service_ranges_dict["udp"]:
      result_list.append("udp_"+tcp_serv["start"]+"-"+tcp_serv["end"])    

  exit()


  # Collect tcp/udp services
  if _service_ranges_dict["tcp"]:
    for tcp_serv in _service_ranges_dict["tcp"]:     

      result_list.append("tcp_"+tcp_serv["start"]+"-"+tcp_serv["end"])
  if _service_ranges_dict["udp"]:
    for tcp_serv in _service_ranges_dict["udp"]:
      result_list.append("udp_"+tcp_serv["start"]+"-"+tcp_serv["end"])    

  # Resolve and collect others services
  if _service_ranges_dict["others"]:
    for serv_uid in _service_ranges_dict["others"]:
      log.debug("serv_uid: "+str(serv_uid))
      if _objects_dict[serv_uid]["type"]=="service-tcp":
        type="tcp"
        result_list.append(type+"_"+_objects_dict[serv_uid]["port"])
      elif _objects_dict[serv_uid]["type"]=="service-udp":
        type="udp"
        result_list.append(type+"_"+_objects_dict[serv_uid]["port"])
      elif _objects_dict[serv_uid]["type"]=="service-icmp":
        type="icmp"
        result_list.append(type+"_"+str(_objects_dict[serv_uid]["icmp-type"]))
      elif _objects_dict[serv_uid]["type"]=="service-other":
        type="other"
        result_list.append(type+"_"+str(_objects_dict[serv_uid]["ip-protocol"]))
      # ToDo: consided all service types
      else: 
        type=_objects_dict[serv_uid]["type"]            

  if "tcp_0-65535" and "udp_0-65535" in result_list:    
      result_list.remove("tcp_0-65535")
      result_list.remove("udp_0-65535")
      result_list.append("any")

  print("services result_list")
  pprint.pprint(result_list)
  exit()           
  
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
    # conversation_tmpl_dict.pop("action", "none")
    # conversation_tmpl_dict.pop("name", "none")
    # conversation_tmpl_dict.pop("comments", "none")
    print("Get conversations list out of a rule")
    i=0
    for src_range in _rule["src_ranges"]:
        for dest_range in _rule["dest_ranges"]:
            for service_range in _rule["service_ranges"]:
                i=i+1
                #conversation_dict={}
                conversation_dict = copy.deepcopy(conversation_tmpl_dict)
                #conversation_dict["name"]=_rule["name"]    
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
                # conversation_dict["comments"]=_rule["comments"]    
                # conversation_dict["action"]=_rule["action"]    

    return conversation_dicts_list
    

def saveRuleBaseConversationsToDb(_rulebase_json, _serv_objs_d, _conf_d, _package_name, _dbCon, _QLabel_status):

    result=True    

    log.debug("saveRuleBaseConvToDb: 1. Put all objects (networks, hosts, ranges, services) in a dict")    
    objects_dict_tmp={}
    for obj in _rulebase_json["objects-dictionary"]:
        objects_dict_tmp[obj["uid"]]=obj    

    log.debug("saveRuleBaseConvToDb: 1.1 Add service objects from serv groups to the objects_dict")    
    # Merge two dicts
    objects_dict={**objects_dict_tmp,**_serv_objs_d}
    log.debug("objects_dict:")
    pprint.pprint(objects_dict)    
    #exit()

    log.debug("saveRuleBaseConvToDb: 3. Get rule base in to a dict")
    rulebase_prepared_for_db=[]
    #log.debug("_rulebase_json: ")
    #pprint.pprint(_rulebase_json)
    for rule in _rulebase_json["rulebase"]:  
        # Check for sections 
        if "rulebase" in rule:           
            section=rule["name"] 
            log.debug("This is a section")
            for rule in rule["rulebase"]:                 
                log.debug("rule:")
                pprint.pprint(rule)         
                pprint.pprint(rule["domain"])         
                rule_prepared=OrderedDict()
                rule_prepared["policy_name"]=_package_name
                rule_prepared["policy_import_date"]=datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]
                rule_prepared["policy_vendor"]=conf_d["vendor_name"]
                rule_prepared["policy_mgmt"]=conf_d["mgmt_name"]
                rule_prepared["policy_domain"]=rule["domain"]["name"]    
                rule_prepared["access_layer_name"]=_rulebase_json["name"] 
                #rule_prepared["policy_domain"]=rule["domain"]["name"]        
                rule_prepared["section"]=section
                rule_prepared["rid"]=rule["rule-number"] 
                rule_prepared["name"]=rule["name"]
                rule_prepared["src_ranges"]=rule["source-ranges"]["ipv4"]
                rule_prepared["dest_ranges"]=rule["destination-ranges"]["ipv4"]
                rule_prepared["service_ranges"]=getServiceObjects(rule["service-ranges"], objects_dict)
                rule_prepared["action"]=objects_dict[rule["action"]]["name"].lower()	
                rule_prepared["comments"]=rule["comments"]
                rule_prepared["track"]=objects_dict[rule["track"]["type"]]["name"]
                rulebase_prepared_for_db.append(rule_prepared)        
        
        else:            
            log.debug("rule:")
            pprint.pprint(rule)         
            pprint.pprint(rule["domain"])         
            rule_prepared=OrderedDict()
            rule_prepared["policy_name"]=_package_name
            rule_prepared["policy_import_date"]=datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]
            rule_prepared["policy_vendor"]=conf_d["vendor_name"]
            rule_prepared["policy_mgmt"]=conf_d["mgmt_name"]
            rule_prepared["policy_domain"]=rule["domain"]["name"]    
            rule_prepared["access_layer_name"]=_rulebase_json["name"] 
            #rule_prepared["policy_domain"]=rule["domain"]["name"]        
            rule_prepared["section"]=""
            rule_prepared["rid"]=rule["rule-number"] 
            rule_prepared["name"]=rule["name"]
            rule_prepared["src_ranges"]=rule["source-ranges"]["ipv4"]
            rule_prepared["dest_ranges"]=rule["destination-ranges"]["ipv4"]
            rule_prepared["service_ranges"]=getServiceObjects(rule["service-ranges"], objects_dict)
            rule_prepared["action"]=objects_dict[rule["action"]]["name"].lower()	
            rule_prepared["comments"]=rule["comments"]
            rule_prepared["track"]=objects_dict[rule["track"]["type"]]["name"]
            rulebase_prepared_for_db.append(rule_prepared)
        
    log.debug("\nrulebase_prepared_for_db: ")
    pprint.pprint(rulebase_prepared_for_db)   
    exit()


    log.debug("saveRuleBaseConvToDb: 4. Create conversations and save them into db one by one")
    
    for rule in rulebase_prepared_for_db:
        conversation_dicts_list=[]
        log.debug("saveRuleBaseConvToDb Process on rule")
        pprint.pprint(rule)        

        log.debug("saveRuleBaseConvToDb Create conversation dict here")
        conversation_dicts_list=getConversationDictsLists(rule)
        log.debug("saveRuleBaseConvToDb Conversation dict list:")   
        pprint.pprint(conversation_dicts_list)         
        #exit()
       
        log.debug("saveRuleBaseConvToDb Save conversations of one rule into database")        
        rslt=hlprDb.writeDictsListToDatabase_wrapper(_dbCon, g_policy_conv_db_table, conversation_dicts_list, _QLabel_status, hlprDb.mappingDictDb_conversations, False)
        if rslt!=True:
            log.error("Saving conversations of package {} into database FAILED".format(_package_name))
            result==False
            break

    return result            


def getServiceObjsFromGroups(_service_groups_file):
  serv_objs_d={}
  with open(_service_groups_file) as json_file:
    serv_objs = json.load(json_file)
    #pprint.pprint(serv_objs)
    for obj in serv_objs["objects"]:
      for obj_others in obj["ranges"]["others"]:
        serv_objs_d[obj_others["uid"]]=obj_others

  #pprint.pprint(serv_objs_d)

  return serv_objs_d


################# MODULE'S MAIN  ###################### 
#def ImportDataCHKP(_dbCon, _QLabel_status):
def import_data_into_db_main(_conf_d, _dbCon, _QLabel_status):   
    domains_list=[]
    global log
    log=my_logger_func.get_logger("chkp_get_data_from_mgmt") 

    res_d={}  

    log.info("--- Start CHKP plugin module: import_data_into_db")  
    log.info("Following will be imported into db:")  
    log.info("  - Policy packages")
    log.info("  - Access layers rulebases")  
    log.info("  - Service groups")
    log.info("  - Gateways")

    conf_d["vendor_name"]=g_vendor_name
    mgmt_name=_conf_d["mgmt_name"]
    import_data_folder=_conf_d["data_exported_folder"]+mgmt_name


    log.info("--- 1. Get domains list")
    for subdir, dirs, files in os.walk(import_data_folder):            
      if subdir==import_data_folder:
        domains_l=dirs
        break
    log.debug("domains_l: "+str(domains_l))      
 

    log.info("--- 2. Process per CHKP mgmt domain")
    for domain in domains_l:
      # Just for test
      domain="CMA2"
      log.info("Domain name: "+domain)
    
      log.info("--- --- 2.0 Get files list")
      for subdir, dirs, files_l in os.walk(import_data_folder+"/"+domain):            
        log.debug("Subdir: "+str(subdir))
        log.debug("Dirs: "+str(dirs))
        log.debug("files: "+str(files_l))
        
      log.info("--- --- 2.1 Import gateways")

      
      log.info("--- --- 2.2 Put serv groups into list of dicts")
      serv_objs_d=getServiceObjsFromGroups(subdir+"/"+g_service_groups_file+".json")

      
      log.info("--- --- 2.2.1 Delete rulebase conversations for this mgmt")  
      log.debug("Delete rulebase conversations for mgmt: {}, for vendor name: {}".format(_conf_d["mgmt_name"], _conf_d["vendor_name"]))        
      #cmd="delete from policy_package_conversations where policy_mgmt=\""+_conf_d["mgmt_name"]+"\" and policy_vendor=\""+_conf_d["vendor_name"]+"\";" 
      cmd="delete from "+g_policy_conv_db_table+" where policy_mgmt=\""+_conf_d["mgmt_name"]+"\" and policy_vendor=\""+_conf_d["vendor_name"]+"\";" 
      g_policy_conv_db_table
      log.debug("cmd: "+cmd)      
      if hlprDb.executeSqlCmd(_dbCon, cmd):
        log.debug("Rulebase conversations for this mgmt have been deteted.")
      else:
        log.error("Rulebase conversations for this mgmt could not been deteted.")

      #exit()             
      
      log.info("--- --- 2.3 Get packages")      
      file_name=import_data_folder+"/"+domain+"/packages.json"
      with open(file_name) as json_file:
        packages_d = json.load(json_file)
      #pprint.pprint(packages_j)     
      

      log.info("Per package")
      log.info("--- --- --- 2.3.1 Get access layer rulebase and save them into db")  
      for package in packages_d["packages"]:
        if package["name"]=="Standard":
          continue        
        log.info("Package name: "+package["name"])
        access_layers_l=[d["name"] for d in package["access-layers"]]
        log.info("Import package's access layers into database")        
        for layer in access_layers_l:          
          # FIXME For tests
          layer="HQ_Fra_Network"
          layer=layer.replace(" ","_")
          log.info("Package access layer: "+str(layer))          
          access_layer_file=subdir+"/access_layer__"+layer+".json"
          #importAccessLayerIntoDb(access_layer_file, layer)          
          with open(access_layer_file) as json_file:
            rulebase_json = json.load(json_file)
            rstl=saveRuleBaseConversationsToDb(rulebase_json, serv_objs_d, _conf_d, package["name"], _dbCon, _QLabel_status)
            if rstl==True:
                log.info("Conversations of package {}, layer {} saved into database".format(package["name"], layer))    
            else:
                log.error("Conversations of package {}, layer {} could NOT be saved into database".format(package["name"], layer))    

            #exit()


# We use them only for dev phase
# It must be deactivated in prod
if __name__ == "__main__":  
    
    conf_d={}
    conf_d["mgmt_name"]="mds_fra"
    conf_d["data_exported_folder"]="data/for_import/chkp/"

    dbCon=hlprDb.getDbCon()
    import_data_into_db_main(conf_d, dbCon, "")

