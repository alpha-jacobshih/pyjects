#! /usr/bin/env python3.5
################################################################################
"""
hamu.py: html archives merge utility. to merge html/css/js files into a single html file.

author: jacob_shih
date: 12/02/2016 11:13:18
"""

import argparse
import sys
from html.parser import HTMLParser

LF = '\r'
LFCR = '\r\n'

class HtmlMerger(HTMLParser):
    def error(self, message):
        pass

    tag = None
    content = ""

    def __init__(self):
        HTMLParser.__init__(self, convert_charrefs=True)

    def expand_file(self, filepath):
        with open(filepath, "r") as f:
            content = f.read()
            self.content += content

    def expand_css(self, filepath):
        self.content += "%s%s%s" % (LFCR, "<style type='text/css'>", LFCR)
        self.expand_file(filepath)
        self.content += "%s%s" % ("</style>", LFCR)

    def expand_js(self, filepath):
        self.content += "%s%s%s" % (LFCR, "<script type='text/javascript'>", LFCR)
        self.expand_file(filepath)

    @staticmethod
    def get_tag_attr(attrs, name):
        value = None
        for attr in attrs:
            if name in attr:
                value = attr[1]
        return value

    def handle_starttag(self, tag, attrs):
        self.tag = tag.lower()
        if self.tag == "script":
            self.expand_js(self.get_tag_attr(attrs, "src"))
        elif self.tag == "link" and self.get_tag_attr(attrs, "rel") == "stylesheet":
            self.expand_css(self.get_tag_attr(attrs, "href"))
        else:
            self.content += self.get_starttag_text()

    def handle_startendtag(self, tag, attrs):
        self.tag = tag.lower()
        if self.tag == "link" and self.get_tag_attr(attrs, "rel") == "stylesheet":
            self.expand_css(self.get_tag_attr(attrs, "href"))
        else:
            self.content += self.get_starttag_text()

    def handle_endtag(self, tag):
        self.content += ("</%s>" % tag)
        self.tag = None

    def handle_data(self, data):
        self.content += data

    def handle_entityref(self, name):
        self.content += ("&%s;" % name)

    def handle_charref(self, name):
        self.content += ("&#%s" % name)

    def handle_comment(self, data):
        self.content += ("<!--%s-->" % data)

    def handle_decl(self, decl):
        self.content += ("<!%s>" % decl)


class HtmlArchivesMergeUtility:
    args = None

    def __init__(self):
        pass

    def merge(self):
        args = self.args
        source = args.source
        output = args.output
        with open(source, 'r') as fsrc:
            html = fsrc.read()
            parser = HtmlMerger()
            parser.feed(html)
            with open(output, "w") as fout:
                fout.write(parser.content)

    def run(self, args):
        self.args = args
        action = args.action if "action" in args else None
        if action is not None:
            exec("self.%s()" % action)
        else:
            print(args_parser.parse_args(["-h"]))
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
    parser = AnotherArgumentParser(description="======  html merge utility  ======")
    subparsers = parser.add_subparsers(title="action", help="the actions of the html merge utility")

    # create the parser for the "recv" command
    parser_recv = subparsers.add_parser("merge", help="merge html/css/js files into a single html file.")
    parser_recv.add_argument("-s", "--source", required=True, help="orignal html file that links with css/js files.")
    parser_recv.add_argument("-o", "--output", required=True,
                             help="output html file including original html/css/js files.")
    # FIXME: add option 'compact' to merge the html in compact format.
    parser_recv.set_defaults(action="merge")
    return parser


def main():
    global args_parser
    args_parser = init_args_parser()
    args = args_parser.parse_args(sys.argv[1:])

    hamu = HtmlArchivesMergeUtility()
    hamu.run(args)


################################################################################

if __name__ == "__main__":
    main()
    pass
