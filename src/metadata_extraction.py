"""
metadata_extraction.py
Módulo para extraer metadata relevante (pH, aW, microorganismo, etc.) de chunks.
"""

import re
from typing import List, Dict, Any, Optional


class MetadataExtractor:
    """Clase para extraer metadata de chunks de texto."""
    
    def __init__(self):
        """Inicializa el extractor."""
        self.microorganisms = [
            "Zygosaccharomyces bailii",
            "E. coli",
            "Salmonella",
            "Listeria",
            "Staphylococcus aureus",
            "Clostridium",
            "Pseudomonas",
            "Bacillus",
            "levadura",
            "bacteria",
            "hongo",
            "moho",
            "patógeno",
        ]
    
    def extract_ph_range(self, text: str) -> Optional[Dict[str, float]]:
        """
        Extrae valores de pH del texto.
        
        Args:
            text: Texto a analizar
            
        Returns:
            Dict con pH min y max, o None
        """
        # Patrones comunes: pH 4.0, pH between 3.5-4.5, etc.
        patterns = [
            r'pH\s*(?:=|:|between|of)?\s*(\d+\.?\d*)\s*(?:–|-|to)?\s*(\d+\.?\d*)',
            r'pH\s*(?:=|:|of)?\s*(\d+\.?\d*)',
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            if matches:
                if len(matches[0]) == 2:  # Rango
                    try:
                        return {
                            "ph_min": float(matches[0][0]),
                            "ph_max": float(matches[0][1]),
                        }
                    except ValueError:
                        continue
                else:  # Valor único
                    try:
                        ph_val = float(matches[0])
                        return {"ph_value": ph_val}
                    except (ValueError, TypeError):
                        continue
        
        return None
    
    def extract_aw(self, text: str) -> Optional[Dict[str, float]]:
        """
        Extrae valores de actividad de agua (aW) del texto.
        
        Args:
            text: Texto a analizar
            
        Returns:
            Dict con aW min y max, o None
        """
        # Patrones: aW 0.95, water activity 0.97, aw between 0.9-0.95
        patterns = [
            r'(?:aW|aw|water\s*activity)\s*(?:=|:|between|of)?\s*(0\.\d+)\s*(?:–|-|to)?\s*(0\.\d+)',
            r'(?:aW|aw|water\s*activity)\s*(?:=|:|of)?\s*(0\.\d+)',
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            if matches:
                if len(matches[0]) == 2:  # Rango
                    try:
                        return {
                            "aw_min": float(matches[0][0]),
                            "aw_max": float(matches[0][1]),
                        }
                    except ValueError:
                        continue
                else:  # Valor único
                    try:
                        aw_val = float(matches[0])
                        return {"aw_value": aw_val}
                    except (ValueError, TypeError):
                        continue
        
        return None
    
    def extract_concentration(self, text: str) -> Optional[Dict[str, Any]]:
        """
        Extrae concentraciones de conservantes.
        
        Args:
            text: Texto a analizar
            
        Returns:
            Dict con concentración y unidad
        """
        # Patrones: 500 ppm, 1000 mg/kg, 0.5%, etc.
        patterns = [
            r'(\d+\.?\d*)\s*(ppm|mg/kg|%|g/kg|µL/g)',
        ]
        
        matches = re.findall(patterns[0], text, re.IGNORECASE)
        
        if matches:
            return {
                "concentration_value": float(matches[0][0]),
                "concentration_unit": matches[0][1],
            }
        
        return None
    
    def extract_microorganism(self, text: str) -> Optional[List[str]]:
        """
        Extrae microorganismos mencionados en el texto.
        
        Args:
            text: Texto a analizar
            
        Returns:
            Lista de microorganismos encontrados
        """
        found = []
        
        for organism in self.microorganisms:
            if organism.lower() in text.lower():
                found.append(organism)
        
        return found if found else None
    
    def extract_conservant(self, text: str) -> Optional[List[str]]:
        """
        Extrae nombres de conservantes mencionados.
        
        Args:
            text: Texto a analizar
            
        Returns:
            Lista de conservantes encontrados
        """
        conservants = [
            "benzoato",
            "sorbato",
            "nisina",
            "extracto",
            "aceite esencial",
            "essential oil",
            "eugenol",
            "carvacrol",
            "timol",
            "ácido sórbico",
            "ácido benzoico",
        ]
        
        found = []
        for conservant in conservants:
            if conservant.lower() in text.lower():
                found.append(conservant)
        
        return found if found else None
    
    def extract_chunk_metadata(self, chunk: Dict[str, Any]) -> Dict[str, Any]:
        """
        Extrae toda la metadata relevante de un chunk.
        
        Args:
            chunk: Chunk a procesar
            
        Returns:
            Chunk con metadata extraída
        """
        text = chunk.get("content", "")
        
        metadata = {
            "ph": self.extract_ph_range(text),
            "aw": self.extract_aw(text),
            "concentration": self.extract_concentration(text),
            "microorganisms": self.extract_microorganism(text),
            "conservants": self.extract_conservant(text),
            "has_numeric_data": bool(self.extract_concentration(text)),
        }
        
        return {
            **chunk,
            "extracted_metadata": metadata,
        }
    
    def process_chunks(self, chunks: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Procesa una lista de chunks extrayendo metadata.
        
        Args:
            chunks: Chunks a procesar
            
        Returns:
            Chunks con metadata extraída
        """
        processed_chunks = []
        
        for chunk in chunks:
            processed = self.extract_chunk_metadata(chunk)
            processed_chunks.append(processed)
        
        return processed_chunks
    
    def get_stats(self, chunks: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Retorna estadísticas de extracción de metadata."""
        chunks_with_ph = sum(1 for c in chunks if c.get("extracted_metadata", {}).get("ph"))
        chunks_with_aw = sum(1 for c in chunks if c.get("extracted_metadata", {}).get("aw"))
        chunks_with_microorg = sum(1 for c in chunks if c.get("extracted_metadata", {}).get("microorganisms"))
        chunks_with_conservants = sum(1 for c in chunks if c.get("extracted_metadata", {}).get("conservants"))
        
        return {
            "total_chunks": len(chunks),
            "chunks_with_ph": chunks_with_ph,
            "chunks_with_aw": chunks_with_aw,
            "chunks_with_microorganisms": chunks_with_microorg,
            "chunks_with_conservants": chunks_with_conservants,
            "metadata_coverage_pct": round((chunks_with_ph + chunks_with_aw + chunks_with_microorg + chunks_with_conservants) / (len(chunks) * 4) * 100, 2) if chunks else 0,
        }
