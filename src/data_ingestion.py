"""
data_ingestion.py
Módulo para leer y cargar PDFs desde una carpeta local.
Maneja errores y retorna lista de documentos con metadata.
"""

import os
from pathlib import Path
from typing import List, Dict, Any
import PyPDF2


class PDFIngestion:
    """Clase para ingestar PDFs de una carpeta local."""
    
    def __init__(self, pdf_folder: str = "data/pdfs"):
        """
        Inicializa el ingester de PDFs.
        
        Args:
            pdf_folder: Ruta a la carpeta con PDFs
        """
        self.pdf_folder = Path(pdf_folder)
        self.documents = []
        
    def load_pdfs(self) -> List[Dict[str, Any]]:
        """
        Carga todos los PDFs de la carpeta.
        
        Returns:
            Lista de diccionarios con contenido y metadata de cada PDF
        """
        if not self.pdf_folder.exists():
            raise FileNotFoundError(f"Carpeta no encontrada: {self.pdf_folder}")
        
        pdf_files = list(self.pdf_folder.glob("*.pdf"))
        
        if not pdf_files:
            raise FileNotFoundError(f"No se encontraron PDFs en: {self.pdf_folder}")
        
        print(f"📄 Encontrados {len(pdf_files)} PDFs")
        
        for pdf_file in pdf_files:
            try:
                doc = self._read_pdf(pdf_file)
                self.documents.append(doc)
                print(f"✓ Cargado: {pdf_file.name}")
            except Exception as e:
                print(f"✗ Error al cargar {pdf_file.name}: {str(e)}")
        
        return self.documents
    
    def _read_pdf(self, pdf_path: Path) -> Dict[str, Any]:
        """
        Lee un PDF individual.
        
        Args:
            pdf_path: Ruta al archivo PDF
            
        Returns:
            Diccionario con contenido y metadata
        """
        with open(pdf_path, 'rb') as file:
            reader = PyPDF2.PdfReader(file)
            num_pages = len(reader.pages)
            
            # Extraer texto de todas las páginas
            text = ""
            for page in reader.pages:
                text += page.extract_text() + "\n"
            
            # Extraer metadata del PDF
            metadata = reader.metadata
            
            return {
                "filename": pdf_path.name,
                "path": str(pdf_path),
                "content": text,
                "num_pages": num_pages,
                "metadata": {
                    "title": metadata.get("/Title", "Unknown") if metadata else "Unknown",
                    "author": metadata.get("/Author", "Unknown") if metadata else "Unknown",
                    "creation_date": str(metadata.get("/CreationDate", "Unknown")) if metadata else "Unknown",
                }
            }
    
    def get_documents(self) -> List[Dict[str, Any]]:
        """Retorna los documentos cargados."""
        return self.documents
    
    def get_stats(self) -> Dict[str, Any]:
        """Retorna estadísticas de los documentos cargados."""
        total_pages = sum(doc["num_pages"] for doc in self.documents)
        total_chars = sum(len(doc["content"]) for doc in self.documents)
        
        return {
            "total_pdfs": len(self.documents),
            "total_pages": total_pages,
            "total_characters": total_chars,
            "avg_pages_per_pdf": total_pages / len(self.documents) if self.documents else 0,
        }
