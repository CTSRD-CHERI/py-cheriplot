#-
# SPDX-License-Identifier: BSD-2-Clause
#
# Copyright (c) 2025 Benjamin Barnes-Lewis
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions
# are met:
# 1. Redistributions of source code must retain the above copyright
#    notice, this list of conditions and the following disclaimer.
# 2. Redistributions in binary form must reproduce the above copyright
#    notice, this list of conditions and the following disclaimer in the
#    documentation and/or other materials provided with the distribution.
#
# THIS SOFTWARE IS PROVIDED BY THE AUTHOR AND CONTRIBUTORS ``AS IS'' AND
# ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED.  IN NO EVENT SHALL THE AUTHOR OR CONTRIBUTORS BE LIABLE
# FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
# DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS
# OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION)
# HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT
# LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY
# OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF
# SUCH DAMAGE.
#

import json
import os
from collections import OrderedDict
import db_utils

# Get capabilities from db
def get_caps(db, lb, ub):
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
    print(f"Number of capabilities: {len(caps)}")
    return caps[lb:ub]

# Get symbols from db
def get_syms(db):
    get_syms_q = "SELECT * FROM elf_sym"
    syms_q_results = db_utils.run_sql_query(db, get_syms_q)
    
    syms = []
    for syms_result in syms_q_results:
        sym = {}
        sym["region"] = syms_result[0]
        sym["symbol"] = syms_result[1]
        sym["type"] = syms_result[4]
        sym["bind"] = syms_result[5]
        sym["addr"] = hex(int(syms_result[6], base=16))
        syms.append(sym)
    print(f"Number of symbols: {len(syms)}")
    return syms

# Create a file of all capabilities
def make_caps_file(caps_file_name, lb, ub):
    caps = get_caps("demo.db", lb, ub)

    key_map = {
        "cap_loc_addr": "Location",
        "cap_loc_path": "?",
        "cap_addr": "Address",
        "cap_perms": "Permissions",
        "cap_base": "LowerBound",
        "cap_top": "UpperBound"
    }

    desired_key_order = [
        "Type",
        "Tag",
        "Permissions",
        "Executive",
        "Global",
        "Object Type",
        "UpperBound",
        "LowerBound",
        "Address",
        "Location"
    ]

    new_caps = []
    for cap in caps:
        # Build a temporary dict with mapped/converted keys
        temp_cap = {}
        for old_key, new_key in key_map.items():
            if old_key in cap:
                value = cap[old_key]
                if new_key in ["Location", "LowerBound", "UpperBound"]:
                    try:
                        value = int(value, 16)
                    except Exception:
                        pass
                temp_cap[new_key] = value

        # Fill in defaults
        temp_cap.setdefault("Permissions", "")
        temp_cap.setdefault("Type", "stack")
        temp_cap.setdefault("Tag", 1)
        temp_cap.setdefault("Executive", "")
        temp_cap.setdefault("Global", "")
        temp_cap.setdefault("Object Type", "")

        # Enforce key order
        ordered_cap = OrderedDict((key, temp_cap.get(key, "")) for key in desired_key_order)
        new_caps.append(ordered_cap)

    with open(f"{caps_file_name}.json", "w") as c:
        json.dump(new_caps, c, indent=2)

# Create a json file of all symbols
def make_syms_file(syms_file_name, lb, ub):
    syms = get_syms("demo.db")
    new_syms = syms
    with open(f"{syms_file_name}.json", "w") as s:
        json.dump(new_syms, s, indent=2)
    
if __name__ == "__main__":
    lb, ub = 0, 10425
    make_caps_file("db_caps_inp", lb, ub)
    make_syms_file("db_syms_inp")