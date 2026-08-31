# 🛡️ SIEM & Endpoint Threat Detection Lab (SOC)

A production-grade portfolio project demonstrating hands-on experience in Security Information and Event Management (SIEM), Endpoint Detection & Response (EDR), Detection Engineering, and Incident Response using Wazuh and Docker.

```text
+-------------------+       +-------------------+       +-------------------+
|   Victim Endpoint |       |   Wazuh Manager   |       |   Wazuh Indexer   |
|   (Ubuntu + Agent)| ----> |   (SIEM Engine)   | ----> |   (Data Storage)  |
|   - FIM & Syslog  | 1514  |   - Log Parsing   | 9200  |   - OpenSearch    |
+-------------------+       +-------------------+       +-------------------+
                                      |                           |
                                      v                           v
                            +-------------------+       +-------------------+
                            |  Attack Scripts   |       |  Wazuh Dashboard  |
                            |  (Python/Bash)    |       |  (Kibana UI) 443  |
                            +-------------------+       +-------------------+
```

## 📑 Table of Contents
1. [Project Goals & SOC Learning Objectives](#-project-goals--soc-learning-objectives)
2. [Tech Stack Table](#-tech-stack-table)
3. [Prerequisites & System Requirements](#-prerequisites--system-requirements)
4. [Architecture & Telemetry Pipeline](#-architecture--telemetry-pipeline)
5. [Step-by-Step Deployment Guide](#-step-by-step-deployment-guide)
6. [Attack Simulation & Telemetry Verification](#-attack-simulation--telemetry-verification)
7. [Wazuh Dashboard Investigation Guide](#-wazuh-dashboard-investigation-guide)
8. [Triage & Mitigation Playbook](#-triage--mitigation-playbook)
9. [Security Best Practices](#-security-best-practices)
10. [Author & License](#-author--license)

---

## 🎯 Project Goals & SOC Learning Objectives
The primary goal of this project is to build an isolated, containerized lab environment to simulate real-world cyber attacks and practice SOC analyst workflows.

**Analytical Deliverables:**
- **Log Aggregation:** Successfully ingest `syslog` and `auth.log` from a remote endpoint.
- **Detection Engineering:** Trigger out-of-the-box Wazuh rules via Python and Bash simulation scripts.
- **Threat Hunting:** Identify Indicators of Compromise (IoCs) and map them to the MITRE ATT&CK framework.
- **Incident Response:** Document findings using a structured SOC Incident Report template.

---

## 🛠️ Tech Stack Table

| Technology | Category | Specific Purpose |
| :--- | :--- | :--- |
| **Wazuh Manager** | SIEM / EDR Engine | Analyzes incoming logs, applies detection rules, and triggers alerts. |
| **Wazuh Indexer** | Data Storage | Highly scalable indexing and search engine (based on OpenSearch). |
| **Wazuh Dashboard** | Visualization | Web UI for data visualization, dashboarding, and threat hunting. |
| **Docker & Compose** | Containerization | Orchestrates the isolated multi-node network environment. |
| **Ubuntu 22.04** | Monitored OS | Acts as the victim endpoint generating telemetry. |
| **Python / Bash** | Attack Simulation | Scripts to automate SSH brute force and privilege escalation. |

---

## 💻 Prerequisites & System Requirements
- **OS:** Linux, macOS, or Windows (with WSL2).
- **Docker:** Docker Engine `24.0+` and Docker Compose `v2.20+`.
- **Memory (RAM):** Minimum **8GB** dedicated to Docker (12GB+ recommended).
- **Network:** Port `443` (Dashboard), `1514`, `1515`, and `55000` must be available on the host.

> **Note on Virtual Memory:** Wazuh Indexer requires a high `vm.max_map_count`.
> Run this on your host machine (Linux/WSL) before starting:
> `sudo sysctl -w vm.max_map_count=262144`

---

## 🔄 Architecture & Telemetry Pipeline
1. **Telemetry Generation:** Attack scripts run on the `victim-endpoint` container, modifying `/etc/passwd`, `/etc/sudoers`, and flooding `/var/log/auth.log`.
2. **Data Collection:** The Wazuh Agent monitors these files in real-time (FIM) and reads log entries.
3. **Transmission:** Logs are securely forwarded over TCP port `1514` to the Wazuh Manager.
4. **Processing & Alerting:** Wazuh Manager decodes the logs, matches them against rule IDs (e.g., `5712` for Brute Force), and generates an alert.
5. **Storage & Visualization:** Alerts are sent to the Indexer (port `9200`) and visualized on the Dashboard (port `443`).

---

## 🚀 Step-by-Step Deployment Guide

1. **Clone the Repository:**
   ```bash
   git clone https://github.com/mdazharulislamnk/SIEM---Endpoint-Threat-Detection-Lab--SOC-.git
   cd SIEM---Endpoint-Threat-Detection-Lab--SOC-
   ```

2. **Configure Virtual Memory (Linux/WSL only):**
   ```bash
   sudo sysctl -w vm.max_map_count=262144
   ```

3. **Deploy the Lab Environment:**
   ```bash
   docker compose up -d
   ```
   *Wait 3-5 minutes for all services to initialize.*

4. **Verify Container Health:**
   ```bash
   docker compose ps
   ```

5. **Access the Wazuh Dashboard:**
   - Open a browser and navigate to: `https://localhost` (or `https://127.0.0.1`)
   - Ignore the self-signed certificate warning.
   - **Username:** `admin`
   - **Password:** `SecretPassword` (Configured in docker-compose.yml)

6. **Verify Agent Enrollment:**
   - In the Wazuh Dashboard, click the Wazuh logo top-left.
   - Go to **Agents**. You should see `victim-endpoint` listed as **Active**.

---

## ⚔️ Attack Simulation & Telemetry Verification

### Simulation 1: SSH Brute Force
1. Open a terminal into the victim endpoint:
   ```bash
   docker exec -it victim-endpoint bash
   ```
2. Execute the Python simulation script:
   ```bash
   python3 /root/attack_scripts/brute_force_sim.py
   ```
   *This script injects 20+ failed login attempts into `/var/log/auth.log`.*

### Simulation 2: Privilege Escalation & Rootkit
1. From the same terminal, run the Bash simulation:
   ```bash
   bash /root/attack_scripts/priv_esc_sim.sh
   ```
   *This script modifies `/etc/passwd`, adds a SUID bit to a binary, and simulates a kernel rootkit syslog entry.*

---

## 🔎 Wazuh Dashboard Investigation Guide

Once the simulations are run, pivot to the Wazuh Dashboard to act as a SOC Analyst:

1. **Navigating Alerts:**
   - Go to **Modules** -> **Security events**.
   - Review the "Events" timeline. You should see a massive spike.

2. **Filtering Rules:**
   - Click "Add filter".
   - Field: `rule.id`, Operator: `is`, Value: `5712` (SSHD Brute Force).
   - Alternatively, search for `rule.id: 550` or `554` to find File Integrity Monitoring (FIM) alerts related to `/etc/passwd`.

3. **Inspecting Raw JSON:**
   - Expand any alert in the events list.
   - Switch to the **JSON** tab. Notice the mapped `mitre.technique` (e.g., T1110) and the `full_log` containing the raw syslog data injected by our scripts.

---

## 🛡️ Triage & Mitigation Playbook

When high-severity alerts are detected (like the ones simulated above), follow this SOP:

1. **Verify the Alert:** Confirm the SSH attempts or file modifications are not authorized maintenance by a system administrator.
2. **Contain the Endpoint:**
   - In a real environment, you would isolate the host from the network.
   - *Lab equivalent:* `docker network disconnect soc-net victim-endpoint`
3. **Investigate Scope:** Check if the attacker successfully authenticated (Rule ID `5715: sshd: authentication success`).
4. **Eradication:** Remove rogue users from `/etc/passwd`, delete unauthorized SUID binaries, and reset compromised credentials.
5. **Documentation:** Fill out the `incident_report_template.md` provided in this repository.

---

## 🔒 Security Best Practices

While this lab uses default credentials for ease of setup, a production deployment must implement:
- **Strong Passwords/Vaulting:** Change `SecretPassword` and use a secrets manager.
- **TLS Certificates:** Replace self-signed certs with CA-signed certificates for the Wazuh UI and API.
- **Agent Mutual Authentication:** Implement certificate-based authentication for agent enrollment.
- **Resource Limits:** Define strictly bounded CPU/Memory limits in `docker-compose.yml` to prevent DoS via log flooding.

---

## 📝 Author & License
**Author:** Md Azharul Islam
**Repository:** [GitHub](https://github.com/mdazharulislamnk/SIEM---Endpoint-Threat-Detection-Lab--SOC-.git)

*This project is for educational and portfolio demonstration purposes only. Do not run attack scripts against unauthorized systems.*
