#!/bin/bash
# ==============================================================================
# Privilege Escalation & Persistence Simulation Script
# Purpose: Generate telemetry for unauthorized user creation, SUID modification, 
# and rootkit execution traces for Wazuh SIEM detection.
# ==============================================================================

echo "[*] Starting Privilege Escalation & Persistence Simulation..."

# 1. Unauthorized Persistence: Rogue User Creation
echo "[*] Phase 1: Injecting rogue user 'hacker' into /etc/passwd..."
# Save original state for cleanup
cp /etc/passwd /tmp/passwd.bak
# Inject rogue user with root UID (0) - Triggers FIM and syslog alerts
echo "hacker:x:0:0:Hacker Account:/root:/bin/bash" >> /etc/passwd
sleep 2

echo "[*] Phase 2: Injecting rogue entry into /etc/sudoers..."
cp /etc/sudoers /tmp/sudoers.bak
# This should trigger File Integrity Monitoring (FIM) in Wazuh
echo "hacker ALL=(ALL:ALL) NOPASSWD: ALL" >> /etc/sudoers
sleep 2

# 2. SUID Bit Manipulation
echo "[*] Phase 3: Creating and manipulating a test binary with SUID bit..."
# Create a dummy binary in a monitored directory
cp /bin/ls /bin/test_suid
# Set SUID bit - This should trigger a syscheck alert for permissions change
chmod u+s /bin/test_suid
sleep 2

# 3. Mock Rootkit Execution Trace
echo "[*] Phase 4: Injecting mock rootkit trace into /var/log/syslog..."
TIMESTAMP=$(date '+%b %d %H:%M:%S')
HOSTNAME="victim-endpoint"
# Inject a fake kernel module load or rootkit-like activity
echo "$TIMESTAMP $HOSTNAME kernel: [ 1234.567890] hidden_module: loading out-of-tree module taints kernel." >> /var/log/syslog
echo "$TIMESTAMP $HOSTNAME kernel: [ 1234.567999] rk_sys: hooking sys_call_table at 0xffffffffc0000000" >> /var/log/syslog
sleep 2

echo "[+] Simulation telemetry generated successfully."
echo "[*] Waiting 10 seconds for Wazuh Agent to collect and forward logs..."
sleep 10

# 4. Artifact Cleanup
echo "[*] Phase 5: Cleaning up artifacts..."
mv /tmp/passwd.bak /etc/passwd
mv /tmp/sudoers.bak /etc/sudoers
rm -f /bin/test_suid
echo "[+] Cleanup complete. System restored to original state."

echo "[*] Check Wazuh Dashboard for alerts regarding:"
echo "    - File changes in /etc/passwd and /etc/sudoers (FIM / Syscheck)"
echo "    - SUID bit changes on /bin/test_suid (FIM / Syscheck)"
echo "    - Rootkit anomalies or syslog keyword matches"
