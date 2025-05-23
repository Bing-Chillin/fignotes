#!/bin/bash

REMINDER_FILE="$HOME/.fignotes.txt"

# Check if figlet is installed
if ! command -v figlet &> /dev/null; then
    echo "figlet is not installed. Install it with: yay -S figlet"
    exit 1
fi

usage() {
    echo "Usage:"
    echo "  $0 --add -a \"Reminder text\"      Add a new reminder"
    echo "  $0 --list -l                       List all reminders"
    echo "  $0 --remove -r n                   Remove reminder nth reminder"
    echo "  $0 --show -s                       Show all reminders with figlet"
    exit 1
}

if [ $# -eq 0 ]; then
    usage
fi

case "$1" in
    --add|-a)
        shift
        if [ $# -eq 0 ]; then
            echo "Please provide a reminder to add."
            exit 1
        fi
        echo "$*" >> "$REMINDER_FILE"
        echo "Reminder added."
        ;;
    --list|-l)
        if [ ! -f "$REMINDER_FILE" ] || [ ! -s "$REMINDER_FILE" ]; then
            echo "No reminders found."
            exit 0
        fi
        nl -w2 -s'. ' "$REMINDER_FILE"
        ;;
    --remove|-r)
        shift
        if [ $# -eq 0 ]; then
            echo "Please provide the reminder number to remove."
            exit 1
        fi
        if [ ! -f "$REMINDER_FILE" ]; then
            echo "No reminders to remove."
            exit 1
        fi
        sed -i "${1}d" "$REMINDER_FILE"
        echo "Reminder $1 removed."
        ;;
    --show|-s)
        if [ ! -f "$REMINDER_FILE" ] || [ ! -s "$REMINDER_FILE" ]; then
            echo "No reminders to show."
            exit 0
        fi
        echo -e "\033[1;33m"
        while IFS= read -r line; do
            figlet "$line"
        done < "$REMINDER_FILE"
        echo -e "\033[0m"
        ;;
    *)
        usage
        ;;
esac