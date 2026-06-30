# 🎨 Palette

A lightweight personal task manager. Threads, groups, due dates, and deadlines — no assignees, no effort tags, just your tasks.

---

## Install

**1. Set up**

```bash
cd ~/Palette
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

**2. Run**

```bash
source .venv/bin/activate   # skip if already active
uvicorn main:app --reload
```

Open **[localhost:8000](http://localhost:8000)** in Safari (or any browser).

---

## Run it as a standalone Mac app

A `Palette.app` launcher is included. Double-click it and Palette opens in its **own
native window** — no browser, no tabs, no terminal. (It uses macOS's built-in WebKit
via `pywebview`, started by `desktop.py`.) Closing the window stops the app.

1. Double-click **`Palette.app`** (in this folder).
2. Palette opens in a standalone window with a 🎨 Dock icon.
3. To keep it handy: right-click its Dock icon → **Options → Keep in Dock**.

> The project lives at `~/Palette` (outside macOS-protected folders like Desktop/
> Documents, so it launches with no permission prompts). The launcher expects the
> project at that path — if you move the folder, edit the `PROJECT` line in
> `Palette.app/Contents/MacOS/Palette`.

Prefer a browser instead? Just run `uvicorn main:app --reload` and open
[localhost:8000](http://localhost:8000).

---

## Features

- **Threads** — group tasks by topic or project. Rename or delete a thread from its card header.
- **Groups** — bundle threads into folders. Create from the sidebar; click a group's ✎ to rename it, add/remove threads, or delete it.
- **Due dates & deadlines** — set ASAP / Anytime / a specific date; flag the important ones as deadlines and filter the sidebar to just those.
- **Notes** — click a task to jot a note.
- **Search** — find tasks by description or thread name from the nav bar.
