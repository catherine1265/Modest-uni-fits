# Prediksi per model
from src.config.settings import TOP_CLASSES, BOTTOM_CLASSES, CONF_THRESH
from src.services.preprocess import (
    preprocess,
    extract_hog_clothing,
    extract_hog_card,
)


def check_top(image_path, model):
    feat = extract_hog_clothing(preprocess(image_path)).reshape(1, -1)
    pred = model.predict(feat)[0]
    conf = float(max(model.predict_proba(feat)[0])) if hasattr(model, "predict_proba") else 1.0
    return {"detected": pred in TOP_CLASSES, "class": pred, "confidence": round(conf, 4)}


def check_bottom(image_path, model):
    feat = extract_hog_clothing(preprocess(image_path)).reshape(1, -1)
    pred = model.predict(feat)[0]
    conf = float(max(model.predict_proba(feat)[0])) if hasattr(model, "predict_proba") else 1.0
    return {"detected": pred in BOTTOM_CLASSES, "class": pred, "confidence": round(conf, 4)}


def check_card(image_path, model, threshold=CONF_THRESH):
    feat  = extract_hog_card(preprocess(image_path)).reshape(1, -1)
    proba = model.predict_proba(feat)[0]
    label = int(model.predict(feat)[0])
    conf  = float(proba[1])
    return {"detected": label == 1 and conf >= threshold, "label": label, "confidence": round(conf, 4)}
