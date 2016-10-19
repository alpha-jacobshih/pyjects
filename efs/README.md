# efs (elf file stats)

## elf
### executable and linkable format
* the executable and linkable format (elf, formerly called extensible linking format)
  is a common standard file format for executables, object code, shared libraries,
  and core dumps.
* executable files include four canonical sections called, by convention, .text, .data, .rodata, and .bss.

<img src='https://upload.wikimedia.org/wikipedia/commons/7/77/Elf-layout--en.svg' width='370' title='elf layout'>

#### .text section
the .text section contains executable code and is packed into a segment which has the read and execute access rights.

#### .rodata section
the .rodata section, which contains read-only initialized data, is packed into the same segment that contains the .text section.

#### .data section
the .data section contains initialized data, and is packed into a segment which has the read and write access rights.
* the .data section contains information that could be changed during application execution, so this section must be copied for every instance.

#### .bss section
The .bss section contains uninitialized data, and is packed into a segment which has the read and write access rights.
* the .bss section is guaranteed to be all zeros when the program is loaded into memory.
* any global data that is uninitialized, or initialized to zero is placed in the .bss section.
* the .bss section data doesn't have to be included in the elf file.
* typically only the length of the bss section, but no data, is stored in the object file.
  the program loader allocates and initializes memory for the bss section when it loads the program.

#### caculate elf file size from the result of readelf
* code_size = header!['e_shoff'] + header!['e_shentsize'] * header!['e_shnum']
* (Start of section headers) + (Size of section headers) * (Number of section headers)

```
$ readelf -h test
ELF Header:
  Magic:   7f 45 4c 46 02 01 01 00 00 00 00 00 00 00 00 00
  Class:                             ELF64
  Data:                              2's complement, little endian
  Version:                           1 (current)
  OS/ABI:                            UNIX - System V
  ABI Version:                       0
  Type:                              EXEC (Executable file)
  Machine:                           Advanced Micro Devices X86-64
  Version:                           0x1
  Entry point address:               0x400da0
  Start of program headers:          64 (bytes into file)
  Start of section headers:          12960 (bytes into file)
  Flags:                             0x0
  Size of this header:               64 (bytes)
  Size of program headers:           56 (bytes)
  Number of program headers:         9
  Size of section headers:           64 (bytes)
  Number of section headers:         32
  Section header string table index: 29
```

----

## efs

### efs (elf file stats)
[efs.py](./efs.py) is a python script that analyzes the specified elf files to generate the report including the code size, memory usage and linking libraries.
* to execute efs.py, you should have python 3.x installed in either linux or windows.

#### usage
```
usage: efs.py [-h] -p filename [-t] [-j] [-a]

====== ELF file stats ======

optional arguments:
  -h, --help            show this help message and exit
  -p filename, --project filename
                        a json file describes the project configuration.
  -t, --output-trac     generate the report in trac format.
  -j, --output-js       generate the report in a javascript file.
  -a, --output-html     generate the report in an html file.
```

#### example
 * project file example (dcs962l.json)
```
{
    "project": {
        "name": "dcs962l",
        "model": "DCS-962L",
        "repo": {
            "type": "git",
            "url": "http://172.19.176.125:1234/",
            "queries": {
                "p": "vatics.git",
                "a": "commit",
                "h": ""
            }
        },
        "path": {
            "webfs": "mkimages/webfs/",
            "cgi": "mkimages/webfs/cgi/",
            "sbin": "mkimages/rootfs/sbin/",
            "lib": "mkimages/rootfs/lib/",
            "root": "/home/jacob_shih/000/ipcam/dcs962l/"
        },
        "sbin": [
            {
                "name": "acd",
                "description": "audio codec daemon",
                "comment": ""
            },
            {
                "name": "vcd",
                "description": "video codec daemon",
                "comment": ""

            },
            {
                "name": "watchdog",
                "description": "watchdog",
                "comment": ""

            }
        ]
    }
}
```
 * execute efs.py with the project file dcs962l.json to generate report files in html/js/trac format.
```
./efs.py -p test/dcs962l.json -atj
```

---
#### references
* [Executable and Linkable Format](https://en.wikipedia.org/wiki/Executable_and_Linkable_Format)
* [Special sections in Linux binaries](https://lwn.net/Articles/531148/)
* [The Art Of ELF: Analysis and Exploitations](http://fluxius.handgrep.se/2011/10/20/the-art-of-elf-analysises-and-exploitations/)
* [pyreadelf](https://github.com/eliben/pyelftools)
