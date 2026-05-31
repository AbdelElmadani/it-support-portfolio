# Windows Troubleshooting Guide

A practical reference for diagnosing and resolving common end-user issues on
Windows 10 / 11. Each section follows the same format used in help-desk
knowledge bases: **Symptoms → Diagnose → Resolve**, ending with what to escalate.

> Most commands below run in **Command Prompt** or **PowerShell**. Right-click and
> choose *Run as administrator* when a step changes system settings.

---

## 1. DNS Issues

DNS translates names like `intranet.company.com` into IP addresses. When it
fails, the internet "feels down" even though the connection is fine.

**Symptoms**
- Websites won't load, but the network icon shows connected.
- "Server DNS address could not be found" / `DNS_PROBE_FINISHED_NXDOMAIN`.
- Some sites load by IP but not by name.

**Diagnose**
1. Confirm it's DNS, not connectivity. Ping an IP and a name:
   ```
   ping 8.8.8.8
   ping google.com
   ```
   If the IP responds but the name fails, it's a DNS problem.
2. Check which DNS server the PC is using:
   ```
   ipconfig /all
   ```
   Look at the *DNS Servers* line under the active adapter.
3. Test name resolution directly:
   ```
   nslookup google.com
   ```

**Resolve**
1. Flush the local DNS cache:
   ```
   ipconfig /flushdns
   ```
2. Renew the IP/DNS lease:
   ```
   ipconfig /release
   ipconfig /renew
   ```
3. If the assigned DNS server is unreachable, temporarily set a public resolver
   (e.g. `8.8.8.8` and `1.1.1.1`) in *Adapter settings → IPv4 → Properties* to
   confirm the issue is the DNS server, not the PC.
4. Re-test with `nslookup`.

**Escalate when:** internal/corporate names fail for multiple users — this
usually points to the DNS server or domain controller, not the workstation.

---

## 2. Printer Issues

**Symptoms**
- Jobs sit in the queue and never print.
- "Printer offline" when it's powered on and connected.
- Garbled output or missing/incorrect driver.

**Diagnose**
1. Confirm power, paper, toner, and a clear physical/network connection.
2. Check the print queue (*Settings → Bluetooth & devices → Printers*) for
   stuck jobs.
3. Confirm the **correct** printer is set as default — users often print to a
   disconnected device.

**Resolve**
1. Clear a stuck queue by restarting the Print Spooler:
   ```
   net stop spooler
   ```
   Delete everything in `C:\Windows\System32\spool\PRINTERS`, then:
   ```
   net start spooler
   ```
2. For "offline" printers: uncheck *Use Printer Offline*, then power-cycle the
   printer and confirm it has a valid IP (network printers).
3. For bad output or a corrupt driver, remove the printer, delete the driver in
   *Print Management*, and reinstall the latest driver from the manufacturer.
4. For network printers, verify reachability:
   ```
   ping <printer-ip>
   ```

**Escalate when:** an entire office can't reach a shared/network printer —
likely a print server or VLAN issue rather than one workstation.

---

## 3. VPN Issues

**Symptoms**
- VPN client won't connect or drops repeatedly.
- Connected to VPN, but internal resources/shares are unreachable.
- Browsing breaks only while the VPN is up (a DNS-over-VPN problem).

**Diagnose**
1. Confirm the user has a working internet connection *before* the VPN — VPN
   can't fix a dead connection.
2. Read the exact client error (auth failure vs. timeout vs. certificate).
   - Auth failure → credentials/MFA.
   - Timeout → firewall, server address, or ISP blocking the VPN port.
3. Once connected, test internal access by IP and by name to isolate DNS:
   ```
   ping <internal-server-ip>
   nslookup <internal-hostname>
   ```

**Resolve**
1. Re-enter credentials and complete MFA; confirm the account isn't locked or
   expired.
2. Verify the server address/profile matches IT's current settings.
3. Temporarily disable conflicting security software or a local firewall rule
   to test, then re-enable.
4. If names don't resolve over VPN, `ipconfig /flushdns` and reconnect; this is
   often a split-tunnel / DNS suffix issue.
5. As a last resort, reinstall the VPN client to refresh its virtual adapter.

**Escalate when:** the VPN gateway rejects all users or certificates are
expiring org-wide — that's a server-side fix.

---

## 4. Slow Computer

"Slow" is vague — the goal is to find *what* is slow (boot, apps, disk, or
network) and fix the biggest bottleneck.

**Symptoms**
- Long boot times or apps that hang on launch.
- Constant disk or fan activity at idle.
- General sluggishness that worsened over time.

**Diagnose**
1. Open **Task Manager** (`Ctrl+Shift+Esc`) and sort by **CPU**, **Memory**,
   and **Disk** to find what's consuming resources.
2. Check the **Startup** tab for high-impact programs launching at boot.
3. Check free disk space — a drive over ~90% full slows Windows noticeably.

**Resolve**
1. Disable unnecessary startup programs from Task Manager → *Startup*.
2. Free up space with **Disk Cleanup** (`cleanmgr`) or *Storage Sense*; clear
   `%temp%`.
3. Run a malware scan (Windows Security or the org's endpoint tool).
4. Install pending **Windows Updates** and reboot — fixes often ship as patches.
5. Check drive health for an aging disk:
   ```
   wmic diskdrive get status
   ```
   Consistent high disk usage on a spinning HDD is a strong case for an SSD.
6. Verify the machine meets the RAM needs of its workload; upgrade if it's
   pegged at 100% memory under normal use.

**Escalate when:** hardware is failing (disk SMART errors, overheating) or the
device is below spec for required software — that's a repair/replacement
decision.

---

## Quick Command Reference

| Task | Command |
|------|---------|
| Flush DNS cache | `ipconfig /flushdns` |
| Renew IP/DNS lease | `ipconfig /release` then `ipconfig /renew` |
| Full network config | `ipconfig /all` |
| Test DNS resolution | `nslookup <hostname>` |
| Restart Print Spooler | `net stop spooler` → `net start spooler` |
| Disk Cleanup | `cleanmgr` |
| Check disk health | `wmic diskdrive get status` |
| Test connectivity | `ping 8.8.8.8` |

---

*Maintained as part of my IT support portfolio. Steps reflect standard
first-line troubleshooting; always follow your organization's specific
procedures and change-control policies.*
