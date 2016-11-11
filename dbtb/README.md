# dbtb (doorbell toolbox)

## dbtb (doorbell toolbox)
[dbtb.py](./dbtb.py) is a doorbell toolbox that does:
* listens to the specified port to recieve notification from the boorbell.
* send an http request to ask doorbell simulates a event to push notification.
* rest-like api testing.

#### usage
```
usage: dbtb.py [-h] {recv,test,rest} ...

====== doorbell toolbox ======

optional arguments:
  -h, --help        show this help message and exit

action:
  {recv,test,rest}  the actions of the doorbell toolbox
    recv            receive notifications sent from doorbell.
    test            simulate generating events from doorbell by sending
                    restful api.
    rest            rest-like api test.
```

```
usage: dbtb.py recv [-h] -d DEVICEIP -l LOCALIP -p PORT

optional arguments:
  -h, --help            show this help message and exit
  -d DEVICEIP, --deviceip DEVICEIP
                        device ip address.
  -l LOCALIP, --localip LOCALIP
                        local ip address.
  -p PORT, --port PORT  socket port number.
```

```
usage: dbtb.py test [-h] -d DEVICEIP [-e] [-i eventid]

optional arguments:
  -h, --help            show this help message and exit
  -d DEVICEIP, --deviceip DEVICEIP
                        device ip address.
  -e, --event           ask doorbell to send an event.
  -i eventid, --id eventid
                        event id.
```

```
usage: dbtb.py rest [-h] -d DEVICEIP -u URL [--data DATA]
                    {get,post,put,delete}

positional arguments:
  {get,post,put,delete}
                        http method.

optional arguments:
  -h, --help            show this help message and exit
  -d DEVICEIP, --deviceip DEVICEIP
                        device ip address.
  -u URL, --url URL     url.
  --data DATA           data.
```


#### example
 * start a listener
```
./dbtb.py recv --deviceip 2.10.86.193 --localip 2.10.86.8 --port 9999

00000000: 3C 65 76 65 6E 74 3E 3C 6E 61 6D 65 3E 57 41 4B  | <event><name>WAK
00000010: 45 5F 55 50 5F 50 49 52 5F 44 45 54 45 43 54 49  | E_UP_PIR_DETECTI
00000020: 4F 4E 3C 2F 6E 61 6D 65 3E 3C 64 65 73 63 72 69  | ON</name><descri
00000030: 70 74 69 6F 6E 3E 77 61 6B 65 20 75 70 20 66 72  | ption>wake.up.fr
00000040: 6F 6D 20 50 49 52 20 64 65 74 65 63 74 69 6F 6E  | om.PIR.detection
00000050: 3C 2F 64 65 73 63 72 69 70 74 69 6F 6E 3E 3C 65  | </description><e
00000060: 76 74 5F 69 64 3E 33 3C 2F 65 76 74 5F 69 64 3E  | vt_id>3</evt_id>
00000070: 3C 73 65 71 5F 6E 6F 3E 32 30 3C 2F 73 65 71 5F  | <seq_no>20</seq_
00000080: 6E 6F 3E 3C 2F 65 76 65 6E 74 3E                 | no></event>

<?xml version="1.0" ?>
<event>
        <name>WAKE_UP_PIR_DETECTION</name>
        <description>wake up from PIR detection</description>
        <evt_id>3</evt_id>
        <seq_no>20</seq_no>
</event>
```

 * ask the doorbell to simulate an event occurs and send a notification to remote peer.
```
./dbtb.py test --deviceip 2.10.86.193 --event --id=3
```

 * rest-like api testing.
```
./dbtb.py rest get --deviceip 2.10.86.193 --url /alpha/test/event --data "{'id':'3'}"
```

---
#### references
...
