import hashlib
import numpy as np
from typing import List, Union
import logging
from app.core.config import settings

logger = logging.getLogger(__name__)

class EmbeddingService:
    _instance = None
    _model = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(EmbeddingService, cls).__new__(cls)
            cls._instance._init_model()
        return cls._instance

    def _init_model(self):
        try:
            from sentence_transformers import SentenceTransformer
            logger.info(f"Loading SentenceTransformer: {settings.EMBEDDING_MODEL_NAME}")
            self._model = SentenceTransformer(settings.EMBEDDING_MODEL_NAME)
            logger.info("SentenceTransformer loaded successfully.")
        except Exception as e:
            logger.warning(f"Could not load SentenceTransformer ({e}). Using deterministic semantic feature projector fallback.")
            self._model = None

    def get_text_hash(self, text: str) -> str:
        return hashlib.sha256(text.strip().lower().encode("utf-8")).hexdigest()

    def _fallback_embed(self, text: str, dim: int = 384) -> List[float]:
        """
        Deterministic unit-normalized semantic n-gram pseudo-embedding.
        Ensures consistent cosine similarity behavior even if torch/transformers isn't downloaded.
        """
        tokens = text.lower().replace("-", " ").replace("/", " ").split()
        vec = np.zeros(dim, dtype=np.float32)
        
        for token in tokens:
            token_hash = int(hashlib.md5(token.encode("utf-8")).hexdigest(), 16)
            idx = token_hash % dim
            sign = 1.0 if ((token_hash >> 8) % 2 == 0) else -1.0
            vec[idx] += sign * (1.0 + len(token) * 0.1)
            
            # Bigrams
            if len(token) > 4:
                sub_hash = int(hashlib.md5(token[:4].encode("utf-8")).hexdigest(), 16)
                vec[(sub_hash + 17) % dim] += sign * 0.5

        norm = np.linalg.norm(vec)
        if norm > 0:
            vec = vec / norm
        else:
            vec[0] = 1.0
        return vec.tolist()

    def embed_text(self, text: str) -> List[float]:
        if not text or not text.strip():
            return [0.0] * settings.EMBEDDING_DIMENSION
            
        clean_text = text.strip()
        if self._model is not None:
            try:
                emb = self._model.encode(clean_text, normalize_embeddings=True)
                return emb.tolist()
            except Exception as e:
                logger.error(f"Error encoding text with model: {e}")
                return self._fallback_embed(clean_text, settings.EMBEDDING_DIMENSION)
        return self._fallback_embed(clean_text, settings.EMBEDDING_DIMENSION)

    def embed_batch(self, texts: List[str]) -> List[List[float]]:
        if not texts:
            return []
        if self._model is not None:
            try:
                embs = self._model.encode(texts, normalize_embeddings=True, batch_size=32)
                return [e.tolist() for e in embs]
            except Exception as e:
                logger.error(f"Batch encoding error: {e}")
        return [self._fallback_embed(t, settings.EMBEDDING_DIMENSION) for t in texts]

    @staticmethod
    def cosine_similarity(vec_a: List[float], vec_b: List[float]) -> float:
        if not vec_a or not vec_b:
            return 0.0
        a = np.array(vec_a, dtype=np.float32)
        b = np.array(vec_b, dtype=np.float32)
        norm_a = np.linalg.norm(a)
        norm_b = np.linalg.norm(b)
        if norm_a == 0.0 or norm_b == 0.0:
            return 0.0
        return float(np.dot(a, b) / (norm_a * norm_b))

embedding_service = EmbeddingService()
