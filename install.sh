#!/bin/sh
WORK_DIR="$HOME/Automation_Server"

# Update package list
sudo apt update

# Install dependencies
sudo apt install -y xorg openbox xauth python3 python3-pip python3-venv python-is-python3

# Create virtual environment
python3 -m venv "$WORK_DIR/venv"

# Install Python dependencies
"$WORK_DIR/venv/bin/pip" install -r "$WORK_DIR/requirements.txt"

# Change X11 permissions
sudo sed -i 's/allowed_users=console/allowed_users=anybody/' /etc/X11/Xwrapper.config

# Autologin
sudo cp /etc/systemd/system/getty.target.wants/getty@tty1.service /etc/systemd/system/
sudo sed -i 's/ExecStart=.*/ExecStart=-\/sbin\/agetty --autologin rpiserver --noclear - $TERM/' /etc/systemd/system/getty@tty1.service

sudo systemctl daemon-reload
sudo systemctl enable getty@tty1.service

# Create service files
chmod +x $WORK_DIR/service/service.sh

mkdir -p $HOME/.config/systemd/user

tee $HOME/.config/systemd/user/automation_server.service << 'EOF'
[Unit]
Description=Automation Server
After=network-online.target
Wants=network-online.target

[Service]
ExecStart=%h/Automation_Server/venv/bin/python %h/Automation_Server/src/server.py
Restart=always
RestartSec=5
WorkingDirectory=%h/Automation_Server

[Install]
WantedBy=default.target
EOF

tee $HOME/.config/systemd/user/automation_gui.service << 'EOF'
[Unit]
Description=Automation GUI
After=default.target

[Service]
ExecStart=%h/Automation_Server/service/service.sh
Restart=always
WorkingDirectory=%h/Automation_Server

[Install]
WantedBy=default.target
EOF

# Enable services
systemctl --user enable automation_server.service
systemctl --user enable automation_gui.service

# Reboot