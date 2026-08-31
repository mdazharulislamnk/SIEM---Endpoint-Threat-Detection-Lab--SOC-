#!/usr/bin/env python3
import time
import random
from datetime import datetime
import os

# Ensure the script is run with adequate permissions to write to auth.log
LOG_FILE = "/var/log/auth.log"

USERNAMES = ['admin', 'root', 'test', 'guest', 'oracle', 'ubuntu', 'dbadmin']
BASE_IPS = ['192.168.1.', '10.0.0.', '172.16.0.', '203.0.113.', '198.51.100.']

def generate_ip():
    base = random.choice(BASE_IPS)
    suffix = random.randint(2, 254)
    return f"{base}{suffix}"

def generate_log_entry(username, ip, pid):
    # Standard format for Debian/Ubuntu sshd auth failure
    # e.g., Aug 31 10:15:20 victim-endpoint sshd[12345]: Failed password for invalid user admin from 192.168.1.50 port 54321 ssh2
    now = datetime.now()
    timestamp = now.strftime("%b %d %H:%M:%S")
    hostname = "victim-endpoint"
    port = random.randint(30000, 65000)
    
    # Randomly inject "invalid user" for non-existent users
    if username in ['root', 'ubuntu']:
        msg = f"Failed password for {username} from {ip} port {port} ssh2"
    else:
        msg = f"Failed password for invalid user {username} from {ip} port {port} ssh2"
        
    return f"{timestamp} {hostname} sshd[{pid}]: {msg}\n"

def main():
    print("[*] Starting SSH Brute Force Simulation...")
    print(f"[*] Target Log File: {LOG_FILE}")
    
    if not os.path.exists(LOG_FILE):
        print(f"[!] Warning: {LOG_FILE} does not exist. Creating it...")
        # create if not exists
        try:
            with open(LOG_FILE, 'a') as f:
                pass
        except PermissionError:
            print("[!] Permission Denied. Run with sudo.")
            return

    attempts = random.randint(22, 35) # Ensure >20 to trigger 5712 (Multiple SSHD auth failures)
    print(f"[*] Simulating {attempts} failed login attempts...")
    
    source_ip = generate_ip() # Use one consistent IP per burst for brute force correlation
    
    try:
        with open(LOG_FILE, "a") as f:
            for i in range(attempts):
                username = random.choice(USERNAMES)
                pid = random.randint(1000, 9999)
                log_entry = generate_log_entry(username, source_ip, pid)
                
                f.write(log_entry)
                f.flush()
                
                # Small delay to simulate rapid script execution but not instant
                time.sleep(random.uniform(0.1, 0.5))
                
                if (i + 1) % 5 == 0:
                    print(f"    -> Injected {i + 1} attempts...")
                    
        print(f"[+] Simulation Complete. Injected {attempts} log entries from IP: {source_ip}")
        print("[*] Check Wazuh Dashboard for alerts (Rule IDs 5710, 5712, 5716)")
        
    except PermissionError:
        print("[!] Permission denied. Please run this script as root or via sudo.")
        print("    Example: sudo python3 brute_force_sim.py")

if __name__ == "__main__":
    main()
