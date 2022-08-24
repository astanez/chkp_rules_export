import os
import sys
import my_logger_func
import pprint
from datetime import datetime
from pathlib import Path
  
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), 'classes/')))

import HelperDatabase as hlprDb
import Helper
import Class_ZonesConversation


def getConvViolatingSecMatrix(_dbCon, zones_conv_d_l):
  policy_conv_violating_l=[]

  policies_d_l=hlprDb.getAllDataFromDbTable(_dbCon, "policy_packages_zones")

  log.debug("Process per zones conversaion")
  for zone_conv in zones_conv_d_l:
    log.debug(" --- Find violating policies convers for followng zones conv: ")
    log.debug(str(zone_conv))
    if zone_conv["action"]=="block":
      action_to_check="accept"
    else:
      action_to_check="drop"
      log.info("The communication between zones is allowed. No need for checks.")
      continue

    log.debug("Get relevant policies for this conv from db")
    rel_policies_l=getListOfRelevantPolicyPackages(policies_d_l, zone_conv)  
    #rel_policies_l=[d for d in zones_conv_d_l if d["src_zone"]==src_zone and d["dest_zone"]==dest_zone]
    log.debug("Relevant policies for this conv:")
    for policy in rel_policies_l:
      log.debug(policy)
    #pprint.pprint(rel_policies_l)

    log.debug("Get policy conversations violating zone_conv")
    for rel_policy in rel_policies_l:
      log.debug("--- --- Get violation conv in policy package: "+rel_policy["policy_name"])
      sql_cmd="select * from policy_package_conversations where \
          policy_name==\""+rel_policy["policy_name"]+"\" and\
          policy_mgmt==\""+rel_policy["policy_mgmt"]+"\" and\
          policy_vendor==\""+rel_policy["policy_mgmt_vendor"]+"\" \
          and (\
          ((src_start_dec<=\""+zone_conv["src_ip_start_dec"]+"\" and \
          src_end_dec>=\""+zone_conv["src_ip_start_dec"]+"\") or \
          (src_start_dec<=\""+zone_conv["src_ip_end_dec"]+"\" and \
          src_end_dec>=\""+zone_conv["src_ip_end_dec"]+"\")) \
          or \
          ((src_start_dec>=\""+zone_conv["src_ip_start_dec"]+"\" and \
          src_start_dec<=\""+zone_conv["src_ip_end_dec"]+"\") or \
          (src_end_dec>=\""+zone_conv["src_ip_start_dec"]+"\" and \
          src_end_dec<=\""+zone_conv["src_ip_end_dec"]+"\")) \
          ) and (\
          ((dest_start_dec<=\""+zone_conv["dest_ip_start_dec"]+"\" and \
          dest_end_dec>=\""+zone_conv["dest_ip_start_dec"]+"\") or \
          (dest_start_dec<=\""+zone_conv["dest_ip_end_dec"]+"\" and \
          dest_end_dec>=\""+zone_conv["dest_ip_end_dec"]+"\")) \
          or \
          ((dest_start_dec>=\""+zone_conv["dest_ip_start_dec"]+"\" and \
          dest_start_dec<=\""+zone_conv["dest_ip_end_dec"]+"\") or \
          (dest_end_dec>=\""+zone_conv["dest_ip_start_dec"]+"\" and \
          dest_end_dec<=\""+zone_conv["dest_ip_end_dec"]+"\")) \
          ) and \
          action==\""+action_to_check+"\""
      #policy_conv_violating_l.extend(hlprDb.executeSqlCmdGetResult(_dbCon, sql_cmd)) 
      policy_convs_l=hlprDb.executeSqlCmdGetResult(_dbCon, sql_cmd)
      policy_convs_res_l=[]

      log.debug("Add fields: src_zone, dest_zone, src_zone_ip, dest_zone_ip, zones_action")
      for policy_d in policy_convs_l:
        policy_res_d={}
        policy_res_d["zone_src"]=zone_conv["src_zone"]
        policy_res_d["zone_dest"]=zone_conv["dest_zone"]
        policy_res_d["zone_src_ip"]=zone_conv["src_ip"]
        policy_res_d["zone_dest_ip"]=zone_conv["dest_ip"]
        policy_res_d["zones_action"]=zone_conv["action"]
        policy_res_d.update(policy_d)
        del policy_res_d["id"]
        del policy_res_d["src_start_dec"]
        del policy_res_d["src_end_dec"]
        del policy_res_d["dest_start_dec"]
        del policy_res_d["dest_end_dec"]
        policy_convs_res_l.append(policy_res_d)
        policy_d.clear()

      policy_conv_violating_l.extend(policy_convs_res_l)  
      #log.debug("Zones conv dec ip ranges:")
      #log.debug("Src: {}-{} Dest: {}-{}".format(zone_conv["src_ip_start_dec"],zone_conv["src_ip_end_dec"],zone_conv["dest_ip_start_dec"],zone_conv["dest_ip_end_dec"]))
   
  log.debug("policy_conv_violating_l:")
  log.debug("Policy_convs violating zones conv:")
  for c in policy_conv_violating_l:
    #log.debug(c["policy_name"]+" "+c["src_obj_name"]+" "+c["src_start"]+" "+c["src_end"]+\
    #          " "+c["dest_obj_name"]+" "+c["dest_start"]+" "+c["dest_end"])
    #log.debug("IP ranges dec: {} {} {} {}".format(c["src_start_dec"], c["src_end_dec"], c["dest_start_dec"], c["dest_end_dec"]))
    log.debug("Violating conversation: "+str(c))
  
  return policy_conv_violating_l


def getListOfRelevantPolicyPackages(policies_d_l, zone_conv):
  rel_policies_d_l=[]

  for policy_d in policies_d_l:
    policy_zones_l=policy_d["zones"].split(",")
    policy_zones_l=[i.strip() for i in policy_zones_l]
    if zone_conv["src_zone"] in policy_zones_l or zone_conv["dest_zone"] in policy_zones_l:
      rel_policies_d_l.append(policy_d)

  return rel_policies_d_l


def getListOfRelevantPolicyPackages_old(_dbCon, _report_d):
  rel_policies_d_l=[]
  log.debug("Get all zones conversation from db")
  policies_d_l=hlprDb.getAllDataFromDbTable(_dbCon, "policy_packages_zones")
  
  log.debug("Get relevant zones conversation")
  src_zones_l=_report_d["source_zones"].split(",")
  dest_zones_l=_report_d["destination_zones"].split(",")
  zones_l=set(src_zones_l+dest_zones_l)
  zones_l=[i.strip() for i in zones_l]
  log.debug("zones_l: "+str(zones_l))

  for zone in zones_l:
    for policy_d in policies_d_l:
      policy_zones_l=policy_d["zones"].split(",")
      policy_zones_l=[i.strip() for i in policy_zones_l]
      if zone in policy_zones_l:
        rel_policies_d_l.append(policy_d)

  return rel_policies_d_l


def getRelevantZonesConversations(_dbCon, _report_d):
  rel_zones_conv_d_l=[]
  zones_conv_d_l=[]

  log.debug("Get all zones conversation from db")
  zones_conv_d_l=hlprDb.getAllDataFromDbTable(_dbCon, Class_ZonesConversation.ZonesConversation.db_table)
  
  log.debug("Get relevant zones conversation")
  src_zones_l=_report_d["source_zones"].split(",")
  dest_zones_l=_report_d["destination_zones"].split(",")
  log.debug("Rel src_zones: "+str(src_zones_l))
  log.debug("Rel dest_zones: "+str(dest_zones_l))

  for src_zone in src_zones_l:
    src_zone=src_zone.strip()
    for dest_zone in dest_zones_l:
      dest_zone=dest_zone.strip()
      rel_conv_l=[d for d in zones_conv_d_l if d["src_zone"]==src_zone and d["dest_zone"]==dest_zone]
      rel_zones_conv_d_l.extend(rel_conv_l)  

  #log.debug("rel_zones_conv_d_l")
  #pprint.pprint(rel_zones_conv_d_l)
  
  return rel_zones_conv_d_l


def prepareReportFile(_report_d):
  log.debug("Create folder")

  log.debug("Create file and write csv header")


def prepareReportsSubfolder(_report_d, _my_date):
  # Create subfolder name
  #report_subfolder_name=_report_d["reports_folder"]+_report_d["name"].replace(" ","_")+"_"+_my_date
  report_subfolder_name=os.path.join(_report_d["reports_folder"],_report_d["name"].replace(" ","_")+"_"+_my_date)
  log.debug("report_subfolder_name: "+report_subfolder_name)
  # Create folder
  Path(report_subfolder_name).mkdir(parents=True, exist_ok=True)
  return report_subfolder_name
   

def create_policy_compliance_report_main(_dbCon, _report_d):
  res_d={}
  global log
  log=my_logger_func.get_logger("policy_compl_reports")
  log.info("### Start creation of compliace policy report ###") 

  log.info("Get relevant security matrix zones conversations")
  zones_conv_d_l=getRelevantZonesConversations(_dbCon, _report_d)
  log.debug("relevant zones_conversations: ")
  pprint.pprint(zones_conv_d_l)

  log.info("Get conversations violating security matrix")
  policy_conv_violating_l=getConvViolatingSecMatrix(_dbCon, zones_conv_d_l)  
  res_d["violation_conv_number"]=len(policy_conv_violating_l)
  if not policy_conv_violating_l:
    res_d["success"]=True
    return res_d
    
  log.info("Prepare reports folder.")
  my_date = datetime.now().strftime("%Y%m%d_%H%M%S")
  reports_folder=prepareReportsSubfolder(_report_d, my_date)
  log.info("reports_folder: "+reports_folder)
  reports_file_name=os.path.join(reports_folder, _report_d["name"].replace(" ","_")+"_"+my_date)
  log.info("reports_file_name: "+reports_file_name)
  report_file_name_csv=reports_file_name+".csv"
  report_file_name_json=reports_file_name+".json"

  log.debug("Save violating conversations into csv file.")
  if Helper.saveListOfDictsToCSV(policy_conv_violating_l, report_file_name_csv):
    res_d["success"]=True
    log.debug("Csv report successfully saved into {}".format(report_file_name_csv))
  else:
    res_d["success"]=False
  
  log.debug("Save violating conversations into json.")
  if Helper.saveListOfDictsToJson(policy_conv_violating_l, report_file_name_json):
    res_d["success"]=True
    log.debug("Json report successfully saved into {}".format(report_file_name_json))
  else:
    res_d["success"]=False
  
  return res_d


def main():  
  dbCon=hlprDb.getDbCon()

  report_row_d={}
  report_row_d["name"]="Zone1 to Zone2"
  report_row_d["source_zones"]="Zone1, Zone2"
  report_row_d["destination_zones"]="Zone1, Zone2"
  report_row_d["create_reports"]=""
  report_row_d["regular_reports"]=""
  report_row_d["reports_folder"]="fpa_reports"
  
  res=create_policy_compliance_report_main(dbCon, report_row_d)  
  print("result:")
  print(res)


if __name__ == "__main__":
    # execute only if run as a script
    main()

