#! /usr/bin/env python2.7
################################################################################
"""
pptb.py: a plc parameter toolbox to dump and compare the parameter files.
"""
import argparse
import json
import os
import string
import subprocess
import sys
import tarfile
import xml.etree.cElementTree

TYPE_BYTE = "BYTE"
TYPE_WORD = "WORD"
TYPE_LONG = "LONG"
TYPE_HUGE = "HUGE"
TYPE_HFID = "HFID"
TYPE_MAC = "MAC"
TYPE_KEY = "KEY"
TYPE_DATA = "DATA"


def dump_hex(filename, offset=None, nbytes=None):
    try:
        with file(filename, "r") as fh:
            offset = 0 if offset is None else offset
            nbytes = (os.path.getsize(filename) - offset) if not nbytes else nbytes
            fh.seek(offset)
            buf = fh.read(nbytes)
            for i in range(0, nbytes, 16):
                str_hex = " ".join("{:02X}".format(ord(c)) for c in buf[:16])
                str_asc = "".join(
                    c if c in string.printable and c not in string.whitespace else '.' for c in buf[:16])
                print "{:08x}: {:48s} | {}".format(offset + i, str_hex, str_asc)
                buf = buf[16:]
    except EnvironmentError as e:
        # noinspection PyProtectedMember
        print "%s(): %s" % (sys._getframe().f_code.co_name, e)
    return


class Parameter:
    paramconfig_header_length = 32

    def __init__(self, line=None):
        self._descriptor = None
        self._index = None
        self._bytes = None
        self._offset = None
        self._data = None

        if line:
            self.parseline(line)
        pass

    def parseline(self, line):
        params = line.split(";")
        self._descriptor = params[0]
        self._index = int(params[2])
        self._bytes = int(params[3]) * int(params[4]) / 8
        self._offset = self.paramconfig_header_length + int(params[5], 16)
        pass

    @property
    def key(self): return self._descriptor

    @property
    def name(self): return self._descriptor

    @property
    def index(self): return self._index

    @property
    def bytes(self): return self._bytes

    @property
    def offset(self): return self._offset

    @property
    def data(self): return self._data

    @data.setter
    def data(self, val): self._data = val


class PlcParameterToolbox:
    args = None

    def __init__(self):
        pass

    # noinspection PyMethodMayBeStatic
    def read_pib_file(self, filename, getpib, layout):
        listofhfid = [
            "HFID_Manufacturer",
            "HFID_User",
            "HFID_AVLN"
        ]
        listofmac = [
            "MACAddress",
            "SnifferReturnMACAddress",
            "CCo_MACAdd"
        ]

        xmlroot = xml.etree.cElementTree.parse(layout).getroot()
        params = []
        for obj in xmlroot.iter("object"):
            vartype = TYPE_DATA
            name = obj.attrib["name"]
            """
                the name is defined in layout file and it may be duplicated,
                therefore, we need to define another key to be identical, so
                that we can comapre the parameter files with the key.
            """
            matched = filter(lambda x: x["name"] == name, params)
            key = "{:s}{:02d}".format(name, len(matched)) if matched else name

            offset = int(obj.find("offset").text.strip(), 16)
            length = int(obj.find("length").text.strip(), 10)
            if name in listofhfid:
                vartype = TYPE_HFID
                cmd = "%s %s %X %s" % (getpib, filename, offset, "hfid")
            elif name in listofmac:
                vartype = TYPE_MAC
                cmd = "%s %s %X %s" % (getpib, filename, offset, "mac")
            else:
                cmd = "%s %s %X %s %d" % (getpib, filename, offset, "data", length)
            data = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE).stdout.read()
            o = dict(name=name, key=key, offset=offset, length=length, data=data, type=vartype)
            params.append(o)
        return params

    # noinspection PyMethodMayBeStatic
    def read_paramconfig(self, paramconfig, csvlayout):
        listofhfid = [
            "statinfo_manufacturer_sta_hfid",
            "statinfo_manufacturer_avln_hfid",
            "statinfo_user_sta_hfid",
            "statinfo_user_avln_hfid",
            "odm_private_string",
        ]
        params = []
        if csvlayout and paramconfig:
            csvlayout.seek(0)
            paramconfig.seek(0)
            for line in csvlayout.readlines():
                line = line[:-1]
                if line.startswith("Descriptor") and line.endswith("Flashoffset"):
                    continue
                vartype = TYPE_DATA
                p = Parameter(line)
                if p.name in listofhfid:
                    vartype = TYPE_HFID
                param = dict(name=p.name, key=p.key, offset=p.offset, length=p.bytes, data=None, type=vartype)
                params.append(param)
            for i, param in enumerate(params):
                name, offset, length, vartype = param["name"], param["offset"], param["length"], param["type"]
                paramconfig.seek(offset)
                buf = paramconfig.read(length)
                if vartype is not TYPE_HFID:
                    buf = "".join(map(lambda d: "{:02X}".format(ord(d)), list(buf)))
                else:
                    # strip null characters.
                    buf = "".join(filter(lambda x: ord(x) != 0, list(buf)))
                param["data"] = buf
                params[i] = param
        return params

    # noinspection PyMethodMayBeStatic
    def extract_from_ggl(self, filename):
        tar = tarfile.open(filename)
        paramconfig = csvlayout = None
        for member in tar.getmembers():
            if member.name.startswith("paramconfig"):
                paramconfig = tar.extractfile(member)
            elif member.name.endswith(".csv"):
                csvlayout = tar.extractfile(member)
        return paramconfig, csvlayout

    def dump_raw(self):
        args = self.args
        filename = args.f
        dump_hex(filename)
        return

    # noinspection PyMethodMayBeStatic
    def dump_parameters(self, params, displayall=False):
        if displayall:
            print json.dumps(params, indent=2)
        else:
            linelength = 64
            names = [param["name"] for param in params]
            width = len(max(names, key=len))
            for param in params:
                data = param["data"]
                for i in range(0, len(data), linelength):
                    name = param["name"] if i == 0 else ""
                    print name.ljust(width, " "), data[i:i + linelength]
        pass

    def dump_pib(self):
        args = self.args
        filename, getpib, layout, displayall = args.f, args.g, args.l, args.a
        params = self.read_pib_file(filename, getpib, layout)
        self.dump_parameters(params, displayall)
        return

    def dump_ggl(self):
        args = self.args
        filename, layout, displayall = args.f, args.l, args.a
        paramconfig = csvlayout = None
        if tarfile.is_tarfile(filename):
            paramconfig, csvlayout = self.extract_from_ggl(filename)
        else:
            if layout is None:
                print "".ljust(80, "=")
                print "the file [{:s}] is not a tar file.".format(filename)
                print "if you specified a paramconfig.bin, the layout file (.csv) is required."
                print "please specify a valid tar file or a layout file (.csv) for paramconfig.bin."
                print "".ljust(80, "=")
                print args_parser.parse_args(["dump", "ggl", "-h"])
            else:
                paramconfig, csvlayout = open(filename, "r"), open(layout, "r")

        if paramconfig is not None and csvlayout is not None:
            params = self.read_paramconfig(paramconfig, csvlayout)
            self.dump_parameters(params, displayall)
            if type(paramconfig) is file:
                paramconfig.close()
            if type(csvlayout) is file:
                csvlayout.close()

        return

    def compare(self, params1, params2):
        args = self.args
        brief, output = args.b, args.o
        difflist = []
        for param1 in params1:
            key = param1["key"]
            matched = filter(lambda x: x["key"] == key, params2)
            if matched:
                param2 = dict(matched[0])
                if param1["data"] != param2["data"]:
                    difflist.append(dict(param1=param1, param2=param2))
            else:
                difflist.append(dict(param1=param1, param2=None))
        for param2 in params2:
            key = param2["key"]
            matched = filter(lambda x: x["key"] == key, params1)
            if not matched:
                difflist.append(dict(param1=None, param2=param2))

        for d in difflist:
            separator_width = 80
            name = d["param1"]["name"] if d["param1"] else d["param2"]["name"]
            vartype = d["param1"]["type"] if d["param1"] else d["param2"]["type"]
            offset = d["param1"]["offset"] if d["param1"] else d["param2"]["offset"]
            length = d["param1"]["length"] if d["param1"] else d["param2"]["length"]
            data1 = d["param1"]["data"] if d["param1"] else ""
            data2 = d["param2"]["data"] if d["param2"] else ""

            print "".center(separator_width, "=")
            print "{:04X} {:4d} {:s}".format(offset, length, name)
            if vartype == TYPE_DATA:
                line_data = 16
                line_data_width = line_data * 2

                remainder = offset % line_data
                offset -= remainder
                data1 = data1.rjust((length + remainder) * 2, " ")
                data2 = data2.rjust((length + remainder) * 2, " ")

                lines = len(data1) / line_data_width
                lines = lines if len(data1) % line_data_width is 0 else lines + 1
                for i in range(lines):
                    start = i * line_data_width
                    end = i * line_data_width + line_data_width
                    s1 = data1[start:end]
                    s2 = data2[start:end]
                    diff = (s1 != s2)
                    if not diff and brief:
                        continue
                    s1 = " ".join(s1[s:s + 2] for s in range(0, len(s1), 2))
                    s2 = " ".join(s2[s:s + 2] for s in range(0, len(s2), 2))
                    print "{:s} {:08X}: {:s}".format("-" if diff else " ", offset + start / 2, s1)
                    print "{:s} {:8s}  {:s}".format("+" if diff else " ", "", s2)

            else:
                print "-", data1
                print "+", data2

        if output:
            with open(output, 'w') as f:
                try:
                    d = json.dumps(difflist, indent=2)
                    f.write(d)
                except UnicodeDecodeError as e:
                    print e
            pass
        return

    def diff_pib(self):
        args = self.args
        filename1, filename2, getpib, layout = args.f, args.F, args.g, args.l
        params1 = self.read_pib_file(filename1, getpib, layout)
        params2 = self.read_pib_file(filename2, getpib, layout)
        self.compare(params1, params2)
        return

    def diff_ggl(self):
        args = self.args
        filename1, filename2, layout1, layout2 = args.f, args.F, args.l, args.L

        csvlayout1 = open(layout1, "r") if layout1 else None
        csvlayout2 = open(layout2, "r") if layout2 else None

        if tarfile.is_tarfile(filename1):
            paramconfig1, csvlayout1 = self.extract_from_ggl(filename1)
        else:
            paramconfig1 = open(filename1, "r")

        if tarfile.is_tarfile(filename2):
            paramconfig2, csvlayout2 = self.extract_from_ggl(filename2)
        else:
            paramconfig2 = open(filename2, "r")

        if paramconfig1 is not None and paramconfig2 is not None and csvlayout1 is not None and csvlayout2 is not None:
            params1 = self.read_paramconfig(paramconfig1, csvlayout1)
            params2 = self.read_paramconfig(paramconfig2, csvlayout2)
            self.compare(params1, params2)
            if type(paramconfig1) is file:
                paramconfig1.close()
            if type(paramconfig2) is file:
                paramconfig2.close()
            if type(csvlayout1) is file:
                csvlayout1.close()
            if type(csvlayout2) is file:
                csvlayout2.close()
        else:
            print args_parser.parse_args(["diff", "ggl", "-h"])

        return

    def run(self, args):
        self.args = args
        action = args.action
        if action is not None:
            exec "self.%s()" % action
        return


class AnotherArgumentParser(argparse.ArgumentParser):
    """
    AnotherArgumentParser is subclassed from argparse.ArgumentParser and
    overrides the method error() to print a customized message while the
    command line arguments are parsed error. it prints the error and show
    the command line help if error occurs.
    """

    def error(self, message):
        sys.stderr.write('ERROR: %s\n\n' % message)
        self.print_help()
        sys.exit(2)


def init_args_parser():
    parser = AnotherArgumentParser(description="======  PLC PARAMETER TOOLBOX  ======")
    subparsers = parser.add_subparsers(title="action", help='the actions of the plc parameter toolbox')

    # create the parser for the "dump" command
    parser_dump = subparsers.add_parser("dump", help="dump the parameter file (.pib/.ggl/paramconfig.bin).")

    # create the subparser for the "dump" command
    subparsers_of_dump = parser_dump.add_subparsers(title="dump", help='the actions of dump')

    # create the parser for the "dump raw" command
    parser_dump_raw = subparsers_of_dump.add_parser("raw", help="dump the file in hex.")
    parser_dump_raw.add_argument("-f", metavar="file", required=True, help="the file to be dumped.")
    parser_dump_raw.set_defaults(action="dump_raw")

    # create the parser for the "dump pib" command
    parser_dump_pib = subparsers_of_dump.add_parser("pib", help="dump the pib file.")
    parser_dump_pib.add_argument("-a", action="store_true",
                                 help="display all information (name/offset/length/data) in json.")
    parser_dump_pib.add_argument("-f", metavar="filename", required=True, help="the pib file.")
    parser_dump_pib.add_argument("-g", metavar="getpib", required=True, help="the path of getpib.")
    parser_dump_pib.add_argument("-l", metavar="layout file", required=True,
                                 help="the xml file describes the pib offset.")
    parser_dump_pib.set_defaults(action="dump_pib")

    # create the parser for the "dump ggl" command
    parser_dump_ggl = subparsers_of_dump.add_parser("ggl", help="dump the ggl file.")
    parser_dump_ggl.add_argument("-a", action="store_true",
                                 help="display all information (name/offset/length/data) in json.")
    parser_dump_ggl.add_argument("-f", metavar="filename", required=True, help="the ggl or paramconfig file.")
    parser_dump_ggl.add_argument("-l", metavar="layout file (optional)",
                                 help="the csv file describes parameter offset of paramconfig file.")
    parser_dump_ggl.set_defaults(action="dump_ggl")

    # create the parser for the "diff" command
    parser_diff = subparsers.add_parser("diff", help="compare the parameter files (.pib/.ggl/paramconfig.bin).")

    # create the subparser for the "dump" command
    subparsers_of_diff = parser_diff.add_subparsers(title="diff", help='the actions of diff')

    # create the parser for the "diff pib" command
    parser_diff_pib = subparsers_of_diff.add_parser("pib", help="compare the pib files.")
    parser_diff_pib.add_argument("-f", metavar="filename", required=True, help="the pib file.")
    parser_diff_pib.add_argument("-F", metavar="filename", required=True, help="another pib file to compare.")
    parser_diff_pib.add_argument("-g", metavar="getpib", required=True, help="the path of getpib.")
    parser_diff_pib.add_argument("-l", metavar="layout file", required=True,
                                 help="the xml file describes the pib offset.")
    parser_diff_pib.add_argument("-o", metavar="output", help="save difference to output file (in json).")
    parser_diff_pib.add_argument("-b", action="store_true", help="display in brief.")
    parser_diff_pib.set_defaults(action="diff_pib")

    # create the parser for the "diff ggl" command
    parser_diff_ggl = subparsers_of_diff.add_parser("ggl", help="compare the ggl files.")
    parser_diff_ggl.add_argument("-f", metavar="filename", required=True, help="the ggl or paramconfig file (src).")
    parser_diff_ggl.add_argument("-F", metavar="filename", required=True,
                                 help="another ggl or paramconfig file (dst) to compare.")
    parser_diff_ggl.add_argument("-l", metavar="layout file (optional)",
                                 help="the csv file describes parameter offset of paramconfig file (src).")
    parser_diff_ggl.add_argument("-L", metavar="layout file (optional)",
                                 help="the csv file describes parameter offset of paramconfig file (dst).")
    parser_diff_ggl.add_argument("-o", metavar="output", help="save difference to output file (in json).")
    parser_diff_ggl.add_argument("-b", action="store_true", help="display in brief.")
    parser_diff_ggl.set_defaults(action="diff_ggl")

    return parser


def main():
    global args_parser
    args_parser = init_args_parser()
    args = args_parser.parse_args()

    pptb = PlcParameterToolbox()
    pptb.run(args)
    pass


################################################################################

if __name__ == "__main__":
    main()
    pass
