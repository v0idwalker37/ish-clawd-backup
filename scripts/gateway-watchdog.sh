#!/bin/bash
# Gateway watchdog - checks if openclaw-gateway is running, restarts if not
if ! pgrep -f "openclaw-gateway" > /dev/null 2>&1; then
    echo "$(date): Gateway down, restarting..." >> /tmp/openclaw/watchdog.log
    systemctl --user restart openclaw-gateway
else
    MINUTE=$(date +%M)
    if [ "$MINUTE" = "00" ]; then
        echo "$(date): Gateway OK (pid $(pgrep -f openclaw-gateway))" >> /tmp/openclaw/watchdog.log
    fi
fi
