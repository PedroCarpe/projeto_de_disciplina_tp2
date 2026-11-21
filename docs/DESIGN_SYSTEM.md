# Design system do frontend — Nossa Rua

Nome do produto em todas as telas: **Nossa Rua**.

Fonte única: `backend/static/css/app.css`. `base.html` apenas carrega esse CSS.
Todas as telas devem reutilizar tokens e classes — não crie cores, raios ou sombras locais.

## Paleta oficial

Linguagem visual alinhada à referência enviada, com o nome **Nossa Rua**.

| Variável | Hex | Uso |
| --- | --- | --- |
| `--creme` | `#FBF8F3` | Fundo das telas |
| `--tinta` | `#26323B` | Texto principal |
| `--verde` | `#2F6B55` | Ação, links e logotipo |
| `--verde-escuro` | `#1F5240` | Botão principal |
| `--verde-escuro-hover` | `#173E31` | Hover do botão principal |
| `--menta` | `#D5EBDF` | Resolvido / acentos suaves |
| `--lavanda` | `#E1DCF5` | Registrada |
| `--pessego` | `#FFDFCF` | Destaque e ponto do logotipo |
| `--ceu` | `#D6E8F5` | Em andamento |
| `--manteiga` | `#FBF0C8` | Em análise |
| `--branco` | `#FFFFFF` | Painéis e campos |

Aliases mantidos: `--verde-creme`, `--branco-quente`, `--salvia`. Derivados: `--texto-secundario` (`#5E6B73`), `--verde-cinza`, `--borda` (`#EDE6DB`), `--linha`, `--placeholder`. Validação: `--erro` (`#9B3B2E`) e `--erro-suave` (`#FBE9E4`).

Fonte: **Nunito** (400/600/700/800). Raios: campos `18px`, botões `16px`, cartões `22px`.

## Papéis semânticos

Use sempre: `--cor-fundo`, `--cor-painel`, `--cor-texto`, `--cor-texto-muto`, `--cor-borda`, `--cor-destaque`, `--cor-link`, `--cor-foco`, `--cor-placeholder`.

## Logotipo

Include reutilizável: `{% include "includes/logo.html" %}`.

Composição: quadrado verde arredondado com pin branco, centro verde e ponto pêssego + `Nossa Rua` em **Nunito ExtraBold (800)**, cor `#2F6B55`, com o ponto final em `#FFDFCF`. Sem sombra, 3D ou gradiente.

| Classe | Função |
| --- | --- |
| `.marca` | Contêiner alinhado horizontalmente |
| `.marca__icone` | Quadrado verde com pin |
| `.marca__pin`, `.marca__centro`, `.marca__brilho` | Partes do pin |
| `.marca__nome` | Texto da marca |
| `.marca__ponto` | Ponto final em pêssego |

## Componentes compartilhados

| Grupo | Classes |
| --- | --- |
| Estrutura | `.autenticacao`, `.apresentacao`, `.apresentacao__conteudo`, `.acesso`, `.acesso__conteudo` |
| Apresentação | `.apresentacao__frases`, `.apresentacao__frase`, `.apresentacao__frase-secundaria`, `.linha-mapa` |
| Texto de acesso | `.etiqueta`, `.etiqueta__icone`, `.acesso__titulo`, `.acesso__subtitulo`, `.acesso__visitante` |
| Alternador | `.alternador`, `.alternador__opcao`, `.alternador__opcao--ativa` |
| Formulário | `.formulario`, `.campo`, `.campo__etiqueta`, `.campo__grupo`, `.campo__icone`, `.campo__controle`, `.campo__acao` |
| Validação | `.aviso-erro`, `.aviso-sucesso`, `.campo__grupo--invalido`, `.campo__erro` |
| Botão e link | `.ligacao`, `.botao`, `.botao--primario`, `.botao--secundario`, `.botao__seta` |
| Página inicial | `.inicio`, `.inicio__cabecalho`, `.inicio__acoes`, `.inicio__hero`, `.inicio__titulo`, `.inicio__descricao`, `.inicio__recursos`, `.recurso`, `.recurso--pessego`, `.recurso--ceu`, `.recurso--menta`, `.inicio__estados`, `.estado`, `.estado--registrada`, `.estado--analise`, `.estado--andamento`, `.estado--resolvida` |

## Regras

1. Estenda `base.html` e use `{% block content %}`.
2. Reutilize as classes acima antes de criar novas.
3. Nunca use hexadecimal direto na página; ajuste o token em `app.css`.
4. Mobile primeiro: uma coluna; a partir de `48rem`, apresentação à esquerda e formulário à direita.
5. Campos, botões e links continuam sendo HTML real e acessível.
6. Telas de autenticação: `/login/` e `/cadastro/`. O cadastro usa os mesmos componentes do login e exibe erros via `.aviso-erro` e `.campo__erro` (servidor e JavaScript), e sucesso via `.aviso-sucesso`.
7. Cadastro: usa o `User` padrão do Django com `username = e-mail`; e-mail é único (comparação sem diferenciar maiúsculas) e a senha é salva com hash.
8. Página inicial pública em `/` (`name="inicio"`), servida por `home_view`; “Explorar como visitante” no login aponta para ela. Cartões e pastéis seguem os tokens existentes.
