import socket
import json
import json,datetime
import time,random,decimal


s = socket.socket()
print("Socket Created")
s.bind(('localhost',12345))
s.listen(3)
print("waiting for connections")
c, addr = s.accept()


def create_data():
    device_id = "234"
    source = "Ban,Ind"
    dest = " Del,Ind"
    temp = 19 + float(decimal.Decimal(random.randrange(1,1999))/100)
    batlevel = float(decimal.Decimal(random.randrange(1,100))/10)
    timestamp = datetime.datetime.now()
    formatted_datetime = timestamp.strftime('%Y-%m-%d %H:%M')
    data = {
        "device_id" : device_id,
        "from" : source,
        "to" : dest,
        "temperature" : temp,
        "batterylevel" : batlevel,
        "timestamp" : formatted_datetime
     }
    return data

while True:
    try:
        print("connected with", addr)
        data = create_data()
        userdata = json.dumps(data).encode('utf-8')
        print(userdata)
        c.send(userdata)
        time.sleep(100)
    except Exception as e:
        print(e)
