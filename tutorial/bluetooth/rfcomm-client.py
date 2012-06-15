import bluetooth

bd_addr = "F8:DB:7F:18:E1:D5"

port = 1

sock=bluetooth.BluetoothSocket( bluetooth.RFCOMM )
sock.connect((bd_addr, port))
sock.send("hello!!")

sock.close()
