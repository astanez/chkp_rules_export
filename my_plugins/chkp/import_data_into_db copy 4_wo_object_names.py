#### 
# Exports data from Check Pont management via Web API
# 

# ToDo:
# Replace all "return false" from main -> to put error value in the result list 


import sys
import http.client
import json
import ssl
import os
import pprint
import json
import time
from pathlib import Path
import ast
import os.path as path
import re
import shutil

## This tool sends publish and logout to mgmt server

## Make sure following parameters are conifigured as env vars:
# export CHECKPOINT_SERVER=10.211.55.10
# export CHECKPOINT_USERNAME=automation_user
# export CHECKPOINT_PASSWORD=qwe123
# export CHECKPOINT_PORT=433
# export CHECKPOINT_DOMAIN="CMA2"

this_script_path = path.abspath(path.join(__file__, ".."))
#print("this_script_path: "+this_script_path)
#mylibs_path=(this_script_path+"/../../mylibs/").replace("!","\!")
mylibs_path=this_script_path+"/../../mylibs/"
sys.path.append(mylibs_path)

#print(str(sys.path))
#print(os.environ["PATH"])
#print(os.getenv("PATH"))

import my_logger_func

# Here the API session id will be saved during login
sid_file=this_script_path+"/sid.json"


def sendHttpsPos_Old(_ip, _port, _url, _headers, _body):  
  conn = http.client.HTTPSConnection(_ip+":"+_port, context = ssl._create_unverified_context())
  conn.request('POST', _url, _body, _headers)
  response = conn.getresponse()
  #print("\n Response")
  #print(response.read().decode())
  return response.read().decode()


def login_old(_conf_d):  
  rslt=""
  
  log.info("Login to CHKP mgmt "+_conf_d["mgmt_ip"]+":"+_conf_d["mgmt_port"]+" with user: "+_conf_d["mgmt_user"])

  log.debug("Login 1: Prepare header and body")  
  headers = {'Content-type': 'application/json'}  
  body = {"user": _conf_d["mgmt_user"], "password": _conf_d["mgmt_pwd"]}
  body_json = json.dumps(body)  
  #pprint.pprint(body_json)

  log.debug("Login 2: Send login API call")
  url="/web_api/login"  
  response=sendHttpsPost(_conf_d["mgmt_ip"], _conf_d["mgmt_port"], url, headers, body_json)
  response_d=json.loads(response)
  log.debug("Response:")
  print(response_d)
  if response_d["sid"]:
    log.info("Login successful")
  else: 
    log.error("Login failed")  

  if response_d["sid"]:
    log.debug("Login 3. Save reponse into "+sid_file)   
    with open(sid_file, 'w') as outfile:
      json.dump(response_d, outfile)   

  return rslt


def sendHttpsPost(_ip, _port, _action, _headers, _body_d):  
  url="/web_api/"+_action  
  body_json = json.dumps(_body_d)   
  conn = http.client.HTTPSConnection(_ip+":"+_port, context = ssl._create_unverified_context())
  conn.request('POST', url, body_json, _headers)
  response = conn.getresponse()
  #print("\n Response")
  #print(response.read().decode())
  response_d=json.loads(response.read().decode())
  #return response.read().decode()
  return response_d


def api_call_login(_conf_d, _domain=""):
  sid=""
  log.debug("Login to CHKP mgmt "+_conf_d["mgmt_ip"]+":"+_conf_d["mgmt_port"]+" with user: "+_conf_d["mgmt_user"]+" to domain "+_domain)  
  headers = {'Content-type': 'application/json'}  
  if _domain:  
    body_d = {"user": _conf_d["mgmt_user"], "password": _conf_d["mgmt_pwd"], "domain": _domain}  
  else: 
    body_d = {"user": _conf_d["mgmt_user"], "password": _conf_d["mgmt_pwd"]}    
  action="login"  
  response_d=sendHttpsPost(_conf_d["mgmt_ip"], _conf_d["mgmt_port"], action, headers, body_d)
  log.debug("response_d: "+str(response_d))  
  if "sid" in response_d:
    if response_d["sid"]:
      sid=response_d["sid"]  
      log.debug("Login successful")      
  
  if not sid:  
    log.debug("Login failed")  
  
  return sid  


def api_call(_conf_d, _sid, _action, _body_d):
  
  resp_d=api_call_inner(_conf_d, _sid, _action, _body_d)        
  items_l=[]

  # Get all items
  if "total" and "to" in resp_d:
    total=resp_d["total"]
    to=resp_d["to"]
    log.debug("total: "+str(total))
    if total>to:      
      log.debug("We need to run this call multiple times to get all items")      
      log.debug("_body_d: "+str(_body_d))      
      log.debug("keys: "+str(resp_d.keys()))

      # Set item list names for each api call
      if _action=="show-access-rulebase":
        items_list_name="rulebase"
      elif _action=="show-service-groups":
        items_list_name="objects"
      else:
        log.error("API call name unknown")  
        return False

      # This routine will get all items
      offset=0
      limit=500      
      _body_d["limit"]=limit     
      while offset<total+limit:
        log.debug("offset: "+str(offset))
        _body_d["offset"]=offset
        resp_d_tmp=api_call_inner(_conf_d, _sid, _action, _body_d)  
        items_l.extend(resp_d_tmp[items_list_name])
        offset=offset+limit

      resp_d["to"]=len(items_l)
      resp_d[items_list_name]=items_l      

  return resp_d


def api_call_inner(_conf_d, _sid, _action, _body_d):
  log.debug("To CHKP mgmt "+_conf_d["mgmt_ip"]+":"+_conf_d["mgmt_port"]+" with user: "+_conf_d["mgmt_user"])  
  log.debug("API call: "+_action)
  log.debug("body: "+str(_body_d))
  headers = {'Content-type': 'application/json', 'X-chkp-sid': _sid}      
  resp_d=sendHttpsPost(_conf_d["mgmt_ip"], _conf_d["mgmt_port"], _action, headers, _body_d)
  #log.debug("resp_d: "+str(resp_d))  
  return resp_d


def api_call_logout(_conf_d, _sid):
  rslt=True
  resp_d=api_call(_conf_d, _sid, "logout", {})
  if resp_d["message"]:
    if resp_d["message"]=="OK":      
      log.debug("Logout successful")            
  if not resp_d["message"]:
    rslt=False
    if not resp_d["message"]=="OK":      
      log.error("Logout failed")        
      rslt=False
  return rslt


def isMgmtMDS(_conf_d):
  rslt=True
  
  log.debug("--- --- getMgmtType 1: Try to connect to Global domain")
  sid=api_call_login(_conf_d, "Global")
  if not sid:
    log.error("Login failed")
    return False

  log.debug("--- --- getMgmtType 2: Logout")
  resp_d=api_call(_conf_d, sid, "logout", {})
  if resp_d["message"]:
    if resp_d["message"]=="OK":      
      log.debug("Logout successful")      
  if not resp_d["message"]:
    if not resp_d["message"]=="OK":      
      log.error("Logout failed")      

  return rslt



  


def getDomainsList(_conf_d):
  domains_l=[]
  log.debug("--- --- getDomainsList 1: Login")  
  sid=api_call_login(_conf_d, "")
  if not sid:
    log.error("Login failed")
    return False

  log.debug("--- --- getDomainsList 2: Get domains list")  
  resp_d=api_call(_conf_d, sid, "show-domains", {"limit": 500})
  if resp_d["objects"]:        
    domains_l=[d["name"] for d in resp_d["objects"]]
    log.debug("domains_l: "+str(domains_l))

  log.debug("--- --- getDomainsList 3: Logout")  
  resp_d=api_call_logout(_conf_d, sid)
  
  return domains_l


def apiCallFailed(_resp_d):
  rslt=False
  if "message" in _resp_d:
    if _resp_d["message"].find("not found"):
      rslt=True
  return rslt


def exportPackages(_conf_d, _sid, _domain):        
  log.debug("--- --- exportPackages: Get policy packages list")  
  packages_d=api_call(_conf_d, _sid, "show-packages", {"limit": 500, "details-level": "full"})
  #log.debug("packages_d: "+str(packages_d))
  if "packages" in packages_d:    
    writeIntoFile(_conf_d["data_export_folder"]+_conf_d["mgmt_name"]+"/"+_domain, "packages", packages_d)    
  else:    
    packages_d={}

  return packages_d


def exportAccessRulebases(_conf_d, _sid, _domain, _packages_d):
  rslt={}
  
  # log.debug("--- --- exportAccessRulebases 1: Get policy packages list")  
  # packages_d=api_call(_conf_d, _sid, "show-packages", {"limit": 500, "details-level": "full"})
  # #log.debug("packages_d: "+str(packages_d))
  # if not packages_d["packages"]:    
  #   rslt=False 
  # #packages_l=[d["name"] for d in packages_d["packages"]]  
  # #log.debug("packages_l: "+str(packages_l))  
  # writeIntoFile(_conf_d["data_export_folder"]+_conf_d["mgmt_name"]+"/"+_domain, "packages", packages_d)

  if _packages_d:
    log.debug("--- --- exportAccessRulebases: Export each access layer rulebase")      
    for package in _packages_d["packages"]: 
      if package["name"]=="Standard":
        continue
      for access_layer in package["access-layers"]:          
        access_layer_name=access_layer["name"].replace(" ","_")
        rslt[access_layer_name]=True     
        log.debug("Export access layer rulebase: "+access_layer["name"])           
        resp_d=api_call(_conf_d, _sid, "show-access-rulebase", {"name": access_layer["name"], "limit": 500, "details-level": "full"})
        #log.debug("resp_d: "+str(resp_d))         
        if apiCallFailed(resp_d):
          log.error("Export of following access layer rulebase failed: "+access_layer["name"])           
          rslt[access_layer_name]=False
        else:        
          writeIntoFile(_conf_d["data_export_folder"]+_conf_d["mgmt_name"]+"/"+_domain, "access_layer__"+access_layer_name, resp_d)
  
  return rslt  


def exportServiceGroups(_conf_d, _sid, _domain):
  rslt=True  
  log.debug("--- --- exportServiceGroups")  
  resp_d=api_call(_conf_d, _sid, "show-service-groups", {"limit": 500, "details-level": "full"})
  if not resp_d:    
    rslt=False   
  #log.debug("packages_l: "+str(packages_l))
  writeIntoFile(_conf_d["data_export_folder"]+_conf_d["mgmt_name"]+"/"+_domain, "service-groups", resp_d)
     
  return rslt


def exportGateways(_conf_d, _sid, _domain):
  rslt=True  
  log.debug("--- --- exportGateways")  
  resp_d=api_call(_conf_d, _sid, "show-gateways-and-servers", {"limit": 500, "details-level": "full"})
  if not resp_d:    
    rslt=False     
  writeIntoFile(_conf_d["data_export_folder"]+_conf_d["mgmt_name"]+"/"+_domain, "gateways", resp_d)
     
  return rslt


#### Common fuctions 
def  writeIntoFile(_folder, _file, _data_l):
  log.debug("Create folder")  
  Path(_folder).mkdir(parents=True, exist_ok=True)
 
  log.debug("Write json file")
  my_file=_folder+"/"+_file+".json"
  try:
    j = json.dumps(_data_l, indent=4)
    f = open(my_file, 'w')
    print(j, file=f)
    f.close()
    log.debug("Data have been written into: "+my_file)
  except:
    log.error("Data could not be written into: "+my_file)


################# MODULE'S MAIN  ###################### 
def import_data_into_db_main(_conf_d):   
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

  # Check input data
  if not _conf_d["mgmt_name"]:
    log.error("mgmt_name is empty.")
    return False    

  #log.info("--- 1. Check if we are on MDS or on SMS")
  
    
# We use them only for dev phase
# It must be deactivated in prod
def main():  
  conf_d={}
  conf_d["mgmt_name"]="mds_fra"
  conf_d["mgmt_ip"]="10.211.55.10"
  conf_d["mgmt_user"]="automation_user"
  conf_d["mgmt_pwd"]="qwe123"
  conf_d["mgmt_port"]="443"
  conf_d["data_export_folder"]="data/for_import/chkp/"
  

  import_data_into_db_main(conf_d)  
 
if __name__ == "__main__":
    # execute only if run as a script
    main()



