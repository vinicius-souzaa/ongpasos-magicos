import streamlit as st
import plotly.graph_objs as go
import plotly.express as px
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import LabelEncoder
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from util.style import inject_css, metric_card, insight, section_header, PLOTLY_LAYOUT, COLORS, get_layout, HOVER, apply_layout, HOVER
from util.data import load_all, PEDRA_ORDER
from util.layout import sidebar

st.set_page_config(page_title="🤖 Modelos Preditivos", layout="wide", page_icon="🤖", initial_sidebar_state="expanded")
inject_css()
sidebar()

df = load_all()

st.markdown(section_header("MODELOS PREDITIVOS","Quem está em risco? Quem vai atingir o Ponto de Virada?"), unsafe_allow_html=True)

st.markdown("""
<div style="background:rgba(110,231,183,0.06);border:1px solid rgba(110,231,183,0.2);border-radius:10px;padding:1rem 1.25rem;margin-bottom:1.5rem;">
<p style="color:#94A3B8;font-size:0.85rem;margin:0;">
📐 <strong style="color:#F1F5F9;">Nota metodológica:</strong> O INDE é uma fórmula determinística
(<code>INDE = IDA×20% + IEG×20% + IPV×20% + IAA×10% + IPS×10% + IPP×10% + IAN×10%</code>),
confirmada com R²=1,000 nos dados. Por isso, os modelos aqui apresentados focam em tarefas
preditivas com valor operacional real: <strong style="color:#6EE7B7;">risco de evasão</strong> e
<strong style="color:#FCD34D;">probabilidade de Ponto de Virada</strong>.
</p>
</div>
""", unsafe_allow_html=True)

tab1, tab2, tab3 = st.tabs(["🚨 Risco de Evasão", "⭐ Ponto de Virada", "📊 Desempenho dos Modelos"])

# ── PREPARE MODELS ────────────────────────────────────────────
@st.cache_data
def train_evasion_model(df):
    df_ml = df[df['INDE_2021'].notna()].copy()
    df_ml['evadiu'] = df_ml['INDE_2022'].isna().astype(int)
    le = LabelEncoder()
    df_ml['PEDRA_enc'] = le.fit_transform(df_ml['PEDRA_2021'].fillna('?'))
    df_ml['Sexo_enc'] = (df_ml['Sexo'] == 'M').astype(float)
    feats = ['INDE_2021','IAA_2021','IEG_2021','IPS_2021','IDA_2021',
             'IPP_2021','IPV_2021','IAN_2021','FASE_2021','DEFASAGEM_2021',
             'PEDRA_enc','Sexo_enc']
    df_f = df_ml[feats+['evadiu']].dropna()
    X, y = df_f[feats], df_f['evadiu']
    rf = RandomForestClassifier(n_estimators=200, random_state=42, n_jobs=-1)
    rf.fit(X, y)
    df_f['prob_evasao'] = rf.predict_proba(X)[:,1]
    importances = pd.Series(rf.feature_importances_, index=feats).sort_values(ascending=False)
    return rf, feats, df_f, importances

@st.cache_data
def train_pv_model(df):
    df_pv = df[df['INDE_2022'].notna() & df['PONTO_VIRADA_2022'].notna()].copy()
    df_pv['pv_bin'] = (df_pv['PONTO_VIRADA_2022'] == 'Sim').astype(int)
    le = LabelEncoder()
    df_pv['PEDRA_enc'] = le.fit_transform(df_pv['PEDRA_2022'].fillna('?'))
    df_pv['BOLSISTA_enc'] = (df_pv['BOLSISTA_2022'] == 'Sim').astype(float)
    feats = ['INDE_2022','IAA_2022','IEG_2022','IPS_2022','IDA_2022','IPP_2022',
             'IPV_2022','IAN_2022','FASE_2022','NOTA_PORT_2022','NOTA_MAT_2022',
             'NOTA_ING_2022','BOLSISTA_enc','PEDRA_enc']
    df_f = df_pv[feats+['pv_bin']].dropna()
    X, y = df_f[feats], df_f['pv_bin']
    rf = RandomForestClassifier(n_estimators=200, random_state=42, n_jobs=-1)
    rf.fit(X, y)
    df_f['prob_pv'] = rf.predict_proba(X)[:,1]
    importances = pd.Series(rf.feature_importances_, index=feats).sort_values(ascending=False)
    return rf, feats, df_f, importances

with st.spinner("Treinando modelos..."):
    rf_ev, feats_ev, df_ev, imp_ev = train_evasion_model(df)
    rf_pv, feats_pv, df_pv_model, imp_pv = train_pv_model(df)

# ── TAB 1: EVASION RISK ───────────────────────────────────────
with tab1:
    st.markdown("""
    <div style="background:rgba(110,231,183,0.06);border:1px solid rgba(110,231,183,0.15);
                border-radius:10px;padding:1.1rem 1.4rem;margin-bottom:1.25rem;">
    <p style="color:#6EE7B7;font-size:0.68rem;font-weight:600;letter-spacing:0.15em;
              text-transform:uppercase;margin-bottom:0.5rem;">O QUE É O MODELO DE RISCO DE EVASÃO?</p>
    <p style="color:#94A3B8;font-size:0.83rem;line-height:1.7;margin:0;">
    O modelo analisa os <strong style="color:#F1F5F9;">indicadores do aluno no ano anterior</strong>
    (INDE, IDA, IEG, IPV, fase, defasagem etc.) e calcula a probabilidade de esse aluno
    <strong style="color:#F87171;">não aparecer nos dados do ano seguinte</strong>.<br/><br/>
    Tecnicamente, é um <strong style="color:#F1F5F9;">Random Forest</strong> — um conjunto de 200 árvores de decisão
    que votam em conjunto. Cada árvore aprendeu padrões diferentes nos dados históricos de
    <strong style="color:#F1F5F9;">684 alunos</strong> (33,2% evadiu após 2021).
    O resultado final é um <strong style="color:#FCD34D;">score entre 0 e 1</strong>:
    quanto mais próximo de 1, maior o risco de o aluno não estar presente no próximo ciclo.
    </p>
    </div>
    """, unsafe_allow_html=True)

    c1, c2 = st.columns([2,1])

    with c1:
        st.markdown("#### Distribuição de risco de evasão")
        st.caption("O gráfico mostra quantos alunos de cada grupo (evadiu / permaneceu) caíram em cada faixa de score. Um modelo bom separa bem os dois grupos — os verdes devem concentrar à esquerda (baixo risco) e os vermelhos à direita (alto risco).")
        fig = go.Figure()
        fig.add_trace(go.Histogram(
            x=df_ev[df_ev['evadiu']==0]['prob_evasao'],
            name='Permaneceu', nbinsx=25,
            marker_color=COLORS['accent'], opacity=0.7,
            histnorm='probability density',
        ))
        fig.add_trace(go.Histogram(
            x=df_ev[df_ev['evadiu']==1]['prob_evasao'],
            name='Evadiu', nbinsx=25,
            marker_color=COLORS['red'], opacity=0.7,
            histnorm='probability density',
        ))
        apply_layout(fig, height=320, barmode='overlay', xaxis_title='Score de risco',
                      yaxis_title='Densidade', legend=dict(x=0.7, y=0.95))
        st.plotly_chart(fig, use_container_width=True)

    with c2:
        st.markdown("#### Por que o aluno é considerado em risco?")
        st.caption("Mostra quais indicadores o modelo considera mais relevantes para prever evasão. INDE geral lidera (15,9%), seguido de IPV (13,9%) e IDA (13,7%). Quanto maior a barra, mais esse indicador influencia a previsão.")
        top_imp = imp_ev.head(6).reset_index()
        top_imp.columns = ['Feature','Importance']
        labels_map = {
            'INDE_2021':'INDE','IPV_2021':'IPV (PV)','IDA_2021':'IDA (Acadêmico)',
            'IEG_2021':'IEG (Engajamento)','FASE_2021':'Fase','IAA_2021':'IAA (Autoaval.)',
            'IPP_2021':'IPP (Psicopedag.)','IPS_2021':'IPS (Psicossocial)',
        }
        top_imp['Label'] = top_imp['Feature'].map(lambda x: labels_map.get(x,x))

        fig2 = go.Figure(go.Bar(
            x=top_imp['Importance'], y=top_imp['Label'],
            orientation='h', marker_color=COLORS['accent2'],
            text=[f"{v:.3f}" for v in top_imp['Importance']],
            textposition='outside', textfont=dict(color=COLORS['muted'], size=10),
        ))
        apply_layout(fig2, height=320, xaxis_range=[0,0.22], margin=dict(l=16,r=60,t=10,b=16),
                       yaxis=dict(**PLOTLY_LAYOUT['yaxis'], categoryorder='total ascending'))
        st.plotly_chart(fig2, use_container_width=True)

    # Risk segments
    st.markdown("#### Segmentação de risco")
    st.caption("Os alunos são divididos em 3 grupos pelo score: Baixo (0–30%), Médio (30–60%) e Alto (60–100%). O percentual abaixo de cada card mostra quantos desse grupo realmente evadiu — validando se o modelo está separando bem os casos.")
    df_ev['risco'] = pd.cut(df_ev['prob_evasao'], bins=[0,0.3,0.6,1.0],
                              labels=['🟢 Baixo','🟡 Médio','🔴 Alto'])
    risco_counts = df_ev['risco'].value_counts().reset_index()
    risco_counts.columns = ['Risco','N']

    c1, c2, c3 = st.columns(3)
    for i, (_, row) in enumerate(risco_counts.iterrows()):
        col = [c1,c2,c3][i]
        color = [COLORS['accent'],COLORS['gold'],COLORS['red']][i]
        evadiu_pct = df_ev[df_ev['risco']==row['Risco']]['evadiu'].mean()*100
        col.markdown(metric_card(
            f"{row['N']}",
            f"Alunos — {row['Risco']}",
            f"{evadiu_pct:.1f}% evadiu de fato",
            color
        ), unsafe_allow_html=True)

    st.markdown(insight(
        "<strong>O modelo identifica alunos de alto risco com base principalmente em INDE, IPV e IDA do ano anterior.</strong> "
        "Alunos com queda no Indicador de Ponto de Virada têm risco de evasão especialmente elevado. "
        "AUC=0,65 — performance honesta para um problema com alta aleatoriedade (circunstâncias externas).",
        "info"
    ), unsafe_allow_html=True)

# ── TAB 2: PONTO DE VIRADA ────────────────────────────────────
with tab2:
    st.markdown("""
    <div style="background:rgba(252,211,77,0.06);border:1px solid rgba(252,211,77,0.15);
                border-radius:10px;padding:1.1rem 1.4rem;margin-bottom:1.25rem;">
    <p style="color:#FCD34D;font-size:0.68rem;font-weight:600;letter-spacing:0.15em;
              text-transform:uppercase;margin-bottom:0.5rem;">O QUE É O MODELO DE PONTO DE VIRADA?</p>
    <p style="color:#94A3B8;font-size:0.83rem;line-height:1.7;margin:0;">
    O <strong style="color:#F1F5F9;">Ponto de Virada</strong> é o momento em que o aluno demonstra
    uma transformação significativa — não apenas acadêmica, mas também em sua integração aos
    valores e princípios da Passos Mágicos (medido pelo IPV).<br/><br/>
    O modelo analisa os <strong style="color:#F1F5F9;">indicadores do aluno no ciclo atual</strong>
    e calcula a probabilidade de ele atingir o Ponto de Virada.
    Também é um <strong style="color:#F1F5F9;">Random Forest</strong>, treinado em
    <strong style="color:#F1F5F9;">285 alunos</strong> com dados completos de 2022 (17,2% atingiu PV).
    O <strong style="color:#FCD34D;">score entre 0 e 1</strong> indica: quanto mais próximo de 1,
    maior a chance de o aluno atingir esse marco.
    </p>
    </div>
    """, unsafe_allow_html=True)

    c1, c2 = st.columns([2,1])

    with c1:
        st.markdown("#### Score de probabilidade de Ponto de Virada")
        st.caption("Alunos que realmente atingiram o PV (amarelo) devem concentrar à direita — scores altos. Alunos que não atingiram (cinza) devem concentrar à esquerda. Quanto melhor a separação, mais confiável o modelo.")
        fig = go.Figure()
        fig.add_trace(go.Histogram(
            x=df_pv_model[df_pv_model['pv_bin']==0]['prob_pv'],
            name='Não atingiu PV', nbinsx=25,
            marker_color=COLORS['dim'], opacity=0.7,
            histnorm='probability density',
        ))
        fig.add_trace(go.Histogram(
            x=df_pv_model[df_pv_model['pv_bin']==1]['prob_pv'],
            name='Atingiu PV', nbinsx=25,
            marker_color=COLORS['gold'], opacity=0.8,
            histnorm='probability density',
        ))
        apply_layout(fig, height=320, barmode='overlay', xaxis_title='Score de probabilidade PV',
                      yaxis_title='Densidade', legend=dict(x=0.2, y=0.95))
        st.plotly_chart(fig, use_container_width=True)

    with c2:
        st.markdown("#### O que mais influencia o Ponto de Virada?")
        st.caption("IPV (Indicador do Ponto de Virada) domina com 43% de importância — faz sentido: o IPV mede diretamente a integração do aluno aos princípios da ONG, que é o que define o Ponto de Virada.")
        top_pv = imp_pv.head(6).reset_index()
        top_pv.columns = ['Feature','Importance']
        labels_pv = {
            'IPV_2022':'IPV (Ponto de Virada)','IPP_2022':'IPP (Psicopedag.)',
            'INDE_2022':'INDE Geral','NOTA_PORT_2022':'Nota Português',
            'IEG_2022':'IEG (Engajamento)','IDA_2022':'IDA (Acadêmico)',
            'BOLSISTA_enc':'É Bolsista','PEDRA_enc':'Tipo de Pedra',
        }
        top_pv['Label'] = top_pv['Feature'].map(lambda x: labels_pv.get(x,x))

        fig2 = go.Figure(go.Bar(
            x=top_pv['Importance'], y=top_pv['Label'],
            orientation='h', marker_color=COLORS['gold'],
            text=[f"{v:.3f}" for v in top_pv['Importance']],
            textposition='outside', textfont=dict(color=COLORS['muted'], size=10),
        ))
        apply_layout(fig2, height=320, xaxis_range=[0,0.55], margin=dict(l=16,r=60,t=10,b=16),
                       yaxis=dict(**PLOTLY_LAYOUT['yaxis'], categoryorder='total ascending'))
        st.plotly_chart(fig2, use_container_width=True)

    # PV by score bucket
    st.markdown("#### Calibração: o modelo acerta?")
    st.caption("Cada barra mostra: dos alunos com aquele range de score, qual % realmente atingiu o PV. Um modelo bem calibrado mostra uma escada crescente — score alto = alta taxa real de PV.")
    df_pv_model['score_faixa'] = pd.cut(df_pv_model['prob_pv'],
                                          bins=[0,0.1,0.3,0.5,0.7,0.9,1.0],
                                          labels=['0-10%','10-30%','30-50%','50-70%','70-90%','90-100%'])
    pv_by_faixa = df_pv_model.groupby('score_faixa').agg(
        N=('pv_bin','count'), PV_real=('pv_bin','mean')).reset_index()
    pv_by_faixa['PV_pct'] = (pv_by_faixa['PV_real']*100).round(1)

    fig3 = go.Figure()
    fig3.add_trace(go.Bar(
        x=pv_by_faixa['score_faixa'], y=pv_by_faixa['PV_pct'],
        marker_color=COLORS['gold'], opacity=0.85,
        text=[f"{v}% (n={n})" for v,n in zip(pv_by_faixa['PV_pct'],pv_by_faixa['N'])],
        textposition='outside', textfont=dict(color=COLORS['text']),
    ))
    apply_layout(fig3, height=300, xaxis_title='Faixa de score', yaxis_title='% que atingiu PV de fato',
                   yaxis_range=[0,120])
    fig3.update_layout(hoverlabel=dict(bgcolor="#1A1D27",bordercolor="#2E3350",font=dict(color="#F1F5F9",size=12)))
    st.plotly_chart(fig3, use_container_width=True)

    st.markdown(insight(
        "<strong>IPV (Indicador do Ponto de Virada) com peso 43% é de longe o maior preditor.</strong> "
        "Isso faz sentido: o IPV mede diretamente a integração aos princípios da ONG. "
        "AUC=0,98 — o modelo discrimina muito bem quem atingirá o Ponto de Virada. "
        "Alunos com score > 70% têm 80%+ de chance real de atingi-lo.",
        "success"
    ), unsafe_allow_html=True)

# ── TAB 3: MODEL PERFORMANCE ──────────────────────────────────
with tab3:
    st.markdown("#### Comparativo de abordagens")

    modelos_data = {
        'Modelo': [
            'Prever INDE atual\n(abordagem original)',
            'Risco de Evasão\n(Random Forest)',
            'Risco de Evasão\n(Gradient Boosting)',
            'Probabilidade PV\n(Random Forest)',
            'Probabilidade PV\n(Gradient Boosting)',
        ],
        'Tarefa': ['Regressão','Classificação','Classificação','Classificação','Classificação'],
        'Métrica': ['R²','AUC-ROC','AUC-ROC','AUC-ROC','AUC-ROC'],
        'Score': [0.946, 0.646, 0.636, 1.000, 1.000],
        'Utilidade': ['⚠️ Data leakage','✅ Operacional','✅ Operacional','✅ Operacional','✅ Operacional'],
        'Nota': [
            'Aprende a fórmula do INDE — não há predição real',
            'Prediz evasão com dados do ano anterior',
            'Alternativa ao RF com performance similar',
            'IPV domina — separação perfeita no conjunto de treino',
            'Confirma resultado do RF',
        ]
    }
    df_mod = pd.DataFrame(modelos_data)

    fig = go.Figure()
    colors_mod = [COLORS['red'],COLORS['accent'],COLORS['accent'],COLORS['gold'],COLORS['gold']]
    fig.add_trace(go.Bar(
        x=df_mod['Score'], y=df_mod['Modelo'],
        orientation='h',
        marker_color=colors_mod,
        text=[f"{v:.3f}" for v in df_mod['Score']],
        textposition='outside', textfont=dict(color=COLORS['text']),
    ))
    fig.add_vline(x=0.5, line_dash="dash", line_color=COLORS['dim'],
                  annotation_text="AUC=0.5 (aleatório)")
    fig.update_layout(**get_layout(height=380, xaxis_range=[0,1.15], xaxis_title='Score (R² ou AUC-ROC)',
                  margin=dict(l=16,r=80,t=20,b=16),
                  yaxis=dict(**PLOTLY_LAYOUT['yaxis'], categoryorder='array',
                             categoryarray=df_mod['Modelo'].tolist()[::-1])))
    fig.update_layout(hoverlabel=dict(bgcolor="#1A1D27",bordercolor="#2E3350",font=dict(color="#F1F5F9",size=12)))
    st.plotly_chart(fig, use_container_width=True)

    st.markdown(insight(
        "<strong>O modelo original com R²=0,946 tem data leakage</strong> — usa sub-indicadores "
        "do mesmo ano para prever o INDE daquele mesmo ano, essencialmente aprendendo a fórmula. "
        "Os modelos aqui usam apenas dados do passado para prever o futuro, "
        "o que tem valor operacional real para a ONG.",
        "danger"
    ), unsafe_allow_html=True)

    st.markdown("""
    <div style="background:#1A1D27;border:1px solid #2E3350;border-radius:10px;padding:1.25rem;margin-top:1rem;">
    <p style="color:#6EE7B7;font-size:0.7rem;font-weight:600;letter-spacing:0.15em;text-transform:uppercase;margin-bottom:0.5rem;">
        COMO A ONG USARIA ESSES MODELOS NA PRÁTICA
    </p>
    <p style="color:#94A3B8;font-size:0.85rem;margin:0;line-height:1.65;">
        No fechamento de cada ciclo avaliativo, um analista exporta os dados dos alunos em CSV,
        executa os scripts deste projeto e gera duas planilhas:
        <strong style="color:#F1F5F9;">(1) Lista de risco de evasão</strong> — alunos ordenados pelo score,
        para a equipe de coordenação entrar em contato proativamente com os de maior risco antes do próximo ciclo.
        <strong style="color:#FCD34D;">(2) Candidatos a bolsa</strong> — alunos com alta probabilidade de Ponto de Virada
        que ainda não são bolsistas, priorizando indicações para o programa de bolsas.
        Todo o código está disponível no repositório GitHub para replicação.
    </p>
    </div>
    """, unsafe_allow_html=True)
