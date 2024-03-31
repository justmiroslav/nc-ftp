#!/usr/bin/env python3
from setup_node import run_command
import os, subprocess

def check_ip(client_ip):
    with open("credentials.txt", "r") as file:
        for line in file:
            client_ip_ = line.strip().split(" ")[0]
            if client_ip == client_ip_:
                return True
    return False

def check_credentials(client_ip, password):
    with open("credentials.txt", "r") as file:
        for line in file:
            client_ip_, password_ = line.strip().split(" ")
            if client_ip == client_ip_ and password == password_:
                return True
    return False

def main():
    client_ip = os.environ.get("SOCAT_PEERADDR", "")
    if client_ip and check_ip(client_ip):
        password = input(f"Enter key for {client_ip}: ").strip()
        action = "ACCEPT" if check_credentials(client_ip, password) else "DROP"
    else:
        action = "DROP"
    for old_action in ["ACCEPT", "DROP"]:
        while True:
            delete_rule = subprocess.run(
                ["sudo", "iptables", "-D", "INPUT", "-p", "tcp", "--dport", "21", "-s", client_ip, "-j", old_action],
                stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            if delete_rule.returncode != 0:
                break
    run_command("iptables", "-I", "INPUT", "-p", "tcp", "--dport", "21", "-s", client_ip, "-j", action)
    if action == "DROP":
        print(f"Access denied for {client_ip} due to incorrect {'Credential Key' if check_ip(client_ip) else 'IP address'}.")
    else:
        print(f"Access granted for {client_ip}.")

if __name__ == "__main__":
    main()
