"""
chunking.py
Módulo para dividir documentos en chunks manejables.
Mantiene contexto y solapamiento entre chunks.
"""

from typing import List, Dict, Any


class DocumentChunker:
    """Clase para dividir documentos en chunks."""
    
    def __init__(self, chunk_size: int = 500, overlap: int = 50):
        """
        Inicializa el chunker.
        
        Args:
            chunk_size: Número de caracteres por chunk
            overlap: Número de caracteres solapados entre chunks
        """
        self.chunk_size = chunk_size
        self.overlap = overlap
    
    def chunk_text(self, text: str, chunk_id_prefix: str = "") -> List[Dict[str, Any]]:
        """
        Divide un texto en chunks con solapamiento.
        
        Args:
            text: Texto a dividir
            chunk_id_prefix: Prefijo para IDs de chunks
            
        Returns:
            Lista de chunks
        """
        chunks = []
        start = 0
        chunk_count = 0
        
        while start < len(text):
            # Definir fin del chunk
            end = min(start + self.chunk_size, len(text))
            
            # Intentar cortar en un límite sensato (punto, párrafo)
            if end < len(text):
                # Buscar último punto o salto de línea
                last_period = text.rfind('.', start, end)
                last_newline = text.rfind('\n', start, end)
                
                if last_period > start:
                    end = last_period + 1
                elif last_newline > start:
                    end = last_newline + 1
            
            chunk_text = text[start:end].strip()
            
            if chunk_text:  # Solo añadir si no está vacío
                chunks.append({
                    "id": f"{chunk_id_prefix}_chunk_{chunk_count}",
                    "content": chunk_text,
                    "start_char": start,
                    "end_char": end,
                    "length": len(chunk_text),
                })
                chunk_count += 1
            
            # Mover al siguiente chunk con solapamiento
            start = end - self.overlap
        
        return chunks
    
    def chunk_documents(self, documents: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Divide una lista de documentos en chunks.
        
        Args:
            documents: Documentos a procesar
            
        Returns:
            Lista de chunks con metadata del documento origen
        """
        all_chunks = []
        
        for doc in documents:
            doc_chunks = self.chunk_text(
                doc["content"],
                chunk_id_prefix=doc["filename"].replace(".pdf", "")
            )
            
            # Añadir metadata del documento a cada chunk
            for chunk in doc_chunks:
                chunk.update({
                    "source_file": doc["filename"],
                    "source_path": doc["path"],
                    "doc_title": doc["metadata"].get("title", "Unknown"),
                    "doc_author": doc["metadata"].get("author", "Unknown"),
                })
                all_chunks.append(chunk)
        
        return all_chunks
    
    def get_stats(self, chunks: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Retorna estadísticas de chunking."""
        if not chunks:
            return {"total_chunks": 0, "avg_chunk_size": 0}
        
        total_chunks = len(chunks)
        avg_size = sum(chunk["length"] for chunk in chunks) / total_chunks
        min_size = min(chunk["length"] for chunk in chunks)
        max_size = max(chunk["length"] for chunk in chunks)
        
        # Contar documentos únicos
        unique_docs = len(set(chunk["source_file"] for chunk in chunks))
        
        return {
            "total_chunks": total_chunks,
            "unique_documents": unique_docs,
            "avg_chunk_size": round(avg_size, 2),
            "min_chunk_size": min_size,
            "max_chunk_size": max_size,
            "chunks_per_document": round(total_chunks / unique_docs, 2) if unique_docs > 0 else 0,
        }
