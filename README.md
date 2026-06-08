# 🏓 Ping Pong

A lightweight task manager. Threads, people, groups, due dates.

---

## Install

**1. Clone and set up**

```bash
git clone https://github.com/MarinaMancoridis/PingPong.git
cd PingPong
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

**2. Run**

```bash
source venv/bin/activate   # skip if already active
uvicorn main:app --reload
```

Open **[localhost:8000](http://localhost:8000)** in Chrome.

---

## Add to your Dock (Mac)

Ping Pong works as a standalone app — no browser chrome, lives in your Dock.

1. Open [localhost:8000](http://localhost:8000) in **Chrome**
2. Click the **install icon** (⊕) in the address bar → **Install**
3. The app opens in its own window. Find it in Launchpad or Spotlight (`Ping Pong`)
4. Right-click its Dock icon → **Options → Keep in Dock**

Next time, just click the Dock icon — it starts the server automatically if you have it set up as a background service, or run `uvicorn main:app` first if you prefer manual control.

---

## Tips

- **Threads** — group tasks by topic, project, or anything you like
- **People** — assign tasks; filter to just your own with the **Me** button
- **Effort** — tag tasks as Mindless / Standard / Intense; filter in Me mode
- **Search** — find tasks by content or person name from the nav bar
- **Export** — download a CSV snapshot from any thread's sidebar
