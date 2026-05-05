#!/usr/bin/env python3
"""
WW2 Pretense conversion script (Expanded v3)
1. Clean init.lua - remove modern structures and swap ground unit types in templates
2. Process mission & warehouses - swap ALL unit types (Players + AI Templates)
3. Repack .miz
"""

import os
import re
import zipfile
import time

SRC_DIR      = r'C:\Users\conbe\DevProjects\repos\WW2-pretense\src\original_Pretense_caucasus_1.7.2'
INIT_LUA     = os.path.join(SRC_DIR, 'l10n', 'DEFAULT', 'init.lua')
MISSION_FILE = os.path.join(SRC_DIR, 'mission')
WAREHOUSES   = os.path.join(SRC_DIR, 'warehouses')
OUTPUT_MIZ   = r'C:\Users\conbe\DevProjects\repos\WW2-pretense\WW2_pretense_caucasus.miz'

# ─────────────────────────────────────────────────────────────────
# Mappings
# ─────────────────────────────────────────────────────────────────

# Comprehensive Aircraft Mapping (Modern -> WW2)
TYPE_MAP = {
    'F-16C_50':       'P-51D-30-NA',
    'FA-18C_hornet':  'SpitfireLFMkIX',
    'F-14B':          'P-51D-30-NA',
    'F-15C':          'P-51D-30-NA',
    'F-15E':          'P-47D-30',
    'F-15ESE':        'P-47D-30',
    'F-5E-3':         'P-51D-30-NA',
    'M-2000C':        'SpitfireLFMkIX',
    'Mirage-F1EE':    'SpitfireLFMkIX',
    'Mirage-F1M-EE':  'SpitfireLFMkIX',
    'A-10C_2':        'P-47D-30',
    'A-10A':          'P-47D-30',
    'AV8BNA':         'P-47D-40',
    'AJS37':          'MosquitoFBVI',
    'MiG-29S':        'Bf-109K-4',
    'MiG-29A':        'Bf-109K-4',
    'Su-27':          'Bf-109K-4',
    'Su-33':          'Bf-109K-4',
    'JF-17':          'Fw-190D-9',
    'MiG-21Bis':      'Bf-109K-4',
    'MiG-19P':        'Fw-190A-8',
    'Su-25':          'Fw-190A-8',
    'Su-25T':         'Fw-190A-8',
    'MiG-23MLD':      'Bf-109K-4',
    'MiG-25PD':       'Bf-109K-4',
    'MiG-31':         'Bf-109K-4',
    'Su-24M':         'Ju-88A4',
    'Su-30':          'Bf-109K-4',
    'Su-34':          'Ju-88A4',
    'MiG-27K':        'Ju-88A4',
    'Tu-22M3':        'Ju-88A4',
    'Tornado IDS':    'Ju-88A4',
    'C-101CC':        'TF-51D',
    'MB-339A':        'TF-51D',
    'L-39ZA':         'TF-51D',
    'A-50':           'Ju-88A4',
    'E-3A':           'B-17G',
    'E-2C':           'B-17G',
    'IL-78M':         'Ju-88A4',
    'KC130':          'Hercules',
    'KC-135':         'Hercules',
    'S-3B Tanker':    'Hercules',
    'MQ-9 Reaper':    'Yak-52',
    'An-26B':         'Hercules',
    'C-47':           'Hercules',
    'UH-60A':         'Yak-52',
    'UH-1H':          'Yak-52', 
    'AH-64D_BLK_II':  'Yak-52',
    'AH-1W':          'Yak-52',
    'Ka-50_3':        'Yak-52',
    'Ka-50':          'Yak-52',
    'Mi-24P':         'Yak-52',
    'Mi-24V':         'Yak-52',
    'Mi-8MT':         'Yak-52',
    'SA342L':         'Yak-52',
    'SA342M':         'Yak-52',
    'CH-47Fbl1':      'Yak-52',
    'CH-47D':         'Yak-52',
}

UNIT_MAP = {
    "T-90": "Tiger_I",
    "M-1 Abrams": "M4_Sherman",
    "M-2 Bradley": "Cromwell_IV",
    "M1128 Stryker MGS": "M8_Greyhound",
    "BTR_D": "Pz_IV",
    "BTR-80": "Pz_IV",
    "BTR-82A": "Pz_IV",
    "BRDM-2": "M8_Greyhound",
    "ZSU-23-4 Shilka": "Flak_38",
    "Gepard": "Bofors_40mm",
    "HEMTT_C-RAM_Phalanx": "M45_Quadmount",
    "Strela-1 9P31": "Flak_38",
    "M1097 Avenger": "M45_Quadmount",
    "Ural-375 ZU-23": "Flak_38",
    "Ural-4320T": "Opel_Blitz_36-6700A",
    "GAZ-66": "Opel_Blitz_36-6700A",
    "KAMAZ Truck": "Opel_Blitz_36-6700A",
    "Tigr_233036": "Opel_Blitz_36-6700A",
    "M1043 HMMWV Armament": "M8_Greyhound",
    "M1045 HMMWV TOW": "M4_Sherman",
    "M 818": "Bedford_MWD",
    "ATZ-5": "Bedford_MWD",
    "M978 HEMTT Tanker": "Bedford_MWD",
    "ZIL-135": "Opel_Blitz_36-6700A",
    "SA-18 Igla manpad": "Infantry AK", 
    "Soldier stinger": "Soldier M4 GRG",
}

SHIP_MAP = {
    "Stennis": "USS_Samuel_Chase",
    "USS_Arleigh_Burke_IIa": "USS_Samuel_Chase",
    "PERRY": "USS_Samuel_Chase",
    "LHA_Tarawa": "USS_Samuel_Chase",
}

ALL_MAPS = {**TYPE_MAP, **UNIT_MAP, **SHIP_MAP}

# ─────────────────────────────────────────────────────────────────
# 1. Clean init.lua
# ─────────────────────────────────────────────────────────────────

print("=== Cleaning init.lua ===")

with open(INIT_LUA, 'r', encoding='utf-8') as fh:
    raw = fh.read()

lines = raw.split('\n')
clean = []

LINE_REMOVE = [
    'presets.missions.attack.sead:extend',
    'presets.missions.support.awacs:extend',
    'presets.missions.support.tanker:extend',
    'stennis:addSupportFlight("Focus Flight"',
    'stennis:addSupportFlight("Bloodhound Flight"',
]

in_sead_preset = False
in_support_block = False
sead_depth = 0
support_depth = 0
replaced_units_init = 0

for line in lines:
    if not in_sead_preset and 'sead = Preset:new({' in line:
        in_sead_preset = True
        sead_depth = line.count('{') - line.count('}')
        continue
    if in_sead_preset:
        sead_depth += line.count('{') - line.count('}')
        if sead_depth <= 0: in_sead_preset = False
        continue

    if not in_support_block and re.search(r'^\s*support\s*=\s*\{', line):
        in_support_block = True
        support_depth = line.count('{') - line.count('}')
        continue
    if in_support_block:
        support_depth += line.count('{') - line.count('}')
        if support_depth <= 0: in_support_block = False
        continue

    if any(p in line for p in LINE_REMOVE): continue

    for old, new in ALL_MAPS.items():
        if f'"{old}"' in line:
            line = line.replace(f'"{old}"', f'"{new}"')
            replaced_units_init += 1

    clean.append(line)

print(f"  units/aircraft   : replaced {replaced_units_init} references")

with open(INIT_LUA, 'w', encoding='utf-8') as fh:
    fh.write('\n'.join(clean))

# ─────────────────────────────────────────────────────────────────
# 2. Process mission & warehouses
# ─────────────────────────────────────────────────────────────────

def process_file(path, label):
    print(f"\n=== Processing {label} ===")
    with open(path, 'r', encoding='utf-8') as fh:
        lines = fh.readlines()
    
    replaced_count = 0
    for i, line in enumerate(lines):
        for old, new in ALL_MAPS.items():
            needle = f'"{old}"'
            if needle in line:
                lines[i] = line.replace(needle, f'"{new}"')
                replaced_count += 1
                break
    
    with open(path, 'w', encoding='utf-8') as fh:
        fh.writelines(lines)
    print(f"  {replaced_count} total replacements made")

process_file(MISSION_FILE, "mission file")
process_file(WAREHOUSES, "warehouses file")

# ─────────────────────────────────────────────────────────────────
# 3. Repack as .miz
# ─────────────────────────────────────────────────────────────────

print(f"\n=== Repacking to {OUTPUT_MIZ} ===")

with zipfile.ZipFile(OUTPUT_MIZ, 'w', zipfile.ZIP_DEFLATED) as zf:
    file_count = 0
    fixed_time = (2026, 4, 29, 12, 0, 0)
    for root, dirs, files in os.walk(SRC_DIR):
        for fname in sorted(files):
            fpath = os.path.join(root, fname)
            arcname = os.path.relpath(fpath, SRC_DIR)
            zinfo = zipfile.ZipInfo(arcname, date_time=fixed_time)
            zinfo.compress_type = zipfile.ZIP_DEFLATED
            with open(fpath, 'rb') as f:
                zf.writestr(zinfo, f.read())
            file_count += 1

print(f"  {file_count} files packed\nDone.")
