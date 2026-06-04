# Gabungin top + bottom + card jadi 1 keputusan

import os
import joblib

from src.config.settings import (
    TOP_MODEL_PATH,
    BOTTOM_MODEL_PATH,
    CARD_MODEL_PATH,
)
from src.services.classifier import check_top, check_bottom, check_card


def load_models():
    models = {}
    for name, path in [("top", TOP_MODEL_PATH), ("bottom", BOTTOM_MODEL_PATH), ("card", CARD_MODEL_PATH)]:
        if not os.path.exists(path):
            raise FileNotFoundError(f"Model tidak ditemukan: {path}")
        models[name] = joblib.load(path)
        print(f"Loaded: {path}")
    return models


def run_decision(image_path, models=None):
    if models is None:
        models = load_models()
    top    = check_top(image_path, models["top"])
    bottom = check_bottom(image_path, models["bottom"])
    card   = check_card(image_path, models["card"])
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
    return {"status": "PASS" if passed else "FAIL", "top": top, "bottom": bottom, "card": card, "reasons": reasons, "image_path": image_path}
