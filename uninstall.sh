#!/usr/bin/env bash

if [ $UID -eq 0 ]; then
    echo "Uninstalling system-wide for all users."
    BIN_DIR=/usr/local/bin
    SYSTEMD_UNIT_DIR=/usr/local/lib/systemd/user
    SYSTEMCTL_DAEMON_RELOAD='systemctl daemon-reload'
    SYSTEMCTL_DISABLE='systemctl --global disable'
else
    echo "Uninstalling for current user."
    echo "(run as root to uninstall system-wide)"
    if [ -z "$HOME" ]; then
        echo "ERROR: \$HOME not set!" >&2
        exit 2
    fi
    BIN_DIR="$HOME/.local/bin"
    SYSTEMD_UNIT_DIR="$HOME/.config/systemd/user"
    SYSTEMCTL_DAEMON_RELOAD='systemctl --user daemon-reload'
    SYSTEMCTL_DISABLE='systemctl --user disable'
fi

if [ "$UID" -ne 0 ]; then
    systemctl --user stop openrgb_nightmode_kde.service
fi

$SYSTEMCTL_DISABLE openrgb_nightmode_kde.service

rm -f "$BIN_DIR/openrgb_nightmode_kde.py"
rm -f "$SYSTEMD_UNIT_DIR/openrgb_nightmode_kde.service"

$SYSTEMCTL_DAEMON_RELOAD
