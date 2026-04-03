import streamlit as st
import plotly.graph_objs as go
import plotly.express as px
import pandas as pd
import numpy as np
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from util.style import inject_css, metric_card, insight, section_header, PLOTLY_LAYOUT, COLORS
from util.data import load_all, load_turma, load_motivos, PEDRA_ORDER, PEDRA_COLORS
from util.layout import sidebar

inject_css()
sidebar()

df       = load_all()
df_turma = load_turma()
df_motivos = load_motivos()

# ── HERO ─────────────────────────────────────────────────────
st.markdown("""
<div style="margin-bottom:2rem;">
    <div style="font-size:0.7rem;font-weight:600;letter-spacing:0.2em;text-transform:uppercase;
                color:#6EE7B7;margin-bottom:0.4rem;">DATATHON · FIAP PÓSTECH DATA ANALYTICS</div>
    <h1 style="font-size:2.4rem;font-weight:800;color:#F1F5F9;line-height:1.1;margin:0 0 0.5rem;">
        Luminar de Dados<br/><span style="color:#6EE7B7;">Iluminando Vidas</span>
    </h1>
    <p style="color:#64748B;font-size:0.95rem;max-width:680px;margin:0;">
        Análise do impacto educacional e social da ONG Passos Mágicos sobre crianças e jovens
        em situação de vulnerabilidade — baseada nos dados PEDE 2020, 2021 e 2022.
    </p>
</div>
""", unsafe_allow_html=True)

# ── KPI CARDS ────────────────────────────────────────────────
c1,c2,c3,c4,c5 = st.columns(5)

inde_22  = df['INDE_2022'].mean()
inde_20  = df['INDE_2020'].mean()
pv_pct   = (df['PONTO_VIRADA_2022']=='Sim').sum() / df['PONTO_VIRADA_2022'].notna().sum() * 100
df_b     = df[df['BOLSISTA_2022'].notna() & df['INDE_2022'].notna()]
bol_pv   = (df_b[df_b['BOLSISTA_2022']=='Sim']['PONTO_VIRADA_2022']=='Sim').mean()*100
top22    = (df['PEDRA_2022']=='Topázio').sum()
top20    = (df['PEDRA_2020']=='Topázio').sum()

with c1: st.markdown(metric_card("1.349","Alunos analisados","3 anos de dados"), unsafe_allow_html=True)
with c2: st.markdown(metric_card(f"{inde_22:.2f}","INDE médio 2022",f"vs {inde_20:.2f} em 2020",COLORS['accent2']), unsafe_allow_html=True)
with c3: st.markdown(metric_card(f"{pv_pct:.1f}%","Atingiram Ponto de Virada","em 2022",COLORS['gold']), unsafe_allow_html=True)
with c4: st.markdown(metric_card(f"{bol_pv:.1f}%","Bolsistas com Ponto de Virada",f"vs 9,4% não bolsistas",COLORS['accent']), unsafe_allow_html=True)
with c5: st.markdown(metric_card(f"{top22}","Alunos Topázio 2022",f"+{top22-top20} desde 2020",COLORS['gold']), unsafe_allow_html=True)

st.divider()

# ── INDE EVOLUTION + PEDRAS ──────────────────────────────────
col_a, col_b = st.columns([3,2])

with col_a:
    st.markdown(section_header("01 — IMPACTO LONGITUDINAL","Evolução do INDE: 2020 → 2021 → 2022"), unsafe_allow_html=True)
    df3 = df[['INDE_2020','INDE_2021','INDE_2022']].dropna()
    sample = df3.sample(min(120, len(df3)), random_state=42)

    fig = go.Figure()
    for _, row in sample.iterrows():
        is_up = row['INDE_2022'] > row['INDE_2020']
        fig.add_trace(go.Scatter(
            x=['2020','2021','2022'],
            y=[row['INDE_2020'],row['INDE_2021'],row['INDE_2022']],
            mode='lines', showlegend=False,
            line=dict(color='rgba(110,231,183,0.15)' if is_up else 'rgba(248,113,113,0.15)', width=1),
        ))
    means = [df3['INDE_2020'].mean(), df3['INDE_2021'].mean(), df3['INDE_2022'].mean()]
    fig.add_trace(go.Scatter(
        x=['2020','2021','2022'], y=means,
        mode='lines+markers+text',
        line=dict(color=COLORS['accent'], width=3),
        marker=dict(size=10, color=COLORS['accent']),
        text=[f"<b>{v:.2f}</b>" for v in means],
        textposition=['bottom center','bottom center','top center'],
        textfont=dict(color=COLORS['accent'], size=13),
        name='Média do grupo',
    ))
    layout = {**PLOTLY_LAYOUT, 'height':340, 'yaxis_title':"INDE", 'yaxis_range':[3,10],
              'xaxis':dict(**PLOTLY_LAYOUT['xaxis'], type='category',
                           categoryorder='array', categoryarray=['2020','2021','2022'])}
    fig.update_layout(**layout)
    fig.update_layout(hoverlabel=dict(bgcolor="#1A1D27",bordercolor="#2E3350",font=dict(color="#F1F5F9",size=12)))
    st.plotly_chart(fig, use_container_width=True)
    st.markdown(insight(
        "<strong>80,6% dos veteranos (3 anos) pioraram o INDE de 2020 a 2022.</strong> "
        "A aparente recuperação geral em 2022 é puxada pela entrada de novos alunos — "
        "não pela melhora dos veteranos. Isso revela um desafio de retenção de qualidade "
        "nas fases avançadas do programa.", "warning"
    ), unsafe_allow_html=True)

with col_b:
    st.markdown(section_header("02 — CLASSIFICAÇÃO","Distribuição por Pedra: 2020 vs 2022"), unsafe_allow_html=True)
    pedra_data = []
    for ano in ['2020','2022']:
        counts = df[f'PEDRA_{ano}'].value_counts()
        total_ano = counts.sum()
        for p in PEDRA_ORDER:
            pedra_data.append({'Ano':ano,'Pedra':p,'Count':counts.get(p,0),
                               'Pct': counts.get(p,0)/total_ano*100})
    df_ped = pd.DataFrame(pedra_data)

    fig2 = go.Figure()
    for pedra in PEDRA_ORDER:
        sub = df_ped[df_ped['Pedra']==pedra]
        fig2.add_trace(go.Bar(
            name=pedra, x=sub['Ano'], y=sub['Pct'],
            marker_color=PEDRA_COLORS[pedra],
            text=[f"{v:.1f}%" for v in sub['Pct']],
            textposition='inside',
            textfont=dict(color='#0F1117', size=11),
        ))
    layout2 = {**PLOTLY_LAYOUT, 'height':240, 'barmode':'stack', 'yaxis_title':"%",
               'legend':dict(orientation='h', y=-0.15, x=0.5, xanchor='center'),
               'xaxis':dict(**PLOTLY_LAYOUT['xaxis'], type='category')}
    fig2.update_layout(**layout2)
    fig2.update_layout(hoverlabel=dict(bgcolor="#1A1D27",bordercolor="#2E3350",font=dict(color="#F1F5F9",size=12)))
    st.plotly_chart(fig2, use_container_width=True)
    st.markdown(f"""
    <div style="display:grid;grid-template-columns:1fr 1fr;gap:0.5rem;margin-top:0.5rem;">
        <div style="background:#1A1D27;border:1px solid #2E3350;border-radius:8px;padding:0.8rem;text-align:center;">
            <div style="font-size:1.4rem;font-weight:700;color:#FCD34D;">+41%</div>
            <div style="font-size:0.68rem;color:#475569;text-transform:uppercase;letter-spacing:0.1em;">Topázio 2020→2022</div>
        </div>
        <div style="background:#1A1D27;border:1px solid #2E3350;border-radius:8px;padding:0.8rem;text-align:center;">
            <div style="font-size:1.4rem;font-weight:700;color:#F9A8D4;">+46%</div>
            <div style="font-size:0.68rem;color:#475569;text-transform:uppercase;letter-spacing:0.1em;">Ágata 2020→2022</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

st.divider()

# ── BOLSISTAS + VULNERABILIDADE ──────────────────────────────
col_c, col_d = st.columns(2)

with col_c:
    st.markdown(section_header("03 — BOLSAS","Bolsistas vs Não Bolsistas"), unsafe_allow_html=True)
    df_b2 = df[df['BOLSISTA_2022'].notna() & df['INDE_2022'].notna() & df['PONTO_VIRADA_2022'].notna()]
    grupos = df_b2.groupby('BOLSISTA_2022').agg(
        INDE=('INDE_2022','mean'),
        PV=('PONTO_VIRADA_2022', lambda x: (x=='Sim').mean()*100),
        n=('INDE_2022','count')
    ).reset_index()
    grupos['Label'] = grupos['BOLSISTA_2022'].map({'Sim':'Bolsistas','Não':'Não Bolsistas'})

    fig3 = go.Figure()
    fig3.add_trace(go.Bar(
        name='INDE Médio', x=grupos['Label'], y=grupos['INDE'],
        marker_color=[COLORS['accent'],COLORS['dim']],
        text=[f"{v:.3f}" for v in grupos['INDE']],
        textposition='outside', textfont=dict(color=COLORS['text']),
        yaxis='y', offsetgroup=1,
    ))
    fig3.add_trace(go.Bar(
        name='% Ponto de Virada', x=grupos['Label'], y=grupos['PV'],
        marker_color=[COLORS['gold'],COLORS['border']],
        text=[f"{v:.1f}%" for v in grupos['PV']],
        textposition='outside', textfont=dict(color=COLORS['text']),
        yaxis='y2', offsetgroup=2,
    ))
    layout3 = {**PLOTLY_LAYOUT, 'height':300, 'barmode':'group',
               'yaxis':dict(**PLOTLY_LAYOUT['yaxis'], title='INDE Médio', range=[0,9]),
               'yaxis2':dict(overlaying='y', side='right', title='% Ponto de Virada',
                             range=[0,55], gridcolor='rgba(0,0,0,0)',
                             tickfont=dict(color=COLORS['muted']),
                             title_font=dict(color=COLORS['muted'])),
               'legend':dict(orientation='h', y=-0.18, x=0.5, xanchor='center')}
    fig3.update_layout(**layout3)
    fig3.update_layout(hoverlabel=dict(bgcolor="#1A1D27",bordercolor="#2E3350",font=dict(color="#F1F5F9",size=12)))
    st.plotly_chart(fig3, use_container_width=True)
    st.markdown(insight(
        "Bolsistas têm <strong>INDE 11,1% maior</strong> e <strong>4× mais chance de atingir "
        "Ponto de Virada</strong> (38,9% vs 9,4%). Expandir bolsas é a intervenção com maior "
        "ROI educacional evidenciado.", "success"
    ), unsafe_allow_html=True)

with col_d:
    st.markdown(section_header("04 — VULNERABILIDADE","Alunos em situação de risco 2022"), unsafe_allow_html=True)
    df22 = df[df['INDE_2022'].notna()].copy()
    vuln_cats = {
        'IPS Psicossocial':       (df22['IPS_2022'] < df22['IPS_2022'].quantile(0.25)).sum(),
        'IAA Autoavaliação':      (df22['IAA_2022'] < df22['IAA_2022'].quantile(0.25)).sum(),
        'IPP Psicopedagógico':    (df22['IPP_2022'] < df22['IPP_2022'].quantile(0.25)).sum(),
        'Multi-vulnerável\n(IPS+IAA)': ((df22['IPS_2022'] < df22['IPS_2022'].quantile(0.25)) &
                                        (df22['IAA_2022'] < df22['IAA_2022'].quantile(0.25))).sum(),
    }
    total_22 = len(df22)
    fig4 = go.Figure(go.Bar(
        x=list(vuln_cats.values()), y=list(vuln_cats.keys()),
        orientation='h',
        marker_color=[COLORS['accent2'],COLORS['accent2'],COLORS['accent2'],COLORS['red']],
        text=[f"{v} ({v/total_22*100:.1f}%)" for v in vuln_cats.values()],
        textposition='outside', textfont=dict(color=COLORS['muted'], size=11),
    ))
    layout4 = {**PLOTLY_LAYOUT, 'height':240,
               'xaxis':dict(**PLOTLY_LAYOUT['xaxis'], title='Nº de alunos',
                            range=[0, max(vuln_cats.values())*1.4]),
               'margin':dict(l=16,r=80,t=10,b=16)}
    fig4.update_layout(**layout4)
    fig4.update_layout(hoverlabel=dict(bgcolor="#1A1D27",bordercolor="#2E3350",font=dict(color="#F1F5F9",size=12)))
    st.plotly_chart(fig4, use_container_width=True)
    st.markdown(insight(
        "<strong>73 alunos são multi-vulneráveis</strong> (IPS + IAA abaixo do P25). "
        "Esse grupo tem probabilidade de Ponto de Virada próxima de zero. "
        "Intervenção prioritária da equipe de Psicologia.", "danger"
    ), unsafe_allow_html=True)

st.divider()

# ── EVASION ──────────────────────────────────────────────────
st.markdown(section_header("05 — EVASÃO","Por que os alunos saem do programa?"), unsafe_allow_html=True)
df_inat = df_turma[df_turma['IdMotivoInativacao'].notna()].merge(df_motivos, on='IdMotivoInativacao', how='left')
df_inat = df_inat[df_inat['MotivoInativacao'].notna()]
top_motivos = df_inat['MotivoInativacao'].value_counts().head(8).reset_index()
top_motivos.columns = ['Motivo','Total']
top_motivos['Pct'] = (top_motivos['Total']/top_motivos['Total'].sum()*100).round(1)

col_e, col_f = st.columns([2,1])
with col_e:
    colors_bar = [COLORS['accent'] if i==0 else COLORS['red'] if i==1 else COLORS['accent2']
                  for i in range(len(top_motivos))]
    fig5 = go.Figure(go.Bar(
        x=top_motivos['Total'], y=top_motivos['Motivo'], orientation='h',
        marker_color=colors_bar,
        text=[f"{r['Total']} ({r['Pct']:.1f}%)" for _,r in top_motivos.iterrows()],
        textposition='outside', textfont=dict(color=COLORS['muted'], size=11),
    ))
    layout5 = {**PLOTLY_LAYOUT, 'height':300,
               'xaxis':dict(**PLOTLY_LAYOUT['xaxis'], title='Número de evasões',
                            range=[0, top_motivos['Total'].max()*1.35]),
               'margin':dict(l=16,r=80,t=10,b=16),
               'yaxis':dict(**PLOTLY_LAYOUT['yaxis'], categoryorder='total ascending')}
    fig5.update_layout(**layout5)
    fig5.update_layout(hoverlabel=dict(bgcolor="#1A1D27",bordercolor="#2E3350",font=dict(color="#F1F5F9",size=12)))
    st.plotly_chart(fig5, use_container_width=True)
with col_f:
    st.markdown(insight(
        "<strong>Transferência (18,8%) e Sem Retorno ao Contato (17,6%)</strong> somam 36% do total. "
        "Ambos indicam ruptura de vínculo, não rejeição ao programa.", "info"
    ), unsafe_allow_html=True)
    st.markdown(insight(
        "<strong>A hipótese de evasão masculina por trabalho não se confirma.</strong> "
        "Taxa F=53% vs M=57% — diferença de 4 p.p. sem relevância prática.", "warning"
    ), unsafe_allow_html=True)

st.divider()

# ── INDE FORMULA ─────────────────────────────────────────────
st.markdown(section_header("06 — METODOLOGIA","Fórmula oficial do INDE — confirmada nos dados"), unsafe_allow_html=True)
inds  = ['IDA','IEG','IPV','IAA','IPS','IPP','IAN']
pesos = [20,20,20,10,10,10,10]
corrs = [0.821,0.805,0.792,0.463,0.274,0.285,0.395]

fig6 = go.Figure()
fig6.add_trace(go.Bar(
    name='Peso no INDE (%)', x=inds, y=pesos,
    marker_color=COLORS['accent'], opacity=0.85, yaxis='y',
    text=[f"{p}%" for p in pesos], textposition='inside',
    textfont=dict(color='#0F1117', size=12),
))
fig6.add_trace(go.Scatter(
    name='Correlação com INDE', x=inds, y=corrs,
    mode='lines+markers',
    line=dict(color=COLORS['gold'], width=2.5, dash='dot'),
    marker=dict(size=9, color=COLORS['gold']),
    yaxis='y2',
    text=[f"r={c:.2f}" for c in corrs],
    textposition='top center', textfont=dict(color=COLORS['gold'], size=10),
))
layout6 = {**PLOTLY_LAYOUT, 'height':300,
           'yaxis':dict(**PLOTLY_LAYOUT['yaxis'], title='Peso (%)', range=[0,28]),
           'yaxis2':dict(overlaying='y', side='right', title='Correlação',
                         range=[0,1.1], gridcolor='rgba(0,0,0,0)',
                         tickfont=dict(color=COLORS['muted']),
                         title_font=dict(color=COLORS['muted'])),
           'legend':dict(orientation='h', y=-0.18, x=0.5, xanchor='center'),
           'margin':dict(l=16,r=60,t=20,b=16)}
fig6.update_layout(**layout6)
fig6.update_layout(hoverlabel=dict(bgcolor="#1A1D27",bordercolor="#2E3350",font=dict(color="#F1F5F9",size=12)))
st.plotly_chart(fig6, use_container_width=True)
st.markdown(insight(
    "<strong>IDA e IEG são os drivers reais do INDE</strong> (peso 20% + correlação ~0,82). "
    "IPS e IPP têm peso 10% mas correlação baixa (~0,28) — medem dimensões importantes "
    "mas não se traduzem diretamente no índice numérico. "
    "<strong>INDE = IAN×10% + IDA×20% + IEG×20% + IAA×10% + IPS×10% + IPP×10% + IPV×20%</strong> "
    "(verificado com R²=1,000).", "info"
), unsafe_allow_html=True)
