"""
svninfo.py: retrieve the latest svn info.
"""
from subprocess import Popen, PIPE
from tools.log import Log

def svn_info_show_item(repo_path, item):
    p = Popen('cd %s; svn info --show-item "%s"' % (repo_path, item), shell=True, stdout=PIPE)
    (_stdout, _stderr) = p.communicate()
    s = _stdout.strip()
    return s.decode('utf8') if type(s) is bytes else s

def svn_info(repo_path):
    info = dict()
    info["revision"] = svn_info_show_item(repo_path, "revision")
    info["last-changed-date"] = svn_info_show_item(repo_path, "last-changed-date")
    info["last-changed-revision"] = svn_info_show_item(repo_path, "last-changed-revision")
    info["last-changed-author"] = svn_info_show_item(repo_path, "last-changed-author")
    info["url"] = svn_info_show_item(repo_path, "url")
    info["wc-root"] = svn_info_show_item(repo_path, "wc-root")
    return info