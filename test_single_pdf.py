"""
test_single_pdf.py
Script simplificado para probar el pipeline con UN SOLO PDF.
Útil para debugging y verificación de funcionamiento local.
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


def test_single_pdf(pdf_filename: str = "FTB-61-212.pdf"):
    """
    Prueba el pipeline completo con un solo PDF.

    Args:
        pdf_filename: Nombre del PDF a procesar (debe estar en data/pdfs/)
    """

    print("=" * 70)
    print("🧪 TEST DE UN SOLO PDF - PRESERV-RAG")
    print("=" * 70)
    print(f"\n📄 PDF seleccionado: {pdf_filename}\n")

    # Configuración
    pdf_folder = "data/pdfs"
    db_path = "data/test_chroma_db"  # BD separada para pruebas
    chunk_size = 500
    overlap = 50

    try:
        # ===================================================================
        # 1. VERIFICAR QUE EL PDF EXISTE
        # ===================================================================
        print("1️⃣  VERIFICANDO PDF")
        print("-" * 70)

        pdf_path = Path(pdf_folder) / pdf_filename
        if not pdf_path.exists():
            print(f"❌ ERROR: No se encontró el PDF: {pdf_path}")
            print(f"\n💡 PDFs disponibles en {pdf_folder}:")
            for pdf in Path(pdf_folder).glob("*.pdf"):
                print(f"   - {pdf.name}")
            return

        print(f"✓ PDF encontrado: {pdf_path}")
        print(f"  Tamaño: {pdf_path.stat().st_size / 1024:.1f} KB\n")

        # ===================================================================
        # 2. INGESTA DEL PDF
        # ===================================================================
        print("2️⃣  CARGANDO PDF")
        print("-" * 70)

        ingestion = PDFIngestion(pdf_folder=pdf_folder)
        # Filtrar solo el PDF seleccionado
        all_docs = ingestion.load_pdfs()
        documents = [doc for doc in all_docs if doc["filename"] == pdf_filename]

        if not documents:
            print(f"❌ ERROR: No se pudo cargar {pdf_filename}")
            return

        doc = documents[0]
        print(f"✓ PDF cargado exitosamente")
        print(f"  - Páginas: {doc['num_pages']}")
        print(f"  - Caracteres totales: {len(doc['content']):,}")
        print(f"  - Título: {doc['metadata']['title']}\n")

        # ===================================================================
        # 3. LIMPIEZA DE TEXTO
        # ===================================================================
        print("3️⃣  LIMPIANDO TEXTO")
        print("-" * 70)

        extractor = TextExtractor()
        cleaned_docs = extractor.process_documents(documents)

        cleaned_doc = cleaned_docs[0]
        print(f"✓ Texto limpiado")
        print(f"  - Caracteres originales: {cleaned_doc['length_original']:,}")
        print(f"  - Caracteres limpios: {cleaned_doc['length_cleaned']:,}")
        reduction = ((cleaned_doc['length_original'] - cleaned_doc['length_cleaned'])
                    / cleaned_doc['length_original'] * 100)
        print(f"  - Reducción: {reduction:.1f}%")
        print(f"  - Referencias encontradas: {len(cleaned_doc['references'])}\n")

        # Mostrar muestra del texto limpio
        print("📝 Muestra del texto limpio (primeros 300 caracteres):")
        print(f"   {cleaned_doc['content'][:300]}...\n")

        # ===================================================================
        # 4. CHUNKING
        # ===================================================================
        print("4️⃣  DIVIDIENDO EN CHUNKS")
        print("-" * 70)

        chunker = DocumentChunker(chunk_size=chunk_size, overlap=overlap)
        chunks = chunker.chunk_documents(cleaned_docs)

        print(f"✓ Documento dividido en chunks")
        print(f"  - Total chunks: {len(chunks)}")
        print(f"  - Tamaño promedio: {sum(c['length'] for c in chunks) / len(chunks):.1f} caracteres")
        print(f"  - Chunk más pequeño: {min(c['length'] for c in chunks)} caracteres")
        print(f"  - Chunk más grande: {max(c['length'] for c in chunks)} caracteres\n")

        # Mostrar primer chunk como ejemplo
        print("📝 Ejemplo del primer chunk:")
        print(f"   ID: {chunks[0]['id']}")
        print(f"   Longitud: {chunks[0]['length']}")
        print(f"   Contenido: {chunks[0]['content'][:200]}...\n")

        # ===================================================================
        # 5. EXTRACCIÓN DE METADATA
        # ===================================================================
        print("5️⃣  EXTRAYENDO METADATA")
        print("-" * 70)

        metadata_extractor = MetadataExtractor()
        chunks_with_metadata = metadata_extractor.process_chunks(chunks)

        # Contar chunks con metadata
        chunks_with_ph = sum(1 for c in chunks_with_metadata
                            if c.get("extracted_metadata", {}).get("ph"))
        chunks_with_aw = sum(1 for c in chunks_with_metadata
                            if c.get("extracted_metadata", {}).get("aw"))
        chunks_with_microorg = sum(1 for c in chunks_with_metadata
                                  if c.get("extracted_metadata", {}).get("microorganisms"))
        chunks_with_conserv = sum(1 for c in chunks_with_metadata
                                 if c.get("extracted_metadata", {}).get("conservants"))

        print(f"✓ Metadata extraída")
        print(f"  - Chunks con pH: {chunks_with_ph}")
        print(f"  - Chunks con aW: {chunks_with_aw}")
        print(f"  - Chunks con microorganismos: {chunks_with_microorg}")
        print(f"  - Chunks con conservantes: {chunks_with_conserv}\n")

        # Mostrar ejemplo de chunk con metadata
        print("📝 Ejemplo de chunk con metadata:")
        for chunk in chunks_with_metadata[:10]:  # Buscar uno con metadata
            if chunk.get("extracted_metadata"):
                meta = chunk["extracted_metadata"]
                if any([meta.get("ph"), meta.get("aw"), meta.get("microorganisms"), meta.get("conservants")]):
                    print(f"   ID: {chunk['id']}")
                    if meta.get("ph"):
                        print(f"   pH: {meta['ph']}")
                    if meta.get("aw"):
                        print(f"   aW: {meta['aw']}")
                    if meta.get("microorganisms"):
                        print(f"   Microorganismos: {', '.join(meta['microorganisms'][:3])}")
                    if meta.get("conservants"):
                        print(f"   Conservantes: {', '.join(meta['conservants'][:3])}")
                    print(f"   Contenido: {chunk['content'][:150]}...")
                    break
        print()

        # ===================================================================
        # 6. VECTORIZACIÓN (ESTE ES EL PASO CRÍTICO)
        # ===================================================================
        print("6️⃣  CREANDO BASE VECTORIAL")
        print("-" * 70)
        print("⚠️  Este paso puede tardar la primera vez que se ejecuta")
        print("   (descarga del modelo de embeddings ~90MB)\n")

        try:
            vdb = VectorDatabase(db_path=db_path, model_name="all-MiniLM-L6-v2")
            print("✓ Modelo de embeddings cargado")

            vdb.add_chunks(chunks_with_metadata)
            print(f"✓ {len(chunks_with_metadata)} chunks indexados en la base vectorial\n")

        except Exception as e:
            print(f"❌ ERROR en vectorización: {str(e)}")
            print("\n💡 Posibles causas:")
            print("   1. Problema de compatibilidad con ChromaDB")
            print("   2. Falta de conexión a internet (para descargar modelo)")
            print("   3. Falta de espacio en disco")
            print("\n💡 Solución: Ver PROBLEMAS_COMUNES.md")
            raise

        # ===================================================================
        # 7. BÚSQUEDA DE PRUEBA
        # ===================================================================
        print("7️⃣  PROBANDO BÚSQUEDA")
        print("-" * 70)

        retriever = SimpleRetriever(vdb)

        test_queries = [
            "conservante natural",
            "pH acidez",
            "microorganismos levaduras",
        ]

        for i, query in enumerate(test_queries, 1):
            print(f"\n🔍 Query {i}: '{query}'")
            results = retriever.retrieve(query, n_results=3)

            if results:
                for j, result in enumerate(results, 1):
                    print(f"   {j}. [Similitud: {result['similarity_score']:.4f}]")
                    print(f"      {result['content'][:150]}...")
            else:
                print("   ⚠️  No se encontraron resultados")

        # ===================================================================
        # RESUMEN FINAL
        # ===================================================================
        print("\n" + "=" * 70)
        print("✅ TEST COMPLETADO EXITOSAMENTE")
        print("=" * 70)
        print(f"\n📊 RESUMEN:")
        print(f"  - PDF procesado: {pdf_filename}")
        print(f"  - Páginas: {doc['num_pages']}")
        print(f"  - Chunks creados: {len(chunks)}")
        print(f"  - Chunks con metadata: {chunks_with_ph + chunks_with_aw + chunks_with_microorg + chunks_with_conserv}")
        print(f"  - Base de datos: {db_path}")

        print(f"\n💡 SIGUIENTE PASO:")
        print(f"   Si este test funcionó, puedes ejecutar el pipeline completo con:")
        print(f"   python run_pipeline.py")

    except Exception as e:
        print(f"\n❌ ERROR INESPERADO: {str(e)}")
        print(f"\n🔍 Tipo de error: {type(e).__name__}")
        import traceback
        print(f"\n📋 Stack trace completo:")
        traceback.print_exc()
        print(f"\n💡 Revisa el archivo PROBLEMAS_COMUNES.md para soluciones")


if __name__ == "__main__":
    # Puedes cambiar el PDF aquí o pasarlo como argumento
    import sys

    if len(sys.argv) > 1:
        pdf_name = sys.argv[1]
    else:
        # PDF por defecto para testing (uno pequeño)
        pdf_name = "FTB-61-212.pdf"

    test_single_pdf(pdf_name)
