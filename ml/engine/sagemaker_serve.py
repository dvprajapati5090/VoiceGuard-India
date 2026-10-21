"""
AWS SageMaker Endpoint Inference Handler for Agentis Multi-Lingual Voice Verification Agent.
Supports English (en), Hindi (hi), and Gujarati (gu) audio evaluation.
Implements model_fn, input_fn, predict_fn, and output_fn.

API Contract:
- Request: POST JSON {"language": "en"|"hi"|"gu", "sample_type": "authentic"|"cloned"|"ambiguous", "audio_file_path": str}
"""

import json
import base64
import numpy as np

from ml_engine.ensemble_scorer import SpoofDetectionEnsemble
from ml_engine.dataset.generator import AudioSampleGenerator

def model_fn(model_dir):
    """SageMaker model loader hook."""
    print("[SageMaker-Init] Loading Agentis Multi-Lingual Spoof Detection Ensemble Model...")
    ensemble = SpoofDetectionEnsemble()
    return ensemble

def input_fn(request_body, request_content_type='application/json'):
    """SageMaker input deserializer hook."""
    if request_content_type == 'application/json':
        data = json.loads(request_body)
        return data
    else:
        raise ValueError(f"Unsupported content type: {request_content_type}")

def predict_fn(input_data, model):
    """
    SageMaker prediction hook.
    Evaluates requested audio clip across English (en), Hindi (hi), or Gujarati (gu).
    """
    language = input_data.get("language", "en")
    
    if "sample_type" in input_data:
        gen = AudioSampleGenerator()
        file_path = gen.generate_waveform(duration_sec=4.0, sample_type=input_data["sample_type"], language=language)
        result = model.score_audio_file(file_path, language=language)
        result["requested_sample_type"] = input_data["sample_type"]
        return result
        
    elif "audio_file_path" in input_data:
        result = model.score_audio_file(input_data["audio_file_path"], language=language)
        return result
        
    elif "audio_base64" in input_data:
        raw_bytes = base64.b64decode(input_data["audio_base64"])
        int_samples = np.frombuffer(raw_bytes, dtype=np.int16)
        float_signal = int_samples.astype(np.float32) / 32768.0
        result = model.score_signal(float_signal, language=language)
        return result
        
    else:
        gen = AudioSampleGenerator()
        file_path = gen.generate_waveform(duration_sec=4.0, sample_type="authentic", language=language)
        return model.score_audio_file(file_path, language=language)

def output_fn(prediction, response_content_type='application/json'):
    """SageMaker output serializer hook."""
    if response_content_type == 'application/json':
        return json.dumps(prediction, indent=2), response_content_type
    else:
        return json.dumps(prediction), 'application/json'
