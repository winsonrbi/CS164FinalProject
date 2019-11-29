import socket
import getpass

def receiveMessage(s):
  full_message = ''
  length = 0
  packet = s.recv(8).decode("utf-8")
  header = packet [:4]
  length = int(packet [4:8])
  full_message = s.recv(length).decode("utf-8")
  return { 'header' : header , 'length' : length , 'message' : full_message}

def sendMessage(client_socket, message, options = "SHOW"):
  #packet is made here
  makePacket = ""
  if options == "SHOW":
    makePacket = "SHOW"

  lengthString = str(len(message)).zfill(4)
  makePacket = makePacket + lengthString + message
  print(makePacket)
  client_socket.send(bytes(makePacket, "utf-8"))

 
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.connect(('10.0.0.4',2715))
#client_socket.setblocking(False)
while True:
  packet = receiveMessage(client_socket)
  sendVal = None
  if(packet["header"] == "SHOW"):
   sendVal =  input(packet["message"])
  elif (packet["header"] == "DISP"):
    print(packet["message"])
  else:
    sendVal = getpass.getpass(packet["message"])
  if( (sendVal is not None)): 
    sendMessage(client_socket,sendVal)
