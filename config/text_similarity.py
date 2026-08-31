import logging

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

logger = logging.getLogger("config")


def compute_cosine_similarities(query_text, candidate_texts, ngram_range=(1, 1)):
    """
    Returns a list of TF-IDF cosine-similarity scores between `query_text` and each
    text in `candidate_texts` (same order). Used by both the ATS resume-vs-job scorer
    (ai_module) and the job recommendation engine (data_science) — previously each app
    had its own near-identical TfidfVectorizer + cosine_similarity implementation.

    Returns None if vectorization fails (e.g. all-stopword/empty input), so callers can
    apply whatever fallback score makes sense for their context — the two existing
    callers use different fallback values (0.3 vs 0.5), so that stays caller-specific
    rather than being baked in here.
    """
    if not candidate_texts:
        return []
    try:
        vectorizer = TfidfVectorizer(stop_words="english", ngram_range=ngram_range)
        corpus = [query_text or ""] + [t or "" for t in candidate_texts]
        tfidf = vectorizer.fit_transform(corpus)
        sims = cosine_similarity(tfidf[0:1], tfidf[1:])[0]
        return [float(s) for s in sims]
    except ValueError as e:
        logger.info("tfidf_similarity_fallback", extra={"reason": str(e)})
        return None
