"""Hilfen für die Playwright-Tests der PWA (iPhone-Größe, Zeit und Zeitzone Berlin)."""
import datetime as dt
import json
import os

BASE = os.environ.get('TB_BASE', 'http://127.0.0.1:8765/AppT/')
SHOTS = os.environ.get('TB_SHOTS', os.path.join(os.path.dirname(os.path.abspath(__file__)), 'shots'))
os.makedirs(SHOTS, exist_ok=True)
TZ = dt.timezone(dt.timedelta(hours=1))


def T(y, mo, d, h=8, mi=0):
    return dt.datetime(y, mo, d, h, mi, tzinfo=TZ)


def new_ctx(b, dark=False, scale=1):
    return b.new_context(viewport={'width': 390, 'height': 844}, device_scale_factor=scale, is_mobile=True,
                         has_touch=True, locale='de-DE', timezone_id='Europe/Berlin',
                         color_scheme='dark' if dark else 'light', service_workers='block')


def open_app(b, when, dark=False, scale=1, state=None, errors=None):
    """Öffnet die App zur Zeit `when`. state: fertiger Zustand (dict) für localStorage, sonst Beispieldaten."""
    c = new_ctx(b, dark, scale)
    p = c.new_page()
    errs = errors if errors is not None else []
    p.on('pageerror', lambda e: errs.append(str(e)))
    p.on('console', lambda m: errs.append('console: ' + m.text) if m.type == 'error' else None)
    p.clock.install(time=when)
    if state is not None:
        p.add_init_script('try{if(!sessionStorage.getItem("_seeded")){localStorage.setItem("trainingsbuch.v1",'
                          + json.dumps(json.dumps(state)) + ');sessionStorage.setItem("_seeded","1")}}catch(e){}')
    p.goto(BASE)
    p.wait_for_selector('#main')
    p.wait_for_timeout(300)
    p.errs = errs
    return p


def E(p, js):
    return p.evaluate('s=>window.__ev(s)', js)


def S(p):
    return E(p, 'JSON.parse(JSON.stringify(S))')


def act(p, sel, i=0):
    p.locator('#main ' + sel).nth(i).click()
    p.wait_for_timeout(120)


def shot(p, name, full=True):
    p.screenshot(path=f'{SHOTS}/{name}.png', full_page=full)


def main_text(p):
    return p.locator('#main').inner_text()
