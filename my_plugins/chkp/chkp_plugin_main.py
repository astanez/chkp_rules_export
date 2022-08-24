import sys
import os
import os.path as path

import chkp_get_data_from_mgmt
import chkp_import_data_into_db

this_script_path = path.abspath(path.join(__file__, ".."))
mylibs_path=this_script_path+"/../../mylibs/"
sys.path.append(mylibs_path)

import my_logger_func
import HelperDatabase as hlprDb


def import_data_from_chkp_into_db(_dbCon, _conf_d, _qlabel_status):
  result = False
  domains_list=[]
  global log
  log=my_logger_func.get_logger("chkp_get_data_from_mgmt")
  log.info("### Start Check Point data export plugin ###") 

  # # Get data from CHKP management into json files
  log.info("Get data from CHKP management into json file")
  res_d=chkp_get_data_from_mgmt.export_data_main(_conf_d, log)  
  if "all_exports_ok" in res_d:
    if res_d["all_exports_ok"]:
      result = True
  if not result:
    log.error("ERROR: Data export from CHKP management failed")
    return result

 
  log.info("Import data from CHKP management into database")
  res_d=chkp_import_data_into_db.import_data_into_db_main(_conf_d, _dbCon, _qlabel_status, log)
  if "all_imports_ok" in res_d:
    if res_d["all_imports_ok"]:
      result = True
  if not result:
    log.error("ERROR: Data export from CHKP management failed")
    return result

  return result


# def main():  
#   dbCon=hlprDb.getDbCon()

#   conf_d={}
#   conf_d["mgmt_name"]="MGMT1"
#   conf_d["mgmt_ip"]="10.211.55.10"
#   conf_d["mgmt_user"]="automation_user"
#   conf_d["mgmt_pwd"]="qwe123"
 
#   res=import_data_from_chkp_into_db(dbCon, conf_d, "")  
#   print("result:")
#   print(res)

# if __name__ == "__main__":
#     # execute only if run as a script
#     main()
