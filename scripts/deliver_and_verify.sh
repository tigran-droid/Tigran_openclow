#!/bin/sh
# Deliver the brief in a way that the agent cannot cut short, and clear the
# folder afterwards so nothing can ever be delivered twice.
#
# Why the detaching (17 Aug 2026): the agent called deliver.py and finished its
# turn in the same breath without waiting. The turn ended, deliver.py was killed
# after 4 of 9 messages, and the agent reported a complete delivery it had never
# seen. setsid puts deliver.py in a session of its own, so every send finishes
# even if the agent stops waiting. We then poll its log and print what actually
# happened, so the agent has a real result to report instead of a guess.
#
# Why the clearing (17 Aug 2026, same day): on the next run the agent saw the
# files still sitting in /root/brief, copied them, and delivered yesterday's
# text again - old headers, old wording, no new voice note - instead of writing
# the brief. Prose telling it to empty the folder first was already in SYSTEM.md
# and was skipped. So the files are moved out of reach here instead: after a
# confirmed delivery this folder holds no parts at all, and the next run has
# nothing to reuse. If the agent then tries to deliver without writing,
# deliver.py's own check fails with "Nothing sent. Missing: ...".

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

        # Only retire the files once they have actually gone out. "Nothing sent"
        # means they were never delivered, so leave them alone to be fixed.
        if grep -qE '^Sent [0-9]+ text' "$LOG"; then
            ARCHIVE="$DIR/last-sent"
            rm -rf "$ARCHIVE"
            mkdir -p "$ARCHIVE"
            mv "$DIR"/[0-9][0-9]-*.txt "$ARCHIVE"/ 2>/dev/null
            mv "$DIR"/voice-*.txt      "$ARCHIVE"/ 2>/dev/null
            echo "(parts moved to $ARCHIVE - write all ten fresh next run)"
        fi
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
