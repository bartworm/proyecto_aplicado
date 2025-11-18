"""
text_extraction.py
Módulo para limpiar y normalizar texto extraído de PDFs.
"""

import re
from typing import List, Dict, Any


class TextExtractor:
    """Clase para limpiar y normalizar texto."""
    
    def __init__(self):
        """Inicializa el extractor."""
        pass
    
    def clean_text(self, text: str) -> str:
        """
        Limpia el texto extraído de PDFs.
        
        Args:
            text: Texto crudo
            
        Returns:
            Texto limpio y normalizado
        """
        # Eliminar saltos de línea múltiples
        text = re.sub(r'\n\n+', '\n', text)
        
        # Eliminar espacios en blanco múltiples
        text = re.sub(r' +', ' ', text)
        
        # Eliminar caracteres especiales problemáticos
        text = re.sub(r'[\x00-\x08\x0B\x0C\x0E-\x1F\x7F-\x9F]', '', text)
        
        # Normalizar espacios alrededor de puntuación
        text = re.sub(r' +([.,;:!?])', r'\1', text)
        
        # Eliminar URLs
        text = re.sub(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', '', text)
        
        # Eliminar emails
        text = re.sub(r'\S+@\S+', '', text)
        
        # Eliminar números de página (patrón común)
        text = re.sub(r'^\s*\d+\s*$', '', text, flags=re.MULTILINE)
        
        # Strip
        text = text.strip()
        
        return text
    
    def extract_references(self, text: str) -> List[str]:
        """
        Extrae referencias bibliográficas del texto.
        
        Args:
            text: Texto que contiene referencias
            
        Returns:
            Lista de referencias encontradas
        """
        # Patrón simple para detectar referencias (mejorarlo según formato)
        pattern = r'\[.*?\]|\(.*?20\d{2}.*?\)|doi:.*'
        references = re.findall(pattern, text)
        return references
    
    def extract_numbers(self, text: str) -> List[float]:
        """
        Extrae números del texto.
        
        Args:
            text: Texto a analizar
            
        Returns:
            Lista de números encontrados
        """
        pattern = r'\d+\.?\d*'
        numbers = [float(m) for m in re.findall(pattern, text)]
        return numbers
    
    def process_documents(self, documents: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Procesa una lista de documentos.
        
        Args:
            documents: Documentos cargados
            
        Returns:
            Documentos con texto limpio
        """
        processed = []
        
        for doc in documents:
            cleaned_content = self.clean_text(doc["content"])
            
            processed.append({
                **doc,
                "content": cleaned_content,
                "content_cleaned": True,
                "length_original": len(doc["content"]),
                "length_cleaned": len(cleaned_content),
                "references": self.extract_references(doc["content"]),
            })
        
        return processed
    
    def get_stats(self, documents: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Retorna estadísticas de limpieza."""
        total_original = sum(doc.get("length_original", 0) for doc in documents)
        total_cleaned = sum(doc.get("length_cleaned", 0) for doc in documents)
        reduction = ((total_original - total_cleaned) / total_original * 100) if total_original > 0 else 0
        
        return {
            "total_original_chars": total_original,
            "total_cleaned_chars": total_cleaned,
            "reduction_percentage": round(reduction, 2),
            "documents_processed": len(documents),
        }
