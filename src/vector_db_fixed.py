"""
vector_db_fixed.py
Versión mejorada de vector_db.py con mejor compatibilidad para ChromaDB.
Compatible con versiones 0.4.x de ChromaDB.

USO:
    Reemplaza la importación en tus scripts:
    from vector_db_fixed import VectorDatabase
"""

import chromadb
from sentence_transformers import SentenceTransformer
from typing import List, Dict, Any
import os
import warnings


class VectorDatabase:
    """
    Clase para gestionar la base de datos vectorial con ChromaDB.
    Versión mejorada con mejor compatibilidad y manejo de errores.
    """

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

        # Inicializar cliente de Chroma con API compatible
        print(f"Inicializando ChromaDB en: {db_path}")

        try:
            # Intenta usar PersistentClient (versión nueva, más estable)
            self.client = chromadb.PersistentClient(
                path=db_path,
            )
            print("✓ ChromaDB inicializado con PersistentClient")

        except AttributeError:
            # Fallback para versiones más antiguas
            warnings.warn("Usando API antigua de ChromaDB")
            try:
                from chromadb.config import Settings
                settings = Settings(
                    persist_directory=db_path,
                    anonymized_telemetry=False,
                )
                self.client = chromadb.Client(settings)
                print("✓ ChromaDB inicializado con Client (API antigua)")
            except Exception as e:
                raise RuntimeError(
                    f"No se pudo inicializar ChromaDB. "
                    f"Error: {str(e)}\n"
                    f"Intenta actualizar ChromaDB: pip install --upgrade chromadb"
                )

        # Cargar modelo de embeddings
        print(f"Cargando modelo de embeddings: {model_name}")
        print("⏳ Primera vez puede tardar (descarga ~90MB)...")

        try:
            self.embedder = SentenceTransformer(model_name)
            print("✓ Modelo de embeddings cargado correctamente")
        except Exception as e:
            raise RuntimeError(
                f"Error al cargar modelo de embeddings.\n"
                f"Error: {str(e)}\n"
                f"Verifica conexión a internet o descarga manual del modelo."
            )

        # Crear o cargar colección
        try:
            # Intenta obtener colección existente
            self.collection = self.client.get_collection(name="preserv_rag")
            print(f"✓ Colección existente cargada ({self.collection.count()} chunks)")

        except Exception:
            # Si no existe, créala
            self.collection = self.client.create_collection(
                name="preserv_rag",
                metadata={"hnsw:space": "cosine"}
            )
            print("✓ Nueva colección creada")

    def add_chunks(self, chunks: List[Dict[str, Any]], batch_size: int = 100) -> None:
        """
        Añade chunks a la base de datos en lotes para mejor rendimiento.

        Args:
            chunks: Lista de chunks con contenido y metadata
            batch_size: Tamaño de lote para procesamiento (default 100)
        """
        if not chunks:
            print("⚠️  No hay chunks para añadir")
            return

        total_chunks = len(chunks)
        print(f"\n📦 Procesando {total_chunks} chunks en lotes de {batch_size}")

        # Procesar en lotes
        for i in range(0, total_chunks, batch_size):
            batch = chunks[i:i + batch_size]
            batch_num = (i // batch_size) + 1
            total_batches = (total_chunks + batch_size - 1) // batch_size

            print(f"   Lote {batch_num}/{total_batches}: procesando {len(batch)} chunks...")

            # Extraer datos del batch
            ids = [chunk["id"] for chunk in batch]
            contents = [chunk["content"] for chunk in batch]

            # Preparar metadata para Chroma
            metadatas = []
            for chunk in batch:
                metadata = {
                    "source_file": str(chunk.get("source_file", "unknown")),
                    "doc_title": str(chunk.get("doc_title", "unknown")),
                    "chunk_length": int(chunk.get("length", 0)),
                }

                # Añadir metadata extraída si existe
                if "extracted_metadata" in chunk:
                    extracted = chunk["extracted_metadata"]
                    if extracted.get("ph"):
                        metadata["has_ph"] = "true"
                    if extracted.get("aw"):
                        metadata["has_aw"] = "true"
                    if extracted.get("microorganisms"):
                        # Limitar a 3 para no exceder límites de Chroma
                        microorgs = extracted["microorganisms"][:3]
                        metadata["microorganisms"] = ",".join(microorgs)
                    if extracted.get("conservants"):
                        conservs = extracted["conservants"][:3]
                        metadata["conservants"] = ",".join(conservs)

                metadatas.append(metadata)

            # Generar embeddings para el batch
            try:
                embeddings = self.embedder.encode(
                    contents,
                    show_progress_bar=False,
                    convert_to_numpy=True
                )
                embeddings_list = embeddings.tolist()

            except Exception as e:
                print(f"   ❌ Error generando embeddings: {str(e)}")
                continue

            # Añadir a Chroma
            try:
                self.collection.add(
                    ids=ids,
                    embeddings=embeddings_list,
                    documents=contents,
                    metadatas=metadatas,
                )
                print(f"   ✓ Lote {batch_num} añadido correctamente")

            except Exception as e:
                print(f"   ❌ Error añadiendo lote a ChromaDB: {str(e)}")
                continue

        print(f"\n✅ {total_chunks} chunks procesados y añadidos a la BD")

    def search(self, query: str, n_results: int = 5, filters: Dict = None) -> List[Dict[str, Any]]:
        """
        Busca chunks similares a una query.

        Args:
            query: Texto de búsqueda
            n_results: Número de resultados a retornar
            filters: Filtros de metadata opcionales

        Returns:
            Lista de chunks relevantes con puntuación de similitud
        """
        try:
            # Generar embedding de la query
            query_embedding = self.embedder.encode([query])[0].tolist()

            # Preparar parámetros de búsqueda
            search_params = {
                "query_embeddings": [query_embedding],
                "n_results": n_results,
                "include": ["documents", "metadatas", "distances"]
            }

            # Añadir filtros si existen
            if filters:
                search_params["where"] = filters

            # Buscar en Chroma
            results = self.collection.query(**search_params)

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

        except Exception as e:
            print(f"❌ Error en búsqueda: {str(e)}")
            return []

    def get_collection_stats(self) -> Dict[str, Any]:
        """Retorna estadísticas de la colección."""
        try:
            count = self.collection.count()

            return {
                "total_chunks": count,
                "collection_name": self.collection.name,
                "model_used": self.model_name,
                "db_path": self.db_path,
            }
        except Exception as e:
            print(f"⚠️  Error obteniendo stats: {str(e)}")
            return {
                "total_chunks": 0,
                "collection_name": "unknown",
                "model_used": self.model_name,
                "db_path": self.db_path,
                "error": str(e)
            }

    def delete_collection(self) -> None:
        """Elimina la colección actual."""
        try:
            self.client.delete_collection(name="preserv_rag")
            print("✓ Colección eliminada")
        except Exception as e:
            print(f"⚠️  Error al eliminar colección: {str(e)}")

    def clear_collection(self) -> None:
        """Limpia todos los documentos de la colección sin eliminarla."""
        try:
            # Recrear la colección (método más seguro)
            self.client.delete_collection(name="preserv_rag")
            self.collection = self.client.create_collection(
                name="preserv_rag",
                metadata={"hnsw:space": "cosine"}
            )
            print("✓ Colección limpiada")
        except Exception as e:
            print(f"⚠️  Error al limpiar colección: {str(e)}")


# ============================================================================
# FUNCIONES DE UTILIDAD
# ============================================================================

def test_chromadb_installation():
    """Prueba rápida de instalación de ChromaDB."""
    print("\n🧪 PROBANDO INSTALACIÓN DE CHROMADB\n")

    try:
        import chromadb
        print(f"✓ ChromaDB instalado - Versión: {chromadb.__version__}")

        # Probar creación de cliente
        client = chromadb.PersistentClient(path="./test_chroma")
        print("✓ PersistentClient funciona correctamente")

        # Probar colección
        collection = client.create_collection(name="test")
        print("✓ Creación de colección funciona")

        # Limpiar
        client.delete_collection(name="test")
        print("✓ Eliminación de colección funciona")

        print("\n✅ ChromaDB funciona correctamente!\n")
        return True

    except Exception as e:
        print(f"\n❌ Error con ChromaDB: {str(e)}")
        print("\n💡 Intenta:")
        print("   pip install --upgrade chromadb")
        print("   o")
        print("   pip install chromadb==0.4.22\n")
        return False


def test_sentence_transformers():
    """Prueba rápida de instalación de sentence-transformers."""
    print("\n🧪 PROBANDO INSTALACIÓN DE SENTENCE-TRANSFORMERS\n")

    try:
        from sentence_transformers import SentenceTransformer
        print("✓ sentence-transformers instalado")

        # Probar carga de modelo pequeño
        print("⏳ Descargando modelo de prueba (puede tardar)...")
        model = SentenceTransformer('paraphrase-MiniLM-L3-v2')
        print("✓ Modelo cargado correctamente")

        # Probar encoding
        embedding = model.encode(["test"])
        print(f"✓ Encoding funciona (dimensión: {len(embedding[0])})")

        print("\n✅ sentence-transformers funciona correctamente!\n")
        return True

    except Exception as e:
        print(f"\n❌ Error con sentence-transformers: {str(e)}")
        print("\n💡 Intenta:")
        print("   pip install --upgrade sentence-transformers")
        print("   o verifica conexión a internet\n")
        return False


# ============================================================================
# MAIN PARA TESTING
# ============================================================================

if __name__ == "__main__":
    print("=" * 70)
    print("🔧 DIAGNÓSTICO DE DEPENDENCIAS")
    print("=" * 70)

    # Test ChromaDB
    chroma_ok = test_chromadb_installation()

    # Test sentence-transformers
    st_ok = test_sentence_transformers()

    # Resumen
    print("=" * 70)
    if chroma_ok and st_ok:
        print("✅ TODAS LAS DEPENDENCIAS FUNCIONAN CORRECTAMENTE")
        print("\n💡 Puedes ejecutar:")
        print("   python test_single_pdf.py")
    else:
        print("❌ ALGUNAS DEPENDENCIAS TIENEN PROBLEMAS")
        print("\n💡 Revisa las soluciones sugeridas arriba")
    print("=" * 70)
