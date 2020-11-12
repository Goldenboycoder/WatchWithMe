from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.firefox.firefox_binary import FirefoxBinary
import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import socket
import threading

hostip=''
port=5555
vUrl=''
Driver=''
binary=FirefoxBinary("D:\\Browsers\\FireFox\\firefox.exe")

def sync(username,address):
    vtime=Driver.execute_script("return document.getElementById('movie_player').getCurrentTime()")
    print("syncing with ",username)
    return vtime


def join(user,address):
    print(user," joined")
    return vUrl

Protocol={'JOIN':join , 'SYNC':sync}

def getIp():
        try:
            s = socket.socket( socket.AF_INET, socket.SOCK_STREAM )
            internetHost="www.google.com"
            internetHostport=80
            s.connect( ( internetHost, internetHostport ) )
            ip = s.getsockname()[0]
            s.close()
            return ip
        except :
            return False

def handleConnection(connection,address):
    with connection:
        print('Connected by {}'.format(address))
        while True:
            re = connection.recv(1024)
            req=re.decode('utf-8')
            code , data = req.split('-',1)
            response=Protocol[code.upper()](data,address)
            connection.sendall(str(response).encode('utf-8'))

def openYT(Driver,url):
    Driver.get(url)

def syncYT(Driver,htime):
    plus='+='
    mminus='-='
    seek=''
    ctime=Driver.execute_script("return document.getElementById('movie_player').getCurrentTime()")
    res= float(htime)-float(ctime)
    if res > 0:
        seek=plus+str(abs(res))
    else:
        seek=mminus+str(abs(res))
    
    Driver.execute_script('document.getElementsByTagName("video")[0].currentTime'+seek)

print("Welcome to watch together")
bType=input("Are you using Chrome or Firefox (selenium drivers  needed) c/f : ")
uType=input("Are you the host y/n : ")

if bType == 'f':
   Driver=webdriver.Firefox(firefox_binary=binary, executable_path=r"D:\\My Files\Projects\\watch to py\\geckodriver.exe")
elif bType=='c':
    Driver=webdriver.Chrome()
else:
    print('???')

if uType == 'y' :
    ip=False
    while not ip :
        ip=getIp()
        if ip:
            hostip=ip

    vUrl=input("Enter the url of the youtube video : ")
    openYT(Driver,vUrl)
    print(Driver.execute_script("return document.getElementById('movie_player').getCurrentTime()"))
    try:
        with socket.socket(socket.AF_INET,socket.SOCK_STREAM) as s:
            s.bind((hostip,port))
            s.listen()
            print("listening on port : ",port)
            while True:
                connection , address = s.accept()
                thred=threading.Thread(target=handleConnection,args=[connection , address],daemon=True)
                #uses daemon thread to be able to test, in real application proccess will keep running in background after program closes
                thred.start()
                print(Driver.execute_script("return document.getElementById('movie_player').getCurrentTime()"))
    except Exception as e:
        print(e)
else:
    hostip=input("enter the hosts ip : ")
    port=int(input("Enter hosts port : "))
    username=input("Enter username : ")
    try:
        with socket.socket(socket.AF_INET,socket.SOCK_STREAM) as s:
            s.connect((hostip,port))
            joined=False
            while True:
                if not joined :
                    req='{}-{}'.format("join",username)
                    s.sendall(req.encode('utf-8'))
                    re = s.recv(1024).decode('utf-8')
                    openYT(Driver,re)
                    joined=True
                else:
                    time.sleep(10)
                    req='{}-{}'.format("sync",username)
                    s.sendall(req.encode('utf-8'))
                    re = s.recv(1024)
                    response = re.decode('utf-8')
                    syncYT(Driver,response)
    except Exception as e:
        print(e)


    



'''
Driver.get(vUrl)
Driver.execute_script('document.getElementsByTagName("video")[0].currentTime')
time.sleep(5)
ctime=Driver.execute_script("return document.getElementById('movie_player').getCurrentTime()")
print("Video is at : {}".format(ctime))
#to change time
Driver.execute_script('document.getElementsByTagName("video")[0].currentTime+=30')
'''