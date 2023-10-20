#!/usr/bin/env bash

if [[ " $* " =~ " -h " ]]; then
    cat <<'EOF'
Install for current user:
    ./install
Install system-wide for all users:
    sudo ./install
Skip "Continue? [y/N]" prompt:
    ./install -y
OR
    sudo ./install -y
EOF
    exit 0
fi

if [ $UID -eq 0 ]; then
    echo "Installing system-wide for all users."
    BIN_DIR=/usr/local/bin
    SYSTEMD_UNIT_DIR=/usr/local/lib/systemd/user
    SYSTEMCTL_DAEMON_RELOAD='systemctl daemon-reload'
    SYSTEMCTL_ENABLE='systemctl --global enable'
else
    echo "Installing for current user."
    echo "(run as root to install system-wide)"
    if [ -z "$HOME" ]; then
        echo "ERROR: \$HOME not set!" >&2
        exit 2
    fi
    BIN_DIR="$HOME/.local/bin"
    SYSTEMD_UNIT_DIR="$HOME/.config/systemd/user"
    SYSTEMCTL_DAEMON_RELOAD='systemctl --user daemon-reload'
    SYSTEMCTL_ENABLE='systemctl --user enable'
fi

if [ -z "$DESTDIR" ] && [[ ! " $* " =~ " -y " ]]; then
    read -rp "Continue? [y/N]: " yn
    case $yn in
    y | Y | yes)
        :
        ;;
    *)
        echo exiting...
        exit
        ;;
    esac
fi

mkdir -p "$DESTDIR/$BIN_DIR"
install -m 755 openrgb_nightmode_kde.py "$DESTDIR/$BIN_DIR"

mkdir -p "$DESTDIR/$SYSTEMD_UNIT_DIR"
cat <<EOF > "$DESTDIR/$SYSTEMD_UNIT_DIR/openrgb_nightmode_kde.service"
[Unit]
Description=Follow KDE nightcolor color temperature with OpenRGB

[Service]
ExecStart=/usr/bin/python -u $BIN_DIR/openrgb_nightmode_kde.py
Restart=on-failure
RestartSec=10

[Install]
WantedBy=default.target
EOF

if [ -z "$DESTDIR" ]; then
    $SYSTEMCTL_DAEMON_RELOAD
    $SYSTEMCTL_ENABLE "$SYSTEMD_UNIT_DIR/openrgb_nightmode_kde.service"
    if [ $UID -eq 0 ]; then
        echo "Service will start on next login, or start now with:"
        echo "systemctl --user daemon-reload"
        echo "systemctl --user start openrgb_nightmode_kde.service"
    else
        echo "Starting openrgb_nightmode_kde.service ..."
        systemctl --user start openrgb_nightmode_kde.service
    fi
fi

echo "Installation complete :3"

exit 0
