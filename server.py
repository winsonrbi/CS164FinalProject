import socket
import select
from _thread import * 
#USERS
users = { "john" : "123" , "sally" : "password" , "bill" : "root"}

def menuPrompt(s):
  s.send(bytes("Menu Options: ", "utf-8"))
  s.send(bytes("1. Chat ", "utf-8"))
  s.send(bytes("2. Change Password ", "utf-8"))
  s.send(bytes("2. Logout ", "utf-8"))

#listen forever
def receiveMessage(s):
  full_message = ''
  length = 0
  packet = s.recv(8).decode("utf-8")
  header = packet [:4]
  if(packet[4:8] == '0000'):
    #returned nothing
    return{ 'header' : header, 'length' : 0 , 'message' : 'empty_string'}
  length = int(packet [4:8])
  full_message = s.recv(length).decode("utf-8")
  return { 'header' : header , 'length' : length , 'message' : full_message}

def sendMessage(client_socket, message, options = "SHOW"):
  #packet is made here
  makePacket = ""
  if options == "SHOW":
    makePacket = "SHOW"
  if options == "HIDE":
    makePacket = "HIDE"
  if options == "DISP":
    makePacket = "DISP" 
  
  lengthString = str(len(message)).zfill(4)
  makePacket = makePacket + lengthString + message
  client_socket.send(bytes(makePacket, "utf-8"))

def login(client_socket):
  sendMessage(client_socket,"Login: ")
  

server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
#binds socket to ip and port 2715
server_socket.bind(('10.0.0.4',2715))
server_socket.listen(5)#queue of 5
#listen forever
sockets_list = [server_socket]
clients = {}
print("Server Started")

def clientthread(client_socket):
  global clients
  sendMessage(client_socket,"Login: ")
  user = receiveMessage(client_socket)
  if user is False:
    return
  if(user["message"] in users):
    clients[client_socket] =[user["message"],"OUT"]
    print("Connection from {} - {}:{} has been established!".format(user["message"],client_address[0],client_address[1]))
    sendMessage(client_socket, "Password: " , "HIDE")
  else:
    sendMessage(client_socket, "Invalid Username, Goodbyte","DISP")
    client_socket.close()  
  while(1):
      message = receiveMessage(client_socket)
      if message is False:
        print("Connection closed from {}".format(clients[client_socket][0]))
        del clients[client_socket]
        return
        continue
      if(clients[client_socket][1] == "OUT"):
        if(message["message"] == users[clients[client_socket][0]]):
          sendMessage(client_socket,"Welcome to Win-Chat","DISP")
          clients[client_socket][1] = "MENU"
        else:
          sendMessage(client_socket, "Invalid Password, Goodbyte","DISP")
      if(clients[client_socket][1] == "MENU"):
        sendMessage(client_socket,"Menu: \n 1. Chat \n 2. Change Password \n 3. Logout \n")
        clients[client_socket][1] = "MENU_CHOICE"
      if(clients[client_socket][1] == "MENU_CHOICE"):
        message = receiveMessage(client_socket)
        if(message["message"] == "1"):
          clients[client_socket][1] = "CHAT"
        if(message["message"] == "2"):
          clients[client_socket][1] = "CHANGE_PASS"
        if(message['message'] == '3'):
          del clients[client_socket]
          sendMessage(client_socket, "Logging Out, Good Byte","DISP")
          client_socket.close()
          return
      if(clients[client_socket][1] == "CHANGE_PASS"):
          sendMessage(client_socket, "Enter Current Password: " , "HIDE")
          currPass = receiveMessage(client_socket)["message"]
          if(currPass == users[clients[client_socket][0]]):
            sendMessage(client_socket, "Enter New Password: " , "HIDE")
            newPass = receiveMessage(client_socket)
            users[clients[client_socket][0]] = newPass
          else:
            sendMessage(client_socket, "Wrong Password", "DISP")
          clients[client_socket][1] = "MENU"
          sendMessage(client_socket, "Hit [Enter]  to Continue")
      if(clients[client_socket][1] == "CHAT"):
        sendMessage(client_socket, "Available Clients","DISP")
    
while 1: 
  client_socket, client_address = server_socket.accept()
  start_new_thread(clientthread, (client_socket,))
    
  #display menu prompt only when user successfully logs in
  #menuPrompt(clientsocket)