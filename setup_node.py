#!/usr/bin/env python3
import sys, subprocess

def run_command(*args):
    subprocess.run(["sudo"] + list(args), check=True)

def install_packages():
    run_command("apt-get", "install", "-y", "net-tools", "nmap", "vsftpd", "python3-pip", "socat")

def setup_iptables(allowed_ips):
    run_command("iptables", "-F")
    run_command("iptables", "-A", "INPUT", "-p", "icmp", "--icmp-type", "echo-request", "-j", "DROP")
    run_command("iptables", "-A", "INPUT", "-p", "tcp", "--dport", "21", "-j", "DROP")
    if allowed_ips:
        for ip in allowed_ips:
            while True:
                delete_rule = subprocess.run(["sudo", "iptables", "-D", "INPUT", "-p", "tcp", "--dport", "21", "-s", ip], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                if delete_rule.returncode != 0:
                    break
            run_command("iptables", "-I", "INPUT", "-p", "tcp", "--dport", "21", "-s", ip, "-j", "ACCEPT")

def setup_ftp_user():
    run_command("useradd", "-m", "-d", "/home/ftp_user", "-s", "/bin/bash", "ftp_user")
    run_command("bash", "-c", "echo 'ftp_user:MyFTPPass!' | sudo chpasswd")
    subprocess.run(["sudo", "-u", "ftp_user", "--", "bash", "-c", """
            mkdir /home/ftp_user/ftp
            for i in $(seq 1 2); do
                echo "Hello World!" > /home/ftp_user/ftp/$i.txt
            done
            chmod -R a+rwx /home/ftp_user/ftp
        """])

def main():
    allowed_ips = sys.argv[1].replace(" ", "").split(",") if len(sys.argv) > 1 else []
    install_packages()
    setup_iptables(allowed_ips)
    setup_ftp_user()
    print("FTP server is ready.")

if __name__ == "__main__":
    main()
