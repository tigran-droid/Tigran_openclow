#!/bin/sh
# Deliver the brief in a way that the agent cannot cut short.
#
# Why this exists (17 Aug 2026): the agent called deliver.py and finished its
# turn in the same breath without waiting. The turn ended, deliver.py was killed
# after 4 of 9 messages, and the agent reported a complete delivery it had never
# seen. Chrisy would have received a briefing, the news, one voice note and one
# post - and nothing else.
#
# setsid puts deliver.py in a session of its own, so all nine sends finish even
# if the agent stops waiting. We then poll its log and print what actually
# happened, so the agent has a real result to report instead of a guess.

TO="${1:?usage: deliver_and_verify.sh <chat-id> [brief-dir]}"
DIR="${2:-/root/brief}"
LOG="$DIR/deliver.log"

: > "$LOG"
setsid nohup python3 /root/deliver.py --to "$TO" --dir "$DIR" >>"$LOG" 2>&1 &

# deliver.py prints exactly one summary line when it finishes:
#   "Sent N text messages and M voice notes."   or   "Nothing sent. Missing: ..."
i=0
while [ "$i" -lt 72 ]; do          # 72 * 5s = 6 minutes
    if grep -qE '^(Sent [0-9]+ text|Nothing sent)' "$LOG" 2>/dev/null; then
        cat "$LOG"
        exit 0
    fi
    sleep 5
    i=$((i + 1))
done

echo "DELIVERY NOT CONFIRMED after 6 minutes. It is still running detached and"
echo "will finish on its own, but you have NOT seen a result - say exactly that."
echo "--- log so far ---"
cat "$LOG"
exit 1
