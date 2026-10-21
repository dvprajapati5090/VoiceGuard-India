"""
Comprehensive Test Script for Agentis ML Spoof Detection Ensemble.
Verifies dataset generation, individual sub-models, ensemble scoring, and SageMaker endpoint contract.
"""

import os
import sys
import json
import unittest

# Add project root to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from ml_engine.dataset.generator import AudioSampleGenerator
from ml_engine.models.lcnn_filter import LCNNFilter
from ml_engine.models.wav2vec2_antispoof import Wav2Vec2AntiSpoof
from ml_engine.models.prosody_analyzer import ProsodyAnalyzer
from ml_engine.ensemble_scorer import SpoofDetectionEnsemble
from ml_engine import sagemaker_serve

class TestMLSpoofEnsemble(unittest.TestCase):
    
    @classmethod
    def setUpClass(cls):
        """Generate test audio samples."""
        cls.gen = AudioSampleGenerator()
        cls.sample_paths = cls.gen.generate_all_samples()
        cls.ensemble = SpoofDetectionEnsemble()

    def test_audio_generator(self):
        """Verify audio samples exist and have non-zero size."""
        for sample_type, path in self.sample_paths.items():
            self.assertTrue(os.path.exists(path), f"Sample path {path} does not exist")
            self.assertGreater(os.path.getsize(path), 1000, f"Sample file {path} is too small")

    def test_lcnn_filter(self):
        """Verify LCNN pre-filter produces valid score (0.0 to 1.0)."""
        signal = self.ensemble.load_audio_from_file(self.sample_paths["authentic"])
        res = LCNNFilter().predict(signal)
        self.assertIn("score", res)
        self.assertGreaterEqual(res["score"], 0.0)
        self.assertLessEqual(res["score"], 1.0)

    def test_wav2vec2_antispoof(self):
        """Verify Wav2Vec2 scorer produces valid score."""
        signal = self.ensemble.load_audio_from_file(self.sample_paths["authentic"])
        res = Wav2Vec2AntiSpoof().predict(signal)
        self.assertIn("score", res)
        self.assertGreaterEqual(res["score"], 0.0)
        self.assertLessEqual(res["score"], 1.0)

    def test_prosody_analyzer(self):
        """Verify Prosody analyzer measures pitch metrics."""
        signal = self.ensemble.load_audio_from_file(self.sample_paths["authentic"])
        res = ProsodyAnalyzer().predict(signal)
        self.assertIn("score", res)
        self.assertIn("jitter_percent", res["metrics"])

    def test_ensemble_classification(self):
        """Verify ensemble correctly classifies authentic voice vs AI clone vs ambiguous noise."""
        # 1. Authentic voice -> PASS
        auth_res = self.ensemble.score_audio_file(self.sample_paths["authentic"])
        print(f"\n[TEST AUTHENTIC] Score: {auth_res['ensemble_score']}, Class: {auth_res['classification']}")
        self.assertEqual(auth_res["classification"], "PASS")

        # 2. Cloned deepfake -> BLOCK
        clone_res = self.ensemble.score_audio_file(self.sample_paths["cloned"])
        print(f"[TEST CLONED]    Score: {clone_res['ensemble_score']}, Class: {clone_res['classification']}")
        self.assertEqual(clone_res["classification"], "BLOCK")

        # 3. Ambiguous noisy call -> AMBIGUOUS (Triggers self-correction)
        ambig_res = self.ensemble.score_audio_file(self.sample_paths["ambiguous"])
        print(f"[TEST AMBIGUOUS] Score: {ambig_res['ensemble_score']}, Class: {ambig_res['classification']}")
        self.assertEqual(ambig_res["classification"], "AMBIGUOUS")
        self.assertTrue(ambig_res["requires_self_correction"])

    def test_sagemaker_endpoint_contract(self):
        """Verify SageMaker serve handler compatibility."""
        model = sagemaker_serve.model_fn(".")
        input_payload = json.dumps({"sample_type": "cloned"})
        deserialized = sagemaker_serve.input_fn(input_payload, "application/json")
        prediction = sagemaker_serve.predict_fn(deserialized, model)
        output_str, ctype = sagemaker_serve.output_fn(prediction, "application/json")
        
        parsed_out = json.loads(output_str)
        self.assertEqual(parsed_out["classification"], "BLOCK")

if __name__ == "__main__":
    unittest.main()
