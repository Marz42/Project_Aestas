import logging
import os

from app.core.config import Settings, get_settings
from app.models.article import Article
from app.services.clustering.text_utils import article_rerank_text

logger = logging.getLogger(__name__)

_reranker = None


def _get_reranker(settings: Settings):
    global _reranker
    if _reranker is None:
        os.environ.setdefault("HF_HOME", settings.hf_home)
        from sentence_transformers import CrossEncoder

        logger.info("Loading reranker model: %s", settings.reranker_model)
        _reranker = CrossEncoder(settings.reranker_model)
    return _reranker


def _normalize_scores(raw_scores: list[float]) -> list[float]:
    """Map CrossEncoder logits to 0~1 for threshold comparison."""
    try:
        from scipy.special import expit

        return [float(expit(s)) for s in raw_scores]
    except ImportError:
        import math

        return [1.0 / (1.0 + math.exp(-s)) for s in raw_scores]


def rerank_pairs(
    query_text: str,
    candidate_texts: list[str],
    settings: Settings | None = None,
) -> list[float]:
    if not candidate_texts:
        return []
    settings = settings or get_settings()
    reranker = _get_reranker(settings)
    pairs = [[query_text, text] for text in candidate_texts]
    raw = reranker.predict(pairs)
    if hasattr(raw, "tolist"):
        raw = raw.tolist()
    if isinstance(raw, (int, float)):
        return _normalize_scores([float(raw)])
    return _normalize_scores([float(s) for s in raw])


def score_articles(
    source: Article,
    candidates: list[Article],
    settings: Settings | None = None,
) -> list[tuple[Article, float]]:
    if not candidates:
        return []
    query_text = article_rerank_text(source)
    candidate_texts = [article_rerank_text(c) for c in candidates]
    scores = rerank_pairs(query_text, candidate_texts, settings)
    return list(zip(candidates, scores, strict=True))
