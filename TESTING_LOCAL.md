# 🧪 Guía de Testing Local - Preserv-RAG

Esta guía te ayudará a probar el proyecto en tu computador local de forma incremental, identificando y solucionando problemas paso a paso.

---

## 📋 Pre-requisitos

Antes de empezar, verifica que tienes:

- ✅ Python 3.8 o superior
- ✅ pip actualizado
- ✅ 4GB RAM mínimo
- ✅ 1GB espacio en disco
- ✅ Conexión a internet (para primera ejecución)

```bash
# Verificar Python
python --version

# Verificar pip
pip --version

# Verificar espacio
df -h .

# Verificar RAM
free -h  # Linux
# o
vm_stat  # macOS
```

---

## 🚀 Setup Inicial

### 1. Clonar/Descargar el proyecto

```bash
cd proyecto_aplicado
```

### 2. Crear entorno virtual (RECOMENDADO)

```bash
# Crear entorno virtual
python -m venv venv

# Activar
source venv/bin/activate  # Linux/Mac
# o
venv\Scripts\activate  # Windows
```

### 3. Instalar dependencias

```bash
pip install -r requirements.txt
```

**⚠️ Si hay errores de instalación:**
```bash
# Actualizar pip primero
pip install --upgrade pip

# Instalar una por una
pip install PyPDF2==3.0.1
pip install sentence-transformers==2.2.2
pip install chromadb==0.4.22  # Nota: versión actualizada
pip install streamlit==1.28.1
pip install pandas numpy python-dotenv
```

---

## 🧪 Testing Incremental

### Paso 0: Verificar Instalación de Dependencias

```bash
python src/vector_db_fixed.py
```

**Salida esperada:**
```
✓ ChromaDB instalado - Versión: X.X.X
✓ sentence-transformers instalado
✅ TODAS LAS DEPENDENCIAS FUNCIONAN CORRECTAMENTE
```

**Si falla:** Consulta `PROBLEMAS_COMUNES.md`

---

### Paso 1: Test Básico de Python

```bash
python -c "import PyPDF2; import chromadb; import sentence_transformers; print('✓ Todas las librerías OK')"
```

**Si falla:** Reinstala las dependencias.

---

### Paso 2: Test de PDFs Disponibles

```bash
ls -lh data/pdfs/
```

**Verifica que:**
- La carpeta existe
- Hay archivos .pdf dentro
- Los archivos no están corruptos

**Si no hay PDFs:** Añade al menos un PDF académico a `data/pdfs/`

---

### Paso 3: Test de UN SOLO PDF (LO MÁS IMPORTANTE)

Este es el test más importante para identificar problemas:

```bash
python test_single_pdf.py FTB-61-212.pdf
```

**Este script hace:**
1. ✅ Verifica que el PDF existe
2. ✅ Carga el PDF con PyPDF2
3. ✅ Limpia el texto
4. ✅ Divide en chunks
5. ✅ Extrae metadata
6. ✅ Crea embeddings (CRÍTICO - puede fallar aquí)
7. ✅ Indexa en ChromaDB
8. ✅ Hace búsquedas de prueba

**Salida esperada (extracto):**
```
🧪 TEST DE UN SOLO PDF - PRESERV-RAG
======================================================================

1️⃣  VERIFICANDO PDF
----------------------------------------------------------------------
✓ PDF encontrado: data/pdfs/FTB-61-212.pdf
  Tamaño: 687.0 KB

2️⃣  CARGANDO PDF
----------------------------------------------------------------------
✓ PDF cargado exitosamente
  - Páginas: 10
  - Caracteres totales: 45,230
  ...

6️⃣  CREANDO BASE VECTORIAL
----------------------------------------------------------------------
Cargando modelo: all-MiniLM-L6-v2
✓ Modelo de embeddings cargado
✓ 89 chunks indexados en la base vectorial

✅ TEST COMPLETADO EXITOSAMENTE
```

---

### Problemas Comunes en el Paso 3

#### ❌ Error: "ModuleNotFoundError: No module named 'chromadb'"

**Solución:**
```bash
pip install chromadb
```

#### ❌ Error: "AttributeError: 'Settings' object has no attribute 'chroma_db_impl'"

**Problema:** Versión incompatible de ChromaDB

**Solución:**
```bash
pip install --upgrade chromadb

# Si persiste, usa la versión fija
python test_single_pdf.py  # Después de modificar las importaciones
```

**O modifica `test_single_pdf.py` línea 12:**
```python
# CAMBIAR:
from vector_db import VectorDatabase

# POR:
from vector_db_fixed import VectorDatabase
```

#### ❌ Error: "OSError: Can't load tokenizer"

**Problema:** No puede descargar el modelo de HuggingFace

**Solución 1 - Usar modelo más pequeño:**
En `test_single_pdf.py`, línea 108, cambia:
```python
vdb = VectorDatabase(db_path=db_path, model_name="paraphrase-MiniLM-L3-v2")
```

**Solución 2 - Verificar internet:**
```bash
ping huggingface.co
```

**Solución 3 - Descargar manualmente:**
Ver `PROBLEMAS_COMUNES.md` sección "Error al descargar modelo"

#### ❌ Error: "MemoryError" o proceso Killed

**Problema:** No hay suficiente RAM

**Solución 1 - Reducir tamaño de chunks:**
En `test_single_pdf.py`, línea 23, cambia:
```python
chunk_size = 300  # En vez de 500
```

**Solución 2 - Usar PDF más pequeño:**
```bash
python test_single_pdf.py benzoate-sorbate.pdf
```

#### ❌ Error: "PdfReadError" o PDF corrupto

**Problema:** El PDF está mal formado

**Solución:**
Prueba con otro PDF:
```bash
# Listar PDFs disponibles
ls data/pdfs/

# Probar con otro
python test_single_pdf.py antibiotics-08-00208.pdf
```

---

### Paso 4: Test con MÚLTIPLES PDFs

Una vez que el test de un solo PDF funcione, prueba con todos:

```bash
python run_pipeline.py
```

**Este procesará todos los PDFs en `data/pdfs/`**

**Tiempo estimado:** 2-10 minutos dependiendo de:
- Número de PDFs
- Tamaño de PDFs
- Velocidad de CPU

**Si falla por memoria:** Reduce el número de PDFs temporalmente

---

### Paso 5: Test de Interfaz Streamlit

Si el pipeline completo funciona:

```bash
streamlit run streamlit_app.py
```

**Abre el navegador en:** http://localhost:8501

---

## 🔍 Diagnóstico de Problemas

### Script de Diagnóstico Automático

```bash
python -c "
import sys
print(f'Python: {sys.version}')

try:
    import PyPDF2
    print('✓ PyPDF2 instalado')
except:
    print('✗ PyPDF2 NO instalado')

try:
    import chromadb
    print(f'✓ ChromaDB instalado - v{chromadb.__version__}')
except Exception as e:
    print(f'✗ ChromaDB: {e}')

try:
    import sentence_transformers
    print('✓ sentence-transformers instalado')
except:
    print('✗ sentence-transformers NO instalado')

import os
print(f'✓ PDFs disponibles: {len([f for f in os.listdir(\"data/pdfs\") if f.endswith(\".pdf\")])}')
"
```

---

## 📝 Checklist de Testing

Marca cada paso conforme funcione:

- [ ] Dependencias instaladas
  ```bash
  python src/vector_db_fixed.py
  ```

- [ ] PDFs disponibles
  ```bash
  ls data/pdfs/
  ```

- [ ] Test de 1 PDF funciona
  ```bash
  python test_single_pdf.py FTB-61-212.pdf
  ```

- [ ] Pipeline completo funciona
  ```bash
  python run_pipeline.py
  ```

- [ ] Interfaz Streamlit funciona
  ```bash
  streamlit run streamlit_app.py
  ```

---

## 💡 Tips para Testing Exitoso

### 1. Empieza Simple
- Primero 1 PDF
- Luego 3-5 PDFs
- Finalmente todos

### 2. Usa el Script de Test
El script `test_single_pdf.py` está diseñado para:
- Mostrar progreso detallado
- Identificar exactamente dónde falla
- Proporcionar mensajes de error útiles

### 3. Lee los Errores Completos
Copia el stack trace completo cuando reportes errores.

### 4. Verifica Versiones
Si algo no funciona, verifica las versiones:
```bash
pip list | grep -E "chromadb|sentence-transformers|PyPDF2"
```

### 5. Entorno Limpio
Si nada funciona, crea un entorno completamente nuevo:
```bash
deactivate  # Si estás en un venv
python -m venv venv_nuevo
source venv_nuevo/bin/activate
pip install -r requirements.txt
python test_single_pdf.py
```

---

## 🎯 Objetivos de Testing

### Mínimo Viable (para aprobar pruebas):
✅ Test de 1 PDF funciona

### Objetivo Completo:
✅ Pipeline completo funciona con todos los PDFs
✅ Interfaz Streamlit funciona
✅ Búsquedas retornan resultados relevantes

---

## 📊 Métricas de Éxito

Después del test de 1 PDF, deberías ver:

```
📊 RESUMEN:
  - PDF procesado: FTB-61-212.pdf
  - Páginas: 10
  - Chunks creados: 89
  - Chunks con metadata: 25
  - Base de datos: data/test_chroma_db
```

**Valores aceptables:**
- ✅ Chunks creados > 0
- ✅ Al menos algunos chunks con metadata
- ✅ Búsquedas retornan resultados (similitud > 0.3)

---

## 🆘 Ayuda Adicional

Si después de seguir esta guía aún tienes problemas:

1. **Revisa:** `PROBLEMAS_COMUNES.md`
2. **Ejecuta:** Diagnóstico completo
   ```bash
   python test_single_pdf.py > test_output.txt 2>&1
   cat test_output.txt
   ```
3. **Reporta:** El error completo con:
   - Sistema operativo
   - Versión de Python
   - Output del comando que falla
   - Stack trace completo

---

## 🎓 Archivos de Ayuda

- `test_single_pdf.py` - Script de test simplificado
- `PROBLEMAS_COMUNES.md` - Soluciones a errores frecuentes
- `src/vector_db_fixed.py` - Versión mejorada de vector_db
- `README.md` - Documentación general del proyecto

---

## ✅ Flujo Recomendado

```
1. Verificar instalación
   ↓
2. Test de 1 PDF
   ↓
3. ¿Funcionó?
   ├─ SÍ → Pipeline completo
   └─ NO → Revisar PROBLEMAS_COMUNES.md
            ↓
            Aplicar solución
            ↓
            Volver al paso 2
```

---

**¡Buena suerte con el testing! 🚀**
