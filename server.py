import socket
import select
import in_place
from _thread import * 
#USERS

class Mail:
  from_user = ""
  to_user = ""
  message = ""
  read = False

  def __init__(self,from_user,to_user, message):
    self.from_user = from_user
    self.to_user = to_user
    self.message = message
  def is_read(self):
    return self.read
  def get_message(self):
    return self.message
  
  def get_to_user(self):
    return self.to_user
  
  def get_from_user(self):
    return self.from_user

  def get_length(self):
    return self.length
  
  def get_display_string(self):
    display_string = ""
    if(self.read == False):
      display_string = display_string + "[UNREAD]"
      self.read = True
    display_string = display_string +  "[FROM: "+  self.from_user + "] -  " + self.message + "\n"
    return display_string

class User:
  def __init__(self, username, password):
    self.username = username
    self.password = password
    self.mailbox = []
    self.friends_list=[]
    self.friend_requests_list=[]
    self.client_socket = ""

  def add_client_socket(self,client_socket):
    self.client_socket = client_socket
  
  def add_message(self,message_packet):
    self.mailbox.append(message_packet)
  
  def add_friend(self,friend):
    self.friends_list.append(friend)
  
  def add_friend_request(self,friend_request):
    self.friend_requests.append(friend_request)

  def get_unread_message_count(self):
    count = 0
    for message in self.mailbox:
      if( message.is_read() == False):
        count+=1
    
    return count
  
  def get_friends_list(self):
    return self.friends_list

  def get_friend_requests(self):
    return self.friends_requests_list

  def get_mailbox(self):
    return self.mailbox

  def get_username(self):
    return self.username

  def get_password(self):
    return self.password
  
  def set_password(self,new_password):
    self.password = new_password

  def get_mailbox_string(self):
    display_string = ""
    for mail in self.mailbox:
      display_string = display_string + mail.get_display_string()

    return display_string

def create_users():
  user_list=[]
  
  user1 = User('john','1234')
  user_list.append(user1)
  
  user2 = User('sam','1234')
  user_list.append(user2)
  
  user3 = User('jack','pass')
  user_list.append(user3)
  
  return user_list

def verifyUser(userName):
  global user_list

  for user in user_list:
    if(user.get_username() == userName):
      return True

  return False

def verifyPassword(userName,password):
  global user_list
  
  for user in user_list:
    if(user.get_username() == userName):
      if(user.get_password() == password):
        return True
      else:
        return False

  return False

def changePassword(userName,newPassword):
  global user_list
    
  for user in user_list:
    if(user.get_username() == userName):
      user.set_password(newPassword)
      return
  return
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
  
def get_all_users():
  global user_list
  
  combineString = ""
  i = 0
  for user in user_list:
    i = i + 1
    combineString = combineString + str(i) + ". " + user.get_username() + " \n"

  return combineString

def get_user(userName):
  global user_list
  
  for user in user_list:
    print(user.get_username)
    print(userName)
    if(user.get_username() == userName):
      return user

  return False

is_online = []
user_list = create_users()
for user in user_list:
  print(user.get_username() + " " + user.get_password())
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
  try:
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
          is_online.remove(get_user(userName))
          return
          continue
        if(clients[client_socket][1] == "OUT"):
          if(verifyPassword(userName, message["message"])):
            get_user(userName).add_client_socket(client_socket)
            is_online.append(get_user(userName))
            sendMessage(client_socket,"Welcome to Win-Chat","DISP")
            clients[client_socket][1] = "MENU"
          else:
            sendMessage(client_socket, "Invalid Password, Goodbyte","DISP")
        if(clients[client_socket][1] == "MENU"):
          sendMessage(client_socket,"Menu: \n 1. Send Message \n 2. View Mailbox \n 3. Broadcast \n 4. Change Password \n 5. Logout \n Choice: ")
          clients[client_socket][1] = "MENU_CHOICE"
        if(clients[client_socket][1] == "MENU_CHOICE"):
          message = receiveMessage(client_socket)
          if(message["message"] == "1"):
            clients[client_socket][1] = "SEND_MESSAGE"
          elif(message["message"] == "2"):
            clients[client_socket][1] = "VIEW_MAILBOX"
          elif(message["message"] == '3'):
            clients[client_socket][1] = "BROADCAST"
          elif(message["message"] == "4"):
            clients[client_socket][1] = "CHANGE_PASS"
          elif(message['message'] == '5'):
            del clients[client_socket]
            sendMessage(client_socket, "Logging Out, Good Byte","DISP")
            del clients[client_socket]
            is_online.remove(get_user(userName))
            client_socket.close()
            return
          else:
            clients[client_socket][1] = "MENU"
            singlePass = True
            continue
          print("MENU CHOICE: " + message["message"])
        if(clients[client_socket][1] == "MENU"):
          continue

    
        if(clients[client_socket][1] == "CHANGE_PASS"):
            sendMessage(client_socket, "Enter Current Password: " , "HIDE")
            currPass = receiveMessage(client_socket)["message"]
            if(verifyPassword(userName,currPass)):
              sendMessage(client_socket, "Enter New Password: " , "HIDE")
              newPass = receiveMessage(client_socket)
              changePassword(userName,newPass["message"])
            else:
              sendMessage(client_socket, "Wrong Password", "DISP")
            clients[client_socket][1] = "MENU"
            sendMessage(client_socket, "Hit [Enter]  to Continue")
        if(clients[client_socket][1] == "SEND_MESSAGE"):
          sendMessage(client_socket, "USERS: ", "DISP")
          sendMessage(client_socket,get_all_users(),"DISP")
          sendMessage(client_socket,"TO: " )
          recipient = receiveMessage(client_socket)["message"]
          sendMessage(client_socket,"Message: " )
          mail_message = receiveMessage(client_socket)["message"]
          new_mail = Mail(userName,recipient,mail_message)
          try:
            target_user = get_user(recipient)
            target_user.add_message(new_mail)
            sendMessage(client_socket, "\nMessage Sent to " + recipient + "\n","DISP")
          
          except:
            sendMessage(client_socket, "\nError Occured, Try Again Later \n")
          clients[client_socket][1] = "MENU"
          singlePass = True
        
        if(clients[client_socket][1] == "VIEW_MAILBOX"):
          targetUser= get_user(userName)
          header_string = targetUser.get_username() + "'s MAILBOX - " + str(targetUser.get_unread_message_count()) + " UNREAD MESSAGES \n"
          sendMessage(client_socket,header_string,"DISP")
          targetString = targetUser.get_mailbox_string()
          sendMessage(client_socket,targetString, "DISP")
          clients[client_socket][1] = "MENU"
          sendMessage(client_socket,"Press [Enter] to Continue")
         
        if(clients[client_socket][1] == "BROADCAST"):
          sendMessage(client_socket,"------BROADCAST-----\n","DISP")
          targetString = "People Online: \n"
          i = 0
          for user in is_online:
            i = i + 1
            targetString = targetString + str(i) + ". "+ user.get_username() +"\n"
          sendMessage(client_socket,targetString,"DISP")
          sendMessage(client_socket, "Message: ")
  except:
    print("Connection was dropped")
    try:
      is_online.remove(get_user(userName))
    except:
      print("Already Removed")
while 1: 
  client_socket, client_address = server_socket.accept()
  start_new_thread(clientthread, (client_socket,))
  print("WE BACK AT IT")   
  #display menu prompt only when user successfully logs in
  #menuPrompt(clientsocket)
