"""
benchmark.py
Módulo para evaluar el rendimiento del sistema RAG.
Calcula métricas como Precision, Recall, MRR, etc.
"""

from typing import List, Dict, Any, Tuple
import numpy as np


class RAGBenchmark:
    """Clase para evaluar el rendimiento del RAG."""
    
    def __init__(self, retriever):
        """
        Inicializa el benchmark.
        
        Args:
            retriever: Instancia del retriever
        """
        self.retriever = retriever
        self.results = []
    
    def calculate_precision_at_k(self, retrieved: List[Dict], relevant: List[str], k: int = 5) -> float:
        """
        Calcula Precision@K.
        
        Args:
            retrieved: Lista de documentos recuperados
            relevant: Lista de IDs relevantes esperados
            k: Número de top resultados a considerar
            
        Returns:
            Precision@K (0-1)
        """
        retrieved_ids = [r["id"] for r in retrieved[:k]]
        relevant_retrieved = sum(1 for rid in retrieved_ids if rid in relevant)
        
        return relevant_retrieved / k if k > 0 else 0
    
    def calculate_recall_at_k(self, retrieved: List[Dict], relevant: List[str], k: int = 5) -> float:
        """
        Calcula Recall@K.
        
        Args:
            retrieved: Lista de documentos recuperados
            relevant: Lista de IDs relevantes esperados
            k: Número de top resultados a considerar
            
        Returns:
            Recall@K (0-1)
        """
        retrieved_ids = [r["id"] for r in retrieved[:k]]
        relevant_retrieved = sum(1 for rid in retrieved_ids if rid in relevant)
        
        return relevant_retrieved / len(relevant) if len(relevant) > 0 else 0
    
    def calculate_mrr(self, retrieved: List[Dict], relevant: List[str]) -> float:
        """
        Calcula Mean Reciprocal Rank.
        
        Args:
            retrieved: Lista de documentos recuperados
            relevant: Lista de IDs relevantes esperados
            
        Returns:
            MRR (0-1)
        """
        for rank, result in enumerate(retrieved, 1):
            if result["id"] in relevant:
                return 1 / rank
        
        return 0
    
    def calculate_ndcg(self, retrieved: List[Dict], relevant: List[str], k: int = 5) -> float:
        """
        Calcula Normalized Discounted Cumulative Gain.
        
        Args:
            retrieved: Lista de documentos recuperados
            relevant: Lista de IDs relevantes esperados
            k: Número de top resultados
            
        Returns:
            NDCG@K (0-1)
        """
        # DCG
        dcg = 0
        for rank, result in enumerate(retrieved[:k], 1):
            if result["id"] in relevant:
                dcg += 1 / np.log2(rank + 1)
        
        # Ideal DCG
        idcg = sum(1 / np.log2(rank + 1) for rank in range(1, min(len(relevant), k) + 1))
        
        return dcg / idcg if idcg > 0 else 0
    
    def evaluate_query(self, query: str, relevant_ids: List[str], k: int = 5) -> Dict[str, Any]:
        """
        Evalúa una single query.
        
        Args:
            query: Texto de búsqueda
            relevant_ids: IDs de documentos relevantes
            k: Top-K a considerar
            
        Returns:
            Diccionario con métricas
        """
        retrieved = self.retriever.retrieve(query, n_results=k * 2)
        
        metrics = {
            "query": query,
            "num_relevant": len(relevant_ids),
            "num_retrieved": len(retrieved),
            "precision_at_5": self.calculate_precision_at_k(retrieved, relevant_ids, k=5),
            "precision_at_10": self.calculate_precision_at_k(retrieved, relevant_ids, k=10),
            "recall_at_5": self.calculate_recall_at_k(retrieved, relevant_ids, k=5),
            "recall_at_10": self.calculate_recall_at_k(retrieved, relevant_ids, k=10),
            "mrr": self.calculate_mrr(retrieved, relevant_ids),
            "ndcg_at_5": self.calculate_ndcg(retrieved, relevant_ids, k=5),
            "ndcg_at_10": self.calculate_ndcg(retrieved, relevant_ids, k=10),
            "avg_similarity_score": np.mean([r["similarity_score"] for r in retrieved]) if retrieved else 0,
        }
        
        self.results.append(metrics)
        return metrics
    
    def evaluate_multiple_queries(self, query_relevance_pairs: List[Tuple[str, List[str]]]) -> Dict[str, Any]:
        """
        Evalúa múltiples queries.
        
        Args:
            query_relevance_pairs: Lista de (query, relevant_ids)
            
        Returns:
            Métricas agregadas
        """
        for query, relevant_ids in query_relevance_pairs:
            self.evaluate_query(query, relevant_ids)
        
        return self.get_aggregated_metrics()
    
    def get_aggregated_metrics(self) -> Dict[str, Any]:
        """
        Retorna métricas agregadas de todas las evaluaciones.
        
        Returns:
            Diccionario con métricas promedio
        """
        if not self.results:
            return {"error": "No results to aggregate"}
        
        n_queries = len(self.results)
        
        aggregated = {
            "total_queries": n_queries,
            "avg_precision_at_5": np.mean([r["precision_at_5"] for r in self.results]),
            "avg_precision_at_10": np.mean([r["precision_at_10"] for r in self.results]),
            "avg_recall_at_5": np.mean([r["recall_at_5"] for r in self.results]),
            "avg_recall_at_10": np.mean([r["recall_at_10"] for r in self.results]),
            "avg_mrr": np.mean([r["mrr"] for r in self.results]),
            "avg_ndcg_at_5": np.mean([r["ndcg_at_5"] for r in self.results]),
            "avg_ndcg_at_10": np.mean([r["ndcg_at_10"] for r in self.results]),
            "avg_similarity_score": np.mean([r["avg_similarity_score"] for r in self.results]),
        }
        
        # Redondear a 4 decimales
        for key in aggregated:
            if isinstance(aggregated[key], float):
                aggregated[key] = round(aggregated[key], 4)
        
        return aggregated
    
    def get_results_dataframe(self):
        """Retorna resultados como pandas DataFrame."""
        try:
            import pandas as pd
            return pd.DataFrame(self.results)
        except ImportError:
            return None
