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
import yaml

from PySide2 import QtCore, QtGui, QtWidgets
from PySide2.QtWidgets import *

this_script_path = path.abspath(path.join(__file__, ".."))
mylibs_path=this_script_path+"/../../mylibs/"
sys.path.append(mylibs_path)

import my_logger_func
import HelperDatabase as hlprDb
import InitPageObjs


from PySide2.QtWidgets import QLabel


#FIXME: Put these data into config file
# Global vars
# DatabaseName = "data/fwPoliciesAnalyser.db"
# g_vendor_name="CHKP"
# g_policy_conv_db_table="policy_package_conversations"
# g_service_groups_file="service-groups"


## Depricated
def getServiceObjects(_service_ranges_dict, _objects_dict):
  result_list=[]
  log.debug("getServiceObjects: _service_ranges_dict:")
  #pprint.pprint(_service_ranges_dict)

  # Collect tcp/udp services
  #if "tcp" in _service_ranges_dict:
    # for tcp_serv in _service_ranges_dict["tcp"]:     
    #   srv_d={}
    #   srv_d["service_obj_name"]=
    #   srv_d["service_obj_name"]=

  #    result_list.append("tcp_"+tcp_serv["start"]+"-"+tcp_serv["end"])
  if _service_ranges_dict["udp"]:
    for tcp_serv in _service_ranges_dict["udp"]:
      result_list.append("udp_"+tcp_serv["start"]+"-"+tcp_serv["end"])    


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
  #pprint.pprint(result_list)
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
    #print(service_parts)
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


def getConversationDictsLists_old(_rule):
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
    log.info("Get conversations list out of a rule")
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
                conversation_dict["src_start_dec"]=src_range["start_dec"]
                conversation_dict["src_end_dec"]=src_range["end_dec"]
                conversation_dict["dest_obj_name"]=""
                conversation_dict["dest_start"]=dest_range["start"]
                conversation_dict["dest_end"]=dest_range["end"]
              
                conversation_dict["service_obj_name"]=service_range    
                
                fillServiceFields(service_range, conversation_dict) 

                conversation_dicts_list.append(conversation_dict)                
                # conversation_dict["comments"]=_rule["comments"]    
                # conversation_dict["action"]=_rule["action"]    

    return conversation_dicts_list


def getConversationDictsLists(_rule):
  #print("")
  conversation_dicts_list=[]
  conversation_tmpl_dict={}
  conversation_tmpl_dict = copy.deepcopy(_rule)    
  conversation_tmpl_dict.pop("source", "none")
  conversation_tmpl_dict.pop("destination", "none")
  conversation_tmpl_dict.pop("service", "none")
  # conversation_tmpl_dict.pop("action", "none")
  # conversation_tmpl_dict.pop("name", "none")
  # conversation_tmpl_dict.pop("comments", "none")
  log.info("Get conversations list out of a rule")
  i=0
  for src in _rule["source"]:
    for dest in _rule["destination"]:
      for service in _rule["service"]:
        i=i+1
        #conversation_dict={}
        conversation_dict = copy.deepcopy(conversation_tmpl_dict)
        #conversation_dict["name"]=_rule["name"]    
        conversation_dict["rule_conv_id"]=i                
        # TBD              
        conversation_dict["src_obj_name"]=src["name"]
        conversation_dict["src_start"]=src["start"]
        conversation_dict["src_end"]=src["end"]
        conversation_dict["src_start_dec"]=src["start_dec"]
        conversation_dict["src_end_dec"]=src["end_dec"]
        conversation_dict["dest_obj_name"]=dest["name"]
        conversation_dict["dest_start"]=dest["start"]
        conversation_dict["dest_end"]=dest["end"]
        conversation_dict["dest_start_dec"]=dest["start_dec"]
        conversation_dict["dest_end_dec"]=dest["end_dec"]

        conversation_dict["service_obj_name"]=service["name"]    
        conversation_dict["service_protocol"]=service["protocol"]
        conversation_dict["service_number_start"]=service["start"]
        conversation_dict["service_number_end"]=service["end"]

        conversation_dicts_list.append(conversation_dict)                
        #conversation_dict["comments"]=_rule["comments"]    
        #conversation_dict["action"]=_rule["action"]    

        #pprint.pprint(conversation_dict)
        #exit()

    return conversation_dicts_list
    
def getRulePreparedForDb(_rule, _package_name, _access_layer_name, _section, _objs_dict, _conf_d):        
  log.debug("Rule prepared to be saved into db:")                
  #pprint.pprint(_rule)         
  #pprint.pprint(_rule["domain"])
  rule_prepared_db=OrderedDict()
  rule_prepared_db["policy_name"]=_package_name
  rule_prepared_db["policy_import_date"]=datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]
  rule_prepared_db["policy_vendor"]=_conf_d["vendor_name"]
  rule_prepared_db["policy_mgmt"]=_conf_d["mgmt_name"]
  #rule_prepared_db["policy_management"]=_conf_d["mgmt_name"]
  rule_prepared_db["policy_domain"]=_rule["domain"]["name"]    
  rule_prepared_db["access_layer_name"]=_access_layer_name
  rule_prepared_db["policy_domain"]=_rule["domain"]["name"]        
  rule_prepared_db["section"]=_section
  rule_prepared_db["enabled"]=_rule["enabled"] 
  rule_prepared_db["rid"]=_rule["rule-number"] 
  rule_prepared_db["name"]=""
  if "name" in _rule:
    rule_prepared_db["name"]=_rule["name"]
  rule_prepared_db["source"]=_rule["source"]
  rule_prepared_db["destination"]=_rule["destination"]
  rule_prepared_db["service"]=_rule["service"]
  rule_prepared_db["action"]=_objs_dict[_rule["action"]]["name"].lower()	
  rule_prepared_db["comments"]=_rule["comments"]
  rule_prepared_db["track"]=_objs_dict[_rule["track"]["type"]]["name"]
  log.debug("rule prepared for db dict:")                
  #pprint.pprint(rule_prepared_db)      

  return rule_prepared_db


def getNetObjDictsL(_obj_d):      
  net_obj_d_l=[]
  net_obj_d={"name":"", "type":"", "start":"", "end":""}
  net_obj_d_l.append(net_obj_d)

  type=_obj_d["type"]  
  log.debug("type: "+type)
  log.debug("_obj_d: ")
  #pprint.pprint(_obj_d)

  net_obj_d["name"]=_obj_d["name"]
  net_obj_d["type"]=_obj_d["type"]
  if type=="group":
    log.debug("")
    log.debug("members: "+str(_obj_d["members"]))
    net_obj_d_l.pop(0)
    for mem in _obj_d["members"]:
      net_obj_d_l.extend(getNetObjDictsL(mem))
      
  elif type=="host" or type=="CpmiHostCkp":
    log.debug("") 
    net_obj_d["start"]=_obj_d["ipv4-address"]
    net_obj_d["end"]=_obj_d["ipv4-address"]
    #pprint.pprint(net_obj_d)
    #exit()

  elif type=="network":
    log.debug("")
    net_obj_d["start"]=_obj_d["subnet4"]
    net_obj_d["end"]=ipaddress.IPv4Network(_obj_d["subnet4"]+"/"+_obj_d["subnet-mask"]).broadcast_address
    net_obj_d["end"]=str(net_obj_d["end"])
    #pprint.pprint(net_obj_d)
    #exit()
  
  elif type=="address-range":
    log.debug("") 
    #pprint.pprint(net_obj_d)
    net_obj_d["start"]=_obj_d["ipv4-address-first"]
    net_obj_d["end"]=_obj_d["ipv4-address-last"]

  elif type=="CpmiAnyObject":     
    log.debug("") 
    #pprint.pprint(net_obj_d)
    net_obj_d["start"]="0.0.0.0"
    net_obj_d["end"]="255.255.255.255"

  else:
    log.error("ERROR!!! following net obj type is unknown: "+type)
    exit()

  return net_obj_d_l


def getPort_d(_port):
  rslt_d={}

  log.debug("_port: "+_port)  
  if re.search("^\d*$", _port): 
    log.debug("port found")
    rslt_d["start"]=_port
    rslt_d["end"]=_port

  elif re.search("^\d*-\d*$", _port):
    log.debug("range found")  
    tmp_l=_port.split("-")
    rslt_d["start"]=tmp_l[0]
    rslt_d["end"]=tmp_l[1]

  elif re.search("^>\d*$", _port):
    log.debug("greater than found") 
    rslt_d["start"]=_port.replace(">","")
    rslt_d["end"]="65536"

  else:
    log.error("ERROR!!! following port format is unknown: "+_port)
    exit()

  return rslt_d


def getServiceObjsDictsL(_obj_d, _objects_dict):
  objs_prep_d_l=[]
  
  obj_prep_d={"name":"", "type":"", "protocol":"", "start":"", "end":""}
  objs_prep_d_l.append(obj_prep_d)

  log.debug("_obj_d:")
  #pprint.pprint(_obj_d)
  type=_obj_d["type"]  
  log.debug("type: "+type)
  log.debug("_obj_d: ")  

  obj_prep_d["name"]=_obj_d["name"]
  obj_prep_d["type"]=_obj_d["type"]

  if type=="service-group":
    log.info("")
    for mem in _obj_d["members"]:
      log.debug("mem: "+str(mem))
      if isinstance(mem, dict):
        #objs_prep_d_l.append(getServiceObjsDictsL(mem, _objects_dict))
        objs_prep_d_l.pop(0)
        objs_prep_d_l.extend(getServiceObjsDictsL(mem, _objects_dict))
      else:
        #objs_prep_d_l.append(getServiceObjsDictsL(_objects_dict[mem], _objects_dict))
        objs_prep_d_l.pop(0)
        objs_prep_d_l.extend(getServiceObjsDictsL(_objects_dict[mem], _objects_dict))

  elif type=="service-udp":
    obj_prep_d["protocol"]="udp"
    obj_prep_d.update(getPort_d(_obj_d["port"]))
   
  elif type=="service-tcp":
    obj_prep_d["protocol"]="tcp"
    obj_prep_d.update(getPort_d(_obj_d["port"]))

  elif type=="service-icmp":
    obj_prep_d["protocol"]="icmp"
    obj_prep_d["start"]=_obj_d["icmp-type"]
    obj_prep_d["end"]=_obj_d["icmp-type"]

  elif type=="CpmiAnyObject":
    obj_prep_d["protocol"]="any"
    obj_prep_d["start"]="0"
    obj_prep_d["end"]="65536"

  elif type=="service-other":
    obj_prep_d["protocol"]=_obj_d["ip-protocol"]
    obj_prep_d["start"]="0"
    obj_prep_d["end"]="0"

  elif type=="service-dce-rpc":
    obj_prep_d["protocol"]="dce-rpc"
    obj_prep_d["start"]=_obj_d["interface-uuid"]
    obj_prep_d["end"]=_obj_d["interface-uuid"]  

  elif type=="service-rpc":
    obj_prep_d["protocol"]="rpc"
    obj_prep_d["start"]=_obj_d["program-number"]
    obj_prep_d["end"]=_obj_d["program-number"]  

  else:
    log.error("ERROR!!! following service obj type is unknown: "+type)
    exit()

  return objs_prep_d_l


def resolveRuleObjs(_rulebase_prepared_for_db_l, _objects_dict):
  
  for rule_d in _rulebase_prepared_for_db_l:
    log.debug("resolveRuleObjs: Resolve sources")      
    
    src_objs_l=[]
    service_objs_l=[]
    dest_objs_l=[]
    #for obj_uid in rule_d["source"]:
    for obj_uid in rule_d["source"]:
      obj_prep_d_l=getNetObjDictsL(_objects_dict[obj_uid])      
      src_objs_l.extend(obj_prep_d_l)
      #pprint.pprint(obj_prep_d)
    
    for obj_uid in rule_d["destination"]:
      obj_prep_d_l=getNetObjDictsL(_objects_dict[obj_uid])        
      dest_objs_l.extend(obj_prep_d_l)
      #pprint.pprint(obj_prep_d)

    for obj_uid in rule_d["service"]:
      obj_prep_d_l=getServiceObjsDictsL(_objects_dict[obj_uid], _objects_dict)        
      service_objs_l.extend(obj_prep_d_l)
      
    # print("src objs prep: ")
    # pprint.pprint(src_objs_l)
    # print("dest objs prep: ")
    # pprint.pprint(dest_objs_l)

    rule_d["source"]=src_objs_l
    rule_d["destination"]=dest_objs_l
    rule_d["service"]=service_objs_l

    #pprint.pprint(rule_d)
    #exit()


def calcDecimalForNetobjs(rulebase_prepared_for_db_l):
  #log.debug("Calc")
  for rule_d in rulebase_prepared_for_db_l:
    #log.debug("rule_d: ")
    for src in rule_d["source"]: 
      src["start_dec"]=int(ipaddress.IPv4Address(src["start"]))
      src["end_dec"]=int(ipaddress.IPv4Address(src["end"]))
      #pprint.pprint(src)
      #exit()
    for dest in rule_d["destination"]: 
      dest["start_dec"]=int(ipaddress.IPv4Address(dest["start"]))
      dest["end_dec"]=int(ipaddress.IPv4Address(dest["end"]))
      #pprint.pprint(src)
      #exit()

    #rule_d["source"]=src
    #rule_d["destination"]=dest
    #pprint.pprint(rule_d)
    #exit()



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
    #pprint.pprint(objects_dict)    
    #exit()

    log.debug("saveRuleBaseConvToDb: 3. Put rulebase into list of dict")

    rulebase_prepared_for_db_l=[]
    #log.debug("_rulebase_json: ")
    #pprint.pprint(_rulebase_json)    
    access_layer_name=_rulebase_json["name"]
    for rule in _rulebase_json["rulebase"]:  
        # Check for sections 
        if not "name" in rule:
          rule["name"]=""
        section=""
        if "rulebase" in rule:           
            section=rule["name"] 
            log.debug("This is a section")
            for rule in rule["rulebase"]:       
                rule_prepared_for_db_d=getRulePreparedForDb(rule, _package_name, access_layer_name, section, objects_dict, _conf_d)                                    
                rulebase_prepared_for_db_l.append(rule_prepared_for_db_d)  
        else:       
          #log.debug("       Rule: ")
          #pprint.pprint(rule)     
          rule_prepared_for_db_d=getRulePreparedForDb(rule, _package_name, access_layer_name, section, objects_dict, _conf_d)                                    
          rulebase_prepared_for_db_l.append(rule_prepared_for_db_d)                        
        
    log.debug("\nrulebase_prepared_for_db: ")
    #pprint.pprint(rulebase_prepared_for_db_l)   
    #exit()

    log.debug("saveRuleBaseConvToDb: 3.1 Resolve objects UIDs")    
    resolveRuleObjs(rulebase_prepared_for_db_l, objects_dict)

    log.debug("Calculate decimal values for src and dest")
    calcDecimalForNetobjs(rulebase_prepared_for_db_l)
    
    log.debug("\nrulebase_prepared_for_db resolved: ")
    #pprint.pprint(rulebase_prepared_for_db_l)  

    #exit()
    log.debug("saveRuleBaseConvToDb: 4. Create conversations and save them into db one by one")
    
    for rule in rulebase_prepared_for_db_l:
        conversation_dicts_list=[]
        log.debug("saveRuleBaseConvToDb Process on rule")
        #pprint.pprint(rule)        

        log.debug("saveRuleBaseConvToDb Create conversation dict here")
        conversation_dicts_list=getConversationDictsLists(rule)
        log.debug("saveRuleBaseConvToDb Conversation dict list:")   
        #pprint.pprint(conversation_dicts_list)         
        #exit()
       
        log.debug("saveRuleBaseConvToDb Save conversations of one rule into database")        
        rslt=hlprDb.writeDictsListToDatabase_wrapper(_dbCon, _conf_d["policy_conv_db_table"], conversation_dicts_list, _QLabel_status, hlprDb.mappingDictDb_conversations, False)
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


def getGrMembers(serv_gr_d):
  gr_mem_d_l=[]
  for mem in serv_gr_d["members"]:
    if isinstance(mem, dict):
      if mem["type"]=="service-group":
        log.debug("Nested serv group found")
        gr_mem_d_l.extend(getGrMembers(mem))
      else: 
        log.debug("Serv in serv group found")
        gr_mem_d_l.append(mem)       

  return gr_mem_d_l

def getServiceObjsFromGroupsFromRulebase(rulebase_json):
  gr_mems_d={}
  gr_mems_d_l=[]
  #pprint.pprint(rulebase_json["objects-dictionary"])
  serv_gr_l=[]
  
  log.debug("Get all serv groups")
  for d in rulebase_json["objects-dictionary"]:
    if d["type"]=="service-group":
      serv_gr_l.append(d)
  
  for serv_gr_d in serv_gr_l:
    # Use recursion here
    gr_mems_d_l.extend(getGrMembers(serv_gr_d))
  log.debug("Create dict out of list of dicts")
  for gr_mem_d in gr_mems_d_l:
    gr_mems_d[gr_mem_d["uid"]]=gr_mem_d

  log.debug("\n\nGroup members: ")
  #pprint.pprint(gr_mems_d)
  log.debug("gr_mem_d_l len: "+str(len(gr_mems_d)))
  
  return gr_mems_d


# def calcStatistics(rslt_d):
#   statistics_d=[]
#   statistics_d["Packages total:"] 

def getAllImportsStatus(res_d):
  all_exports_ok=True
  for rslt_domain in res_d["domains"]:
    for k, domain_d in rslt_domain.items():
      #log.debug("cma_d[all_exports_ok] "+str(cma_d["all_exports_ok"]))
      if not domain_d["all_imports_ok"]:
        all_exports_ok=False
        break
  res_d["all_imports_ok"]=all_exports_ok
  return all_exports_ok


def getPerDomainAllImportsStatus(_domain_res_d):
    result=True
    for k, v in _domain_res_d["imported_packages"].items(): 
      if not v: 
        result=False
    _domain_res_d["all_imports_ok"]=result
    log.debug("_res_layers_d: "+str(_domain_res_d))  
   

def importPackageZonesIntoDb(_dbCon, _mgmt_name, _conf_d, _policy_packages_l, _QLabel_status):
  rslt=""
  packages_zones_l=[]
 
  log.info("importPackageZonesIntoDb: Get data from packages.json into a list")
  for policy_d in _policy_packages_l:
    #log.debug("policy_d: "+str(policy_d))
    if policy_d["name"]=="Standard": 
      continue
    
    # Get zones from comment 
    zones=""
    zones_l=[]
    zones_str=policy_d["comments"]
    zones_l=zones_str.split(" ")
    log.info("zones_l: "+str(zones_l))
    if zones_l:
      if _conf_d["zones_tag_name"] in zones_l:
        if len(zones_l)>=zones_l.index(_conf_d["zones_tag_name"])+1:
          zones=zones_l[int(zones_l.index(_conf_d["zones_tag_name"]))+1]
    
    policy_zones_d={}
    #policy_zones_d["policy_mgmt"]=_mgmt_name
    #policy_zones_d["policy_mgmt_vendor"]=_conf_d["vendor_name"]
    policy_zones_d["policy_management"]=_mgmt_name
    policy_zones_d["policy_vendor"]=_conf_d["vendor_name"]
    policy_zones_d["policy_domain"]=policy_d["domain"]["name"]
    policy_zones_d["policy_name"]=policy_d["name"]
    policy_zones_d["policy_comments"]=policy_d["comments"]
    policy_zones_d["zones"]=zones
    
    
    log.debug("policy_zones_d: "+str(policy_zones_d))
    packages_zones_l.append(policy_zones_d)

  log.info("importPackageZonesIntoDb: Get pages object")        
  pages_d={}
  pages_d=InitPageObjs.initPageObjs()
  policy_packages_o=pages_d["policy_packages"]
  
  # FIXME: to be implemented
  log.info("importPackageZonesIntoDb: Verify data")        
  log.info("importPackageZonesIntoDb: Save data into db")
  rslt=hlprDb.writeDictsListToDatabase_wrapper(_dbCon, policy_packages_o.db_table, packages_zones_l, _QLabel_status, policy_packages_o.mapping_qtable_db_d, False) 
  
  return rslt



################# MODULE'S MAIN  ###################### 
#def ImportDataCHKP(_dbCon, _QLabel_status):
def import_data_into_db_main(_conf_d, _dbCon, _QLabel_status, _log):  
    global log
    log=_log
    res_d={}
    res_d["all_imports_ok"]=False
    res_d["domains"]=[]

    domains_list=[]
    #log=my_logger_func.get_logger("chkp_get_data_from_mgmt") 
   
    log.info("--- Start CHKP plugin module: import_data_into_db")  
  
    log.info("Following will be imported into db:")  
    log.info("  - Policy packages")
    log.info("  - Access layers rulebases")  
    log.info("  - Service groups")
    log.info("  - Gateways")

    # Get data from config.yml
    config_d={}
    with open(this_script_path+"/config.yml", 'r') as stream:
      config_d = yaml.safe_load(stream)
    _conf_d["data_export_folder"]=config_d["data_export_folder"]
    _conf_d["vendor_name"]=config_d["vendor_name"]
    _conf_d["policy_conv_db_table"]=config_d["policy_conv_db_table"]
    _conf_d["service_groups_file"]=config_d["service_groups_file"]
    _conf_d["policy_package_zones_db_table"]=config_d["policy_package_zones_db_table"]
    
    _conf_d["zones_tag_name"]=config_d["zones_tag_name"]
    #print(config_d)
 
    mgmt_name=_conf_d["mgmt_name"]
    import_data_folder=_conf_d["data_export_folder"]+mgmt_name

    log.info("--- 1. Get domains list")
    for subdir, dirs, files in os.walk(import_data_folder):            
      if subdir==import_data_folder:
        domains_l=dirs
        break
    domains_l.sort()
    log.info("domains_l: "+str(domains_l))  
    #exit()

    log.info("--- 1.1 Delete rulebase conversations for this mgmt")  
    log.debug("Delete rulebase conversations for mgmt: {}, for vendor name: {}".format(_conf_d["mgmt_name"], _conf_d["vendor_name"]))        
    #cmd="delete from policy_package_conversations where policy_mgmt=\""+_conf_d["mgmt_name"]+"\" and policy_vendor=\""+_conf_d["vendor_name"]+"\";" 
    cmd="delete from "+_conf_d["policy_conv_db_table"]+" where policy_mgmt=\""+_conf_d["mgmt_name"]+"\" and policy_vendor=\""+_conf_d["vendor_name"]+"\";" 
    log.debug("cmd: "+cmd)      
    if hlprDb.executeSqlCmd(_dbCon, cmd):
      log.debug("Rulebase conversations for this mgmt have been deteted.")
    else:
      log.error("Rulebase conversations for this mgmt could not been deteted.") 


    log.info("--- 1.2 Delete policy packages for this mgmt")  
    log.debug("Delete policy packages for mgmt: {}, for vendor name: {}".format(_conf_d["mgmt_name"], _conf_d["vendor_name"]))        
    cmd="delete from "+_conf_d["policy_package_zones_db_table"]+" where policy_mgmt=\""+_conf_d["mgmt_name"]+"\" and policy_mgmt_vendor=\""+_conf_d["vendor_name"]+"\";" 
    log.debug("cmd: "+cmd)      
    if hlprDb.executeSqlCmd(_dbCon, cmd):
      log.debug("Policy packages for mgmt {} have been deteted.".format(_conf_d["mgmt_name"]))
    else:
      log.error("Rulebase conversations for mgmt {} could not been deteted.".format(_conf_d["mgmt_name"]))          
  
    
    log.info("--- 2. Process per CHKP mgmt domain")
    for domain in domains_l:
      
      # Just for test
      #domain="CMA1"
      log.info("Domain name: "+domain)
      
      # Prepare containers for summary
      domain_imp_res_d={}
      packages_imp_res_l=[]
      res_d["domains"].append({domain : domain_imp_res_d})
      #domain_imp_res_d["imported_packages"]=packages_imp_res_l
      domain_imp_res_d["imported_packages"]={}
      domain_imp_res_d["all_imports_ok"]=""
      
      log.info("--- --- 2.0 Get files list")
      for subdir, dirs, files_l in os.walk(import_data_folder+"/"+domain):            
        log.debug("Subdir: "+str(subdir))
        log.debug("Dirs: "+str(dirs))
        log.debug("files: "+str(files_l))
        
      log.info("--- --- 2.1 Import gateways")
    
      log.info("--- --- 2.2 Put serv obj from groups into list of dicts")
      log.info("Get serv objs from service groups")
      serv_objs_d=getServiceObjsFromGroups(subdir+"/"+_conf_d["service_groups_file"]+".json")

      log.info("--- --- 2.3 Get packages")      
      file_name=import_data_folder+"/"+domain+"/packages.json"
      with open(file_name) as json_file:
        packages_d = json.load(json_file)
      #log.info("packages_d: "+str(packages_d))

      
      log.info("--- --- --- 2.3.0.1 Import package zones into Db")    
      log.info("_conf_d: "+str(_conf_d))
      # 
      #exit()
      res_importPackagesZones=importPackageZonesIntoDb(_dbCon, mgmt_name, _conf_d, packages_d["packages"], _QLabel_status)
      if res_importPackagesZones==True:
        log.info("importPackagesZones into db succeeded: "+str(res_importPackagesZones))
      else:
        log.error("importPackagesZones into db failed: "+str(res_importPackagesZones))
        res_d["all_imports_ok"]=False
        return res_d
      
      log.info("Per package")
      log.info("--- --- --- 2.3.1 Get access layer rulebase and save them into db")  
      for package in packages_d["packages"]:
        if package["name"]=="Standard":
          continue        
      
        log.info("Package name: "+package["name"])
        access_layers_l=[d["name"] for d in package["access-layers"]]
        log.info("Import package's access layers into database") 

        # For summary collection
        package_imp_res_d={}
        res_layers_d={}
        domain_imp_res_d["imported_packages"][package["name"]]=package_imp_res_d
        package_imp_res_d["layers"]=res_layers_d

        for layer in access_layers_l:          
          # FIXME For tests
          #layer="HQ_Fra_Network"
          layer=layer.replace(" ","_")
          log.info("Package access layer: "+str(layer))     
          
          access_layer_file=subdir+"/access_layer__"+layer+".json"
          #importAccessLayerIntoDb(access_layer_file, layer)    
         
          with open(access_layer_file) as json_file:
            rulebase_json = json.load(json_file)

          log.info("Get serv objs from service groups from rulebase file")  
          serv_objs_d.update(getServiceObjsFromGroupsFromRulebase(rulebase_json))
      
          rstl=saveRuleBaseConversationsToDb(rulebase_json, serv_objs_d, _conf_d, package["name"], _dbCon, _QLabel_status)
          
          #packages_imp_res_d[package["name"]]["import_ok"]=rstl
          # For results collection
          #res_layers_l.append({layer : rstl})
          res_layers_d[layer]=rstl
          if rstl==True:
              log.info("Conversations of package {}, layer {} saved into database".format(package["name"], layer))    
          else:
              log.error("Conversations of package {}, layer {} could NOT be saved into database".format(package["name"], layer))    

      #Per domain all_imports_summary
      getPerDomainAllImportsStatus(domain_imp_res_d)   
      log.info("!!! !!! res_d for domain {} {}".format(domain, str(res_d))) 
       

    log.info("### ### ### ### ###")
    log.info("Packages import into database finished.")
    log.info("Import result overview: ")
    #calcStatistics(rslt_d)
    #pprint.pprint(rt_d)

    getAllImportsStatus(res_d)
    log.info("Import results:")  
    print(json.dumps(res_d, indent=4))  

    return res_d


# def main():
#   conf_d={}
#   conf_d["mgmt_name"]="mds_fra"
#   conf_d["data_export_folder"]="data/for_import/chkp/"

#   dbCon=hlprDb.getDbCon()
#   import_data_into_db_main(conf_d, dbCon, "")
      
# # We use them only for dev phase
# # It must be deactivated in prod
# if __name__ == "__main__":  
#   main()
   

