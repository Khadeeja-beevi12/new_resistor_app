"""Pure resistor logic: no web code, so it can be imported in a notebook or tested alone."""
import random

DIGITS = {"Black": 0, "Brown": 1, "Red": 2, "Orange": 3, "Yellow": 4,
          "Green": 5, "Blue": 6, "Violet": 7, "Grey": 8, "White": 9}
MULTIPLIERS = {k: 10 ** v for k, v in DIGITS.items()}
TOLERANCES = {"Brown": "±1%", "Red": "±2%", "Gold": "±5%", "Silver": "±10%"}

CHALLENGES = [
    ("Brown", "Black", "Brown", "Gold"),     # 100 Ω
    ("Red", "Red", "Brown", "Gold"),         # 220 Ω
    ("Orange", "Orange", "Brown", "Gold"),   # 330 Ω
    ("Yellow", "Violet", "Brown", "Gold"),   # 470 Ω
    ("Green", "Blue", "Brown", "Gold"),      # 560 Ω
    ("Brown", "Black", "Red", "Gold"),       # 1 kΩ
    ("Red", "Red", "Red", "Gold"),           # 2.2 kΩ
    ("Yellow", "Violet", "Red", "Gold"),     # 4.7 kΩ
    ("Brown", "Black", "Orange", "Gold"),    # 10 kΩ
    ("Brown", "Red", "Orange", "Gold"),      # 12 kΩ
    ("Red", "Red", "Orange", "Gold"),        # 22 kΩ
    ("Yellow", "Violet", "Orange", "Gold"),  # 47 kΩ
    ("Green", "Blue", "Orange", "Gold"),     # 56 kΩ
]


def calculate(bands):
    b1, b2, mult, tol = bands
    value = (DIGITS[b1] * 10 + DIGITS[b2]) * MULTIPLIERS[mult]
    return value, TOLERANCES.get(tol, "")


def fmt(v):
    if v >= 1_000_000:
        return f"{v / 1_000_000:g} MΩ"
    if v >= 1_000:
        return f"{v / 1_000:g} kΩ"
    return f"{v:g} Ω"


def normalize(answer):
    """Convert '220', '220 ohm', '1k', '1 kΩ', '4.7kΩ' to a float in ohms."""
    if answer is None:
        return None
    t = str(answer).strip().lower().replace(" ", "").replace(",", "")
    for junk in ("ohms", "ohm", "ω"):
        t = t.replace(junk, "")
    t = t.replace("kilo", "k").replace("mega", "m")
    try:
        if t.endswith("k"):
            return float(t[:-1]) * 1_000
        if t.endswith("m"):
            return float(t[:-1]) * 1_000_000
        return float(t)
    except ValueError:
        return None


def pick(previous=None):
    options = [c for c in CHALLENGES if tuple(c) != tuple(previous or ())]
    return random.choice(options or CHALLENGES)
