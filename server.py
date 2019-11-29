import socket
import select
import in_place
from _thread import * 
#USERS
def verifyUser(userName):
  userName = "USER=" + userName
  with open("users.txt") as f:
    searchlines = f.readlines()
    for i, line in enumerate(searchlines):
      if userName in line:
        return True
  return False

def verifyPassword(userName,password):
  searchTarget = "USER=" + userName + " : " + "PASS=" + password
  with open("users.txt") as f:  
    searchlines = f.readlines()
    for i, line in enumerate(searchlines):
      if searchTarget in line:
        return True
  return False

def changePassword(userName,oldPassword,newPassword):
  searchTarget = "USER=" + userName + " : " + "PASS=" + oldPassword + '\n'
  replaceTarget = "USER=" + userName + " : " + "PASS=" + newPassword + '\n'
  with in_place.InPlace('users.txt') as fp:
    for line in fp:
      if(line == searchTarget):
        fp.write(''.join(replaceTarget))
      else:
        fp.write(''.join(c for c in line))

#listen forever
def receiveMessage(s):
  full_message = ''
  length = 0
  packet = s.recv(8).decode("utf-8")
  print(packet)
  header = packet [:4]
  if(packet[4:8] == '0000'):
    #returned nothing
    return{ 'header' : header, 'length' : 0 , 'message' : 'empty_string'}
  length = int(packet [4:8])
  full_message = s.recv(length).decode("utf-8")
  print(full_message)
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

server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
#binds socket to ip and port 2715
server_socket.bind(('10.0.0.4',2715))
server_socket.listen(5)#queue of 5
#listen forever
sockets_list = [server_socket]
clients = {}
print("Server Started")
inChat = list()

def clientthread(client_socket):
  global inChat
  global clients
  singlePass = False
  userName = None
  sendMessage(client_socket,"Login: ")
  user = receiveMessage(client_socket)
  if user is False:
    return
  if(verifyUser(user["message"])):
    clients[client_socket] =[user["message"],"OUT"]
    userName = user["message"]
    print("Connection from {} - {}:{} has been established!".format(user["message"],client_address[0],client_address[1]))
    sendMessage(client_socket, "Password: " , "HIDE")
  else:
    sendMessage(client_socket, "Invalid Username, Goodbyte","DISP")
    client_socket.close() 
    return 
  while(1):
      if(singlePass == False):
        message = receiveMessage(client_socket)
      else:
        singlePass = False
      if message is False:
        print("Connection closed from {}".format(clients[client_socket][0]))
        del clients[client_socket]
        return
        continue
      if(clients[client_socket][1] == "OUT"):
        if(verifyPassword(userName, message["message"])):
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
        elif(message["message"] == "2"):
          clients[client_socket][1] = "CHANGE_PASS"
        elif(message['message'] == '3'):
          del clients[client_socket]
          sendMessage(client_socket, "Logging Out, Good Byte","DISP")
          client_socket.close()
          return
        else:
          clients[client_socket][1] = "MENU"
          singlePass = True
          continue
      if(clients[client_socket][1] == "MENU"):
        continue

  
      if(clients[client_socket][1] == "CHANGE_PASS"):
          sendMessage(client_socket, "Enter Current Password: " , "HIDE")
          currPass = receiveMessage(client_socket)["message"]
          if(verifyPassword(userName,currPass)):
            sendMessage(client_socket, "Enter New Password: " , "HIDE")
            newPass = receiveMessage(client_socket)
            changePassword(userName,currPass,newPass["message"])
          else:
            sendMessage(client_socket, "Wrong Password", "DISP")
          clients[client_socket][1] = "MENU"
          sendMessage(client_socket, "Hit [Enter]  to Continue")
      if(clients[client_socket][1] == "CHAT"):
        sendMessage(client_socket, "Available Clients","DISP")
        combineString = ''
        i = 0
        for key,value in clients.items():
          i = i + 1
          combineString = combineString + str(i) + ". "  +value[0]  + " \n"
        sendMessage(client_socket,combineString,"DISP")
        inChat.append(client_socket)
        clients[client_socket][1] = "MESSENGER"

      if(clients[client_socket][1] == "MESSENGER"):
          sendMessage(client_socket, "Enter Message(or :update): ")
          messsage = receiveMessage(client_socket)
          print( "WHAT I RECEIVED: " + message["message"])
          message = receiveMessage(client_socket)
          print(message)
          if(message["message"] == ":update"):
            continue
          for user_socket in inChat:
            if( client_socket != user_socket):
              sendMessage(user_socket, message['message'])
            
while 1: 
  client_socket, client_address = server_socket.accept()
  start_new_thread(clientthread, (client_socket,))
    
  #display menu prompt only when user successfully logs in
  #menuPrompt(clientsocket)
