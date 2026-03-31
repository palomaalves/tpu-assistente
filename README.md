# TPU Assistente — Consulta das Tabelas Processuais Unificadas do CNJ

> Extração automatizada e consulta em linguagem natural das Tabelas Processuais Unificadas (TPU) do Conselho Nacional de Justiça (CNJ), com interface conversacional via IA.

---

## Sobre o Projeto

As **Tabelas Processuais Unificadas (TPU)** são padronizações obrigatórias definidas pelo CNJ para classificação de classes, assuntos e movimentos processuais em todo o Poder Judiciário brasileiro. Elas são atualizadas mensalmente e publicadas pelo Sistema de Gestão de Tabelas (SGT).

Este projeto oferece:

- **Extração automatizada** das 3 tabelas TPU diretamente do WebService SOAP do SGT/CNJ
- **Geração de arquivos JSON e Excel** formatados e prontos para uso
- **Interface de consulta em linguagem natural** via Artifact no Claude (sem necessidade de API Key própria)

---

## Tabelas Extraídas

| Tabela | Tipo | Registros (jan/2026) | Arquivo |
|--------|------|----------------------|---------|
| Classes Processuais | `C` | 847 | `classes_sgt_cnj` |
| Assuntos | `A` | 5.598 | `assuntos_sgt_cnj` |
| Movimentos | `M` | 957 | `movimentos_sgt_cnj` |

---

## Estrutura do Repositório

```
tpu-assistente/
├── extrair_TPU_SGT_json.py      # Script de extração — gera apenas JSON
├── extrair_TPU_SGT_json_1.py    # Script de extração — gera JSON + Excel formatado
├── classes_sgt_cnj.json         # Dados extraídos — Classes
├── assuntos_sgt_cnj.json        # Dados extraídos — Assuntos
├── movimentos_sgt_cnj.json      # Dados extraídos — Movimentos
├── classes_sgt_cnj.xlsx         # Planilha formatada — Classes
├── assuntos_sgt_cnj.xlsx        # Planilha formatada — Assuntos
└── movimentos_sgt_cnj.xlsx      # Planilha formatada — Movimentos
```

---

## Como Usar

### Pré-requisitos

```bash
pip install requests openpyxl
```

### Extração (apenas JSON)

```bash
python extrair_TPU_SGT_json.py
```

Gera em `Documentos/`:
- `classes_sgt_cnj.json`
- `assuntos_sgt_cnj.json`
- `movimentos_sgt_cnj.json`

### Extração completa (JSON + Excel)

```bash
python extrair_TPU_SGT_json_1.py
```

Gera em `Documentos/` os mesmos arquivos `.json` mais os `.xlsx` com formatação profissional (cores por nível hierárquico, filtros automáticos, cabeçalho fixo).

---

## Estrutura dos Dados

Cada registro nas tabelas possui os seguintes campos:

| Campo | Descrição |
|-------|-----------|
| `codigo` | Código identificador do item |
| `nome` | Descrição do item |
| `nivel` | Nível na hierarquia (1 = raiz) |
| `hierarquia` | Caminho completo (ex: `Cível > Família > Alimentos`) |
| `codigo_pai` | Código do item pai |
| `nome_pai` | Descrição do item pai |
| `ativo` | `Sim` ou `Nao` |
| `glossario` | Definição/observação do CNJ (quando disponível) |

---

## Como Funciona a Extração

O script utiliza o **WebService SOAP público do SGT/CNJ** — sem necessidade de login, token ou autenticação:

```
Endpoint: https://www.cnj.jus.br/sgt/sgt_ws.php
Operação: getArrayFilhosItemPublicoWS
```

A árvore hierárquica é percorrida recursivamente a partir da raiz (`seq=0`) para cada tipo de tabela (`C`, `A`, `M`), com um delay de 200ms entre chamadas para respeitar o servidor.

```
getDataUltimaVersao()           → verifica versão atual
getArrayFilhosItemPublicoWS(0)  → raiz de cada tabela
  └─ getArrayFilhosItemPublicoWS(n) → filhos recursivos (BFS)
```

---

## Interface de Consulta em Linguagem Natural

Os arquivos `.json` gerados podem ser carregados no **Assistente TPU** (Artifact no Claude.ai), permitindo consultas como:

- *"Qual o código da classe processual para ação de alimentos?"*
- *"Quais assuntos existem para crimes ambientais?"*
- *"Me mostre os movimentos relacionados a sentença condenatória"*

A interface usa a IA do Claude embutida no Artifact — **sem necessidade de API Key própria**.

---

## Atualização Mensal

As TPUs são atualizadas mensalmente pelo CNJ. Para atualizar os dados:

```bash
python extrair_TPU_SGT_json.py
```

A versão atual das tabelas é exibida no início da execução:

```
Versao das tabelas: 29/01/2026
```

---

## Fonte dos Dados

- **CNJ — Sistema de Gestão de Tabelas (SGT):** https://www.cnj.jus.br/sgt/
- **WebService público:** https://www.cnj.jus.br/sgt/sgt_ws.php
- **Página oficial TPU:** https://www.cnj.jus.br/programas-e-acoes/tabela-processuais-unificadas/

---

## Contexto Institucional

Projeto desenvolvido na **Coordenadoria de Governança de Dados** do **Tribunal de Justiça de Pernambuco (TJPE)**, com o objetivo de facilitar a consulta e o cruzamento das TPUs com bases processuais internas.

---

## Licença

Dados públicos fornecidos pelo CNJ sob acesso livre. Os scripts deste repositório estão disponíveis para uso e adaptação.
