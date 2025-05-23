import curses
import os
import time
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
    stdscr.nodelay(True)  # Non-blocking input
    reminders = load_reminders()
    input_str = ""
    selected = 0
    scroll = 0
    figlet = Figlet(font='standard')
    last_input_time = time.time()
    selection_visible = True

    while True:
        max_y, max_x = stdscr.getmaxyx()
        stdscr.clear()
        stdscr.addstr(0, 0, "Fignotes - Type and Enter to add, ↑/↓ to select, PgUp/PgDn=scroll, ctrl+d=delete, q=quit", curses.A_BOLD)
        row = 2

        # Prepare figlet-rendered reminders and their heights
        rendered_reminders = []
        for reminder in reminders:
            rendered = figlet.renderText(reminder)
            lines = rendered.splitlines()
            rendered_reminders.append(lines)

        # Calculate total lines and scrolling
        total_lines = sum(len(lines) + 1 for lines in rendered_reminders)
        visible_lines = max_y - 3  # 2 for header, 1 for input

        # Flatten reminders with their idx for scrolling
        flat = []
        for idx, lines in enumerate(rendered_reminders):
            for i, line in enumerate(lines):
                flat.append((idx, i, line))
            flat.append((None, None, ""))  # Spacer

        # Clamp scroll
        max_scroll = max(0, len(flat) - visible_lines)
        scroll = min(scroll, max_scroll)
        scroll = max(scroll, 0)

        # Draw visible portion
        display_flat = flat[scroll:scroll + visible_lines]
        drawn_idxs = set()
        for disp_row, (idx, i, line) in enumerate(display_flat, start=2):
            highlight = idx is not None and idx == selected and selection_visible
            if highlight:
                stdscr.attron(curses.A_REVERSE)
                drawn_idxs.add(disp_row)
            try:
                stdscr.addstr(disp_row, 2, line[:max_x-3])
            except curses.error:
                pass
            if highlight:
                stdscr.attroff(curses.A_REVERSE)

        # Only print input prompt if there's space
        if 2 + len(display_flat) < max_y:
            stdscr.addstr(2 + len(display_flat), 0, "Add: " + input_str[:max_x-6])
        stdscr.refresh()

        # Hide selection after 2 seconds of inactivity
        if time.time() - last_input_time > 2:
            selection_visible = False
        else:
            selection_visible = True

        c = stdscr.getch()
        if c != -1:
            last_input_time = time.time()  # Reset timer on any keypress

        if c == curses.KEY_UP:
            selected = max(0, selected - 1)
            # Scroll up if selected is above visible
            sel_line = 0
            for idx, lines in enumerate(rendered_reminders):
                if idx == selected:
                    break
                sel_line += len(lines) + 1
            if sel_line < scroll:
                scroll = sel_line
        elif c == curses.KEY_DOWN:
            selected = min(len(reminders) - 1, selected + 1) if reminders else 0
            # Scroll down if selected is below visible
            sel_line = 0
            for idx, lines in enumerate(rendered_reminders):
                if idx == selected:
                    break
                sel_line += len(lines) + 1
            if sel_line >= scroll + visible_lines:
                scroll = sel_line - visible_lines + 1
        elif c == curses.KEY_NPAGE:  # Page Down
            scroll = min(scroll + visible_lines, max_scroll)
        elif c == curses.KEY_PPAGE:  # Page Up
            scroll = max(scroll - visible_lines, 0)
        elif c == ord('q'):
            break
        elif c == 4 and reminders:  # Ctrl+D
            reminders.pop(selected)
            selected = min(selected, len(reminders) - 1)
            save_reminders(reminders)
            # Recalculate scroll after delete
            scroll = 0
            for idx, lines in enumerate(rendered_reminders):
                if idx == selected:
                    break
                scroll += len(lines) + 1
            scroll = max(0, min(scroll, max_scroll))
        elif c in (curses.KEY_BACKSPACE, 127, 8):
            input_str = input_str[:-1]
        elif c == 10:  # Enter
            if input_str.strip():
                reminders.append(input_str.strip())
                save_reminders(reminders)
                input_str = ""
                selected = len(reminders) - 1
                # Scroll to new reminder
                scroll = 0
                for idx, lines in enumerate(rendered_reminders):
                    if idx == selected:
                        break
                    scroll += len(lines) + 1
                scroll = max(0, min(scroll, max_scroll))
        elif 32 <= c <= 126:
            input_str += chr(c)
        else:
            time.sleep(0.05)  # Prevent high CPU usage

if __name__ == "__main__":
    curses.wrapper(lambda stdscr: (
        curses.start_color(),
        curses.use_default_colors(),
        curses.init_pair(1, curses.COLOR_BLACK, -1),
        main(stdscr)
    ))