import json
import math
import re
from collections import Counter, defaultdict
from pathlib import Path


TOKEN_RE = re.compile(r"[a-zA-Z0-9']+")

STOPWORDS = {
    "a", "an", "and", "are", "as", "at", "be", "by", "for", "from", "has",
    "have", "how", "in", "is", "it", "its", "of", "on", "or", "that", "the",
    "their", "this", "to", "was", "were", "what", "when", "where", "who",
    "why", "with", "tell", "me", "about", "explain"
}


def tokenize(text):
    return [
        token.lower()
        for token in TOKEN_RE.findall(text)
        if token.lower() not in STOPWORDS and len(token) > 1
    ]


def split_sentences(text):
    protected = re.sub(r"\b([A-Z])\.", r"\1<DOT>", text)
    parts = re.split(r"(?<=[.!?])\s+", protected)
    return [part.replace("<DOT>", ".") for part in parts if part.strip()]


class RAGEngine:
    def __init__(self, kb_path):
        self.kb_path = Path(kb_path)
        self.documents = self._load_documents()
        self.doc_tokens = [tokenize(self._doc_text(doc)) for doc in self.documents]
        self.idf = self._build_idf()
        self.doc_vectors = [self._vectorize(tokens) for tokens in self.doc_tokens]

    def _load_documents(self):
        with self.kb_path.open("r", encoding="utf-8") as file:
            data = json.load(file)
        return data["documents"]

    def _doc_text(self, doc):
        return f"{doc['title']} {doc.get('category', '')} {doc['text']}"

    def _build_idf(self):
        document_count = len(self.doc_tokens)
        frequency = defaultdict(int)

        for tokens in self.doc_tokens:
            for token in set(tokens):
                frequency[token] += 1

        return {
            token: math.log((1 + document_count) / (1 + count)) + 1
            for token, count in frequency.items()
        }

    def _vectorize(self, tokens):
        counts = Counter(tokens)
        length = max(sum(counts.values()), 1)
        return {
            token: (count / length) * self.idf.get(token, 0.0)
            for token, count in counts.items()
        }

    def _cosine_similarity(self, left, right):
        shared = set(left) & set(right)
        numerator = sum(left[token] * right[token] for token in shared)
        left_norm = math.sqrt(sum(value * value for value in left.values()))
        right_norm = math.sqrt(sum(value * value for value in right.values()))

        if left_norm == 0 or right_norm == 0:
            return 0.0
        return numerator / (left_norm * right_norm)

    def retrieve(self, question, top_k=3):
        query_vector = self._vectorize(tokenize(question))
        scored = []

        for doc, doc_vector in zip(self.documents, self.doc_vectors):
            score = self._cosine_similarity(query_vector, doc_vector)
            if score > 0:
                scored.append((score, doc))

        scored.sort(key=lambda item: item[0], reverse=True)
        return [
            {
                "score": round(score, 4),
                "id": doc["id"],
                "title": doc["title"],
                "category": doc.get("category", ""),
                "text": doc["text"],
            }
            for score, doc in scored[:top_k]
        ]

    def answer(self, question):
        sources = self.retrieve(question)

        if not sources:
            return {
                "answer": (
                    "I could not find that in the local Tollywood knowledge base. "
                    "Try asking about Telugu cinema history, major films, directors, "
                    "stars, music, studios, or pan-Indian releases."
                ),
                "sources": [],
            }

        lead = self._build_answer(question, sources)
        return {"answer": lead, "sources": sources}

    def _build_answer(self, question, sources):
        source_texts = [source["text"] for source in sources]
        compact_context = " ".join(source_texts)
        sentences = split_sentences(compact_context)

        query_terms = set(tokenize(question))
        ranked_sentences = []

        for sentence in sentences:
            sentence_terms = set(tokenize(sentence))
            overlap = len(query_terms & sentence_terms)
            if overlap:
                ranked_sentences.append((overlap, sentence))

        ranked_sentences.sort(key=lambda item: item[0], reverse=True)
        selected = [sentence for _, sentence in ranked_sentences[:4]]

        if not selected:
            selected = [sources[0]["text"]]

        answer = " ".join(selected)
        return answer[:900].strip()
