"""
vector_db.py
Módulo para crear y gestionar la base de datos vectorial con Chroma.
Usa sentence-transformers para embeddings.
"""

import chromadb
from chromadb.config import Settings
from sentence_transformers import SentenceTransformer
from typing import List, Dict, Any, Tuple
import os


class VectorDatabase:
    """Clase para gestionar la base de datos vectorial."""
    
    def __init__(self, db_path: str = "data/chroma_db", model_name: str = "all-MiniLM-L6-v2"):
        """
        Inicializa la base de datos vectorial.
        
        Args:
            db_path: Ruta donde almacenar la BD
            model_name: Modelo de sentence-transformers a usar
        """
        self.db_path = db_path
        self.model_name = model_name
        
        # Crear carpeta si no existe
        os.makedirs(db_path, exist_ok=True)
        
        # Inicializar cliente de Chroma
        settings = Settings(
            chroma_db_impl="duckdb+parquet",
            persist_directory=db_path,
            anonymized_telemetry=False,
        )
        self.client = chromadb.Client(settings)
        
        # Cargar modelo de embeddings
        print(f"Cargando modelo: {model_name}")
        self.embedder = SentenceTransformer(model_name)
        
        # Crear colección
        self.collection = self.client.get_or_create_collection(
            name="preserv_rag",
            metadata={"hnsw:space": "cosine"}
        )
    
    def add_chunks(self, chunks: List[Dict[str, Any]]) -> None:
        """
        Añade chunks a la base de datos.
        
        Args:
            chunks: Lista de chunks con contenido y metadata
        """
        if not chunks:
            print("⚠ No hay chunks para añadir")
            return
        
        # Extraer contenidos y metadata
        ids = [chunk["id"] for chunk in chunks]
        contents = [chunk["content"] for chunk in chunks]
        
        # Preparar metadata para Chroma
        metadatas = []
        for chunk in chunks:
            metadata = {
                "source_file": chunk.get("source_file", "unknown"),
                "doc_title": chunk.get("doc_title", "unknown"),
                "chunk_length": chunk.get("length", 0),
            }
            
            # Añadir metadata extraída si existe
            if "extracted_metadata" in chunk:
                extracted = chunk["extracted_metadata"]
                if extracted.get("ph"):
                    metadata["has_ph"] = True
                if extracted.get("aw"):
                    metadata["has_aw"] = True
                if extracted.get("microorganisms"):
                    metadata["microorganisms"] = ",".join(extracted["microorganisms"][:3])
                if extracted.get("conservants"):
                    metadata["conservants"] = ",".join(extracted["conservants"][:3])
            
            metadatas.append(metadata)
        
        # Generar embeddings
        print(f"Generando embeddings para {len(contents)} chunks...")
        embeddings = self.embedder.encode(contents, show_progress_bar=True)
        
        # Convertir a lista de listas (formato esperado por Chroma)
        embeddings_list = embeddings.tolist()
        
        # Añadir a Chroma
        print("Añadiendo chunks a la base de datos...")
        self.collection.add(
            ids=ids,
            embeddings=embeddings_list,
            documents=contents,
            metadatas=metadatas,
        )
        
        print(f"✓ {len(chunks)} chunks añadidos a la BD")
    
    def search(self, query: str, n_results: int = 5) -> List[Dict[str, Any]]:
        """
        Busca chunks similares a una query.
        
        Args:
            query: Texto de búsqueda
            n_results: Número de resultados a retornar
            
        Returns:
            Lista de chunks relevantes con puntuación de similitud
        """
        # Generar embedding de la query
        query_embedding = self.embedder.encode([query])[0].tolist()
        
        # Buscar en Chroma
        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=n_results,
            include=["documents", "metadatas", "distances"]
        )
        
        # Formatear resultados
        formatted_results = []
        
        if results["ids"] and len(results["ids"]) > 0:
            for i, doc_id in enumerate(results["ids"][0]):
                # Chroma retorna distancias, convertir a similitud
                distance = results["distances"][0][i]
                similarity = 1 - distance  # Para cosine distance
                
                formatted_results.append({
                    "id": doc_id,
                    "content": results["documents"][0][i],
                    "metadata": results["metadatas"][0][i],
                    "similarity_score": round(similarity, 4),
                    "distance": round(distance, 4),
                })
        
        return formatted_results
    
    def get_collection_stats(self) -> Dict[str, Any]:
        """Retorna estadísticas de la colección."""
        count = self.collection.count()
        
        return {
            "total_chunks": count,
            "collection_name": self.collection.name,
            "model_used": self.model_name,
            "db_path": self.db_path,
        }
    
    def delete_collection(self) -> None:
        """Elimina la colección actual."""
        self.client.delete_collection(name="preserv_rag")
        print("✓ Colección eliminada")
    
    def persist(self) -> None:
        """Persiste los cambios a disco."""
        self.client.persist()
        print("✓ Base de datos persistida")
