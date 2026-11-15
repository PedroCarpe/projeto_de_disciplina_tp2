# Sistema de Registro e Acompanhamento de Ocorrências

Sistema desenvolvido para o projeto da disciplina de **Técnicas de Programação 2 (UnB)**, permitindo o registro geolocalizado de ocorrências urbanas, visualização em mapas interativos e painel estatístico para administradores.

---

## 🚀 Tecnologias Utilizadas

* **Backend:** Python 3.10+, Django, Django REST Framework
* **Banco de Dados:** PostgreSQL + PostGIS (GeoDjango)
* **Frontend:** React, Vite, TypeScript, Leaflet.js (Mapas), Chart.js (Gráficos)
* **Qualidade e Padrão de Código:** Ruff (PEP 8) e Google TypeScript Style Guide (`gts`), Mypy, TypeScript strict mode
* **Testes e Cobertura:** Pytest (`pytest-cov`) e Vitest (Meta de cobertura: $\ge 80\%$)
* **Documentação:** Sphinx e TypeDoc

---

## 📂 Estrutura do Repositório

```text
sistema-ocorrencias/
├── backend/          # API REST em Django e testes com pytest
├── 
└── .gitignore