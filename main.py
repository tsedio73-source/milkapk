"""
CD Milk - Kivy Android App
Powered by Tsedio 2026
Version 1.2.0
"""

import os
os.environ['KIVY_NO_ENV_CONFIG'] = '1'

import json
import threading
from datetime import datetime, date

from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen, SlideTransition
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.spinner import Spinner
from kivy.uix.popup import Popup
from kivy.uix.widget import Widget
from kivy.graphics import Color, RoundedRectangle, Rectangle
from kivy.clock import Clock
from kivy.metrics import dp, sp
from kivy.utils import get_color_from_hex
from kivy.storage.jsonstore import JsonStore

# ─── STORAGE ─────────────────────────────────────────────────────────────────
store = JsonStore('cdmilk_data.json')

def save(key, value):
    data = {}
    if store.exists('app'):
        data = dict(store.get('app'))
    data[key] = value
    store.put('app', **data)

def load(key, default=None):
    if store.exists('app'):
        return store.get('app').get(key, default)
    return default

# ─── API URLs ─────────────────────────────────────────────────────────────────
AUTH_URL  = 'https://script.google.com/macros/s/AKfycbydV7TyhFE0vIcLG1kgEctJBXK-mEqO3feNJ1GUNZnjW5tWftR5oxVm20VY1lmE_FpO5Q/exec'
MILK_URL  = 'https://script.google.com/macros/s/AKfycbyuQtjA1NXRxUm_-AIqgQlWG9Vtd5ZGUGZWl2Dzbr_lp-curuTAsWK3-ojBPhyMvHHHsg/exec'
READ_URL  = 'https://script.google.com/macros/s/AKfycby8EUcL7pVk0exlN3PUV_Q-EjZ8clo4HqfaQjUOZ-sK-7kEdJrq5JMFJnwX1BoKEaWHAw/exec'
INFO_URL  = 'https://script.google.com/macros/s/AKfycbwcca5zGgaYrLTWU2Yt2OI_62RrtB1JiF25OgKrMu9aHSLULL2yAxwibCOlGerBuH78JQ/exec'
ADMIN_URL = 'https://script.google.com/macros/s/AKfycbz7fMlrVjPyvMZMd2LjEI8Oq_APdYs6iGmFs7aCHGFeAYIpCvffutrB2tMumoUQDMT8/exec'

# ─── COLORS ───────────────────────────────────────────────────────────────────
C_BLUE   = get_color_from_hex('#1686FF')
C_GREEN  = get_color_from_hex('#50AD1C')
C_ORANGE = get_color_from_hex('#FF9E00')
C_RED    = get_color_from_hex('#E53935')
C_PURPLE = get_color_from_hex('#5F6BEF')
C_DARK   = get_color_from_hex('#1A1A2E')
C_WHITE  = (1, 1, 1, 1)
C_GREY   = get_color_from_hex('#888888')
C_BG     = get_color_from_hex('#F5F7FA')

# ─── HELPERS ──────────────────────────────────────────────────────────────────
def fetch_json(url):
    try:
        from urllib.request import urlopen, Request
        req  = Request(url, headers={'User-Agent': 'CDMilkApp/1.2'})
        resp = urlopen(req, timeout=12)
        return json.loads(resp.read().decode())
    except Exception as e:
        print('Fetch error:', e)
        return None

def post_json(url, data):
    try:
        from urllib.request import urlopen, Request
        body = json.dumps(data).encode()
        req  = Request(url, data=body, method='POST',
                       headers={'Content-Type': 'application/json',
                                'User-Agent': 'CDMilkApp/1.2'})
        urlopen(req, timeout=12)
        return True
    except Exception as e:
        print('Post error:', e)
        return False

def run_thread(fn, *args):
    t = threading.Thread(target=fn, args=args, daemon=True)
    t.start()

def show_toast(msg, color=None):
    color = color or C_GREEN
    content = BoxLayout(padding=dp(10))
    lbl = Label(text=msg, font_size=sp(14), color=C_WHITE,
                halign='center', valign='middle')
    lbl.bind(size=lbl.setter('text_size'))
    content.add_widget(lbl)
    with content.canvas.before:
        Color(*color)
        rrect = RoundedRectangle(pos=content.pos, size=content.size, radius=[dp(10)])
    content.bind(
        pos=lambda *a: setattr(rrect, 'pos', content.pos),
        size=lambda *a: setattr(rrect, 'size', content.size)
    )
    popup = Popup(content=content, size_hint=(0.75, None), height=dp(60),
                  pos_hint={'center_x': 0.5, 'top': 0.18},
                  title='', separator_height=0,
                  background_color=(0,0,0,0), overlay_color=(0,0,0,0))
    popup.open()
    Clock.schedule_once(lambda dt: popup.dismiss(), 2.5)

# ─── SIMPLE WIDGET HELPERS ────────────────────────────────────────────────────

def make_btn(text, bg=None, height=dp(50), font_size=sp(15)):
    bg = bg or C_BLUE
    return Button(text=text, font_size=font_size, bold=True, color=C_WHITE,
                  size_hint_y=None, height=height,
                  background_normal='', background_color=bg)

def make_input(hint='', password=False, input_filter=None):
    inp = TextInput(hint_text=hint, multiline=False, password=password,
                    size_hint_y=None, height=dp(48), font_size=sp(15),
                    background_color=(1,1,1,1), foreground_color=(0.1,0.1,0.1,1),
                    cursor_color=C_BLUE, padding=(dp(12), dp(12)))
    if input_filter:
        inp.input_filter = input_filter
    return inp

def make_lbl(text, size=sp(14), color=None, bold=False, height=dp(30), halign='left'):
    color = color or (0.2, 0.2, 0.2, 1)
    lbl = Label(text=text, font_size=size, color=color, bold=bold,
                size_hint_y=None, height=height, halign=halign, valign='middle')
    lbl.bind(size=lbl.setter('text_size'))
    return lbl

def make_topbar(title, back_fn, color=None):
    color = color or C_BLUE
    bar = BoxLayout(size_hint_y=None, height=dp(56), padding=(dp(6), dp(4)))
    with bar.canvas.before:
        Color(*color)
        bar._rect = Rectangle(pos=bar.pos, size=bar.size)
    bar.bind(pos=lambda *a: setattr(bar._rect, 'pos', bar.pos),
             size=lambda *a: setattr(bar._rect, 'size', bar.size))
    btn_back = Button(text='  ←', font_size=sp(20), bold=True, color=C_WHITE,
                      size_hint=(None, 1), width=dp(52),
                      background_normal='', background_color=(0,0,0,0))
    btn_back.bind(on_press=lambda *a: back_fn())
    lbl = Label(text=title, font_size=sp(17), bold=True, color=C_WHITE)
    bar.add_widget(btn_back)
    bar.add_widget(lbl)
    bar.add_widget(Widget(size_hint=(None,1), width=dp(52)))
    return bar


# ═══════════════════════════════════════════════════════════════════════════════
# SCREENS
# ═══════════════════════════════════════════════════════════════════════════════

class LoginScreen(Screen):
    def __init__(self, **kw):
        super().__init__(**kw)
        root = BoxLayout(orientation='vertical')

        # Header
        header = BoxLayout(size_hint_y=None, height=dp(180), orientation='vertical',
                           padding=dp(20), spacing=dp(6))
        with header.canvas.before:
            Color(*C_BLUE)
            header._rect = Rectangle(pos=header.pos, size=header.size)
        header.bind(pos=lambda *a: setattr(header._rect, 'pos', header.pos),
                    size=lambda *a: setattr(header._rect, 'size', header.size))
        header.add_widget(Widget())
        header.add_widget(make_lbl('CD Milk', size=sp(34), color=C_WHITE,
                                    bold=True, height=dp(52), halign='center'))
        header.add_widget(make_lbl('Powered by Tsedio', size=sp(13),
                                    color=(1,1,1,0.75), height=dp(26), halign='center'))
        header.add_widget(Widget())
        root.add_widget(header)

        # Form area
        form = BoxLayout(orientation='vertical', spacing=dp(12),
                         padding=(dp(28), dp(28), dp(28), dp(20)))
        with form.canvas.before:
            Color(*C_BG)
            form._rect = Rectangle(pos=form.pos, size=form.size)
        form.bind(pos=lambda *a: setattr(form._rect, 'pos', form.pos),
                  size=lambda *a: setattr(form._rect, 'size', form.size))

        form.add_widget(make_lbl('Naam', color=C_GREY, height=dp(22)))
        self.inp_name = make_input('Apna naam likhein')
        form.add_widget(self.inp_name)

        form.add_widget(make_lbl('Code', color=C_GREY, height=dp(22)))
        self.inp_code = make_input('Code likhein', input_filter='int')
        form.add_widget(self.inp_code)

        form.add_widget(Widget(size_hint_y=None, height=dp(8)))
        self.btn_login = make_btn('Login  →', bg=C_BLUE, height=dp(52))
        self.btn_login.bind(on_press=self.do_login)
        form.add_widget(self.btn_login)

        self.lbl_status = make_lbl('', color=C_GREY, height=dp(24), halign='center')
        form.add_widget(self.lbl_status)
        form.add_widget(Widget())
        root.add_widget(form)
        self.add_widget(root)

    def on_enter(self):
        if load('login') == 'logged':
            pin = load('pin', '')
            if pin:
                Clock.schedule_once(lambda dt: self._ask_pin(), 0.2)
            else:
                Clock.schedule_once(lambda dt: App.get_running_app().go('home'), 0.1)

    def _ask_pin(self):
        content = BoxLayout(orientation='vertical', spacing=dp(12), padding=dp(16))
        lbl = make_lbl('PIN enter karo', bold=True, height=dp(30), halign='center')
        inp = make_input('PIN', password=True, input_filter='int')
        btn = make_btn('Unlock', bg=C_BLUE, height=dp(46))
        popup = Popup(title='Locked', content=content,
                      size_hint=(0.82, None), height=dp(220))
        def check(*a):
            if inp.text.strip() == load('pin', ''):
                popup.dismiss()
                App.get_running_app().go('home')
            else:
                lbl.text  = 'Wrong PIN!'
                lbl.color = C_RED
        btn.bind(on_press=check)
        content.add_widget(lbl)
        content.add_widget(inp)
        content.add_widget(btn)
        popup.open()

    def do_login(self, *a):
        name = self.inp_name.text.strip()
        code = self.inp_code.text.strip()
        if not name or not code:
            show_toast('Naam aur Code zaroori hai!', C_RED)
            return
        self.btn_login.text     = 'Connecting...'
        self.btn_login.disabled = True
        self.lbl_status.text    = 'Please wait...'

        def _post():
            post_json(AUTH_URL, {'name': name, 'code': code, 'action': 'login'})
            def _done(dt):
                save('username', name)
                save('code', code)
                save('login', 'logged')
                self.btn_login.text     = 'Login  →'
                self.btn_login.disabled = False
                self.lbl_status.text    = ''
                App.get_running_app().go('home')
                show_toast(f'Welcome {name}!', C_GREEN)
            Clock.schedule_once(_done, 0)
        run_thread(_post)


# ─────────────────────────────────────────────────────────────────────────────

class HomeScreen(Screen):
    def __init__(self, **kw):
        super().__init__(**kw)
        root = BoxLayout(orientation='vertical', spacing=0)

        # Blue header
        header = BoxLayout(size_hint_y=None, height=dp(110),
                           orientation='vertical', padding=(dp(16), dp(10)))
        with header.canvas.before:
            Color(*C_BLUE)
            header._rect = Rectangle(pos=header.pos, size=header.size)
        header.bind(pos=lambda *a: setattr(header._rect, 'pos', header.pos),
                    size=lambda *a: setattr(header._rect, 'size', header.size))
        self.lbl_user = make_lbl('...', size=sp(13), color=(1,1,1,0.8),
                                  height=dp(22), halign='center')
        lbl_title = make_lbl('CD Milk', size=sp(28), color=C_WHITE,
                              bold=True, height=dp(46), halign='center')
        header.add_widget(self.lbl_user)
        header.add_widget(lbl_title)
        root.add_widget(header)

        # Stats row
        stats = BoxLayout(size_hint_y=None, height=dp(70))
        with stats.canvas.before:
            Color(0.95, 0.97, 1, 1)
            stats._rect = Rectangle(pos=stats.pos, size=stats.size)
        stats.bind(pos=lambda *a: setattr(stats._rect, 'pos', stats.pos),
                   size=lambda *a: setattr(stats._rect, 'size', stats.size))

        left = BoxLayout(orientation='vertical', padding=(dp(10), dp(4)))
        self.lbl_count = make_lbl('--', size=sp(22), bold=True,
                                   color=C_BLUE, height=dp(30), halign='center')
        left.add_widget(self.lbl_count)
        left.add_widget(make_lbl('Records', size=sp(11), color=C_GREY,
                                  height=dp(18), halign='center'))

        right = BoxLayout(orientation='vertical', padding=(dp(10), dp(4)))
        self.lbl_amt = make_lbl('Rs.--', size=sp(22), bold=True,
                                 color=C_GREEN, height=dp(30), halign='center')
        right.add_widget(self.lbl_amt)
        right.add_widget(make_lbl('Amount', size=sp(11), color=C_GREY,
                                   height=dp(18), halign='center'))

        stats.add_widget(left)
        stats.add_widget(right)
        root.add_widget(stats)

        # Buttons
        scroll = ScrollView()
        box = BoxLayout(orientation='vertical', spacing=dp(12),
                        padding=(dp(16), dp(14)), size_hint_y=None)
        box.bind(minimum_height=box.setter('height'))

        buttons = [
            ('New Milk Entry',   'milk',    C_GREEN),
            ('View Records',     'records', C_PURPLE),
            ('New Receipt',      'receipt', C_DARK),
            ('Info Dashboard',   'info',    (0.05, 0.6, 0.9, 1)),
            ('Admin Settings',   'admin',   (0.55, 0.35, 0.0, 1)),
        ]
        for (text, screen, color) in buttons:
            btn = make_btn(text, bg=color, height=dp(56), font_size=sp(16))
            btn.bind(on_press=lambda inst, s=screen: App.get_running_app().go(s))
            box.add_widget(btn)

        box.add_widget(Widget(size_hint_y=None, height=dp(10)))
        box.add_widget(make_lbl('Powered by Tsedio 2026  |  v1.2.0',
                                 size=sp(11), color=C_GREY, height=dp(24), halign='center'))
        scroll.add_widget(box)
        root.add_widget(scroll)
        self.add_widget(root)

    def on_enter(self):
        name = load('username', 'User')
        self.lbl_user.text = f'Namaste, {name}'
        run_thread(self._load_stats)

    def _load_stats(self):
        code      = load('code', '')
        from_date = load('fromDate', '')
        to_date   = load('toDate', '')
        eamt      = float(load('AMT', 0) or 0)
        data      = fetch_json(f'{INFO_URL}?action=read&code={code}')
        if not data:
            return
        count, amt = 0, eamt
        for r in data:
            raw = str(r.get('entryid', r.get('date', ''))).strip()[:10]
            if from_date and to_date and from_date <= raw <= to_date:
                count += 1
                amt   += float(r.get('totalamount', 0) or 0)
        def _upd(dt):
            self.lbl_count.text = str(count)
            self.lbl_amt.text   = f'Rs.{amt:.2f}'
        Clock.schedule_once(_upd, 0)


# ─────────────────────────────────────────────────────────────────────────────

class MilkEntryScreen(Screen):
    def __init__(self, **kw):
        super().__init__(**kw)
        root = BoxLayout(orientation='vertical')
        root.add_widget(make_topbar('Milk Entry',
                                     lambda: App.get_running_app().go('home'), C_GREEN))

        scroll = ScrollView()
        form = BoxLayout(orientation='vertical', spacing=dp(8),
                         padding=(dp(18), dp(12)), size_hint_y=None)
        form.bind(minimum_height=form.setter('height'))

        today = date.today().isoformat()
        self.inp_date   = make_input(f'Date YYYY-MM-DD')
        self.inp_date.text = today
        self.inp_type   = Spinner(values=['Buffalo', 'Cow', 'Mix'], text='Buffalo',
                                   size_hint_y=None, height=dp(48), font_size=sp(15))
        self.inp_weight = make_input('Weight (Ltr)', input_filter='float')
        self.inp_water  = make_input('Water %', input_filter='float')
        self.inp_water.text = '0'
        self.inp_fat    = make_input('FAT', input_filter='float')
        self.inp_snf    = make_input('SNF', input_filter='float')
        self.inp_rate   = make_input('Rate (Rs)', input_filter='float')

        fields = [
            ('Date',         self.inp_date),
            ('Type',         self.inp_type),
            ('Weight (Ltr)', self.inp_weight),
            ('Water %',      self.inp_water),
            ('FAT',          self.inp_fat),
            ('SNF',          self.inp_snf),
            ('Rate (Rs)',    self.inp_rate),
        ]
        for (label, widget) in fields:
            form.add_widget(make_lbl(label, color=C_GREY, height=dp(22)))
            form.add_widget(widget)

        form.add_widget(Widget(size_hint_y=None, height=dp(10)))
        self.btn_save = make_btn('Save Entry', bg=C_GREEN, height=dp(54))
        self.btn_save.bind(on_press=self.save)
        form.add_widget(self.btn_save)
        form.add_widget(Widget(size_hint_y=None, height=dp(30)))

        scroll.add_widget(form)
        root.add_widget(scroll)
        self.add_widget(root)

    def save(self, *a):
        weight = self.inp_weight.text.strip()
        rate   = self.inp_rate.text.strip()
        if not weight or not rate:
            show_toast('Weight aur Rate zaroori hai!', C_RED)
            return

        date_val = self.inp_date.text.strip() or date.today().isoformat()
        parts    = date_val.split('-')
        display  = f'{parts[2]}/{parts[1]}/{parts[0][-2:]}' if len(parts) == 3 else date_val

        milk_data = {
            'name':      load('username', 'Guest'),
            'code':      load('code', 'N/A'),
            'date':      display,
            'timestamp': date_val,
            'type':      self.inp_type.text,
            'weight':    weight,
            'water':     self.inp_water.text or '0',
            'fat':       self.inp_fat.text or '0',
            'snf':       self.inp_snf.text or '0',
            'rate':      rate,
        }

        self.btn_save.text     = 'Saving...'
        self.btn_save.disabled = True

        def _post():
            ok = post_json(MILK_URL, milk_data)
            def _done(dt):
                self.btn_save.disabled = False
                self.btn_save.text     = 'Save Entry'
                if ok:
                    show_toast('Entry saved!', C_GREEN)
                    self.inp_weight.text = ''
                    self.inp_fat.text    = ''
                    self.inp_snf.text    = ''
                    self.inp_rate.text   = ''
                else:
                    show_toast('Network Error!', C_RED)
            Clock.schedule_once(_done, 0)
        run_thread(_post)


# ─────────────────────────────────────────────────────────────────────────────

class RecordsScreen(Screen):
    def __init__(self, **kw):
        super().__init__(**kw)
        self._records = []
        root = BoxLayout(orientation='vertical')
        root.add_widget(make_topbar('Live Records',
                                     lambda: App.get_running_app().go('home'), C_PURPLE))

        btn_row = BoxLayout(size_hint_y=None, height=dp(48), padding=(dp(12), dp(4)))
        btn_copy = make_btn('Copy Report', bg=C_PURPLE, height=dp(40))
        btn_copy.bind(on_press=self.copy_report)
        btn_row.add_widget(btn_copy)
        root.add_widget(btn_row)

        self.scroll_box = BoxLayout(orientation='vertical', spacing=dp(10),
                                     padding=(dp(12), dp(6)), size_hint_y=None)
        self.scroll_box.bind(minimum_height=self.scroll_box.setter('height'))
        self.lbl_loading = make_lbl('Loading...', size=sp(16), color=C_GREY,
                                     height=dp(60), halign='center')
        self.scroll_box.add_widget(self.lbl_loading)

        sv = ScrollView()
        sv.add_widget(self.scroll_box)
        root.add_widget(sv)

        # Bottom
        bottom = BoxLayout(size_hint_y=None, height=dp(64), spacing=dp(20),
                           padding=(dp(16), dp(8)))
        with bottom.canvas.before:
            Color(*C_DARK)
            bottom._rect = Rectangle(pos=bottom.pos, size=bottom.size)
        bottom.bind(pos=lambda *a: setattr(bottom._rect, 'pos', bottom.pos),
                    size=lambda *a: setattr(bottom._rect, 'size', bottom.size))
        self.lbl_tw = make_lbl('Weight\n--', size=sp(13), bold=True,
                                color=get_color_from_hex('#4ade80'),
                                height=dp(48), halign='center')
        self.lbl_ta = make_lbl('Amount\nRs.--', size=sp(13), bold=True,
                                color=get_color_from_hex('#4ade80'),
                                height=dp(48), halign='center')
        bottom.add_widget(self.lbl_tw)
        bottom.add_widget(self.lbl_ta)
        root.add_widget(bottom)
        self.add_widget(root)

    def on_enter(self):
        self.scroll_box.clear_widgets()
        self.scroll_box.add_widget(self.lbl_loading)
        run_thread(self._load)

    def _load(self):
        name = load('username', '')
        code = load('code', '')
        data = fetch_json(f'{READ_URL}?name={name}&code={code}')

        def _render(dt):
            self.scroll_box.clear_widgets()
            if not data:
                self.scroll_box.add_widget(
                    make_lbl('Error loading data', color=C_RED,
                              height=dp(60), halign='center'))
                return

            records     = list(reversed(data))
            self._records = records
            total_w = total_a = 0

            for r in records:
                w   = float(r.get('weight', 0) or 0)
                amt = float(r.get('totalamount', 0) or 0)
                total_w += w
                total_a += amt

                card = BoxLayout(orientation='vertical', spacing=dp(2),
                                  size_hint_y=None, height=dp(162),
                                  padding=(dp(14), dp(8)))
                with card.canvas.before:
                    Color(1, 1, 1, 1)
                    rrect = RoundedRectangle(pos=card.pos, size=card.size, radius=[dp(12)])
                card.bind(pos=lambda *a, c=card, r=rrect: setattr(r, 'pos', c.pos),
                          size=lambda *a, c=card, r=rrect: setattr(r, 'size', c.size))

                def row(k, v, vc=None):
                    b = BoxLayout(size_hint_y=None, height=dp(22))
                    b.add_widget(make_lbl(k, size=sp(12), color=C_GREY, height=dp(22)))
                    b.add_widget(make_lbl(str(v), size=sp(12), bold=True,
                                           color=vc or (0.1,0.1,0.1,1),
                                           height=dp(22), halign='right'))
                    return b

                card.add_widget(row('Date',    r.get('date', 'N/A')))
                card.add_widget(row('Type',    r.get('type', 'N/A')))
                card.add_widget(row('Weight',  f'{w:.2f} kg'))
                card.add_widget(row('Water',   f"{r.get('water',0)}%"))
                card.add_widget(row('FAT/SNF', f"{r.get('fat','?')}/{r.get('snf','?')}"))
                card.add_widget(row('Rate',    f"Rs.{r.get('rate','?')}"))
                card.add_widget(row('Amount',  f'Rs.{amt:.2f}', C_PURPLE))
                self.scroll_box.add_widget(card)

            self.lbl_tw.text = f'Weight\n{total_w:.2f} kg'
            self.lbl_ta.text = f'Amount\nRs.{total_a:.2f}'

        Clock.schedule_once(_render, 0)

    def copy_report(self, *a):
        lines = ['MILK REPORT', '=' * 28]
        for r in self._records:
            lines.append(
                f"Date:{r.get('date')} | {r.get('type')} | "
                f"Wt:{r.get('weight')}kg | Rs.{r.get('totalamount')}"
            )
        try:
            from kivy.core.clipboard import Clipboard
            Clipboard.copy('\n'.join(lines))
            show_toast('Report copied!', C_BLUE)
        except Exception:
            show_toast('Copy supported nahi', C_RED)


# ─────────────────────────────────────────────────────────────────────────────

class InfoScreen(Screen):
    def __init__(self, **kw):
        super().__init__(**kw)
        root = BoxLayout(orientation='vertical')
        root.add_widget(make_topbar('Info Dashboard',
                                     lambda: App.get_running_app().go('home'),
                                     (0.05, 0.6, 0.9, 1)))

        scroll = ScrollView()
        box = BoxLayout(orientation='vertical', spacing=dp(12),
                        padding=(dp(16), dp(14)), size_hint_y=None)
        box.bind(minimum_height=box.setter('height'))

        self.lbl_date = make_lbl('Date filter loading...', color=C_GREY,
                                  height=dp(28), halign='center')
        box.add_widget(self.lbl_date)

        grid = GridLayout(cols=2, spacing=dp(10), size_hint_y=None, height=dp(270))
        stats_info = [
            ('avl_amt',  'Avl Amount',      C_ORANGE),
            ('avl_wt',   'Supply (Period)', C_GREEN),
            ('new_rec',  'New Receipts',    C_GREEN),
            ('earn',     'Total Earning',   C_ORANGE),
            ('total_wt', 'Total Supply',    C_ORANGE),
            ('all_rec',  'All Receipts',    C_ORANGE),
        ]
        self.stat_labels = {}
        for (key, name, color) in stats_info:
            cell = BoxLayout(orientation='vertical', padding=(dp(6), dp(8)), spacing=dp(4))
            with cell.canvas.before:
                Color(*color[:3], 0.12)
                rrect = RoundedRectangle(pos=cell.pos, size=cell.size, radius=[dp(10)])
            cell.bind(pos=lambda *a, c=cell, r=rrect: setattr(r, 'pos', c.pos),
                      size=lambda *a, c=cell, r=rrect: setattr(r, 'size', c.size))
            lv = make_lbl('...', size=sp(17), bold=True, color=color,
                           height=dp(32), halign='center')
            ln = make_lbl(name, size=sp(11), color=C_GREY,
                           height=dp(18), halign='center')
            cell.add_widget(lv)
            cell.add_widget(ln)
            self.stat_labels[key] = lv
            grid.add_widget(cell)

        box.add_widget(grid)
        btn_ref = make_btn('Refresh', bg=(0.05, 0.6, 0.9, 1), height=dp(48))
        btn_ref.bind(on_press=lambda *a: run_thread(self._load))
        box.add_widget(btn_ref)
        box.add_widget(Widget(size_hint_y=None, height=dp(20)))

        scroll.add_widget(box)
        root.add_widget(scroll)
        self.add_widget(root)

    def on_enter(self):
        run_thread(self._load)

    def _load(self):
        code      = load('code', '')
        from_date = load('fromDate', '')
        to_date   = load('toDate', '')

        def _upd_date(dt):
            self.lbl_date.text = (f'{from_date}  to  {to_date}'
                                  if from_date and to_date
                                  else 'Admin mein date set karo')
        Clock.schedule_once(_upd_date, 0)

        data = fetch_json(f'{INFO_URL}?action=read&code={code}')
        if not data:
            return

        fw = fa = fw2 = fa2 = fc = 0
        for r in data:
            w   = float(r.get('weight', 0) or 0)
            amt = float(r.get('totalamount', 0) or 0)
            fw  += w
            fa  += amt
            raw  = str(r.get('entryid', r.get('date', ''))).strip()[:10]
            if from_date and to_date and from_date <= raw <= to_date:
                fw2 += w
                fa2 += amt
                fc  += 1

        def _render(dt):
            self.stat_labels['avl_amt'].text  = f'Rs.{fa2:.2f}'
            self.stat_labels['avl_wt'].text   = f'{fw2:.2f}kg'
            self.stat_labels['new_rec'].text  = str(fc)
            self.stat_labels['earn'].text     = f'Rs.{fa:.2f}'
            self.stat_labels['total_wt'].text = f'{fw:.2f}kg'
            self.stat_labels['all_rec'].text  = str(len(data))
        Clock.schedule_once(_render, 0)


# ─────────────────────────────────────────────────────────────────────────────

class AdminScreen(Screen):
    def __init__(self, **kw):
        super().__init__(**kw)
        self._records = []
        root = BoxLayout(orientation='vertical')
        root.add_widget(make_topbar('Admin Settings',
                                     lambda: App.get_running_app().go('home'),
                                     (0.24, 0.56, 0.24, 1)))

        scroll = ScrollView()
        box = BoxLayout(orientation='vertical', spacing=dp(12),
                        padding=(dp(14), dp(12)), size_hint_y=None)
        box.bind(minimum_height=box.setter('height'))

        # Date Filter
        box.add_widget(make_lbl('Date Filter', size=sp(15), bold=True,
                                 color=(0.24,0.56,0.24,1), height=dp(30)))
        today = date.today().isoformat()
        self.inp_from = make_input('From Date (YYYY-MM-DD)')
        self.inp_from.text = load('fromDate', today)
        self.inp_till = make_input('To Date (YYYY-MM-DD)')
        self.inp_till.text = load('toDate', today)
        box.add_widget(self.inp_from)
        box.add_widget(self.inp_till)
        btn_date = make_btn('Save Date Filter', bg=C_GREEN, height=dp(46))
        btn_date.bind(on_press=self.save_date)
        box.add_widget(btn_date)

        box.add_widget(Widget(size_hint_y=None, height=dp(8)))

        # PIN
        box.add_widget(make_lbl('Set PIN', size=sp(15), bold=True,
                                 color=(0.24,0.56,0.24,1), height=dp(30)))
        self.inp_pin  = make_input('New PIN', password=True, input_filter='int')
        self.inp_pinc = make_input('Confirm PIN', password=True, input_filter='int')
        box.add_widget(self.inp_pin)
        box.add_widget(self.inp_pinc)
        row_pin = BoxLayout(spacing=dp(10), size_hint_y=None, height=dp(46))
        b_del = make_btn('Delete PIN', bg=C_RED, height=dp(46))
        b_sav = make_btn('Save PIN', bg=C_GREEN, height=dp(46))
        b_del.bind(on_press=self.del_pin)
        b_sav.bind(on_press=self.save_pin)
        row_pin.add_widget(b_del)
        row_pin.add_widget(b_sav)
        box.add_widget(row_pin)

        box.add_widget(Widget(size_hint_y=None, height=dp(8)))

        # Amount
        box.add_widget(make_lbl('Adjust Amount', size=sp(15), bold=True,
                                 color=(0.24,0.56,0.24,1), height=dp(30)))
        self.inp_amt = make_input('e.g. 100 ya -50', input_filter='float')
        self.inp_amt.text = load('AMT', '') or ''
        box.add_widget(self.inp_amt)
        btn_amt = make_btn('Submit Amount', bg=C_ORANGE, height=dp(46))
        btn_amt.bind(on_press=self.set_amt)
        box.add_widget(btn_amt)

        box.add_widget(Widget(size_hint_y=None, height=dp(8)))

        # Data Explorer
        box.add_widget(make_lbl('Data Explorer', size=sp(15), bold=True,
                                 color=(0.24,0.56,0.24,1), height=dp(30)))
        btn_load = make_btn('Load Live Data', bg=(0.12,0.54,0.9,1), height=dp(46))
        btn_load.bind(on_press=lambda *a: run_thread(self._fetch_data))
        box.add_widget(btn_load)

        self.data_box = BoxLayout(orientation='vertical', spacing=dp(6),
                                   size_hint_y=None)
        self.data_box.bind(minimum_height=self.data_box.setter('height'))
        self.lbl_data = make_lbl("Load button dabao", color=C_GREY,
                                  height=dp(36), halign='center')
        self.data_box.add_widget(self.lbl_data)
        box.add_widget(self.data_box)

        box.add_widget(Widget(size_hint_y=None, height=dp(8)))
        btn_logout = make_btn('Logout', bg=C_RED, height=dp(50))
        btn_logout.bind(on_press=self.logout)
        box.add_widget(btn_logout)
        box.add_widget(Widget(size_hint_y=None, height=dp(30)))

        scroll.add_widget(box)
        root.add_widget(scroll)
        self.add_widget(root)

    def save_date(self, *a):
        f = self.inp_from.text.strip()
        t = self.inp_till.text.strip()
        if not f or not t:
            show_toast('Dono dates daalo!', C_RED); return
        save('fromDate', f)
        save('toDate', t)
        show_toast(f'Filter: {f} to {t}', C_GREEN)

    def del_pin(self, *a):
        save('pin', '')
        show_toast('PIN deleted!', C_BLUE)

    def save_pin(self, *a):
        p  = self.inp_pin.text.strip()
        pc = self.inp_pinc.text.strip()
        if not p:
            show_toast('PIN empty hai!', C_RED); return
        if p != pc:
            show_toast('PINs match nahi karte!', C_RED); return
        save('pin', p)
        self.inp_pin.text  = ''
        self.inp_pinc.text = ''
        show_toast('PIN saved!', C_GREEN)

    def set_amt(self, *a):
        amt = self.inp_amt.text.strip()
        if not amt:
            show_toast('Amount daalo!', C_RED); return
        save('AMT', amt)
        v = float(amt)
        if v > 0:   show_toast(f'Rs.{amt} added!', C_GREEN)
        elif v < 0: show_toast(f'Rs.{abs(v):.0f} subtracted!', C_BLUE)
        else:       show_toast('Amount = 0', C_BLUE)

    def _fetch_data(self):
        code = load('code', '')
        data = fetch_json(f'{ADMIN_URL}?action=read&code={code}')

        def _render(dt):
            self.data_box.clear_widgets()
            if not data:
                self.lbl_data.text = 'Data load failed'
                self.data_box.add_widget(self.lbl_data)
                return
            self.lbl_data.text = f'{len(data)} records loaded'
            self.data_box.add_widget(self.lbl_data)
            self._records = list(reversed(data))
            for r in self._records:
                row = BoxLayout(size_hint_y=None, height=dp(40),
                                spacing=dp(4), padding=(dp(6), dp(4)))
                with row.canvas.before:
                    Color(0.96, 1, 0.96, 1)
                    rrect = RoundedRectangle(pos=row.pos, size=row.size, radius=[dp(6)])
                row.bind(pos=lambda *a, rw=row, rr=rrect: setattr(rr, 'pos', rw.pos),
                         size=lambda *a, rw=row, rr=rrect: setattr(rr, 'size', rw.size))
                row.add_widget(make_lbl(str(r.get('rownum','?')),
                                         size=sp(11), color=C_GREY, height=dp(32)))
                row.add_widget(make_lbl(str(r.get('date', r.get('entryid','?')))[:10],
                                         size=sp(11), color=(0.2,0.2,0.2,1), height=dp(32)))
                row.add_widget(make_lbl(f"Rs.{float(r.get('totalamount',0)):.0f}",
                                         size=sp(12), bold=True, color=C_GREEN, height=dp(32)))
                rn = r.get('rownum')
                bd = Button(text='X', font_size=sp(13), bold=True, color=C_WHITE,
                            size_hint=(None, 1), width=dp(36),
                            background_normal='', background_color=C_RED)
                bd.bind(on_press=lambda inst, n=rn: run_thread(self._delete, n))
                row.add_widget(bd)
                self.data_box.add_widget(row)

        Clock.schedule_once(_render, 0)

    def _delete(self, rownum):
        code = load('code', '')
        try:
            from urllib.request import urlopen, Request
            url = f'{ADMIN_URL}?action=delete&code={code}&row={rownum}'
            req = Request(url, headers={'User-Agent': 'CDMilkApp/1.2'})
            urlopen(req, timeout=10)
            def _done(dt):
                show_toast(f'Row {rownum} deleted!', C_GREEN)
                run_thread(self._fetch_data)
            Clock.schedule_once(_done, 0)
        except Exception:
            Clock.schedule_once(lambda dt: show_toast('Delete failed!', C_RED), 0)

    def logout(self, *a):
        save('login', '')
        save('username', '')
        save('code', '')
        App.get_running_app().go('login')
        show_toast('Logged out!', C_BLUE)


# ─────────────────────────────────────────────────────────────────────────────

class ReceiptScreen(Screen):
    def __init__(self, **kw):
        super().__init__(**kw)
        self._receipt_text = ''
        root = BoxLayout(orientation='vertical')
        root.add_widget(make_topbar('New Receipt',
                                     lambda: App.get_running_app().go('home'), C_DARK))

        scroll = ScrollView()
        box = BoxLayout(orientation='vertical', spacing=dp(14),
                        padding=(dp(16), dp(16)), size_hint_y=None)
        box.bind(minimum_height=box.setter('height'))

        card = BoxLayout(orientation='vertical', padding=dp(18),
                         size_hint_y=None, height=dp(320))
        with card.canvas.before:
            Color(1, 1, 1, 1)
            rrect = RoundedRectangle(pos=card.pos, size=card.size, radius=[dp(14)])
        card.bind(pos=lambda *a: setattr(rrect, 'pos', card.pos),
                  size=lambda *a: setattr(rrect, 'size', card.size))

        self.lbl_receipt = Label(
            text='Loading...',
            font_size=sp(13),
            color=(0.1, 0.1, 0.1, 1),
            halign='center',
            valign='top',
        )
        self.lbl_receipt.bind(size=self.lbl_receipt.setter('text_size'))
        card.add_widget(self.lbl_receipt)
        box.add_widget(card)

        btn_copy = make_btn('Copy Receipt', bg=C_PURPLE, height=dp(50))
        btn_copy.bind(on_press=self._copy)
        box.add_widget(btn_copy)
        box.add_widget(Widget(size_hint_y=None, height=dp(30)))

        scroll.add_widget(box)
        root.add_widget(scroll)
        self.add_widget(root)

    def on_enter(self):
        self.lbl_receipt.text = 'Loading receipt...'
        run_thread(self._load)

    def _load(self):
        code      = load('code', '')
        name      = load('username', '')
        from_date = load('fromDate', '')
        to_date   = load('toDate', '')
        data      = fetch_json(f'{INFO_URL}?action=read&code={code}')

        if not data:
            Clock.schedule_once(
                lambda dt: setattr(self.lbl_receipt, 'text', 'Could not load'), 0)
            return

        tw = ta = count = 0
        for r in data:
            w   = float(r.get('weight', 0) or 0)
            amt = float(r.get('totalamount', 0) or 0)
            raw = str(r.get('entryid', r.get('date', ''))).strip()[:10]
            if from_date and to_date and from_date <= raw <= to_date:
                tw    += w
                ta    += amt
                count += 1

        self._receipt_text = (
            f"======================\n"
            f"    CD MILK RECEIPT\n"
            f"======================\n"
            f"Name   : {name}\n"
            f"Code   : {code}\n"
            f"From   : {from_date}\n"
            f"To     : {to_date}\n"
            f"----------------------\n"
            f"Entries: {count}\n"
            f"Weight : {tw:.2f} kg\n"
            f"Amount : Rs.{ta:.2f}\n"
            f"======================\n"
            f"  Powered by Tsedio\n"
        )
        Clock.schedule_once(
            lambda dt: setattr(self.lbl_receipt, 'text', self._receipt_text), 0)

    def _copy(self, *a):
        try:
            from kivy.core.clipboard import Clipboard
            Clipboard.copy(self._receipt_text)
            show_toast('Receipt copied!', C_GREEN)
        except Exception:
            show_toast('Copy supported nahi', C_RED)


# ═══════════════════════════════════════════════════════════════════════════════
# MAIN
# ═══════════════════════════════════════════════════════════════════════════════

class CDMilkApp(App):
    def build(self):
        self.title = 'CD Milk'
        sm = ScreenManager(transition=SlideTransition())
        sm.add_widget(LoginScreen(name='login'))
        sm.add_widget(HomeScreen(name='home'))
        sm.add_widget(MilkEntryScreen(name='milk'))
        sm.add_widget(RecordsScreen(name='records'))
        sm.add_widget(InfoScreen(name='info'))
        sm.add_widget(AdminScreen(name='admin'))
        sm.add_widget(ReceiptScreen(name='receipt'))
        self.sm = sm
        return sm

    def go(self, screen):
        self.sm.transition.direction = 'left'
        self.sm.current = screen

    def go_back(self):
        self.sm.transition.direction = 'right'
        self.sm.current = 'home'


if __name__ == '__main__':
    CDMilkApp().run()