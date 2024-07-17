# newtool - tag line

This repo is a shell / template/ set of start files for a new tool using the cjnfuncs freamework.

README placeholder text follows

Monitors WAN-side internet access and WAN IP address changes on a home network.  Sends email and/or text notifications for internet outages (after restored) and WAN IP changes.  The tool is highly configurable for which modem and router you may be using.  Configurations for dd-wrt and pfSense routers, and Motorola and Technicolor/Cox gateway modems are included.

Supported on Python3.6+ on Linux and Windows.

**NOTE:**  Due to as-of-yet unsolved problems with Python 3.6 and import_resources, the `--setup-user` and `--setup-site` switches are not working on Py 3.6.  Manually grab the files from the [github](https://github.com/cjnaz/XXXX) `src/deployment_files directory` and place them in the `~\.config\XXXX` directory.  These command line switches work correctly on Python 3.7+.



`wanstatus --service` enters an infinite loop, periodically checking the status of internet access and the WAN IP address.  `wanstatus` interactively checks status.

- Internet access is detected by contacting an external DNS server (faster) such as the Google public DNS server at 8.8.8.8.  Alternately, web addresses may be pinged to detect internet access (slower).
- If there is NO internet access then the outage time is captured and logged, and wanstatus enters a tight loop checking for recovery of internet access.  Once restored, wanstatus sends email and/or text notifications that internet access was lost and now restored, and how long the outage was.
- If there IS access to the internet, then wanstatus reads and logs the modem status page (typically at 192.168.100.1).
- wanstatus then reads the pfSense or dd-wrt router status page for the WAN IP address, and if changed then sends email and/or notification messages of the change.
- Finally, wanstatus periodically checks with an external web page for the reported WAN IP address.  


All parameters are set in the `wanstatus.cfg` config file.  On each loop in service mode the config file is checked for changes, and reloaded as needed.  This allows for on-the-fly configuration changes.

wanstatus may be started manually, or may be configured to start at system boot.  An example systemd unit file is included.  See systemd documentation for how to set it up.

<br/>

---

## Notable changes since prior release
V3.0 - Converted to package format, updated to cjnfuncs 2.0

<br/>

---

## Usage
```
$ wanstatus -h
usage: wanstatus [-h] [--config-file CONFIG_FILE] [--log-file LOG_FILE]
                 [--print-log] [--service] [--setup-user] [--setup-site] [-V]

Check internet access and WAN IP address.  Send notification/email after outage is over and
on WAN IP change.
3.0

optional arguments:
  -h, --help            show this help message and exit
  --config-file CONFIG_FILE, -c CONFIG_FILE
                        Path to the config file (Default <wanstatus.cfg)> in user/site config directory.
  --log-file LOG_FILE, -l LOG_FILE
                        Path to the log file.
  --print-log, -p       Print the tail end of the log file (default last 40 lines).
  --service             Enter endless loop for use as a systemd service.
  --setup-user          Install starter files in user space.
  --setup-site          Install starter files in system-wide space. Run with root prev.
  -V, --version         Return version number and exit.
```

<br/>

---

## Example output
```
$$ wanstatus 
 WARNING:  ========== wanstatus (3.0) ==========
 WARNING:  Config file </home/me/.config/wanstatus/wanstatus.cfg>
    INFO:  Internet access:             Working          (DNS server 72.105.29.22, command run time   11.3 ms)
    INFO:  Modem status:                Locked           (command run time 6550.7 ms)
    INFO:  Router reported WANIP:       27.177.61.124    (command run time 2300.2 ms)
    INFO:  Externally reported WANIP:   27.177.61.124    (command run time  350.1 ms)
```

<br/>

---

## Setup and Usage notes
- Install wanstatus from PyPI (pip install wanstatus).
- Install the initial configuration files (`wanstatus --setup-user` places files at ~/.config/wanstatus).
- Edit/configure `wanstatus.cfg`, `creds_SMTP`, and `creds_wanstatus` as needed.
- Run manually as `wanstatus`, or install the systemd service.
- When running in service mode (continuously looping) the config file may be edited and is reloaded when changed.  This allows for changing settings without having to restart the service.


<br/>

---

## Customization notes

<br/>

---

## Version history
- 0.1 230226 - New
