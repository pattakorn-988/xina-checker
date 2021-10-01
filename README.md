# xina-checker

Used to monitor Sitecore versions in various environment

### Prepare environment

```
git clone https://github.com/pattakorn-988/xina-checker.git
```

Duplicate ``.env.sample`` into ``.env`` and populate.

```
pip3 install -r requirements.txt
python3 main.py
```

### Run as systemd service

```
sudo nano /etc/systemd/system/xina.service
```
```
[Unit]
Description=John Xina, Sitecore Checker
After=multi-user.target
After=network-online.target
Wants=network-online.target

[Service]
Type=simple
ExecStart=sudo -H -u pi /usr/bin/python3 /home/pi/xina-checker/main.py
Restart=always

[Install]
WantedBy=multi-user.target
```
```
sudo systemctl daemon-reload
sudo systemctl enable xina.service
sudo systemctl start xina.service
```
