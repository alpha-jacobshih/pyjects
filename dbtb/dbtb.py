#! /usr/bin/env python3.5
################################################################################
"""
dbtb.py: doorbell ipcam toolbox
    features:
    * recv
      - receive notifications (udp packets on the specified port) sent from doorbell.
        . the notifications are sent in xml format. an example as below:
            <event>
                <name>WAKE_UP_BUTTON_PRESSED</name>
                <description>wake up from button pressed</description>
                <evt_id>2</evt_id>
                <seq_no>87</seq_no>
            </event>

    * test
      - simulate generating events from doorbell by sending restful api.
        . to generate an event of entering standby mode:
          http://192.168.240.1/alpha/test/event?id=1
        . to generate an event of waking up from button pressed:
          http://192.168.240.1/alpha/test/event?id=2

    * rest
      - to send http request to the doorbell to test the rest-like api.
"""
import argparse
import json
import re
import select
import socket
import string
import sys
import time
import urllib.parse
import xml.dom.minidom
from xml.parsers.expat import ExpatError
from urllib.request import http

URL_PREFIX = "/alpha"
URL_CONFIG = URL_PREFIX + "/config"
URL_TEST = URL_PREFIX + "/test"
URL_CONFIG_PEER = URL_CONFIG + "/peer"
URL_TEST_EVENT = URL_TEST + "/event"
XML_ROOT = "doorbell"
MAXDATALEN = 512


def d2x(d, root="root", pretty=False):
    """
    d2x() converts a dictionary to xml string.
    :param d: the dictionary to be converted.
    :param root: name of the xml root node.
    :param pretty: set True for pretty formatting
    :return: xml string
    """
    # FIXME:
    # insert proper indent for pretty formatting.
    op = lambda tag: ('<%s>' % tag)
    cl = lambda tag: '</%s>' % tag + ("\n" if pretty else "")
    ml = lambda v, xs: xs + op(key) + str(v) + cl(key)

    xstring = op(root) if root else ""
    xstring += "\n" if pretty else ""

    for key, value in d.items():
        vtype = type(value)
        if vtype is list:
            for val in value:
                xstring = ml(val, xstring)
        if vtype is dict: xstring = ml(d2x(value, "", pretty), xstring)
        if vtype is not list and vtype is not dict: xstring = ml(value, xstring)

    xstring += cl(root) if root else ""

    return xstring


def http_req(host, url, method="GET", data=None, **kwargs):
    """
    send an http request to the host with the method and url specified, the
    data, if any, is encoded with urlencode for GET or xml string for PUT/POST.
    :param host: host ip address.
    :param url: url.
    :param method: http method (get,post,put,delete).
    :param data: data to be sent, either xml string or a dict.
    :param kwargs: optional parameters to be encoded as data.
    :return: http reponse. an instance of http.client.HTTPResponse.
    """
    method = method.upper()
    conn = http.client.HTTPConnection(host, timeout=10)
    datadict = kwargs
    if type(data) is dict: datadict = {**datadict, **data}
    body = None
    if method == "POST" or method == "PUT":
        body = d2x(datadict, root=XML_ROOT)
    else:
        url += "?" + urllib.parse.urlencode(datadict)

    conn.request(method, url, body=body)
    return conn.getresponse()


def do_recv(peer_ipaddr, port_number):
    port_number = int(port_number)
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind((peer_ipaddr, port_number))

    try:
        while True:
            incomingdata, _, _ = select.select([sock], [], [], 1 / 10)
            if incomingdata:
                data, addr = sock.recvfrom(MAXDATALEN)
                buf = data
                offset = 0
                for i in range(0, len(data), 16):
                    str_hex = " ".join("{:02X}".format(c) for c in buf[:16])
                    str_asc = "".join(
                        chr(c) if chr(c) in string.printable and chr(c) not in string.whitespace else '.' for c in
                        buf[:16])
                    print("%s" % "{:08x}: {:48s} | {}".format(offset + i, str_hex, str_asc))
                    buf = buf[16:]
                print()

                s = re.sub(u"[\x00-\x08\x0b-\x0c\x0e-\x1f]+", u"", data.decode("utf-8"))
                try:
                    xmldom = xml.dom.minidom.parseString(s)
                    print(xmldom.toprettyxml())
                    print()
                except ExpatError as _:
                    pass
            time.sleep(100 / 1000)
    except KeyboardInterrupt as _:
        pass


def config_peer(deviceip, localip, port):
    http_req(deviceip, URL_CONFIG_PEER, ipaddr=localip, port=port)


class DoorbellToolbox:
    args = None

    def __init__(self):
        pass

    def recv(self):
        args = self.args
        config_peer(args.deviceip, args.localip, args.port)
        do_recv(args.localip, args.port)

    def test(self):
        args = self.args
        if args.event:
            http_req(args.deviceip, URL_TEST_EVENT, id=args.id)

    def rest(self):
        args = self.args
        host = args.deviceip
        url = args.url
        method = args.method
        data = None if args.data is None else json.loads(args.data.replace("'", '"'))
        resp = http_req(host, url, method, data, something="what's happened")
        print("%s: %s %s %s" %(method, host, url, data))
        print("HTTP %d\n%s" %(resp.status, resp.read().decode("utf8")))

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
        sys.stderr.write('\n[ERROR] %s\n\n' % message)
        self.print_help()
        sys.exit(2)


def init_args_parser():
    parser = AnotherArgumentParser(description="======  doorbell toolbox  ======")
    subparsers = parser.add_subparsers(title="action", help='the actions of the doorbell toolbox')

    # create the parser for the "recv" command
    parser_recv = subparsers.add_parser("recv", help="receive notifications sent from doorbell.")
    parser_recv.add_argument("-d", "--deviceip", required=True, help="device ip address.")
    parser_recv.add_argument("-l", "--localip", required=True, help="local ip address.")
    parser_recv.add_argument("-p", "--port", required=True, help="socket port number.")
    parser_recv.set_defaults(action="recv")

    # create the parser for the "test" command
    parser_test = subparsers.add_parser("test", help="simulate generating events from doorbell by sending restful api.")
    parser_test.add_argument("-d", "--deviceip", required=True, help="device ip address.")
    parser_test.add_argument("-e", "--event", action="store_true", default=False, help="ask doorbell to send an event.")
    parser_test.add_argument("-i", "--id", metavar="eventid", help="event id.")
    parser_test.set_defaults(action="test")

    # create the parser for the "rest" command
    parser_rest = subparsers.add_parser("rest", help="rest-like api test.")
    parser_rest.add_argument("method", choices=["get", "post", "put", "delete"], help="http method.")
    parser_rest.add_argument("-d", "--deviceip", required=True, help="device ip address.")
    parser_rest.add_argument("-u", "--url", required=True, help="url.")
    parser_rest.add_argument("--data", help="data.")
    parser_rest.set_defaults(action="rest")
    return parser


def main():
    global args_parser
    args_parser = init_args_parser()
    args = args_parser.parse_args(sys.argv[1:])

    dbtb = DoorbellToolbox()
    dbtb.run(args)


################################################################################

if __name__ == "__main__":
    main()
    pass
