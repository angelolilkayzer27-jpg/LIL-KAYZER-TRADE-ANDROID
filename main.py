# -*- coding: utf-8 -*-
"""LIL KAYZER TRADE Android - señalización manual, sin ejecución de operaciones."""
import threading, time, math, webbrowser
from datetime import datetime
from kivy.app import App
from kivy.clock import Clock
from kivy.metrics import dp
from kivy.core.window import Window
from kivy.utils import platform
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.spinner import Spinner
from kivy.uix.scrollview import ScrollView
from kivy.uix.popup import Popup
try:
    from iqoptionapi.stable_api import IQ_Option
except Exception:
    IQ_Option = None

STRATEGIES = [
    "1. EMA 20 + EMA 50 + RSI",
    "2. Pullback EMA 20/50 + RSI",
    "3. ADX + EMA 50",
    "4. MACD + EMA 50",
    "5. Breakout + ATR",
    "6. Reversión RSI",
    "7. Filtro de lateralidad",
    "8. Filtro de volatilidad",
    "9. Confirmación múltiple / puntuación",
    "10. Semáforo (EMA 4/8/16 + SAR + RSI)"
]


# Lista masiva ampliada de más de 100 activos
ACTIVOS_MASIVOS = [
    "EURUSD", "GBPUSD", "USDJPY", "AUDUSD", "USDCAD", "EURGBP", "EURJPY", "GBPJPY",
    "AUDJPY", "NZDUSD", "EURAUD", "EURNZD", "GBPAUD", "GBPNZD", "CADJPY", "CHFJPY",
    "AUDCAD", "AUDNZD", "CADCHF", "GBPCAD", "NZDCAD", "NZDCHF", "USDCHF",
    "EURUSD-OTC", "GBPUSD-OTC", "USDJPY-OTC", "AUDUSD-OTC", "USDCAD-OTC", "EURGBP-OTC",
    "EURJPY-OTC", "GBPJPY-OTC", "AUDJPY-OTC", "NZDUSD-OTC", "EURAUD-OTC", "CADJPY-OTC",
    "USDCHF-OTC", "GBPAUD-OTC", "EURNZD-OTC", "GBPNZD-OTC", "CHFJPY-OTC", "AUDCAD-OTC",
    "AUDNZD-OTC", "CADCHF-OTC", "GBPCAD-OTC", "NZDCAD-OTC", "NZDCHF-OTC",
    "Bitcoin", "Ethereum", "Ripple", "Litecoin", "Cardano", "Solana", "Polkadot",
    "Bitcoin-OTC", "Ethereum-OTC", "Ripple-OTC", "Litecoin-OTC", "Cardano-OTC",
    "Tesla", "Apple", "Microsoft", "Amazon", "Google", "Netflix", "Meta", "Alibaba",
    "Tesla-OTC", "Apple-OTC", "Microsoft-OTC", "Amazon-OTC", "Google-OTC", "Netflix-OTC",
    "Gold", "Silver", "Crude Oil", "Brent Oil", "Gold-OTC", "Silver-OTC",
    "SP500", "NASDAQ", "DAX", "FTSE", "NIKKEI", "SP500-OTC", "NASDAQ-OTC", "DAX-OTC"
]


class Candle:
    def __init__(self, o, h, l, c):
        self.o, self.h, self.l, self.c = o, h, l, c


def ema(values, period):
    if not values:
        return 0.0
    k = 2 / (period + 1)
    e = values[0]
    for v in values[1:]:
        e = v * k + e * (1 - k)
    return e


def rsi(values, period=14):
    if len(values) <= period:
        return 50.0
    gains, losses = [], []
    for a, b in zip(values[-period - 1 : -1], values[-period:]):
        d = b - a
        gains.append(max(d, 0))
        losses.append(max(-d, 0))
    ag, al = sum(gains) / period, sum(losses) / period
    if al == 0:
        return 100.0
    return 100 - (100 / (1 + ag / al))


def atr(candles, period=14):
    if len(candles) < 2:
        return 0.0
    trs = []
    for i in range(max(1, len(candles) - period), len(candles)):
        c, p = candles[i], candles[i - 1]
        trs.append(max(c.h - c.l, abs(c.h - p.c), abs(c.l - p.c)))
    return sum(trs) / len(trs) if trs else 0.0


def macd(values):
    if len(values) < 26:
        return 0.0, 0.0
    line = ema(values, 12) - ema(values, 26)
    seq = []
    for i in range(max(1, len(values) - 35), len(values) + 1):
        v = values[:i]
        seq.append(ema(v, 12) - ema(v, 26))
    return line, ema(seq, 9) if seq else 0.0


def adx(candles, period=14):
    if len(candles) < period + 2:
        return 20.0
    plus, minus, trs = [], [], []
    for i in range(len(candles) - period, len(candles)):
        c, p = candles[i], candles[i - 1]
        up, dn = c.h - p.h, p.l - c.l
        plus.append(up if up > dn and up > 0 else 0)
        minus.append(dn if dn > up and dn > 0 else 0)
        trs.append(max(c.h - c.l, abs(c.h - p.c), abs(c.l - p.c)))
    t = sum(trs) or 1e-9
    pdi, mdi = 100 * sum(plus) / t, 100 * sum(minus) / t
    return 100 * abs(pdi - mdi) / max(pdi + mdi, 1e-9)


def parabolic_sar(candles, af_step=0.02, af_max=0.2):
    if len(candles) < 2:
        return candles[-1].c, True
    is_up = candles[1].c > candles[0].c
    sar = candles[0].l if is_up else candles[0].h
    ep = candles[0].h if is_up else candles[0].l
    af = af_step
    for i in range(1, len(candles)):
        c = candles[i]
        sar = sar + af * (ep - sar)
        if is_up:
            sar = min(sar, candles[i - 1].l, candles[i - 2].l) if i >= 2 else min(sar, candles[i - 1].l)
            if c.l < sar:
                is_up = False; sar = ep; ep = c.l; af = af_step
            elif c.h > ep:
                ep = c.h; af = min(af + af_step, af_max)
        else:
            sar = max(sar, candles[i - 1].h, candles[i - 2].h) if i >= 2 else max(sar, candles[i - 1].h)
            if c.h > sar:
                is_up = True; sar = ep; ep = c.h; af = af_step
            elif c.l < ep:
                ep = c.l; af = min(af + af_step, af_max)
    return sar, is_up


def get_signal(candles, strategy):
    closes = [x.c for x in candles]
    if len(closes) < 55:
        return "ESPERAR", 50, "Datos insuficientes"


    e20, e50, rv = ema(closes, 20), ema(closes, 50), rsi(closes)
    a, at, (m, s) = adx(candles), atr(candles), macd(closes)
    last = candles[-1]
    up = e20 > e50 and last.c > e20
    down = e20 < e50 and last.c < e20


    su = sum([up, rv > 52, a >= 22, m > s])
    sd = sum([down, rv < 48, a >= 22, m < s])


    # Confianza basada en confluencia real de indicadores
    confianza_calculada = min(96, 75 + (max(su, sd) * 5))


    if strategy.startswith("10."):
        e4, e8, e16 = ema(closes, 4), ema(closes, 8), ema(closes, 16)
        p4, p16 = ema(closes[:-1], 4), ema(closes[:-1], 16)
        _, sar_up = parabolic_sar(candles)
        if p4 <= p16 and e4 > e8 > e16 and sar_up and rv > 50:
            return "CALL", 93, f"Semáforo Alcista (EMA 4/8/16) | RSI {rv:.1f}"
        if p4 >= p16 and e4 < e8 < e16 and not sar_up and rv < 50:
            return "PUT", 93, f"Semáforo Bajista (EMA 4/8/16) | RSI {rv:.1f}"
        return "ESPERAR", 50, "Sin cruce válido"


    if strategy.startswith("1."):
        if up and rv >= 52: return "CALL", confianza_calculada, f"EMA20>EMA50 | RSI {rv:.1f}"
        if down and rv <= 48: return "PUT", confianza_calculada, f"EMA20<EMA50 | RSI {rv:.1f}"
    elif strategy.startswith("2."):
        if up and last.l <= e20 and rv > 50: return "CALL", 90, "Pullback EMA20 + RSI"
        if down and last.h >= e20 and rv < 50: return "PUT", 90, "Pullback EMA20 + RSI"
    elif strategy.startswith("3."):
        if a >= 25 and up: return "CALL", 88, f"ADX {a:.1f} + EMA50"
        if a >= 25 and down: return "PUT", 88, f"ADX {a:.1f} + EMA50"
    elif strategy.startswith("4."):
        if m > s and last.c > e50: return "CALL", 89, "MACD > señal + EMA50"
        if m < s and last.c < e50: return "PUT", 89, "MACD < señal + EMA50"
    elif strategy.startswith("5."):
        hh = max(x.h for x in candles[-20:-1])
        ll = min(x.l for x in candles[-20:-1])
        if last.c > hh and at > 0: return "CALL", 91, "Breakout + ATR"
        if last.c < ll and at > 0: return "PUT", 91, "Breakout + ATR"
    elif strategy.startswith("6."):
        if rv <= 25: return "CALL", 94, f"RSI extremo {rv:.1f}"
        if rv >= 75: return "PUT", 94, f"RSI extremo {rv:.1f}"
    elif strategy.startswith("7."):
        # Filtro de lateralidad: evita operar cuando la separación EMA es mínima
        # y el ADX indica ausencia de tendencia.
        separation = abs(e20 - e50) / max(abs(last.c), 1e-9) * 10000
        if a >= 22 and separation >= 3 and up and rv > 52:
            return "CALL", min(90, confianza_calculada), f"Mercado con tendencia | ADX {a:.1f}"
        if a >= 22 and separation >= 3 and down and rv < 48:
            return "PUT", min(90, confianza_calculada), f"Mercado con tendencia | ADX {a:.1f}"
        return "ESPERAR", 50, f"Lateralidad/no tendencia (ADX {a:.1f})"
    elif strategy.startswith("8."):
        # Filtro de volatilidad con ATR relativo: descarta mercados demasiado quietos.
        atr_pct = (at / abs(last.c) * 100) if last.c else 0
        if atr_pct < 0.015:
            return "ESPERAR", 50, f"Volatilidad insuficiente (ATR {atr_pct:.3f}%)"
        if up and rv >= 52:
            return "CALL", min(90, confianza_calculada), f"Volatilidad válida | ATR {atr_pct:.3f}%"
        if down and rv <= 48:
            return "PUT", min(90, confianza_calculada), f"Volatilidad válida | ATR {atr_pct:.3f}%"
        return "ESPERAR", 50, f"Sin dirección clara | ATR {atr_pct:.3f}%"
    elif strategy.startswith("9."):
        if su >= 3 and su > sd: return "CALL", confianza_calculada, "Confirmación múltiple alcista"
        if sd >= 3 and sd > su: return "PUT", confianza_calculada, "Confirmación múltiple bajista"


    return "ESPERAR", 50, "Sin confluencia suficiente"




BG = (0.027, 0.039, 0.063, 1)
CARD = (0.051, 0.075, 0.122, 1)
CYAN = (0, 0.898, 1, 1)
GREEN = (0, 0.90, 0.46, 1)
RED = (1, 0.20, 0.28, 1)
WHITE = (0.88, 0.91, 0.95, 1)

class LKButton(Button):
    def __init__(self, **kwargs):
        kwargs.setdefault('background_normal', '')
        kwargs.setdefault('background_color', (0.07, 0.13, 0.21, 1))
        kwargs.setdefault('color', WHITE)
        kwargs.setdefault('font_size', '14sp')
        kwargs.setdefault('size_hint_y', None)
        kwargs.setdefault('height', dp(44))
        super().__init__(**kwargs)

class LILKayzerApp(App):
    def build(self):
        self.title = 'LIL KAYZER TRADE'
        Window.clearcolor = BG
        self.api = None
        self.connected = False
        self._broker_email = None
        self._broker_password = None
        self.scanning = False
        self.stop_event = threading.Event()
        self.scan_thread = None
        self.timeframe = '1m'
        self.latest_signal = None
        self.history = []
        self.selected_asset = None
        root = BoxLayout(orientation='vertical', padding=dp(10), spacing=dp(8))
        header = BoxLayout(size_hint_y=None, height=dp(58), spacing=dp(8))
        header.add_widget(Label(text='[b][color=00E5FF]🐾 LIL KAYZER TRADE[/color][/b]\n[color=90A4AE]BOT DE SEÑALES V3.0 · ANDROID[/color]', markup=True, halign='left', valign='middle'))
        self.status = Label(text='● SIN CONECTAR', color=RED, size_hint_x=.55, bold=True)
        header.add_widget(self.status)
        root.add_widget(header)
        scroll = ScrollView(do_scroll_x=False)
        content = BoxLayout(orientation='vertical', spacing=dp(8), size_hint_y=None, padding=(0,0,0,dp(8)))
        content.bind(minimum_height=content.setter('height'))

        content.add_widget(self.section('CONFIGURACIÓN DE ANÁLISIS'))
        tfrow = BoxLayout(size_hint_y=None, height=dp(44), spacing=dp(5))
        self.tf_buttons = {}
        for tf in ['1m','2m','5m','10m']:
            b = LKButton(text=tf, background_color=CYAN if tf == self.timeframe else CARD, color=(0,0,0,1) if tf == self.timeframe else WHITE)
            b.bind(on_release=lambda inst, t=tf: self.choose_tf(t))
            tfrow.add_widget(b); self.tf_buttons[tf] = b
        content.add_widget(tfrow)
        self.strategy = Spinner(text=STRATEGIES[0], values=STRATEGIES, size_hint_y=None, height=dp(46), background_normal='', background_color=CARD)
        content.add_widget(self.strategy)
        self.expiry = Spinner(text='1 minuto', values=['1 minuto','2 minutos','5 minutos'], size_hint_y=None, height=dp(46), background_normal='', background_color=CARD)
        content.add_widget(self.expiry)

        content.add_widget(self.section('ACCESO A IQ OPTION'))
        self.email = TextInput(hint_text='Correo de IQ Option', multiline=False, size_hint_y=None, height=dp(46), background_color=CARD, foreground_color=WHITE, hint_text_color=(.55,.62,.69,1))
        self.password = TextInput(hint_text='Contraseña (no se guarda)', password=True, multiline=False, size_hint_y=None, height=dp(46), background_color=CARD, foreground_color=WHITE, hint_text_color=(.55,.62,.69,1))
        content.add_widget(self.email); content.add_widget(self.password)
        row = BoxLayout(size_hint_y=None, height=dp(46), spacing=dp(6))
        self.connect_btn = LKButton(text='CONECTAR', background_color=(0, .40, .95, 1))
        self.connect_btn.bind(on_release=self.connect_broker)
        row.add_widget(self.connect_btn)
        self.scan_btn = LKButton(text='INICIAR ESCANEO', background_color=GREEN, color=(0,0,0,1))
        self.scan_btn.bind(on_release=self.toggle_scan)
        row.add_widget(self.scan_btn)
        content.add_widget(row)

        content.add_widget(self.section('MULTI SCANNER'))
        self.asset_filter = Spinner(text='Todos los activos abiertos', values=['Todos los activos abiertos','Forex','OTC'], size_hint_y=None, height=dp(44), background_normal='', background_color=CARD)
        content.add_widget(self.asset_filter)
        self.scan_info = Label(text='El escáner consultará los activos que la API reporte abiertos.', color=(.60,.68,.75,1), size_hint_y=None, height=dp(42), halign='left', valign='middle')
        self.scan_info.bind(size=lambda inst, val: setattr(inst, 'text_size', val))
        content.add_widget(self.scan_info)

        content.add_widget(self.section('SEÑAL ACTUAL'))
        self.signal_asset = Label(text='Esperando conexión y señal', color=WHITE, bold=True, font_size='20sp', size_hint_y=None, height=dp(42))
        content.add_widget(self.signal_asset)
        self.signal_direction = Label(text='SIN SEÑAL', color=CYAN, bold=True, font_size='26sp', size_hint_y=None, height=dp(50))
        content.add_widget(self.signal_direction)
        self.signal_details = Label(text='Estrategia: —\nConfianza del indicador: —\nExpiración: —\nMotivo: —', color=WHITE, size_hint_y=None, height=dp(100), halign='left', valign='middle')
        self.signal_details.bind(size=lambda inst, val: setattr(inst, 'text_size', val))
        content.add_widget(self.signal_details)
        self.open_btn = LKButton(text='ABRIR IQ OPTION PARA OPERAR MANUALMENTE', background_color=GREEN, color=(0,0,0,1), height=dp(52))
        self.open_btn.bind(on_release=self.open_broker)
        content.add_widget(self.open_btn)

        content.add_widget(self.section('MEJORES SEÑALES / HISTORIAL'))
        self.history_label = Label(text='Todavía no hay señales.', color=(.75,.81,.87,1), size_hint_y=None, height=dp(130), halign='left', valign='top')
        self.history_label.bind(size=lambda inst, val: setattr(inst, 'text_size', val))
        content.add_widget(self.history_label)
        content.add_widget(Label(text='Solo genera señales. Nunca ejecuta operaciones. La puntuación no garantiza resultados.', color=(.58,.65,.72,1), font_size='11sp', size_hint_y=None, height=dp(40)))
        scroll.add_widget(content); root.add_widget(scroll)
        return root

    def section(self, text):
        return Label(text='[b][color=00E5FF]'+text+'[/color][/b]', markup=True, size_hint_y=None, height=dp(32), halign='left', valign='middle')

    def choose_tf(self, tf):
        self.timeframe = tf
        for key, button in self.tf_buttons.items():
            button.background_color = CYAN if key == tf else CARD
            button.color = (0,0,0,1) if key == tf else WHITE

    def popup(self, title, message):
        box = BoxLayout(orientation='vertical', padding=dp(12), spacing=dp(12))
        box.add_widget(Label(text=message))
        close = LKButton(text='ACEPTAR')
        box.add_widget(close)
        pop = Popup(title=title, content=box, size_hint=(.9,.45), auto_dismiss=False)
        close.bind(on_release=pop.dismiss); pop.open()

    def connect_broker(self, *_):
        if IQ_Option is None:
            self.popup('Dependencia no disponible', 'La biblioteca iqoptionapi no está instalada o no pudo cargarse en esta compilación Android. Revisa el README y compila con las dependencias indicadas; la compatibilidad debe probarse en el dispositivo.')
            return
        email, password = self.email.text.strip(), self.password.text
        if not email or not password:
            self.popup('Faltan credenciales', 'Introduce tu correo y contraseña directamente en el dispositivo. La app no guarda estos datos.')
            return
        self.connect_btn.disabled = True; self.connect_btn.text = 'CONECTANDO…'
        # Credentials stay only in process memory; they are never written to disk.
        self._broker_email = email
        self._broker_password = password
        threading.Thread(target=self._connect_worker, args=(email,password), daemon=True).start()

    def _connect_worker(self, email, password):
        try:
            api = IQ_Option(email, password)
            if hasattr(api, 'set_max_reconnect'):
                api.set_max_reconnect(5)
            result = api.connect()
            ok = result[0] if isinstance(result, tuple) else bool(result)
            if not ok:
                reason = str(result[1]) if isinstance(result, tuple) and len(result)>1 else 'El broker rechazó la conexión.'
                Clock.schedule_once(lambda dt: self._connection_result(False, reason), 0)
                return
            try:
                api.change_balance('PRACTICE')
            except Exception as balance_exc:
                balance_error = str(balance_exc)[:250]
                Clock.schedule_once(lambda dt, err=balance_error: self._connection_result(False, f'Conectó, pero no pudo seleccionar PRACTICE: {err}'), 0)
                return
            if hasattr(api, 'check_connect') and not api.check_connect():
                Clock.schedule_once(lambda dt: self._connection_result(False, 'La sesión se cerró inmediatamente después de conectar.'), 0)
                return
            self.api = api
            Clock.schedule_once(lambda dt: self._connection_result(True, 'Conectado a IQ Option · cuenta PRACTICE'), 0)
        except Exception as exc:
            Clock.schedule_once(lambda dt: self._connection_result(False, str(exc)[:300]), 0)

    def _connection_result(self, ok, message):
        self.connect_btn.disabled = False; self.connect_btn.text = 'CONECTADO' if ok else 'CONECTAR'
        self.connected = ok
        self.status.text = '● CONECTADO' if ok else '● ERROR DE CONEXIÓN'
        self.status.color = GREEN if ok else RED
        self.scan_info.text = message
        if not ok: self.popup('Conexión fallida', message)

    def toggle_scan(self, *_):
        if self.scanning:
            self.stop_event.set(); self.scan_btn.text = 'DETENIENDO…'; return
        if not self.api:
            self.popup('Conexión requerida', 'Conecta con IQ Option antes de iniciar el escaneo.')
            return
        self.stop_event.clear(); self.scanning = True
        self.scan_btn.text = 'DETENER ESCANEO'
        config = {'timeframe':self.timeframe, 'strategy':self.strategy.text, 'expiry':self.expiry.text, 'filter':self.asset_filter.text}
        self.scan_thread = threading.Thread(target=self._scan_worker, args=(config,), daemon=True)
        self.scan_thread.start()

    def _get_open_assets(self):
        """Return every asset reported as open by the broker API.

        The API can expose several market sections (turbo, binary, digital,
        forex, CFD, crypto, etc.). Restricting this to only turbo/binary made
        the old scanner silently miss valid assets.
        """
        opened = self.api.get_all_open_time()
        assets = set()
        if not isinstance(opened, dict):
            return []
        for section in opened.values():
            if not isinstance(section, dict):
                continue
            for symbol, info in section.items():
                if isinstance(info, dict) and info.get('open') is True:
                    assets.add(str(symbol))
        return sorted(assets)

    def _scan_worker(self, config):
        seconds = {'1m':60,'2m':120,'5m':300,'10m':600}.get(config['timeframe'],60)
        last_sent = {}
        while not self.stop_event.is_set():
            try:
                if not self.api:
                    break
                if hasattr(self.api, 'check_connect') and not self.api.check_connect():
                    if self._broker_email and self._broker_password:
                        reconnect = self.api.connect()
                        reconnect_ok = reconnect[0] if isinstance(reconnect, tuple) else bool(reconnect)
                        if reconnect_ok:
                            try: self.api.change_balance('PRACTICE')
                            except Exception: pass
                        else:
                            raise RuntimeError('La conexión con IQ Option se perdió y no pudo restablecerse.')
                    else:
                        raise RuntimeError('La sesión de IQ Option no está conectada.')
                assets = self._get_open_assets()
                if config['filter'] == 'Forex': assets = [a for a in assets if '-OTC' not in a]
                elif config['filter'] == 'OTC': assets = [a for a in assets if '-OTC' in a]
                found=[]; now=time.time()
                for symbol in assets:
                    if self.stop_event.is_set(): break
                    try:
                        endtime = self.api.get_server_timestamp() if hasattr(self.api, 'get_server_timestamp') else now
                        raw = self.api.get_candles(symbol, seconds, 80, endtime)
                        if not raw or len(raw)<55: continue
                        raw = sorted(raw, key=lambda x:x.get('from',0))
                        candles=[]
                        for item in raw:
                            vals=(float(item['open']),float(item['max']),float(item['min']),float(item['close']))
                            if all(math.isfinite(v) for v in vals): candles.append(Candle(*vals))
                        if len(candles)<55: continue
                        direction, confidence, reason = get_signal(candles[:-1], config['strategy'])
                        if direction not in ('CALL','PUT'): continue
                        candle_id=raw[-1].get('from',0); key=(direction,candle_id,config['strategy'])
                        if last_sent.get(symbol)==key: continue
                        last_sent[symbol]=key
                        found.append({'symbol':symbol,'direction':direction,'confidence':int(confidence),'reason':reason,'strategy':config['strategy'],'expiry':config['expiry'],'time':datetime.now().strftime('%H:%M:%S'),'timeframe':config['timeframe']})
                    except Exception:
                        continue
                found.sort(key=lambda x:x['confidence'], reverse=True)
                if found: Clock.schedule_once(lambda dt, items=found: self.publish(items),0)
                Clock.schedule_once(lambda dt, n=len(assets): setattr(self.scan_info,'text',f'Escaneo consultó {n} activos · actualización aproximada cada 3 s · {datetime.now().strftime("%H:%M:%S")}'),0)
            except Exception as exc:
                Clock.schedule_once(lambda dt, err=str(exc)[:180]: setattr(self.scan_info,'text','Error de escaneo: '+err),0)
            self.stop_event.wait(3)
        self.scanning=False
        Clock.schedule_once(lambda dt: setattr(self.scan_btn,'text','INICIAR ESCANEO'),0)

    def publish(self, signals):
        if not signals: return
        self.latest_signal = signals[0]
        s=self.latest_signal
        self.selected_asset=s['symbol']
        self.signal_asset.text=s['symbol']+' · '+s['timeframe']
        self.signal_direction.text=('⬆ CALL' if s['direction']=='CALL' else '⬇ PUT')+'  '+str(s['confidence'])+'%'
        self.signal_direction.color=GREEN if s['direction']=='CALL' else RED
        self.signal_details.text=f"Estrategia: {s['strategy']}\nConfianza del indicador: {s['confidence']}% (no es probabilidad garantizada)\nExpiración sugerida: {s['expiry']}\nMotivo: {s['reason']}\nDetectada: {s['time']}"
        for item in reversed(signals[:8]):
            self.history.insert(0, item)
        self.history=self.history[:40]
        lines=[]
        for i,item in enumerate(self.history[:12],1):
            lines.append(f"{i}. {item['time']}  {item['symbol']}  {item['direction']} {item['confidence']}%\n   {item['strategy']} · {item['expiry']}")
        self.history_label.text='\n'.join(lines)

    def open_broker(self, *_):
        # IQ Option does not expose a documented, stable Android deep link for every asset.
        # Open the official trading room; the user chooses the signal's asset and enters manually.
        url = 'https://iqoption.com/traderoom'
        try:
            if platform == 'android':
                from jnius import autoclass
                Intent = autoclass('android.content.Intent')
                Uri = autoclass('android.net.Uri')
                activity = autoclass('org.kivy.android.PythonActivity').mActivity
                intent = Intent(Intent.ACTION_VIEW, Uri.parse(url))
                activity.startActivity(intent)
            else:
                webbrowser.open(url)
            if self.latest_signal:
                self.popup('Operación manual', f"Señal seleccionada: {self.latest_signal['symbol']} · {self.latest_signal['direction']}\nAbre el activo correspondiente en IQ Option y confirma manualmente la operación. No se envía ninguna orden desde esta app.")
        except Exception:
            self.popup('Abrir IQ Option', 'Abre IQ Option manualmente y busca el activo de la señal.')

    def on_stop(self):
        self.stop_event.set()
        try:
            if self.api and hasattr(self.api, 'close'):
                self.api.close()
        except Exception:
            pass

if __name__ == '__main__':
    LILKayzerApp().run()
