# Sistema de Ocorrências Georreferenciadas

Sistema web monolítico para gerenciamento e rastreamento de ocorrências com suporte a geoprocessamento, desenvolvido em **Django 5.2 LTS** e **PostGIS**, com foco em padrões acadêmicos de alta qualidade de código e testes automatizados.

## 🛠️ Stack Tecnológica

* **Backend & Servidor:** Python 3.12 (com suporte a versões 3.10+), Django 5.2 LTS
* **Banco de Dados:** PostgreSQL com extensão espacial **PostGIS** (GeoDjango nativo)
* **Frontend:** Server-Side Rendering (SSR) com Django Templates, Tailwind CSS (via CDN) e Leaflet.js (para mapas interativos)
* **Qualidade de Código & Linters:** Ruff (formatação e linting estrito com regras Django) e Mypy (tipagem estática estrita com `django-stubs`)
* **Testes Automatizados:** Pytest, `pytest-django` e `pytest-cov` (Meta de cobertura $\ge 80\%$)

## 📂 Estrutura do Projeto

O projeto adota uma arquitetura monolítica organizada sob o diretório `backend/`, refletindo a seguinte árvore de diretórios:

```text
.
├── backend
│   ├── db.sqlite3
│   ├── manage.py
│   ├── pyproject.toml
│   ├── requirements.txt
│   └── setup
│       ├── asgi.py
│       ├── __init__.py
│       ├── __pycache__
│       │   ├── __init__.cpython-312.pyc
│       │   ├── settings.cpython-312.pyc
│       │   ├── urls.cpython-312.pyc
│       │   └── wsgi.cpython-312.pyc
│       ├── settings.py
│       ├── urls.py
│       └── wsgi.py
```

## ⚙️ Pré-requisitos e Instalação

### 1. Configuração Inicial do Repositório (Git)
Para garantir compatibilidade entre ambientes Linux (Ubuntu) e Windows na equipe, configure o tratamento de quebras de linha:
```bash
git config --global core.autocrlf input
```

### 2. Configurando o Ambiente Virtual e Dependências Python
Acesse a pasta `backend/`, crie o ambiente virtual oculto (`.venv`) e instale as dependências:
```bash
cd backend

# Criar o ambiente virtual
python -m venv .venv

# Ativar no Linux / Ubuntu:
source .venv/bin/activate

# Ativar no Windows (PowerShell):
# .\.venv\Scripts\Activate

# Instalar os pacotes
pip install -r requirements.txt
```

## 🌍 Dependências Geoespaciais (GeoDjango & PostGIS)

Como o sistema lida com georreferenciamento, o Django utiliza o módulo nativo `django.contrib.gis` (GeoDjango). Além do banco de dados PostgreSQL com a extensão PostGIS ativa, o sistema operacional precisa das bibliotecas C de geoprocessamento (**GDAL** e **GEOS**).

### Instalação no Linux (Ubuntu)
No Ubuntu, a instalação das bibliotecas C é feita diretamente pelo gerenciador de pacotes do sistema:
```bash
sudo apt-get update
sudo apt-get install binutils libproj-dev gdal-bin libgdal-dev
```

### Instalação no Windows
No Windows, como o ambiente de desenvolvimento da equipe é misto, siga os passos abaixo:
1. Instale o **PostgreSQL** com a extensão **PostGIS** ativada.
2. Utilize o instalador **OSGeo4W** ou baixe os binários pré-compilados compatíveis com a sua versão do Python/GDAL.

## 🗄️ Configuração do Banco de Dados (PostGIS)

No seu servidor PostgreSQL, crie um banco de dados dedicado ao projeto e ative a extensão espacial PostGIS:

```sql
CREATE DATABASE sistema_ocorrencias;
\c sistema_ocorrencias;
CREATE EXTENSION postgis;
```

## 🚀 Executando o Projeto

Com o ambiente virtual ativado e as dependências instaladas na pasta `backend/`, aplique as migrações e inicie o servidor:

```bash
python manage.py migrate
python manage.py runserver
```

Acesse no navegador: `http://127.0.0.1:8000/`

## 🧪 Qualidade de Código e Testes

O projeto utiliza ferramentas estritas para garantir rigor acadêmico e estabilidade:

* **Linting e Formatação (Ruff):**
  ```bash
  ruff check .
  ```
* **Checagem de Tipos Estáticos (Mypy):**
  ```bash
  mypy .
  ```
* **Execução de Testes com Cobertura ($\ge 80\%$):**
  ```bash
  pytest
  ```