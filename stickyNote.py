import streamlit as st
import sqlite3
import json
import uuid
import base64
import html
from pathlib import Path
from datetime import datetime


# ============================================================
# BASIC APP CONFIG
# ============================================================

st.set_page_config(
    page_title="Sticky Wall",
    page_icon="📝",
    layout="wide",
    initial_sidebar_state="collapsed",
)


# ============================================================
# LOCAL STORAGE CONFIG
# ============================================================

APP_DIR = Path(__file__).parent
DB_PATH = APP_DIR / "sticky_wall.db"
UPLOAD_DIR = APP_DIR / "sticky_uploads"
UPLOAD_DIR.mkdir(exist_ok=True)


# ============================================================
# DESIGN CONSTANTS
# ============================================================

NOTE_COLORS = {
    "Yellow": "#fff3b0",
    "Blue": "#cdeff3",
    "Pink": "#ffd6d6",
    "Orange": "#ffd0a3",
    "Green": "#d8f3dc",
    "Purple": "#e6d7ff",
    "White": "#f3f3f3",
}

DEFAULT_LISTS = ["Personal", "Work", "Ideas", "Teaching", "Research"]


# ============================================================
# DATABASE LAYER
# ============================================================

@st.cache_resource
def get_connection():
    """
    Creates one reusable SQLite connection.
    check_same_thread=False is needed because Streamlit reruns the script often.
    """
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    """Create notes table if it does not exist."""
    conn = get_connection()
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS notes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            body TEXT DEFAULT '',
            color TEXT DEFAULT 'Yellow',
            list_name TEXT DEFAULT 'Personal',
            tags_json TEXT DEFAULT '[]',
            todos_json TEXT DEFAULT '[]',
            image_paths_json TEXT DEFAULT '[]',
            pinned INTEGER DEFAULT 0,
            archived INTEGER DEFAULT 0,
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL
        )
        """
    )
    conn.commit()


def seed_demo_notes():
    """Seed initial demo notes only if database is empty."""
    conn = get_connection()
    count = conn.execute("SELECT COUNT(*) FROM notes").fetchone()[0]

    if count > 0:
        return

    demo_notes = [
        {
            "title": "Social Media",
            "body": "- Plan social content\n- Build content calendar\n- Plan promotion and distribution",
            "color": "Yellow",
            "list_name": "Work",
            "tags": ["marketing"],
            "todos": [],
        },
        {
            "title": "Content Strategy",
            "body": (
                "Would need time to get insights: goals, personas, budget, audits. "
                "After that, it would be good to focus on assembling the team and tooling."
            ),
            "color": "Blue",
            "list_name": "Work",
            "tags": ["strategy"],
            "todos": [],
        },
        {
            "title": "Email A/B Tests",
            "body": "- Subject lines\n- Sender\n- CTA\n- Sending times",
            "color": "Pink",
            "list_name": "Work",
            "tags": ["experiments"],
            "todos": [],
        },
        {
            "title": "Banner Ads",
            "body": "Notes from the workshop:",
            "color": "Orange",
            "list_name": "Work",
            "tags": ["ads"],
            "todos": [
                {"text": "Sizing matters", "done": False},
                {"text": "Choose distinctive imagery", "done": False},
                {"text": "Landing page must match the display ad", "done": True},
            ],
        },
    ]

    now = datetime.now().isoformat(timespec="seconds")

    for note in demo_notes:
        conn.execute(
            """
            INSERT INTO notes
            (title, body, color, list_name, tags_json, todos_json, image_paths_json,
             pinned, archived, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                note["title"],
                note["body"],
                note["color"],
                note["list_name"],
                json.dumps(note["tags"]),
                json.dumps(note["todos"]),
                json.dumps([]),
                0,
                0,
                now,
                now,
            ),
        )

    conn.commit()


def row_to_note(row):
    """Convert SQLite row into normal Python dictionary."""
    if row is None:
        return None

    note = dict(row)
    note["tags"] = json.loads(note.pop("tags_json") or "[]")
    note["todos"] = json.loads(note.pop("todos_json") or "[]")
    note["image_paths"] = json.loads(note.pop("image_paths_json") or "[]")
    note["pinned"] = bool(note["pinned"])
    note["archived"] = bool(note["archived"])
    return note


def fetch_notes(search="", list_filter="All", tag_filter="All", archived=False):
    """
    Retrieve notes from SQLite with optional search, list, and tag filters.
    """
    conn = get_connection()

    query = """
        SELECT * FROM notes
        WHERE archived = ?
    """
    params = [1 if archived else 0]

    if search.strip():
        query += """
            AND (
                LOWER(title) LIKE ?
                OR LOWER(body) LIKE ?
                OR LOWER(tags_json) LIKE ?
                OR LOWER(list_name) LIKE ?
            )
        """
        s = f"%{search.lower().strip()}%"
        params.extend([s, s, s, s])

    if list_filter != "All":
        query += " AND list_name = ?"
        params.append(list_filter)

    if tag_filter != "All":
        query += " AND LOWER(tags_json) LIKE ?"
        params.append(f"%{tag_filter.lower()}%")

    query += " ORDER BY pinned DESC, updated_at DESC"

    rows = conn.execute(query, params).fetchall()
    return [row_to_note(row) for row in rows]


def get_note(note_id):
    """Fetch one note by id."""
    conn = get_connection()
    row = conn.execute("SELECT * FROM notes WHERE id = ?", (note_id,)).fetchone()
    return row_to_note(row)


def save_note(
    note_id,
    title,
    body,
    color,
    list_name,
    tags,
    todos,
    image_paths,
    pinned,
    archived,
):
    """
    Create or update a note.
    If note_id is None, creates a new note.
    Otherwise updates the existing note.
    """
    conn = get_connection()
    now = datetime.now().isoformat(timespec="seconds")

    if note_id is None:
        conn.execute(
            """
            INSERT INTO notes
            (title, body, color, list_name, tags_json, todos_json, image_paths_json,
             pinned, archived, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                title,
                body,
                color,
                list_name,
                json.dumps(tags),
                json.dumps(todos),
                json.dumps(image_paths),
                1 if pinned else 0,
                1 if archived else 0,
                now,
                now,
            ),
        )
    else:
        conn.execute(
            """
            UPDATE notes
            SET title = ?,
                body = ?,
                color = ?,
                list_name = ?,
                tags_json = ?,
                todos_json = ?,
                image_paths_json = ?,
                pinned = ?,
                archived = ?,
                updated_at = ?
            WHERE id = ?
            """,
            (
                title,
                body,
                color,
                list_name,
                json.dumps(tags),
                json.dumps(todos),
                json.dumps(image_paths),
                1 if pinned else 0,
                1 if archived else 0,
                now,
                note_id,
            ),
        )

    conn.commit()


def delete_note(note_id):
    """Delete a note permanently."""
    conn = get_connection()
    conn.execute("DELETE FROM notes WHERE id = ?", (note_id,))
    conn.commit()


def update_todos_only(note_id, todos):
    """Update checklist state without changing the full note."""
    conn = get_connection()
    conn.execute(
        """
        UPDATE notes
        SET todos_json = ?, updated_at = ?
        WHERE id = ?
        """,
        (
            json.dumps(todos),
            datetime.now().isoformat(timespec="seconds"),
            note_id,
        ),
    )
    conn.commit()


def fetch_all_lists_and_tags():
    """Get list names and tags for sidebar filters."""
    conn = get_connection()
    rows = conn.execute("SELECT list_name, tags_json FROM notes WHERE archived = 0").fetchall()

    lists = set(DEFAULT_LISTS)
    tags = set()

    for row in rows:
        if row["list_name"]:
            lists.add(row["list_name"])

        for tag in json.loads(row["tags_json"] or "[]"):
            tags.add(tag)

    return sorted(lists), sorted(tags)


# ============================================================
# FILE / IMAGE HELPERS
# ============================================================

def save_uploaded_images(uploaded_files):
    """
    Save uploaded images to local folder and return relative file paths.
    """
    saved_paths = []

    for file in uploaded_files or []:
        extension = Path(file.name).suffix.lower()
        safe_name = f"{uuid.uuid4().hex}{extension}"
        output_path = UPLOAD_DIR / safe_name

        with open(output_path, "wb") as f:
            f.write(file.getbuffer())

        saved_paths.append(str(output_path))

    return saved_paths


def image_to_base64(path):
    """
    Convert local image file to base64 data URL for displaying inside HTML cards.
    """
    try:
        path = Path(path)
        if not path.exists():
            return ""

        mime = "image/png"
        if path.suffix.lower() in [".jpg", ".jpeg"]:
            mime = "image/jpeg"
        elif path.suffix.lower() == ".gif":
            mime = "image/gif"

        data = base64.b64encode(path.read_bytes()).decode("utf-8")
        return f"data:{mime};base64,{data}"
    except Exception:
        return ""


# ============================================================
# TODO / MARKDOWN HELPERS
# ============================================================

def parse_tags(text):
    """Convert comma-separated tags into clean list."""
    return [tag.strip() for tag in text.split(",") if tag.strip()]


def todos_to_text(todos):
    """
    Convert todos list into editable text format.
    Example:
    [ ] Buy milk
    [x] Submit assignment
    """
    lines = []
    for item in todos:
        prefix = "[x]" if item.get("done") else "[ ]"
        lines.append(f"{prefix} {item.get('text', '')}")
    return "\n".join(lines)


def parse_todos(text):
    """
    Parse todos from text area.
    Supports:
    [ ] incomplete task
    [x] completed task
    plain line becomes incomplete task
    """
    todos = []

    for raw_line in text.splitlines():
        line = raw_line.strip()

        if not line:
            continue

        if line.lower().startswith("[x]"):
            todos.append({"text": line[3:].strip(), "done": True})
        elif line.lower().startswith("[ ]"):
            todos.append({"text": line[3:].strip(), "done": False})
        else:
            todos.append({"text": line, "done": False})

    return todos


def short_text(text, limit=150):
    """Shorten card preview text."""
    text = text.replace("\n", " ").strip()
    if len(text) <= limit:
        return text
    return text[:limit].rstrip() + "..."


# ============================================================
# CSS
# ============================================================

st.markdown(
    """
    <style>
    [data-testid="stAppViewContainer"] {
        background:
            radial-gradient(circle at 10% 10%, rgba(255,255,255,0.35), transparent 22%),
            linear-gradient(135deg, #d3ded0 0%, #b8c9b8 100%);
    }

    [data-testid="stHeader"] {
        background: transparent;
    }

    [data-testid="stToolbar"] {
        display: none;
    }

    .block-container {
        max-width: 1220px;
        padding-top: 2.2rem;
        padding-bottom: 3rem;
    }

    .app-shell {
        background: #f7f7f7;
        border-radius: 28px;
        box-shadow: 0 30px 70px rgba(80, 91, 75, 0.28);
        min-height: 760px;
        padding: 26px;
    }

    .sidebar-card {
        background: #f4f4f4;
        border-right: 1px solid #e5e5e5;
        border-radius: 22px;
        min-height: 705px;
        padding: 26px 20px;
    }

    .sidebar-title {
        font-size: 24px;
        font-weight: 900;
        color: #2c3130;
        margin-bottom: 20px;
    }

    .sidebar-section {
        font-size: 11px;
        letter-spacing: 0.08em;
        color: #6d706d;
        font-weight: 900;
        margin-top: 26px;
        margin-bottom: 10px;
        text-transform: uppercase;
    }

    .menu-item {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 10px 13px;
        border-radius: 10px;
        color: #353937;
        font-size: 14px;
        font-weight: 700;
        margin-bottom: 4px;
    }

    .menu-item.active {
        background: #e9e9e9;
    }

    .count-badge {
        background: #ececec;
        padding: 3px 8px;
        border-radius: 6px;
        font-size: 11px;
        font-weight: 900;
    }

    .main-title {
        font-size: 43px;
        font-weight: 950;
        color: #202625;
        margin-bottom: 28px;
        letter-spacing: -1px;
    }

    .toolbar {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 24px;
    }

    .note-card {
        min-height: 225px;
        border-radius: 12px;
        padding: 22px;
        box-shadow: 0 8px 18px rgba(0,0,0,0.06);
        border: 1px solid rgba(255,255,255,0.65);
        color: #2b3130;
        transition: all 0.16s ease;
        text-decoration: none !important;
        display: block;
        margin-bottom: 18px;
    }

    .note-card:hover {
        transform: translateY(-3px);
        box-shadow: 0 16px 28px rgba(0,0,0,0.11);
    }

    .note-title {
        font-size: 21px;
        font-weight: 950;
        margin-bottom: 10px;
        color: #232928;
    }

    .note-body {
        font-size: 14px;
        line-height: 1.45;
        font-weight: 650;
        color: #444b4a;
    }

    .note-meta {
        margin-top: 16px;
        font-size: 11px;
        color: #5d6462;
        display: flex;
        gap: 6px;
        flex-wrap: wrap;
    }

    .tag-pill {
        display: inline-block;
        background: rgba(255,255,255,0.55);
        border-radius: 8px;
        padding: 4px 8px;
        font-size: 11px;
        font-weight: 800;
    }

    .add-card {
        min-height: 225px;
        border-radius: 12px;
        background: #ededed;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 72px;
        color: #2f3433;
        text-decoration: none !important;
        box-shadow: inset 0 0 0 1px #e1e1e1;
        transition: all 0.16s ease;
    }

    .add-card:hover {
        background: #e5e5e5;
        transform: translateY(-3px);
    }

    .image-preview {
        width: 100%;
        max-height: 115px;
        object-fit: cover;
        border-radius: 10px;
        margin-bottom: 12px;
    }

    .empty-state {
        background: #ffffff;
        border: 1px dashed #d2d2d2;
        border-radius: 16px;
        padding: 40px;
        text-align: center;
        color: #777;
    }

    div[data-testid="stButton"] > button {
        border-radius: 10px;
        font-weight: 800;
        border: 1px solid #dadada;
        background: white;
        color: #333;
    }

    div[data-testid="stButton"] > button:hover {
        border: 1px solid #bdbdbd;
        background: #f1f1f1;
        color: #111;
    }

    div[data-testid="stFormSubmitButton"] > button {
        background: #202625;
        color: white;
        border-radius: 10px;
        font-weight: 900;
    }

    div[data-testid="stFormSubmitButton"] > button:hover {
        background: #333a39;
        color: white;
    }

    .small-help {
        font-size: 12px;
        color: #666;
        line-height: 1.45;
    }

    a {
        text-decoration: none !important;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


# ============================================================
# QUERY PARAM HELPERS
# ============================================================

def get_query_param(name):
    """Read query parameter safely."""
    try:
        value = st.query_params.get(name)
        return value
    except Exception:
        return None


def clear_popup_params():
    """Close modal by clearing note/new query params."""
    try:
        st.query_params.clear()
    except Exception:
        pass
    st.rerun()


# ============================================================
# NOTE CARD RENDERING
# ============================================================

def render_note_card(note):
    """
    Render note as clickable HTML card.
    Clicking changes URL to ?note=<id>, and the app opens the modal.
    """
    color = NOTE_COLORS.get(note["color"], NOTE_COLORS["Yellow"])
    safe_title = html.escape(note["title"])
    safe_body = html.escape(short_text(note["body"]))

    tag_html = "".join(
        f'<span class="tag-pill">#{html.escape(tag)}</span>'
        for tag in note["tags"][:3]
    )

    todo_preview = ""
    if note["todos"]:
        done_count = sum(1 for item in note["todos"] if item.get("done"))
        todo_preview = f'<span class="tag-pill">☑ {done_count}/{len(note["todos"])} tasks</span>'

    pinned = '<span class="tag-pill">📌 pinned</span>' if note["pinned"] else ""

    image_html = ""
    if note["image_paths"]:
        data_url = image_to_base64(note["image_paths"][0])
        if data_url:
            image_html = f'<img class="image-preview" src="{data_url}" />'

    st.markdown(
        f"""
        <a href="?note={note["id"]}" class="note-card" style="background:{color};">
            {image_html}
            <div class="note-title">{safe_title}</div>
            <div class="note-body">{safe_body}</div>
            <div class="note-meta">
                <span class="tag-pill">{html.escape(note["list_name"])}</span>
                {tag_html}
                {todo_preview}
                {pinned}
            </div>
        </a>
        """,
        unsafe_allow_html=True,
    )


def render_add_card():
    """Render add-new sticky card."""
    st.markdown(
        """
        <a href="?new=1" class="add-card">
            +
        </a>
        """,
        unsafe_allow_html=True,
    )


# ============================================================
# NOTE EDITOR
# ============================================================

def note_editor(note=None):
    """
    Shared create/edit form.
    If note is None, creates a blank note.
    Otherwise edits the selected note.
    """
    is_new = note is None
    note_id = None if is_new else note["id"]

    default_title = "" if is_new else note["title"]
    default_body = "" if is_new else note["body"]
    default_color = "Yellow" if is_new else note["color"]
    default_list = "Personal" if is_new else note["list_name"]
    default_tags = "" if is_new else ", ".join(note["tags"])
    default_todos = "" if is_new else todos_to_text(note["todos"])
    default_images = [] if is_new else note["image_paths"]
    default_pinned = False if is_new else note["pinned"]
    default_archived = False if is_new else note["archived"]

    editor_key = f"editor_body_{note_id or 'new'}"

    if editor_key not in st.session_state:
        st.session_state[editor_key] = default_body

    st.write("#### Note details")

    title = st.text_input("Title", value=default_title)

    c1, c2, c3 = st.columns(3)

    with c1:
        color = st.selectbox(
            "Sticky color",
            list(NOTE_COLORS.keys()),
            index=list(NOTE_COLORS.keys()).index(default_color)
            if default_color in NOTE_COLORS
            else 0,
        )

    with c2:
        list_name = st.text_input("List / category", value=default_list)

    with c3:
        tags_text = st.text_input("Tags, comma-separated", value=default_tags)

    pinned = st.checkbox("Pin note", value=default_pinned)
    archived = st.checkbox("Archive note", value=default_archived)

    st.divider()

    st.write("#### Rich text note body")

    st.caption(
        "Use Markdown formatting: **bold**, *italics*, # heading, - bullet, [link](https://example.com), `code`."
    )

    fmt_cols = st.columns(5)

    with fmt_cols[0]:
        if st.button("Add bold", key=f"bold_{note_id or 'new'}"):
            st.session_state[editor_key] += "\n**bold text**"

    with fmt_cols[1]:
        if st.button("Add italics", key=f"italics_{note_id or 'new'}"):
            st.session_state[editor_key] += "\n*italic text*"

    with fmt_cols[2]:
        if st.button("Add heading", key=f"heading_{note_id or 'new'}"):
            st.session_state[editor_key] += "\n## Heading"

    with fmt_cols[3]:
        if st.button("Add bullet", key=f"bullet_{note_id or 'new'}"):
            st.session_state[editor_key] += "\n- Bullet point"

    with fmt_cols[4]:
        if st.button("Add link", key=f"link_{note_id or 'new'}"):
            st.session_state[editor_key] += "\n[link text](https://example.com)"

    body = st.text_area(
        "Body",
        key=editor_key,
        height=180,
        label_visibility="collapsed",
    )

    with st.expander("Preview formatted note"):
        st.markdown(body)

    st.divider()

    st.write("#### To-do list")

    todos_text = st.text_area(
        "Checklist items",
        value=default_todos,
        height=120,
        help="Use [ ] for pending tasks and [x] for completed tasks.",
    )

    st.caption("Example: `[ ] Prepare lecture slides` or `[x] Submit report`")

    st.divider()

    st.write("#### Images")

    existing_images = default_images.copy()

    if existing_images:
        st.caption("Existing images")
        remove_images = []

        for path in existing_images:
            img_col, remove_col = st.columns([4, 1])
            with img_col:
                if Path(path).exists():
                    st.image(path, use_container_width=True)
                else:
                    st.warning(f"Missing file: {path}")

            with remove_col:
                if st.checkbox("Remove", key=f"remove_img_{path}_{note_id}"):
                    remove_images.append(path)

        existing_images = [path for path in existing_images if path not in remove_images]

    uploaded_images = st.file_uploader(
        "Upload images",
        type=["png", "jpg", "jpeg", "webp"],
        accept_multiple_files=True,
    )

    st.divider()

    save_col, cancel_col = st.columns([1, 1])

    with save_col:
        save_clicked = st.button(
            "Save sticky",
            type="primary",
            use_container_width=True,
            key=f"save_{note_id or 'new'}",
        )

    with cancel_col:
        cancel_clicked = st.button(
            "Cancel",
            use_container_width=True,
            key=f"cancel_{note_id or 'new'}",
        )

    if cancel_clicked:
        clear_popup_params()

    if save_clicked:
        if not title.strip():
            st.warning("Please enter a title.")
            return

        new_image_paths = save_uploaded_images(uploaded_images)

        save_note(
            note_id=note_id,
            title=title.strip(),
            body=body.strip(),
            color=color,
            list_name=list_name.strip() or "Personal",
            tags=parse_tags(tags_text),
            todos=parse_todos(todos_text),
            image_paths=existing_images + new_image_paths,
            pinned=pinned,
            archived=archived,
        )

        st.success("Sticky saved.")
        clear_popup_params()


# ============================================================
# MODALS / POPUPS
# ============================================================

@st.dialog("Create new sticky", width="large")
def create_note_popup():
    note_editor(note=None)


@st.dialog("Sticky note", width="large")
def view_note_popup(note_id):
    note = get_note(note_id)

    if note is None:
        st.error("This sticky note no longer exists.")
        if st.button("Close"):
            clear_popup_params()
        return

    tab_view, tab_edit = st.tabs(["View", "Edit"])

    with tab_view:
        title_col, action_col = st.columns([4, 1])

        with title_col:
            st.subheader(note["title"])

        with action_col:
            if st.button("Close", use_container_width=True):
                clear_popup_params()

        st.caption(
            f"List: {note['list_name']} · "
            f"Updated: {note['updated_at']} · "
            f"Tags: {', '.join(note['tags']) if note['tags'] else 'None'}"
        )

        if note["image_paths"]:
            st.write("#### Images")
            for path in note["image_paths"]:
                if Path(path).exists():
                    st.image(path, use_container_width=True)

        if note["body"]:
            st.write("#### Note")
            st.markdown(note["body"])

        if note["todos"]:
            st.write("#### Checklist")

            changed = False
            updated_todos = []

            for i, item in enumerate(note["todos"]):
                checked = st.checkbox(
                    item["text"],
                    value=item.get("done", False),
                    key=f"todo_{note_id}_{i}",
                )

                if checked != item.get("done", False):
                    changed = True

                updated_todos.append(
                    {
                        "text": item["text"],
                        "done": checked,
                    }
                )

            if changed:
                update_todos_only(note_id, updated_todos)
                st.rerun()

        st.divider()

        danger_col_1, danger_col_2 = st.columns(2)

        with danger_col_1:
            archive_label = "Unarchive" if note["archived"] else "Archive"
            if st.button(archive_label, use_container_width=True):
                save_note(
                    note_id=note["id"],
                    title=note["title"],
                    body=note["body"],
                    color=note["color"],
                    list_name=note["list_name"],
                    tags=note["tags"],
                    todos=note["todos"],
                    image_paths=note["image_paths"],
                    pinned=note["pinned"],
                    archived=not note["archived"],
                )
                clear_popup_params()

        with danger_col_2:
            if st.button("Delete permanently", use_container_width=True):
                delete_note(note_id)
                clear_popup_params()

    with tab_edit:
        note_editor(note=note)


# ============================================================
# SIDEBAR
# ============================================================

def render_sidebar():
    lists, tags = fetch_all_lists_and_tags()

    st.markdown('<div class="sidebar-card">', unsafe_allow_html=True)
    st.markdown('<div class="sidebar-title">Menu</div>', unsafe_allow_html=True)

    search = st.text_input(
        "Search",
        placeholder="Search notes...",
        label_visibility="collapsed",
        key="search_input",
    )

    st.markdown('<div class="sidebar-section">Tasks</div>', unsafe_allow_html=True)

    archived = st.checkbox("Show archived notes")

    st.markdown(
        """
        <div class="menu-item active">
            <span>▣ Sticky Wall</span>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown('<div class="sidebar-section">Lists</div>', unsafe_allow_html=True)

    list_filter = st.radio(
        "List filter",
        ["All"] + lists,
        label_visibility="collapsed",
        key="list_filter",
    )

    st.markdown('<div class="sidebar-section">Tags</div>', unsafe_allow_html=True)

    tag_filter = st.radio(
        "Tag filter",
        ["All"] + tags,
        label_visibility="collapsed",
        key="tag_filter",
    )

    st.markdown(
        """
        <div style="height: 90px;"></div>
        <div class="menu-item"><span>⚙ Settings</span></div>
        <div class="menu-item"><span>↪ Sign out</span></div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown("</div>", unsafe_allow_html=True)

    return search, list_filter, tag_filter, archived


# ============================================================
# MAIN BOARD
# ============================================================

def render_board(notes):
    top_col_1, top_col_2 = st.columns([4, 1])

    with top_col_1:
        st.markdown('<div class="main-title">Sticky Wall</div>', unsafe_allow_html=True)

    with top_col_2:
        st.markdown("<br>", unsafe_allow_html=True)
        st.link_button("➕ New sticky", "?new=1", use_container_width=True)

    if not notes:
        st.markdown(
            """
            <div class="empty-state">
                <h3>No sticky notes found</h3>
                <p>Try changing your search/filter, or create a new sticky note.</p>
            </div>
            """,
            unsafe_allow_html=True,
        )
        st.write("")
        render_add_card()
        return

    # Render notes in a 3-column masonry-like grid.
    cols = st.columns(3)

    for i, note in enumerate(notes):
        with cols[i % 3]:
            render_note_card(note)

    # Add-card at the end.
    with cols[len(notes) % 3]:
        render_add_card()


# ============================================================
# APP STARTUP
# ============================================================

init_db()
seed_demo_notes()


# ============================================================
# MAIN APP LAYOUT
# ============================================================

st.markdown('<div class="app-shell">', unsafe_allow_html=True)

sidebar_col, main_col = st.columns([0.26, 0.74], gap="large")

with sidebar_col:
    search, list_filter, tag_filter, archived = render_sidebar()

with main_col:
    notes = fetch_notes(
        search=search,
        list_filter=list_filter,
        tag_filter=tag_filter,
        archived=archived,
    )
    render_board(notes)

st.markdown("</div>", unsafe_allow_html=True)


# ============================================================
# POPUP ROUTING
# Clicking a sticky note sets ?note=<id>.
# Clicking the plus card sets ?new=1.
# ============================================================

new_mode = get_query_param("new")
selected_note_id = get_query_param("note")

if new_mode == "1":
    create_note_popup()

if selected_note_id:
    try:
        view_note_popup(int(selected_note_id))
    except ValueError:
        st.error("Invalid note id.")