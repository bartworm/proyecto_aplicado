# 🔧 Problemas Comunes y Soluciones

Este documento lista los problemas más comunes al ejecutar el proyecto localmente y sus soluciones.

---

## ❌ Problema 1: Error con ChromaDB al inicializar

### Síntomas:
```
AttributeError: 'Settings' object has no attribute 'chroma_db_impl'
TypeError: Settings.__init__() got an unexpected keyword argument 'chroma_db_impl'
ValueError: Could not connect to database
```

### Causa:
La versión de ChromaDB especificada (0.4.14) tiene incompatibilidades con la forma en que se inicializa el cliente en `src/vector_db.py`.

### Solución:

**Opción A: Actualizar ChromaDB (Recomendado)**

1. Actualiza `requirements.txt`:
   ```
   chromadb>=0.4.22
   ```

2. Reinstala:
   ```bash
   pip install --upgrade chromadb
   ```

3. El código actual debería funcionar, pero si no, modifica `src/vector_db.py` línea 32-37:

   **ANTES:**
   ```python
   settings = Settings(
       chroma_db_impl="duckdb+parquet",
       persist_directory=db_path,
       anonymized_telemetry=False,
   )
   self.client = chromadb.Client(settings)
   ```

   **DESPUÉS:**
   ```python
   self.client = chromadb.PersistentClient(
       path=db_path,
       settings=Settings(anonymized_telemetry=False)
   )
   ```

**Opción B: Usar versión específica compatible**

```bash
pip install chromadb==0.4.22
```

---

## ❌ Problema 2: Error al descargar modelo de sentence-transformers

### Síntomas:
```
OSError: Can't load tokenizer for 'sentence-transformers/all-MiniLM-L6-v2'
ConnectionError: HTTPSConnectionPool
```

### Causa:
- No hay conexión a internet para descargar el modelo (~90MB)
- Firewall/proxy bloqueando HuggingFace

### Solución:

**Opción A: Descargar manualmente**

1. Descarga el modelo desde: https://huggingface.co/sentence-transformers/all-MiniLM-L6-v2

2. Colócalo en `~/.cache/torch/sentence_transformers/`

3. O especifica la ruta local:
   ```python
   vdb = VectorDatabase(model_name="/ruta/al/modelo/local")
   ```

**Opción B: Usar modelo más ligero**

En `run_pipeline.py` o `test_single_pdf.py`, cambia:
```python
vdb = VectorDatabase(model_name="all-MiniLM-L6-v2")
```

Por:
```python
vdb = VectorDatabase(model_name="paraphrase-MiniLM-L3-v2")  # Más ligero
```

---

## ❌ Problema 3: No se encuentran los PDFs

### Síntomas:
```
FileNotFoundError: Carpeta no encontrada: data/pdfs
FileNotFoundError: No se encontraron PDFs en: data/pdfs
```

### Causa:
La carpeta `data/pdfs` está vacía o no existe.

### Solución:

1. Verifica la estructura:
   ```bash
   ls -la data/pdfs/
   ```

2. Si no hay PDFs, coloca al menos uno:
   ```bash
   # Asegúrate de que hay archivos .pdf en data/pdfs/
   ```

3. Para pruebas rápidas, usa el script de un solo PDF:
   ```bash
   python test_single_pdf.py nombre_del_pdf.pdf
   ```

---

## ❌ Problema 4: Error de memoria (RAM insuficiente)

### Síntomas:
```
MemoryError
Killed (proceso terminado por el SO)
```

### Causa:
Procesar muchos PDFs grandes consume mucha RAM al generar embeddings.

### Solución:

**Opción A: Procesar en lotes pequeños**

Modifica `src/vector_db.py`, método `add_chunks`:

```python
def add_chunks(self, chunks: List[Dict[str, Any]], batch_size: int = 50) -> None:
    """Añade chunks en lotes para evitar problemas de memoria."""

    for i in range(0, len(chunks), batch_size):
        batch = chunks[i:i + batch_size]
        # ... resto del código procesando batch en vez de chunks
```

**Opción B: Usar modelo más pequeño**

```python
vdb = VectorDatabase(model_name="paraphrase-MiniLM-L3-v2")
```

**Opción C: Reducir tamaño de chunks**

En `run_pipeline.py`:
```python
chunk_size = 300  # En vez de 500
```

**Opción D: Procesar un solo PDF primero**

```bash
python test_single_pdf.py FTB-61-212.pdf
```

---

## ❌ Problema 5: Error con PyPDF2

### Síntomas:
```
PdfReadError: PDF starts with
AttributeError: 'PdfReader' object has no attribute 'getNumPages'
```

### Causa:
- PDF corrupto o mal formado
- Versión incompatible de PyPDF2

### Solución:

**Opción A: Actualizar PyPDF2**

```bash
pip install --upgrade PyPDF2
```

**Opción B: Probar con PDF diferente**

Algunos PDFs están mal formados. Prueba con otro:
```bash
python test_single_pdf.py benzoate-sorbate.pdf
```

**Opción C: Usar pypdf (fork más reciente)**

En `requirements.txt`:
```
pypdf>=3.17.0  # En vez de PyPDF2
```

En `src/data_ingestion.py`:
```python
import pypdf  # En vez de PyPDF2
```

---

## ❌ Problema 6: Importaciones no encontradas

### Síntomas:
```
ModuleNotFoundError: No module named 'chromadb'
ModuleNotFoundError: No module named 'sentence_transformers'
```

### Causa:
Dependencias no instaladas.

### Solución:

```bash
# Reinstalar todas las dependencias
pip install -r requirements.txt

# O instalar manualmente
pip install PyPDF2 sentence-transformers chromadb streamlit pandas numpy python-dotenv
```

Si usas un entorno virtual, asegúrate de activarlo primero:
```bash
source venv/bin/activate  # Linux/Mac
# o
venv\Scripts\activate  # Windows
```

---

## ❌ Problema 7: ChromaDB - "No embedding function provided"

### Síntomas:
```
ValueError: You must provide an embedding function or pass embeddings
InvalidArgumentError: embedding function required
```

### Causa:
Estás usando una versión muy reciente de ChromaDB que cambió la API.

### Solución:

Modifica `src/vector_db.py`, método `__init__`:

```python
from chromadb.utils import embedding_functions

# En __init__, después de cargar el embedder:
self.embedder = SentenceTransformer(model_name)

# Crear función de embedding para Chroma
self.embedding_function = embedding_functions.SentenceTransformerEmbeddingFunction(
    model_name=model_name
)

# Al crear colección:
self.collection = self.client.get_or_create_collection(
    name="preserv_rag",
    embedding_function=self.embedding_function,
    metadata={"hnsw:space": "cosine"}
)
```

---

## ❌ Problema 8: Permisos denegados al crear carpetas

### Síntomas:
```
PermissionError: [Errno 13] Permission denied: 'data/chroma_db'
```

### Causa:
No tienes permisos para escribir en la carpeta.

### Solución:

```bash
# Dar permisos de escritura
chmod -R 755 data/

# O ejecutar con permisos de usuario actual
python test_single_pdf.py
```

---

## ✅ Flujo de Debugging Recomendado

### 1. Primero, verifica instalación básica:
```bash
python -c "import PyPDF2; import chromadb; import sentence_transformers; print('✓ Todas las librerías instaladas')"
```

### 2. Prueba con un solo PDF:
```bash
python test_single_pdf.py FTB-61-212.pdf
```

### 3. Si funciona, prueba con el pipeline completo:
```bash
python run_pipeline.py
```

### 4. Si el pipeline funciona, prueba la interfaz:
```bash
streamlit run streamlit_app.py
```

---

## 📋 Checklist de Verificación

Antes de reportar un problema, verifica:

- [ ] ¿Tienes Python 3.8 o superior?
  ```bash
  python --version
  ```

- [ ] ¿Están instaladas todas las dependencias?
  ```bash
  pip list | grep -E "chromadb|sentence-transformers|PyPDF2"
  ```

- [ ] ¿Existe la carpeta data/pdfs con PDFs dentro?
  ```bash
  ls -lh data/pdfs/
  ```

- [ ] ¿Tienes conexión a internet? (para descargar modelo)
  ```bash
  ping huggingface.co -c 3
  ```

- [ ] ¿Tienes suficiente espacio en disco? (mínimo 1GB libre)
  ```bash
  df -h .
  ```

- [ ] ¿Tienes suficiente RAM? (mínimo 4GB recomendado)
  ```bash
  free -h
  ```

---

## 🆘 Si nada funciona...

1. **Crea un entorno limpio:**
   ```bash
   python -m venv venv_nuevo
   source venv_nuevo/bin/activate
   pip install -r requirements.txt
   ```

2. **Usa las versiones exactas que funcionan:**
   ```bash
   pip install PyPDF2==3.0.1 chromadb==0.4.22 sentence-transformers==2.2.2
   ```

3. **Prueba el script de test simplificado:**
   ```bash
   python test_single_pdf.py FTB-61-212.pdf
   ```

4. **Si aún así falla, reporta el error con:**
   - Versión de Python (`python --version`)
   - Sistema operativo
   - Output completo del error
   - Stack trace completo

---

## 📞 Soporte

Si encuentras un error no documentado aquí:

1. Ejecuta con logging detallado:
   ```bash
   python test_single_pdf.py 2>&1 | tee error.log
   ```

2. Revisa el stack trace completo

3. Busca el error en: https://github.com/chroma-core/chroma/issues

4. Consulta docs de ChromaDB: https://docs.trychroma.com/
