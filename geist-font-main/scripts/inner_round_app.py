#!/usr/bin/env python3
"""
Interactive inner-round preview + export for Geist Sans upright.

Always reads from immutable geist-font-original/. Never writes there.
Exports go to geist-font-main/exports/Geist-inner-r{N}/.

  python3 scripts/inner_round_app.py
  # open http://127.0.0.1:8765
"""

from __future__ import annotations

import json
import shutil
import sys
import threading
import webbrowser
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlparse

SCRIPT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPT_DIR))

import round_inner_corners as ric  # noqa: E402

HOST = "127.0.0.1"
PORT = 8765

ORIGINAL_PKG = ric.default_original_package()
EXPORTS_ROOT = SCRIPT_DIR.parent / "exports"


HTML_PAGE = r"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8"/>
<meta name="viewport" content="width=device-width, initial-scale=1"/>
<title>Geist Inner Round</title>
<style>
  :root {
    --bg: #111314;
    --panel: #1a1d1f;
    --text: #e8ebe4;
    --muted: #8b928a;
    --accent: #c8d4a8;
    --line: #2a2f2c;
  }
  * { box-sizing: border-box; }
  body {
    margin: 0;
    font-family: "IBM Plex Sans", "Helvetica Neue", sans-serif;
    background: var(--bg);
    color: var(--text);
    min-height: 100vh;
    display: grid;
    grid-template-rows: auto 1fr auto;
  }
  header {
    padding: 1.25rem 1.5rem 0.75rem;
    border-bottom: 1px solid var(--line);
  }
  header h1 {
    margin: 0;
    font-size: 1.1rem;
    font-weight: 560;
    letter-spacing: 0.02em;
  }
  header p {
    margin: 0.35rem 0 0;
    color: var(--muted);
    font-size: 0.85rem;
  }
  main {
    display: grid;
    grid-template-columns: minmax(260px, 320px) 1fr;
    min-height: 0;
  }
  @media (max-width: 800px) {
    main { grid-template-columns: 1fr; }
  }
  aside {
    padding: 1.25rem 1.5rem;
    border-right: 1px solid var(--line);
    background: var(--panel);
    display: flex;
    flex-direction: column;
    gap: 1.1rem;
  }
  label {
    display: flex;
    flex-direction: column;
    gap: 0.4rem;
    font-size: 0.78rem;
    text-transform: uppercase;
    letter-spacing: 0.06em;
    color: var(--muted);
  }
  input[type="range"] { width: 100%; accent-color: var(--accent); }
  input[type="text"], select {
    background: #0f1112;
    border: 1px solid var(--line);
    color: var(--text);
    border-radius: 6px;
    padding: 0.55rem 0.7rem;
    font: inherit;
    text-transform: none;
    letter-spacing: 0;
    font-size: 0.95rem;
  }
  .row {
    display: flex;
    align-items: baseline;
    justify-content: space-between;
    gap: 0.75rem;
  }
  .value {
    font-variant-numeric: tabular-nums;
    color: var(--accent);
    font-size: 1.1rem;
  }
  .chips { display: flex; flex-wrap: wrap; gap: 0.4rem; }
  .chip {
    border: 1px solid var(--line);
    background: #121516;
    color: var(--text);
    border-radius: 999px;
    padding: 0.3rem 0.7rem;
    font-size: 0.8rem;
    cursor: pointer;
  }
  .chip:hover { border-color: var(--accent); }
  button.primary {
    margin-top: auto;
    background: var(--accent);
    color: #141714;
    border: 0;
    border-radius: 8px;
    padding: 0.85rem 1rem;
    font-weight: 650;
    font-size: 0.95rem;
    cursor: pointer;
  }
  button.primary:disabled { opacity: 0.5; cursor: wait; }
  button.secondary {
    background: transparent;
    color: var(--muted);
    border: 1px solid var(--line);
    border-radius: 8px;
    padding: 0.65rem 1rem;
    cursor: pointer;
  }
  .preview-wrap {
    padding: 1.5rem;
    display: flex;
    flex-direction: column;
    gap: 0.75rem;
    min-height: 420px;
  }
  .preview {
    flex: 1;
    background: #0a0a0a;
    border: 1px solid var(--line);
    border-radius: 12px;
    overflow: hidden;
    min-height: 320px;
    display: flex;
    align-items: center;
    justify-content: center;
  }
  .preview svg { width: 100%; height: 100%; }
  .status {
    font-size: 0.85rem;
    color: var(--muted);
    min-height: 1.2em;
  }
  .status.ok { color: var(--accent); }
  .status.err { color: #e8a0a0; }
  footer {
    padding: 0.75rem 1.5rem 1.25rem;
    border-top: 1px solid var(--line);
    color: var(--muted);
    font-size: 0.75rem;
  }
  code { color: var(--text); }
</style>
</head>
<body>
  <header>
    <h1>Geist Inner Round</h1>
    <p>Reads only from <code>geist-font-original</code>. Export writes to <code>geist-font-main/exports/</code>.</p>
  </header>
  <main>
    <aside>
      <label>
        <span class="row"><span>Radius (Regular UPM)</span><span class="value" id="radiusVal">40</span></span>
        <input id="radius" type="range" min="0" max="80" step="1" value="40"/>
      </label>
      <label>
        Master
        <select id="master">
          <option>Thin</option>
          <option selected>Regular</option>
          <option>Black</option>
        </select>
      </label>
      <label>
        Preview text
        <input id="text" type="text" value="Futurism"/>
      </label>
      <div class="chips">
        <button class="chip" type="button" data-text="Futurism">Futurism</button>
        <button class="chip" type="button" data-text="Hamburgefonstiv">Hamburgefonstiv</button>
        <button class="chip" type="button" data-text="FEHTtfkx 0123">FEHTtfkx 0123</button>
      </div>
      <button class="primary" id="exportBtn" type="button">Export font</button>
      <button class="secondary" id="refreshBtn" type="button">Refresh preview</button>
      <div class="status" id="status">Ready</div>
    </aside>
    <section class="preview-wrap">
      <div class="preview" id="preview"></div>
    </section>
  </main>
  <footer>
    Thin / Black radii scale automatically (×0.55 / ×1.35). Export = proof Latin .glyphspackage + Thin/Regular/Black TTFs.
  </footer>
<script>
const $ = (id) => document.getElementById(id);
let timer = null;
let busy = false;

function setStatus(msg, cls) {
  const el = $("status");
  el.textContent = msg;
  el.className = "status" + (cls ? " " + cls : "");
}

async function updatePreview() {
  if (busy) return;
  busy = true;
  const radius = $("radius").value;
  const master = $("master").value;
  const text = $("text").value || "Futurism";
  $("radiusVal").textContent = radius;
  setStatus("Rendering…");
  try {
    const url = `/api/preview?radius=${encodeURIComponent(radius)}&master=${encodeURIComponent(master)}&text=${encodeURIComponent(text)}`;
    const res = await fetch(url);
    if (!res.ok) throw new Error(await res.text());
    const svg = await res.text();
    $("preview").innerHTML = svg;
    const rNum = Number(radius);
    let msg = `Preview · ${master} · r=${radius}`;
    if (rNum > 40) {
      msg += " — may over-round fine features; counters are protected";
    }
    setStatus(msg, "ok");
  } catch (err) {
    setStatus(String(err), "err");
  } finally {
    busy = false;
  }
}

function schedulePreview() {
  clearTimeout(timer);
  timer = setTimeout(updatePreview, 120);
}

$("radius").addEventListener("input", () => {
  $("radiusVal").textContent = $("radius").value;
  schedulePreview();
});
$("master").addEventListener("change", schedulePreview);
$("text").addEventListener("input", schedulePreview);
$("refreshBtn").addEventListener("click", updatePreview);
document.querySelectorAll(".chip").forEach((btn) => {
  btn.addEventListener("click", () => {
    $("text").value = btn.dataset.text;
    updatePreview();
  });
});

$("exportBtn").addEventListener("click", async () => {
  const radius = $("radius").value;
  $("exportBtn").disabled = true;
  setStatus("Exporting… this can take a minute");
  try {
    const res = await fetch("/api/export", {
      method: "POST",
      headers: {"Content-Type": "application/json"},
      body: JSON.stringify({ radius: Number(radius) }),
    });
    const data = await res.json();
    if (!res.ok) throw new Error(data.error || "Export failed");
    const ttfNote = data.ttfs && data.ttfs.length
      ? ` · ${data.ttfs.length} TTF(s)`
      : " · glyphspackage only (install fontmake for TTF)";
    setStatus(`Exported ${data.export_dir}${ttfNote}`, "ok");
  } catch (err) {
    setStatus(String(err), "err");
  } finally {
    $("exportBtn").disabled = false;
  }
});

updatePreview();
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

    def _send_json(self, code: int, payload: dict) -> None:
        data = json.dumps(payload).encode("utf-8")
        self._send(code, data, "application/json; charset=utf-8")

    def do_GET(self) -> None:
        parsed = urlparse(self.path)
        if parsed.path in ("/", "/index.html"):
            self._send(200, HTML_PAGE.encode("utf-8"), "text/html; charset=utf-8")
            return
        if parsed.path == "/api/preview":
            qs = parse_qs(parsed.query)
            try:
                radius = float(qs.get("radius", ["40"])[0])
                master = qs.get("master", ["Regular"])[0]
                text = qs.get("text", ["Futurism"])[0]
                if master not in ric.MASTER_IDS:
                    master = "Regular"
                if not ORIGINAL_PKG.is_dir():
                    raise FileNotFoundError(
                        f"Missing original package: {ORIGINAL_PKG}"
                    )
                svg = ric.render_preview_svg(
                    ORIGINAL_PKG, text, radius=radius, master=master
                )
                self._send(200, svg.encode("utf-8"), "image/svg+xml; charset=utf-8")
            except Exception as exc:
                self._send(500, str(exc).encode("utf-8"), "text/plain; charset=utf-8")
            return
        self._send(404, b"Not found", "text/plain; charset=utf-8")

    def do_POST(self) -> None:
        parsed = urlparse(self.path)
        if parsed.path != "/api/export":
            self._send(404, b"Not found", "text/plain; charset=utf-8")
            return
        length = int(self.headers.get("Content-Length", "0"))
        raw = self.rfile.read(length) if length else b"{}"
        try:
            payload = json.loads(raw.decode("utf-8") or "{}")
            radius = float(payload.get("radius", 40))
            if not ORIGINAL_PKG.is_dir():
                raise FileNotFoundError(f"Missing original package: {ORIGINAL_PKG}")

            export_dir = EXPORTS_ROOT / f"Geist-inner-r{int(round(radius))}"
            if export_dir.exists():
                shutil.rmtree(export_dir)
            export_dir.mkdir(parents=True)

            pkg = ric.export_filleted_package(
                ORIGINAL_PKG, export_dir, radius=radius
            )
            # Copy license
            for name in ("OFL.txt", "AUTHORS.txt"):
                src = ORIGINAL_PKG.parent.parent / name
                if src.exists():
                    shutil.copy2(src, export_dir / name)

            ttf_dir = export_dir / "ttf"
            ttfs = ric.build_ttfs_from_glyphspackage(pkg, ttf_dir)
            self._send_json(
                200,
                {
                    "ok": True,
                    "export_dir": str(export_dir),
                    "glyphspackage": str(pkg),
                    "ttfs": [str(p) for p in ttfs],
                    "radius": radius,
                },
            )
        except Exception as exc:
            self._send_json(500, {"ok": False, "error": str(exc)})


def main() -> int:
    if not ORIGINAL_PKG.is_dir():
        sys.stderr.write(
            f"Original package not found:\n  {ORIGINAL_PKG}\n"
            "Create it first (see geist-font-original/README.md).\n"
        )
        return 1

    venv_python = SCRIPT_DIR.parent / ".venv-inner-round" / "bin" / "python"
    if venv_python.is_file() and Path(sys.executable).resolve() != venv_python.resolve():
        # Re-exec under project venv so export/fontmake deps are available.
        import os

        os.execv(str(venv_python), [str(venv_python), str(Path(__file__).resolve()), *sys.argv[1:]])

    server = ThreadingHTTPServer((HOST, PORT), Handler)
    url = f"http://{HOST}:{PORT}/"
    print(f"Geist Inner Round → {url}")
    print(f"Original: {ORIGINAL_PKG}")
    print(f"Exports:  {EXPORTS_ROOT}")
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
