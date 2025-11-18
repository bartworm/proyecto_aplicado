"""
retriever.py
Módulo para recuperar documentos relevantes basado en búsqueda vectorial.
"""

from typing import List, Dict, Any
from vector_db import VectorDatabase


class SimpleRetriever:
    """Clase para realizar búsquedas en la base vectorial."""
    
    def __init__(self, vector_db: VectorDatabase):
        """
        Inicializa el retriever.
        
        Args:
            vector_db: Instancia de VectorDatabase
        """
        self.vector_db = vector_db
    
    def retrieve(self, query: str, n_results: int = 5) -> List[Dict[str, Any]]:
        """
        Recupera documentos relevantes para una query.
        
        Args:
            query: Texto de búsqueda
            n_results: Número de resultados
            
        Returns:
            Lista de documentos relevantes
        """
        results = self.vector_db.search(query, n_results=n_results)
        return results
    
    def retrieve_with_threshold(self, query: str, threshold: float = 0.3, n_results: int = 10) -> List[Dict[str, Any]]:
        """
        Recupera documentos con puntuación mínima.
        
        Args:
            query: Texto de búsqueda
            threshold: Puntuación mínima de similitud (0-1)
            n_results: Máximo número de resultados
            
        Returns:
            Lista de documentos sobre el threshold
        """
        results = self.vector_db.search(query, n_results=n_results)
        
        # Filtrar por threshold
        filtered = [r for r in results if r["similarity_score"] >= threshold]
        
        return filtered
    
    def retrieve_by_source(self, query: str, source_file: str, n_results: int = 5) -> List[Dict[str, Any]]:
        """
        Recupera documentos de una fuente específica.
        
        Args:
            query: Texto de búsqueda
            source_file: Nombre del archivo fuente
            n_results: Número de resultados
            
        Returns:
            Lista de documentos de la fuente
        """
        all_results = self.vector_db.search(query, n_results=n_results * 2)
        
        # Filtrar por fuente
        filtered = [r for r in all_results if r["metadata"].get("source_file") == source_file]
        
        return filtered[:n_results]
    
    def retrieve_with_metadata(self, query: str, metadata_filter: Dict[str, Any], n_results: int = 5) -> List[Dict[str, Any]]:
        """
        Recupera documentos con filtro de metadata.
        
        Args:
            query: Texto de búsqueda
            metadata_filter: Dict con condiciones (ej: {"has_ph": True})
            n_results: Número de resultados
            
        Returns:
            Lista de documentos filtrados
        """
        all_results = self.vector_db.search(query, n_results=n_results * 3)
        
        # Filtrar por metadata
        filtered = []
        for result in all_results:
            metadata = result["metadata"]
            match = True
            
            for key, value in metadata_filter.items():
                if key not in metadata or metadata[key] != value:
                    match = False
                    break
            
            if match:
                filtered.append(result)
        
        return filtered[:n_results]
    
    def get_retriever_stats(self, queries: List[str] = None) -> Dict[str, Any]:
        """
        Retorna estadísticas del retriever.
        
        Args:
            queries: Lista de queries para probar (opcional)
            
        Returns:
            Estadísticas
        """
        stats = {
            "vector_db_stats": self.vector_db.get_collection_stats(),
            "retriever_type": "SimpleRetriever",
        }
        
        if queries:
            avg_results = 0
            avg_similarity = 0
            
            for query in queries:
                results = self.retrieve(query)
                avg_results += len(results)
                if results:
                    avg_similarity += sum(r["similarity_score"] for r in results) / len(results)
            
            stats["avg_results_per_query"] = round(avg_results / len(queries), 2)
            stats["avg_similarity_score"] = round(avg_similarity / len(queries), 4)
        
        return stats
