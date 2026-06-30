import random
import sqlite3
from contextlib import contextmanager
from datetime import date, timedelta
from typing import Optional

from fastapi import FastAPI, Form, Request
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse, Response
from fastapi.templating import Jinja2Templates
from PIL import Image, ImageDraw, ImageFont

app = FastAPI()
templates = Jinja2Templates(directory="templates")
DB = "palette.db"

# Emojis used as group icons.
EMOJIS = [
    # animals
    "🦊", "🐻", "🦁", "🐯", "🐺", "🦝", "🐨", "🦔", "🦦", "🦥",
    "🐸", "🦋", "🐙", "🦜", "🐬", "🦭", "🐲", "🦩", "🐝", "🦀",
    "🐧", "🦆", "🦉", "🦅", "🐦", "🦚", "🦤", "🐢", "🦎", "🐠",
    "🐡", "🦑", "🦞", "🐊", "🦏", "🦛", "🦒", "🦘", "🐘", "🦓",
    "🐿️", "🦫", "🦡", "🐇", "🐾",
    # nature & celestial
    "🌙", "⭐", "🌸", "🍀", "🌊", "🌋", "🌵", "🌴", "🍄", "🌺",
    "🌻", "🌹", "🍁", "❄️", "☄️", "🌪️", "🌈", "🔥", "💧", "🌿",
    # objects & symbols
    "🎯", "🎸", "🚀", "🔮", "🎪", "🍕", "🎩", "🎭", "🎨", "🎲",
    "🧩", "🎻", "🥁", "🎺", "🪗", "🎮", "🕹️", "🧸", "🪆", "🎠",
    "🏆", "🥇", "🔭", "🧪", "💡", "🔑", "🪄", "⚗️", "🧲",
    "🪁", "🛸", "🧊", "🪬", "🫧",
]

THREAD_COLORS = [
    "#4a90e2", "#e2844a", "#50b86c", "#9b6be2",
    "#e24a7a", "#4ab8e2", "#d4a23a", "#7a6be2",
]

# Curated swatches for group boxes (used as a soft tint behind grouped threads).
GROUP_COLORS = [
    "#4a90e2", "#50b86c", "#9b6be2", "#e2844a",
    "#e24a7a", "#4ab8e2", "#d4a23a", "#6b7280",
]


@contextmanager
def get_conn():
    conn = sqlite3.connect(DB)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
        conn.commit()
    finally:
        conn.close()


def init_db():
    with get_conn() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS threads (
                id         INTEGER PRIMARY KEY AUTOINCREMENT,
                name       TEXT NOT NULL,
                sort_order INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS groups (
                id         INTEGER PRIMARY KEY AUTOINCREMENT,
                name       TEXT NOT NULL,
                icon       TEXT DEFAULT '',
                color      TEXT DEFAULT '',
                sort_order INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        # Migrate older DBs: add the color column and backfill from the palette.
        g_cols = {r[1] for r in conn.execute("PRAGMA table_info(groups)").fetchall()}
        if "color" not in g_cols:
            conn.execute("ALTER TABLE groups ADD COLUMN color TEXT DEFAULT ''")
        for i, grp in enumerate(
            conn.execute("SELECT id FROM groups WHERE color IS NULL OR color = '' ORDER BY sort_order, created_at").fetchall()
        ):
            conn.execute("UPDATE groups SET color=? WHERE id=?",
                         (GROUP_COLORS[i % len(GROUP_COLORS)], grp["id"]))
        # Enforce one group per thread: keep only the earliest membership per thread.
        conn.execute("""
            DELETE FROM group_threads
            WHERE rowid NOT IN (SELECT MIN(rowid) FROM group_threads GROUP BY thread_id)
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS group_threads (
                group_id  INTEGER NOT NULL REFERENCES groups(id),
                thread_id INTEGER NOT NULL REFERENCES threads(id),
                PRIMARY KEY (group_id, thread_id)
            )
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS tasks (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                thread_id   INTEGER REFERENCES threads(id),
                description TEXT NOT NULL,
                due_date    TEXT,
                notes       TEXT,
                closed_at   TIMESTAMP,
                sort_order  INTEGER DEFAULT 0,
                is_deadline INTEGER DEFAULT 0,
                status      TEXT NOT NULL DEFAULT 'open',
                created_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS app_state (
                key   TEXT PRIMARY KEY,
                value TEXT
            )
        """)
        # Grandfather any NULL due_dates as ANYTIME.
        conn.execute("UPDATE tasks SET due_date = 'ANYTIME' WHERE due_date IS NULL")


def _get_state(conn, key, default=""):
    row = conn.execute("SELECT value FROM app_state WHERE key = ?", (key,)).fetchone()
    return row["value"] if row else default


def _set_state(conn, key, value):
    conn.execute(
        "INSERT INTO app_state (key, value) VALUES (?, ?) "
        "ON CONFLICT(key) DO UPDATE SET value = excluded.value",
        (key, value),
    )


def _pick_group_emoji(conn):
    used = {row[0] for row in conn.execute("SELECT icon FROM groups WHERE icon != ''").fetchall()}
    available = [e for e in EMOJIS if e not in used]
    return random.choice(available if available else EMOJIS)


init_db()


# ── Jinja2 filters ────────────────────────────────────────────────────────────

def fmt_date(s):
    if not s:
        return ""
    if s == 'ASAP':
        return "ASAP"
    if s == 'ANYTIME':
        return "Anytime"
    try:
        d = date.fromisoformat(s)
        today = date.today()
        if d == today:
            return "Today"
        if d == today + timedelta(days=1):
            return "Tomorrow"
        return d.strftime("%b %-d")
    except Exception:
        return s


def date_cls(s):
    if not s:
        return ""
    if s == 'ASAP':
        return "soon"
    if s == 'ANYTIME':
        return ""
    try:
        d = date.fromisoformat(s)
        today = date.today()
        if d < today:
            return "overdue"
        if d <= today + timedelta(days=2):
            return "soon"
        return "future"
    except Exception:
        return ""


templates.env.filters["fmt_date"] = fmt_date
templates.env.filters["date_cls"] = date_cls


# ── helpers ───────────────────────────────────────────────────────────────────

def _threads_with_tasks(conn):
    threads = conn.execute(
        "SELECT * FROM threads ORDER BY sort_order ASC, created_at ASC"
    ).fetchall()
    # thread_id -> its (single) group_id, if any
    thread_group = {r["thread_id"]: r["group_id"]
                    for r in conn.execute("SELECT thread_id, group_id FROM group_threads").fetchall()}
    result = []
    for i, thread in enumerate(threads):
        tasks = conn.execute("""
            SELECT * FROM tasks
            WHERE thread_id = ? AND status = 'open'
            ORDER BY sort_order ASC, created_at DESC
        """, (thread["id"],)).fetchall()

        result.append({
            "thread":     thread,
            "tasks":      tasks,
            "open_count": len(tasks),
            "color":      THREAD_COLORS[i % len(THREAD_COLORS)],
            "group_id":   thread_group.get(thread["id"]),
        })
    return result


def _groups_with_threads(conn):
    groups = conn.execute("SELECT * FROM groups ORDER BY sort_order, created_at").fetchall()
    result = []
    for g in groups:
        thread_ids = [r["thread_id"] for r in
                      conn.execute("SELECT thread_id FROM group_threads WHERE group_id = ?",
                                   (g["id"],)).fetchall()]
        result.append({"group": g, "thread_ids": thread_ids})
    return result


def _due_sidebar(conn, color_map, name_map, today):
    rows = conn.execute("""
        SELECT * FROM tasks
        WHERE status = 'open'
        ORDER BY
            CASE WHEN due_date IS NULL THEN 1 ELSE 0 END,
            due_date ASC,
            created_at ASC
    """).fetchall()

    overdue_tasks, asap_tasks, dated_tasks, anytime_tasks = [], [], [], []
    for row in rows:
        task = dict(row)
        task["thread_color"] = color_map.get(task["thread_id"], "#aaa")
        task["thread_name"] = name_map.get(task["thread_id"], "")
        d = task["due_date"]
        if not d or d == 'ANYTIME':
            anytime_tasks.append(task)
        elif d == 'ASAP':
            asap_tasks.append(task)
        else:
            try:
                if date.fromisoformat(d) < today:
                    overdue_tasks.append(task)
                else:
                    dated_tasks.append(task)
            except ValueError:
                anytime_tasks.append(task)

    upper_groups = []

    if overdue_tasks:
        upper_groups.append({
            "label": "Overdue", "cls": "overdue", "tasks": overdue_tasks,
        })

    if asap_tasks:
        upper_groups.append({
            "label": "ASAP", "cls": "asap", "tasks": asap_tasks,
        })

    dated_map, dated_order = {}, []
    for task in dated_tasks:
        d = date.fromisoformat(task["due_date"])
        if d == today:
            key, label, cls = "__today", "Today", "today"
        elif d == today + timedelta(days=1):
            key, label, cls = "__tomorrow", "Tomorrow", "tomorrow"
        else:
            key, label, cls = d.isoformat(), d.strftime("%a, %b %-d"), "future"
        if key not in dated_map:
            dated_map[key] = {"label": label, "cls": cls, "tasks": []}
            dated_order.append(key)
        dated_map[key]["tasks"].append(task)
    upper_groups.extend(dated_map[k] for k in dated_order)

    anytime_group = None
    if anytime_tasks:
        anytime_group = {"label": "Anytime", "cls": "anytime", "tasks": anytime_tasks}

    return upper_groups, anytime_group


# ── routes ────────────────────────────────────────────────────────────────────

_icon_cache = None


@app.get("/icon-192.png")
async def app_icon():
    global _icon_cache
    if _icon_cache is None:
        img = Image.new("RGBA", (192, 192), (0, 0, 0, 0))
        d   = ImageDraw.Draw(img)
        fnt = ImageFont.truetype("/System/Library/Fonts/Apple Color Emoji.ttc", 160)
        bb  = d.textbbox((0, 0), "🎨", font=fnt, embedded_color=True)
        x   = (192 - (bb[2] - bb[0])) // 2 - bb[0]
        y   = (192 - (bb[3] - bb[1])) // 2 - bb[1]
        d.text((x, y), "🎨", font=fnt, embedded_color=True)
        import io
        buf = io.BytesIO()
        img.save(buf, format="PNG")
        _icon_cache = buf.getvalue()
    return Response(content=_icon_cache, media_type="image/png",
                    headers={"Cache-Control": "public, max-age=86400"})


@app.get("/manifest.json")
async def manifest():
    return JSONResponse({
        "name": "Palette",
        "short_name": "Palette",
        "start_url": "/",
        "display": "standalone",
        "display_override": ["window-controls-overlay"],
        "background_color": "#f0efe9",
        "theme_color": "#f0efe9",
        "icons": [
            {"src": "/icon-192.png", "sizes": "192x192", "type": "image/png"}
        ]
    })


@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    today = date.today()
    with get_conn() as conn:
        threads_data = _threads_with_tasks(conn)
        color_map    = {td["thread"]["id"]: td["color"] for td in threads_data}
        name_map     = {td["thread"]["id"]: td["thread"]["name"] for td in threads_data}
        due_upper, due_anytime = _due_sidebar(conn, color_map, name_map, today)
        groups_data  = _groups_with_threads(conn)
        today_note   = _get_state(conn, "today", "")
    return templates.TemplateResponse(request, "index.html", {
        "threads_data":  threads_data,
        "due_upper":     due_upper,
        "due_anytime":   due_anytime,
        "today":         today.isoformat(),
        "groups_data":   groups_data,
        "today_note":    today_note,
        "all_emojis":    EMOJIS,
        "group_colors":  GROUP_COLORS,
    })


# Tasks

@app.post("/tasks/reorder")
async def reorder_tasks(request: Request):
    data = await request.json()
    with get_conn() as conn:
        for i, tid in enumerate(data.get("ids", [])):
            conn.execute("UPDATE tasks SET sort_order=? WHERE id=?", (i, int(tid)))
    return JSONResponse({"ok": True})


@app.post("/tasks")
async def create_task(
    description: str = Form(...),
    thread_id:   int = Form(...),
    due_date:    str = Form(""),
    is_deadline: str = Form("0"),
):
    with get_conn() as conn:
        max_order = conn.execute(
            "SELECT COALESCE(MAX(sort_order), -1) FROM tasks WHERE thread_id=?", (thread_id,)
        ).fetchone()[0]
        conn.execute(
            "INSERT INTO tasks (thread_id, description, due_date, sort_order, is_deadline) "
            "VALUES (?,?,?,?,?)",
            (thread_id, description.strip(), due_date or None, max_order + 1,
             1 if is_deadline == "1" else 0),
        )
    return RedirectResponse("/", status_code=303)


@app.post("/tasks/{task_id}/notes")
async def update_task_notes(task_id: int, notes: str = Form("")):
    with get_conn() as conn:
        conn.execute("UPDATE tasks SET notes=? WHERE id=?", (notes, task_id))
    return JSONResponse({"ok": True})


@app.post("/tasks/{task_id}/update")
async def update_task(
    task_id:     int,
    description: str = Form(...),
    due_date:    str = Form(""),
    is_deadline: str = Form("0"),
):
    with get_conn() as conn:
        conn.execute(
            "UPDATE tasks SET description=?, due_date=?, is_deadline=? WHERE id=?",
            (
                description.strip(),
                due_date or "ANYTIME",
                1 if is_deadline == "1" else 0,
                task_id,
            ),
        )
    return RedirectResponse("/", status_code=303)


@app.post("/tasks/{task_id}/close")
async def close_task(task_id: int):
    with get_conn() as conn:
        conn.execute("UPDATE tasks SET status='closed', closed_at=CURRENT_TIMESTAMP WHERE id=?", (task_id,))
    return RedirectResponse("/", status_code=303)


# Threads

@app.post("/threads")
async def create_thread(name: str = Form(...)):
    with get_conn() as conn:
        max_order = conn.execute("SELECT COALESCE(MAX(sort_order), -1) FROM threads").fetchone()[0]
        conn.execute("INSERT INTO threads (name, sort_order) VALUES (?,?)", (name.strip(), max_order + 1))
    return RedirectResponse("/", status_code=303)


@app.post("/threads/reorder")
async def reorder_threads(request: Request):
    data = await request.json()
    with get_conn() as conn:
        for i, tid in enumerate(data.get("ids", [])):
            conn.execute("UPDATE threads SET sort_order=? WHERE id=?", (i, int(tid)))
    return JSONResponse({"ok": True})


@app.post("/threads/{thread_id}/update")
async def update_thread(thread_id: int, name: str = Form(...)):
    with get_conn() as conn:
        conn.execute("UPDATE threads SET name=? WHERE id=?", (name.strip(), thread_id))
    return RedirectResponse("/", status_code=303)


@app.post("/threads/{thread_id}/delete")
async def delete_thread(thread_id: int):
    with get_conn() as conn:
        conn.execute("DELETE FROM tasks WHERE thread_id=?", (thread_id,))
        conn.execute("DELETE FROM group_threads WHERE thread_id=?", (thread_id,))
        conn.execute("DELETE FROM threads WHERE id=?", (thread_id,))
    return RedirectResponse("/", status_code=303)


# Groups

@app.post("/groups")
async def create_group(name: str = Form(...)):
    with get_conn() as conn:
        max_order = conn.execute("SELECT COALESCE(MAX(sort_order), -1) FROM groups").fetchone()[0]
        icon = _pick_group_emoji(conn)
        color = GROUP_COLORS[(max_order + 1) % len(GROUP_COLORS)]
        conn.execute("INSERT INTO groups (name, sort_order, icon, color) VALUES (?,?,?,?)",
                     (name.strip(), max_order + 1, icon, color))
    return RedirectResponse("/", status_code=303)


@app.post("/groups/{group_id}/update")
async def update_group(group_id: int, name: str = Form(...)):
    with get_conn() as conn:
        conn.execute("UPDATE groups SET name=? WHERE id=?", (name.strip(), group_id))
    return RedirectResponse("/", status_code=303)


@app.post("/groups/{group_id}/icon")
async def update_group_icon(group_id: int, emoji: str = Form(...)):
    with get_conn() as conn:
        conn.execute("UPDATE groups SET icon=? WHERE id=?", (emoji.strip(), group_id))
    return JSONResponse({"ok": True})


@app.post("/groups/{group_id}/color")
async def update_group_color(group_id: int, color: str = Form(...)):
    with get_conn() as conn:
        conn.execute("UPDATE groups SET color=? WHERE id=?", (color.strip(), group_id))
    return JSONResponse({"ok": True})


@app.post("/groups/{group_id}/delete")
async def delete_group(group_id: int):
    with get_conn() as conn:
        conn.execute("DELETE FROM group_threads WHERE group_id=?", (group_id,))
        conn.execute("DELETE FROM groups WHERE id=?", (group_id,))
    return RedirectResponse("/", status_code=303)


@app.post("/groups/{group_id}/threads/add")
async def add_thread_to_group(group_id: int, thread_id: int = Form(...)):
    with get_conn() as conn:
        # One group per thread: drop any prior membership first.
        conn.execute("DELETE FROM group_threads WHERE thread_id=?", (thread_id,))
        conn.execute("INSERT OR IGNORE INTO group_threads (group_id, thread_id) VALUES (?,?)",
                     (group_id, thread_id))
    return JSONResponse({"ok": True})


@app.post("/groups/{group_id}/threads/{thread_id}/remove")
async def remove_thread_from_group(group_id: int, thread_id: int):
    with get_conn() as conn:
        conn.execute("DELETE FROM group_threads WHERE group_id=? AND thread_id=?",
                     (group_id, thread_id))
    return JSONResponse({"ok": True})


# Today notepad

@app.post("/today")
async def save_today(body: str = Form("")):
    with get_conn() as conn:
        _set_state(conn, "today", body)
    return JSONResponse({"ok": True})
