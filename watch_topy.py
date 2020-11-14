from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.firefox.firefox_binary import FirefoxBinary
import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import socket
import threading
from pathlib import Path

hostip=''
port=5555
vUrl=''
Driver=''


class WatchWithMe:

    def __init__(self,hostip=None,port=None,delay=7):
        self.hostip=hostip
        self.port=port
        self.delay=delay

        self.Protocol={'JOIN':self.join , 'SYNC':self.sync}


    def sync(self,Driver,username,address):
        #sync with client by sending the current time
        vtime=Driver.execute_script("return document.getElementById('movie_player').getCurrentTime()")
        print("syncing with ",username)
        return vtime


    def join(self,user,address):
        #provided new users with the video link
        print(user," joined")
        return vUrl

    #Protocol={'JOIN':join , 'SYNC':sync}

    def getIp(self):
            try:
                s = socket.socket( socket.AF_INET, socket.SOCK_STREAM )
                internetHost="www.google.com"
                internetHostport=80
                s.connect( ( internetHost, internetHostport ) )
                ip = s.getsockname()[0]
                s.close()
                print(ip)
                return ip
            except :
                return False

    def handleConnection(self,Driver,connection,address):
        #handles client coonections and respond to requests according to the Protocol
        with connection:
            print('Connected by {}'.format(address))
            while True:
                re = connection.recv(1024)
                req=re.decode('utf-8')
                code , data = req.split('-',1)
                response=self.Protocol[code.upper()](Driver,data,address)
                connection.sendall(str(response).encode('utf-8'))

    def openYT(self,Driver,url):
        #open url
        Driver.get(url)

    def syncYT(self,Driver,htime):
        #sync client current time with the host
        plus='+='
        mminus='-='
        seek=''
        ctime=Driver.execute_script("return document.getElementById('movie_player').getCurrentTime()")
        #calculate time difference 
        res= float(htime)-float(ctime)
        if res > 0:
            seek=plus+str(abs(res))
        else:
            seek=mminus+str(abs(res))
        
        Driver.execute_script('document.getElementsByTagName("video")[0].currentTime'+seek)

    print("Welcome to watch together")
    def browserSetup(self,Driver):
        bType=input("Are you using Chrome or Firefox (selenium drivers  needed) c/f : ")
        try:
            if bType == 'f':
                filename=Path("./paths.txt")
                FirefoxPath=''
                GeckoDriverPath=''
                if filename.exists():
                    file = open(filename,'r') 
                    paths=file.readlines() 
                    file.close()
                    FirefoxPath , GeckoDriverPath= paths
                    FirefoxPath=FirefoxPath.rstrip()
                    GeckoDriverPath=GeckoDriverPath.rstrip()
                else:
                    print("please provide the paths for firefox.exe and geckodriver.exe respectively using \ \ ")
                    FirefoxPath=input("firefox.exe path : ")
                    GeckoDriverPath=input("geckodriver.exe path")
                    file = open(filename,'w')
                    file.writelines([FirefoxPath+" \n",GeckoDriverPath+" \n"])
                    file.close()

                binary=FirefoxBinary(FirefoxPath)
                Driver=webdriver.Firefox(firefox_binary=binary, executable_path=GeckoDriverPath)
                return Driver
            elif bType=='c':
                filename=Path("./Cpaths.txt")
                ChromeDriver=''
                if filename.exists():
                    file = open(filename,'r') 
                    paths=file.readline() 
                    file.close()
                    ChromeDriver= paths
                    ChromeDriver=ChromeDriver.rstrip()
                else:
                    print("please provide the paths for ChromeDriver.exe using \ \ ")
                    ChromeDriver=input("ChromeDriver.exe path : ")
                    file = open(filename,'w')
                    file.writeline(ChromeDriver+" \n")
                    file.close()
                Driver=webdriver.Chrome(ChromeDriver)
                return Driver
            else:
                print('???')
                return False
        except Exception as e:
            print(e)
            return False


    def roleInit(self,Driver,hostip,port):
        
        uType=input("Are you the host y/n : ")

        if uType == 'y' :
            ip=False
            while not ip :
                ip=self.getIp()
                if ip:
                    hostip=ip

            vUrl=input("Enter the url of the youtube video : ")
            self.openYT(Driver,vUrl)
            print(Driver.execute_script("return document.getElementById('movie_player').getCurrentTime()"))
            try:
                with socket.socket(socket.AF_INET,socket.SOCK_STREAM) as s:
                    s.bind((hostip,port))
                    s.listen()
                    print("listening on port : ",port)
                    while True:
                        connection , address = s.accept()
                        thred=threading.Thread(target=self.handleConnection,args=[Driver, connection , address],daemon=True)
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
                            #send a join request , response should be a url
                            req='{}-{}'.format("join",username)
                            s.sendall(req.encode('utf-8'))
                            re = s.recv(1024).decode('utf-8')
                            self.openYT(Driver,re)
                            joined=True
                        else:
                            #send request to sync with host , response should be host current time
                            time.sleep(7) #interval between each sync
                            req='{}-{}'.format("sync",username)
                            s.sendall(req.encode('utf-8'))
                            re = s.recv(1024)
                            response = re.decode('utf-8')
                            self.syncYT(Driver,response)
            except Exception as e:
                print(e)

