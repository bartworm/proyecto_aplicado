"""
run_pipeline.py
Script para ejecutar el pipeline completo sin interfaz gráfica.
Útil para procesamiento batch.
"""

import sys
from pathlib import Path

# Agregar src al path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from data_ingestion import PDFIngestion
from text_extraction import TextExtractor
from chunking import DocumentChunker
from metadata_extraction import MetadataExtractor
from vector_db import VectorDatabase
from retriever import SimpleRetriever
from benchmark import RAGBenchmark


def main():
    """Ejecuta el pipeline completo."""
    
    print("=" * 60)
    print("🧬 PRESERV-RAG - PIPELINE BASELINE (HITO 1)")
    print("=" * 60)
    
    # Configuración
    pdf_folder = "data/pdfs"
    db_path = "data/chroma_db"
    chunk_size = 500
    overlap = 50
    
    # 1. INGESTA
    print("\n1️⃣  INGESTA DE PDFs")
    print("-" * 60)
    try:
        ingestion = PDFIngestion(pdf_folder=pdf_folder)
        documents = ingestion.load_pdfs()
        ingest_stats = ingestion.get_stats()
        
        print(f"✓ {ingest_stats['total_pdfs']} PDFs cargados")
        print(f"  - Total páginas: {ingest_stats['total_pages']}")
        print(f"  - Total caracteres: {ingest_stats['total_characters']:,}")
    except Exception as e:
        print(f"✗ Error en ingesta: {str(e)}")
        return
    
    # 2. EXTRACCIÓN DE TEXTO
    print("\n2️⃣  EXTRACCIÓN Y LIMPIEZA DE TEXTO")
    print("-" * 60)
    try:
        extractor = TextExtractor()
        cleaned_docs = extractor.process_documents(documents)
        extract_stats = extractor.get_stats(cleaned_docs)
        
        print("✓ Texto limpiado y normalizado")
        print(f"  - Reducción de caracteres: {extract_stats['reduction_percentage']}%")
        print(f"  - Caracteres originales: {extract_stats['total_original_chars']:,}")
        print(f"  - Caracteres limpios: {extract_stats['total_cleaned_chars']:,}")
    except Exception as e:
        print(f"✗ Error en extracción: {str(e)}")
        return
    
    # 3. CHUNKING
    print("\n3️⃣  DIVISIÓN EN CHUNKS")
    print("-" * 60)
    try:
        chunker = DocumentChunker(chunk_size=chunk_size, overlap=overlap)
        chunks = chunker.chunk_documents(cleaned_docs)
        chunking_stats = chunker.get_stats(chunks)
        
        print("✓ Documentos divididos en chunks")
        print(f"  - Total chunks: {chunking_stats['total_chunks']}")
        print(f"  - Documentos únicos: {chunking_stats['unique_documents']}")
        print(f"  - Tamaño promedio: {chunking_stats['avg_chunk_size']} caracteres")
        print(f"  - Chunks por documento: {chunking_stats['chunks_per_document']}")
    except Exception as e:
        print(f"✗ Error en chunking: {str(e)}")
        return
    
    # 4. EXTRACCIÓN DE METADATA
    print("\n4️⃣  EXTRACCIÓN DE METADATA")
    print("-" * 60)
    try:
        metadata_extractor = MetadataExtractor()
        chunks_with_metadata = metadata_extractor.process_chunks(chunks)
        metadata_stats = metadata_extractor.get_stats(chunks_with_metadata)
        
        print("✓ Metadata extraída de chunks")
        print(f"  - Chunks con pH: {metadata_stats['chunks_with_ph']}")
        print(f"  - Chunks con aW: {metadata_stats['chunks_with_aw']}")
        print(f"  - Chunks con microorganismos: {metadata_stats['chunks_with_microorganisms']}")
        print(f"  - Chunks con conservantes: {metadata_stats['chunks_with_conservants']}")
        print(f"  - Cobertura de metadata: {metadata_stats['metadata_coverage_pct']}%")
    except Exception as e:
        print(f"✗ Error en extracción de metadata: {str(e)}")
        return
    
    # 5. VECTORIZACIÓN
    print("\n5️⃣  VECTORIZACIÓN E INDEXACIÓN")
    print("-" * 60)
    try:
        vdb = VectorDatabase(db_path=db_path, model_name="all-MiniLM-L6-v2")
        vdb.add_chunks(chunks_with_metadata)
        vdb_stats = vdb.get_collection_stats()
        
        print("✓ Base vectorial creada")
        print(f"  - Total chunks indexados: {vdb_stats['total_chunks']}")
        print(f"  - Modelo usado: {vdb_stats['model_used']}")
        print(f"  - Ruta BD: {vdb_stats['db_path']}")
    except Exception as e:
        print(f"✗ Error en vectorización: {str(e)}")
        return
    
    # 6. BÚSQUEDA DE PRUEBA
    print("\n6️⃣  BÚSQUEDA DE PRUEBA")
    print("-" * 60)
    try:
        retriever = SimpleRetriever(vdb)
        
        test_queries = [
            "Benzoato alternativa natural pH 4.2 levaduras",
            "Sorbato extracto plantas conservante",
            "Nisina microorganismo inhibición",
        ]
        
        for i, query in enumerate(test_queries, 1):
            print(f"\nQuery {i}: {query}")
            results = retriever.retrieve(query, n_results=3)
            
            if results:
                for j, result in enumerate(results, 1):
                    print(f"  {j}. [Similitud: {result['similarity_score']:.4f}] {result['content'][:100]}...")
            else:
                print("  No se encontraron resultados")
    except Exception as e:
        print(f"✗ Error en búsqueda: {str(e)}")
        return
    
    # 7. RESUMEN FINAL
    print("\n" + "=" * 60)
    print("✅ PIPELINE COMPLETADO EXITOSAMENTE")
    print("=" * 60)
    print("\n📊 RESUMEN DEL PIPELINE:")
    print(f"  - PDFs procesados: {ingest_stats['total_pdfs']}")
    print(f"  - Chunks creados: {chunking_stats['total_chunks']}")
    print(f"  - Chunks indexados: {vdb_stats['total_chunks']}")
    print(f"  - Metadata extraída: {metadata_stats['metadata_coverage_pct']}%")
    print(f"\n🎯 Para usar la interfaz gráfica:")
    print("  streamlit run streamlit_app.py")
    print(f"\n📁 Archivos generados:")
    print(f"  - Base vectorial: {db_path}")


if __name__ == "__main__":
    main()
