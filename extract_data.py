import json
import math
import sqlite3
import os

import db_utils

def get_caps(db):
    get_libs_q = "SELECT * FROM vm"
    libs_q_results = db_utils.run_sql_query(db, get_libs_q)

    libs = []
    for libs_result in libs_q_results:
        lib = {}
        lib["start_addr"] = int(libs_result[0], base=16)
        lib["end_addr"] = int(libs_result[1], base=16)
        lib["mmap_path"] = os.path.basename(libs_result[2])
        if lib["mmap_path"].startswith("unknown"):
            lib["mmap_path"] = "heap"
        libs.append(lib)
        
    get_caps_q = "SELECT * FROM cap_info"
    caps_q_results = db_utils.run_sql_query(db, get_caps_q)

    caps = []
    for caps_result in caps_q_results:
        cap = {}
        cap["cap_loc_addr"] = hex(int(caps_result[0], base=16))
        cap["cap_loc_path"] = os.path.basename(caps_result[1])
        if cap["cap_loc_path"].startswith("unknown"):
            cap["cap_loc_path"] = "heap"
        cap["cap_addr"] = hex(int(caps_result[2], base=16))
        cap["cap_perms"] = caps_result[3]
        cap["cap_base"] = hex(int(caps_result[4], base=16))
        cap["cap_top"] = hex(int(caps_result[5], base=16))
        caps.append(cap)

    return caps

dbname= "demo.db"
caps = get_caps(dbname)
count = 0
for cap in caps:
    if cap["cap_loc_path"] == "Stack":
        count+=1
        print(json.dumps(cap, indent=2))
print(count)
