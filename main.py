# Import the designated libraries
import os
import time
import string
import random
import socket
import wmi
import getpass
import paramiko
import requests
from bs4 import BeautifulSoup
from datetime import datetime
from twilio.rest import Client


def get_hostname_ip():  # Function that obtains the host name and ip address of the machine being used to log in
    try:
        host_name = socket.gethostname()
        host_ip = socket.gethostbyname(host_name)
    except:
        host_name = "NULL"
        host_ip = "NULL"
    return host_name, host_ip


def menu():     # Function that displays the standard menu for non-admin users
    logged_in = ""
    while True:
        os.system('cls')
        print("Logged in as: " + logged_in)
        print("\nMenu\n-----------------------------------")
        print("1) Login")
        print("2) Create account")
        print("3) Log out")
        print("4) Exit")
        choice = input("\n>> ")
        if choice == "1":
            logged_in = cred_check()
        elif choice == "2":
            logged_in = register_user()
        elif choice == "3":
            if logged_in != "":
                logged_in = log_out()
            else:
                print("No user is logged in!\n")
        elif choice == "4":
            quit()
        else:
            print("Please enter a valid choice.")


def menu_admin(logged_in):      # Function that displays the admin specific selection menu
    while True:
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
            logged_in = register_user()
        elif choice == "3":
            if logged_in != "":
                logged_in = log_out()
                menu()
            else:
                print("No user is logged in!\n")
        elif choice == "4":
            quit()
        else:
            print("Please enter a valid choice.")


def admin_panel(logged_in):     # Function that displays the admin only menu
    while True:
        os.system('cls')
        print("Logged in as: " + logged_in + " [ADMIN]")
        print("Admin Panel\n-----------------------------------")
        print("1) Activate Process Watcher")
        print("2) SSH Connection")
        print("3) Weather Report")
        print("4) Go Back")
        choice = input("\n>> ")
        if choice == "1":   # If the user selects the option for Process Watcher
            os.system('cls')
            print("Process Watcher\n-----------------------------------")
            c = wmi.WMI()
            process_watcher = c.Win32_Process.watch_for("creation")
            while True:
                new_process = process_watcher()
                process_owner = new_process.GetOwner()
                process_owner = "%s\\%s" % (process_owner[0],process_owner[2])
                executable = new_process.ExecutablePath
                pid = new_process.ProcessId
                parent_pid = new_process.ParentProcessId
                print("Process owner: ", process_owner)
                print("Executable: ", executable)
                print("PID: ", pid)
                print("Parent PID: ", parent_pid, '\n')
        elif choice == "2":     # If the user selects the option for an SSH connection
            os.system('cls')
            print("SSH Connection\n-----------------------------------")
            success = False
            while success == False:
                ip = input(str("Connect to: "))
                print("\nAttempting connection to host " + ip + "\n")
                os.sleep(3)
                if ip == "192.168.1.1":
                    username = input("Username: ")
                    password = getpass.getpass()
                    success = True
                    print("Attempting log in to " + ip)
                    os.sleep(3)
            ssh = paramiko.SSHClient()
            ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            ssh.connect(ip, port=22, username=username, password=password, look_for_keys=False, timeout=None)
            os.system('cls')
            print("Shell established with host " + ip)
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
                    print("\nLog off successful.")
                    time.sleep(2)
                    admin_panel(logged_in)
                else:
                    stdin, stdout, stderr = ssh.exec_command(command)
                    b = stdout.readlines()
                    print(b)
                    stdout.channel.close()
        elif choice == "3":     # If the user selects the option to obtain a weather report
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


def cred_check():   # Function to handle user login
    os.system('cls')
    failed_login = 0
    logins = dict()
    success = False
    while True:
        while success == False:
            os.system('cls')
            print("User log in\n-----------------------------------")
            uname_login = str(input("Username: "))
            pwd_login = getpass.getpass()
            print("\nValidating credentials..")
            time.sleep(2)
            with open('locked_accounts.txt', 'r') as f:
                locked_accounts = f.read().splitlines()
            if uname_login in locked_accounts:
                host_name, host_ip = get_hostname_ip()
                with open('login_history.txt', 'a') as f:
                    f.write(uname_login + ", " + host_name + ", " + host_ip + ", " + str(datetime.now()) + ", " + "LOCKED ACCOUNT" + "\n")
                f.close()
                print("\nSorry, but your account is locked. Please contact an administrator to unlock your account.")
                time.sleep(3)
                menu()
            elif logins[uname_login] == pwd_login:
                success = True
                code = two_factor()
                print("\nPlease enter the code sent to your mobile device, or type EXIT to go back.")
                twof_code = str(input(">> "))
                if twof_code == "EXIT":
                    menu()
                elif twof_code == code:
                    host_name, host_ip = get_hostname_ip()
                    with open('login_history.txt', 'a') as f:
                        f.write(uname_login + ", " + host_name + ", " + host_ip + ", " + str(datetime.now()) + ", " + "SUCCESS" + "\n")
                    f.close()
                    logged_in = uname_login
                    print("\nValidating credentials..\n")
                    time.sleep(2)
                    admin = admin_check(logged_in)
                    if admin == True:
                        menu_admin(logged_in)
                    else:
                        return logged_in
                else:
                    host_name, host_ip = get_hostname_ip()
                    with open('login_history.txt', 'a') as f:
                        f.write(uname_login + ", " + host_name + ", " + host_ip + ", " + str(datetime.now()) + ", " + "FAILED" + "\n")
                    f.close()
                    time.sleep(3)
                    failed_login += 1
                    print("\nLogin failed. Attempt ", failed_login, " of 3\n")
                    time.sleep(3)
                    success = False
                    if failed_login == 3:
                        with open('locked_accounts.txt', 'a') as f:
                            f.write(uname_login + "\n")
                        f.close()
            else:
                host_name, host_ip = get_hostname_ip()
                with open('login_history.txt', 'a') as f:
                    f.write(uname_login + ", " + host_name + ", " + host_ip + ", " + str(datetime.now()) + ", " + "FAILED" + "\n")
                f.close()
                failed_login += 1
                print("\nLogin failed.\n")
                time.sleep(3)
                success = False
                if failed_login == 3:
                    with open('locked_accounts.txt', 'a') as f:
                        f.write(uname_login + "\n")
                    f.close()


def two_factor(size=8, chars=string.ascii_uppercase + string.digits):   # Function to generate and send the 2 factor authentication SMS code
    code = ''.join(random.choice(chars) for _ in range(size))
    text_alert_from = +15074811128
    text_alert_to = +15074408674
    text_body = "Your code is: " + code
    client = Client("AC0969b7fcb8bf56748d697f16ef8ee16a", "aa760f3fa534876dd1dd0de36239dc08")
    client.messages.create(to=text_alert_to, from_=text_alert_from, body=text_body)
    return code


def log_out():  # Function to log the user out
    logged_in = ""
    print("\nYou have successfully logged out.\n")
    return logged_in


def register_user():    # Function to register a new user
    uname = load_file('credentials.txt')
    register_uname = uname_register(uname)
    register_pwd = pwd_register()
    print("\nValidating credentials..")
    time.sleep(2)
    with open('credentials.txt', 'a') as f:
        f.write("\n" + register_uname + "," + register_pwd)
    f.close()
    print("\nUser successfully created.")
    time.sleep(2)
    logged_in = register_uname
    return logged_in


def load_file(file_to_open):    # Function to load a file and read the lines
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


def uname_register(uname):      # Function to register a new username
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


def pwd_register():     # Function to obtain the password used for registration
    register_pwd = ""
    while register_pwd == "":
        register_pwd = getpass.getpass("Create a password: ")
        if register_pwd == "":
            print("Password cannot be null.\n")
    return register_pwd


def admin_check(logged_in):     # Function to check if the user logging in is an admin
    if logged_in == "nick":
        return True
    else:
        return False


def main():
    menu()


if __name__ == '__main__':
    main()
