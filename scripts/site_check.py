#!/usr/bin/env python3
"""Drive the built index page in Chromium and check the cover flow behaves as a carousel should.

    make site-check                         # after make site
    python scripts/site_check.py _site      # needs Playwright and axe-playwright-python (the gates' browser)

It checks the WAI-ARIA carousel roles, that only the centered talk is reachable, the keys, a click on a
side cover, the announcement after a glide, focus kept on the new centered talk, target sizes, the
reduced-motion and no-script pages, and axe at 1920 and on a phone in both themes. Exits 1 on a failure.
"""

from __future__ import annotations

import functools
import http.server
import pathlib
import re
import sys
import threading

from axe_playwright_python.sync_playwright import Axe
from playwright.sync_api import Page, sync_playwright

STATE = """() => {
  const all = [...document.querySelectorAll('.talk')];
  const c = all.findIndex((s) => !s.hasAttribute('aria-hidden'));
  return {
    c, n: all.length, shown: all.filter((s) => !s.hasAttribute('aria-hidden')).length,
    live: document.querySelector('[aria-live]').textContent, hash: location.hash,
    inert: all.map((s) => s.querySelector('.about').inert),
    img: all[c] && all[c].querySelector('img') ? all[c].querySelector('img').src.split('/').pop() : null,
    loop: !!(all[c] && all[c].querySelector('img[data-loop]')),
    anim: all[c] ? getComputedStyle(all[c].querySelector('.cover')).animationName : null,
  };
}"""
#: Long enough for a smooth glide to land and the strip to report it has settled.
SETTLE_MS = 1400


class Report:
    def __init__(self) -> None:
        self.failed: list[str] = []

    def check(self, name: str, ok: bool, detail: object = "") -> None:
        print(f"{'ok  ' if ok else 'FAIL'} {name}" + (f": {detail}" if detail and not ok else ""))
        if not ok:
            self.failed.append(name)


def axe(page: Page) -> list[str]:
    result = Axe().run(page, options={"runOnly": ["wcag2a", "wcag2aa", "wcag21aa", "wcag22aa", "best-practice"]})
    return [f"{v['id']} {v['nodes'][0]['target']}" for v in result.response["violations"]]


def serve(root: pathlib.Path) -> tuple[http.server.ThreadingHTTPServer, str]:
    class Quiet(http.server.SimpleHTTPRequestHandler):
        def log_message(self, *args: object) -> None:
            pass

    handler = functools.partial(Quiet, directory=str(root))
    server = http.server.ThreadingHTTPServer(("127.0.0.1", 0), handler)
    threading.Thread(target=server.serve_forever, daemon=True).start()
    return server, f"http://127.0.0.1:{server.server_address[1]}/"


def run(url: str) -> Report:
    r = Report()
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page(viewport={"width": 1920, "height": 1080})
        errors: list[str] = []
        page.on("pageerror", lambda e: errors.append(str(e)))
        page.goto(url)
        page.wait_for_timeout(SETTLE_MS)
        s = page.evaluate(STATE)
        middle = (s["n"] - 1) // 2
        r.check("opens on the middle talk, announcing nothing", s["c"] == middle and s["live"] == "", s)
        r.check("one talk shown, the others hidden and inert", s["shown"] == 1 and s["inert"].count(False) == 1, s)
        roles = page.evaluate("""() => ({
          region: document.getElementById('talks').getAttribute('aria-roledescription'),
          slides: [...document.querySelectorAll('.talk')].every((t) => t.getAttribute('role') === 'group'
            && t.getAttribute('aria-roledescription') === 'slide'),
          names: [...document.querySelectorAll('.talk')].map((t) => t.getAttribute('aria-labelledby').split(' ')
            .map((id) => document.getElementById(id).textContent).join('')),
        })""")
        r.check("carousel and slide roles", roles["region"] == "carousel" and roles["slides"], roles)
        r.check(
            "each slide named by its title and position",
            all(name.endswith(f", {i + 1} of {s['n']}") for i, name in enumerate(roles["names"])),
            roles["names"],
        )
        if s["loop"]:
            r.check("the centered talk plays its preview loop", s["img"] == "thumb-loop.webp", s["img"])

        page.keyboard.press("ArrowRight")
        page.wait_for_timeout(SETTLE_MS)
        s = page.evaluate(STATE)
        r.check(
            "ArrowRight centers the next talk and announces it once settled",
            s["c"] == middle + 1 and s["live"].endswith(f"{middle + 2} of {s['n']}") and s["hash"],
            s,
        )
        page.keyboard.press("ArrowLeft")
        page.keyboard.press("ArrowLeft")
        page.wait_for_timeout(SETTLE_MS)
        r.check("two quick presses add up", page.evaluate(STATE)["c"] == middle - 1)

        side = page.locator(".talk").nth(0).locator(".cover").bounding_box()
        assert side is not None
        page.mouse.click(side["x"] + side["width"] * 0.3, side["y"] + side["height"] / 2)
        page.wait_for_timeout(SETTLE_MS)
        r.check("a click on a side cover centers it without leaving", page.evaluate(STATE)["c"] == 0, page.url)
        r.check(
            "previous is marked unavailable on the first talk",
            page.get_attribute(".prev", "aria-disabled") == "true",
        )

        page.focus(".talk:not([aria-hidden]) .open")
        page.keyboard.press("ArrowRight")
        page.wait_for_timeout(SETTLE_MS)
        focus = page.evaluate(
            "(() => { const a = document.activeElement; return [a.className, a.closest('.talk') === "
            "document.querySelector('.talk:not([aria-hidden])')]; })()"
        )
        r.check("focus moves to the new centered talk's Open the deck", focus == ["open", True], focus)

        page.goto("about:blank")
        page.goto(url)
        page.wait_for_timeout(SETTLE_MS)
        tabbed = []
        for _ in range(12):
            page.keyboard.press("Tab")
            tabbed.append(page.evaluate("document.activeElement.closest('[aria-hidden], [inert]') === null"))
        r.check("Tab never reaches a hidden talk", all(tabbed), tabbed)
        r.check("axe, 1920, light", not (v := axe(page)), v)
        r.check("no script errors", not errors, errors)
        page.close()

        for scheme in ("light", "dark"):
            ctx = browser.new_context(
                viewport={"width": 390, "height": 844}, color_scheme=scheme, is_mobile=True, has_touch=True
            )
            phone = ctx.new_page()
            phone.goto(url)
            phone.wait_for_timeout(SETTLE_MS)
            r.check(f"axe, phone, {scheme}", not (v := axe(phone)), v)
            sizes = phone.evaluate(
                "[...document.querySelectorAll('.talk:not([aria-hidden]) .chip, .talk:not([aria-hidden]) .open,"
                " .step, .dots button')].map((e) => { const b = e.getBoundingClientRect();"
                " return [e.className, b.width, b.height]; })"
            )
            r.check(
                f"targets at least 24 px, the primary and steps 44 px ({scheme})",
                all(w >= 24 and h >= 24 for _, w, h in sizes)
                and all(h >= 44 for c, _, h in sizes if c in ("open", "step prev", "step next")),
                sizes,
            )
            r.check(
                f"no sideways page scroll on a phone ({scheme})",
                phone.evaluate("document.documentElement.scrollWidth <= innerWidth"),
            )
            ctx.close()

        ctx = browser.new_context(viewport={"width": 1920, "height": 1080}, reduced_motion="reduce")
        still = ctx.new_page()
        still.goto(url)
        still.wait_for_timeout(SETTLE_MS)
        s = still.evaluate(STATE)
        r.check("reduced motion: flat covers, no loop", s["anim"] == "flow-flat" and s["img"] != "thumb-loop.webp", s)
        ctx.close()

        # The page as a browser without script draws it: served with its scripts removed, so axe can still run.
        ctx = browser.new_context(viewport={"width": 1920, "height": 1080})
        plain = ctx.new_page()
        plain.route(
            url,
            lambda route: route.fulfill(
                response=(resp := route.fetch()), body=re.sub(r"<script>.*?</script>", "", resp.text(), flags=re.S)
            ),
        )
        plain.goto(url)
        plain.wait_for_timeout(SETTLE_MS)  # the cards' entrance fade has ended
        r.check("the scripts were removed", plain.evaluate("document.scripts.length") == 0)
        state = plain.evaluate("""() => ({
          flow: document.documentElement.classList.contains('flow'),
          roles: document.querySelectorAll('[aria-roledescription], [inert]').length,
          hidden: document.querySelectorAll('.talk[aria-hidden]').length,
          links: [...document.querySelectorAll('.about a')].filter((a) => a.getBoundingClientRect().width > 0).length,
          total: document.querySelectorAll('.about a').length,
        })""")
        r.check(
            "without script: every talk and link shown, no carousel roles",
            not state["flow"] and not state["roles"] and not state["hidden"] and state["links"] == state["total"],
            state,
        )
        r.check("axe, without script", not (v := axe(plain)), v)
        ctx.close()
        browser.close()
    return r


def main() -> int:
    if len(sys.argv) != 2:
        raise SystemExit("usage: site_check.py SITE_FOLDER")
    root = pathlib.Path(sys.argv[1])
    if not (root / "index.html").is_file():
        raise SystemExit(f"no {root / 'index.html'}; run make site first")
    server, url = serve(root)
    try:
        report = run(url)
    finally:
        server.shutdown()
    if report.failed:
        print(f"{len(report.failed)} check(s) failed", file=sys.stderr)
        return 1
    print("the index page behaves")
    return 0


if __name__ == "__main__":
    sys.exit(main())
