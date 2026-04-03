import streamlit as st
import plotly.graph_objs as go
import pandas as pd
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from util.style import inject_css, insight, section_header, PLOTLY_LAYOUT, COLORS
from util.data import load_all
from util.layout import sidebar

inject_css()
sidebar()

df = load_all()

st.markdown(section_header("CONCLUSÕES E RECOMENDAÇÕES","O que os dados dizem para a ONG"), unsafe_allow_html=True)

# ── ACHADOS PRINCIPAIS ────────────────────────────────────────
st.markdown("### 🔍 Achados principais")

col1, col2 = st.columns(2)
with col1:
    st.markdown("""
    <div style="background:#1A1D27;border:1px solid #2E3350;border-radius:12px;padding:1.5rem;height:100%;">
    <p style="color:#6EE7B7;font-size:0.68rem;font-weight:600;letter-spacing:0.15em;text-transform:uppercase;margin-bottom:1rem;">IMPACTO POSITIVO CONFIRMADO</p>

    <div style="border-left:2px solid #6EE7B7;padding-left:0.75rem;margin-bottom:0.75rem;">
    <p style="color:#F1F5F9;font-size:0.88rem;font-weight:600;margin:0 0 0.2rem;">Bolsistas: 4× mais Ponto de Virada</p>
    <p style="color:#64748B;font-size:0.78rem;margin:0;">38,9% vs 9,4% — diferença de 29,5 p.p. consistente em todos os anos analisados.</p>
    </div>

    <div style="border-left:2px solid #6EE7B7;padding-left:0.75rem;margin-bottom:0.75rem;">
    <p style="color:#F1F5F9;font-size:0.88rem;font-weight:600;margin:0 0 0.2rem;">Topázio cresceu 41% de 2020 a 2022</p>
    <p style="color:#64748B;font-size:0.78rem;margin:0;">92 → 130 alunos no nível máximo de classificação. Ágata +46% (171→250).</p>
    </div>

    <div style="border-left:2px solid #6EE7B7;padding-left:0.75rem;">
    <p style="color:#F1F5F9;font-size:0.88rem;font-weight:600;margin:0 0 0.2rem;">Fórmula INDE verificada com R²=1,000</p>
    <p style="color:#64748B;font-size:0.78rem;margin:0;">INDE = IDA×20% + IEG×20% + IPV×20% + IAA×10% + IPS×10% + IPP×10% + IAN×10%</p>
    </div>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown("""
    <div style="background:#1A1D27;border:1px solid #2E3350;border-radius:12px;padding:1.5rem;height:100%;">
    <p style="color:#F87171;font-size:0.68rem;font-weight:600;letter-spacing:0.15em;text-transform:uppercase;margin-bottom:1rem;">DESAFIOS IDENTIFICADOS</p>

    <div style="border-left:2px solid #F87171;padding-left:0.75rem;margin-bottom:0.75rem;">
    <p style="color:#F1F5F9;font-size:0.88rem;font-weight:600;margin:0 0 0.2rem;">43% de retenção longitudinal</p>
    <p style="color:#64748B;font-size:0.78rem;margin:0;">Dos 727 alunos de 2020, apenas 314 aparecem nos 3 anos. Alta rotatividade.</p>
    </div>

    <div style="border-left:2px solid #F87171;padding-left:0.75rem;margin-bottom:0.75rem;">
    <p style="color:#F1F5F9;font-size:0.88rem;font-weight:600;margin:0 0 0.2rem;">80,6% dos veteranos pioraram o INDE</p>
    <p style="color:#64748B;font-size:0.78rem;margin:0;">Alunos presentes nos 3 anos: INDE 7,72→7,03→6,97. A "recuperação" geral é puxada por ingressantes.</p>
    </div>

    <div style="border-left:2px solid #F87171;padding-left:0.75rem;">
    <p style="color:#F1F5F9;font-size:0.88rem;font-weight:600;margin:0 0 0.2rem;">73 alunos multi-vulneráveis</p>
    <p style="color:#64748B;font-size:0.78rem;margin:0;">IPS + IAA abaixo do P25 simultaneamente. Probabilidade de PV próxima de zero sem intervenção.</p>
    </div>
    </div>
    """, unsafe_allow_html=True)

st.divider()

# ── RECOMENDAÇÕES ─────────────────────────────────────────────
st.markdown("### 💡 Recomendações baseadas em dados")

recs = [
    {
        "icon": "🎓",
        "titulo": "Expandir o programa de bolsas",
        "impacto": "ALTO",
        "cor_impacto": COLORS['red'],
        "texto": "Bolsistas têm INDE 11,1% maior e 4× mais Ponto de Virada. "
                 "No Top 10% do INDE, 39,1% são bolsistas vs 3,4% no Bottom 10%. "
                 "Usar o modelo preditivo para identificar candidatos ideais: alunos com "
                 "score de PV > 50% que ainda não são bolsistas (estimativa: ~40 alunos/ano).",
        "cor": COLORS['accent'],
    },
    {
        "icon": "🚨",
        "titulo": "Programa de retenção proativa",
        "impacto": "ALTO",
        "cor_impacto": COLORS['red'],
        "texto": "Apenas 43% dos alunos de 2020 aparecem nos 3 anos. "
                 "Rodar o modelo de risco de evasão no início de cada semestre e contatar "
                 "proativamente os alunos com score > 60%. Foco especial em 14-15 anos "
                 "(pico de evasão para ambos os gêneros) e jovens de 18-19 anos do sexo feminino "
                 "(evasão 2,5× maior que masculino nessa faixa).",
        "cor": COLORS['red'],
    },
    {
        "icon": "🧠",
        "titulo": "Intervenção prioritária nos 73 alunos multi-vulneráveis",
        "impacto": "CRÍTICO",
        "cor_impacto": COLORS['red'],
        "texto": "Alunos com IPS + IAA abaixo do percentil 25 têm probabilidade de Ponto de Virada "
                 "próxima de zero. São 73 alunos identificados em 2022. "
                 "A equipe de Psicologia deve ser acionada prioritariamente para esse grupo — "
                 "em linha com a prática já descrita no relatório PEDE 2020 (os '41 alunos vulneráveis IAA').",
        "cor": COLORS['accent2'],
    },
    {
        "icon": "📚",
        "titulo": "Reforço em Português e Inglês",
        "impacto": "MÉDIO",
        "cor_impacto": COLORS['gold'],
        "texto": "Médias abaixo de 6: Português (5,80) e Inglês (5,84) vs Matemática (6,31). "
                 "Inglês tem maior correlação com INDE (r=0,72) — pode ser proxy de engajamento global. "
                 "Programas de reforço nessas duas disciplinas têm potencial de alavancagem no INDE.",
        "cor": COLORS['gold'],
    },
    {
        "icon": "📊",
        "titulo": "Revisar os pesos dos indicadores psicossociais",
        "impacto": "MÉDIO",
        "cor_impacto": COLORS['gold'],
        "texto": "IPS e IPP têm peso de 10% cada no INDE mas correlação muito baixa (~0,28) com o índice. "
                 "Isso não significa que são irrelevantes — mas que medem dimensões que o INDE não captura bem. "
                 "Considerar avaliar esses indicadores separadamente do INDE, "
                 "com metas e acompanhamento próprios.",
        "cor": COLORS['dim'],
    },
    {
        "icon": "🔄",
        "titulo": "Monitorar a trajetória dos veteranos separadamente",
        "impacto": "MÉDIO",
        "cor_impacto": COLORS['gold'],
        "texto": "O INDE médio geral mascara uma queda contínua entre os veteranos. "
                 "Criar uma métrica de 'progresso longitudinal' separada da média cross-sectional "
                 "permitiria distinguir: o programa está melhorando os alunos que ficam? "
                 "Ou o INDE médio sobe apenas pela entrada de novos alunos em fases iniciais?",
        "cor": COLORS['accent2'],
    },
]

for rec in recs:
    st.markdown(f"""
    <div style="background:#1A1D27;border:1px solid #2E3350;border-radius:10px;
                padding:1.1rem 1.4rem;margin-bottom:0.75rem;
                border-left:3px solid {rec['cor']};">
        <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:0.4rem;">
            <span style="color:#F1F5F9;font-size:0.95rem;font-weight:600;">
                {rec['icon']} {rec['titulo']}
            </span>
            <span style="background:{rec['cor_impacto']}22;color:{rec['cor_impacto']};
                         border:1px solid {rec['cor_impacto']}44;
                         font-size:0.62rem;font-weight:600;letter-spacing:0.1em;
                         padding:0.15rem 0.6rem;border-radius:2rem;">
                {rec['impacto']}
            </span>
        </div>
        <p style="color:#64748B;font-size:0.83rem;line-height:1.65;margin:0;">{rec['texto']}</p>
    </div>
    """, unsafe_allow_html=True)

st.divider()

# ── NOTA SOBRE GÊNERO ─────────────────────────────────────────
st.markdown("### ⚧ Nota sobre a hipótese de evasão masculina")
st.markdown(insight(
    "<strong>A hipótese do fundador — que meninos adolescentes abandonam o programa para trabalhar "
    "e ajudar na renda familiar — não se confirma como padrão dominante nos dados.</strong> "
    "Taxa de evasão: F=53,0% vs M=56,9% pós-2020 — diferença de 3,9 p.p. sem relevância prática. "
    "Na tabela de inativações (1.781 registros), a taxa por gênero é praticamente idêntica: F=19,4% vs M=19,3%. "
    "Apenas 2 comentários de inativação mencionam trabalho — ambos de alunas. "
    "Os principais motivos são: transporte precário, conflito de horário com escola e problemas de saúde familiar. "
    "A hipótese pode ser verdadeira em casos individuais, mas não é o fenômeno estrutural dominante.",
    "danger"
), unsafe_allow_html=True)

st.divider()

# ── SOBRE O PROJETO ───────────────────────────────────────────
st.markdown("### 📌 Sobre este projeto")
st.markdown("""
<div style="background:#0D0F1A;border:1px solid #1E2135;border-radius:12px;padding:1.5rem;">
<div style="display:grid;grid-template-columns:1fr 1fr 1fr;gap:1.5rem;">

<div>
<p style="color:#6EE7B7;font-size:0.68rem;font-weight:600;letter-spacing:0.15em;text-transform:uppercase;margin-bottom:0.5rem;">DADOS</p>
<p style="color:#64748B;font-size:0.8rem;line-height:1.6;margin:0;">
PEDE 2020, 2021 e 2022<br/>
1.349 alunos · 69 variáveis<br/>
Integração com TbAluno (Sexo)<br/>
e TbAlunoTurma (inativações)
</p>
</div>

<div>
<p style="color:#6EE7B7;font-size:0.68rem;font-weight:600;letter-spacing:0.15em;text-transform:uppercase;margin-bottom:0.5rem;">MODELOS</p>
<p style="color:#64748B;font-size:0.8rem;line-height:1.6;margin:0;">
Random Forest (evasão · AUC=0,65)<br/>
Random Forest (PV · AUC=0,98)<br/>
Fórmula INDE verificada<br/>
com R²=1,000
</p>
</div>

<div>
<p style="color:#6EE7B7;font-size:0.68rem;font-weight:600;letter-spacing:0.15em;text-transform:uppercase;margin-bottom:0.5rem;">STACK TÉCNICO</p>
<p style="color:#64748B;font-size:0.8rem;line-height:1.6;margin:0;">
Python · Pandas · NumPy<br/>
scikit-learn · Plotly<br/>
Streamlit · Git / GitHub<br/>
Streamlit Community Cloud
</p>
</div>

</div>

<div style="margin-top:1.25rem;padding-top:1rem;border-top:1px solid #1E2135;">
<p style="color:#475569;font-size:0.75rem;margin:0;">
<strong style="color:#94A3B8;">Vinicius Abreu Ernestino Souza</strong> ·
PósTech Data Analytics · FIAP · Grupo 22 · Turma 3DTAT ·

</p>
</div>
</div>
""", unsafe_allow_html=True)
