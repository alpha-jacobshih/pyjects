"""
gitlog.py: git log parser.
"""
from subprocess import Popen, PIPE

GIT_COMMIT_FIELDS = ['id', 'author_name', 'author_email', 'date', 'message']
GIT_LOG_FORMAT = ['%H', '%an', '%ae', '%ad', '%s']


def git_logs(repo_path):
    global GIT_LOG_FORMAT
    log_format = '%x1f'.join(GIT_LOG_FORMAT) + '%x1e'
    p = Popen('cd %s; git log --format="%s"' % (repo_path, log_format), shell=True, stdout=PIPE)
    (logs, _) = p.communicate()
    logs = logs.strip(b'\n\x1e').split(b'\x1e')
    logs = [row.strip().split(b'\x1f') for row in logs]
    logs = [dict(zip(GIT_COMMIT_FIELDS, row)) for row in logs]
    return logs
