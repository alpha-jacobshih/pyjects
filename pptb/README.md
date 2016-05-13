# pptb
PLC Parameter Toolbox  
[pptb.py](#): a plc parameter toolbox to dump and compare the parameter files for either pib or ggl.
to execute pptb.py, you should have python 2.7 installed in either linux or windows.

---
## dump
usage:  
```
usage: pptb.py dump [-h] {raw,pib,ggl} ...

optional arguments:
  -h, --help     show this help message and exit

dump:
  {raw,pib,ggl}  the actions of dump
    raw          dump the file in hex.
    pib          dump the pib file.
    ggl          dump the ggl file.
```

### dump raw
usage:
```
usage: pptb.py dump raw [-h] -f file

optional arguments:
  -h, --help  show this help message and exit
  -f file     the file to be dumped.
```

example:
```
./pptb.py dump raw -f ./test/DHPP508AVA1_PIB110CEB_WM.pib

00000000: 01 00 01 00 00 00 00 00 60 00 00 00 00 00 00 00  | ........`.......
00000010: 00 03 00 00 91 B2 C5 65 FF FF FF FF 60 03 00 00  | .......e....`...
00000020: FF FF FF FF 0E 00 00 00 00 00 00 00 00 00 00 00  | ................
00000030: 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00  | ................
00000040: 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00  | ................
00000050: 00 00 00 00 00 00 00 00 00 00 00 00 61 4D 3B 9A  | ............aM;.
00000060: 00 00 00 00 04 00 00 00 CD AB 34 12 01 00 00 00  | ..........4.....
00000070: 04 00 00 00 01 00 00 00 02 00 00 00 04 00 00 00  | ................
00000080: 01 00 00 00 03 00 00 00 04 00 00 00 04 00 00 00  | ................
...
```

### dump pib
usage:
```
usage: pptb.py dump pib [-h] [-a] -f filename -g getpib -l layout file

optional arguments:
  -h, --help      show this help message and exit
  -a              display all information (name/offset/length/data) in json.
  -f filename     the pib file.
  -g getpib       the path of getpib.
  -l layout file  the xml file describes the pib offset.
```

example:
 1. dump the pib file in brief.
```
./pptb.py dump pib -g ./test/getpib -l ./test/piboffset.xml -f ./test/DHPP508AVA1_PIB110CEB_WM.pib

...
MACAddress                            00:57:19:11:13:00
DAK                                   689F074B8B0275A2710B0B5779AD1630
HFID_Manufacturer                     A*AT1*N12001*P0110*F0111*H1A*D639*CDHPP508AVA1_FW111b01
NMK                                   50D3E4933F855B7040784DF815AA8DB7
HFID_User                             DHPP508AVA1_PIB110CEB_WM_AV500
HFID_AVLN                             DHPP508AVA1_FW111b01_FWDate_09_Mar_2016_CS_ce5b1c36
...
```
 2. dump the pib file in detail.
```
./pptb.py dump pib -a -g ./test/getpib -l ./test/piboffset.xml -f ./test/DHPP508AVA1_PIB110CEB_WM.pib

[
  {
    "type": "MAC",
    "length": 6,
    "data": "00:57:19:11:13:00",
    "name": "MACAddress",
    "offset": 12
  },
  {
    "type": "DATA",
    "length": 16,
    "data": "689F074B8B0275A2710B0B5779AD1630",
    "name": "DAK",
    "offset": 18
  },
  {
    "type": "HFID",
    "length": 64,
    "data": "A*AT1*N12001*P0110*F0111*H1A*D639*CDHPP508AVA1_FW111b01",
    "name": "HFID_Manufacturer",
    "offset": 36
  },
  {
    "type": "DATA",
    "length": 16,
    "data": "50D3E4933F855B7040784DF815AA8DB7",
    "name": "NMK",
    "offset": 100
  },
  {
    "type": "HFID",
    "length": 64,
    "data": "DHPP508AVA1_PIB110CEB_WM_AV500",
    "name": "HFID_User",
    "offset": 116
  },
  {
    "type": "HFID",
    "length": 64,
    "data": "DHPP508AVA1_FW111b01_FWDate_09_Mar_2016_CS_ce5b1c36",
    "name": "HFID_AVLN",
    "offset": 180
  },
  ...
]
```

### dump ggl
usage:
```
usage: pptb.py dump ggl [-h] [-a] -f filename [-l layout file optional]

optional arguments:
  -h, --help            show this help message and exit
  -a                    display all information (name/offset/length/data) in
                        json.
  -f filename           the ggl or paramconfig file.
  -l layout file (optional)
                        the csv file describes parameter offset of paramconfig
                        file.
```

example:
 1. dump the pib file in brief.
```
./pptb.py dump ggl -f ./test/DHPP610AVB1_FW100CEBb02.rakis_A1_no_diag.ggl

...
statinfo_manufacturer_sta_hfid                  DHPP610AVB1_FW100b02_FWDate_13_May_2016_CS_A3BEB3A8
statinfo_manufacturer_avln_hfid                 DHPP610AVB1_PIB100CEB_WM_AV+
button_control                                  0F00
led_timing_2                                    FF7F0000
odm_private_string                              A*AR1*N03220*P0100*F0100*H1A*D65D*CDHPP610AVB1_FW100b02
plconfig_user_nmk                               50D3E4933F855B7040784DF815AA8DB7
statinfo_user_sta_hfid                          DHPP610AVB1_FW100b02_FWDate_13_May_2016_CS_A3BEB3A8
statinfo_user_avln_hfid                         DHPP610AVB1_PIB100CEB_WM_AV+
...
```
 2. dump the pib file in detail.
```
./pptb.py dump ggl -a -f ./test/DHPP610AVB1_FW100CEBb02.rakis_A1_no_diag.ggl

[
  {
    "type": "HFID",
    "length": 64,
    "data": "DHPP610AVB1_FW100b02_FWDate_13_May_2016_CS_A3BEB3A8",
    "name": "statinfo_manufacturer_sta_hfid",
    "offset": 263
  },
  {
    "type": "HFID",
    "length": 64,
    "data": "DHPP610AVB1_PIB100CEB_WM_AV+",
    "name": "statinfo_manufacturer_avln_hfid",
    "offset": 327
  },
  {
    "type": "HFID",
    "length": 64,
    "data": "A*AR1*N03220*P0100*F0100*H1A*D65D*CDHPP610AVB1_FW100b02",
    "name": "odm_private_string",
    "offset": 399
  },
  {
    "type": "DATA",
    "length": 16,
    "data": "50D3E4933F855B7040784DF815AA8DB7",
    "name": "plconfig_user_nmk",
    "offset": 470
  },
  {
    "type": "HFID",
    "length": 64,
    "data": "DHPP610AVB1_FW100b02_FWDate_13_May_2016_CS_A3BEB3A8",
    "name": "statinfo_user_sta_hfid",
    "offset": 486
  },
  {
    "type": "HFID",
    "length": 64,
    "data": "DHPP610AVB1_PIB100CEB_WM_AV+",
    "name": "statinfo_user_avln_hfid",
    "offset": 550
  },
...
]
```
----

## diff
usage:
```
usage: pptb.py diff [-h] {pib,ggl} ...

optional arguments:
  -h, --help  show this help message and exit

diff:
  {pib,ggl}   the actions of diff
    pib       compare the pib files.
    ggl       compare the ggl files.
```

### diff pib
usage:
```
usage: pptb.py diff pib [-h] -f filename -F filename -g getpib -l layout file
                        [-o output] [-b]

optional arguments:
  -h, --help      show this help message and exit
  -f filename     the pib file.
  -F filename     another pib file to compare.
  -g getpib       the path of getpib.
  -l layout file  the xml file describes the pib offset.
  -o output       save difference to output file (in json).
  -b              display in brief.
```

example:
```
./pptb.py diff pib -b -g ./test/getpib -l ./test/piboffset.xml -f ./test/DHPP508AVA1_PIB102CEB_WM.pib -F ./test/DHPP508AVA1_PIB110CEB_WM.pib

================================================================================
0024   64 HFID_Manufacturer
- A*AT1*N12001*P0110*F0111*H1A*D639*CDHPP508AVA1_FW111b01
+ A*AT1*N12001*P0102*F0110*H1A*D5AC*CDHPP508AVA1_FW110b01
================================================================================
0074   64 HFID_User
- DHPP508AVA1_PIB110CEB_WM_AV500
+ DHPP508AVA1_PIB102CEB_WM_AV500
================================================================================
00B4   64 HFID_AVLN
- DHPP508AVA1_FW111b01_FWDate_09_Mar_2016_CS_ce5b1c36
+ DHPP508AVA1_FW110b01_FWDate_12_Oct_2015_CS_ce5b1c36
================================================================================
0239  384 Reserved_CustomAggregationParameters
- 00000360: 00 00 01 01 01 01 01 00 00 00 00 00 00 00 00 00
+           00 00 01 01 01 01 01 04 00 00 00 00 00 00 00 00
================================================================================
03B9 1619 RSVD
- 000006E0: 02 01 02 00 00 00 00 00 00 00 00 00 00 00 00 00
+           00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00
- 000006F0: 00 00 00 00 02 00 00 00 00 00 00 00 00 00 00 00
+           00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00
================================================================================
0A10 4620 PrescalerValues
- 00000F20: 00 00 00 00 01 00 00 00 00 00 00 00 00 00 00 00
+           00 00 00 00 01 00 00 00 12 12 12 12 12 12 02 11
- 00000F30: 0D 14 1E 2A 2E 2F 2F 2F 2D 19 13 00 00 00 00 00
+           25 1F 1B 1C 1B 1B 1B 1A 1E 21 23 27 25 23 25 24
- 00000F40: 00 00 00 0E 0A 0B 00 00 00 00 00 00 00 00 00 00
+           24 22 23 23 22 23 28 13 05 10 10 10 10 10 10 10
...
```

### diff ggl
usage:
```
usage: pptb.py diff ggl [-h] -f filename -F filename
                        [-l layout file optional)] [-L layout file (optional]
                        [-o output] [-b]

optional arguments:
  -h, --help            show this help message and exit
  -f filename           the ggl or paramconfig file (src).
  -F filename           another ggl or paramconfig file (dst) to compare.
  -l layout file (optional)
                        the csv file describes parameter offset of paramconfig
                        file (src).
  -L layout file (optional)
                        the csv file describes parameter offset of paramconfig
                        file (dst).
  -o output             save difference to output file (in json).
  -b                    display in brief.
```

example:
```
./pptb.py diff ggl -b -f ./test/DHPP610AVB1_FW100CEBb01.rakis_A0_no_diag.ggl -F ./test/DHPP610AVB1_FW100CEBb02.rakis_A1_no_diag.ggl

================================================================================
00FC    8 load_thr
- 00000100: 44 5B 75 90
+           44 60 7A 95
================================================================================
0107   64 statinfo_manufacturer_sta_hfid
- DHPP610AVB1_FW100b01_FWDate_16_Mar_2016_CS_49AA4C7B
+ DHPP610AVB1_FW100b02_FWDate_13_May_2016_CS_A3BEB3A8
================================================================================
0147   64 statinfo_manufacturer_avln_hfid
- DHPP610AVB1_PIB100CEB_WM_AV500
+ DHPP610AVB1_PIB100CEB_WM_AV+
================================================================================
018F   64 odm_private_string
- A*AR1*N03200*P0100*F0100*H1A*D63G*CDHPP610AVB1_FW100b01
+ A*AR1*N03220*P0100*F0100*H1A*D65D*CDHPP610AVB1_FW100b02
================================================================================
01E6   64 statinfo_user_sta_hfid
- DHPP610AVB1_FW100b01_FWDate_16_Mar_2016_CS_49AA4C7B
+ DHPP610AVB1_FW100b02_FWDate_13_May_2016_CS_A3BEB3A8
================================================================================
0226   64 statinfo_user_avln_hfid
- DHPP610AVB1_PIB100CEB_WM_AV500
+ DHPP610AVB1_PIB100CEB_WM_AV+
================================================================================
0ABB    1 pbo_rx_linearity_table_index
- 00000AB0:                                  00
+
================================================================================
0AF5    1 avs_overheat_thr_up_c
- 00000AF0:
+                          73
================================================================================
0AF6    1 avs_overheat_thr_down_c
- 00000AF0:
+                             69
...
```

----
