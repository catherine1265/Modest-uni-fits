def run_decision_cropped(top_path, bottom_path, card_path, models=None):
    if models is None:
        models = load_models()
    top    = check_top(top_path, models["top"])
    bottom = check_bottom(bottom_path, models["bottom"])
    card   = check_card(card_path, models["card"])
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
