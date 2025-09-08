# ruff: noqa: E402
from __future__ import annotations

"""Module: tools/pull_browser_private_saves.py
Auto-added docstring to aid static analysis and navigation.
"""
# pull_perchance_attach.py — attach to an EXISTING Chrome tab and extract Perchance "private saves"
# No new windows. Reads localStorage/sessionStorage/<img> data URLs, tries IndexedDB too, writes files to Downloads.

import os
import re
import time
import base64
import pathlib
import sys
import subprocess
from urllib.parse import unquote


# --- Auto-install deps ---
def install_if_missing(pkg, imp=None):
    try:
        __import__(imp or pkg)
    except ImportError:
        print(f"[INFO] Installing missing package: {pkg}")
        subprocess.check_call([sys.executable, "-m", "pip", "install", pkg])


install_if_missing("selenium")
install_if_missing("webdriver_manager")

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import JavascriptException
from selenium.webdriver.support.ui import WebDriverWait

OUTPUT_DIR = os.path.join(os.path.expanduser("~"), "Downloads")
TARGET_HOST = "perchance.org"  # tab URL must contain this

DATA_URL_RE = re.compile(r"^data:image/(png|jpeg|jpg|webp);base64,", re.IGNORECASE)


def sanitize(name: str) -> str:
    return re.sub(r"[^\w\-.]+", "_", (name or "image")).strip()[:120]


def decode_and_save(data_url: str, outdir: str, base: str):
    m = DATA_URL_RE.match(data_url)
    if not m:
        return None
    ext = m.group(1).lower()
    if ext == "jpg":
        ext = "jpeg"
    b64 = data_url.split(",", 1)[1]
    try:
        b64 = unquote(b64)
    except Exception:
        pass
    try:
        raw = base64.b64decode(b64, validate=False)
    except Exception:
        return None
    pathlib.Path(outdir).mkdir(parents=True, exist_ok=True)
    i = 1
    while True:
        fn = os.path.join(outdir, f"{base}_{i:03d}.{ext}")
        if not os.path.exists(fn):
            break
        i += 1
    with open(fn, "wb") as f:
        f.write(raw)
    return fn


JS_COLLECT_LOCAL = r"""
(function collectLocal() {
  function fromStorage(store, label) {
    const out = [];
    try {
      if (!store) return out;
      for (let i=0; i<store.length; i++) {
        const k = store.key(i);
        const v = store.getItem(k);
        if (typeof v === 'string' && v.startsWith('data:image')) {
          out.push({source: label, key: k, dataUrl: v});
        } else if (typeof v === 'string' && v.includes('data:image')) {
          const matches = v.match(/data:image\/(?:png|jpeg|jpg|webp);base64,[A-Za-z0-9+/=]+/g);
          if (matches) { for (const m of matches) out.push({source: label, key: k, dataUrl: m}); }
        }
      }
    } catch(e) {}
    return out;
  }
  function fromImgs(doc, label) {
    const out = [];
    try {
      const imgs = doc.querySelectorAll('img');
      for (const img of imgs) {
        const src = img.getAttribute('src') || '';
        if (src.startsWith('data:image')) {
          out.push({source: label, key: img.getAttribute('alt') || 'img', dataUrl: src});
        }
      }
    } catch(e) {}
    return out;
  }
  const results = [];
  try {
    results.push(...fromStorage(window.localStorage, 'top.localStorage'));
    results.push(...fromStorage(window.sessionStorage, 'top.sessionStorage'));
    results.push(...fromImgs(document, 'top.document'));
  } catch(e){}
  const seen = new Set(); const uniq = [];
  for (const r of results) { if (!seen.has(r.dataUrl)) { uniq.push(r); seen.add(r.dataUrl);} }
  return uniq;
})();
"""

# IndexedDB collection must be async; Selenium supports execute_async_script
JS_COLLECT_INDEXEDDB = r"""
var done = arguments[0];
(async function collectIndexedDB() {
  const out = [];
  try {
    if (!('indexedDB' in window) || !indexedDB.databases) { done(out); return; }
    const dbs = await indexedDB.databases();
    for (const dbinfo of dbs) {
      try {
        const db = await new Promise((res, rej) => {
          const r = indexedDB.open(dbinfo.name);
          r.onsuccess = () => res(r.result);
          r.onerror = () => rej(r.error||new Error('open failed'));
        });
        for (const storeName of db.objectStoreNames) {
          try {
            const tx = db.transaction(storeName, 'readonly');
            const store = tx.objectStore(storeName);
            const req = store.getAll();
            const vals = await new Promise((res, rej) => {
              req.onsuccess = () => res(req.result || []);
              req.onerror = () => rej(req.error || new Error('getAll failed'));
            });
            for (const v of vals) {
              if (typeof v === 'string') {
                const m = v.match(/data:image\/(?:png|jpeg|jpg|webp);base64,[A-Za-z0-9+/=]+/g);
                if (m) for (const d of m) out.push({source: `idb:${dbinfo.name}/${storeName}`, key: 'item', dataUrl: d});
              } else if (v && typeof v === 'object') {
                const s = JSON.stringify(v);
                const m = s.match(/data:image\/(?:png|jpeg|jpg|webp);base64,[A-Za-z0-9+/=]+/g);
                if (m) for (const d of m) out.push({source: `idb:${dbinfo.name}/${storeName}`, key: 'json', dataUrl: d});
              }
            }
            db.close();
          } catch(e){}
        }
      } catch(e){}
    }
  } catch(e){}
  // dedupe
  const seen = new Set(); const uniq = [];
  for (const r of out) { if (!seen.has(r.dataUrl)) { uniq.push(r); seen.add(r.dataUrl);} }
  done(uniq);
})();
"""


def attach_driver():
    addr = os.environ.get("ATTACH_ADDR")  # "127.0.0.1:9222"
    if not addr:
        print(
            "[ERROR] ATTACH_ADDR not set. Run Chrome with --remote-debugging-port and set ATTACH_ADDR, e.g.:"
        )
        print('  $env:ATTACH_ADDR = "127.0.0.1:9222"')
        sys.exit(1)
    opts = Options()
    opts.add_experimental_option("debuggerAddress", addr)
    # Important: NO Service(...) here; we’re attaching to your existing Chrome
    return webdriver.Chrome(options=opts)


def pick_perchance_tab(driver):
    # try to switch to a window whose URL contains our target host
    for handle in driver.window_handles:
        driver.switch_to.window(handle)
        url = driver.current_url or ""
        if TARGET_HOST in url:
            return True
    return False


def main():
    driver = attach_driver()
    try:
        if not pick_perchance_tab(driver):
            print(
                f"[ERROR] No tab with '{TARGET_HOST}' found. Open the Perchance page in that Chrome and try again."
            )
            return

        # Give the page a moment to finish any lazy-init of storage
        WebDriverWait(driver, 10).until(
            lambda d: d.execute_script("return document.readyState") == "complete"
        )
        time.sleep(2)

        # Collect localStorage/sessionStorage/imgs
        try:
            local_results = driver.execute_script(JS_COLLECT_LOCAL) or []
        except JavascriptException as e:
            print(f"[WARN] JS local collector failed: {e}")
            local_results = []

        # Collect IndexedDB (best effort; may not be supported)
        try:
            idb_results = driver.execute_async_script(JS_COLLECT_INDEXEDDB) or []
        except Exception as e:
            # execute_async_script can fail if site blocks it; we'll continue with local results
            print(f"[WARN] IndexedDB collector failed: {e}")
            idb_results = []

        results = []
        seen = set()
        for r in local_results + idb_results:
            du = r.get("dataUrl")
            if du and du not in seen:
                seen.add(du)
                results.append(r)

        if not results:
            print(
                "No images found in localStorage/sessionStorage/IndexedDB. On the Perchance page, click 'Private Save' first, then rerun."
            )
            return

        saved = 0
        for r in results:
            src = r.get("source", "store")
            key = r.get("key", "img")
            base = sanitize(f"perchance_{src}_{key}")
            out = decode_and_save(r["dataUrl"], OUTPUT_DIR, base)
            if out:
                print("Saved:", out)
                saved += 1

        print(f"\nDone. Saved {saved} image(s) to: {OUTPUT_DIR}")
    finally:
        # Do NOT close the browser; you're attached to your running Chrome
        pass


if __name__ == "__main__":
    main()
