#!/bin/bash
# Monitor HDD hash job and start copy when complete

DB_PATH="/home/ungouge/clawd/projects/hdd-consolidate/index.db"
LOG_PATH="/home/ungouge/clawd/projects/hdd-consolidate/monitor.log"
COPY_SCRIPT="/home/ungouge/clawd/projects/hdd-consolidate/copy_files.py"

log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG_PATH"
}

check_remaining() {
    python3 << EOF
import sqlite3
conn = sqlite3.connect('$DB_PATH')
c = conn.cursor()
c.execute("SELECT COUNT(*) FROM files WHERE hash IS NULL OR hash = ''")
remaining = c.fetchone()[0]
conn.close()
print(remaining)
EOF
}

log "=== HDD Monitor Started ==="
log "Will check every 5 minutes for completion"

while true; do
    REMAINING=$(check_remaining 2>/dev/null)
    
    if [ -z "$REMAINING" ]; then
        log "ERROR: Could not check database"
        sleep 300  # 5 min
        continue
    fi
    
    log "Remaining files to hash: $REMAINING"
    
    if [ "$REMAINING" -eq 0 ]; then
        log "✅ HASHING COMPLETE! Starting copy process..."
        
        # Check if copy script exists
        if [ ! -f "$COPY_SCRIPT" ]; then
            log "⚠️  Copy script not found at $COPY_SCRIPT"
            log "Waiting for Ish to write the copy script..."
            exit 0
        fi
        
        # Start the copy process
        cd /home/ungouge/clawd/projects/hdd-consolidate
        log "Starting: python3 copy_files.py"
        python3 copy_files.py >> copy_output.log 2>&1 &
        COPY_PID=$!
        
        log "Copy process started (PID: $COPY_PID)"
        log "Monitor with: tail -f ~/clawd/projects/hdd-consolidate/copy_output.log"
        
        exit 0
    fi
    
    # Wait 5 minutes before next check
    sleep 300
done
