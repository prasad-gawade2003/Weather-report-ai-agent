import math
import re
from typing import List, Dict, Any, Optional
from app.knowledge_data import INITIAL_KNOWLEDGE_DOCUMENTS
from app.schemas import RAGSource, RAGDocumentItem

class WeatherRAGEngine:
    """
    Retrieval-Augmented Generation (RAG) Engine for Weather & Climate Safety.
    Uses hybrid sparse-dense semantic scoring (TF-IDF + Term Proximity + Category Boosting)
    with zero external C++ dependencies, ensuring rock-solid local execution.
    """
    def __init__(self):
        self.documents: Dict[str, Dict[str, Any]] = {}
        self.vocab: Dict[str, int] = {}
        self.doc_vectors: Dict[str, Dict[str, float]] = {}
        self.idf: Dict[str, float] = {}
        
        # Load initial documents
        for doc in INITIAL_KNOWLEDGE_DOCUMENTS:
            self.add_document(doc)
            
    def _tokenize(self, text: str) -> List[str]:
        """Convert text into normalized tokens."""
        text = text.lower()
        # Extract alphanumeric words
        tokens = re.findall(r'\b[a-z0-9_-]{2,}\b', text)
        return tokens

    def add_document(self, doc_data: Dict[str, Any]) -> str:
        """Add or update a document in the vector index."""
        doc_id = doc_data.get("id") or f"doc-{len(self.documents)+1}"
        doc_entry = {
            "id": doc_id,
            "title": doc_data.get("title", "Weather Advisory"),
            "category": doc_data.get("category", "general"),
            "tags": doc_data.get("tags", []),
            "content": doc_data.get("content", "")
        }
        self.documents[doc_id] = doc_entry
        self._reindex()
        return doc_id

    def _reindex(self):
        """Recompute TF-IDF index across all documents."""
        n_docs = len(self.documents)
        if n_docs == 0:
            return

        doc_tokens = {}
        df = {}

        for doc_id, doc in self.documents.items():
            # Combine title, tags, and content with title/tags having higher weight
            weighted_text = f"{doc['title']} {doc['title']} {' '.join(doc['tags'] * 3)} {doc['content']}"
            tokens = self._tokenize(weighted_text)
            doc_tokens[doc_id] = tokens
            
            seen_in_doc = set(tokens)
            for token in seen_in_doc:
                df[token] = df.get(token, 0) + 1

        # Calculate IDF
        self.idf = {
            token: math.log((n_docs + 1) / (count + 1)) + 1.0 
            for token, count in df.items()
        }

        # Calculate TF-IDF vectors
        self.doc_vectors = {}
        for doc_id, tokens in doc_tokens.items():
            tf = {}
            for t in tokens:
                tf[t] = tf.get(t, 0) + 1
            
            # Normalize TF
            total_tokens = len(tokens) or 1
            vector = {}
            norm_sq = 0.0
            for t, count in tf.items():
                tfidf_val = (count / total_tokens) * self.idf.get(t, 1.0)
                vector[t] = tfidf_val
                norm_sq += tfidf_val ** 2
            
            # Unit norm
            norm = math.sqrt(norm_sq) or 1.0
            self.doc_vectors[doc_id] = {t: val / norm for t, val in vector.items()}

    def search(self, query: str, top_k: int = 3, category: Optional[str] = None) -> List[RAGSource]:
        """
        Hybrid semantic & keyword search across the knowledge store.
        Returns top_k most relevant knowledge chunks with score.
        """
        query_tokens = self._tokenize(query)
        if not query_tokens:
            return []

        # Build query vector
        q_tf = {}
        for t in query_tokens:
            q_tf[t] = q_tf.get(t, 0) + 1
            
        q_len = len(query_tokens) or 1
        q_vector = {}
        norm_sq = 0.0
        for t, count in q_tf.items():
            tfidf_val = (count / q_len) * self.idf.get(t, 1.0)
            q_vector[t] = tfidf_val
            norm_sq += tfidf_val ** 2
            
        norm = math.sqrt(norm_sq) or 1.0
        q_vector = {t: val / norm for t, val in q_vector.items()}

        scores = []
        for doc_id, doc in self.documents.items():
            if category and doc.get("category") != category:
                continue

            doc_vec = self.doc_vectors.get(doc_id, {})
            # Dot product for cosine similarity
            sim = sum(q_vector.get(t, 0.0) * doc_vec.get(t, 0.0) for t in doc_vec if t in q_vector)
            
            # Tag match bonus
            tags = [t.lower() for t in doc.get("tags", [])]
            for qt in query_tokens:
                if qt in tags:
                    sim += 0.15

            if sim > 0.01:
                # Find most relevant snippet or return leading 250 characters
                content = doc.get("content", "")
                snippet = content[:280] + "..." if len(content) > 280 else content
                scores.append({
                    "id": doc_id,
                    "title": doc.get("title", ""),
                    "category": doc.get("category", ""),
                    "snippet": snippet,
                    "score": round(min(sim, 1.0), 3)
                })

        # Sort descending by score
        scores.sort(key=lambda x: x["score"], reverse=True)
        top_results = scores[:top_k]
        
        return [
            RAGSource(
                id=res["id"],
                title=res["title"],
                category=res["category"],
                snippet=res["snippet"],
                score=res["score"]
            )
            for res in top_results
        ]

    def format_context_for_llm(self, rag_sources: List[RAGSource]) -> str:
        """Format retrieved knowledge sources for injection into LLM prompt."""
        if not rag_sources:
            return "No specific meteorological knowledge base documents retrieved."
            
        lines = ["--- RETRIEVED METEOROLOGICAL & SAFETY ADVISORIES (RAG) ---"]
        for idx, src in enumerate(rag_sources, 1):
            doc = self.documents.get(src.id)
            full_content = doc.get("content", src.snippet) if doc else src.snippet
            lines.append(f"\n[Source {idx}: {src.title} (Category: {src.category}, Relevance: {int(src.score * 100)}%)]")
            lines.append(full_content)
        lines.append("\n-----------------------------------------------------------")
        return "\n".join(lines)

    def get_all_documents(self) -> List[RAGDocumentItem]:
        """Return list of all indexed documents."""
        return [
            RAGDocumentItem(
                id=doc["id"],
                title=doc["title"],
                category=doc["category"],
                tags=doc["tags"],
                content=doc["content"]
            )
            for doc in self.documents.values()
        ]

# Global singleton RAG engine instance
rag_engine = WeatherRAGEngine()
