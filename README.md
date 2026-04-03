# ✨ Luminar de Dados — Iluminando Vidas

> **Análise do impacto educacional e social da ONG Passos Mágicos**  
> Datathon · PósTech Data Analytics · FIAP

[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://ongpasos-magicos.streamlit.app/)
![Python](https://img.shields.io/badge/Python-3.11-blue?logo=python&logoColor=white)
![Streamlit](https://img.shields.io/badge/Streamlit-1.36-FF4B4B?logo=streamlit&logoColor=white)
![scikit-learn](https://img.shields.io/badge/scikit--learn-1.3-F7931E?logo=scikit-learn&logoColor=white)
![Plotly](https://img.shields.io/badge/Plotly-5.15-3F4F75?logo=plotly&logoColor=white)

---

## 🎯 Sobre o projeto

A [Passos Mágicos](https://passosmagicos.org.br/) é uma ONG fundada em 1992 que transforma a vida de crianças e jovens em situação de vulnerabilidade social em Embu-Guaçu, SP. Por 31 anos, o programa combina educação acelerada, suporte psicológico e protagonismo juvenil para romper o ciclo de pobreza.

Este projeto aplica **análise de dados, visualização interativa e machine learning** sobre os dados PEDE (Pesquisa Extensiva do Desenvolvimento Educacional) de 2020, 2021 e 2022 para:

- Quantificar o impacto real do programa com evidências
- Identificar os fatores que mais influenciam o desenvolvimento dos alunos
- Construir modelos preditivos com utilidade operacional para a ONG
- Fornecer um simulador interativo para avaliação de perfis individuais

---

## 🔍 Principais descobertas

| Achado | Dado |
|--------|------|
| **Bolsistas têm 4× mais Ponto de Virada** | 38,9% vs 9,4% dos não bolsistas |
| **Alunos Topázio cresceram 41%** | De 92 (2020) para 130 (2022) |
| **43% de retenção longitudinal** | Dos 727 alunos de 2020, apenas 314 aparecem nos 3 anos |
| **73 alunos multi-vulneráveis** | IPS + IAA abaixo do P25 — risco crítico sem intervenção |
| **Fórmula INDE confirmada** | `IDA×20% + IEG×20% + IPV×20% + outros×10%` — verificado com R²=1,000 |
| **Hipótese de gênero refutada** | Taxa de evasão: F=53% vs M=57% — diferença de 4 p.p. sem relevância |

---

## 🤖 Modelos preditivos

Dois modelos Random Forest com valor operacional real para a ONG:

**Risco de Evasão** — prediz quais alunos têm maior probabilidade de não comparecer ao próximo ciclo, usando dados do período anterior (sem data leakage).

```
AUC-ROC = 0.65  |  Features: INDE, IPV, IDA, IEG, Fase, IAA, IPP
```

**Probabilidade de Ponto de Virada** — prediz quais alunos têm maior chance de atingir uma transformação significativa no ciclo atual.

```
AUC-ROC = 0.98  |  Feature dominante: IPV (43% de importância)
```

> 💡 **Por que não modelar o INDE?** O INDE é uma fórmula determinística confirmada nos dados com R²=1,000. Modelá-lo com ML seria redundante — o modelo simplesmente aprenderia a fórmula. Os modelos aqui focam em tarefas com incerteza real e valor operacional.

---

## 🎯 Simulador interativo

A página **Simulador** permite que coordenadores da ONG insiram os indicadores de um aluno e recebam em tempo real:

- Score de risco de evasão com classificação (Baixo / Médio / Alto)
- Probabilidade de Ponto de Virada
- INDE calculado automaticamente pela fórmula oficial
- Recomendação personalizada baseada na combinação dos dois scores

---

## 🗂️ Estrutura do projeto

```
📦 ongpasos-magicos
├── main.py                          # Entry point + navegação
├── requirements.txt
├── pages/
│   ├── 0_Visao_Geral.py            # ✨ KPIs executivos e visão macro
│   ├── 1_Analise_Exploratoria.py   # 📊 EDA: INDE, pedras, gênero, defasagem
│   ├── 2_Modelos_Preditivos.py     # 🤖 Modelos de evasão e Ponto de Virada
│   ├── 3_Conclusoes.py             # 💡 Recomendações baseadas em dados
│   └── 4_Simulador.py             # 🎯 Simulador interativo por aluno
├── util/
│   ├── style.py                    # Design system: cores, layout, componentes
│   ├── data.py                     # Carregamento e cache dos dados
│   └── layout.py                   # Sidebar de navegação
└── *.csv                           # Datasets PEDE 2020–2022 + tabelas auxiliares
```

---

## 🛠️ Stack técnico

| Categoria | Tecnologias |
|-----------|------------|
| **Linguagem** | Python 3.11 |
| **Dashboard** | Streamlit 1.36 |
| **Visualização** | Plotly 5.15 |
| **Machine Learning** | scikit-learn (Random Forest) |
| **Manipulação de dados** | Pandas, NumPy |
| **Deploy** | Streamlit Community Cloud |
| **Versionamento** | Git / GitHub |

---

## 📊 Dataset

Os dados são provenientes da **PEDE — Pesquisa Extensiva do Desenvolvimento Educacional** da Associação Passos Mágicos, cobrindo os anos de 2020, 2021 e 2022.

| Fonte | Registros | Descrição |
|-------|-----------|-----------|
| `PEDE_PASSOS_DATASET_MERGED.csv` | 1.349 alunos · 73 variáveis | Dataset principal com dados educacionais, socioeconômicos e gênero |
| `TbAlunoTurma_enriched.csv` | 9.157 registros | Histórico de matrículas e inativações com motivo e idade |
| `TbMotivoInativacao.csv` | 19 categorias | Tabela de motivos de saída do programa |

---

## 🚀 Como executar localmente

```bash
# Clone o repositório
git clone https://github.com/vinicius-souzaa/ongpasos-magicos.git
cd ongpasos-magicos

# Instale as dependências
pip install -r requirements.txt

# Execute o app
streamlit run main.py
```

---

## 👤 Autor

**Vinicius Abreu Ernestino Souza**  
Data Analyst · São Paulo, SP

[![LinkedIn](https://img.shields.io/badge/LinkedIn-vinicius--souzaa-0A66C2?logo=linkedin)](https://www.linkedin.com/in/viniciusaesouza/)
[![GitHub](https://img.shields.io/badge/GitHub-vinicius--souzaa-181717?logo=github)](https://github.com/vinicius-souzaa)
[![Streamlit](https://img.shields.io/badge/Demo-Live-FF4B4B?logo=streamlit)](https://ongpasos-magicos.streamlit.app/)

---

<p align="center">
  <sub>Desenvolvido com 💚 para a ONG Passos Mágicos · PEDE 2020–2022</sub>
</p>
