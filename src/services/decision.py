# =====================================================
# services/decision.py
# Gabungin top + bottom + card jadi 1 keputusan. NO streamlit.
# =====================================================

import os
import joblib

from src.config.settings import (
    TOP_MODEL_PATH,
    BOTTOM_MODEL_PATH,
    CARD_MODEL_PATH,
)
from src.services.classifier import check_top, check_bottom, check_card
from src.utils.helpers import ensure_models


def load_models():
    ensure_models()
    models = {}
    for name, path in [("top", TOP_MODEL_PATH), ("bottom", BOTTOM_MODEL_PATH), ("card", CARD_MODEL_PATH)]:
        if not os.path.exists(path):
            raise FileNotFoundError(f"Model tidak ditemukan: {path}")
        models[name] = joblib.load(path)
        print(f"Loaded: {path}")
    return models


def _build_result(top, bottom, card):
    reasons, passed = [], True
    if top["detected"]:
        reasons.append(f"Top OK: {top['class']} ({top['confidence']:.2%})")
    else:
        reasons.append(f"Top FAIL: {top['class']} ({top['confidence']:.2%})")
        passed = False
    if bottom["detected"]:
        reasons.append(f"Bottom OK: {bottom['class']} ({bottom['confidence']:.2%})")
    else:
        reasons.append(f"Bottom FAIL: {bottom['class']} ({bottom['confidence']:.2%})")
        passed = False
    if card["detected"]:
        reasons.append(f"Card OK ({card['confidence']:.2%})")
    else:
        reasons.append(f"Card FAIL ({card['confidence']:.2%})")
        passed = False
    return {"status": "PASS" if passed else "FAIL", "top": top, "bottom": bottom, "card": card, "reasons": reasons}


def run_decision(image_path, models=None):
    if models is None:
        models = load_models()
    top    = check_top(image_path, models["top"])
    bottom = check_bottom(image_path, models["bottom"])
    card   = check_card(image_path, models["card"])
    return _build_result(top, bottom, card)


def run_decision_cropped(top_path, bottom_path, card_path, models=None):
    if models is None:
        models = load_models()
    top    = check_top(top_path, models["top"])
    bottom = check_bottom(bottom_path, models["bottom"])
    card   = check_card(card_path, models["card"])
    return _build_result(top, bottom, card)
