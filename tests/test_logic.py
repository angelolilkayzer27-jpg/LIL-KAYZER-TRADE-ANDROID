import ast
import math
import random
from pathlib import Path

SOURCE = Path(__file__).parents[1] / 'main.py'
TREE = ast.parse(SOURCE.read_text(encoding='utf-8'))
NS = {}
for name in ('Candle', 'ema', 'rsi', 'atr', 'macd', 'adx', 'parabolic_sar', 'get_signal'):
    nodes = [n for n in TREE.body if getattr(n, 'name', None) == name]
    assert nodes, f'Missing pure-logic symbol: {name}'
    exec(compile(ast.Module(body=nodes, type_ignores=[]), str(SOURCE), 'exec'), NS)


def make_candles(direction=1, count=100):
    out = []
    price = 100.0
    for _ in range(count):
        delta = direction * 0.2 + random.uniform(-0.05, 0.05)
        close = price + delta
        high = max(price, close) + 0.05
        low = min(price, close) - 0.05
        out.append(NS['Candle'](price, high, low, close))
        price = close
    return out


def test_indicators_are_finite():
    candles = make_candles(1)
    closes = [c.c for c in candles]
    values = [
        NS['ema'](closes, 20),
        NS['rsi'](closes),
        NS['atr'](candles),
        NS['macd'](closes)[0],
        NS['macd'](closes)[1],
        NS['adx'](candles),
        NS['parabolic_sar'](candles)[0],
    ]
    assert all(math.isfinite(v) for v in values)


def test_all_strategies_return_valid_result():
    for direction in (1, -1, 0):
        candles = make_candles(direction)
        for strategy in range(1, 11):
            signal, confidence, reason = NS['get_signal'](candles, f'{strategy}. test')
            assert signal in {'CALL', 'PUT', 'ESPERAR'}
            assert 0 <= confidence <= 100
            assert isinstance(reason, str) and reason


def test_short_history_waits():
    candles = make_candles(1, 20)
    assert NS['get_signal'](candles, '1. test')[0] == 'ESPERAR'
