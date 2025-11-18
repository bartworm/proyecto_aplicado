# ⚡ INICIO RÁPIDO - Preserv-RAG Hito 1

## En 5 Minutos

### Paso 1: Preparar el Ambiente (1 min)
```bash
# Clonar/descargar el proyecto
cd preserv-rag

# Crear entorno virtual
python -m venv venv

# Activar (elegir según tu SO)
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# Instalar dependencias
pip install -r requirements.txt
```

### Paso 2: Agregar tus PDFs (1 min)
```bash
# Crear carpeta
mkdir -p data/pdfs

# Copiar tus 20 PDFs aquí
# En Windows: arrastra y suelta en la carpeta
# En Linux/Mac:
cp /ruta/a/tus/pdfs/*.pdf data/pdfs/
```

### Paso 3: Ejecutar Pipeline Automático (2 min)
```bash
python run_pipeline.py
```

**Salida esperada:**
```
============================================================
🧬 PRESERV-RAG - PIPELINE BASELINE (HITO 1)
============================================================

1️⃣  INGESTA DE PDFs
✓ 20 PDFs cargados
  - Total páginas: 250
  - Total caracteres: 1,500,000

2️⃣  EXTRACCIÓN Y LIMPIEZA DE TEXTO
✓ Texto limpiado y normalizado
  - Reducción de caracteres: 15%

... (continúa)

✅ PIPELINE COMPLETADO EXITOSAMENTE
```

### Paso 4: Usar la Interfaz (1 min)
```bash
streamlit run streamlit_app.py
```

Se abrirá en `http://localhost:8501`

---

## Uso Básico en Streamlit

### 1️⃣ **Pipeline Tab** (Ejecuta cada paso)
   - Cargar PDFs ✓
   - Limpiar Texto ✓
   - Dividir en Chunks ✓
   - Extraer Metadata ✓
   - Crear Base Vectorial ✓

### 2️⃣ **Búsqueda Tab**
   ```
   Consulta: "¿Qué alternativa a benzoato para pH 4.2 contra levaduras?"
   ```
   Retorna: Top-5 chunks más similares con puntuación

### 3️⃣ **Métricas Tab**
   - Ver estadísticas de la BD
   - Agregar queries de prueba
   - Ejecutar benchmark
   - Ver métricas (Precision, Recall, MRR, NDCG)

---

## Estructura de Carpetas Después de Ejecutar

```
preserv-rag/
├── data/
│   ├── pdfs/
│   │   ├── paper1.pdf
│   │   ├── paper2.pdf
│   │   └── ... (20 PDFs totales)
│   └── chroma_db/  ← Creado automáticamente
│       └── (base de datos vectorial)
├── src/
│   ├── data_ingestion.py
│   ├── text_extraction.py
│   ├── chunking.py
│   ├── metadata_extraction.py
│   ├── vector_db.py
│   ├── retriever.py
│   ├── benchmark.py
│   └── __init__.py
├── streamlit_app.py
├── run_pipeline.py
├── requirements.txt
└── README.md
```

---

## Solución de Problemas Comunes

### ❌ "ModuleNotFoundError: No module named 'streamlit'"
```bash
pip install -r requirements.txt
```

### ❌ "FileNotFoundError: data/pdfs"
```bash
mkdir -p data/pdfs
# Copia tus PDFs en esa carpeta
```

### ❌ "CUDA out of memory" (si tienes GPU)
- Reduce `chunk_size` en streamlit_app.py (línea 40)
- Usa modelo más pequeño: `all-MiniLM-L6-v2` (ya configurado)

### ❌ "Puerto 8501 en uso"
```bash
streamlit run streamlit_app.py --server.port 8502
```

---

## Estructura de una Consulta Efectiva

```
"Necesito reemplazar [CONSERVANTE A] en un [PRODUCTO] 
con pH [X.X] y aW [0.XX] para inhibir [MICROORGANISMO]"
```

**Ejemplo:**
```
"Necesito reemplazar Benzoato de Sodio en una salsa 
con pH 4.2 y aW 0.97 para inhibir Zygosaccharomyces bailii"
```

---

## Archivos Importantes

| Archivo | Propósito |
|---------|-----------|
| `streamlit_app.py` | **INTERFAZ PRINCIPAL** |
| `run_pipeline.py` | Ejecutar pipeline sin UI |
| `src/data_ingestion.py` | Cargar PDFs |
| `src/vector_db.py` | Gestionar embeddings |
| `src/retriever.py` | Buscar en BD |
| `requirements.txt` | Dependencias |

---

## Próximos Pasos (Hito 2)

- ✅ Sistema Base completado
- ⏳ Integrar Claude para generación
- ⏳ Técnicas avanzadas de retrieval
- ⏳ Mejorar métricas vs baseline

---

**¿Preguntas?** Revisa `README.md` para documentación completa.
