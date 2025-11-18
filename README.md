# 🧬 Preserv-RAG - Sistema Baseline (Hito 1)

Sistema RAG para recomendar alternativas naturales a conservantes sintéticos en alimentos.

## 📋 Descripción

**Preserv-RAG** es un pipeline de Retrieval-Augmented Generation (RAG) que procesa documentos científicos sobre preservantes naturales y permite hacer consultas para obtener recomendaciones basadas en parámetros como:

- **pH** del producto
- **Actividad de agua (aW)**
- **Microorganismo objetivo** a inhibir
- **Concentración** deseada

## 🏗️ Estructura del Proyecto

```
preserv-rag/
├── data/
│   ├── pdfs/              # Aquí van tus 20 PDFs
│   └── chroma_db/         # Base de datos vectorial (se crea automáticamente)
├── src/
│   ├── __init__.py
│   ├── data_ingestion.py      # Carga PDFs
│   ├── text_extraction.py     # Limpia texto
│   ├── chunking.py            # Divide en chunks
│   ├── metadata_extraction.py # Extrae pH, aW, etc.
│   ├── vector_db.py           # Gestiona Chroma
│   ├── retriever.py           # Búsqueda vectorial
│   └── benchmark.py           # Métricas
├── streamlit_app.py       # Interfaz principal
├── requirements.txt       # Dependencias
└── README.md              # Este archivo
```

## 🚀 Instalación

### Requisitos Previos
- Python 3.8+
- pip

### Pasos

1. **Clonar/Descargar el proyecto:**
```bash
cd preserv-rag
```

2. **Crear entorno virtual (recomendado):**
```bash
python -m venv venv

# En Windows:
venv\Scripts\activate

# En Linux/Mac:
source venv/bin/activate
```

3. **Instalar dependencias:**
```bash
pip install -r requirements.txt
```

4. **Crear carpeta de PDFs:**
```bash
mkdir -p data/pdfs
# Copia tus 20 PDFs aquí
```

5. **Ejecutar la aplicación:**
```bash
streamlit run streamlit_app.py
```

La interfaz se abrirá en `http://localhost:8501`

## 📖 Uso

### Opción 1: Interfaz Gráfica (Recomendado)

1. **Pipeline Tab:**
   - Haz clic en "Cargar PDFs" → "Limpiar Texto" → "Dividir en Chunks" → etc.
   - Sigue los pasos en orden

2. **Búsqueda Tab:**
   - Una vez completado el pipeline, ingresa tu consulta
   - Ej: "¿Qué alternativa a benzoato para pH 4.2?"

3. **Métricas Tab:**
   - Ve el desempeño del sistema baseline
   - Agrega queries de prueba para evaluación

### Opción 2: Código Python

```python
from src.data_ingestion import PDFIngestion
from src.text_extraction import TextExtractor
from src.chunking import DocumentChunker
from src.metadata_extraction import MetadataExtractor
from src.vector_db import VectorDatabase
from src.retriever import SimpleRetriever

# 1. Cargar PDFs
ingestion = PDFIngestion(pdf_folder="data/pdfs")
documents = ingestion.load_pdfs()

# 2. Limpiar texto
extractor = TextExtractor()
cleaned_docs = extractor.process_documents(documents)

# 3. Chunking
chunker = DocumentChunker(chunk_size=500, overlap=50)
chunks = chunker.chunk_documents(cleaned_docs)

# 4. Metadata
metadata_extractor = MetadataExtractor()
chunks_with_metadata = metadata_extractor.process_chunks(chunks)

# 5. Vectorización
vdb = VectorDatabase(db_path="data/chroma_db")
vdb.add_chunks(chunks_with_metadata)

# 6. Búsqueda
retriever = SimpleRetriever(vdb)
results = retriever.retrieve("¿Qué alternativa a benzoato?", n_results=5)

for result in results:
    print(f"Similitud: {result['similarity_score']}")
    print(f"Contenido: {result['content'][:200]}...")
```

## 📊 Métricas Implementadas

### Retrieval Metrics:
- **Precision@K:** Proporción de resultados relevantes en top-K
- **Recall@K:** Proporción de documentos relevantes recuperados
- **MRR (Mean Reciprocal Rank):** Posición del primer resultado relevante
- **NDCG@K (Normalized Discounted Cumulative Gain):** Relevancia ordenada

### Sistema Metrics:
- Número de chunks creados
- Cobertura de metadata extraída
- Puntuación promedio de similitud
- Tiempo de procesamiento

## 🔧 Configuración

### Variables en `streamlit_app.py`:

```python
chunk_size = 500          # Tamaño de cada chunk (caracteres)
overlap = 50              # Solapamiento entre chunks
n_results = 5             # Número de resultados a retornar
similarity_threshold = 0.3 # Puntuación mínima de similitud
```

### Modelo de Embeddings:

Por defecto usa `all-MiniLM-L6-v2` de sentence-transformers. Para cambiar:

```python
vdb = VectorDatabase(model_name="sentence-transformers/all-mpnet-base-v2")
```

Otras opciones:
- `all-mpnet-base-v2` (mejor, más lento)
- `paraphrase-MiniLM-L6-v2`
- `all-distilroberta-v1`

## 📝 Formato Esperado de PDFs

El sistema está optimizado para papers académicos con:
- Secciones claramente delimitadas
- Datos de pH y aW mencionados explícitamente
- Nombres de microorganismos científicos
- Concentraciones en ppm o mg/kg

Ejemplo de texto procesable:
```
"...el extracto de clavo a 500 ppm inhibió completamente 
Zygosaccharomyces bailii a pH 4.0 y aW 0.97..."
```

## 🐛 Troubleshooting

### "Carpeta no encontrada"
```bash
# Asegúrate de crear la carpeta y copiar PDFs:
mkdir -p data/pdfs
cp /ruta/a/tus/pdfs/* data/pdfs/
```

### "Out of Memory con PDFs grandes"
- Reduce `chunk_size` en la configuración
- Procesa PDFs en lotes más pequeños

### "Embeddings lentos"
- Usa un modelo más pequeño: `all-MiniLM-L6-v2` (ya configurado)
- Reduce número de chunks

## 📚 Recursos Adicionales

- [Chroma Docs](https://docs.trychroma.com/)
- [Sentence-Transformers](https://www.sbert.net/)
- [Streamlit Docs](https://docs.streamlit.io/)
- [PyPDF2 Docs](https://pypdf2.readthedocs.io/)

## 📅 Hito 1 Entregables

✅ Pipeline de procesamiento de datos (ingesta → vectorización)
✅ Chunking con solapamiento
✅ Extracción de metadata (pH, aW, microorganismos, etc.)
✅ Base de datos vectorial (Chroma)
✅ Retriever simple
✅ Benchmark con métricas baseline
✅ Interfaz Streamlit completa
✅ Documentación

## 🔄 Próximo: Hito 2

- Técnicas avanzadas de retrieval (hybrid search, reranking, etc.)
- Integración de Claude para generación aumentada
- Mejora de métricas vs baseline
- Componentes modularizados en interfaz

## 📄 Licencia

Este proyecto es para fines educativos.

---

**Versión:** 1.0 (Hito 1)
**Última actualización:** Noviembre 2024
