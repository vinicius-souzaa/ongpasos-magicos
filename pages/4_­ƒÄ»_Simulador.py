import streamlit as st
import plotly.graph_objs as go
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import LabelEncoder
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from util.style import inject_css, insight, section_header, PLOTLY_LAYOUT, COLORS
from util.data import load_all, PEDRA_ORDER
from util.layout import sidebar

st.set_page_config(
    page_title="Simulador · Passos Mágicos",
    layout="wide",
    page_icon="🎯",
    initial_sidebar_state="expanded"
)
inject_css()
sidebar()

df = load_all()

# ── TRAIN MODELS ──────────────────────────────────────────────
@st.cache_data
def train_models(df):
    le_pedra = LabelEncoder()
    le_pedra.fit(PEDRA_ORDER + ['?'])

    # Evasion model
    df_ev = df[df['INDE_2021'].notna()].copy()
    df_ev['evadiu'] = df_ev['INDE_2022'].isna().astype(int)
    df_ev['PEDRA_enc'] = df_ev['PEDRA_2021'].fillna('?').apply(
        lambda x: x if x in le_pedra.classes_ else '?')
    df_ev['PEDRA_enc'] = le_pedra.transform(df_ev['PEDRA_enc'])
    df_ev['Sexo_enc'] = (df_ev['Sexo'] == 'M').astype(float)
    feats_ev = ['INDE_2021','IAA_2021','IEG_2021','IPS_2021','IDA_2021',
                'IPP_2021','IPV_2021','IAN_2021','FASE_2021','DEFASAGEM_2021',
                'PEDRA_enc','Sexo_enc']
    df_evf = df_ev[feats_ev + ['evadiu']].dropna()
    rf_ev = RandomForestClassifier(n_estimators=200, random_state=42, n_jobs=-1)
    rf_ev.fit(df_evf[feats_ev], df_evf['evadiu'])

    # PV model
    df_pv = df[df['INDE_2022'].notna() & df['PONTO_VIRADA_2022'].notna()].copy()
    df_pv['pv_bin'] = (df_pv['PONTO_VIRADA_2022'] == 'Sim').astype(int)
    df_pv['PEDRA_enc'] = df_pv['PEDRA_2022'].fillna('?').apply(
        lambda x: x if x in le_pedra.classes_ else '?')
    df_pv['PEDRA_enc'] = le_pedra.transform(df_pv['PEDRA_enc'])
    df_pv['BOLSISTA_enc'] = (df_pv['BOLSISTA_2022'] == 'Sim').astype(float)
    feats_pv = ['INDE_2022','IAA_2022','IEG_2022','IPS_2022','IDA_2022','IPP_2022',
                'IPV_2022','IAN_2022','FASE_2022','NOTA_PORT_2022','NOTA_MAT_2022',
                'NOTA_ING_2022','BOLSISTA_enc','PEDRA_enc']
    df_pvf = df_pv[feats_pv + ['pv_bin']].dropna()
    rf_pv = RandomForestClassifier(n_estimators=200, random_state=42, n_jobs=-1)
    rf_pv.fit(df_pvf[feats_pv], df_pvf['pv_bin'])

    return rf_ev, feats_ev, rf_pv, feats_pv, le_pedra

with st.spinner("Carregando modelos..."):
    rf_ev, feats_ev, rf_pv, feats_pv, le_pedra = train_models(df)

# ── HEADER ────────────────────────────────────────────────────
st.markdown(section_header("SIMULADOR", "Avalie o perfil de um aluno"), unsafe_allow_html=True)

st.markdown("""
<div style="background:rgba(129,140,248,0.06);border:1px solid rgba(129,140,248,0.2);
            border-radius:10px;padding:1rem 1.4rem;margin-bottom:1.5rem;">
<p style="color:#94A3B8;font-size:0.85rem;line-height:1.65;margin:0;">
🎯 Preencha os indicadores do aluno abaixo para obter dois resultados:
<strong style="color:#F87171;">risco de evasão</strong> (probabilidade de não comparecer ao próximo ciclo) e
<strong style="color:#FCD34D;">probabilidade de Ponto de Virada</strong> (chance de atingir uma transformação significativa).
Os valores são calculados pelos mesmos modelos treinados nos dados históricos da ONG.
</p>
</div>
""", unsafe_allow_html=True)

# ── INPUT FORM ────────────────────────────────────────────────
st.markdown("### 📋 Dados do aluno")

col_info, col_acad, col_psico = st.columns(3)

with col_info:
    st.markdown("""
    <div style="color:#6EE7B7;font-size:0.68rem;font-weight:600;letter-spacing:0.15em;
                text-transform:uppercase;margin-bottom:0.75rem;">DADOS GERAIS</div>
    """, unsafe_allow_html=True)
    fase = st.selectbox("Fase do programa", options=[0,1,2,3,4,5,6,7],
                        format_func=lambda x: f"Fase {x}", index=2)
    pedra = st.selectbox("Classificação (Pedra)", options=PEDRA_ORDER, index=2)
    sexo = st.radio("Sexo", options=["Feminino","Masculino"], horizontal=True)
    defasagem = st.slider("Defasagem escolar", min_value=-4, max_value=2, value=-1,
                          help="Diferença entre nível ideal e fase real. Negativo = atrasado.")
    bolsista = st.radio("É bolsista?", options=["Não","Sim"], horizontal=True)

with col_acad:
    st.markdown("""
    <div style="color:#6EE7B7;font-size:0.68rem;font-weight:600;letter-spacing:0.15em;
                text-transform:uppercase;margin-bottom:0.75rem;">INDICADORES ACADÊMICOS</div>
    """, unsafe_allow_html=True)
    inde = st.slider("INDE (Índice Geral)", 0.0, 10.0, 7.0, 0.1,
                     help="Índice de Desenvolvimento Educacional")
    ida = st.slider("IDA — Desempenho Acadêmico", 0.0, 10.0, 6.5, 0.1,
                    help="Notas nas provas e avaliações")
    ieg = st.slider("IEG — Engajamento", 0.0, 10.0, 7.0, 0.1,
                    help="Entrega de lições, participação em atividades")
    ian = st.slider("IAN — Nível de Aprendizado", 0.0, 10.0, 5.0, 0.1,
                    help="Adequação ao nível esperado para a idade")
    nota_port = st.slider("Nota Português", 0.0, 10.0, 6.0, 0.1)
    nota_mat  = st.slider("Nota Matemática",  0.0, 10.0, 6.5, 0.1)
    nota_ing  = st.slider("Nota Inglês",      0.0, 10.0, 6.0, 0.1)

with col_psico:
    st.markdown("""
    <div style="color:#6EE7B7;font-size:0.68rem;font-weight:600;letter-spacing:0.15em;
                text-transform:uppercase;margin-bottom:0.75rem;">INDICADORES PSICOSSOCIAIS</div>
    """, unsafe_allow_html=True)
    iaa = st.slider("IAA — Autoavaliação", 0.0, 10.0, 8.0, 0.1,
                    help="Como o aluno se avalia sobre estudos, família e comunidade")
    ips = st.slider("IPS — Psicossocial", 0.0, 10.0, 7.0, 0.1,
                    help="Condição psicossocial — alunos em atendimento terapêutico têm IPS específico")
    ipp = st.slider("IPP — Psicopedagógico", 0.0, 10.0, 6.5, 0.1,
                    help="Suporte psicopedagógico recebido")
    ipv = st.slider("IPV — Ponto de Virada", 0.0, 10.0, 7.5, 0.1,
                    help="Integração aos princípios Passos Mágicos — o maior preditor do PV")

st.divider()

# ── CALCULATE ─────────────────────────────────────────────────
pedra_enc = le_pedra.transform([pedra])[0]
sexo_enc  = 1.0 if sexo == "Masculino" else 0.0
bolsista_enc = 1.0 if bolsista == "Sim" else 0.0

X_ev = pd.DataFrame([[inde, iaa, ieg, ips, ida, ipp, ipv, ian,
                       float(fase), float(defasagem), pedra_enc, sexo_enc]],
                    columns=feats_ev)
prob_evasao = rf_ev.predict_proba(X_ev)[0][1]

X_pv = pd.DataFrame([[inde, iaa, ieg, ips, ida, ipp, ipv, ian,
                       float(fase), nota_port, nota_mat, nota_ing,
                       bolsista_enc, pedra_enc]],
                    columns=feats_pv)
prob_pv = rf_pv.predict_proba(X_pv)[0][1]

# Risk labels
def risco_label(prob):
    if prob < 0.30: return "🟢 BAIXO", COLORS['accent']
    elif prob < 0.60: return "🟡 MÉDIO", COLORS['gold']
    else: return "🔴 ALTO", COLORS['red']

def pv_label(prob):
    if prob < 0.25: return "⬇️ IMPROVÁVEL", COLORS['dim']
    elif prob < 0.50: return "🔄 POSSÍVEL", COLORS['accent2']
    elif prob < 0.75: return "⬆️ PROVÁVEL", COLORS['gold']
    else: return "⭐ MUITO PROVÁVEL", COLORS['accent']

risco_txt, risco_cor = risco_label(prob_evasao)
pv_txt, pv_cor = pv_label(prob_pv)

# ── RESULTS ───────────────────────────────────────────────────
st.markdown("### 📊 Resultado da análise")

res1, res2, res3 = st.columns([2, 2, 1])

with res1:
    st.markdown(f"""
    <div style="background:#1A1D27;border:1px solid {risco_cor}44;border-radius:12px;
                padding:1.5rem;text-align:center;border-top:3px solid {risco_cor};">
        <div style="font-size:0.68rem;font-weight:600;letter-spacing:0.15em;text-transform:uppercase;
                    color:{risco_cor};margin-bottom:0.75rem;">RISCO DE EVASÃO</div>
        <div style="font-size:3.5rem;font-weight:800;color:{risco_cor};line-height:1;">
            {prob_evasao*100:.1f}%
        </div>
        <div style="font-size:1rem;font-weight:600;color:{risco_cor};margin-top:0.5rem;">
            {risco_txt}
        </div>
        <div style="font-size:0.75rem;color:#475569;margin-top:0.75rem;line-height:1.5;">
            Probabilidade de o aluno não<br/>comparecer ao próximo ciclo
        </div>
    </div>
    """, unsafe_allow_html=True)

with res2:
    st.markdown(f"""
    <div style="background:#1A1D27;border:1px solid {pv_cor}44;border-radius:12px;
                padding:1.5rem;text-align:center;border-top:3px solid {pv_cor};">
        <div style="font-size:0.68rem;font-weight:600;letter-spacing:0.15em;text-transform:uppercase;
                    color:{pv_cor};margin-bottom:0.75rem;">PONTO DE VIRADA</div>
        <div style="font-size:3.5rem;font-weight:800;color:{pv_cor};line-height:1;">
            {prob_pv*100:.1f}%
        </div>
        <div style="font-size:1rem;font-weight:600;color:{pv_cor};margin-top:0.5rem;">
            {pv_txt}
        </div>
        <div style="font-size:0.75rem;color:#475569;margin-top:0.75rem;line-height:1.5;">
            Probabilidade de atingir uma<br/>transformação significativa
        </div>
    </div>
    """, unsafe_allow_html=True)

with res3:
    # Indicator summary
    st.markdown(f"""
    <div style="background:#1A1D27;border:1px solid #2E3350;border-radius:12px;padding:1.25rem;">
        <div style="font-size:0.68rem;font-weight:600;letter-spacing:0.15em;text-transform:uppercase;
                    color:#475569;margin-bottom:0.75rem;">PERFIL</div>
        <div style="font-size:0.78rem;color:#64748B;line-height:2;">
            Fase: <strong style="color:#F1F5F9;">{fase}</strong><br/>
            Pedra: <strong style="color:#F1F5F9;">{pedra}</strong><br/>
            Sexo: <strong style="color:#F1F5F9;">{sexo}</strong><br/>
            Bolsista: <strong style="color:#F1F5F9;">{bolsista}</strong><br/>
            Defasagem: <strong style="color:#F1F5F9;">{defasagem:+d}</strong>
        </div>
    </div>
    """, unsafe_allow_html=True)

st.divider()

# ── GAUGE CHARTS ─────────────────────────────────────────────
col_g1, col_g2 = st.columns(2)

def make_gauge(value, title, color, threshold_low=0.3, threshold_high=0.6):
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=value * 100,
        number=dict(suffix="%", font=dict(color=color, size=36)),
        title=dict(text=title, font=dict(color=COLORS['muted'], size=13)),
        gauge=dict(
            axis=dict(range=[0, 100], tickfont=dict(color=COLORS['muted'], size=10),
                      tickcolor=COLORS['border']),
            bar=dict(color=color, thickness=0.3),
            bgcolor=COLORS['surface'],
            bordercolor=COLORS['border'],
            steps=[
                dict(range=[0, threshold_low*100], color='rgba(110,231,183,0.1)'),
                dict(range=[threshold_low*100, threshold_high*100], color='rgba(252,211,77,0.1)'),
                dict(range=[threshold_high*100, 100], color='rgba(248,113,113,0.1)'),
            ],
            threshold=dict(
                line=dict(color=color, width=3),
                thickness=0.8,
                value=value * 100,
            ),
        ),
    ))
    fig.update_layout(
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(color=COLORS['muted']),
        height=250,
        margin=dict(l=20, r=20, t=40, b=20),
    )
    return fig

with col_g1:
    st.plotly_chart(make_gauge(prob_evasao, "Risco de Evasão", risco_cor), use_container_width=True)

with col_g2:
    st.plotly_chart(make_gauge(prob_pv, "Probabilidade de Ponto de Virada", pv_cor, 0.25, 0.5),
                    use_container_width=True)

st.divider()

# ── RECOMMENDATIONS ───────────────────────────────────────────
st.markdown("### 💡 Recomendação para este aluno")

if prob_evasao >= 0.6 and prob_pv < 0.25:
    st.markdown(insight(
        f"<strong>Aluno em situação crítica.</strong> Alto risco de evasão ({prob_evasao*100:.1f}%) "
        f"combinado com baixa probabilidade de Ponto de Virada ({prob_pv*100:.1f}%). "
        "Ação recomendada: <strong>contato imediato</strong> com a família e encaminhamento "
        "para a equipe de Psicologia. Verificar barreiras de transporte, conflito de horário "
        "ou questões de saúde familiar.",
        "danger"
    ), unsafe_allow_html=True)

elif prob_evasao >= 0.6:
    st.markdown(insight(
        f"<strong>Alto risco de evasão ({prob_evasao*100:.1f}%).</strong> "
        "Mesmo com potencial para Ponto de Virada, o aluno pode não completar o ciclo. "
        "Priorizar ações de retenção: contato proativo, verificar necessidades de suporte logístico.",
        "warning"
    ), unsafe_allow_html=True)

elif prob_pv >= 0.5 and bolsista == "Não":
    st.markdown(insight(
        f"<strong>Forte candidato a bolsa.</strong> Probabilidade de Ponto de Virada de {prob_pv*100:.1f}% "
        "e baixo risco de evasão. Este aluno reúne as condições para ser indicado ao programa de bolsas — "
        "o que historicamente aumenta em 4× a chance de atingir o Ponto de Virada.",
        "success"
    ), unsafe_allow_html=True)

elif prob_pv >= 0.5:
    st.markdown(insight(
        f"<strong>Alto potencial de Ponto de Virada ({prob_pv*100:.1f}%).</strong> "
        "Aluno no caminho certo. Manter o acompanhamento atual e reforçar os indicadores "
        "com menor desempenho.",
        "success"
    ), unsafe_allow_html=True)

elif prob_evasao < 0.3 and prob_pv < 0.25:
    st.markdown(insight(
        f"<strong>Aluno estável mas sem destaque.</strong> Risco de evasão baixo ({prob_evasao*100:.1f}%) "
        f"mas probabilidade de Ponto de Virada também baixa ({prob_pv*100:.1f}%). "
        "Verificar IPV e IEG — engajamento e integração aos princípios são os caminhos "
        "para destravar o desenvolvimento.",
        "info"
    ), unsafe_allow_html=True)

else:
    st.markdown(insight(
        f"<strong>Perfil intermediário.</strong> Risco de evasão: {prob_evasao*100:.1f}% | "
        f"Probabilidade de PV: {prob_pv*100:.1f}%. "
        "Monitorar evolução no próximo ciclo, com atenção especial ao IPV e IDA.",
        "info"
    ), unsafe_allow_html=True)

# ── FEATURE CONTRIBUTION ──────────────────────────────────────
st.divider()
st.markdown("### 🔍 Quais indicadores mais influenciam este resultado?")
st.caption("Importância global do modelo — os indicadores com maior barra são os que o modelo considera mais decisivos para a previsão de qualquer aluno.")

col_f1, col_f2 = st.columns(2)

imp_ev_series = pd.Series(rf_ev.feature_importances_, index=feats_ev)
imp_labels_ev = {
    'INDE_2021':'INDE Geral', 'IPV_2021':'IPV — Ponto de Virada', 'IDA_2021':'IDA — Acadêmico',
    'IEG_2021':'IEG — Engajamento', 'FASE_2021':'Fase do Programa', 'IAA_2021':'IAA — Autoavaliação',
    'IPP_2021':'IPP — Psicopedagógico', 'IPS_2021':'IPS — Psicossocial',
    'PEDRA_enc':'Pedra', 'DEFASAGEM_2021':'Defasagem', 'IAN_2021':'IAN — Aprendizado', 'Sexo_enc':'Sexo',
}
top_ev = imp_ev_series.sort_values(ascending=True).tail(6)

with col_f1:
    st.markdown("**Risco de evasão**")
    fig = go.Figure(go.Bar(
        x=top_ev.values, y=[imp_labels_ev.get(i,i) for i in top_ev.index],
        orientation='h', marker_color=COLORS['red'],
        text=[f"{v*100:.1f}%" for v in top_ev.values],
        textposition='outside', textfont=dict(color=COLORS['muted'], size=10),
    ))
    layout = PLOTLY_LAYOUT.copy()
    layout.update(height=260, xaxis_range=[0,0.22], margin=dict(l=16,r=60,t=10,b=16))
    fig.update_layout(**layout)
    st.plotly_chart(fig, use_container_width=True)

imp_pv_series = pd.Series(rf_pv.feature_importances_, index=feats_pv)
imp_labels_pv = {
    'IPV_2022':'IPV — Ponto de Virada', 'IPP_2022':'IPP — Psicopedagógico',
    'INDE_2022':'INDE Geral', 'NOTA_PORT_2022':'Nota Português',
    'IEG_2022':'IEG — Engajamento', 'IDA_2022':'IDA — Acadêmico',
    'BOLSISTA_enc':'É Bolsista', 'PEDRA_enc':'Pedra', 'IPS_2022':'IPS — Psicossocial',
    'IAA_2022':'IAA — Autoavaliação', 'NOTA_ING_2022':'Nota Inglês',
    'NOTA_MAT_2022':'Nota Matemática', 'IAN_2022':'IAN — Aprendizado', 'FASE_2022':'Fase',
}
top_pv = imp_pv_series.sort_values(ascending=True).tail(6)

with col_f2:
    st.markdown("**Probabilidade de Ponto de Virada**")
    fig2 = go.Figure(go.Bar(
        x=top_pv.values, y=[imp_labels_pv.get(i,i) for i in top_pv.index],
        orientation='h', marker_color=COLORS['gold'],
        text=[f"{v*100:.1f}%" for v in top_pv.values],
        textposition='outside', textfont=dict(color=COLORS['muted'], size=10),
    ))
    layout2 = PLOTLY_LAYOUT.copy()
    layout2.update(height=260, xaxis_range=[0,0.55], margin=dict(l=16,r=60,t=10,b=16))
    fig2.update_layout(**layout2)
    st.plotly_chart(fig2, use_container_width=True)

st.markdown("""
<div style="background:#0D0F1A;border:1px solid #1E2135;border-radius:8px;
            padding:0.9rem 1.2rem;margin-top:0.5rem;">
<p style="color:#475569;font-size:0.75rem;margin:0;line-height:1.6;">
⚠️ <strong style="color:#64748B;">Limitação importante:</strong>
Os modelos foram treinados nos dados históricos da ONG (2020–2022).
Evasão é influenciada por muitos fatores externos não capturados nos dados
(mudança de cidade, questões familiares, saúde). O score é um indicador de risco,
não uma certeza. Use como apoio à decisão, não como substituto do julgamento humano da equipe.
</p>
</div>
""", unsafe_allow_html=True)
