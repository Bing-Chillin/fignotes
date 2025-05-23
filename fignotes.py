import curses
import os
from pyfiglet import Figlet

REMINDER_FILE = os.path.expanduser("~/.fignotes.txt")

def load_reminders():
    if not os.path.exists(REMINDER_FILE):
        return []
    with open(REMINDER_FILE, "r") as f:
        return [line.strip() for line in f if line.strip()]

def save_reminders(reminders):
    with open(REMINDER_FILE, "w") as f:
        for r in reminders:
            f.write(r + "\n")

def main(stdscr):
    curses.curs_set(1)
    stdscr.nodelay(False)
    reminders = load_reminders()
    input_str = ""
    selected = 0
    figlet = Figlet(font='standard')

    while True:
        stdscr.clear()
        max_y, max_x = stdscr.getmaxyx()
        stdscr.addstr(0, 0, "Fignotes - Type and Enter to add, ↑/↓ to select, ctrl+d=delete, q=quit", curses.A_BOLD)
        row = 2
        for idx, reminder in enumerate(reminders):
            rendered = figlet.renderText(reminder)
            lines = rendered.splitlines()
            for i, line in enumerate(lines):
                if row + i >= max_y - 2:
                    break  # Prevent writing out of bounds
                if idx == selected:
                    stdscr.attron(curses.color_pair(1))
                try:
                    stdscr.addstr(row + i, 2, line[:max_x-3])
                except curses.error:
                    pass
                if idx == selected:
                    stdscr.attroff(curses.color_pair(1))
            row += len(lines) + 1
            if row >= max_y - 2:
                break  # Stop if no more space
        # Only print input prompt if there's space
        if row < max_y:
            stdscr.addstr(row, 0, "Add: " + input_str[:max_x-6])
        stdscr.refresh()

        c = stdscr.getch()
        if c == curses.KEY_UP:
            selected = max(0, selected - 1)
        elif c == curses.KEY_DOWN:
            selected = min(len(reminders) - 1, selected + 1) if reminders else 0
        elif c == ord('q'):
            break
        elif c == 4 and reminders:  # Ctrl+D
            reminders.pop(selected)
            selected = min(selected, len(reminders) - 1)
            save_reminders(reminders)
        elif c in (curses.KEY_BACKSPACE, 127, 8):
            input_str = input_str[:-1]
        elif c == 10:  # Enter
            if input_str.strip():
                reminders.append(input_str.strip())
                save_reminders(reminders)
                input_str = ""
                selected = len(reminders) - 1
        elif 32 <= c <= 126:
            input_str += chr(c)

if __name__ == "__main__":
    curses.wrapper(lambda stdscr: (
        curses.start_color(),
        curses.init_pair(1, curses.COLOR_BLACK, curses.COLOR_WHITE),
        main(stdscr)
    ))