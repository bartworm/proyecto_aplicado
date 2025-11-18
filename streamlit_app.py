"""
streamlit_app.py
Interfaz Streamlit para el sistema Preserv-RAG Hito 1.
Permite hacer consultas y ver métricas baseline.
"""

import streamlit as st
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


# Configuración de Streamlit
st.set_page_config(
    page_title="Preserv-RAG - Hito 1 (Baseline)",
    page_icon="🧬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS personalizado
st.markdown("""
    <style>
    .metric-box {
        background-color: #f0f2f6;
        padding: 20px;
        border-radius: 10px;
        margin: 10px 0;
    }
    .retrieval-box {
        background-color: #e8f4f8;
        padding: 15px;
        border-left: 4px solid #1f77b4;
        margin: 10px 0;
    }
    </style>
""", unsafe_allow_html=True)

# Título
st.title("🧬 Preserv-RAG - Sistema Baseline (Hito 1)")
st.markdown("**Pipeline RAG para recomendaciones de alternativas naturales a conservantes sintéticos**")

# Sidebar
with st.sidebar:
    st.header("⚙️ Configuración")
    
    pdf_folder = st.text_input(
        "Carpeta con PDFs",
        value="data/pdfs",
        help="Ruta relativa o absoluta a la carpeta con archivos PDF"
    )
    
    chunk_size = st.slider(
        "Tamaño de chunk (caracteres)",
        min_value=200,
        max_value=1500,
        value=500,
        step=100
    )
    
    overlap = st.slider(
        "Solapamiento entre chunks",
        min_value=0,
        max_value=200,
        value=50,
        step=10
    )
    
    n_results = st.slider(
        "Número de resultados a retornar",
        min_value=1,
        max_value=20,
        value=5
    )
    
    similarity_threshold = st.slider(
        "Umbral de similitud",
        min_value=0.0,
        max_value=1.0,
        value=0.3,
        step=0.05
    )

# Tabs principales
tab1, tab2, tab3, tab4 = st.tabs([
    "🔄 Pipeline",
    "🔍 Búsqueda",
    "📊 Métricas Baseline",
    "📋 Información"
])

# ============= TAB 1: PIPELINE =============
with tab1:
    st.header("Pipeline de Procesamiento")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("1️⃣ Ingesta de PDFs")
        if st.button("Cargar PDFs", key="load_pdfs"):
            try:
                with st.spinner("Cargando PDFs..."):
                    ingestion = PDFIngestion(pdf_folder=pdf_folder)
                    documents = ingestion.load_pdfs()
                    stats = ingestion.get_stats()
                    
                    st.session_state['documents'] = documents
                    st.session_state['ingestion_stats'] = stats
                    
                    st.success(f"✓ {stats['total_pdfs']} PDFs cargados")
                    st.metric("Total de páginas", stats['total_pages'])
                    st.metric("Caracteres totales", f"{stats['total_characters']:,}")
            except Exception as e:
                st.error(f"❌ Error: {str(e)}")
    
    with col2:
        if "ingestion_stats" in st.session_state:
            st.subheader("Estadísticas de Ingesta")
            stats = st.session_state['ingestion_stats']
            st.write(f"**PDFs cargados:** {stats['total_pdfs']}")
            st.write(f"**Páginas totales:** {stats['total_pages']}")
            st.write(f"**Caracteres:** {stats['total_characters']:,}")
            st.write(f"**Prom. páginas/PDF:** {stats['avg_pages_per_pdf']:.2f}")
    
    st.divider()
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("2️⃣ Limpieza de Texto")
        if st.button("Limpiar Texto", key="clean_text"):
            if "documents" not in st.session_state:
                st.warning("⚠️ Primero carga los PDFs")
            else:
                try:
                    with st.spinner("Limpiando texto..."):
                        extractor = TextExtractor()
                        cleaned_docs = extractor.process_documents(st.session_state['documents'])
                        stats = extractor.get_stats(cleaned_docs)
                        
                        st.session_state['cleaned_documents'] = cleaned_docs
                        st.session_state['extraction_stats'] = stats
                        
                        st.success("✓ Texto limpio")
                        st.metric("Reducción de caracteres", f"{stats['reduction_percentage']}%")
                except Exception as e:
                    st.error(f"❌ Error: {str(e)}")
    
    with col2:
        if "extraction_stats" in st.session_state:
            st.subheader("Estadísticas de Limpieza")
            stats = st.session_state['extraction_stats']
            st.write(f"**Caracteres originales:** {stats['total_original_chars']:,}")
            st.write(f"**Caracteres limpios:** {stats['total_cleaned_chars']:,}")
            st.write(f"**Reducción:** {stats['reduction_percentage']}%")
    
    st.divider()
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("3️⃣ Chunking")
        if st.button("Dividir en Chunks", key="chunk"):
            if "cleaned_documents" not in st.session_state:
                st.warning("⚠️ Primero limpia el texto")
            else:
                try:
                    with st.spinner("Dividiendo en chunks..."):
                        chunker = DocumentChunker(chunk_size=chunk_size, overlap=overlap)
                        chunks = chunker.chunk_documents(st.session_state['cleaned_documents'])
                        stats = chunker.get_stats(chunks)
                        
                        st.session_state['chunks'] = chunks
                        st.session_state['chunking_stats'] = stats
                        
                        st.success(f"✓ {stats['total_chunks']} chunks creados")
                except Exception as e:
                    st.error(f"❌ Error: {str(e)}")
    
    with col2:
        if "chunking_stats" in st.session_state:
            st.subheader("Estadísticas de Chunking")
            stats = st.session_state['chunking_stats']
            st.write(f"**Total de chunks:** {stats['total_chunks']}")
            st.write(f"**Documentos únicos:** {stats['unique_documents']}")
            st.write(f"**Tamaño promedio:** {stats['avg_chunk_size']} caracteres")
            st.write(f"**Chunks/documento:** {stats['chunks_per_document']}")
    
    st.divider()
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("4️⃣ Extracción de Metadata")
        if st.button("Extraer Metadata", key="extract_metadata"):
            if "chunks" not in st.session_state:
                st.warning("⚠️ Primero crea los chunks")
            else:
                try:
                    with st.spinner("Extrayendo metadata..."):
                        extractor = MetadataExtractor()
                        chunks_with_metadata = extractor.process_chunks(st.session_state['chunks'])
                        stats = extractor.get_stats(chunks_with_metadata)
                        
                        st.session_state['chunks_with_metadata'] = chunks_with_metadata
                        st.session_state['metadata_stats'] = stats
                        
                        st.success("✓ Metadata extraída")
                except Exception as e:
                    st.error(f"❌ Error: {str(e)}")
    
    with col2:
        if "metadata_stats" in st.session_state:
            st.subheader("Estadísticas de Metadata")
            stats = st.session_state['metadata_stats']
            st.write(f"**Chunks con pH:** {stats['chunks_with_ph']}")
            st.write(f"**Chunks con aW:** {stats['chunks_with_aw']}")
            st.write(f"**Chunks con microorganismos:** {stats['chunks_with_microorganisms']}")
            st.write(f"**Chunks con conservantes:** {stats['chunks_with_conservants']}")
    
    st.divider()
    
    st.subheader("5️⃣ Vectorización e Indexación")
    if st.button("Crear Base Vectorial", key="vectorize"):
        if "chunks_with_metadata" not in st.session_state:
            st.warning("⚠️ Primero extrae la metadata")
        else:
            try:
                with st.spinner("Creando base vectorial (puede tomar tiempo)..."):
                    vdb = VectorDatabase(db_path="data/chroma_db")
                    vdb.add_chunks(st.session_state['chunks_with_metadata'])
                    stats = vdb.get_collection_stats()
                    
                    st.session_state['vector_db'] = vdb
                    st.session_state['vdb_stats'] = stats
                    
                    st.success("✓ Base vectorial creada")
                    st.info(f"📊 {stats['total_chunks']} chunks indexados con {stats['model_used']}")
            except Exception as e:
                st.error(f"❌ Error: {str(e)}")


# ============= TAB 2: BÚSQUEDA =============
with tab2:
    st.header("🔍 Búsqueda Vectorial")
    
    if "vector_db" not in st.session_state:
        st.warning("⚠️ Primero completa el pipeline en la pestaña 'Pipeline'")
    else:
        query = st.text_area(
            "Ingresa tu consulta",
            placeholder="Ej: ¿Qué alternativa natural puedo usar para reemplazar benzoato en una salsa con pH 4.2?",
            height=100
        )
        
        if st.button("Buscar", key="search"):
            if query.strip():
                with st.spinner("Buscando..."):
                    retriever = SimpleRetriever(st.session_state['vector_db'])
                    results = retriever.retrieve(query, n_results=n_results)
                    
                    if results:
                        st.success(f"✓ {len(results)} resultados encontrados")
                        
                        for i, result in enumerate(results, 1):
                            with st.container():
                                col1, col2 = st.columns([3, 1])
                                
                                with col1:
                                    st.markdown(f"### Resultado {i}")
                                    st.write(f"**Similitud:** {result['similarity_score']:.4f}")
                                    st.write(f"**Fuente:** {result['metadata'].get('source_file', 'Unknown')}")
                                    st.write(f"**Chunk ID:** `{result['id']}`")
                                
                                with col2:
                                    if result['similarity_score'] >= similarity_threshold:
                                        st.success("✓ Sobre threshold")
                                    else:
                                        st.warning("⚠️ Bajo threshold")
                                
                                st.markdown("**Contenido:**")
                                st.text(result['content'][:500] + "..." if len(result['content']) > 500 else result['content'])
                                
                                st.divider()
                    else:
                        st.info("No se encontraron resultados relevantes")
            else:
                st.warning("Por favor ingresa una consulta")


# ============= TAB 3: MÉTRICAS BASELINE =============
with tab3:
    st.header("📊 Métricas del Sistema Baseline")
    
    if "vector_db" not in st.session_state:
        st.warning("⚠️ Primero completa el pipeline")
    else:
        st.subheader("Estadísticas de la Base de Datos")
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total de chunks", st.session_state['vdb_stats']['total_chunks'])
        with col2:
            st.metric("Modelo de embeddings", st.session_state['vdb_stats']['model_used'])
        with col3:
            st.metric("Ruta de BD", st.session_state['vdb_db_path'] if "vdb_db_path" in st.session_state else "data/chroma_db")
        
        st.divider()
        
        st.subheader("Evaluación con Queries de Prueba")
        
        # Queries de prueba sugeridas
        default_queries = [
            ("Benzoato en pH 4.2 contra levaduras", ["chunk_id_1", "chunk_id_2"]),
            ("Alternativas naturales a sorbato", ["chunk_id_3"]),
            ("Nisina y extractos de plantas", ["chunk_id_4", "chunk_id_5"]),
        ]
        
        st.info("💡 Agrega queries de prueba para evaluar el sistema")
        
        col1, col2 = st.columns(2)
        with col1:
            query_input = st.text_input("Ingresa una query de prueba")
        with col2:
            relevant_input = st.text_input("Chunk IDs relevantes (separados por comas)")
        
        if st.button("Agregar Query de Prueba"):
            if query_input and relevant_input:
                if "test_queries" not in st.session_state:
                    st.session_state['test_queries'] = []
                
                relevant_ids = [id.strip() for id in relevant_input.split(",")]
                st.session_state['test_queries'].append((query_input, relevant_ids))
                st.success("✓ Query agregada")
        
        if "test_queries" in st.session_state and st.session_state['test_queries']:
            if st.button("Ejecutar Benchmark"):
                with st.spinner("Ejecutando evaluación..."):
                    retriever = SimpleRetriever(st.session_state['vector_db'])
                    benchmark = RAGBenchmark(retriever)
                    
                    aggregated = benchmark.evaluate_multiple_queries(st.session_state['test_queries'])
                    
                    st.session_state['benchmark_results'] = aggregated
                    st.success("✓ Evaluación completada")
        
        if "benchmark_results" in st.session_state:
            st.subheader("Resultados del Benchmark")
            
            results = st.session_state['benchmark_results']
            
            # Métricas principales
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Total de queries", results['total_queries'])
            with col2:
                st.metric("Precision@5", f"{results['avg_precision_at_5']:.4f}")
            with col3:
                st.metric("Recall@5", f"{results['avg_recall_at_5']:.4f}")
            with col4:
                st.metric("MRR", f"{results['avg_mrr']:.4f}")
            
            # Métricas adicionales
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("NDCG@5", f"{results['avg_ndcg_at_5']:.4f}")
            with col2:
                st.metric("NDCG@10", f"{results['avg_ndcg_at_10']:.4f}")
            with col3:
                st.metric("Similitud Promedio", f"{results['avg_similarity_score']:.4f}")
            
            st.markdown("**Interpretación:**")
            st.write("""
            - **Precision@K:** Proporción de resultados relevantes en los top-K
            - **Recall@K:** Proporción de documentos relevantes recuperados
            - **MRR:** Posición promedio del primer resultado relevante (1/rank)
            - **NDCG:** Métrica que considera el ranking (relevancia ordenada)
            """)


# ============= TAB 4: INFORMACIÓN =============
with tab4:
    st.header("📋 Información del Sistema")
    
    st.subheader("Arquitectura del Pipeline Hito 1")
    
    architecture = """
    ```
    ┌─────────────────┐
    │   PDFs (Ingesta)│
    └────────┬────────┘
             │
    ┌────────▼─────────────────┐
    │  Extracción de Texto     │
    │  (PyPDF2)                │
    └────────┬─────────────────┘
             │
    ┌────────▼──────────────────┐
    │  Limpieza y Normalización │
    │  (regex, espacios)        │
    └────────┬──────────────────┘
             │
    ┌────────▼─────────────────────────┐
    │  Chunking                        │
    │  (500 chars, overlap=50)         │
    └────────┬─────────────────────────┘
             │
    ┌────────▼──────────────────────────────────┐
    │  Extracción de Metadata                   │
    │  (pH, aW, microorganismos, conservantes)  │
    └────────┬──────────────────────────────────┘
             │
    ┌────────▼─────────────────────────────┐
    │  Vectorización                       │
    │  (sentence-transformers)             │
    └────────┬─────────────────────────────┘
             │
    ┌────────▼──────────────────┐
    │  Chroma Vector Database   │
    │  (Almacenamiento)         │
    └────────┬──────────────────┘
             │
    ┌────────▼───────────────┐
    │  Retriever Simple      │
    │  (Búsqueda Vectorial)  │
    └────────┬───────────────┘
             │
    ┌────────▼──────────────────────┐
    │  Benchmark                    │
    │  (Métricas: P@K, R@K, MRR...)│
    └───────────────────────────────┘
    ```
    """
    
    st.markdown(architecture)
    
    st.subheader("Componentes del Sistema")
    
    components = {
        "data_ingestion.py": "Carga PDFs desde carpeta local",
        "text_extraction.py": "Limpia y normaliza texto",
        "chunking.py": "Divide documentos en chunks",
        "metadata_extraction.py": "Extrae pH, aW, microorganismos, etc.",
        "vector_db.py": "Maneja base vectorial con Chroma",
        "retriever.py": "Recupera chunks similares",
        "benchmark.py": "Calcula métricas de evaluación",
        "streamlit_app.py": "Interfaz de usuario",
    }
    
    for component, description in components.items():
        st.write(f"**{component}:** {description}")
    
    st.subheader("Tecnologías Utilizadas")
    
    tech_table = """
    | Componente | Librería | Propósito |
    |---|---|---|
    | Lectura de PDFs | PyPDF2 | Extraer texto de PDFs |
    | Embeddings | sentence-transformers | Generar vectores de texto |
    | Vector DB | Chroma | Almacenar embeddings |
    | Interfaz | Streamlit | UI interactiva |
    | Evaluación | NumPy | Cálculo de métricas |
    """
    
    st.markdown(tech_table)
    
    st.subheader("Flujo de Uso")
    
    st.markdown("""
    1. **Cargar PDFs** → Selecciona la carpeta con archivos
    2. **Limpiar Texto** → Normaliza el contenido
    3. **Crear Chunks** → Divide en fragmentos
    4. **Extraer Metadata** → Identifica pH, aW, etc.
    5. **Vectorizar** → Crea embeddings e indexa
    6. **Buscar** → Consulta la base vectorial
    7. **Evaluar** → Mide rendimiento con métricas
    """)
    
    st.divider()
    
    st.markdown("**Versión:** Hito 1 (Baseline)")
    st.markdown("**Entrega:** 22 de Noviembre")
    st.markdown("**Próximo:** Hito 2 - Mejoras avanzadas y generación con Claude")
