# Plugin to expord data from Check Point (CHKP) management server (mgmt) and to save them into mysql database


# 1. Export data from CHKP management

# 2. Import data into database


CHKP plugin. 
Export data from MGMT result: 

{
    "all_exports_ok": true,
    "domains": [
        {
            "CMA1": {
                "all_exports_ok": true,
                "login_ok": true,
                "policy_packages_export_ok": true,
                "access_layers_export_ok": true,
                "access_layers_exported": {
                    "NewYourk_DC_Network": true
                },
                "service_groups_export_ok": true,
                "gateways_export_ok": true
            }
        },
        {
            "CMA2": {
                "all_exports_ok": true,
                "login_ok": true,
                "policy_packages_export_ok": true,
                "access_layers_export_ok": true,
                "access_layers_exported": {
                    "DE_Branch_Mun_Network": true,
                    "Layer_dc_fra": true,
                    "HQ_Fra_Network": true,
                    "UK_Branch_Network": true
                },
                "service_groups_export_ok": true,
                "gateways_export_ok": true
            }
        }
    ],
    "config_data": {
        "mgmt_name": "mds_fra",
        "mgmt_ip": "10.211.55.10",
        "mgmt_user": "automation_user",
        "mgmt_port": "443",
        "data_export_folder": "data/for_import/chkp/"
    }
}