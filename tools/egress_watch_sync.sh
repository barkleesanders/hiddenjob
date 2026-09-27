#!/usr/bin/env bash
# Watch VM egress; when it recovers, run the hiddenjob discovery sync.
# Logs to ~/workspace/hiddenjob/.hiddenjob/watcher.log
set -u
LOG="$HOME/workspace/hiddenjob/.hiddenjob/watcher.log"
echo "$(date -u +%FT%TZ) watcher: started" >> "$LOG"
for i in $(seq 1 90); do
  if curl -s -o /dev/null -m 10 https://example.com 2>/dev/null; then
    echo "$(date -u +%FT%TZ) watcher: egress OK after $i checks; starting sync" >> "$LOG"
    cd "$HOME/workspace/hiddenjob" && python3 -u hiddenjob.py sync --limit 10 --ats-timeout 12 >> .hiddenjob/sync_run.log 2>&1
    echo "SYNC EXIT: $?" >> .hiddenjob/sync_run.log
    echo "$(date -u +%FT%TZ) watcher: sync finished" >> "$LOG"
    DB="$HOME/workspace/hiddenjob/.hiddenjob/hiddenjob.sqlite3"
    sqlite3 "$DB" "SELECT COUNT(*), COUNT(DISTINCT source) FROM jobs;" >> "$LOG"
    exit 0
  fi
  sleep 120
done
echo "$(date -u +%FT%TZ) watcher: egress never recovered in 3h; giving up" >> "$LOG"
exit 1
