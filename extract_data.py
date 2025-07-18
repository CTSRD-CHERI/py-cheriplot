#-
# SPDX-License-Identifier: BSD-2-Clause
#
# Copyright (c) 2025 Jessica Man
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
        sym["addr"] = int(syms_result[6], base=16)
        syms.append(sym)
    return syms

dbname= "demo.db"
caps = get_caps(dbname)
caps_subset = caps[200:210]
for cap in caps_subset:
    print(json.dumps(cap, indent=2))

print("How many caps found? ", len(caps))

syms = get_syms(dbname)
syms_subset = syms[0:10]
for sym in syms_subset:
    print(json.dumps(sym, indent=2))

print("How many syms found? ", len(syms))
