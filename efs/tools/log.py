################################################################################

import inspect
import json
import os

################################################################################

__all__ = []


def export(obj):
    __all__.append(obj.__name__)
    return obj


################################################################################
# deco_print() is a decorator function that helps print message in the format
# that decorated funciton defines.
#
def deco_print(f):
    # noinspection PyDecorator
    @classmethod
    def d_f(cls, *args):
        msg = ''
        if Log.level != LogLevel.SILENT:
            if len(args) > 0:
                msg += f(cls)
                for i in args:
                    msg += str(i) + ' '
                pass
            print(msg)
            pass
        pass

    return d_f


################################################################################
class LogLevel:
    (SILENT, DEBUG, INFO, WARN, ERROR, FATAL) = \
        (0, 1, 2, 3, 4, 5)

    def __init__(self):
        pass

    pass


################################################################################
# class Log
#
@export
class Log:
    level = LogLevel.DEBUG

    def __init__(self):
        pass

    ################################################################################
    # _api_log() prints message in the format:
    #       filename(line number): message
    # e.g.:
    #       http.py(112): >>>>>  GET http://2.10.86.188/users/verify.cgi
    #
    @deco_print
    def _api_log(self):
        separator = '\\' if os.name is 'nt' else '/'
        line = str(inspect.stack()[3][2])
        fname = inspect.stack()[3][1].split(separator)[-1]
        return fname + '(' + line + '): '

    @classmethod
    def debug(cls, *args):
        if cls.level <= LogLevel.DEBUG:
            cls._api_log(*args)

    @classmethod
    def info(cls, *args):
        if cls.level <= LogLevel.INFO:
            cls._api_log(*args)

    @classmethod
    def warn(cls, *args):
        if cls.level <= LogLevel.WARN:
            cls._api_log(*args)

    @classmethod
    def error(cls, *args):
        if cls.level <= LogLevel.ERROR:
            cls._api_log(*args)

    ################################################################################
    # beautify_json() converts the json string in a beautiful format. it returns
    # the orginal string if it is not a valid json.
    #   jsondict, a json dictionary.
    #   beautify, beautify the json string if beautify is set true.
    #   encoding, encoding method, can get from locale.getdefaultlocale()[1].
    #
    @classmethod
    def beautify_json(cls, jsondict, beautify=True, encoding=None):
        jsonstr = ''
        try:
            if beautify:
                jsonstr = json.dumps(jsondict, indent=2, sort_keys=True, ensure_ascii=False)
            else:
                jsonstr = json.dumps(jsondict, ensure_ascii=False)
            if encoding is not None:
                jsonstr = jsonstr.encode(encoding)
        except ValueError as e:
            del e
            pass
        return jsonstr

    ################################################################################
    # beautify_jsonstr() converts the json string in a beautiful format. it returns
    # the orginal string if it is not a valid json.
    #   jsonstr, a json string.
    #   beautify, beautify the json string if beautify is set true.
    #
    @classmethod
    def beautify_jsonstr(cls, jsonstr, beautify=True):
        try:
            jsondict = json.loads(jsonstr)
            jsonstr = cls.beautify_json(jsondict, beautify)
        except ValueError as e:
            del e
            pass
        return jsonstr

    ################################################################################
    # whoami() return the name of the caller function.
    #
    @classmethod
    def whoami(cls):
        caller_name = inspect.stack()[1][3]
        return caller_name


if __name__ == '__main__':
    pass
