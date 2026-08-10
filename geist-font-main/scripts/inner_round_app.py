#!/usr/bin/env python3
"""
Namche-Shadow live preview (http://127.0.0.1:8765).

Serves the RoundCorner-exported OTFs from exports/Namche-Shadow/otf/
and proves them in the browser via @font-face.

  python3 scripts/inner_round_app.py
"""

from __future__ import annotations

import mimetypes
import sys
import threading
import webbrowser
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import unquote, urlparse

SCRIPT_DIR = Path(__file__).resolve().parent
EXPORTS_ROOT = SCRIPT_DIR.parent / "exports"
NAMCHE_DIR = EXPORTS_ROOT / "Namche-Shadow"
FONT_DIRS = {
    ".woff2": NAMCHE_DIR / "woff2",
    ".woff": NAMCHE_DIR / "woff",
    ".otf": NAMCHE_DIR / "otf",
    ".ttf": NAMCHE_DIR / "ttf",
}
FAMILY = "Namche-Shadow"

HOST = "127.0.0.1"
PORT = 8765

WEIGHTS = [
    ("Thin", 100),
    ("ExtraLight", 200),
    ("Light", 300),
    ("Regular", 400),
    ("Medium", 500),
    ("SemiBold", 600),
    ("Bold", 700),
    ("ExtraBold", 800),
    ("Black", 900),
]


def _font_face_css() -> str:
    blocks = []
    for style, wght in WEIGHTS:
        stem = f"{FAMILY}-{style}"
        blocks.append(
            f"""@font-face {{
  font-family: "{FAMILY}";
  src: url("/fonts/{stem}.woff2") format("woff2"),
       url("/fonts/{stem}.woff") format("woff"),
       url("/fonts/{stem}.otf") format("opentype");
  font-weight: {wght};
  font-style: normal;
  font-display: block;
}}"""
        )
    return "\n".join(blocks)


def _weight_options() -> str:
    opts = []
    for style, wght in WEIGHTS:
        selected = " selected" if style == "Regular" else ""
        opts.append(f'<option value="{wght}"{selected}>{style}</option>')
    return "\n".join(opts)


HTML_PAGE = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8"/>
<meta name="viewport" content="width=device-width, initial-scale=1"/>
<title>Namche-Shadow</title>
<style>
{_font_face_css()}
  :root {{
    --bg: #111314;
    --panel: #1a1d1f;
    --text: #e8ebe4;
    --muted: #8b928a;
    --accent: #c8d4a8;
    --line: #2a2f2c;
  }}
  * {{ box-sizing: border-box; }}
  body {{
    margin: 0;
    font-family: "IBM Plex Sans", "Helvetica Neue", sans-serif;
    background: var(--bg);
    color: var(--text);
    min-height: 100vh;
    display: grid;
    grid-template-rows: auto 1fr auto;
  }}
  header {{
    padding: 1.25rem 1.5rem 0.75rem;
    border-bottom: 1px solid var(--line);
  }}
  header h1 {{
    margin: 0;
    font-family: "{FAMILY}", sans-serif;
    font-weight: 400;
    font-size: 1.75rem;
    letter-spacing: -0.02em;
  }}
  header p {{
    margin: 0.45rem 0 0;
    color: var(--muted);
    font-size: 0.85rem;
  }}
  main {{
    display: grid;
    grid-template-columns: minmax(260px, 320px) 1fr;
    min-height: 0;
  }}
  @media (max-width: 800px) {{
    main {{ grid-template-columns: 1fr; }}
  }}
  aside {{
    padding: 1.25rem 1.5rem;
    border-right: 1px solid var(--line);
    background: var(--panel);
    display: flex;
    flex-direction: column;
    gap: 1.1rem;
  }}
  label {{
    display: flex;
    flex-direction: column;
    gap: 0.4rem;
    font-size: 0.78rem;
    text-transform: uppercase;
    letter-spacing: 0.06em;
    color: var(--muted);
  }}
  input[type="range"] {{ width: 100%; accent-color: var(--accent); }}
  input[type="text"], select {{
    background: #0f1112;
    border: 1px solid var(--line);
    color: var(--text);
    border-radius: 6px;
    padding: 0.55rem 0.7rem;
    font: inherit;
    text-transform: none;
    letter-spacing: 0;
    font-size: 0.95rem;
  }}
  .row {{
    display: flex;
    align-items: baseline;
    justify-content: space-between;
    gap: 0.75rem;
  }}
  .value {{
    font-variant-numeric: tabular-nums;
    color: var(--accent);
    font-size: 1.1rem;
  }}
  .chips {{ display: flex; flex-wrap: wrap; gap: 0.4rem; }}
  .chip {{
    border: 1px solid var(--line);
    background: #121516;
    color: var(--text);
    border-radius: 999px;
    padding: 0.3rem 0.7rem;
    font-size: 0.8rem;
    cursor: pointer;
  }}
  .chip:hover {{ border-color: var(--accent); }}
  button.secondary {{
    background: transparent;
    color: var(--muted);
    border: 1px solid var(--line);
    border-radius: 8px;
    padding: 0.65rem 1rem;
    cursor: pointer;
  }}
  .preview-wrap {{
    padding: 1.5rem;
    display: flex;
    flex-direction: column;
    gap: 0.75rem;
    min-height: 420px;
  }}
  .preview {{
    position: relative;
    flex: 1;
    background: #0a0a0a;
    border: 1px solid var(--line);
    border-radius: 12px;
    overflow: hidden;
    min-height: 320px;
    display: flex;
    align-items: center;
    justify-content: center;
    cursor: text;
  }}
  .preview:focus-within {{ border-color: var(--accent); }}
  .preview-type {{
    position: absolute;
    inset: 0;
    width: 100%;
    height: 100%;
    margin: 0;
    padding: 1.5rem 1.75rem;
    border: 0;
    background: transparent;
    color: var(--text);
    caret-color: var(--accent);
    font-family: "{FAMILY}", sans-serif;
    font-weight: 400;
    font-size: 96px;
    line-height: 1.15;
    letter-spacing: -0.02em;
    outline: none;
    resize: none;
    z-index: 1;
  }}
  .preview-hint {{
    position: absolute;
    left: 1.75rem;
    bottom: 1rem;
    color: var(--muted);
    font-size: 0.75rem;
    pointer-events: none;
    z-index: 0;
    opacity: 0.7;
  }}
  .preview:focus-within .preview-hint,
  .preview.has-text .preview-hint {{ opacity: 0; }}
  .status {{
    font-size: 0.85rem;
    color: var(--muted);
    min-height: 1.2em;
  }}
  .status.ok {{ color: var(--accent); }}
  .status.err {{ color: #e8a0a0; }}
  footer {{
    padding: 0.75rem 1.5rem 1.25rem;
    border-top: 1px solid var(--line);
    color: var(--muted);
    font-size: 0.75rem;
  }}
  code {{ color: var(--text); }}
</style>
</head>
<body>
  <header>
    <h1>Namche-Shadow</h1>
    <p>RoundCorner export proof — caps/figures −40, rest −25. Serves <code>woff2</code> / <code>woff</code> / <code>otf</code> from <code>exports/Namche-Shadow/</code>.</p>
  </header>
  <main>
    <aside>
      <label>
        Weight
        <select id="weight">
{_weight_options()}
        </select>
      </label>
      <label>
        <span class="row"><span>Size</span><span class="value" id="sizeVal">96</span></span>
        <input id="size" type="range" min="24" max="220" step="1" value="96"/>
      </label>
      <label>
        Preview text
        <input id="text" type="text" value="Namche" autocomplete="off" spellcheck="false"/>
      </label>
      <div class="chips">
        <button class="chip" type="button" data-text="Namche">Namche</button>
        <button class="chip" type="button" data-text="NAMCHE">NAMCHE</button>
        <button class="chip" type="button" data-text="Hamburgefonstiv">Hamburgefonstiv</button>
        <button class="chip" type="button" data-text="To AVATAR">To AVATAR</button>
        <button class="chip" type="button" data-text="0123456789">0123456789</button>
        <button class="chip" type="button" data-text="ÄÖÜßæœ">ÄÖÜßæœ</button>
      </div>
      <button class="secondary" id="refreshBtn" type="button">Reload fonts</button>
      <div class="status" id="status">Ready</div>
    </aside>
    <section class="preview-wrap">
      <div class="preview" id="preview">
        <textarea id="previewType" class="preview-type" spellcheck="false" autocomplete="off" aria-label="Type preview text">Namche</textarea>
        <div class="preview-hint">Click and type to proof…</div>
      </div>
    </section>
  </main>
  <footer>
    Glyphs RoundCorner filters on static instances · VF kept unfiltered (incompatible after rounding).
  </footer>
<script>
const $ = (id) => document.getElementById(id);

function setStatus(msg, cls) {{
  const el = $("status");
  el.textContent = msg;
  el.className = "status" + (cls ? " " + cls : "");
}}

function syncText(fromPreview) {{
  const val = fromPreview ? $("previewType").value : $("text").value;
  if ($("text").value !== val) $("text").value = val;
  if ($("previewType").value !== val) $("previewType").value = val;
  $("preview").classList.toggle("has-text", Boolean(val && val.length));
}}

function applyPreview() {{
  syncText(document.activeElement === $("previewType"));
  const weight = $("weight").value;
  const size = $("size").value;
  const style = $("weight").selectedOptions[0].textContent;
  $("sizeVal").textContent = size;
  $("previewType").style.fontWeight = weight;
  $("previewType").style.fontSize = size + "px";
  document.querySelector("header h1").style.fontWeight = weight;
  setStatus(`Preview · ${{style}} · ${{size}}px`, "ok");
}}

$("weight").addEventListener("change", applyPreview);
$("size").addEventListener("input", applyPreview);
$("text").addEventListener("input", () => {{
  syncText(false);
  applyPreview();
}});
$("previewType").addEventListener("input", () => {{
  syncText(true);
  applyPreview();
}});
$("preview").addEventListener("click", () => {{
  $("previewType").focus();
}});
$("refreshBtn").addEventListener("click", () => {{
  // Cache-bust @font-face by reloading
  location.reload();
}});
document.querySelectorAll(".chip").forEach((btn) => {{
  btn.addEventListener("click", () => {{
    $("text").value = btn.dataset.text;
    $("previewType").value = btn.dataset.text;
    syncText(false);
    applyPreview();
  }});
}});

document.fonts.ready.then(() => {{
  syncText(false);
  applyPreview();
  setStatus("Namche-Shadow loaded", "ok");
}}).catch((err) => setStatus(String(err), "err"));
</script>
</body>
</html>
"""


class Handler(BaseHTTPRequestHandler):
    def log_message(self, fmt: str, *args) -> None:
        sys.stderr.write("%s - %s\n" % (self.address_string(), fmt % args))

    def _send(self, code: int, body: bytes, content_type: str) -> None:
        self.send_response(code)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self) -> None:
        parsed = urlparse(self.path)
        path = unquote(parsed.path)

        if path in ("/", "/index.html"):
            self._send(200, HTML_PAGE.encode("utf-8"), "text/html; charset=utf-8")
            return

        if path.startswith("/fonts/"):
            name = Path(path).name
            if "/" in name or ".." in name or not name.startswith(f"{FAMILY}-") and not name.startswith(f"{FAMILY}["):
                self._send(404, b"Not found", "text/plain; charset=utf-8")
                return
            suffix = Path(name).suffix.lower()
            font_dir = FONT_DIRS.get(suffix)
            if font_dir is None:
                self._send(404, b"Unsupported font format", "text/plain; charset=utf-8")
                return
            font_path = font_dir / name
            if not font_path.is_file():
                self._send(
                    404,
                    f"Missing font: {font_path}".encode("utf-8"),
                    "text/plain; charset=utf-8",
                )
                return
            ctype = {
                ".woff2": "font/woff2",
                ".woff": "font/woff",
                ".otf": "font/otf",
                ".ttf": "font/ttf",
            }.get(suffix) or (mimetypes.guess_type(name)[0] or "application/octet-stream")
            self._send(200, font_path.read_bytes(), ctype)
            return

        self._send(404, b"Not found", "text/plain; charset=utf-8")


def main() -> int:
    otf_dir = FONT_DIRS[".otf"]
    if not otf_dir.is_dir():
        sys.stderr.write(
            f"Namche-Shadow fonts not found:\n  {otf_dir}\n"
            "Export/rename OTFs into exports/Namche-Shadow/otf/ first.\n"
        )
        return 1

    missing = []
    for style, _ in WEIGHTS:
        for ext, folder in ((".otf", otf_dir), (".woff", FONT_DIRS[".woff"]), (".woff2", FONT_DIRS[".woff2"])):
            if not (folder / f"{FAMILY}-{style}{ext}").is_file():
                missing.append(f"{FAMILY}-{style}{ext}")
    if missing:
        sys.stderr.write("Missing fonts:\n  " + "\n  ".join(missing) + "\n")
        return 1

    venv_python = SCRIPT_DIR.parent / ".venv-inner-round" / "bin" / "python"
    if venv_python.is_file() and Path(sys.executable).resolve() != venv_python.resolve():
        import os

        os.execv(str(venv_python), [str(venv_python), str(Path(__file__).resolve()), *sys.argv[1:]])

    server = ThreadingHTTPServer((HOST, PORT), Handler)
    url = f"http://{HOST}:{PORT}/"
    print(f"Namche-Shadow → {url}")
    print(f"Fonts:   {NAMCHE_DIR}/{{woff2,woff,otf}}")
    print("Ctrl+C to stop")

    threading.Timer(0.6, lambda: webbrowser.open(url)).start()
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nStopped.")
    finally:
        server.server_close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
