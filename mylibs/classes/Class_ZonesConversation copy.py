import sys, os
import json


class ZonesConversation():
  
  # Dict X  
  dicx_value1="fadsffssdfa"

  # Dict Y  
  dicy_value1="ffssdfa"
  
  

  db_table="security_matrix_conversations"
  db_table_mapping={}
  db_table_mapping["src_zone"]="src_zone"
  db_table_mapping["dest_zone"]="dest_zone"
  db_table_mapping["src_ip"]="src_ip"
  db_table_mapping["dest_ip"]="dest_ip"
  db_table_mapping["src_ip_start_dec"]="src_ip_start_dec"
  db_table_mapping["src_ip_end_dec"]="src_ip_end_dec"
  db_table_mapping["dest_ip_start_dec"]="dest_ip_start_dec"
  db_table_mapping["dest_ip_end_dec"]="dest_ip_end_dec"  
  db_table_mapping["action"]="action"

  def __init__(self):

    self.src_zone=""
    self.dest_zone=""
    self.src_ip=""
    self.dest_ip=""
    self.src_ip_start_dec=""
    self.src_ip_end_dec=""
    self.dest_ip_start_dec=""
    self.dest_ip_end_dec=""  
    self.action=""

  #def __str__(self):
  def toStr(self, _log):
    attrs = vars(self)
    _log.info("Zone conversation: ")
    for k, v in attrs.items():
      if k=="dbMapping":
        continue
      _log.info(k+": "+v)
  
  def __str__(self):
    attrs = vars(self)
    attrs_str=json.dumps(attrs, indent=4, sort_keys=True)
    return attrs_str  


  def __repr__(self):
    attrs = vars(self)
    attrs_str=json.dumps(attrs, indent=4, sort_keys=True)
    return attrs_str  