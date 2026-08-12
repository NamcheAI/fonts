#!/usr/bin/env python3
"""
Namche family live preview (http://127.0.0.1:8765).

Serves RoundCorner-exported static fonts from exports/Namche-*/otf|woff|woff2.

  python3 scripts/inner_round_app.py
"""

from __future__ import annotations

import json
import mimetypes
import sys
import threading
import webbrowser
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import unquote, urlparse

SCRIPT_DIR = Path(__file__).resolve().parent
EXPORTS_ROOT = SCRIPT_DIR.parent / "exports"

# Specimen lists families in PREVIEW_FAMILIES that have OTFs under exports/.
PREVIEW_FAMILIES = ("Namche-Shadow", "Namche-Shadow-Simple")

# Known recipes (family folder name → label).
FAMILIES = {
    "Namche-Shadow": {
        "label": "Namche-Shadow",
        "recipe": "multi-tier −60 / −80 / −60(A,V,Z,X,ẞ) / −50(k,x,v,w) / −40(M,N,W,2,4,7,6) / −50(9)",
    },
    "Namche-Shadow-Simple": {
        "label": "Namche-Shadow-Simple",
        "recipe": "caps/figures −40 · rest −25",
    },
}

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


def _family_has_fonts(family: str) -> bool:
    otf = EXPORTS_ROOT / family / "otf"
    if not otf.is_dir():
        return False
    return any((otf / f"{family}-{style}.otf").is_file() for style, _ in WEIGHTS)


def _available_families() -> list[str]:
    """Return previewable families that have OTFs (PREVIEW_FAMILIES only)."""
    found = []
    for name in PREVIEW_FAMILIES:
        if _family_has_fonts(name):
            found.append(name)
            FAMILIES.setdefault(
                name,
                {"label": name, "recipe": "RoundCorner export"},
            )
    return found


def _font_face_css(families: list[str]) -> str:
    blocks = []
    for family in families:
        for style, wght in WEIGHTS:
            stem = f"{family}-{style}"
            blocks.append(
                f"""@font-face {{
  font-family: "{family}";
  src: url("/fonts/{family}/{stem}.woff2") format("woff2"),
       url("/fonts/{family}/{stem}.woff") format("woff"),
       url("/fonts/{family}/{stem}.otf") format("opentype");
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


def _family_options(families: list[str]) -> str:
    opts = []
    for name in families:
        meta = FAMILIES.get(name, {"label": name, "recipe": ""})
        opts.append(
            f'<option value="{name}">{meta["label"]} — {meta["recipe"]}</option>'
        )
    return "\n".join(opts)


def _missing_export_note(families: list[str]) -> str:
    notes = []
    for name in PREVIEW_FAMILIES:
        if name in families:
            continue
        meta = FAMILIES.get(name, {"label": name, "recipe": ""})
        pkg = EXPORTS_ROOT / name / f"{name}.glyphspackage"
        if pkg.is_dir():
            notes.append(
                f"{meta['label']} package ready — export OTFs into "
                f"<code>exports/{name}/otf/</code> (Glyphs: Scripts → Namche → Export {meta['label']})"
            )
        else:
            notes.append(
                f"Export statics into <code>exports/{name}/otf/</code> to preview {meta['label']}."
            )
    if not notes:
        return (
            "Both families shipping: <strong>Namche-Shadow</strong> (multi-tier) and "
            "<strong>Namche-Shadow-Simple</strong> (−40/−25) · Glyphs RoundCorner on statics · VF unfiltered."
        )
    return " · ".join(notes)


def _build_html(families: list[str]) -> str:
    default = families[0]
    recipes = {name: FAMILIES.get(name, {}).get("recipe", "") for name in families}
    footer_note = _missing_export_note(families)
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8"/>
<meta name="viewport" content="width=device-width, initial-scale=1"/>
<title>Namche Fonts</title>
<style>
{_font_face_css(families)}
  :root {{
    --bg: #0e1011;
    --bg-glow: #171c18;
    --panel: #15191a;
    --text: #e8ebe4;
    --muted: #8b928a;
    --accent: #c8d4a8;
    --accent-soft: rgba(200, 212, 168, 0.14);
    --line: #2a2f2c;
    --line-strong: #3a423c;
    --field: #0c0e0f;
    --danger: #e8a0a0;
    --ease-out: cubic-bezier(0.23, 1, 0.32, 1);
    --ease-in-out: cubic-bezier(0.77, 0, 0.175, 1);
    --ease: cubic-bezier(0.25, 0.1, 0.25, 1);
    --press-duration: 140ms;
    --ui-duration: 180ms;
    --swap-duration: 200ms;
  }}
  * {{ box-sizing: border-box; }}
  html, body {{ height: 100%; }}
  body {{
    margin: 0;
    font-family: "{default}", "IBM Plex Sans", "Helvetica Neue", sans-serif;
    background:
      radial-gradient(1200px 600px at 80% -10%, var(--bg-glow), transparent 55%),
      radial-gradient(900px 500px at 0% 100%, rgba(200, 212, 168, 0.05), transparent 50%),
      var(--bg);
    color: var(--text);
    min-height: 100vh;
    display: grid;
    grid-template-rows: auto 1fr auto;
  }}
  header {{
    padding: 1.5rem 1.75rem 1rem;
    border-bottom: 1px solid var(--line);
  }}
  header h1 {{
    margin: 0;
    font-family: "{default}", sans-serif;
    font-weight: 500;
    font-size: clamp(2.1rem, 4vw, 3rem);
    letter-spacing: -0.035em;
    line-height: 1;
  }}
  header p {{
    margin: 0.55rem 0 0;
    color: var(--muted);
    font-size: 0.85rem;
    max-width: 42rem;
  }}
  main {{
    display: grid;
    grid-template-columns: minmax(280px, 340px) 1fr;
    min-height: 0;
  }}
  @media (max-width: 800px) {{
    main {{ grid-template-columns: 1fr; }}
    aside {{ border-right: 0; border-bottom: 1px solid var(--line); }}
  }}
  aside {{
    padding: 1.35rem 1.5rem 1.5rem;
    border-right: 1px solid var(--line);
    background: color-mix(in srgb, var(--panel) 92%, transparent);
    backdrop-filter: blur(10px);
    display: flex;
    flex-direction: column;
    gap: 1.15rem;
  }}
  label {{
    display: flex;
    flex-direction: column;
    gap: 0.45rem;
    font-size: 0.72rem;
    text-transform: uppercase;
    letter-spacing: 0.07em;
    color: var(--muted);
  }}
  input[type="range"] {{
    width: 100%;
    accent-color: var(--accent);
    cursor: pointer;
  }}
  input[type="text"], select {{
    background: var(--field);
    border: 1px solid var(--line);
    color: var(--text);
    border-radius: 8px;
    padding: 0.6rem 0.75rem;
    font: inherit;
    text-transform: none;
    letter-spacing: 0;
    font-size: 0.95rem;
    transition:
      border-color var(--ui-duration) var(--ease),
      background-color var(--ui-duration) var(--ease),
      box-shadow var(--ui-duration) var(--ease);
  }}
  input[type="text"]:focus, select:focus {{
    outline: none;
    border-color: var(--accent);
    box-shadow: 0 0 0 3px var(--accent-soft);
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
    font-size: 1.05rem;
    letter-spacing: 0;
    text-transform: none;
  }}
  .chips {{ display: flex; flex-wrap: wrap; gap: 0.4rem; }}
  .chip, button.secondary {{
    appearance: none;
    -webkit-tap-highlight-color: transparent;
    transition:
      transform var(--press-duration) var(--ease-out),
      border-color var(--ui-duration) var(--ease),
      background-color var(--ui-duration) var(--ease),
      color var(--ui-duration) var(--ease),
      box-shadow var(--ui-duration) var(--ease);
  }}
  .chip {{
    border: 1px solid var(--line);
    background: #121516;
    color: var(--text);
    border-radius: 999px;
    padding: 0.34rem 0.75rem;
    font-size: 0.8rem;
    cursor: pointer;
  }}
  .chip[aria-pressed="true"] {{
    border-color: color-mix(in srgb, var(--accent) 65%, var(--line));
    background: var(--accent-soft);
    color: var(--accent);
    box-shadow: inset 0 0 0 1px rgba(200, 212, 168, 0.08);
  }}
  .chip:active, button.secondary:active {{
    transform: scale(0.97);
  }}
  @media (hover: hover) and (pointer: fine) {{
    .chip:hover {{
      border-color: var(--line-strong);
    }}
    .chip[aria-pressed="true"]:hover {{
      border-color: color-mix(in srgb, var(--accent) 80%, var(--line));
    }}
    button.secondary:hover {{
      border-color: var(--line-strong);
      color: var(--text);
    }}
  }}
  button.secondary {{
    background: transparent;
    color: var(--muted);
    border: 1px solid var(--line);
    border-radius: 8px;
    padding: 0.65rem 1rem;
    cursor: pointer;
    font: inherit;
    font-size: 0.9rem;
    text-align: left;
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
    background:
      linear-gradient(180deg, rgba(255,255,255,0.02), transparent 40%),
      #090a0a;
    border: 1px solid var(--line);
    border-radius: 14px;
    overflow: hidden;
    min-height: 360px;
    display: flex;
    align-items: center;
    justify-content: center;
    cursor: text;
    box-shadow: 0 24px 60px rgba(0, 0, 0, 0.28);
    transition:
      border-color var(--ui-duration) var(--ease),
      box-shadow var(--ui-duration) var(--ease);
  }}
  .preview:focus-within {{
    border-color: color-mix(in srgb, var(--accent) 55%, var(--line));
    box-shadow:
      0 24px 60px rgba(0, 0, 0, 0.28),
      0 0 0 3px var(--accent-soft);
  }}
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
    font-family: "{default}", sans-serif;
    font-weight: 400;
    font-size: 96px;
    line-height: 1.15;
    letter-spacing: -0.02em;
    outline: none;
    resize: none;
    z-index: 1;
    transition:
      opacity var(--swap-duration) var(--ease),
      filter var(--swap-duration) var(--ease);
  }}
  .preview-type.is-swapping {{
    opacity: 0.72;
    filter: blur(2px);
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
    transition: opacity var(--ui-duration) var(--ease-out);
  }}
  .preview:focus-within .preview-hint,
  .preview.has-text .preview-hint {{ opacity: 0; }}
  .status {{
    font-size: 0.85rem;
    color: var(--muted);
    min-height: 1.2em;
    transition: color var(--ui-duration) var(--ease), opacity 120ms var(--ease-out);
  }}
  .status.ok {{ color: var(--accent); }}
  .status.err {{ color: var(--danger); }}
  .status.is-flash {{ opacity: 0.55; }}
  footer {{
    padding: 0.85rem 1.75rem 1.35rem;
    border-top: 1px solid var(--line);
    color: var(--muted);
    font-size: 0.75rem;
  }}
  code {{ color: var(--text); }}
  .chips .chip {{
    opacity: 0;
    transform: translateY(6px);
    animation: chip-in 280ms var(--ease-out) forwards;
  }}
  .chips .chip:nth-child(1) {{ animation-delay: 0ms; }}
  .chips .chip:nth-child(2) {{ animation-delay: 40ms; }}
  .chips .chip:nth-child(3) {{ animation-delay: 80ms; }}
  .chips .chip:nth-child(4) {{ animation-delay: 120ms; }}
  .chips .chip:nth-child(5) {{ animation-delay: 160ms; }}
  .chips .chip:nth-child(6) {{ animation-delay: 200ms; }}
  @keyframes chip-in {{
    to {{
      opacity: 1;
      transform: translateY(0);
    }}
  }}
  @media (prefers-reduced-motion: reduce) {{
    .chip, button.secondary, input[type="text"], select, .preview, .preview-type, .preview-hint, .status {{
      transition-duration: 0.01ms !important;
    }}
    .chip:active, button.secondary:active {{
      transform: none;
    }}
    .preview-type.is-swapping {{
      filter: none;
      opacity: 0.85;
    }}
    .chips .chip {{
      animation: none;
      opacity: 1;
      transform: none;
    }}
  }}
</style>
</head>
<body>
  <header>
    <h1 id="brand">{default}</h1>
    <p id="subtitle">RoundCorner static proof · <span id="recipe">{FAMILIES[default]["recipe"]}</span></p>
  </header>
  <main>
    <aside>
      <label>
        Family
        <select id="family">
{_family_options(families)}
        </select>
      </label>
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
      <div class="chips" role="group" aria-label="Sample strings">
        <button class="chip" type="button" data-text="Namche" aria-pressed="true">Namche</button>
        <button class="chip" type="button" data-text="NAMCHE" aria-pressed="false">NAMCHE</button>
        <button class="chip" type="button" data-text="Hamburgefonstiv" aria-pressed="false">Hamburgefonstiv</button>
        <button class="chip" type="button" data-text="To AVATAR" aria-pressed="false">To AVATAR</button>
        <button class="chip" type="button" data-text="0123456789" aria-pressed="false">0123456789</button>
        <button class="chip" type="button" data-text="ÄÖÜßæœ" aria-pressed="false">ÄÖÜßæœ</button>
      </div>
      <button class="secondary" id="refreshBtn" type="button">Reload fonts</button>
      <div class="status" id="status" role="status" aria-live="polite">Ready</div>
    </aside>
    <section class="preview-wrap">
      <div class="preview" id="preview">
        <textarea id="previewType" class="preview-type" spellcheck="false" autocomplete="off" aria-label="Type preview text">Namche</textarea>
        <div class="preview-hint">Click and type to proof…</div>
      </div>
    </section>
  </main>
  <footer>
    {footer_note}
  </footer>
<script>
const RECIPES = {json.dumps(recipes)};
const $ = (id) => document.getElementById(id);
const reduceMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
let lastFamily = null;
let lastWeight = null;
let swapTimer = 0;

function setStatus(msg, cls, {{ flash = false }} = {{}}) {{
  const el = $("status");
  el.textContent = msg;
  el.className = "status" + (cls ? " " + cls : "") + (flash ? " is-flash" : "");
  if (!flash) return;
  requestAnimationFrame(() => {{
    requestAnimationFrame(() => el.classList.remove("is-flash"));
  }});
}}

function syncText(fromPreview) {{
  const val = fromPreview ? $("previewType").value : $("text").value;
  if ($("text").value !== val) $("text").value = val;
  if ($("previewType").value !== val) $("previewType").value = val;
  $("preview").classList.toggle("has-text", Boolean(val && val.length));
  syncChipPressed(val);
}}

function syncChipPressed(val) {{
  document.querySelectorAll(".chip").forEach((btn) => {{
    btn.setAttribute("aria-pressed", btn.dataset.text === val ? "true" : "false");
  }});
}}

function pulseSwap() {{
  if (reduceMotion) return;
  const el = $("previewType");
  el.classList.add("is-swapping");
  clearTimeout(swapTimer);
  swapTimer = window.setTimeout(() => el.classList.remove("is-swapping"), 200);
}}

function applyPreview({{ swap = false }} = {{}}) {{
  syncText(document.activeElement === $("previewType"));
  const family = $("family").value;
  const weight = $("weight").value;
  const size = $("size").value;
  const style = $("weight").selectedOptions[0].textContent;
  const familyChanged = lastFamily !== null && family !== lastFamily;
  const weightChanged = lastWeight !== null && weight !== lastWeight;
  if (swap && (familyChanged || weightChanged)) pulseSwap();
  $("sizeVal").textContent = size;
  $("previewType").style.fontFamily = `"${{family}}", sans-serif`;
  $("previewType").style.fontWeight = weight;
  $("previewType").style.fontSize = size + "px";
  $("brand").textContent = family;
  $("brand").style.fontFamily = `"${{family}}", sans-serif`;
  $("brand").style.fontWeight = weight;
  $("recipe").textContent = RECIPES[family] || "";
  lastFamily = family;
  lastWeight = weight;
  // Flash status only on occasional family/weight swaps — never on size scrubbing.
  setStatus(
    `Preview · ${{family}} · ${{style}} · ${{size}}px`,
    "ok",
    {{ flash: Boolean(swap && (familyChanged || weightChanged)) }},
  );
}}

$("family").addEventListener("change", () => applyPreview({{ swap: true }}));
$("weight").addEventListener("change", () => applyPreview({{ swap: true }}));
// Size changes are high-frequency — update instantly, no swap animation.
$("size").addEventListener("input", () => applyPreview());
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
$("refreshBtn").addEventListener("click", () => location.reload());
document.querySelectorAll(".chip").forEach((btn) => {{
  btn.addEventListener("click", () => {{
    $("text").value = btn.dataset.text;
    $("previewType").value = btn.dataset.text;
    syncText(false);
    applyPreview();
    $("previewType").focus({{ preventScroll: true }});
  }});
}});

document.fonts.ready.then(() => {{
  syncText(false);
  applyPreview();
}}).catch((err) => setStatus(String(err), "err"));
</script>
</body>
</html>
"""


class Handler(BaseHTTPRequestHandler):
    families: list[str] = []
    html: bytes = b""

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
            self._send(200, self.html, "text/html; charset=utf-8")
            return

        # /fonts/<Family>/<file>
        if path.startswith("/fonts/"):
            parts = path.strip("/").split("/")
            if len(parts) != 3:
                self._send(404, b"Not found", "text/plain; charset=utf-8")
                return
            _, family, name = parts
            if (
                family not in self.families
                or "/" in name
                or ".." in name
                or not (name.startswith(f"{family}-") or name.startswith(f"{family}["))
            ):
                self._send(404, b"Not found", "text/plain; charset=utf-8")
                return
            suffix = Path(name).suffix.lower()
            sub = {".woff2": "woff2", ".woff": "woff", ".otf": "otf", ".ttf": "ttf"}.get(suffix)
            if not sub:
                self._send(404, b"Unsupported font format", "text/plain; charset=utf-8")
                return
            font_path = EXPORTS_ROOT / family / sub / name
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
            }.get(suffix, "application/octet-stream")
            self._send(200, font_path.read_bytes(), ctype)
            return

        self._send(404, b"Not found", "text/plain; charset=utf-8")


def main() -> int:
    families = _available_families()
    if not families:
        sys.stderr.write(
            "No preview fonts found.\n"
            f"Export statics into exports/<Family>/otf/ "
            f"(PREVIEW_FAMILIES={', '.join(PREVIEW_FAMILIES)}).\n"
        )
        return 1

    Handler.families = families
    Handler.html = _build_html(families).encode("utf-8")

    venv_python = SCRIPT_DIR.parent / ".venv-inner-round" / "bin" / "python"
    if venv_python.is_file() and Path(sys.executable).resolve() != venv_python.resolve():
        import os

        os.execv(str(venv_python), [str(venv_python), str(Path(__file__).resolve()), *sys.argv[1:]])

    server = ThreadingHTTPServer((HOST, PORT), Handler)
    url = f"http://{HOST}:{PORT}/"
    print(f"Namche fonts → {url}")
    print(f"  Preview families: {', '.join(PREVIEW_FAMILIES)}")
    for name in families:
        print(f"  {name}: {EXPORTS_ROOT / name}")
    for name in PREVIEW_FAMILIES:
        if name in families:
            continue
        pkg = EXPORTS_ROOT / name / f"{name}.glyphspackage"
        if pkg.is_dir():
            recipe = FAMILIES.get(name, {}).get("recipe", "")
            print(f"  {name}: package ready, export OTFs to preview ({recipe})")
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
