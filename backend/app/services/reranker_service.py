import logging
from typing import List, Tuple, Dict, Any
from app.core.config import settings

logger = logging.getLogger(__name__)

class RerankerService:
    _instance = None
    _model = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(RerankerService, cls).__new__(cls)
            cls._instance._init_model()
        return cls._instance

    def _init_model(self):
        try:
            from sentence_transformers import CrossEncoder
            logger.info(f"Loading CrossEncoder: {settings.RERANKER_MODEL_NAME}")
            self._model = CrossEncoder(settings.RERANKER_MODEL_NAME)
            logger.info("CrossEncoder loaded successfully.")
        except Exception as e:
            logger.info(f"CrossEncoder not active ({e}). Using lexical-semantic cross-scoring fallback.")
            self._model = None

    def rerank(self, query: str, candidate_texts: List[str]) -> List[float]:
        """
        Takes a query and a list of candidate documents/opportunity texts.
        Returns a list of float relevance scores.
        """
        if not candidate_texts:
            return []

        if self._model is not None:
            try:
                pairs = [[query, text] for text in candidate_texts]
                scores = self._model.predict(pairs)
                # Normalize scores to 0.0 - 1.0 range via sigmoid if raw logits
                import math
                def sigmoid(x):
                    return 1.0 / (1.0 + math.exp(-float(x)))
                return [sigmoid(s) for s in scores]
            except Exception as e:
                logger.error(f"Error during cross-encoder prediction: {e}")

        # Deterministic cross-scoring fallback:
        # Measures query term precision, multi-token phrase coverage, and proximity
        query_words = set(query.lower().split())
        scores = []
        for text in candidate_texts:
            text_lower = text.lower()
            matched_words = sum(1 for w in query_words if len(w) > 2 and w in text_lower)
            coverage = matched_words / max(len(query_words), 1)
            
            # Bonus for exact query phrase match
            phrase_bonus = 0.25 if query.lower() in text_lower else 0.0
            score = min(1.0, 0.4 * coverage + phrase_bonus + 0.35)
            scores.append(score)
        return scores

reranker_service = RerankerService()
