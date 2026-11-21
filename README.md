# Sistema de Ocorrências Georreferenciadas

Sistema web monolítico para gerenciamento e rastreamento de ocorrências com suporte a geoprocessamento, desenvolvido em **Django 5.2 LTS** e **PostGIS**, com foco em padrões acadêmicos de alta qualidade de código e testes automatizados.

## 🛠️ Stack Tecnológica

* **Backend & Servidor:** Python 3.12 (com suporte a versões 3.10+), Django 5.2 LTS
* **Banco de Dados:** PostgreSQL com extensão espacial **PostGIS** (GeoDjango nativo)
* **Frontend:** Server-Side Rendering (SSR) com Django Templates, Tailwind CSS (via CDN) e Leaflet.js (para mapas interativos)
* **Qualidade de Código & Linters:** Ruff (formatação e linting estrito com regras Django) e Mypy (tipagem estática estrita com `django-stubs`)
* **Testes Automatizados:** Pytest, `pytest-django` e `pytest-cov`; testes de unidade do Back e testes de integração da aplicação Django.

## 📂 Estrutura do Projeto

O projeto adota uma arquitetura monolítica organizada sob o diretório `backend/`:

```text
.
├── README.md
├── docs/
│   └── FRONTEND.md
└── backend/
    ├── manage.py
    ├── pyproject.toml
    ├── requirements.txt
    ├── setup/
    │   ├── asgi.py
    │   ├── settings.py
    │   ├── urls.py
    │   └── wsgi.py
    ├── templates/
    │   └── base.html
    └── usuarios/
        ├── migrations/
        ├── templates/usuarios/
        │   ├── cadastro.html
        │   └── login.html
        ├── tests/
        │   ├── test_cadastro_integracao.py
        │   └── test_cadastro_unidade.py
        ├── admin.py
        ├── apps.py
        ├── forms.py
        ├── models.py
        ├── urls.py
        └── views.py
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

## 🗃️ Usando o SQLite no desenvolvimento

Enquanto o banco padrão do projeto for o SQLite, o Django usa o arquivo `backend/db.sqlite3` (configurado em `backend/setup/settings.py`). Para abrir esse banco pelo terminal, primeiro entre na pasta `backend/`:

```bash
cd backend
sqlite3 db.sqlite3
```

No prompt do SQLite (`sqlite>`), use os comandos próprios do `sqlite3`:

```text
.tables
.schema auth_user
.schema usuarios_usuario
.quit
```

`.tables` lista as tabelas, `.schema auth_user` mostra a estrutura da tabela de usuários do Django e `.quit` fecha o SQLite. `.schema usuarios_usuario` só será útil se essa tabela existir: o cadastro atual usa o modelo padrão do Django, armazenado em `auth_user`.

Para consultar os usuários, execute SQL no prompt `sqlite>` (cada consulta termina com ponto e vírgula):

```sql
SELECT id, username FROM auth_user;
```

Os comandos que começam com ponto são comandos do programa `sqlite3`, não instruções SQL. Para conferir qual arquivo SQLite o Django está usando, veja `DATABASES` em `setup/settings.py`.

Também é possível abrir o banco configurado pelo Django, sem informar o caminho diretamente:

```bash
python manage.py dbshell
```

Esse comando requer que o executável `sqlite3` esteja instalado e disponível no `PATH`.

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
* **Execução de testes (unidade e integração):**
  ```bash
  pytest
  ```

Os testes de unidade do Back ficam em `backend/tests/` ou em módulos `test_*.py` dentro da pasta `tests/` de cada app, sem depender de ciclo HTTP completo, template ou banco quando isso não for necessário. Os testes de integração Django exercitam a ligação entre URL, view, formulário, banco e resposta; ficam em módulos `test_*_integracao.py` nessa pasta (por exemplo, `backend/usuarios/tests/test_cadastro_integracao.py`). O time de Front pode assumir a manutenção dos testes de integração voltados às telas, incluindo status, templates, contexto e HTML renderizado. Regras de negócio e comportamento isolado dos componentes Python continuam cobertos pelos testes de unidade do Back.

A meta de cobertura deve ser definida para o conjunto que o grupo acordar; cobertura agregada não substitui a separação de responsabilidades entre os tipos de teste.

## 📝 Padrões de commits

As mensagens de commit seguem o formato:

```text
<tipo>: <descrição curta no presente>
```

Usamos estes tipos para indicar a intenção da mudança:

* `feat`: adiciona uma funcionalidade.
* `fix`: corrige um comportamento incorreto.
* `test`: adiciona ou altera testes, sem implementar a funcionalidade correspondente.
* `refactor`: reorganiza o código sem mudar o comportamento.
* `docs`: atualiza documentação.
* `chore`: faz manutenção ou atualiza configurações e ferramentas.

Exemplos do histórico deste projeto:

```text
test: define fluxo de cadastro por template
feat: implementa cadastro integrado ao template
refactor: simplifica fluxo da view de cadastro
chore: atualiza arquivos
```

Quando o trabalho usar TDD, registramos as etapas em commits separados: primeiro o teste que falha (`test`), depois a implementação que o faz passar (`feat` ou `fix`) e, por fim, a refatoração (`refactor`).
