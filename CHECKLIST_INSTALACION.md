# ✅ CHECKLIST - INSTALACIÓN Y VERIFICACIÓN

## 📋 Pre-Instalación

- [ ] Python 3.8+ instalado (`python --version`)
- [ ] pip actualizado (`pip --upgrade pip`)
- [ ] Git instalado (opcional pero recomendado)
- [ ] 500MB de espacio libre en disco
- [ ] 20 archivos PDF preparados en una carpeta

---

## 🚀 Paso 1: Descargar y Configurar

```bash
# 1. Descargar/Clonar el proyecto
git clone <url-repositorio>
cd preserv-rag

# ✅ Verificar estructura
ls -la
# Debe mostrar:
# - src/
# - streamlit_app.py
# - requirements.txt
# - etc.
```

**Checklist:**
- [ ] Carpeta `preserv-rag/` existe
- [ ] Archivo `streamlit_app.py` presente
- [ ] Carpeta `src/` contiene 8 archivos `.py`
- [ ] Archivo `requirements.txt` presente

---

## 🐍 Paso 2: Crear Entorno Virtual

### En Windows:
```bash
python -m venv venv
venv\Scripts\activate
```

**Checklist:**
- [ ] Comando ejecutado sin errores
- [ ] Prompt cambia a `(venv) C:\...`
- [ ] `pip --version` muestra virtualenv

### En Linux/Mac:
```bash
python3 -m venv venv
source venv/bin/activate
```

**Checklist:**
- [ ] Comando ejecutado sin errores
- [ ] Prompt cambia a `(venv) $`
- [ ] `which python` muestra ruta virtual

---

## 📦 Paso 3: Instalar Dependencias

```bash
pip install -r requirements.txt
```

**Esperado:**
```
Collecting PyPDF2==3.0.1
Collecting sentence-transformers==2.2.2
Collecting chromadb==0.4.14
Collecting streamlit==1.28.1
...
Successfully installed (todos los paquetes)
```

**Checklist:**
- [ ] Sin errores de instalación
- [ ] Todos los paquetes instalados
- [ ] No hay mensajes "ERROR" o "FAILED"
- [ ] Último mensaje: "Successfully installed X packages"

**Verificar instalación:**
```bash
pip list | grep -E "PyPDF2|sentence-transformers|chromadb|streamlit"
```

**Checklist:**
- [ ] PyPDF2 3.0.1
- [ ] sentence-transformers 2.2.2
- [ ] chromadb 0.4.14
- [ ] streamlit 1.28.1

---

## 📁 Paso 4: Preparar Carpeta de PDFs

```bash
# Crear carpeta
mkdir -p data/pdfs

# Copiar PDFs (Windows)
xcopy "C:\ruta\a\pdfs\*.pdf" "data\pdfs\"

# Copiar PDFs (Linux/Mac)
cp /ruta/a/pdfs/*.pdf data/pdfs/
```

**Verificar:**
```bash
ls -la data/pdfs/
# Debe mostrar: 20 archivos .pdf
```

**Checklist:**
- [ ] Carpeta `data/pdfs/` creada
- [ ] 20 archivos PDF copiados
- [ ] Tamaño total > 100MB (típicamente)
- [ ] Al menos uno es legible (ej: `file data/pdfs/*.pdf`)

---

## ▶️ Paso 5: Ejecutar Pipeline Automático (Opcional)

```bash
python run_pipeline.py
```

**Esperado:**
```
============================================================
🧬 PRESERV-RAG - PIPELINE BASELINE (HITO 1)
============================================================

1️⃣  INGESTA DE PDFs
---------
✓ 20 PDFs cargados
  - Total páginas: XXX
  - Total caracteres: XXX,XXX

2️⃣  EXTRACCIÓN Y LIMPIEZA DE TEXTO
✓ Texto limpiado...

... (continúa)

✅ PIPELINE COMPLETADO EXITOSAMENTE
```

**Checklist:**
- [ ] Sin errores críticos
- [ ] Se carga PDFs
- [ ] Se procesan chunks
- [ ] Se crea base vectorial
- [ ] Mensaje final: "PIPELINE COMPLETADO"

---

## 🖥️ Paso 6: Ejecutar Streamlit

```bash
streamlit run streamlit_app.py
```

**Esperado en terminal:**
```
  You can now view your Streamlit app in your browser.

  Local URL: http://localhost:8501
  Network URL: http://192.168.x.x:8501
```

**Checklist:**
- [ ] Sin errores de ejecución
- [ ] Message "You can now view your Streamlit app"
- [ ] URL disponible (localhost:8501)
- [ ] Navegador abre automáticamente o puedo acceder manualmente

---

## 🌐 Paso 7: Verificar Interfaz

### En el Navegador (http://localhost:8501):

**Tab 1: Pipeline**
- [ ] Botón "Cargar PDFs" visible
- [ ] Botón "Limpiar Texto" visible
- [ ] Botón "Dividir en Chunks" visible
- [ ] Botón "Extraer Metadata" visible
- [ ] Botón "Crear Base Vectorial" visible

**Prueba rápida:**
1. Haz clic en "Cargar PDFs"
2. Espera a que aparezca el ✓ de éxito
3. Continúa con los siguientes pasos

**Checklist:**
- [ ] "Cargar PDFs" muestra estadísticas
- [ ] "Limpiar Texto" ejecuta sin errores
- [ ] "Dividir en Chunks" muestra número de chunks
- [ ] "Extraer Metadata" muestra cobertura
- [ ] "Crear Base Vectorial" muestra "chunks indexados"

**Tab 2: Búsqueda**
- [ ] Area de texto para consulta visible
- [ ] Botón "Buscar" funciona
- [ ] Retorna resultados con similitud

**Prueba rápida:**
```
Consulta: "benzoato conservante"
Resultado: 5 chunks con puntuación de similitud
```

**Checklist:**
- [ ] Campo de consulta acepta texto
- [ ] Botón "Buscar" ejecuta
- [ ] Retorna resultados o mensaje "Sin resultados"
- [ ] Cada resultado muestra similitud

**Tab 3: Métricas**
- [ ] Estadísticas de BD visibles
- [ ] Opción de agregar queries de prueba
- [ ] Botón "Ejecutar Benchmark"

**Checklist:**
- [ ] Muestra "Total de chunks"
- [ ] Permite agregar queries
- [ ] Benchmark genera métricas (P@5, R@5, MRR, NDCG)

**Tab 4: Información**
- [ ] Diagrama del pipeline visible
- [ ] Descripción de componentes
- [ ] Lista de tecnologías

**Checklist:**
- [ ] Información visible y legible
- [ ] Navegable sin errores

---

## 🧪 Paso 8: Test Funcional Completo

### Test 1: Pipeline Básico
```python
from src.data_ingestion import PDFIngestion
from src.vector_db import VectorDatabase
from src.retriever import SimpleRetriever

# Cargar
ing = PDFIngestion(pdf_folder="data/pdfs")
docs = ing.load_pdfs()
print(f"✓ Cargados {len(docs)} PDFs")

# Buscar en BD existente
vdb = VectorDatabase(db_path="data/chroma_db")
ret = SimpleRetriever(vdb)
results = ret.retrieve("benzoato pH 4", n_results=3)
print(f"✓ Encontrados {len(results)} resultados")
```

**Checklist:**
- [ ] Se carga PDFs sin error
- [ ] Retrieve retorna resultados
- [ ] Cada resultado tiene: id, content, metadata, similarity_score

### Test 2: Metadata Extraction
```python
from src.metadata_extraction import MetadataExtractor

extractor = MetadataExtractor()

# Test en un chunk simple
chunk = {"content": "pH 4.0 aW 0.95 benzoato 500 ppm"}
result = extractor.extract_chunk_metadata(chunk)

print(f"pH encontrado: {result['extracted_metadata']['ph']}")
print(f"aW encontrado: {result['extracted_metadata']['aw']}")
print(f"Conservantes: {result['extracted_metadata']['conservants']}")
```

**Checklist:**
- [ ] Se extrae pH correctamente
- [ ] Se extrae aW correctamente
- [ ] Se detectan conservantes

### Test 3: Benchmark
```python
from src.benchmark import RAGBenchmark
from src.retriever import SimpleRetriever
from src.vector_db import VectorDatabase

vdb = VectorDatabase(db_path="data/chroma_db")
retriever = SimpleRetriever(vdb)
benchmark = RAGBenchmark(retriever)

# Evaluar una query
metrics = benchmark.evaluate_query(
    "benzoato alternativa",
    ["chunk_0", "chunk_5"],  # IDs relevantes simulados
    k=5
)

print(f"Precision@5: {metrics['precision_at_5']}")
print(f"MRR: {metrics['mrr']}")
```

**Checklist:**
- [ ] Se calcula Precision@5
- [ ] Se calcula MRR
- [ ] Se calcula NDCG@5
- [ ] Valores están entre 0 y 1

---

## 📊 Paso 9: Validación de Datos

```bash
# Verificar BD creada
ls -lh data/chroma_db/

# Verificar tamaño
du -sh data/chroma_db/
# Esperado: 50-200 MB (dependiendo de PDFs)
```

**Checklist:**
- [ ] `data/chroma_db/` existe
- [ ] Contiene archivos `.parquet`
- [ ] Tamaño > 1 MB

---

## 🐛 Solución de Problemas

### Error: "No module named 'PyPDF2'"
```bash
pip install -r requirements.txt
# Si sigue fallando:
pip install PyPDF2==3.0.1 --force-reinstall
```
**Checklist:** - [ ] Dependencias reinstaladas

### Error: "FileNotFoundError: data/pdfs"
```bash
mkdir -p data/pdfs
# Copiar PDFs
cp /ruta/a/pdfs/*.pdf data/pdfs/
```
**Checklist:** - [ ] Carpeta creada y PDFs copiados

### Error: "Port 8501 is already in use"
```bash
streamlit run streamlit_app.py --server.port 8502
# O matar proceso:
# Windows: taskkill /PID <pid> /F
# Linux: kill -9 <pid>
```
**Checklist:** - [ ] Streamlit ejecuta en puerto alternativo

### Error: "Embeddings generation timeout"
- Reducir `chunk_size` en streamlit_app.py (línea ~40)
- Cambiar modelo a algo más pequeño
- Aumentar memoria disponible

**Checklist:** - [ ] Parámetros ajustados

---

## ✨ Verificación Final

```bash
# 1. Verificar estructura
python -c "from src import *; print('✓ Modulos importables')"

# 2. Verificar PDFs
python -c "from src.data_ingestion import PDFIngestion; ing = PDFIngestion(); docs = ing.load_pdfs(); print(f'✓ {len(docs)} PDFs')"

# 3. Verificar BD
python -c "from src.vector_db import VectorDatabase; vdb = VectorDatabase(); print(f'✓ BD con {vdb.get_collection_stats()[\"total_chunks\"]} chunks')"

# 4. Verificar Retriever
python -c "from src.retriever import SimpleRetriever; from src.vector_db import VectorDatabase; ret = SimpleRetriever(VectorDatabase()); res = ret.retrieve('test'); print(f'✓ Retriever ok')"
```

**Checklist:**
- [ ] ✓ Modulos importables
- [ ] ✓ PDFs cargados (20)
- [ ] ✓ BD con chunks
- [ ] ✓ Retriever funciona

---

## 🎉 Instalación Completa

Si todos los checkboxes están marcados ✅, el sistema está **100% operativo**.

### Próximos pasos:
1. Usar Streamlit para explorar datos
2. Hacer consultas y evaluar resultados
3. Ajustar parámetros según necesidad
4. Preparar para Hito 2

---

## 📞 Contacto / Soporte

Si tienes problemas:
1. Revisa sección "Solución de Problemas" arriba
2. Verifica `README.md`
3. Consulta `QUICK_START.md`
4. Revisa logs de errores en terminal

---

**Checklist creado para Preserv-RAG Hito 1**
**Versión: 1.0 - Noviembre 2024**
