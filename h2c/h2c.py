#! /usr/bin/env python3.5
################################################################################
"""
h2c.py: header file to c file generator.
    generates c source files from the header files.
"""
import os
import sys
import argparse
import re

H2C_HEADER = "h2c.h"
C_CODE_TEMPLATE = """
%s {
    %s ret = (%s) 0;
    /*
     * FIXME: implement the function here.
     */
    return ret;
}
"""


class H2C:
    args = None
    files = []

    def __init__(self):
        pass

    @staticmethod
    def read_header_file(filepath):
        buffer = None
        try:
            with open(filepath, "r") as f:
                buffer = f.read()
        except IOError as e:
            print(e)
            pass
        return buffer

    @staticmethod
    def remove_comment(buffer):
        pattern = re.compile(r"/\*+.*\*+/", re.MULTILINE)
        """
        FIXME:
            the pattern /\*+.*\*+/ applies to the comment in the
            same line only, it does not match the multi-line comment.

            the pattern /\*.[^/]*\*(?=/)/ matches the multi-line that
            contain without the slash. it does not match if there is
            slash in comment, i.e. /** on/off **/
        """
        match = pattern.findall(buffer)
        if match:
            buffer = pattern.sub('', buffer)
        return buffer

    @staticmethod
    def is_header_file(filename):
        ex = r"\w+[\w+\.]*\.h$"
        pattern = re.compile(ex)
        match = pattern.match(filename)
        return match is not None

    @staticmethod
    def get_function_declarations(header):
        # find function declarations
        pattern = re.compile(r"\s*[\w\s\*]+\([\w\s\*,\.]*\)\s*;", re.MULTILINE)
        declarations = pattern.findall(header)
        for i in range(0, len(declarations)):
            # trim the leading and trailing spaces
            funcdecl = declarations[i].strip()
            # take off the extern declaration.
            declarations[i] = re.sub(r"extern\s", '', funcdecl)
        return declarations

    @staticmethod
    def get_function_prototype(funcdecl):
        # function prototype contains return type and function name.
        # split the return type and function name into group.
        pattern = re.compile(r"(\w+\s*\**) *(\w+\([\w\s\*,\.]*\))", re.MULTILINE)
        match = pattern.match(funcdecl)
        if match:
            prototype = match.group(0).strip()
            return_type = match.group(1).strip()
            # take off the semicolon, the statement terminator.
            prototype = re.sub(r";$", '', prototype)
            return {"prototype": prototype, "return_type": return_type}
        else:
            return None

    @staticmethod
    def get_c_filename(filename):
        pattern = re.compile(r"([\w+/\\\.]*)\.(h$)")
        match = pattern.match(filename)
        c_filename = "%s.c" % match.group(1) if match else None
        return c_filename

    def generate_include_header(self):
        lines = []
        for file in self.files:
            lines.append('#include "%s"\n' % file["name"])
        return lines

    def generate_h2c_header(self, h2c_header):
        with open(h2c_header, "w") as f:
            lines = self.generate_include_header()
            f.write("".join(lines))

    def get_function_body(self, funcdecl):
        body = ""
        func = self.get_function_prototype(funcdecl)
        if func:
            # generate the dummy code by return 0 cast with return type.
            body = C_CODE_TEMPLATE % (func["prototype"], func["return_type"], func["return_type"])
        return body

    def read_header_files(self, folder):
        for curdir, dirs, filenames in os.walk(folder):
            for filename in filenames:
                if self.is_header_file(filename):
                    filepath = os.path.join(curdir, filename)
                    buffer = self.read_header_file(filepath)
                    file = {
                        "name": filename,  # file name (foo.h)
                        "path": filepath,  # file path (/path/to/foo.h)
                        "buffer": buffer,  # original content of header file
                        "header": None,  # header without comments
                        "body": None  # c code
                    }
                    file["header"] = self.remove_comment(file["buffer"])
                    self.files.append(file)

    def generate_dummy_code(self):
        output = self.args.output
        h2c = self.args.common_header
        if not os.path.exists(output):
            os.makedirs(output)
        h2c_header = os.path.join(output, H2C_HEADER)
        if h2c:
            self.generate_h2c_header(h2c_header)

        for i, file in enumerate(self.files):
            declarations = self.get_function_declarations(file["header"])
            if len(declarations):
                self.files[i]["body"] = ""
                # generate the c file
                for funcdecl in declarations:
                    self.files[i]["body"] += self.get_function_body(funcdecl)

                c_filename = self.get_c_filename(file["name"])
                if c_filename:
                    c_filepath = os.path.join(output, c_filename)
                    with open(c_filepath, "w") as f:
                        lines = []
                        if h2c:
                            lines.append('#include "%s"\n' % H2C_HEADER)
                        else:
                            lines = self.generate_include_header()

                        f.write("".join(lines))
                        f.write("\n")
                        f.write(file["body"])

    def process(self):
        self.read_header_files(self.args.input)
        self.generate_dummy_code()

    def run(self, args):
        self.args = args
        action = args.action
        if action is not None:
            exec("self.%s()" % action)
        return


class AnotherArgumentParser(argparse.ArgumentParser):
    """
    AnotherArgumentParser is subclassed from argparse.ArgumentParser and
    overrides the method error() to print a customized message while the
    command line arguments are parsed error. it prints the error and show
    the command line help if error occurs.
    """

    def error(self, message):
        sys.stderr.write("\n[ERROR] %s\n\n" % message)
        self.print_help()
        sys.exit(2)


def init_args_parser():
    # create the parser
    parser = AnotherArgumentParser(description="======  generate c code from the header file  ======")
    parser.add_argument("-i", "--input", required=True,
                        help="folder of the header files.")
    parser.add_argument("-o", "--output", required=True,
                        help="output folder.")
    parser.add_argument("-c", "--common-header", action="store_true",
                        help="generate a header file (h2c.h) that includes all headers for source code to include.")
    parser.set_defaults(action="process")
    return parser


def main():
    global args_parser
    args_parser = init_args_parser()
    args = args_parser.parse_args()
    h2c = H2C()
    h2c.run(args)


################################################################################

if __name__ == "__main__":
    main()
    pass
