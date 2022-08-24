


import sys
import os
import my_logger_func
import pprint
from datetime import datetime
from pathlib import Path
import ipaddress
  
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), 'classes/')))

import HelperDatabase as hlprDb
import Helper
import Class_ZonesConversation


def convert_ip_to_dec_wrapper(_data_d):

  pprint.pprint(_data_d) 
  res_l=convert_ip_to_dec(_data_d["src"])
  #log.debug("res_l: "+str(res_l))
  _data_d["src_start_dec"]=res_l[0]
  _data_d["src_end_dec"]=res_l[1]

  res_l=convert_ip_to_dec(_data_d["dest"])
  _data_d["dest_start_dec"]=res_l[0]
  _data_d["dest_end_dec"]=res_l[1]


def convert_ip_to_dec(_ip_str):
  log.debug("Translate ip_addresses into decimal ip_addresses")
  res_l=[]
  if "-" in _ip_str:
    # Process on ip range
    ip_l=ip_str.split("-")
    res_l.append(ipaddress.IPv4Network(ip_l[0].strip()).network_address)
    res_l.append(ipaddress.IPv4Network(ip_l[1].strip()).network_address)
  else:
    # Process on ip address or network
    ip=ipaddress.IPv4Network(_ip_str)
    res_l.append(int(ip.network_address))
    res_l.append(int(ip.broadcast_address))
  
  return res_l


def get_rel_policies(_dbCon, _data_d):
  rel_pol_l=[]
  
  if not _data_d["policies"]:
    rel_pol_l=hlprDb.getAllDataFromDbTable(_dbCon, "policy_packages_zones")
  else:
    log.debug("TODO")
    # .....

  return rel_pol_l


def get_conversations(_dbCon, _data_d, rel_policies_l):
  conv_l=[]
  policy_convs_l=[]

  action_to_check="accept"

  log.debug("Get policy conversations violating provided conv")
  for rel_policy in rel_policies_l:
    log.debug("--- --- Get violation conv in policy package: "+rel_policy["policy_name"])
    sql_cmd="select * from policy_package_conversations where \
        policy_name==\""+rel_policy["policy_name"]+"\" and\
        policy_mgmt==\""+rel_policy["policy_mgmt"]+"\" and\
        policy_vendor==\""+rel_policy["policy_mgmt_vendor"]+"\" \
        and (\
        ((src_start_dec<=\""+str(_data_d["src_start_dec"])+"\" and \
        src_end_dec>=\""+str(_data_d["src_start_dec"])+"\") or \
        (src_start_dec<=\""+str(_data_d["src_end_dec"])+"\" and \
        src_end_dec>=\""+str(_data_d["src_end_dec"])+"\")) \
        or \
        ((src_start_dec>=\""+str(_data_d["src_start_dec"])+"\" and \
        src_start_dec<=\""+str(_data_d["src_end_dec"])+"\") or \
        (src_end_dec>=\""+str(_data_d["src_start_dec"])+"\" and \
        src_end_dec<=\""+str(_data_d["src_end_dec"])+"\")) \
        ) and (\
        ((dest_start_dec<=\""+str(_data_d["dest_start_dec"])+"\" and \
        dest_end_dec>=\""+str(_data_d["dest_start_dec"])+"\") or \
        (dest_start_dec<=\""+str(_data_d["dest_end_dec"])+"\" and \
        dest_end_dec>=\""+str(_data_d["dest_end_dec"])+"\")) \
        or \
        ((dest_start_dec>=\""+str(_data_d["dest_start_dec"])+"\" and \
        dest_start_dec<=\""+str(_data_d["dest_end_dec"])+"\") or \
        (dest_end_dec>=\""+str(_data_d["dest_start_dec"])+"\" and \
        dest_end_dec<=\""+str(_data_d["dest_end_dec"])+"\")) \
        ) and \
        service_protocol==\""+str(_data_d["service_prot"])+"\" \
        and (\
        ((service_number_start<=\""+str(_data_d["service_num_start"])+"\" and \
        service_number_end>=\""+str(_data_d["service_num_start"])+"\") or \
        (service_number_start<=\""+str(_data_d["service_num_end"])+"\" and \
        service_number_end>=\""+str(_data_d["service_num_end"])+"\")) \
        or \
        ((service_number_start>=\""+str(_data_d["service_num_start"])+"\" and \
        service_number_start<=\""+str(_data_d["service_num_end"])+"\") or \
        (service_number_end>=\""+str(_data_d["service_num_start"])+"\" and \
        service_number_end<=\""+str(_data_d["service_num_end"])+"\")) \
        ) and \
        action==\""+action_to_check+"\""
    #policy_conv_violating_l.extend(hlprDb.executeSqlCmdGetResult(_dbCon, sql_cmd)) 
    policy_convs_l=hlprDb.executeSqlCmdGetResult(_dbCon, sql_cmd)
    conv_l.extend(policy_convs_l)

  return conv_l

  
def convert_service(_data_d):
  log.debug("Translate to prot and range")
  
  serv_l=_data_d["service"].split("_")
  _data_d["service_prot"]=serv_l[0].strip()

  prot_num_l=serv_l[1].split("-")
  _data_d["service_num_start"]=prot_num_l[0]
  if len(prot_num_l)==2:
    _data_d["service_num_end"]=prot_num_l[1]
  else:
    _data_d["service_num_end"]=prot_num_l[0]


def extendConvL(conv_l, _data_d):
  new_conv_l=[]
  request_d={}
  request_d["request_src"]=_data_d["src"]
  request_d["request_dest"]=_data_d["dest"]
  request_d["request_service"]=_data_d["service"]
  for conv in conv_l:
    conv.pop("id", None)
    new_conv={}
    new_conv=request_d
    new_conv.update(conv)
    new_conv_l.append(new_conv)
  
  return new_conv_l


def make_connections_check_main(_dbCon, _data_d):
  res_d={}
  global log
  log=my_logger_func.get_logger("connections_check")
  log.info("### Start connections check for given src, dest, services and policies ###") 

  log.info("### 1. Validate data")
  #res_d=validate_data(_data_d):
  #if res_d["validation_ok"]==False:
  #  return res_d

  log.info("### 2. Convert ip to dec")
  convert_ip_to_dec_wrapper(_data_d)
  convert_service(_data_d)
  pprint.pprint(_data_d)

  log.info("### 3. Get relevant policies")
  policies_l=get_rel_policies(_dbCon, _data_d)
  #pprint.pprint(policies_l)

  log.info("### 4. Looks for conversations")
  conv_l=get_conversations(_dbCon, _data_d, policies_l)
  #pprint.pprint(conv_l)

  log.info("### 4.1 Extend conversation with src, dest and service")
  conv_l=extendConvL(conv_l, _data_d)
   # Get request data 
  #pprint.pprint(conv_l)
  

  log.info("### 5. Save violating conversations into reports")
  # Create subfolder
  log.info("Prepare reports folder.")
  my_date = datetime.now().strftime("%Y%m%d_%H%M%S")
  report_subfolder_name=os.path.join(_data_d["reports_folder"],"__SingleConnectionCheck")
  Path(report_subfolder_name).mkdir(parents=True, exist_ok=True)
  log.info("report_subfolder created: "+report_subfolder_name)
  report_file_name_csv=os.path.join(report_subfolder_name, "report_"+my_date+".csv")
  report_file_name_json=os.path.join(report_subfolder_name, "report_"+my_date+".json")
  
  log.info("Save violating conversations into csv file.")
  if Helper.saveListOfDictsToCSV(conv_l, report_file_name_csv):
    res_d["success"]=True
    log.info("Csv report successfully saved into {}".format(report_file_name_csv))
  else:
    res_d["success"]=False
  
  log.info("Save violating conversations into json.")
  if Helper.saveListOfDictsToJson(conv_l, report_file_name_json):
    res_d["success"]=True
    log.info("Json report successfully saved into {}".format(report_file_name_json))
  else:
    res_d["success"]=False


  #_data_d["source_start_dec"]=_data_d["source"]
  #_data_d["destination"]=_data_d["source"]
  #_data_d["service"]=_data_d["source"]

  return res_d


def main():  
  dbCon=hlprDb.getDbCon()

  input_data_d={}
  input_data_d["src"]="10.0.0.0/8"
  input_data_d["dest"]="10.0.0.0/16"
  input_data_d["service"]="tcp_22"
  input_data_d["policies"]=""
  input_data_d["reports_folder"]="fpa_reports"
  

  res=make_connections_check_main(dbCon, input_data_d)  
  print("result:")
  print(res)


if __name__ == "__main__":
    # execute only if run as a script
    main()

