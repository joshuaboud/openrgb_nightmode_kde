# openrgb_nightmode_kde
Make OpenRGB colors follow KDE nightmode color temperature.  

## How it works
Modifies whatever colors are currently set on LEDs, so make sure to manually set daytime colors first.

## Installation
1. Clone git repo
2. Install for local user only:
   ```bash
   ./install.sh
   ```
   Install system-wide for all users:
   ```bash
   sudo ./install.sh
   ```

If installed for local user, service should automatically start. To start service immediately after installing system-wide:
```bash
systemctl --user daemon-reload
systemctl --user start openrgb_nightmode_kde.service
```

## Uninstallation
If installed only for local user:
```bash
./uninstall.sh
```
If installed system-wide for all users:
```bash
sudo ./uninstall.sh
```
