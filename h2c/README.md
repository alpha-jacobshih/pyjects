# h2c
header file to c file generator.  
[h2c.py](#): generates c source files from the header files.  
to execute h2c.py, you should have python 3.5 installed in either linux or windows.  

---
## generates c source files from the header files.
usage:  
```
usage: h2c.py [-h] -i INPUT -o OUTPUT

====== generate c code from the header file ======

optional arguments:
  -h, --help            show this help message and exit
  -i INPUT, --input INPUT
                        folder of the header files.
  -o OUTPUT, --output OUTPUT
                        output folder.
```

example:
```
./h2c.py --input ./temp/h/ --output ./temp/src/
```
it traverses into the folder ./temp/h to read the header file and generates the c code to folder ./temp/src.  



