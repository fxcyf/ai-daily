"""Lightweight web interface for mobile access — zero dependencies."""

import html
import json
import textwrap
import urllib.parse
from datetime import date
from http.server import HTTPServer, BaseHTTPRequestHandler
from typing import Optional

from .feeds import fetch_all, Article
from .tracker import LearningTracker

# ── Cached articles (refresh per request is too slow on mobile) ──────
_cached_articles: list[Article] = []
_cache_date: Optional[str] = None


def _get_articles(force: bool = False) -> list[Article]:
    global _cached_articles, _cache_date
    today = date.today().isoformat()
    if force or _cache_date != today or not _cached_articles:
        _cached_articles = fetch_all(max_articles=20)
        _cache_date = today
    return _cached_articles


# ── HTML Templates ───────────────────────────────────────────────────

_BASE_HTML = """\
<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, maximum-scale=1, user-scalable=no">
<meta name="apple-mobile-web-app-capable" content="yes">
<meta name="apple-mobile-web-app-status-bar-style" content="black-translucent">
<title>ai-daily</title>
<style>
:root {{
  --bg: #0d1117; --surface: #161b22; --border: #30363d;
  --text: #e6edf3; --text2: #8b949e; --accent: #58a6ff;
  --green: #3fb950; --yellow: #d29922; --red: #f85149;
  --orange: #db6d28;
}}
* {{ margin: 0; padding: 0; box-sizing: border-box; }}
body {{
  font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
  background: var(--bg); color: var(--text);
  line-height: 1.6; padding: 0 0 80px;
  -webkit-font-smoothing: antialiased;
}}
.container {{ max-width: 600px; margin: 0 auto; padding: 16px; }}
h1 {{ font-size: 1.3em; text-align: center; padding: 16px 0 8px; }}
h2 {{ font-size: 1.1em; margin: 20px 0 12px; color: var(--accent); }}

/* Nav bar */
.nav {{
  position: fixed; bottom: 0; left: 0; right: 0;
  background: var(--surface); border-top: 1px solid var(--border);
  display: flex; justify-content: space-around;
  padding: 8px 0 env(safe-area-inset-bottom, 8px);
  z-index: 100;
}}
.nav a {{
  color: var(--text2); text-decoration: none; font-size: 0.8em;
  display: flex; flex-direction: column; align-items: center; gap: 2px;
  padding: 4px 12px;
}}
.nav a.active {{ color: var(--accent); }}
.nav a .icon {{ font-size: 1.4em; }}

/* Streak banner */
.streak {{
  background: var(--surface); border-radius: 12px;
  padding: 16px; text-align: center; margin: 8px 0 16px;
  border: 1px solid var(--border);
}}
.streak .number {{ font-size: 2em; font-weight: 700; color: var(--orange); }}
.streak .label {{ font-size: 0.85em; color: var(--text2); }}

/* Stats grid */
.stats-grid {{
  display: grid; grid-template-columns: 1fr 1fr; gap: 10px; margin: 12px 0;
}}
.stat-card {{
  background: var(--surface); border-radius: 10px; padding: 14px;
  text-align: center; border: 1px solid var(--border);
}}
.stat-card .val {{ font-size: 1.5em; font-weight: 700; }}
.stat-card .lbl {{ font-size: 0.75em; color: var(--text2); margin-top: 2px; }}

/* Article card */
.article {{
  background: var(--surface); border-radius: 10px; padding: 14px;
  margin: 10px 0; border: 1px solid var(--border);
  transition: border-color 0.2s;
}}
.article:active {{ border-color: var(--accent); }}
.article a {{ color: var(--text); text-decoration: none; }}
.article .title {{ font-weight: 600; font-size: 0.95em; line-height: 1.4; }}
.article .meta {{
  font-size: 0.75em; color: var(--text2); margin-top: 6px;
  display: flex; gap: 8px; flex-wrap: wrap;
}}
.article .summary {{ font-size: 0.8em; color: var(--text2); margin-top: 6px; }}
.tag {{
  display: inline-block; padding: 1px 6px; border-radius: 4px;
  font-size: 0.7em; font-weight: 600;
}}
.tag-community {{ background: #d2992233; color: var(--yellow); }}
.tag-research {{ background: #58a6ff22; color: var(--accent); }}
.tag-newsletter {{ background: #bc8cff22; color: #bc8cff; }}
.tag-news {{ background: #58a6ff22; color: var(--accent); }}
.tag-industry {{ background: #3fb95022; color: var(--green); }}
.tag-tools {{ background: #f8514922; color: var(--red); }}

/* Log form */
.form-group {{ margin: 14px 0; }}
.form-group label {{ font-size: 0.85em; color: var(--text2); display: block; margin-bottom: 4px; }}
.form-group input, .form-group textarea {{
  width: 100%; padding: 10px 12px; border-radius: 8px;
  border: 1px solid var(--border); background: var(--surface);
  color: var(--text); font-size: 1em; font-family: inherit;
}}
.form-group textarea {{ height: 80px; resize: vertical; }}
.form-group input:focus, .form-group textarea:focus {{
  outline: none; border-color: var(--accent);
}}
.btn {{
  display: block; width: 100%; padding: 12px;
  background: var(--accent); color: #fff; border: none;
  border-radius: 10px; font-size: 1em; font-weight: 600;
  cursor: pointer; margin-top: 16px;
}}
.btn:active {{ opacity: 0.8; }}

/* Minutes stepper */
.stepper {{
  display: flex; align-items: center; gap: 12px;
}}
.stepper button {{
  width: 40px; height: 40px; border-radius: 50%;
  border: 1px solid var(--border); background: var(--surface);
  color: var(--text); font-size: 1.3em; cursor: pointer;
}}
.stepper button:active {{ background: var(--border); }}
.stepper .val {{ font-size: 1.3em; font-weight: 700; min-width: 40px; text-align: center; }}

/* History */
.day-row {{
  display: flex; justify-content: space-between; align-items: center;
  padding: 10px 0; border-bottom: 1px solid var(--border);
  font-size: 0.9em;
}}
.day-row .dot {{ width: 8px; height: 8px; border-radius: 50%; margin-right: 10px; flex-shrink: 0; }}
.dot-active {{ background: var(--green); }}
.dot-empty {{ background: var(--border); }}

/* Toast */
.toast {{
  position: fixed; top: 20px; left: 50%; transform: translateX(-50%);
  background: var(--green); color: #fff; padding: 10px 20px;
  border-radius: 8px; font-weight: 600; z-index: 200;
  animation: fadeout 2s ease-in-out forwards;
}}
@keyframes fadeout {{ 0%,70% {{ opacity:1; }} 100% {{ opacity:0; }} }}

.loading {{ text-align: center; padding: 40px; color: var(--text2); }}
</style>
</head>
<body>
{content}
<nav class="nav">
  <a href="/" class="{nav_digest}"><span class="icon">📰</span>动态</a>
  <a href="/log" class="{nav_log}"><span class="icon">✏️</span>打卡</a>
  <a href="/stats" class="{nav_stats}"><span class="icon">📊</span>统计</a>
</nav>
</body>
</html>
"""


def _page(content: str, active: str = "") -> str:
    return _BASE_HTML.format(
        content=content,
        nav_digest="active" if active == "digest" else "",
        nav_log="active" if active == "log" else "",
        nav_stats="active" if active == "stats" else "",
    )


def _render_digest(articles: list[Article]) -> str:
    tracker = LearningTracker()
    stats = tracker.stats()
    streak = stats.current_streak

    parts = ['<div class="container">']
    parts.append('<h1>ai-daily</h1>')

    # Streak banner
    flame = "🔥" * min(max(streak, 1), 5)
    parts.append(f'''<div class="streak">
        <div class="number">{flame} {streak}</div>
        <div class="label">连续学习天数</div>
    </div>''')

    if not articles:
        parts.append('<div class="loading">正在获取中，请稍候刷新...</div>')
    else:
        parts.append(f'<h2>今日精选 ({len(articles)} 篇)</h2>')
        for a in articles:
            t = html.escape(a.title)
            s = html.escape(textwrap.shorten(a.summary, 150, placeholder="...")) if a.summary else ""
            pub = a.published.strftime("%m-%d %H:%M") if a.published else ""
            cat = html.escape(a.category)
            parts.append(f'''<div class="article">
                <a href="{html.escape(a.url)}" target="_blank" rel="noopener">
                    <div class="title">{t}</div>
                </a>
                <div class="meta">
                    <span class="tag tag-{cat}">{cat}</span>
                    <span>{html.escape(a.source)}</span>
                    <span>{pub}</span>
                    <span>~{a.reading_time_min}min</span>
                </div>
                {f'<div class="summary">{s}</div>' if s else ''}
            </div>''')

    parts.append('</div>')
    return _page("\n".join(parts), active="digest")


def _render_log(success: bool = False) -> str:
    parts = ['<div class="container">']
    parts.append('<h1>✏️ 学习打卡</h1>')

    if success:
        parts.append('<div class="toast">打卡成功！</div>')

    parts.append('''
    <form method="POST" action="/log">
        <div class="form-group">
            <label>文章标题（选填）</label>
            <input type="text" name="title" placeholder="今天读了什么？">
        </div>
        <div class="form-group">
            <label>学习笔记（选填）</label>
            <textarea name="notes" placeholder="学到了什么？有什么想法？"></textarea>
        </div>
        <div class="form-group">
            <label>学习时间（分钟）</label>
            <div class="stepper">
                <button type="button" onclick="adj(-5)">-</button>
                <div class="val" id="mins">5</div>
                <button type="button" onclick="adj(5)">+</button>
                <input type="hidden" name="minutes" id="mins-input" value="5">
            </div>
        </div>
        <button type="submit" class="btn">打卡</button>
    </form>
    <script>
    function adj(d) {
        var el = document.getElementById('mins');
        var inp = document.getElementById('mins-input');
        var v = Math.max(1, parseInt(el.textContent) + d);
        el.textContent = v;
        inp.value = v;
    }
    </script>
    ''')

    parts.append('</div>')
    return _page("\n".join(parts), active="log")


def _render_stats() -> str:
    tracker = LearningTracker()
    stats = tracker.stats()
    recent = tracker.recent_entries(14)

    parts = ['<div class="container">']
    parts.append('<h1>📊 学习统计</h1>')

    # Stats grid
    parts.append(f'''<div class="stats-grid">
        <div class="stat-card"><div class="val" style="color:var(--orange)">{stats.current_streak}</div><div class="lbl">当前连续（天）</div></div>
        <div class="stat-card"><div class="val" style="color:var(--yellow)">{stats.longest_streak}</div><div class="lbl">最长连续（天）</div></div>
        <div class="stat-card"><div class="val" style="color:var(--accent)">{stats.total_articles}</div><div class="lbl">累计文章</div></div>
        <div class="stat-card"><div class="val" style="color:var(--green)">{stats.total_minutes}</div><div class="lbl">累计分钟</div></div>
    </div>''')

    # Recent days
    parts.append('<h2>最近 14 天</h2>')
    from datetime import timedelta
    today = date.today()
    logged = {e.date: e for e in recent}

    for i in range(14):
        d = today - timedelta(days=i)
        ds = d.isoformat()
        entry = logged.get(ds)
        if entry:
            dot = "dot-active"
            info = f"{len(entry.articles_read)} 篇 · {entry.minutes_spent}min"
            note = html.escape(textwrap.shorten(entry.notes, 40, placeholder="...")) if entry.notes else ""
            detail = f'<span style="color:var(--green)">{info}</span>'
            if note:
                detail += f'<br><span style="color:var(--text2);font-size:0.8em">{note}</span>'
        else:
            dot = "dot-empty"
            detail = '<span style="color:var(--text2)">—</span>'

        weekday = ["一", "二", "三", "四", "五", "六", "日"][d.weekday()]
        parts.append(f'''<div class="day-row">
            <div style="display:flex;align-items:center">
                <div class="dot {dot}"></div>
                <span>{ds} 周{weekday}</span>
            </div>
            <div style="text-align:right">{detail}</div>
        </div>''')

    parts.append('</div>')
    return _page("\n".join(parts), active="stats")


class DailyHandler(BaseHTTPRequestHandler):
    """HTTP request handler for the web interface."""

    def log_message(self, format, *args):
        """Suppress default logging to keep terminal clean."""
        pass

    def _respond(self, body: str, status: int = 200, content_type: str = "text/html"):
        self.send_response(status)
        self.send_header("Content-Type", f"{content_type}; charset=utf-8")
        self.send_header("Cache-Control", "no-cache")
        encoded = body.encode("utf-8")
        self.send_header("Content-Length", str(len(encoded)))
        self.end_headers()
        self.wfile.write(encoded)

    def do_GET(self):
        path = urllib.parse.urlparse(self.path).path

        if path == "/" or path == "/digest":
            articles = _get_articles()
            self._respond(_render_digest(articles))
        elif path == "/log":
            qs = urllib.parse.urlparse(self.path).query
            success = "ok" in urllib.parse.parse_qs(qs)
            self._respond(_render_log(success=success))
        elif path == "/stats":
            self._respond(_render_stats())
        elif path == "/refresh":
            _get_articles(force=True)
            self.send_response(302)
            self.send_header("Location", "/")
            self.end_headers()
        else:
            self._respond("<h1>404</h1>", status=404)

    def do_POST(self):
        path = urllib.parse.urlparse(self.path).path

        if path == "/log":
            length = int(self.headers.get("Content-Length", 0))
            body = self.rfile.read(length).decode("utf-8")
            params = urllib.parse.parse_qs(body)

            title = params.get("title", [""])[0].strip()
            notes = params.get("notes", [""])[0].strip()
            minutes = int(params.get("minutes", ["5"])[0])

            tracker = LearningTracker()
            tracker.log_today(
                articles=[title] if title else None,
                notes=notes,
                minutes=minutes,
            )

            self.send_response(302)
            self.send_header("Location", "/log?ok")
            self.end_headers()
        else:
            self._respond("<h1>404</h1>", status=404)


def run_server(host: str = "0.0.0.0", port: int = 8080):
    """Start the web server."""
    server = HTTPServer((host, port), DailyHandler)
    # Pre-fetch articles in background
    import threading
    threading.Thread(target=_get_articles, daemon=True).start()

    import socket
    local_ip = _get_local_ip()
    print(f"\n  ai-daily web 已启动\n")
    print(f"  本机访问: http://localhost:{port}")
    if local_ip:
        print(f"  手机访问: http://{local_ip}:{port}")
    print(f"\n  手机和电脑连同一个 WiFi，扫码或输入地址即可")
    print(f"  按 Ctrl+C 停止\n")

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n  已停止")
        server.server_close()


def _get_local_ip() -> Optional[str]:
    """Get local network IP address."""
    import socket
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except OSError:
        return None
