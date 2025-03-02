import requests
import selenium
from selenium import webdriver  
from selenium.common.exceptions import NoAlertPresentException  
from selenium.webdriver.common.by import By 
from selenium.common.exceptions import UnexpectedAlertPresentException
from colorama import Fore, Back, Style, init  
import os  
import time
import logging  
logging.basicConfig(level=logging.ERROR)
#隐藏错误信息，修复时明显错误时记得关掉
init()
global_driver = None
count=0
new=False
def initialize_driver(url):
    global global_driver
    global headers
    if global_driver is None:
        options = webdriver.ChromeOptions()
        options.add_experimental_option('excludeSwitches', ['enable-logging'])
        global_driver = webdriver.Chrome(options=options)
    global new
    if new==False:
        global_driver.get(url)
        need=input(Fore.RED+"Does this webpage require login?(y/n)\n")
        userdata={}
        if need=='y':
            num=int(input(Fore.GREEN+"Please tell me how many variables are required for login:"))
            for i in range(num):
                key=input(Fore.YELLOW+f"Please enter the name of the {i+1}th variable:")
                userdata[key]=i
            for key in userdata:
                userdata[key]=input(Fore.BLUE+f"Enter the value for {key}:")
            for key,value in userdata.items():
                element=global_driver.find_element(By.NAME,key)
                if element:
                    element.send_keys(value)
            submit_button = global_driver.find_element(By.NAME, 'submit')  
            submit_button.click()
        new=True
        global_driver.refresh()
    return global_driver
#This function will initialize web driver                               
def close_driver():
    global global_driver
    if global_driver is not None:
        global_driver.quit()
        global_driver = None
#This function will close web driver
##########################################################################
def change_headers():  
    alter_headers=headers.copy()
    with open(path + "\\request.txt", "r", encoding="UTF-8") as f:  
        next(f)
        for line in f:  
            if not line.strip():  
                break
            key,value = line.strip().split(":",1)  
            alter_headers[key.strip()] = value.strip()
    return alter_headers  
#This function will alter request head
##########################################################################
def hyperlink_text(url):
    try:
        text=url.split(">")[1]
        text=text.split("<")[0]
        return text
    except:
        return False
class trigger_alert():
    def click_href(driver,url):
        link_test=hyperlink_text(url)
        if link_test==False:
            return False
        try:
            link = driver.find_element(By.LINK_TEXT, link_test)
            link.click()
            return True
        except:
            return False
    #This function will search for a hyperlink by its text, and then click on that hyperlink 
    #to trigger the popup window.
    def click_input(driver,name):
        try:
            element = driver.find_element(By.NAME, name)
            element.click()
            return True
        except:
            return False
    #This function will trigger the popup window by clicking on the search box.
class check_alert():
    def GET(url,current):  
        driver = initialize_driver(url)
        try:  
            driver.get(url)
            alert = driver.switch_to.alert
            alert.accept()
            return True  
        #Directly detect the text of the popup window
        except NoAlertPresentException:
            try:
                trigger_alert.click_input(driver,current)
                alert = driver.switch_to.alert
                alert.accept()
                #First, click on a specific element, and then detect the text of the popup.
                return True
            except NoAlertPresentException:
                try:
                    trigger_alert.click_href(driver,url)
                    alert = driver.switch_to.alert
                    alert.accept()
                    #First, click on a hyperlink and then detect the text of the popup window.
                    return True
                except NoAlertPresentException:
                    return False 
    def POST(url,data,key,value):
        driver = initialize_driver(url)
        for _key,_value in data.items():
            element=driver.find_element(By.NAME,_key)
            if element:
                element.send_keys(_value)
        try: 
            submit_button = global_driver.find_element(By.NAME, 'submit')  
            submit_button.click()
            alert = driver.switch_to.alert
            alert.accept()
            return True  
        #Directly detect the text of the popup window
        except NoAlertPresentException:
            try:
                trigger_alert.click_input(driver,key)
                alert = driver.switch_to.alert
                alert.accept()
                #First, click on a specific element, and then detect the text of the popup.
                return True
            except NoAlertPresentException:
                try:
                    trigger_alert.click_href(driver,value)
                    alert = driver.switch_to.alert
                    alert.accept()
                    #First, click on a hyperlink and then detect the text of the popup window.
                    return True
                except NoAlertPresentException:
                    return False
#This function will detect whether a popup window is present by checking the text of the popup.
##########################################################################
class make_payload():
    def urlsplit(url):
        domain=url.split("?")[0]
        _url=url.split("?")[-1]
        param={}
        for val in _url.split("&"):
            param[val.split('=')[0]]=val.split('=')[-1]
            #There will retrieves the names of all variables.
        urls=[]
        for val in param.values():
            new_url=domain+'?'+_url.replace(val,'payload')
            urls.append(new_url)
        return urls
#This function will change variable of url to payload
def get_cv(url):
    url=url.split("?")[-1]
    name=url.split("=payload")[0]
    return name
#This function will retrieves name of current variable
class spider():
    def __init__(self):
        self.url=""
    def get_run(self,url):
        urls=make_payload.urlsplit(url)
        if urls is None:
            return False
        print(Fore.GREEN+"\r[+] XSS scanning......")
        for _urlp in urls:
            current_variable=get_cv(_urlp)
            for _payload in payload:
                _url=_urlp.replace("payload",_payload)
                res=check_alert.GET(_url,current_variable)
                global count
                count=count+1
                print(Fore.RED+f"\r{count}/6634 payload",end="\r")
                if res is True:
                    print(Fore.LIGHTYELLOW_EX+"\n[*] XSS Found: \n",_url)
                    next=input(Fore.LIGHTCYAN_EX+"Do you want to get next payload?(Y/N):")
                    if next=='N':
                       return True 
        return False
    def post_run(self,url,data):
        if not data:
            print(Fore.RED+"Why don't you give me a variable?:<\n")
            return False
        print(Fore.LIGHTYELLOW_EX+"\r[+] XSS scanning......")
        for key in data:
            for _payload in payload:
                data[key]=_payload
                res=check_alert.POST(url,data,key,_payload)
                global count
                count=count+1
                print(Fore.RED+f"\r{count}/6634 payload",end="\r")
                if res is True:
                    print(Fore.LIGHTBLUE_EX+f"\n[*] XSS Found:{key}={data[key]}")
                    next=input(Fore.LIGHTYELLOW_EX+"Do you want to get next payload?(Y/N):")
                    if next=='N':
                       return True 
        return False
##########################################################################
payload=[]
path=os.getcwd()
with open(path+"\\payload.txt","r",encoding="UTF-8") as f:
    for line in f:
        payload.append(line.strip())
#This part of the code reads the payload file and splits all the payload strings.
headers={
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:65.0) Gecko/20100101 Firefox/65.0",
    "Cookie": "security=high; PHPSESSID=b171pc6qicumo686s83fqfe6t5"
}
data={}
#Initializing Request Headers
def main():
    print(Fore.LIGHTBLUE_EX+"Wellcome to use the XSS seeker!\nCommand format is "+Style.RESET_ALL+Fore.RED +"request_way+url"+Style.RESET_ALL+Fore.LIGHTGREEN_EX+" and "+Style.RESET_ALL+Fore.BLUE+"split by space\n"+Style.RESET_ALL)
    global new
    while True:
        cmd=input(Fore.LIGHTBLACK_EX+"Please input command:")
        try:
            way=cmd.split(" ")[0]
            url=cmd.split(" ")[1]
        except:
            print(Fore.RED+"Error command format :c\n")
            continue
        global headers
        global count    
        count=0
        headers=change_headers()
        spi=spider()
        if way=="POST":
            num=int(input(Fore.LIGHTBLUE_EX+"please input variable num:"))
            for i in range(num):
                key=input(Fore.BLUE+f"input {i+1} variable:")
                data[key]=i
            spi.post_run(url,data)
        else:
            spi.get_run(url)
        new=False
        next=input(Fore.YELLOW+"Do you want to find next url?(Y/N)\n")
        if next=='N':
            break
    close_driver()

if __name__=='__main__':
    main()
#This is the main function.
##########################################################################