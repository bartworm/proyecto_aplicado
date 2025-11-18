"""
examples.py
Ejemplos de cómo usar Preserv-RAG programáticamente.
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


# ============================================================================
# EJEMPLO 1: Pipeline Completo Básico
# ============================================================================

def ejemplo_1_pipeline_basico():
    """Pipeline completo de ingesta a búsqueda."""
    
    print("\n" + "="*60)
    print("EJEMPLO 1: Pipeline Básico")
    print("="*60)
    
    # 1. Ingesta
    ingestion = PDFIngestion(pdf_folder="data/pdfs")
    documents = ingestion.load_pdfs()
    print(f"✓ Cargados {len(documents)} PDFs")
    
    # 2. Limpieza
    extractor = TextExtractor()
    cleaned_docs = extractor.process_documents(documents)
    print(f"✓ Texto limpiado")
    
    # 3. Chunking
    chunker = DocumentChunker(chunk_size=500, overlap=50)
    chunks = chunker.chunk_documents(cleaned_docs)
    print(f"✓ {len(chunks)} chunks creados")
    
    # 4. Metadata
    metadata_extractor = MetadataExtractor()
    chunks_with_metadata = metadata_extractor.process_chunks(chunks)
    print(f"✓ Metadata extraída")
    
    # 5. Vectorización
    vdb = VectorDatabase(db_path="data/chroma_db")
    vdb.add_chunks(chunks_with_metadata)
    print(f"✓ Base vectorial creada")
    
    # 6. Búsqueda
    retriever = SimpleRetriever(vdb)
    results = retriever.retrieve("benzoato alternativa natural", n_results=3)
    
    print(f"\n✓ Búsqueda completada: {len(results)} resultados\n")
    for i, result in enumerate(results, 1):
        print(f"{i}. Similitud: {result['similarity_score']:.4f}")
        print(f"   Fuente: {result['metadata']['source_file']}")
        print(f"   Contenido: {result['content'][:100]}...\n")


# ============================================================================
# EJEMPLO 2: Búsqueda con Filtros
# ============================================================================

def ejemplo_2_busqueda_filtrada():
    """Búsqueda con filtros de metadata."""
    
    print("\n" + "="*60)
    print("EJEMPLO 2: Búsqueda con Filtros")
    print("="*60)
    
    # Cargar BD existente
    vdb = VectorDatabase(db_path="data/chroma_db")
    retriever = SimpleRetriever(vdb)
    
    # Búsqueda simple
    print("\n📌 Búsqueda 1: Top-5 resultados")
    results = retriever.retrieve("Zygosaccharomyces levadura", n_results=5)
    print(f"Encontrados {len(results)} resultados")
    
    # Búsqueda con threshold
    print("\n📌 Búsqueda 2: Con umbral de similitud > 0.5")
    results = retriever.retrieve_with_threshold(
        "pH aW conservante natural",
        threshold=0.5,
        n_results=10
    )
    print(f"Encontrados {len(results)} resultados sobre threshold")
    
    # Búsqueda por fuente específica
    print("\n📌 Búsqueda 3: Solo de un PDF específico")
    results = retriever.retrieve_by_source(
        "alternativa benzoato",
        source_file="FTB-61-212.pdf",
        n_results=5
    )
    print(f"Encontrados {len(results)} resultados en FTB-61-212.pdf")


# ============================================================================
# EJEMPLO 3: Extracción de Metadata Detallada
# ============================================================================

def ejemplo_3_metadata_detallada():
    """Analizar metadata extraída."""
    
    print("\n" + "="*60)
    print("EJEMPLO 3: Metadata Detallada")
    print("="*60)
    
    # Cargar chunks con metadata
    ingestion = PDFIngestion(pdf_folder="data/pdfs")
    documents = ingestion.load_pdfs()
    
    extractor = TextExtractor()
    cleaned_docs = extractor.process_documents(documents)
    
    chunker = DocumentChunker(chunk_size=500, overlap=50)
    chunks = chunker.chunk_documents(cleaned_docs)
    
    metadata_extractor = MetadataExtractor()
    chunks_with_metadata = metadata_extractor.process_chunks(chunks)
    
    # Analizar chunks con datos relevantes
    print("\n📊 Chunks con datos relevantes:\n")
    
    for chunk in chunks_with_metadata[:5]:  # Primeros 5
        metadata = chunk.get("extracted_metadata", {})
        
        print(f"ID: {chunk['id']}")
        print(f"Fuente: {chunk['source_file']}")
        
        if metadata.get("ph"):
            print(f"  pH: {metadata['ph']}")
        
        if metadata.get("aw"):
            print(f"  aW: {metadata['aw']}")
        
        if metadata.get("microorganisms"):
            print(f"  Microorganismos: {', '.join(metadata['microorganisms'])}")
        
        if metadata.get("conservants"):
            print(f"  Conservantes: {', '.join(metadata['conservants'])}")
        
        print()


# ============================================================================
# EJEMPLO 4: Benchmarking y Evaluación
# ============================================================================

def ejemplo_4_benchmarking():
    """Evaluar el sistema con queries de prueba."""
    
    print("\n" + "="*60)
    print("EJEMPLO 4: Benchmarking")
    print("="*60)
    
    vdb = VectorDatabase(db_path="data/chroma_db")
    retriever = SimpleRetriever(vdb)
    benchmark = RAGBenchmark(retriever)
    
    # Queries de prueba con IDs relevantes (simulado)
    test_queries = [
        ("benzoato alternativa natural pH 4", ["chunk_0", "chunk_5"]),
        ("sorbato extractos plantas antimicrobiano", ["chunk_10", "chunk_15"]),
        ("nisina levadura inhibición", ["chunk_20", "chunk_25"]),
    ]
    
    # Evaluar
    print("\nEvaluando queries...")
    aggregated = benchmark.evaluate_multiple_queries(test_queries)
    
    # Mostrar resultados
    print("\n📊 Resultados del Benchmark:")
    print(f"  Total queries: {aggregated['total_queries']}")
    print(f"  Precision@5: {aggregated['avg_precision_at_5']:.4f}")
    print(f"  Recall@5: {aggregated['avg_recall_at_5']:.4f}")
    print(f"  MRR: {aggregated['avg_mrr']:.4f}")
    print(f"  NDCG@5: {aggregated['avg_ndcg_at_5']:.4f}")
    print(f"  Similitud promedio: {aggregated['avg_similarity_score']:.4f}")


# ============================================================================
# EJEMPLO 5: Caso de Uso Real - Recomendación de Conservantes
# ============================================================================

def ejemplo_5_caso_real():
    """Caso de uso real: Recomendación de alternativa a conservante."""
    
    print("\n" + "="*60)
    print("EJEMPLO 5: Caso de Uso Real")
    print("="*60)
    
    # Problema del usuario
    problema = """
    Necesito reemplazar 800 ppm de Benzoato de Sodio en una salsa con pH 4.2 
    y aW 0.97. El objetivo es inhibir levaduras osmotolerantes 
    (como Zygosaccharomyces bailii).
    """
    
    print(f"\n🔍 PROBLEMA DEL USUARIO:{problema}\n")
    
    # Cargar sistema
    vdb = VectorDatabase(db_path="data/chroma_db")
    retriever = SimpleRetriever(vdb)
    
    # Consultas derivadas del problema
    consultas = [
        "benzoato reemplazo alternativa natural",
        "pH 4.2 aW 0.97 conservante",
        "Zygosaccharomyces bailii levadura inhibición",
        "alternativa sorbato extracto plantas",
        "nisina concentración eficacia",
    ]
    
    print("📌 BÚSQUEDAS REALIZADAS:\n")
    
    all_results = []
    for i, consulta in enumerate(consultas, 1):
        results = retriever.retrieve(consulta, n_results=3)
        all_results.extend(results)
        print(f"{i}. '{consulta}'")
        print(f"   → {len(results)} resultados encontrados\n")
    
    # Consolidar y mostrar top resultados únicos
    print("📊 TOP-5 RESULTADOS CONSOLIDADOS:\n")
    
    # Eliminar duplicados basados en ID
    unique_results = {r['id']: r for r in all_results}.values()
    sorted_results = sorted(unique_results, key=lambda x: x['similarity_score'], reverse=True)
    
    for i, result in enumerate(sorted_results[:5], 1):
        print(f"{i}. [Similitud: {result['similarity_score']:.4f}]")
        print(f"   Fuente: {result['metadata']['source_file']}")
        print(f"   Contenido: {result['content'][:150]}...\n")
    
    print("💡 INTERPRETACIÓN:")
    print("   Los resultados mostrarían estudios sobre alternativas naturales")
    print("   a benzoato en condiciones similares (pH bajo, aW alta) contra levaduras")


# ============================================================================
# EJEMPLO 6: Análisis de Cobertura de Metadata
# ============================================================================

def ejemplo_6_cobertura_metadata():
    """Analizar qué porcentaje de chunks tiene metadata relevante."""
    
    print("\n" + "="*60)
    print("EJEMPLO 6: Cobertura de Metadata")
    print("="*60)
    
    # Procesar pipeline
    ingestion = PDFIngestion(pdf_folder="data/pdfs")
    documents = ingestion.load_pdfs()
    
    extractor = TextExtractor()
    cleaned_docs = extractor.process_documents(documents)
    
    chunker = DocumentChunker(chunk_size=500, overlap=50)
    chunks = chunker.chunk_documents(cleaned_docs)
    
    metadata_extractor = MetadataExtractor()
    chunks_with_metadata = metadata_extractor.process_chunks(chunks)
    
    stats = metadata_extractor.get_stats(chunks_with_metadata)
    
    print(f"\n📈 Estadísticas de Cobertura:")
    print(f"  Total chunks: {stats['total_chunks']}")
    print(f"  Con pH: {stats['chunks_with_ph']} ({stats['chunks_with_ph']/stats['total_chunks']*100:.1f}%)")
    print(f"  Con aW: {stats['chunks_with_aw']} ({stats['chunks_with_aw']/stats['total_chunks']*100:.1f}%)")
    print(f"  Con microorganismos: {stats['chunks_with_microorganisms']} ({stats['chunks_with_microorganisms']/stats['total_chunks']*100:.1f}%)")
    print(f"  Con conservantes: {stats['chunks_with_conservants']} ({stats['chunks_with_conservants']/stats['total_chunks']*100:.1f}%)")
    print(f"\n  Cobertura total: {stats['metadata_coverage_pct']}%")


# ============================================================================
# MAIN - Ejecutar ejemplos
# ============================================================================

if __name__ == "__main__":
    
    print("\n" + "="*60)
    print("EJEMPLOS DE USO - PRESERV-RAG")
    print("="*60)
    
    # Descomenta el ejemplo que quieras ejecutar
    
    # ejemplo_1_pipeline_basico()          # Completo: ingesta → búsqueda
    ejemplo_2_busqueda_filtrada()         # Búsquedas con filtros
    # ejemplo_3_metadata_detallada()      # Analizar metadata
    # ejemplo_4_benchmarking()             # Evaluación del sistema
    # ejemplo_5_caso_real()                # Caso de uso real
    # ejemplo_6_cobertura_metadata()       # Análisis de cobertura
    
    print("\n" + "="*60)
    print("✅ Ejemplos completados")
    print("="*60)
