# SOC Incident Report

## 1. Executive Summary & Alert Metadata

| Field | Details |
| :--- | :--- |
| **Incident ID** | `INC-202X-XXXX` |
| **Severity** | High / Critical |
| **Detected Timestamp** | `YYYY-MM-DD HH:MM:SS UTC` |
| **Reporter / Analyst** | `[Analyst Name]` |
| **Status** | Open / In Progress / Resolved / Closed |
| **Summary** | Briefly describe the incident (e.g., "Multiple SSH authentication failures followed by unauthorized modification of /etc/passwd and SUID binary creation on victim-endpoint.") |

---

## 2. Threat Actor Tactics, Techniques & Procedures (TTPs)

| MITRE ATT&CK Tactic | Technique ID | Technique Name | Observation / Context |
| :--- | :--- | :--- | :--- |
| **Credential Access** | [T1110](https://attack.mitre.org/techniques/T1110/) | Brute Force | 20+ failed SSH login attempts originating from `[Source IP]` targeting multiple usernames. |
| **Privilege Escalation** | [T1548.001](https://attack.mitre.org/techniques/T1548/001/) | Abuse Elevation Control Mechanism: Setuid and Setgid | A new binary `/bin/test_suid` was created with the SUID bit set, allowing execution with elevated privileges. |
| **Persistence** | [T1078.003](https://attack.mitre.org/techniques/T1078/003/) | Valid Accounts: Local Accounts | Rogue entry 'hacker' with UID 0 appended to `/etc/passwd`. |
| **Defense Evasion** | [T1014](https://attack.mitre.org/techniques/T1014/) | Rootkit | Syslog entries indicate unauthorized hooking of the `sys_call_table`, characteristic of kernel-mode rootkits. |

---

## 3. Telemetry & Log Evidence

### Affected Asset
- **Hostname**: `victim-endpoint`
- **IP Address**: `[Endpoint IP]`
- **OS**: `Ubuntu 22.04 LTS`

### SIEM Alerts (Wazuh)

| Rule ID | Level | Description |
| :--- | :--- | :--- |
| `5712` | 10 | sshd: brute force trying to get access to the system. |
| `550` | 7 | Integrity checksum changed (File modified). |
| `554` | 10 | File added to the system. |
| `1002` | 2 | Unknown problem somewhere in the system (syslog rootkit anomaly). |

### Raw Log Evidence

**Snippet 1: SSH Brute Force (`/var/log/auth.log`)**
```text
Aug 31 10:15:20 victim-endpoint sshd[12345]: Failed password for invalid user admin from 192.168.1.50 port 54321 ssh2
Aug 31 10:15:21 victim-endpoint sshd[12346]: Failed password for root from 192.168.1.50 port 54322 ssh2
... (20+ similar entries)
```

**Snippet 2: SUID & FIM Alert (`Wazuh Alerts`)**
```json
{
  "rule": {
    "id": "550",
    "level": 7,
    "description": "Integrity checksum changed."
  },
  "syscheck": {
    "path": "/etc/passwd",
    "event": "modified",
    "mtime_before": "2023-10-26T12:00:00",
    "mtime_after": "2023-10-26T12:05:00"
  }
}
```

---

## 4. Root Cause Analysis (RCA)

*Detail how the threat actor gained initial access, moved laterally, and achieved their objectives. What vulnerabilities or misconfigurations were exploited?*

**Example:**
The incident originated from an exposed SSH service lacking rate-limiting or fail2ban protections. The attacker successfully brute-forced a weak credential (if applicable, though in this simulation it was just attempts), or exploited a vulnerability to gain initial shell access. Once on the system, the attacker leveraged elevated privileges to modify `/etc/passwd` to ensure persistence and created a SUID binary (`/bin/test_suid`) as a backdoor. Finally, a mock kernel module was loaded to evade detection.

---

## 5. Containment, Eradication & Remediation Actions Taken

### Containment
- [ ] Network isolated `victim-endpoint` from the production bridge network (`soc-net`).
- [ ] Blocked source IP `[Source IP]` at the perimeter firewall.

### Eradication
- [ ] Removed the rogue account `hacker` from `/etc/passwd` and `/etc/sudoers`.
- [ ] Deleted the unauthorized SUID binary `/bin/test_suid`.
- [ ] Terminated all active SSH sessions for the affected asset.

### Remediation
- [ ] Initiated a full antivirus/rootkit scan (e.g., using chkrootkit/rkhunter or Wazuh Rootcheck).
- [ ] Rebuilt the container/VM from a known good gold image (if eradication is insufficient).

---

## 6. Post-Incident Recommendations

1. **Implement Account Lockout:** Configure `pam_tally2` or `fail2ban` to lock accounts or block IPs after 5 failed authentication attempts.
2. **Disable Root SSH Login:** Ensure `PermitRootLogin no` is set in `/etc/ssh/sshd_config`.
3. **Deploy MFA:** Require Multi-Factor Authentication for all SSH access.
4. **FIM Tuning:** Ensure File Integrity Monitoring alerts for `/etc/` are routed to a high-priority SOC queue for immediate triage.
5. **Least Privilege:** Audit sudoers to ensure no users have `NOPASSWD: ALL` access unless strictly necessary for automated services.
