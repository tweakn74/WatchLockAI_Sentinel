# ML Scoring -- Spec

No model artifact is provided in this pack. Implement `detection/ml_scoring.py` with a typed interface:
- function: score_behavior(signal: dict) -> Optional[tuple[float,str]]
  returns: None (no score) unless a `model_path` exists in config and loads successfully.
If a model is later provided at `models/model.pkl`, wrap it safely; otherwise keep path unset.