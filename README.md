# Homeserver Power Saver
A service that suspends your home server and wakes it up in time or if required.

The service turns off your PC according to a set of periods that has been configured. The service considers if your PC is busy and can't be turned off at this moment, e.g. 
* if there is user interactivity on desktop or running terminals where users are logged in
* if there are locked files on samba shares
* if there are running print jobs (cups)
* if [Kodi](https://kodi.tv/) media center plays media at this moment
* if [TvHeadend](https://tvheadend.org/) has active streams 

In case that there is a scheduled [TvHeadend](https://tvheadend.org/) recording during a rest period the service automatically turns on your PC in time so that recordings won't be missed. This is also for scheduled cronjobs that are in your crontabs and scheduled media in [Kodi](https://kodi.tv/) by utilizing the addon [Timers](https://kodi.tv/addons/matrix/script.timers)).

## Command
```
usage: homeserver-power-saver.py [-h] [--daemon] [--stop] [--status] [--version] [--dry-run] s[--mode {mem,disk,off}] --settings SETTINGS [--log {DEBUG,INFO,WARNING,ERROR,CRITICAL}]
                     [--logfile LOGFILE]

options:
  -h, --help            show this help message and exit
  --daemon              start as daemon
  --dbus                handle events coming from d-bus for pre-/post actions
  --stop                stop running daemon
  --status              get status of daemon
  --version             print version
  --dry-run             simulate
  --mode {mem,disk,off,shutdown}
                        mode
  --settings SETTINGS   (required) path to settings file in json format. Typically '../ext/settings.json'
  --log {DEBUG,INFO,WARNING,ERROR,CRITICAL}
                        (optional) log level. Default is INFO
  --logfile LOGFILE     path to log file if process is started as daemon.
```

### Examples

Start service in daemon mode and listen to d-bus events.
```
$ ./homeserver-power-saver.py --daemon --dbus --settings ../ext/settings.json
```

Start service in interactive mode.
```
$ ./homeserver-power-saver.py --dbus --settings ../ext/settings.json
```

Request status of running service:
```
$ ./homeserver-power-saver.py --status
{"pid": 114264, "running": true}
```

Stop running service:
```
$ ./homeserver-power-saver.py --stop
```

## Pre-conditions

1. The script needs _root_ permission (sorry!)
1. The service utilizes
   1. Python 3
   1. The python library [_python-daemon_](https://pypi.org/project/python-daemon/). You can install it like this ```pip install python-daemon``` (Note that must be done with root user!)
   1. The python library [_requests_](https://pypi.org/project/requests/). You can install it like this ```pip install requests``` (Note that must be done with root user!)
   1. The python library [_python-crontab_](https://pypi.org/project/python-crontab/) and [_croniter_](https://pypi.org/project/croniter/). You can install it like this ```pip install python-crontab``` and ```pip install croniter``` (Note that must be done with root user!)
   1. The _ping_ command which is provided in [net-tools](https://network-tools.com/). You can install it like this ```sudo apt install net-tools```
   1. The _who_ command which is POSIX standard.
   1. The _xprintidle_ command which is available in Ubuntu. You can install it like this ```sudo apt install xidle```, see also [xprintidle](https://github.com/g0hl1n/xprintidle).
   1. The _pactl_ command which is available if you system uses pulse audio, see also [pacmd](https://manpages.ubuntu.com/manpages/bionic/man1/pacmd.1.html)
   1. The _smbstatus_ command which is available after you have installed your _samba_ server (e.g. ```apt install samba-common samba```), see also [smbstatus](https://www.samba.org/samba/docs/current/man-html/smbstatus.1.html).
   1. The _lpstat_ command which is available after you have installed _cups_, see also [lpstat](http://www.cups.org/doc/man-lpstat.html).
   1. The _rtcwake_ command which is available in Ubuntu out of the box, see also [rtcwake](https://wiki.ubuntuusers.de/rtcwake/) (wiki.ubuntuusers.de in German)
   1. The _shutdown_ command which is available in Ubuntu out of the box, see also [shutdown](https://wiki.ubuntuusers.de/Herunterfahren/) (wiki.ubuntuusers.de in German)

### Check if your PC is able to suspend and wake up again
The service utilizes the ```rtcwake``` command. Maybe you want to check if your PC is able to suspend and wake up again. You can test it like this:

Open a terminal and enter
```
$ sudo -s
... [enter password]

$ rtcwake -m mem -s 60
```

Your PC should switch to _suspend to ram_ (mode is ```mem```) and wake up after 60 seconds. In case that it doesn't work, you can probably find solutions somewhere in the internet ;-)

## Configuration
To start _homeserver-power-saver_ you need to provide a settings file.

This file is located in the ```/ext``` folder. It is a file in json format. You can find an example [here](https://raw.githubusercontent.com/Heckie75/homeserver-power-saver/main/ext/settings.json). 

Let's go through this file:
```json
{
    "dryrun": false,            // [true,false] - if true then service runs in dry-mode, i.e. PC won't be turned off
    "mode": "mem",              // [mem,disk,off,shutdown] - 'mem' means 'suspend to ram', 'disk' means 'suspend to disk' and 'off' means that system will be powered off. 'shutdown' won't wake up the system anymore 
    "dbus": true,               // handle events coming from d-bus for pre-/post actions
    "respite_prepare": 10,      // time in seconds that will be waited after pre-actions have been executed (see below) and call of rtcwake that suspends system.
    "respite_recover": 10,      // time in seconds that will be waited after system has been turned on again and execution of pre-actions (see below).
    "min_uptime": 5,            // minimal uptime in minutes.
    "min_downtime": 15,         // minimal downtime (suspend) in minutes.
    "checkers": {               // Checkers that tell the service to keep PC turned on if it is busy or to wake up PC earlier, e.g. in case of a scheduled recording. 
        "PowerSaverInterruptionChecker": { // Checker that checks if there are periods in which PC has to wake up or stay up.
            "enable": true,
            "uptimes": [                   // List of periods with uptimes
                {                          // first period
                    "days": [              // days of period, 0=Mon, 6=Sun
                        0,
                        1,
                        2,
                        3,
                        4,
                        5,
                        6
                    ],
                    "from": "6:45",
                    "until": "7:35"
                }
            ],
            "preactions": [                // A list of commands that will be executed before call of rtcwake that suspends system
                [                          // I recognized that it is a good idea to stop tvheadend.service
                    "systemctl",
                    "stop",
                    "tvheadend.service"
                ],
                [                         // I also pause my virtualbox with Windows
                    "sudo",
                    "-u",
                    "heckie",
                    "VBoxManage",
                    "controlvm",
                    "Windows 10 pro",
                    "pause"
                ],
                [
                    "sudo",
                    "-u",
                    "heckie",
                    "/opt/signal-cli/bin/signal-cli",
                    "-c",
                    "/home/heckie/.local/share/signal-cli",
                    "send",
                    "-m",
                    "heckies-nuc ruht sich aus.",
                    "--note-to-self"
                ]
            ],
            "postactions": [               // A list of commands that will be executed after system has been waken up
                [
                    "/home/heckie/bin/usbbind.py",
                    "--rebind",
                    "2040:0265"
                ],
                [                          // I have recognized that energy saving settings aren't optimal anymore after system wakes up. Therefore, I auto-tune settings again.
                    "/home/heckie/bin/rc.local"
                ],
                [                          // Since I have stopped tvheadend.service it is necessary to start this service after system wakes up.
                    "systemctl",
                    "start",
                    "tvheadend.service"
                ],
                [                          // I want also to restart my virtual machine.
                    "sudo",
                    "-u",
                    "heckie",
                    "VBoxManage",
                    "controlvm",
                    "Windows 10 pro",
                    "resume"
                ],
                [
                    "sudo",
                    "-u",
                    "heckie",
                    "/opt/signal-cli/bin/signal-cli",
                    "-c",
                    "/home/heckie/.local/share/signal-cli",
                    "send",
                    "-m",
                    "heckies-nuc ist aufgewacht.",
                    "--note-to-self"
                ]
            ]
        },
        "XIdleInteruptionChecker": {       // Checker that checks latest user desktop activity, e.g. keyboard and mouse
            "enable": true,                // [true,false] if true then checker is activated
            "stay_awake": 10,              // If there was user activity service will wait another 10 minutes before it retries to suspend system
            "min_idle": 30,                // Minimal inactivity time in minutes
            "users": [                     // A list of users with expected desktop activity
                "heckie"
            ]
        },
        "WhoInteruptionChecker": {         // Checker that checks if there are active terminals
            "enable": true,                // [true,false] if true then checker is activated
            "stay_awake": 10,              // If there are active terminals at this moment service will wait another 10 minutes before it retries to suspend system
            "ignore_lines": [              // Some terminals/lines are always active, e.g. the line for the Gnome-Session. This will be ignored. Use the "w" command in order to find out the line for your system!
                "tty7"
            ]
        },
        "ProcessInteruptionChecker": {   // Checker that checks if there are processes running
            "enable": true,
            "stay_awake": 2,             // If at least one process is running wait another 2 minutes before it retries to suspend system
            "processes": [               // list of processes, see also command 'ps -ax -o %c' in order to get an idea of process names
                "tar",                   // typical command used for compressing files or created a backup
                "gzip",                  // typical command used for compressing files or created a backup
                "zip",                   // typical command used for compressing files or created a backup
                "unzip",                 // typical command used for compressing files or created a backup
                "7z",                    // typical command used for compressing files or created a backup
                "cp",                    // command used to copy files
                "scp",                   // command used to copy files by utilizing ssh
                "rsync",                 // command used to sychronize files
                "apt",                   // command that is installing software or updating you system
                "clamscan",              // virus scan
                "brasero",               // cd burning tool
                "wodim",                 // cd burning tool
                "VBoxManage"             // tool to manage virtualbox, e.g. shrinking virtual disks
            ]
        },
        "KodiInteruptionChecker": {        // Checker for Kodi media center
            "enable": true,                // [true,false] if true then checker is activated
            "stay_awake": 10,              // If Kodi plays media at this moment service will wait another 10 minutes before it retries to suspend system
            "preaction" : true,            // if true then powersaver will stop playback before it suspends system so that there won't be playback when system wakes up again
            "host": "192.168.178.30",      // IP address of Kodi's web server. Note that webserver must be activated in Kodi
            "port": 9080,                  // Port of Kodi's web server
            "user": "kodi",                // User for web interface
            "password": "kodi"             // Password of user
        },
        "KodiTimersInterruptionChecker": { // Checker for Kodi media center's timers addon 
            "enable": true,                // [true,false] if true then checker is activated
            "extra_wakeup_time": 2,        // In case of scheduled media system will be started 2 minutes earlier
            "path": "/home/heckie/.kodi",  // path to Kodi's configuration folder
            "postaction": true,            // perform postaction, i.e. set default volume in Kodi according value in settings of timers addon
            "host": "192.168.178.30",      // IP address of Kodi's web server. Note that webserver must be activated in Kodi
            "port": 9080,                  // Port of Kodi's web server
            "user": "kodi",                // User for web interface
            "password": "kodi"             // Password of user
        },
        "TvHeadendInteruptionChecker": {   // Checker for TvHeadend
            "enable": true,                // [true,false] if true then checker is activated
            "stay_awake": 10,              // If TvHeadend has active streams service will wait another 10 minutes before it retries to suspend system
            "extra_wakeup_time": 5,        // In case of scheduled recordings system will be started 5 minutes earlier
            "host": "192.168.178.30",      // IP address of TvHeadend service
            "port": 9981,                  // Port address of TvHeadend service
            "user": "tvheadenduser",       // User name. Note that user need admin permissions in TvHeadend
            "password": "tvheadenduser"    // Password of user
        },
        "TvHeadendEpgGrabberInterruptionChecker": { // Checker for TvHeadend's EPG grabbers that are scheduled by cron expressions
            "enable": true,
            "epg_config_path": "/home/hts/.hts/tvheadend/epggrab/config", // path to config file
            "extra_wakeup_time": 2         // In case of scheduled epg grabbers system will be started 2 minutes earlier
        },
        "PulseAudioSinkInputInterruptionChecker": { // Checker for Samba audio server
            "enable": true,                // [true,false] if true then checker is activated
            "stay_awake": 10,              // If pulse audio has active input sinks system will wait another 10 minutes before it retries to suspend system
            "users": [                     // A list of users with expected desktop activity
                "heckie"
            ]
        },
        "SambaInteruptionChecker": {       // Checker that checks if there are locked files on samba shares
            "enable": true,
            "stay_awake": 10
        },
        "CupsInteruptionChecker": {       // Checker that checks if there are active print jobs
            "enable": true,
            "stay_awake": 5
        },
        "CronInteruptionChecker": {        // Checker that checks jobs in crontabs 
            "enable": true,
            "stay_awake": 30,              // If there was recently a job scheduled it is expected that this job runs this time. Note: Choose a time that fits for everything that you have scheduled!
            "extra_wakeup_time": 5,        // In case of scheduled jobs system will be started 5 minutes earlier
            "users": [                     // Take crontabs of these users into account
                "heckie",
                "root"
            ],
            "tabfiles": [                 // Take additionally these crontabs into account
                "/etc/cron.d/cron-apt"
            ],
            "ignore_frequency" : {        // ignore cron jobs that are scheduled very often. You can combine "max_per_year", "max_days_per_year", "max_day" or "max_hour" or leave them out if not required.
                "max_per_year" : 8760,    // ignore cron jobs that are executed more than 8760 times a year, i.e. more than once an hour on every day
                "max_days_per_year" : 12, // ignore cron jobs that are executed more than 12 days a year
                "max_per_day" : 24,       // ignore cron jobs that are executed more than once an hour
                "max_per_hour" : 59       // ignore cron jobs that are executed every minute
            },
        },
        "LoadInteruptionChecker": {       // Checker that checks if system has a high CPU utilization at this moment indicating that something important is going on that mustn't be interupted
            "enable": true,
            "stay_awake": 5,             // If there is high CPU utilization wait another 5 minutes before it retries to suspend system
            "threshold": 0.95            // level of avg. CPU utilization in last 5 minutes. If CPU utilization is higher system won't suspend, see also command 'top'
        },
        "PingInteruptionChecker": {        // Checker that looks if there are active devices in your network, e.g. your Smartphone that indicated that you are at home 
            "enable": true,                // [true,false] if true then checker is activated
            "stay_awake": 10,              // If devices is reachable at this moment service will wait another 10 minutes before it retries to suspend system
            "ignore_periods": [            // At night you and your smartphone are at home but you want to suspend system. Here you can configure periods when check is ignored. Note: "ignore_periods" can be configured for all checkers!
                {
                    "days": [
                        0,
                        1,
                        2,
                        3,
                        4,
                        5,
                        6
                    ],
                    "from": "22:30",
                    "until": "6:30"
                }
            ],
            "ip": [                        // List of IP addresses
                "192.168.178.21",
                "192.168.178.24",
                "192.168.178.32"
            ]
        }
    },
    "log": "INFO",                        // [DEBUG,INFO,WARNING,ERROR,CRITICAL] Log level
    "logfile": "/tmp/powersaver.log"      // Path to log file
}
```

## Checkers
### Common settings for checkers
All checkers support the following properties:
* ```enable``` - mandatory, you can activate (```true```) or deactivate (```false```) a checker
* ```stay_awake``` - optional, time in minutes to wait in case that something in running at this moment
* ```ignore_periods``` - optional, periods when it is ignored even if it has been determined that something is running at this moment

```json
        "FooChecker": {
            "enable": true,
            "stay_awake": 10,
            "ignore_periods": [
                {
                    "days": [
                        0,
                        1,
                        2,
                        3,
                        4,
                        5,
                        6
                    ],
                    "from": "22:30",
                    "until": "6:30"
                }
            ],
            // ...
        },
```

### PowerSaverInterruptionChecker - Define periods to stay up or wake up your PC

```json
        "PowerSaverInterruptionChecker": { // Checker that checks if there are periods in which PC has to wake up or stay up.
            "enable": true,
            "uptimes": [                   // List of periods with uptimes
                {                          // first period
                    "days": [              // days of period, 0=Mon, 6=Sun
                        0,
                        1,
                        2,
                        3,
                        4,
                        5,
                        6
                    ],
                    "from": "6:45",
                    "until": "7:35"
                }
            ],
            "preactions": [                // A list of commands that will be executed before call of rtcwake that suspends system
                [                          // I recognized that it is a good idea to stop tvheadend.service
                    "systemctl",
                    "stop",
                    "tvheadend.service"
                ],
                [                         // I also pause my virtualbox with Windows
                    "sudo",
                    "-u",
                    "heckie",
                    "VBoxManage",
                    "controlvm",
                    "Windows 10 pro",
                    "pause"
                ],
                [
                    "sudo",
                    "-u",
                    "heckie",
                    "/opt/signal-cli/bin/signal-cli",
                    "-c",
                    "/home/heckie/.local/share/signal-cli",
                    "send",
                    "-m",
                    "heckies-nuc ruht sich aus.",
                    "--note-to-self"
                ]
            ],
            "postactions": [               // A list of commands that will be executed after system has been waken up
                [
                    "/home/heckie/bin/usbbind.py",
                    "--rebind",
                    "2040:0265"
                ],
                [                          // I have recognized that energy saving settings aren't optimal anymore after system wakes up. Therefore, I auto-tune settings again.
                    "/home/heckie/bin/rc.local"
                ],
                [                          // Since I have stopped tvheadend.service it is necessary to start this service after system wakes up.
                    "systemctl",
                    "start",
                    "tvheadend.service"
                ],
                [                          // I want also to restart my virtual machine.
                    "sudo",
                    "-u",
                    "heckie",
                    "VBoxManage",
                    "controlvm",
                    "Windows 10 pro",
                    "resume"
                ],
                [
                    "sudo",
                    "-u",
                    "heckie",
                    "/opt/signal-cli/bin/signal-cli",
                    "-c",
                    "/home/heckie/.local/share/signal-cli",
                    "send",
                    "-m",
                    "heckies-nuc ist aufgewacht.",
                    "--note-to-self"
                ]
            ]
        },
```

### XIdleInteruptionChecker - Check if somebody is working with your desktop

In case that somebody is working with the desktop, e.g. Gnome, KDE, you probably want to keep your PC running. You must specify a list of users that will be taken into account.
```json
        "XIdleInteruptionChecker": {       // Checker that checks latest user desktop activity, e.g. keyboard and mouse
            "enable": true,                // [true,false] if true then checker is activated
            "stay_awake": 10,              // If there was user activity service will wait another 10 minutes before it retries to suspend system
            "min_idle": 30,                // Minimal inactivity time in minutes
            "users": [                     // Allow list with user names. A list of users with expected desktop activity
                "heckie"
            ]
        },
```

Precondition for this checker is that the _xprintidle_ is available. You can install it like this ```sudo apt install xidle```, see also [xprintidle](https://github.com/g0hl1n/xprintidle).

### WhoInteruptionChecker - Check if anybody is logged in

In case that somebody is working on a terminal, e.g. ssh terminal, you probably don't want to suspend your PC as well. 
```json
        "WhoInteruptionChecker": {         // Checker that checks if there are active terminals
            "enable": true,                // [true,false] if true then checker is activated
            "stay_awake": 10,              // If there are active terminals at this moment service will wait another 10 minutes before it retries to suspend system
            "ignore_lines": [              // Some terminals/lines are always active, e.g. the line for the Gnome-Session. This will be ignored. Use the "w" command in order to find out the line for your system!
                "tty7"
            ]
        },
```

#### Determine lines / terminals that should be ignored
The _WhoInteruptionChecker_ checks if there are active lines / terminals. Unfortunately the Gnome desktop itself has also a line. You can find out the line by using the ```w``` command:
```
$ w
 17:23:01 up 5 days,  1:17,  3 users,  load average: 1,75, 1,73, 1,78
USER     TTY      VON              ANMELD@   UNTÄ   JCPU   PCPU WAS
heckie   tty7     :0                So16    5 Tage 21:13   0.39 s /usr/libexec/gnome-session-binary --builtin --session=budgie-desktop
heckie   pts/0    192.168.178.31   16:54   28:09   0.03 s  0.03 s -bash
heckie   pts/1    192.168.178.31   17:23    0.00 s  0.03 s  0.00 s w
```

In this example the Gnome shell has the line ```tty7```. To ignore this shell configuration of _WhoInteruptionChecker_ looks like this:

```json
        "WhoInteruptionChecker": {
            "enable": true,
            "stay_awake": 10,
            "ignore_lines": [
                "tty7"
            ]
        },
```

### KodiInteruptionChecker - Check if Kodi is playing media at this moment

If somebody is playing media in Kodi at this moment, you probably don't want to suspend the system.

```json
        "KodiInteruptionChecker": {        // Checker for Kodi media center
            "enable": true,                // [true,false] if true then checker is activated
            "stay_awake": 10,              // If Kodi plays media at this moment service will wait another 10 minutes before it retries to suspend system
            "preaction" : true,            // if true then powersaver will stop playback before it suspends system so that there won't be playback when system wakes up again
            "host": "192.168.178.30",      // IP address of Kodi's web server. Note that web server must be activated in Kodi
            "port": 9080,                  // Port of Kodi's web server
            "user": "kodi",                // User for web interface
            "password": "kodi"             // Password of user
        },
```

### KodiTimersInterruptionChecker - Check if Kodi has scheduled media

In case that you use the kodi addon [Timers](https://kodi.tv/addons/matrix/script.timers) you can wake up your machine in case that there are scheduled media actions during rest period.

```json
        "KodiTimersInterruptionChecker": { // Checker for Kodi media center's timers addon 
            "enable": true,                // [true,false] if true then checker is activated
            "extra_wakeup_time": 2,        // In case of scheduled media system will be started 2 minutes earlier
            "path": "/home/heckie/.kodi",  // path to Kodi's configuration folder
            "postaction": true,            // perform postaction, i.e. set default volume in Kodi according value in settings of timers addon
            "host": "192.168.178.30",      // IP address of Kodi's web server. Note that webserver must be activated in Kodi
            "port": 9080,                  // Port of Kodi's web server
            "user": "kodi",                // User for web interface
            "password": "kodi"             // Password of user
        },
```

### TvHeadendInteruptionChecker - Check if TvHeadend has active streams and scheduled recordings

If somebody is streaming a recorded movie or a live tv stream at this moment, you probably don't want to suspend the system.
On the other hand you don't want to miss scheduled recordings in periods when the systems suspends. Therefore, this checker can interrupt a rest period and wakes up your PC in time so that scheduled recordings won't be missed.  

```json
        "TvHeadendInteruptionChecker": {   // Checker for TvHeadend
            "enable": true,                // [true,false] if true then checker is activated
            "stay_awake": 10,              // If TvHeadend has active streams service will wait another 10 minutes before it retries to suspend system
            "extra_wakeup_time": 5,        // In case of scheduled recordings system will be started 5 minutes earlier
            "host": "192.168.178.30",      // IP address of TvHeadend service
            "port": 9981,                  // Port address of TvHeadend service
            "user": "tvheadenduser",       // User name. Note that user need admin permissions in TvHeadend
            "password": "tvheadenduser"    // Password of user
        }
```

### TvHeadendEpgGrabberInterruptionChecker - Check if TvHeadend has scheduled EPG grabbers
TVHeadend grabs EPG data over-the-air or by utilizing internal EPG grabbers. These are scheduled by cron expressions. Activate this checker if you want to wake up your system for grabbing. 

Note: By default the EPG grabbers run after TVHeadend has started. This can be a problem if you restart TVHeadend any time you system wakes up.

```json
        "TvHeadendEpgGrabberInterruptionChecker": { // Checker for TvHeadend's EPG grabbers that are scheduled by cron expressions
            "enable": true,
            "epg_config_path": "/home/hts/.hts/tvheadend/epggrab/config", // path to config file
            "extra_wakeup_time": 1         // In case of scheduled epg grabbers system will be started 1 minute earlier
        },
``` 

### PulseAudioSinkInputInterruptionChecker - check if PC is playing audio

If somebody is playing audio ether directly at the PC or using the PC as bluetooth audio sink, you probably don't want to suspend the system.

```json
        "PulseAudioSinkInputInterruptionChecker": { // Checker for Samba audio server
            "enable": true,                // [true,false] if true then checker is activated
            "stay_awake": 10,              // If pulse audio has active input sinks system will wait another 10 minutes before it retries to suspend system
            "users": [                     // A list of users with expected desktop activity
                "heckie"
            ]
        }
```

Precondition for this checker is that the _pacmd_ is available, see also [pacmd](https://manpages.ubuntu.com/manpages/bionic/man1/pacmd.1.html)

### SambaInteruptionChecker - Check if users are working with samba shares

If your PC is a samba file server it isn't a good idea to shutdown the system while users are working on files.
```json
        "SambaInteruptionChecker": {       // Checker that checks if there are locked files on samba shares
            "enable": true,
            "stay_awake": 10
        },
```

Precondition for this checker is that the _smbstatus_ is available. This should be the case after you have installed your _samba_ server (e.g. ```apt install samba-common samba```), see also [smbstatus](https://www.samba.org/samba/docs/current/man-html/smbstatus.1.html).


### CupsInteruptionChecker - Check if there are active print jobs (cups)

If your PC is a print server you shouldn't suspend the system as long as there are active print jobs.
```json
        "CupsInteruptionChecker": {       // Checker that checks if there are active print jobs
            "enable": true,
            "stay_awake": 5
        },
```

Precondition for this checker is that the _lpstat_ is available. This should be the case after you have installed your _cups_ server, see also see also [lpstat](http://www.cups.org/doc/man-lpstat.html).

### CronInteruptionChecker - check if cron jobs are scheduled

This checker keeps your PC up in case that there are cron jobs that are probably still running. This is configured by using the ```stay_awake``` attribute. 

This checker is also able to determine if there are scheduled cron jobs in an upcoming rest period. If this is the case the rest period will be interrupted earlier so that the cron job won't be missed.
```json
        "CronInteruptionChecker": {        // Checker that checks jobs in crontabs 
            "enable": true,
            "stay_awake": 30,              // If there was recently a job scheduled it is expected that this job runs this time. Note: Choose a time that fits for everything that you have scheduled!
            "extra_wakeup_time": 5,        // In case of scheduled jobs system will be started 5 minutes earlier
            "users": [                     // Take crontabs of these users into account
                "heckie",
                "root"
            ],
            "tabfiles": [                 // Take additionally these crontabs into account
                "/etc/cron.d/cron-apt"
            ],
            "ignore_frequency" : {        // ignore cron jobs that are scheduled very often. You can combine "max_per_year", "max_days_per_year", "max_per_day" or "max_per_hour" or leave them out if not required.
                "max_per_year" : 8760,    // ignore cron jobs that are executed more than 8760 times a year, i.e. more than once an hour on every day
                "max_days_per_year" : 12, // ignore cron jobs that are executed more than 12 days a year
                "max_per_day" : 24,       // ignore cron jobs that are executed more than once an hour
                "max_per_hour" : 59       // ignore cron jobs that are executed every minute
            }
        }
```

Sometimes you have jobs that run very often but aren't that important. You can ignore these jobs by utilizing the ```ignore_frequency``` structure. Here you can ignore jobs that run with a specific frequency. You can combine ```max_per_year```, ```max_days_per_year```, ```max_per_day``` or ```max_per_hour``` or leave them out if not required.

On the other hand you maybe need specific handling for special jobs, e.g. longer _stay awake_ time for backing up your home directory. You can annotate your cron jobs by leaving a specific comment, i.e. ```# @homeserver-power-saver(stay_awake=20)```

Example:

Overrule _stay awake_ time for this job since it runs longer or shorter in comparison to global setting ```stay_awake```. In addition ```_extra_wakeup_time_``` has been overruled, too, since after the PC has been woken up it will update software from repo first (this is the way cron-apt works by default).

```
33 3 15 * *    /home/heckie/bin/archive_home > /dev/null 2>&1 # @homeserver-power-saver(extra_wakeup_time=10,stay_awake=30)
```

There are other options:

Don't ignore this job even if it has a high frequency (according setting ```ignore_frequency```)
```
0 * * * *    echo "a job that runs once an hour" # @homeserver-power-saver(force=true,stay_awake=20)
```

Ignore this job in any case:
```
0 3 * * *    echo "a job that is not very important" # @homeserver-power-saver(ignore=true)
```

### PingInteruptionChecker - Check if there are devices in your network

If you don't want to suspend your PC if there are specific devices in your network, e.g. your smartphone, you must activate this checker that tries to reach devices by pinging their IP address. 
```json
        "PingInteruptionChecker": {        // Checker that looks if there are active devices in your network, e.g. your Smartphone that indicated that you are at home 
            "enable": true,                // [true,false] if true then checker is activated
            "stay_awake": 10,              // If devices is reachable at this moment service will wait another 10 minutes before it retries to suspend system
            "ignore_periods": [            // At night you and your smartphone are at home but you want to suspend system. Here you can configure periods when check is ignored. Note: "ignore_periods" can be configured for all checkers!
                {
                    "days": [
                        0,
                        1,
                        2,
                        3,
                        4,
                        5,
                        6
                    ],
                    "from": "22:30",
                    "until": "6:30"
                }
            ],
            "ip": [                        // List of IP addresses
                "192.168.178.21",
                "192.168.178.24",
                "192.168.178.32"
            ]
        },
```

## Pre-actions / post-actions
You can run several action before and after the PC suspends. Actions will be configured as a list (json-style). 

Note that each command is also notated in list style. This enables you to pass commands and parameters.

The command ```systemctl stop tvheadend.service``` is notated like this:
```json
            [
                "systemctl",
                "stop",
                "tvheadend.service"
            ]
```

Example with two commands:
```json
    "preaction": {
        "commands": [
            [ // Command 1: systemctl stop tvheadend.service
                "systemctl",
                "stop",
                "tvheadend.service"
            ],
            [ // Command 2: sudo -u heckie VBoxManage controlvm "Windows 10 pro" pause
                "sudo",
                "-u",
                "heckie",
                "VBoxManage",
                "controlvm",
                "Windows 10 pro",
                "pause"
            ]
        ]
    },
```

Note: If you don't want to run any commands use the empty list notation:
```json
    "preaction": {
        "commands": []
    }
```

### Process flow
The process flow is as follows:
1. perform pre-actions of checkers according settings
2. wait some seconds according given value in ```respite_prepare```
3. set PC into suspend mode according given mode in ```mode``` (```rtcwake``` is called)
4. wait some seconds according given value in ```respite_recover```
5. perform post-actions of checkers according settings
6. prevent that PC will suspend next minutes according ```min_uptime```

## Starting Homeserver Power Saver after boot
Since this script isn't a systemd service you need to start this script differently. You can do it just by adding a line in root's crontab like this:
```
@reboot        /opt/homeserver-power-saver/src/homeserver-power-saver.py --daemon --settings /opt/homeserver-power-saver/ext/settings.json
```

## About
Caused by the energy crisis in Europe in 2022 and rising prices for electricity I think about where I can save energy. I run an Intel NUC NUC8i5BEH as a home automation and home theatre server. It runs 24/7. The setup consumes approx. 10 watts when it idles. 4 watts are eaten by a zoo of USB devices that is connected via a powered USB hub. The other 6W are taken by the Intel NUC itself. I have [measured](https://github.com/Heckie75/voltcraft-sem-6000) that a can save almost these 6 watts if system suspends to ram.

I know that it sounds strange to turn off a server. But especially during night hours there is no need to run it. I developed this script that is able to turn off the PC and turns it on again, e.g. in case of scheduled recordings.

Last but not least my router, FRITZ!Box 7490 (see also [AVM FRITZ!Box](https://avm.de/produkte/fritzbox/)), wakes up my PC in case of an IP request. This takes just a few seconds (<10s).
