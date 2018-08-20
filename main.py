import getpass
import os
import time
import string
import random
import socket
import paramiko
import requests
from bs4 import BeautifulSoup
from datetime import datetime
from twilio.rest import Client


def get_hostname_ip():
    try:
        host_name = socket.gethostname()
        host_ip = socket.gethostbyname(host_name)
    except:
        host_name = "NULL"
        host_ip = "NULL"
    return host_name, host_ip


def menu():                                                         #displays the standard not-admin menu
    logged_in = ""                                                  #initializes the logged_in variable which will will act persistantly
    while True:                                                     #means the loop will run until manual stoppage
        os.system('cls')                                            #clears the terminal screen to keep things clean
        print("Logged in as: " + logged_in)                         #prints menu text
        print("\nMenu\n-----------------------------------")                                             #prints menu text
        print("1) Login")                                           #prints menu text
        print("2) Create account")                                  #prints menu text
        print("3) Log out")                                         #prints menu text
        print("4) Exit")                                            #prints menu text
        choice = input("\n>> ")                                     #line used for user input
        if choice == "1":                                          #if user selects option 1
            logged_in = cred_check()                                #calls the cred_check function to log a user in
        elif choice == "2":                                        #if user selects option 2
            logged_in = register_user()                             #calls the register_user function to create a new user
        elif choice == "3":                                        #if user selects option 3
            if logged_in != "":                                    #checks if the logged_in variable is NOT null
                logged_in = log_out(logged_in)                               #calls the log_out function to log the user out
            else:                                                   #if the logged_in variable IS null
                print("No user is logged in!\n")                    #prints out that the user cannot log out since they aren't logged in
        elif choice == "4":                                        #if user selects option 4
            quit()                                                  #quits the program
        else:                                                       #if the user enters anything that 1-4
            print("Please enter a valid choice.")                   #prints out error message


def menu_admin(logged_in):                                          #displays admin menu
    while True:                                                     #means the loop will run until manual stoppage
        os.system('cls')
        print("Logged in as: " + logged_in + " [ADMIN]")
        print("Menu\n-----------------------------------")
        print("1) Admin panel")
        print("2) Create account")
        print("3) Log out")
        print("4) Exit\n")
        choice = input(">> ")
        if choice == "1":
            admin_panel(logged_in)
        elif choice == "2":
            logged_in = register_user(logged_in)
        elif choice == "3":
            if logged_in != "":
                logged_in = log_out(logged_in)
                menu(logged_in)
            else:
                print("No user is logged in!\n")
        elif choice == "4":
            quit()
        else:
            print("Please enter a valid choice.")


def admin_panel(logged_in):
    while True:                                                     #means the loop will run until manual stoppage
        os.system('cls')
        print("Logged in as: " + logged_in + " [ADMIN]")
        print("Admin Panel\n-----------------------------------")
        print("1) Activate Process Watcher")
        print("2) SSH Connection")
        print("3) Weather Report")
        print("4) Go Back")
        choice = input("\n>> ")
        if choice == "1":
            os.system('cls')
            print("Process Watcher\n-----------------------------------")
            c = wmi.WMI()
            process_watcher = c.Win32_Process.watch_for("creation")
            while True:
                new_process = process_watcher()
                proc_owner = new_process.GetOwner()
                proc_owner = "%s\\%s" % (proc_owner[0],proc_owner[2])
                executable = new_process.ExecutablePath
                cmdline = new_process.CommandLine
                pid = new_process.ProcessId
                parent_pid = new_process.ParentProcessId
                print("Process owner: ", proc_owner)
                print("Executable: ", executable)
                print("PID: ", pid)
                print("Parent PID: ", parent_pid, '\n')
        elif choice == "2":
            os.system('cls')
            print("SSH Connection\n-----------------------------------")
            success = False
            while success == False:
                ip = input(str("Connect to: "))
                print("\nAttempting connectiion to hot " + ip + "\n")
                if ip == "192.168.1.1":
                    username = input("Username: ")
                    password = getpass.getpass()
                    success = True
            ssh = paramiko.SSHClient()
            ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            ssh.connect(ip, port=22, username=username, password=password, look_for_keys=False, timeout=None)
            os.system('cls')
            print("\nShell established with host " + ip)
            stdin, stdout, stderr = ssh.exec_command('cat /proc/version')
            b = stdout.read()
            b = b.decode()
            print(b)
            print("Enter LOG OFF to exit")
            disconnect = False
            while disconnect == False:
                command = input(str("\n>> "))
                if (command == "LOG OFF") or (command == "log off"):
                    ssh.close()
                    disconnect = True
                    print("Log off successful.")
                    time.sleep(2)
                    admin_panel(logged_in)
                else:
                    stdin, stdout, stderr = ssh.exec_command(command)
                    b = stdout.readlines()
                    print(b)
                    stdout.channel.close()
        elif choice == "3":
            os.system('cls')
            page = requests.get("https://forecast.weather.gov/MapClick.php?lat=44.85117740000004&lon=-93.42519919999995")
            soup = BeautifulSoup(page.content, 'html.parser')
            temp_sky = soup.find(id="current_conditions-summary")
            temp = temp_sky.find(class_="myforecast-current-lrg").get_text()
            sky = temp_sky.find(class_="myforecast-current").get_text()
            loc1 = soup.find(id='current-conditions')
            loc = loc1.find('div', attrs={'class': 'panel-heading'})
            location = loc.find(class_="panel-title").get_text()
            x = soup.find(id='current_conditions_detail')
            td = x.find_all('td')
            humidity = td[1].text
            wind = td[3].text
            print("Weather Report\n-----------------------------------")
            print("Location: " + location)
            print("Temperature: " + temp)
            print(sky + " sky")
            print(humidity + " humidity")
            print(wind + " wind")
            time.sleep(5)
            input("\nPress Enter to continue")
            admin_panel(logged_in)
        elif choice == "4":
            menu_admin(logged_in)
        else:
            print("\nPlease enter a valid choice.\n")


def cred_check():                                                   #checks if the supplied username and password are valid
    os.system('cls')                                                #clears the terminal screen to keep things clean
    failed_login = 0                                                #initializes the failed_login variable to 0
    logins = dict()                                                 #initializes the logins variable as a dictionary
    success = False                                                 #initializes the success variable as False
    file_pointer = open('credentials.txt', 'r')                      #opens the credentials.txt file as read-only
    for line in file_pointer:                                        #for each line in the text file
        line = str.strip(line, "\n")                                #grabs all text in the line up until the new line character
        login_info = str.split(line, ",", 2)                         #splits the string into two parts, username and password
        logins[login_info[0]] = login_info[1]                         #sets each set of values into the logins dictionary
    while True:                                                     #will run until manually terminated
        while success == False:                                     #while there is no value username
            os.system('cls')
            print("User log in\n-----------------------------------")                                            #printing menu
            uname_login = str(input("Username: "))                  #asks for user input for username
            pwd_login = getpass.getpass()                           #asks for user input for password (hidden in terminal)
            print("\nValidating credentials..")                     #printing menu
            time.sleep(2)                                           #sleeps for 2 seconds to simulate loadin
            with open('locked_accounts.txt', 'r') as f:
                locked_accounts = f.read().splitlines()
            if uname_login in locked_accounts:
                host_name, host_ip = get_hostname_ip()
                with open('login_history.txt', 'a') as f:                         #open the credentials.txt file as variable f
                    f.write(uname_login + ", " + host_name + ", " + host_ip + ", " + str(datetime.now()) + ", " + "LOCKED ACCOUNT" + "\n")         #writes the newly created username and password to the file
                f.close()
                print("\nSorry, but your account is locked. Please contact an administrator to unlock your account.")
                time.sleep(3)
                menu()
            elif logins[uname_login] == pwd_login:                   #if the supplied username matches one in the dictionary
                success = True                                      #login is successful
                code = two_factor()
                print("\nPlease enter the code sent to your mobile device, or type EXIT to go back.")  #printing menu
                twof_code = str(input(">> "))
                if twof_code == "EXIT":
                    menu()
                elif twof_code == code:
                    host_name, host_ip = get_hostname_ip()
                    with open('login_history.txt', 'a') as f:                         #open the credentials.txt file as variable f
                        f.write(uname_login + ", " + host_name + ", " + host_ip + ", " + str(datetime.now()) + ", " + "SUCCESS" + "\n")         #writes the newly created username and password to the file
                    f.close()
                    logged_in = uname_login                             #sets the logged_in (persistant) variable to the name just used to log in
                    print("\nValidating credentials..\n")                     #printing menu
                    time.sleep(2)                                       #sleeps for 2 seconds to simulate loading
                    admin = admin_check(logged_in)                      #runs the admin_check function to check if the user is an admin
                    if admin == True:                                   #if the user is an admin
                        menu_admin(logged_in)                           #returns to the admin only menu
                    else:                                               #if the user is not an admin
                        return logged_in                                #returns to the normal menu
                else:                                                   #if the correct username or password weren't given
                    host_name, host_ip = get_hostname_ip()
                    with open('login_history.txt', 'a') as f:                         #open the credentials.txt file as variable f
                        f.write(uname_login + ", " + host_name + ", " + host_ip + ", " + str(datetime.now()) + ", " + "FAILED" + "\n")         #writes the newly created username and password to the file
                    f.close()                                                       #closes the file
                    time.sleep(3)
                    failed_login += 1
                    print("\nLogin failed. Attempt ", failed_login, " of 3\n")                          #displays that the login failed
                    time.sleep(3)
                    success = False                                     #increases the failed_login counter
                    if failed_login == 3:                                  #when the failed login counter reaches 3
                        with open('locked_accounts.txt', 'a') as f:                         #open the credentials.txt file as variable f
                            f.write(uname_login + "\n")         #writes the newly created username and password to the file
                        f.close()                                             #quits executing the function
            else:                                                   #if the correct username or password weren't given
                host_name, host_ip = get_hostname_ip()
                with open('login_history.txt', 'a') as f:                         #open the credentials.txt file as variable f
                    f.write(uname_login + ", " + host_name + ", " + host_ip + ", " + str(datetime.now()) + ", " + "FAILED" + "\n")         #writes the newly created username and password to the file
                f.close()
                failed_login += 1
                print("\nLogin failed.\n")                          #displays that the login failed
                time.sleep(3)
                success = False                                     #increases the failed_login counter
                if failed_login == 3:                                  #when the failed login counter reaches 3
                    with open('locked_accounts.txt', 'a') as f:                         #open the credentials.txt file as variable f
                        f.write(uname_login + "\n")         #writes the newly created username and password to the file
                    f.close()                                            #quits executing the function


def two_factor(size=8, chars=string.ascii_uppercase + string.digits):
    code = ''.join(random.choice(chars) for _ in range(size))
    text_alert_from = "+15074811128"
    text_alert_to = "+15074408674"
    text_body = "Your code is: " + code
    client = Client("AC0969b7fcb8bf56748d697f16ef8ee16a", "aa760f3fa534876dd1dd0de36239dc08")
    client.messages.create(to=text_alert_to, from_=text_alert_from, body=text_body)
    return code


def log_out():                                                      #logs out the user
    logged_in = ""                                                  #sets the persistantly passed variable logged_in to null
    print("\nYou have successfully logged out.\n")                  #displays that the user has successfully logged out
    return logged_in                                                #returns the null variable


def register_user():                                                #creates a new user
    uname = load_file('credentials.txt')                                             #calls the load_file function to get the list of taken usernames
    register_uname = uname_register(uname)                          #calls the uname_register function and passes the list of taken usernames
    register_pwd = pwd_register()                                   #calls the pwd_register function to set a password
    print("\nValidating credentials..")                             #printing menu
    time.sleep(2)                                                   #sleeps for 2 seconds to simulate loading
    with open('credentials.txt', 'a') as f:                         #open the credentials.txt file as variable f
        f.write("\n" + register_uname + "," + register_pwd)         #writes the newly created username and password to the file
    f.close()                                                       #closes the file
    print("\nUser successfully created.")                           #printing menu
    time.sleep(2)                                                   #sleeps for 2 seconds
    logged_in = register_uname                                      #sets persistant logged_in variable to the newly logged in user
    return logged_in


def load_file(file_to_open):
    uname = []
    pwd = []
    x = 0
    array = [line.rstrip('\n') for line in open(file_to_open)]
    for pair in array:
        pair = array[x]
        n, p = pair.split(",")
        uname.append(n)
        pwd.append(p)
        x += 1
    return uname


def uname_register(uname):
    os.system('cls')
    register_uname = ""
    print("User creation\n-----------------------------------")
    while register_uname == "":
        register_uname = input("Enter desired Username: ")
        if register_uname == "":
            print("Username cannot be null.\n")
        else:
            if any(register_uname in s for s in uname):
                print("Sorry, that username is already taken.\n")
                register_uname = ""
            else:
                return register_uname


def pwd_register():
    register_pwd = ""
    while register_pwd == "":
        register_pwd = getpass.getpass("Create a password: ")
        if register_pwd == "":
            print("Password cannot be null.\n")
    return register_pwd


def admin_check(logged_in):                                         #performs an admin check
    if logged_in == "nick":                                         #if the logged_in user matches the string
        return True                                                 #returns true, meaning the user is an admin
    else:                                                           #if the logged_in user does not match the string
        return False                                                #returns false, meaning the user is not an admin


def main():
    menu()


if __name__ == '__main__':
    main()
