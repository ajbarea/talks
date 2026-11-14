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
import importlib.util
import pathlib
import re
import sys
import tempfile
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
#: Counts the live region's announcements from now on.
COUNT = """() => { window.__said = 0; const live = document.querySelector('[aria-live]');
  (window.__watch ||= new MutationObserver(() => { window.__said++; }))
    .observe(live, {childList: true, characterData: true, subtree: true}); }"""
#: Which control has focus, and whether it is in the centered talk.
FOCUS = """(() => { const a = document.activeElement;
  return [a.className, a.closest('.talk') === document.querySelector('.talk:not([aria-hidden])')]; })()"""
#: The focused control's focus ring against the colour behind it, as a contrast ratio (0 when it has none).
RING = """() => {
  const el = document.activeElement;
  if (el === document.body) return null;  // Tab has wrapped past the last control
  const st = getComputedStyle(el);
  // Any CSS colour (rgb(), oklab(), color-mix results) as sRGB bytes, read back through a canvas.
  const ctx = Object.assign(document.createElement('canvas'), {width: 1, height: 1}).getContext('2d');
  const rgb = (c) => { ctx.clearRect(0, 0, 1, 1); ctx.fillStyle = c; ctx.fillRect(0, 0, 1, 1);
    return [...ctx.getImageData(0, 0, 1, 1).data].slice(0, 3); };
  const lum = (c) => { const f = (v) => { v /= 255; return v <= 0.03928 ? v / 12.92 : ((v + 0.055) / 1.055) ** 2.4; };
    return 0.2126 * f(c[0]) + 0.7152 * f(c[1]) + 0.0722 * f(c[2]); };
  const ratio = (a, b) => { const [x, y] = [lum(a), lum(b)].sort((p, q) => q - p); return (x + 0.05) / (y + 0.05); };
  const band = el.closest('.stage') && !el.closest('.about');
  const behind = band ? [21, 32, 43] : rgb(getComputedStyle(document.body).backgroundColor);
  const name = el.className || el.textContent.trim().slice(0, 20);
  return [name, st.outlineStyle === 'none' ? 0 : Math.round(ratio(rgb(st.outlineColor), behind) * 10) / 10];
}"""
#: Each visible chip's border colour against the page, as a contrast ratio.
CHIP_BORDER = """() => {
  // Any CSS colour (rgb(), oklab(), color-mix results) as sRGB bytes, read back through a canvas.
  const ctx = Object.assign(document.createElement('canvas'), {width: 1, height: 1}).getContext('2d');
  const rgb = (c) => { ctx.clearRect(0, 0, 1, 1); ctx.fillStyle = c; ctx.fillRect(0, 0, 1, 1);
    return [...ctx.getImageData(0, 0, 1, 1).data].slice(0, 3); };
  const lum = (c) => { const f = (v) => { v /= 255; return v <= 0.03928 ? v / 12.92 : ((v + 0.055) / 1.055) ** 2.4; };
    return 0.2126 * f(c[0]) + 0.7152 * f(c[1]) + 0.0722 * f(c[2]); };
  const page = rgb(getComputedStyle(document.body).backgroundColor);
  return [...document.querySelectorAll('.talk:not([aria-hidden]) .chip')].map((c) => {
    const [x, y] = [lum(rgb(getComputedStyle(c).borderTopColor)), lum(page)].sort((p, q) => q - p);
    return Math.round(((x + 0.05) / (y + 0.05)) * 100) / 100; });
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


def rings(page: Page) -> list[list]:
    """Tab through the page from the top, reading each control's focus ring."""
    page.evaluate("document.activeElement && document.activeElement.blur(); window.scrollTo(0, 0)")
    seen = []
    for _ in range(12):
        page.keyboard.press("Tab")
        seen.append(page.evaluate(RING))
    return [ring for ring in seen if ring]


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
          names: [...document.querySelectorAll('.talk')].map((t) => t.getAttribute('aria-label')),
          titles: [...document.querySelectorAll('.talk h2')].map((h) => h.textContent.trim()),
        })""")
        r.check("carousel and slide roles", roles["region"] == "carousel" and roles["slides"], roles)
        r.check(
            "each slide named by its title and position",
            roles["names"] == [f"{t}, {i + 1} of {s['n']}" for i, t in enumerate(roles["titles"])],
            roles["names"],
        )
        if s["loop"]:
            r.check("the centered talk plays its preview loop", s["img"] == "thumb-loop.webp", s["img"])

        page.evaluate(COUNT)
        page.keyboard.press("ArrowRight")
        page.wait_for_timeout(SETTLE_MS)
        s = page.evaluate(STATE)
        r.check(
            "ArrowRight centers the next talk and announces it exactly once, after it settles",
            s["c"] == middle + 1
            and s["live"].endswith(f"{middle + 2} of {s['n']}")
            and s["hash"]
            and page.evaluate("window.__said") == 1,
            [s, page.evaluate("window.__said")],
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

        for start in (".open", ".chip"):
            page.focus(f".talk:not([aria-hidden]) {start}")
            page.evaluate(COUNT)
            page.keyboard.press("ArrowRight")
            page.wait_for_timeout(SETTLE_MS)
            focus = page.evaluate(FOCUS)
            r.check(
                f"from {start}, focus moves to the new centered talk's Open the deck, read once (no live text)",
                focus == ["open", True] and page.evaluate("window.__said") == 0,
                [focus, page.evaluate("window.__said")],
            )
        page.focus(".talk:not([aria-hidden]) .open")
        side = page.locator(".talk").nth(0).locator(".cover").bounding_box()
        assert side is not None
        page.mouse.click(side["x"] + side["width"] * 0.3, side["y"] + side["height"] / 2)
        page.wait_for_timeout(SETTLE_MS)
        r.check(
            "a click on a cover never leaves focus in hidden content",
            page.evaluate(FOCUS) == ["open", True],
            page.evaluate(FOCUS),
        )
        page.locator(".dots button").nth(2).click()
        page.wait_for_timeout(SETTLE_MS)
        r.check("nor does a click on a dot", page.evaluate(FOCUS) == ["open", True], page.evaluate(FOCUS))

        # A resize or zoom keeps the centered talk, the focus, the address and the silence.
        page.goto("about:blank")
        page.goto(url)
        page.wait_for_timeout(SETTLE_MS)
        page.focus(".talk:not([aria-hidden]) .open")
        page.evaluate(COUNT)
        before = page.evaluate(STATE)
        for w, h in ((1280, 800), (1024, 640), (640, 480), (1920, 1080), (1920, 700), (1920, 1080)):
            page.set_viewport_size({"width": w, "height": h})
            page.wait_for_timeout(700)
        after = page.evaluate(STATE)
        r.check(
            "resizing keeps the talk, focus, address and announces nothing",
            after["c"] == before["c"]
            and after["hash"] == before["hash"]
            and page.evaluate("window.__said") == 0
            and page.evaluate(FOCUS) == ["open", True],
            [before, after, page.evaluate("window.__said")],
        )

        r.check("axe, 1920, light", not (v := axe(page)), v)

        # A drag released exactly on the next talk scrolls nowhere afterwards, and must still settle there.
        # At 1250 px the slot is a whole 140 px, so the release can land exactly on the next talk.
        page.set_viewport_size({"width": 1250, "height": 1080})
        page.wait_for_timeout(700)
        before = page.evaluate(STATE)["c"]
        # The exact distance from here to the next talk's resting place, as the strip measures it.
        dx = page.evaluate(
            "(() => { const s = document.querySelector('.covers'), t = s.children[" + str(before + 1) + "];"
            " return t.offsetLeft + t.offsetWidth / 2 - s.clientWidth / 2 - s.scrollLeft; })()"
        )
        page.mouse.move(625, 400)
        page.mouse.down()
        for k in range(1, 11):
            page.mouse.move(625 - dx * k / 10, 400)
            page.wait_for_timeout(16)
        page.wait_for_timeout(400)
        page.mouse.up()
        page.wait_for_timeout(SETTLE_MS)
        s = page.evaluate(STATE)
        r.check(
            "a drag that ends exactly on a talk settles on it", s["c"] == before + 1 and s["inert"][s["c"]] is False, s
        )

        # A drag past the last talk scrolls nowhere on release; the next drag must still move the strip.
        page.set_viewport_size({"width": 1920, "height": 1080})
        page.wait_for_timeout(700)
        page.keyboard.press("End")
        page.wait_for_timeout(SETTLE_MS)

        def drag(dx: float) -> None:
            page.mouse.move(960, 400)
            page.mouse.down()
            for k in range(1, 11):
                page.mouse.move(960 + dx * k / 10, 400)
                page.wait_for_timeout(16)
            page.wait_for_timeout(300)  # a still release: no fling, so a drag past the end glides nowhere
            page.mouse.up()
            page.wait_for_timeout(SETTLE_MS)

        drag(-300)
        drag(260)
        r.check(
            "a drag after a drag past the end still glides",
            page.evaluate(STATE)["c"] <= s["n"] - 2,
            page.evaluate(STATE),
        )

        # The centered talk's actions stay on the first screen, for every talk: on a 1080p monitor's browser
        # (about 940 px), on short laptops and a landscape tablet, and Open the deck on a phone with its browser
        # toolbars collapsed (390x844; with them shown, it sits one short scroll down, as the PR says).
        names = page.evaluate("[...document.querySelectorAll('.talk')].map((t) => t.dataset.name)")
        for w, h, what in (
            (1920, 940, ".actions"),
            (1366, 768, ".actions"),
            (1280, 720, ".actions"),
            (1024, 768, ".actions"),
            (390, 844, ".open"),
        ):
            page.set_viewport_size({"width": w, "height": h})
            over = {}
            for name in names:
                page.goto("about:blank")
                page.goto(f"{url}#{name}")
                page.wait_for_timeout(900)
                bottom = page.evaluate(
                    f"document.querySelector('.talk:not([aria-hidden]) {what}').getBoundingClientRect().bottom"
                )
                if bottom > h - 8:
                    over[name] = round(bottom)
            r.check(
                f"{'the actions show' if what == '.actions' else 'Open the deck shows'} without scrolling at {w}x{h}, "
                "every talk",
                not over,
                over,
            )
        page.set_viewport_size({"width": 1920, "height": 1080})
        page.goto("about:blank")
        page.goto(url)
        page.wait_for_timeout(SETTLE_MS)
        borders = page.evaluate(CHIP_BORDER)
        r.check("each chip's border reaches 3:1 against the page (light)", min(borders) >= 3, borders)
        r.check("every focus ring stands out (3:1), light", all(c >= 3 for _, c in rings(page)), rings(page))

        page.goto("about:blank")
        page.goto(url)
        page.wait_for_timeout(SETTLE_MS)
        tabbed = []
        for _ in range(12):
            page.keyboard.press("Tab")
            tabbed.append(page.evaluate("document.activeElement.closest('[aria-hidden], [inert]') === null"))
        r.check("Tab never reaches a hidden talk", all(tabbed), tabbed)
        r.check("no script errors", not errors, errors)
        page.close()

        ctx = browser.new_context(viewport={"width": 1920, "height": 1080}, color_scheme="dark")
        dark = ctx.new_page()
        dark.goto(url)
        dark.wait_for_timeout(SETTLE_MS)
        r.check("axe, 1920, dark", not (v := axe(dark)), v)
        r.check("every focus ring stands out (3:1), dark", all(c >= 3 for _, c in rings(dark)), rings(dark))
        borders = dark.evaluate(CHIP_BORDER)
        r.check("each chip's border reaches 3:1 against the page (dark)", min(borders) >= 3, borders)
        ctx.close()

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

        ctx = browser.new_context(viewport={"width": 844, "height": 390}, is_mobile=True, has_touch=True)
        low = ctx.new_page()
        low_errors: list[str] = []
        low.on("pageerror", lambda e: low_errors.append(str(e)))
        low.goto(url)
        low.wait_for_timeout(SETTLE_MS)
        s = low.evaluate(STATE)
        width = low.evaluate("document.querySelector('.talk:not([aria-hidden]) .cover').getBoundingClientRect().width")
        r.check(
            "a landscape phone (844x390) shows a talk",
            width > 100 and s["shown"] == 1 and not low_errors,
            [width, s, low_errors],
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
    # A build without exports draws each talk's title on a blank cover: check it reads in both themes.
    with tempfile.TemporaryDirectory() as tmp:
        spec = importlib.util.spec_from_file_location("talks_site", pathlib.Path(__file__).with_name("site.py"))
        assert spec and spec.loader
        site = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(site)
        site.build(pathlib.Path(tmp) / "site")
        server, url = serve(pathlib.Path(tmp) / "site")
        try:
            with sync_playwright() as p:
                browser = p.chromium.launch()
                for scheme in ("light", "dark"):
                    page = browser.new_page(viewport={"width": 1920, "height": 1080}, color_scheme=scheme)
                    page.goto(url)
                    page.wait_for_timeout(SETTLE_MS)
                    report.check(f"axe, blank covers, {scheme}", not (v := axe(page)), v)
                    page.close()
                browser.close()
        finally:
            server.shutdown()
    if report.failed:
        print(f"{len(report.failed)} check(s) failed", file=sys.stderr)
        return 1
    print("the index page behaves")
    return 0


if __name__ == "__main__":
    sys.exit(main())
