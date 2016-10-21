#! /usr/bin/env python3.5
################################################################################
"""
efs.py: elf file stats
    analyzes the specified elf files to generate the report including the code
    size, memory usage and linking libraries.
"""
import os
import re
import shutil
import sys

if __name__ == '__main__':
    # prevent python from generating compiled byte code (.pyc).
    sys.dont_write_bytecode = True

from tools.anotherargparser import AnotherArgumentParser
from tools.parsejson import parse_json
from tools.log import Log
from pyelftools.elftools.elf.elffile import ELFFile
from pyelftools.elftools.elf.dynamic import DynamicSection
from tools.gitlog import git_logs
from tools.svninfo import svn_info

################################################################################

__all__ = []


def export(obj):
    __all__.append(obj.__name__)
    return obj


################################################################################

class Project:
    class Path:
        path = {}
        root = None
        sbin = None
        lib = None

        def __init__(self, path):
            self.path = path
            self.root = path.get("root", "")
            self.sbin = self.root + path.get("sbin", "")
            self.webfs = self.root + path.get("webfs", "")
            self.cgi = self.root + path.get("cgi", "")
            self.lib = self.root + path.get("lib", "")
            pass

    class Repo:
        SVN = "svn"
        GIT = "git"
        project = None
        repo = {}
        type = None
        browse_path = None
        latest_revision = None

        def __init__(self, project, repo):
            self.project = project
            self.repo = repo
            self.type = repo.get("type", "")
            self.initialize()
            pass

        def initialize(self):
            if self.type == self.GIT:
                self.latest_revision = self.git_latest_revision(self.project.path.root)
                self.browse_path = self.git_browse_path()
            elif self.type == self.SVN:
                self.latest_revision = self.svn_latest_revision(self.project.path.root)
                self.browse_path = self.svn_browse_path()
            pass

        @staticmethod
        def git_latest_revision(project_path):
            logs = git_logs(project_path)
            latest_revision = logs[0]['id'].decode(encoding="utf-8")
            return latest_revision

        @staticmethod
        def svn_latest_revision(project_path):
            info = svn_info(project_path)
            latest_revision = info["last-changed-revision"] if "last-changed-revision" in info else ""
            return latest_revision

        def git_browse_path(self):
            repo = self.repo
            if "queries" in self.repo:
                self.repo["queries"]["h"] = self.latest_revision
            browse_path = repo.get("url", "") + "?"
            for key in repo["queries"]:
                value = repo["queries"][key]
                browse_path += key + "=" + value + ";"
            browse_path = browse_path[:-1]  # remove the last character, a semi-colon.
            return browse_path

        def svn_browse_path(self):
            repo = self.repo
            if "queries" in self.repo:
                self.repo["queries"]["rev"] = self.latest_revision
            browse_path = repo.get("url", "") + "?"
            for key in repo["queries"]:
                value = repo["queries"][key]
                browse_path += key + "=" + value + "&"
            browse_path = browse_path[:-1]  # remove the last character, an ampersand.
            return browse_path

    def __init__(self, dict_project):
        self.dict_project = dict_project
        self.path = self.Path(dict_project.get("path", {}))
        self.repo = self.Repo(self, dict_project.get("repo", {}))
        self.libraries = set()
        self.read_apps()
        self.read_libraries()

    def readelf(self, path, name, elf):
        filename = path + name
        try:
            with open(filename, 'rb') as file:
                elffile = ELFFile(file)
                if "name" not in elf:
                    elf["name"] = name
                if "description" not in elf:
                    elf["description"] = re.split('\.', name)[0]
                elf["libs"] = self.get_libraries_used_by_elf(elffile)
                summary = elf.get("summary", {})
                summary["code_size"] = self.caculate_code_size(elffile)
                summary["sections"] = {
                    "bss": self.get_section_size(elffile, ".bss"),
                    "data": self.get_section_size(elffile, ".data"),
                    "rodata": self.get_section_size(elffile, ".rodata"),
                    "text": self.get_section_size(elffile, ".text"),
                }
                elf["summary"] = summary
        except FileNotFoundError as e:
            print(e)
        return elf

    def read_apps(self):
        self.dict_project["apps"] = []
        if "sbin" in self.dict_project:
            for app in self.dict_project["sbin"]:
                self.readelf(self.path.sbin, app["name"], app)
            self.dict_project["apps"].extend(self.dict_project["sbin"])
        if "cgi" in self.dict_project:
            for app in self.dict_project["cgi"]:
                self.readelf(self.path.cgi, app["name"], app)
            self.dict_project["apps"].extend(self.dict_project["cgi"])

    def read_libraries(self):
        libs = []
        libset = self.libraries.copy()
        for libname in libset:
            lib = dict()
            elf = self.readelf(self.path.lib, libname, lib)
            if elf:
                libs.append(lib)
        self.dict_project["libs"] = sorted(libs, key=lambda x: x["name"])

    def get_libraries_used_by_elf(self, elffile):
        libs = []
        for section in elffile.iter_sections():
            if isinstance(section, DynamicSection):
                for tag in section.iter_tags():
                    if tag.entry.d_tag == 'DT_NEEDED':
                        libs.append(tag.needed)
                        if tag.needed not in self.libraries:
                            self.readelf(self.path.lib, tag.needed, dict())
                            self.libraries.add(tag.needed)
        return libs

    @staticmethod
    def caculate_code_size(elffile):
        header = elffile.header
        code_size = header['e_shoff'] + header['e_shentsize'] * header['e_shnum']
        return code_size

    @staticmethod
    def get_section_size(elffile, sec_name):
        sec = elffile.get_section_by_name(sec_name)
        size = 0
        if sec is not None:
            size = sec["sh_size"]
        return size


class ElfFileStats:
    args = None
    dict_all = None
    html_path = None
    report_path = None
    html_report = True
    trac_report = True

    def __init__(self):
        pass

    def generate_report_path(self):
        curdir = '.\\' if os.name is 'nt' else './'
        if self.html_path is None:
            self.html_path = curdir + 'html'
        if self.report_path is None:
            self.report_path = curdir + 'report'
            if not os.path.exists(self.report_path):
                os.makedirs(self.report_path)
        pass

    def generate_html_report(self, report_in_js=True):
        self.generate_report_path()
        reportjs = self.report_path + '/' + 'report.js'
        reporttemplate = self.html_path + '/' + 'report.html'
        reporthtml = self.report_path + '/' + self.dict_all["project"]["name"] + '.html'
        if report_in_js:
            shutil.copy(reporttemplate, reporthtml)
            with open(reportjs, 'w') as f:
                try:
                    d = Log.beautify_json(self.dict_all).encode('utf8').decode('utf8')
                    f.writelines(["report = ", "\n", d, ";", "\n"])
                except UnicodeDecodeError as e:
                    print(e)
        else:
            reporthtml = self.report_path + '/' + self.dict_all["project"]["name"] + '_report.html'
            with open(reporttemplate, 'r') as src, open(reporthtml, 'w') as dst:
                for line in src:
                    if "<script" in line and "src" in line and "report.js" in line:
                        d = Log.beautify_json(self.dict_all)
                        dst.writelines(["<script type='text/javascript' charset='utf-8'>", "\n"])
                        dst.writelines(["var report = ", "\n"])
                        dst.writelines([d.encode("utf8").decode("utf8"), ";", "\n"])
                        dst.writelines(["</script>", "\n"])
                    else:
                        dst.write(line)
        pass

    @staticmethod
    def trac_table_item(*args, **kwargs):
        bold = kwargs["bold"] if "bold" in kwargs else False
        redmine = kwargs["redmine"] if "redmine" in kwargs else False
        markuptd = "||" if not redmine else "|"
        markupbold = "**" if not redmine else "*"
        line = markuptd.join(map(lambda x: " " + markupbold + x + markupbold + " " if bold else x, args))
        line = "%s%s%s" % (markuptd, line, markuptd)
        return line

    def generate_trac_report(self, redmine=False):
        self.generate_report_path()
        reporttrac = self.report_path + '/' + self.dict_all["project"]["name"]
        reporttrac += '.trac' if not redmine else ".redmine"
        markuph1 = "== " if not redmine else "h1. "
        markuph3 = "=== " if not redmine else "h3. "
        with open(reporttrac, 'w') as f:
            f.writelines([
                markuph1, "Resource Allocation:", "\n", "\n",
                markuph3, "Code Size / Image Size / Memory Usage", "\n", "\n",
                ""
            ])
            line = self.trac_table_item(
                "Module / Features",
                "Code Size ^bytes^",
                "Image Size",
                "Memory Usage ^bytes^",
                "Feature Spec Flexibility",
                "Note",
                bold=True, redmine=redmine)
            f.writelines([line, "\n"])
            for app in self.dict_all["project"]["apps"]:
                summary = app["summary"] if "summary" in app else {}
                sections = summary["sections"] if "sections" in summary else {}
                name = app["name"]
                comment = summary["comment"] if "comment" in summary else " "
                note = summary["note"] if "note" in summary else " "
                code_size = " %s" % "{:,}".format(summary["code_size"]) if "code_size" in summary else "-"
                image_size = " %s" % "{:,}".format(summary["image_size"]) if "image_size" in summary else "-"
                if all(k in sections for k in ("bss", "data", "rodata", "text")):
                    memory_usage = sections["bss"] + sections["data"] + sections["rodata"] + sections["text"]
                    memory_usage = " %s" % "{:,}".format(memory_usage)
                else:
                    memory_usage = " %d" % 0
                line = self.trac_table_item(name, code_size, image_size, memory_usage, comment, note, redmine=redmine)
                f.writelines([line, "\n"])

            f.writelines([
                "----", "\n",
                ""
            ])
        pass

    def process(self):
        args = self.args
        jsonfile = args.project
        genhtml = args.output_html
        genjs = args.output_js
        gentrac = args.output_trac
        genredmine = args.output_redmine
        dictall = self.dict_all = parse_json(jsonfile)
        if not dictall:
            print('cannot load the json file: %s' % jsonfile)
            return

        if "project" not in dictall:
            print('cannot find "project" node in the json file: %s' % jsonfile)
            return

        dictproject = dictall["project"]
        project = Project(dictproject)
        dictproject["repo"]["revision"] = project.repo.latest_revision
        dictproject["repo"]["browse_path"] = project.repo.browse_path

        if genhtml:
            self.generate_html_report(report_in_js=False)
        if genjs:
            self.generate_html_report()
        if gentrac:
            self.generate_trac_report()
        if genredmine:
            self.generate_trac_report(redmine=True)

        return

    def run(self, args):
        self.args = args
        action = args.action
        if action is not None:
            exec("self.%s()" % action)
        return

    pass


def init_args_parser():
    # create the parser
    parser = AnotherArgumentParser(description="======  ELF file stats  ======")
    parser.add_argument("-p", "--project", metavar="filename", required=True,
                        help="a json file describes the project configuration.")
    parser.add_argument("-t", "--output-trac", action="store_true", default=False,
                        help="generate the report in trac format.")
    parser.add_argument("-r", "--output-redmine", action="store_true", default=False,
                        help="generate the report in redmine format.")
    parser.add_argument("-j", "--output-js", action="store_true", default=False,
                        help="generate the report in a javascript file.")
    parser.add_argument("-a", "--output-html", action="store_true", default=False,
                        help="generate the report in an html file.")
    parser.set_defaults(action="process")
    return parser


def main():
    global args_parser
    args_parser = init_args_parser()
    args = args_parser.parse_args()
    efs = ElfFileStats()
    efs.run(args)


################################################################################

if __name__ == "__main__":
    main()
    pass
