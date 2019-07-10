# init

## enumeration
Scanning with nmap reveals SSH and web services on the machine. Using nikto and dirb further reveals _/admin/_ and _/blog/_ directories. WP login is also available. 

While the results of the scans do not initially reveal significant information, the _robots.txt_ contains two interesting entries. 
The first being one of three keys, the second being a dictionary containing potential passwords or other phrases.

By looking through the dictionary, duplicates can be spotted. Sorting and removing doubles leads to a largely reduced file.
The dictionary is used to identify potential usernames and passwords. Since Wordpress reveals existing users when logging in, the file can be used to test for users. A simple python script does the testing.

Afterwards, wpscan can be used to brute force the password:

`wpscan --url http://10.0.2.7 -U elliot -P fsociety.slim -t 10`

This reveals the following:
> Username: elliot, Password: ER28-0652

## Wordpress
By having access to wordpress with an admin account, the typical plugin upload can be used. 
Metasploit actually fails, because it is not detecting a wordpress instance.
This can be avoided by modifying the exploit `gedit /usr/share/metasploit-framework/modules/exploits/unix/webapp/wp_admin_shell_upload.rb` and commenting out the line regarding the failing condition.
Afterwards msf has to be reloaded with `reload`.


## initial access
Looking through home, the user robot can be found with two interesting files. The first is the second key, the other is an md5 hash of the user password.
Utilizing [](https://hashkiller.co.uk/Cracker/MD5) a match can be found: `abcdefghijklmnopqrstuvwxyz` is the password of user `robot`.
Switching to the user allows to read the second flag.

## Priv Esc
Priviledge escalation can be done by hijacking services or other processes owned by other users or through binaries, scripts, etc with set UID bits. Via `ps aux`, `ss -tlpn`, `netstat -tulpen`, `systemctl list-units --type=service --state=running` services and processes can be identified. Regarding SUID bits, `find / -perm /4000 2>/dev/null` can be used.
The search for SUID-bits reveals that nmap is a potential target. Searching for the term _nmap privilege escalation_ reveals an interactive mode available in earlier versions of nmap. This allows to get root access and read the flag in `/root`.
