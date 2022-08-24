import sys, os
import pprint

class ZonesExceptionsConversation():
  def __init__(self):

    self.src_zone=""
    self.dest_zone=""
    self.src_start_dec=""
    self.src_end_dec=""
    self.dest_start_dec=""
    self.dest_end_dec=""  
    self.service_obj_name=""
    self.service_protocol=""
    self.service_number_start=""
    self.service_number_end=""
    self.action=""
    self.cell_indexes=""

    self.dbMapping={}
    self.dbMapping[self.src_zone]="src_zone"
    self.dbMapping[self.dest_zone]="dest_zone"
    self.dbMapping[self.src_start_dec]="src_start_dec"
    self.dbMapping[self.src_end_dec]="src_end_dec"
    self.dbMapping[self.dest_start_dec]="dest_start_dec"
    self.dbMapping[self.dest_end_dec]="dest_end_dec"
    self.dbMapping[self.service_obj_name]="service_obj_name"
    self.dbMapping[self.service_protocol]="service_protocol"
    self.dbMapping[self.service_number_start]="service_number_start"
    self.dbMapping[self.service_number_end]="service_number_end"
    self.dbMapping[self.action]="action"
    self.dbMapping[self.cell_indexes]="cell_indexes"


  #def __str__(self):
  def toStr(self, _log):
    attrs = vars(self)
    _log.info("Zone conversation: ")
    for k, v in attrs.items():
      if k=="dbMapping":
        continue
      _log.info(k+": "+v)
  

  