# 🧠 BI Backend API con FastAPI + PostgreSQL

Este proyecto es un backend construido con **FastAPI** que permite conectarse a una base de datos **PostgreSQL**, obtener tablas, columnas, relaciones, generar gráficos y crear consultas SQL inteligentes usando **OpenAI**.

---

## 🚀 Tecnologías

- Python 3.11+
- FastAPI
- SQLAlchemy
- PostgreSQL
- Uvicorn

---

## 📦 Requisitos previos

- Python 3.10 o superior
- PostgreSQL

- (opcional) Virtualenv o venv

---

## ⚙️ Instalación

```bash
# 1. Clona el repositorio
git clone https://github.com/keremyalex/bi_backend.git
cd bi_backend

# 2. Crea un entorno virtual
python -m venv env
source env/bin/activate  # En Windows: env\Scripts\activate

# 3. Instala las dependencias
pip install -r requirements.txt

# 4. Ejecución
uvicorn app.main:app --reload