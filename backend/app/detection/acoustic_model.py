try:
    import torch
    import torch.nn as nn
    from transformers import Wav2Vec2Processor, Wav2Vec2Model
except ImportError:
    torch = None
    nn = None
import numpy as np
import time
from typing import Optional
from app.config import settings

if nn is not None:
    class SimpleClassifierHead(nn.Module):
        def __init__(self):
            super().__init__()
            # 1024 (XLS-R) + 32 (Language Embedding) = 1056
            self.lang_embed = nn.Linear(2, 32)
            self.fc1 = nn.Linear(1056, 256)
            self.relu = nn.ReLU()
            self.drop = nn.Dropout(0.1)
            self.fc2 = nn.Linear(256, 1)
            self.sigmoid = nn.Sigmoid()

        def forward(self, x, lang_idx):
            # STRETCH: Replace random classifier weights with fine-tuned checkpoint
            lang_vec = torch.zeros(1, 2).to(x.device)
            lang_vec[0, lang_idx] = 1.0
            lang_feat = self.lang_embed(lang_vec)
            
            x = torch.cat([x, lang_feat], dim=-1)
            x = self.fc1(x)
            x = self.relu(x)
            x = self.drop(x)
            x = self.fc2(x)
            return self.sigmoid(x)
else:
    class SimpleClassifierHead:
        pass

class XLSRAcousticModel:
    _instance: Optional['XLSRAcousticModel'] = None

    @classmethod
    def get_instance(cls) -> 'XLSRAcousticModel':
        if cls._instance is None:
            cls._instance = XLSRAcousticModel()
        return cls._instance

    def __init__(self):
        self.is_loaded = False
        if torch is None:
            print("Torch is not installed. XLSRAcousticModel will be disabled.")
            return
            
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        try:
            self.processor = Wav2Vec2Processor.from_pretrained(settings.model_name)
            self.model = Wav2Vec2Model.from_pretrained(settings.model_name).to(self.device)
            self.model.eval()
            self.classifier = SimpleClassifierHead().to(self.device)
            self.classifier.eval()
            self.is_loaded = True
        except Exception as e:
            print(f"Failed to load model: {e}")

    def score(self, audio: np.ndarray, sample_rate: int, language: str) -> float:
        if not self.is_loaded:
            return 0.5
        
        start_t = time.time()
        try:
            emb = self._extract_embedding(audio, sample_rate)
            lang_idx = 0 if language == 'hi' else 1
            score = self._classify(emb, lang_idx)
            
            if time.time() - start_t > 0.45:
                return 0.5
                
            return score
        except Exception:
            return 0.5

    def _extract_embedding(self, audio: np.ndarray, sample_rate: int) -> torch.Tensor:
        inputs = self.processor(audio, sampling_rate=sample_rate, return_tensors="pt")
        with torch.no_grad():
            outputs = self.model(inputs.input_values.to(self.device))
            hidden = outputs.last_hidden_state
            return hidden.mean(dim=1)

    def _classify(self, embedding: torch.Tensor, lang_idx: int) -> float:
        with torch.no_grad():
            out = self.classifier(embedding, lang_idx)
            return out.item()
