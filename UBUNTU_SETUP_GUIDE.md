# Ubuntu Setup Guide for OpenClaw/Ungouge Development

**Target Machine:** Intel i9-9980XE, 32GB RAM, GTX 1080 Ti, NVMe storage  
**OS:** Ubuntu 24.04 LTS (Noble Numbat)  
**Purpose:** OpenClaw + Ungouge development environment

---

## Phase 1: Ubuntu Installation

### Download Ubuntu 24.04 LTS

1. Go to: https://ubuntu.com/download/desktop
2. Download: **Ubuntu 24.04 LTS Desktop** (ISO file)
3. Create bootable USB:
   - **Windows:** Use Rufus (https://rufus.ie)
   - **Mac:** Use balenaEtcher (https://etcher.balena.io)
   - **Linux:** `sudo dd if=ubuntu-24.04.iso of=/dev/sdX bs=4M status=progress`

### Installation Steps

1. **Boot from USB**
   - Insert USB, restart machine
   - Press F12/F2/DEL (depends on motherboard) to enter boot menu
   - Select USB drive

2. **Install Ubuntu**
   - Choose "Install Ubuntu"
   - Language: English
   - Keyboard: US (or your preference)
   - **Updates:** Download updates during installation ✓
   - **Third-party software:** Install third-party software ✓ (for NVIDIA drivers)

3. **Installation Type**
   - Choose: "Erase disk and install Ubuntu"
   - **Enable encryption:** ✓ (use a strong passphrase you'll remember)
   - Choose: "Use LVM" ✓

4. **Time Zone**
   - Select: America/New_York (EST)

5. **User Account**
   - Your name: Jason (or whatever)
   - Computer name: `ungouge-dev` (or `ish-workstation`)
   - Username: `jason` (lowercase)
   - Password: (strong password)
   - **Require password to log in:** ✓

6. **Complete Installation**
   - Wait 15-20 minutes
   - Remove USB when prompted
   - Restart

---

## Phase 2: Initial System Setup

Open Terminal (Ctrl+Alt+T) and run these commands:

### Update System
```bash
sudo apt update && sudo apt upgrade -y
sudo apt autoremove -y
sudo reboot
```

### Install Essential Tools
```bash
sudo apt install -y \
  build-essential \
  git \
  curl \
  wget \
  vim \
  htop \
  tmux \
  zip \
  unzip \
  tree \
  net-tools \
  openssh-server \
  ca-certificates \
  gnupg \
  lsb-release \
  software-properties-common
```

### Enable SSH (for remote access)
```bash
sudo systemctl enable ssh
sudo systemctl start ssh
# Get your IP address
ip addr show | grep "inet " | grep -v 127.0.0.1
```

---

## Phase 3: Install Development Tools

### Install Node.js 24 (via nvm)
```bash
# Install nvm
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.40.0/install.sh | bash

# Reload shell config
source ~/.bashrc

# Install Node 24
nvm install 24
nvm use 24
nvm alias default 24

# Verify
node --version  # Should show v24.x.x
npm --version
```

### Install Python 3.12
```bash
# Ubuntu 24.04 comes with Python 3.12 by default
python3 --version

# Install pip and venv
sudo apt install -y python3-pip python3-venv

# Install common Python tools
pip3 install --user --upgrade pip setuptools wheel
```

### Install Docker
```bash
# Add Docker's official GPG key
sudo install -m 0755 -d /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg
sudo chmod a+r /etc/apt/keyrings/docker.gpg

# Add Docker repository
echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu \
  $(lsb_release -cs) stable" | \
  sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

# Install Docker
sudo apt update
sudo apt install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin

# Add your user to docker group (no sudo needed)
sudo usermod -aG docker $USER

# Reboot to apply group changes
sudo reboot
```

After reboot, verify Docker:
```bash
docker --version
docker run hello-world
```

---

## Phase 4: Install OpenClaw

### Download and Install
```bash
# Download OpenClaw
cd ~
curl -fsSL https://openclaw.com/install.sh | bash

# Or manual install:
# wget https://github.com/openclaw/openclaw/releases/latest/download/openclaw-linux-x64.tar.gz
# tar -xzf openclaw-linux-x64.tar.gz
# sudo mv openclaw /usr/local/bin/

# Verify installation
openclaw --version
```

### Initialize OpenClaw
```bash
# Start OpenClaw gateway
openclaw gateway start

# Check status
openclaw status
```

---

## Phase 5: Restore Workspace from Backup

### Option A: From Google Drive

1. Install Google Drive client:
```bash
# Install rclone (Google Drive CLI client)
sudo apt install -y rclone

# Configure Google Drive
rclone config
# Follow prompts:
# - New remote: name it "gdrive"
# - Storage: Google Drive
# - OAuth in browser (will open browser for auth)
```

2. Download workspace backup:
```bash
# Create workspace directory
mkdir -p ~/clawd

# List available backups
rclone ls gdrive:"Ungouge_Backups"

# Download latest backup
rclone copy gdrive:"Ungouge_Backups/2026-02-12/" ~/clawd/ --progress

# Or sync entire shared drive
rclone sync gdrive:"Ungouge.ai/" ~/clawd/ --progress
```

### Option B: From GitHub (once repos are set up)

```bash
cd ~
git clone https://github.com/yourusername/ungouge-app.git ~/clawd/projects/ungouge-app
git clone https://github.com/yourusername/ungouge-dashboard.git ~/clawd/projects/ungouge-dashboard
```

### Option C: Direct Copy from Mac (over network)

On Mac:
```bash
# Get Mac's IP address
ifconfig | grep "inet " | grep -v 127.0.0.1

# Start SSH if not running
sudo systemsetup -setremotelogin on
```

On Ubuntu:
```bash
# Copy workspace from Mac
rsync -avz --progress moltbot@<MAC_IP>:/Users/moltbot/clawd/ ~/clawd/
```

---

## Phase 6: Install Tailscale (Remote Access)

```bash
# Install Tailscale
curl -fsSL https://tailscale.com/install.sh | sh

# Start Tailscale
sudo tailscale up

# Get your Tailscale IP
tailscale ip -4
```

**On your other devices (laptop, phone):**
- Install Tailscale
- Log in with same account
- You can now SSH from anywhere: `ssh jason@<tailscale-ip>`

---

## Phase 7: Configure OpenClaw

### Edit OpenClaw config
```bash
cd ~/clawd
vim openclaw.json
# or
nano openclaw.json
```

Key settings to verify:
- `workingDirectory`: `/home/jason/clawd`
- `model`: `anthropic/claude-sonnet-4-5`
- `thinkingDefault`: `"high"`
- Telegram credentials (if not already set)

### Set up service credentials

1. **Google Cloud:**
```bash
# Install gcloud CLI
curl https://sdk.cloud.google.com | bash
exec -l $SHELL
gcloud init
# Follow prompts to authenticate as void@ungouge.ai
```

2. **Authenticate OpenClaw services:**
```bash
# GitHub (once you're ready)
gh auth login

# Gmail OAuth
cd ~/clawd/skills/email
# Run the OAuth flow to regenerate token.json
python3 scripts/gmail-setup.py
```

---

## Phase 8: Install Project Dependencies

### Ungouge Dashboard
```bash
cd ~/clawd/projects/ungouge-dashboard/backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
deactivate
```

### Ungouge App
```bash
cd ~/clawd/projects/ungouge-app/backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
deactivate

cd ~/clawd/projects/ungouge-app/frontend
npm install
```

---

## Phase 9: Test Everything

### Test OpenClaw
```bash
openclaw status
# Should show: gateway running, agent main active
```

### Test scraper (quick test)
```bash
cd ~/clawd/projects/ungouge-app
python3 scripts/quote_scraper/scraper.py --sources reddit --max-quotes 5 --max-hours 0.1
```

### Test dashboard deployment
```bash
cd ~/clawd/projects/ungouge-dashboard
bash DEPLOY_DASHBOARD.sh
```

---

## Phase 10: Set Up Automated Backups

### Create backup script
```bash
vim ~/backup-clawd.sh
```

Paste this:
```bash
#!/bin/bash
DATE=$(date +%Y-%m-%d)
BACKUP_DIR=~/clawd-backups/$DATE
mkdir -p $BACKUP_DIR

# Backup workspace
rsync -av --exclude 'node_modules' --exclude 'venv' --exclude '__pycache__' \
  ~/clawd/ $BACKUP_DIR/

# Sync to Google Drive
rclone sync ~/clawd-backups/ gdrive:"Ungouge_Backups/" --progress

echo "Backup complete: $BACKUP_DIR"
```

Make executable:
```bash
chmod +x ~/backup-clawd.sh
```

### Schedule daily backups (cron)
```bash
crontab -e
```

Add this line (runs at 3 AM daily):
```
0 3 * * * /home/jason/backup-clawd.sh >> /home/jason/backup.log 2>&1
```

---

## Phase 11: Performance Tuning (Optional)

### Enable CPU performance mode
```bash
# Install cpufreq tools
sudo apt install -y cpufrequtils

# Set to performance mode
sudo cpufreq-set -r -g performance

# Make permanent
echo 'GOVERNOR="performance"' | sudo tee /etc/default/cpufrequtils
sudo systemctl restart cpufrequtils
```

### Monitor system resources
```bash
# Install monitoring tools
sudo apt install -y htop iotop iftop

# Real-time monitoring
htop  # CPU/RAM
iotop  # Disk I/O (requires sudo)
iftop  # Network (requires sudo)
```

---

## Troubleshooting

### If OpenClaw won't start:
```bash
openclaw gateway stop
openclaw gateway start --verbose
openclaw logs
```

### If Node/npm issues:
```bash
nvm list
nvm use 24
npm cache clean --force
```

### If Python venv issues:
```bash
deactivate
rm -rf venv
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### If Docker permission issues:
```bash
sudo usermod -aG docker $USER
# Then log out and log back in
```

---

## Final Checklist

- [ ] Ubuntu 24.04 LTS installed with encryption
- [ ] System updated and essential tools installed
- [ ] Node.js 24 installed via nvm
- [ ] Python 3.12 with pip and venv working
- [ ] Docker installed and user added to docker group
- [ ] OpenClaw installed and gateway running
- [ ] Workspace restored from backup (Google Drive / rsync)
- [ ] Tailscale installed for remote access
- [ ] Google Cloud CLI authenticated
- [ ] Project dependencies installed (dashboard + app)
- [ ] Test scraper runs successfully
- [ ] Daily backups scheduled via cron
- [ ] SSH access tested from laptop/phone

---

## Post-Migration: Update Memory Files

Once everything is working, I'll update:
- `USER.md` — new hardware specs
- `MEMORY.md` — migration date and notes
- `TOOLS.md` — Ubuntu-specific paths

---

## Estimated Timeline

- Phase 1-2 (Install + Setup): 45 minutes
- Phase 3-4 (Dev tools + OpenClaw): 30 minutes
- Phase 5 (Restore workspace): 15-30 minutes (depends on backup size)
- Phase 6-7 (Tailscale + Config): 15 minutes
- Phase 8 (Dependencies): 20 minutes
- Phase 9-10 (Testing + Backups): 20 minutes

**Total: ~2.5 hours active work**

---

## When You're Ready

Just say the word and we'll start. I can walk you through each phase in real-time if you want, or you can follow this guide at your own pace and ping me if you hit issues.

Let me know when you want to pull the trigger! 🚀
