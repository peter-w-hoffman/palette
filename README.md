# 🎨 Palette

A simple, private task manager for your Mac. Organize tasks into **threads**, bundle
threads into colored **groups**, set **due dates** and **deadlines**, jot notes, and
keep a **Today** scratchpad — all in its own desktop window. Everything is stored
locally on your computer; nothing is sent anywhere.

This guide gets you from zero to a working desktop app, even if you've never used a
terminal before. It takes about 5 minutes.

---

## What you'll need

- **A Mac.**
- **Python 3** (free). It's often already installed. To check, open the **Terminal**
  app (press `⌘ Space`, type `Terminal`, hit Return) and paste this, then press Return:

  ```bash
  python3 --version
  ```

  If you see something like `Python 3.12.x`, you're good. If it says "command not
  found," install Python from **https://www.python.org/downloads/** (download, open
  the installer, click through), then continue.

---

## Step 1 — Download Palette

Pick **one** of these.

### Option A — Terminal (recommended, most reliable)

Open Terminal and paste these lines one at a time (press Return after each). This puts
Palette in your home folder:

```bash
cd ~
git clone https://github.com/peter-w-hoffman/palette.git
```

You now have a folder called **`palette`** in your home folder.

> The very first time you use `git`, macOS may pop up a box offering to install the
> "command line developer tools." Click **Install**, wait for it to finish, then run the
> `git clone` line again.

> 💡 Tip: keep Palette in your **home folder** (as above) rather than in *Desktop* or
> *Documents*. macOS adds extra permission prompts for apps that run from those two
> folders.

### Option B — Download a ZIP (no terminal to download)

1. Go to **https://github.com/peter-w-hoffman/palette**
2. Click the green **`Code`** button → **Download ZIP**.
3. Double-click the downloaded ZIP to unzip it, then move the unzipped **`palette`**
   folder to your home folder (or wherever you like, just **not** Desktop/Documents).

---

## Step 2 — Set it up (one time only)

This creates a small private workspace for Palette and installs the few things it needs.
The reliable way that works for **both** download options is to run one line in Terminal:

```bash
cd ~/palette
bash setup.command
```

- If you used **Option B (ZIP)** and your folder isn't at `~/palette`: type `cd ` in
  Terminal (with a space after it), then **drag the `palette` folder from Finder onto the
  Terminal window** so it fills in the location, press Return, then run `bash setup.command`.

You'll see some text scroll by and finally **`✅ All set!`**. You only ever do this once.

> **Shortcut:** if you downloaded with **Option A (git clone)**, you can instead just
> **double-click `setup.command`** in Finder. (This doesn't work for ZIP downloads,
> because unzipping removes the file's "runnable" flag — so ZIP users should use the
> Terminal line above.)

---

## Step 3 — Open Palette as a desktop app

1. Open the `palette` folder in Finder and **double-click `Palette.app`**.
   - Palette opens in its **own window** with a 🎨 icon in your Dock — no web browser.
2. To keep it one click away: **right-click the 🎨 Dock icon → Options → Keep in Dock**.

That's it. From now on, just click the 🎨 icon in your Dock to open Palette. Closing the
window quits the app.

> The first time you open `Palette.app`, macOS may ask you to confirm (right-click →
> **Open** → **Open**). This only happens once.

---

## Using Palette

- **Threads** — a thread is a list of tasks (e.g. *Apartment hunt*). Create one with the
  **＋** next to "Threads". Rename or delete a thread from the buttons on its card.
- **Groups** — bundle related threads into a colored box. Create one with the **＋** next
  to "Groups", then click a group's **✎** to rename it, pick its **emoji** and **box
  color**, or choose which threads belong to it. Click a group to show/hide its threads.
- **Drag to organize** — drag thread cards anywhere on the canvas; drop one **into** a
  group's colored box to add it to that group, or **out** to remove it.
- **Due dates & deadlines** — give a task a date (or *ASAP* / *Anytime*) and flag the
  important ones as **deadlines**. The right-hand panel lists what's coming up.
- **Today** — a free notepad in the left column for the day's to-dos. Drag its edges to
  resize.
- **Search** — find tasks by name from the search box at the top.

---

## Troubleshooting

- **Double-clicking `Palette.app` does nothing / shows "Palette is not set up yet."**
  You haven't run **Step 2** yet, or it didn't finish. Run `setup.command` again.

- **"Palette can't be opened because it is from an unidentified developer."**
  Right-click `Palette.app` (or `setup.command`) → **Open** → **Open**. You only need to
  do this once per file.

- **A "Palette would like to access your Desktop/Documents folder" prompt appears.**
  Click **Allow**. (You can avoid this entirely by keeping the folder in your home
  folder instead of Desktop/Documents.)

- **`python3: command not found` during setup.**
  Install Python 3 from https://www.python.org/downloads/ and run `setup.command` again.

- **I'd rather use a normal browser.** From the `palette` folder run:

  ```bash
  ./.venv/bin/uvicorn main:app --reload
  ```

  then open **http://localhost:8000** in any browser.

---

## Updating to the latest version

If you downloaded with Option A (Terminal), get updates with:

```bash
cd ~/palette
git pull
bash setup.command   # only needed if the update changed requirements
```

---

## Notes for the curious

Palette is a small [FastAPI](https://fastapi.tiangolo.com/) app. `setup.command` creates
a Python virtual environment in `.venv` and installs `requirements.txt`. `Palette.app` is
a tiny launcher bundle that runs `desktop.py`, which starts the local server and shows it
in a native macOS window via [`pywebview`](https://pywebview.flowrl.com/). Your data lives
in a local `palette.db` SQLite file in the project folder.
