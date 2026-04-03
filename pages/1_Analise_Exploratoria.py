import streamlit as st
import plotly.graph_objs as go
import plotly.express as px
from plotly.subplots import make_subplots
import pandas as pd
import numpy as np
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from util.style import inject_css, metric_card, insight, section_header, PLOTLY_LAYOUT, COLORS, get_layout, HOVER, apply_layout, HOVER
from util.data import load_all, load_turma, PEDRA_ORDER, PEDRA_COLORS, IND_LABELS, IND_PESOS
from util.layout import sidebar

inject_css()
sidebar()

df = load_all()
df_turma = load_turma()

st.markdown(section_header("ANÁLISE EXPLORATÓRIA","Padrões, indicadores e trajetórias"), unsafe_allow_html=True)

# ── TABS ──────────────────────────────────────────────────────
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📈 INDE & Indicadores", "💎 Sistema de Pedras",
    "⚧ Análise por Gênero", "📚 Defasagem & Notas", "🔗 Correlações"
])

# ── TAB 1: INDE & INDICADORES ─────────────────────────────────
with tab1:
    c1, c2 = st.columns(2)

    with c1:
        st.markdown("#### Distribuição do INDE por ano")
        fig = go.Figure()
        for ano, color in [('2020',COLORS['accent2']),('2021',COLORS['red']),('2022',COLORS['accent'])]:
            data = df[f'INDE_{ano}'].dropna()
            fig.add_trace(go.Violin(y=data, name=f"{ano} (n={len(data)})",
                                    box_visible=True, meanline_visible=True,
                                    fillcolor=color, opacity=0.5, line_color=color,
                                    points=False))
        fig.update_layout(**get_layout(height=360))
        st.plotly_chart(fig, use_container_width=True)

    with c2:
        st.markdown("#### Evolução dos indicadores (alunos nos 3 anos)")
        df3i = df[['IDA_2020','IDA_2021','IDA_2022','IEG_2020','IEG_2021','IEG_2022',
                   'IPV_2020','IPV_2021','IPV_2022','IAA_2020','IAA_2021','IAA_2022',
                   'IPS_2020','IPS_2021','IPS_2022','IPP_2020','IPP_2021','IPP_2022',
                   'IAN_2020','IAN_2021','IAN_2022']].dropna()

        inds = ['IDA','IEG','IPV','IAA','IPS','IPP','IAN']
        colors_ind = [COLORS['accent'],COLORS['accent2'],COLORS['gold'],
                      '#34D399','#60A5FA',COLORS['red'],'#C084FC']

        fig2 = go.Figure()
        for ind, color in zip(inds, colors_ind):
            means = [df3i[f'{ind}_{a}'].mean() for a in ['2020','2021','2022']]
            peso = IND_PESOS[ind]
            fig2.add_trace(go.Scatter(
                x=['2020','2021','2022'], y=means, mode='lines+markers',
                name=f"{IND_LABELS[ind]} ({peso}%)",
                line=dict(color=color, width=2 if peso==20 else 1.2,
                          dash='solid' if peso==20 else 'dot'),
                marker=dict(size=8 if peso==20 else 5, color=color),
            ))
        apply_layout(fig2, height=360, legend=dict(x=1.01, y=0.5, orientation='v'))
        st.plotly_chart(fig2, use_container_width=True)

    st.markdown(insight(
        "<strong>IDA (Desempenho Acadêmico) sofreu a maior queda em 2021</strong>: 7,24 → 5,73 — queda de 21%. "
        "Como IDA tem peso de 20% no INDE, essa queda explica ~80% da deterioração do índice geral naquele ano. "
        "Em 2022 houve recuperação parcial para 5,95, mas ainda 18% abaixo do patamar pré-pandemia.",
        "warning"
    ), unsafe_allow_html=True)

    # INDE by fase - more insightful
    st.markdown("#### INDE médio por fase (2022)")
    df_f = df[df['INDE_2022'].notna() & df['FASE_2022'].notna()].copy()
    df_f['FASE_2022'] = df_f['FASE_2022'].astype(int)
    fase_inde = df_f.groupby('FASE_2022').agg(INDE=('INDE_2022','mean'), n=('INDE_2022','count')).reset_index()
    fase_inde['label'] = fase_inde.apply(lambda r: f"Fase {int(r['FASE_2022'])}<br>(n={int(r['n'])})", axis=1)

    fig3 = go.Figure(go.Bar(
        x=fase_inde['label'], y=fase_inde['INDE'],
        marker_color=[COLORS['accent'] if v >= 7.0 else COLORS['accent2'] if v >= 6.5 else COLORS['red']
                      for v in fase_inde['INDE']],
        text=[f"{v:.2f}" for v in fase_inde['INDE']],
        textposition='outside', textfont=dict(color=COLORS['text']),
    ))
    apply_layout(fig3, height=320, yaxis_title="INDE médio", yaxis_range=[0,9],
                   xaxis_title="Fase do programa")
    fig3.update_layout(hoverlabel=dict(bgcolor="#1A1D27",bordercolor="#2E3350",font=dict(color="#F1F5F9",size=12)))
    st.plotly_chart(fig3, use_container_width=True)

# ── TAB 2: PEDRAS ─────────────────────────────────────────────
with tab2:
    c1, c2 = st.columns(2)

    with c1:
        st.markdown("#### Distribuição por ano")
        pedra_data = []
        for ano in ['2020','2021','2022']:
            vc = df[f'PEDRA_{ano}'].value_counts()
            total = vc.sum()
            for p in PEDRA_ORDER:
                pedra_data.append({'Ano':ano,'Pedra':p,'Count':vc.get(p,0),'Pct':vc.get(p,0)/total*100})
        df_ped = pd.DataFrame(pedra_data)

        fig = px.bar(df_ped, x='Ano', y='Count', color='Pedra',
                     color_discrete_map=PEDRA_COLORS, barmode='group', text='Count',
                     category_orders={'Pedra':PEDRA_ORDER})
        fig.update_traces(textposition='outside')
        fig.update_layout(**get_layout(height=340))
        st.plotly_chart(fig, use_container_width=True)

    with c2:
        st.markdown("#### Ponto de Virada por pedra (2022)")
        df_pv = df[['PEDRA_2022','PONTO_VIRADA_2022']].dropna()
        pv_ped = df_pv.groupby('PEDRA_2022')['PONTO_VIRADA_2022'].value_counts(normalize=True).unstack(fill_value=0)*100
        pv_ped = pv_ped.reindex([p for p in PEDRA_ORDER if p in pv_ped.index])
        if 'Sim' not in pv_ped.columns: pv_ped['Sim'] = 0

        fig2 = go.Figure(go.Bar(
            x=pv_ped.index, y=pv_ped['Sim'],
            marker_color=[PEDRA_COLORS[p] for p in pv_ped.index],
            text=[f"{v:.1f}%" for v in pv_ped['Sim']],
            textposition='outside', textfont=dict(color=COLORS['text']),
        ))
        apply_layout(fig2, height=340, yaxis_title="% com Ponto de Virada", yaxis_range=[0,65])
        st.plotly_chart(fig2, use_container_width=True)

    st.markdown(insight(
        "<strong>Topázio: 52,3% atingem Ponto de Virada.</strong> Quartzo: 0%. "
        "O Ponto de Virada não é aleatório — está fortemente vinculado ao nível da pedra. "
        "Promover o avanço de Ágata → Ametista → Topázio é o caminho estrutural para mais Pontos de Virada.",
        "success"
    ), unsafe_allow_html=True)

    # Transição de pedras
    st.markdown("#### Transição 2021 → 2022")
    df_tr = df[['PEDRA_2021','PEDRA_2022']].dropna()
    df_tr = df_tr[df_tr['PEDRA_2021'].isin(PEDRA_ORDER) & df_tr['PEDRA_2022'].isin(PEDRA_ORDER)]
    pn = {p:i for i,p in enumerate(PEDRA_ORDER)}
    df_tr['mov'] = df_tr.apply(
        lambda r: 'Promovido' if pn[r['PEDRA_2022']] > pn[r['PEDRA_2021']]
        else ('Mantido' if pn[r['PEDRA_2022']] == pn[r['PEDRA_2021']] else 'Rebaixado'), axis=1)
    mc = df_tr['mov'].value_counts().reset_index()
    mc.columns = ['Movimento','Count']
    mc['Pct'] = (mc['Count']/mc['Count'].sum()*100).round(1)
    cm = {'Promovido':COLORS['accent'],'Mantido':COLORS['accent2'],'Rebaixado':COLORS['red']}

    fig3 = go.Figure(go.Bar(
        x=mc['Movimento'], y=mc['Count'],
        marker_color=[cm.get(m,COLORS['dim']) for m in mc['Movimento']],
        text=[f"{r['Count']} ({r['Pct']:.1f}%)" for _,r in mc.iterrows()],
        textposition='outside', textfont=dict(color=COLORS['text']),
        width=0.4,
    ))
    fig3.update_layout(**get_layout(height=280))
    fig3.update_layout(hoverlabel=dict(bgcolor="#1A1D27",bordercolor="#2E3350",font=dict(color="#F1F5F9",size=12)))
    st.plotly_chart(fig3, use_container_width=True)

    df_tr2 = df_tr.copy()
    prom = (df_tr2['mov']=='Promovido').sum()
    total_tr = len(df_tr2)
    st.markdown(insight(
        f"<strong>{prom} alunos ({prom/total_tr*100:.1f}%) foram promovidos de pedra</strong> de 2021 para 2022. "
        "A maioria permanece na mesma pedra — o que é esperado, pois a progressão é criteriosa. "
        "Alunos rebaixados merecem atenção especial da equipe pedagógica.",
        "info"
    ), unsafe_allow_html=True)

# ── TAB 3: GÊNERO ─────────────────────────────────────────────
with tab3:
    SEXO_C = {'F':COLORS['fem'],'M':COLORS['masc']}

    c1, c2 = st.columns(2)

    with c1:
        st.markdown("#### Taxa de evasão pós-2020 por gênero")
        df_ev = df[df['INDE_2020'].notna() & df['Sexo'].notna()].copy()
        df_ev['Evadiu'] = ~df_ev['INDE_2022'].notna()
        taxa = df_ev.groupby('Sexo')['Evadiu'].agg(['sum','mean','count']).reset_index()
        taxa.columns = ['Sexo','N','Taxa','Total']
        taxa['Label'] = taxa['Sexo'].map({'F':'Feminino','M':'Masculino'})

        fig = go.Figure()
        for _, row in taxa.iterrows():
            fig.add_trace(go.Bar(
                name=row['Label'], x=[row['Label']], y=[row['Taxa']*100],
                marker_color=SEXO_C[row['Sexo']],
                text=f"{row['Taxa']*100:.1f}%", textposition='outside',
                textfont=dict(color=COLORS['text']), width=0.35,
            ))
        apply_layout(fig, height=300, yaxis_range=[0,75], showlegend=False, yaxis_title="%")
        st.plotly_chart(fig, use_container_width=True)

    with c2:
        st.markdown("#### INDE médio por gênero e ano")
        inde_g = []
        for ano in ['2020','2021','2022']:
            col = f'INDE_{ano}'
            g = df[df[col].notna() & df['Sexo'].notna()].groupby('Sexo')[col].agg(['mean','count']).reset_index()
            for _, row in g.iterrows():
                inde_g.append({'Ano':ano,'Sexo':row['Sexo'],'INDE':row['mean'],'n':row['count']})
        df_ig = pd.DataFrame(inde_g)

        fig2 = go.Figure()
        for s in ['F','M']:
            sub = df_ig[df_ig['Sexo']==s]
            lbl = 'Feminino' if s=='F' else 'Masculino'
            fig2.add_trace(go.Scatter(
                x=sub['Ano'], y=sub['INDE'], mode='lines+markers+text',
                name=lbl, line=dict(color=SEXO_C[s], width=2.5), marker=dict(size=9),
                text=[f"{v:.3f}" for v in sub['INDE']], textposition='top center',
                textfont=dict(color=SEXO_C[s], size=11),
            ))
        apply_layout(fig2, height=300, yaxis_range=[6.5,7.7],
                       xaxis=dict(**PLOTLY_LAYOUT['xaxis'], type='category'))
        st.plotly_chart(fig2, use_container_width=True)

    st.markdown(insight(
        "<strong>A hipótese de evasão masculina por trabalho não se confirma nos dados.</strong> "
        "Taxa pós-2020: M=56,9% vs F=53,0% — diferença de 3,9 p.p. sem relevância prática. "
        "INDE praticamente idêntico entre gêneros (diferença de 0,020 pontos em 2022). "
        "O programa trata ambos de forma igualmente efetiva.",
        "danger"
    ), unsafe_allow_html=True)

    # Faixa etária evasão
    st.markdown("#### Faixa etária na evasão por gênero")
    inat = df_turma[df_turma['IdMotivoInativacao'].notna() & df_turma['Sexo'].notna() & df_turma['IdadeInativacao'].notna()].copy()
    bins = [0,9,11,13,15,17,19,30]
    lbls = ['<10','10-11','12-13','14-15','16-17','18-19','20+']
    inat['IdadeInativacao'] = pd.to_numeric(inat['IdadeInativacao'], errors='coerce')
    inat = inat.dropna(subset=['IdadeInativacao'])
    inat['Faixa'] = pd.cut(inat['IdadeInativacao'], bins=bins, labels=lbls)
    fx = inat.groupby(['Faixa','Sexo']).size().reset_index(name='Count')
    ts = fx.groupby('Sexo')['Count'].transform('sum')
    fx['Pct'] = (fx['Count']/ts*100).round(1)
    fx['Label'] = fx['Sexo'].map({'F':'Feminino','M':'Masculino'})

    fig3 = px.bar(fx, x='Faixa', y='Pct', color='Label',
                  color_discrete_map={'Feminino':COLORS['fem'],'Masculino':COLORS['masc']},
                  barmode='group', text='Pct',
                  category_orders={'Faixa':lbls})
    fig3.update_traces(texttemplate='%{text:.1f}%', textposition='outside')
    apply_layout(fig3, height=320, yaxis_title='% das evasões do gênero', xaxis_title='Faixa etária (anos)',
                   xaxis=dict(**PLOTLY_LAYOUT['xaxis'], type='category'))
    fig3.update_layout(hoverlabel=dict(bgcolor="#1A1D27",bordercolor="#2E3350",font=dict(color="#F1F5F9",size=12)))
    st.plotly_chart(fig3, use_container_width=True)

    st.markdown(insight(
        "<strong>Feminino evade muito mais entre 18-19 anos (13,1% vs 5,1% masculino)</strong> — "
        "possível saída por outros fatores sociais em jovens adultas. "
        "Pico de evasão em 14-15 anos para ambos os gêneros.",
        "warning"
    ), unsafe_allow_html=True)

# ── TAB 4: DEFASAGEM & NOTAS ──────────────────────────────────
with tab4:
    c1, c2 = st.columns(2)

    with c1:
        st.markdown("#### Defasagem escolar 2021")
        dc = df['DEFASAGEM_2021'].value_counts().sort_index().reset_index()
        dc.columns = ['Defasagem','Count']
        dc['Cat'] = dc['Defasagem'].apply(
            lambda x: 'Abaixo' if x<0 else ('No nível' if x==0 else 'Acima'))
        color_map = {'Abaixo':COLORS['red'],'No nível':COLORS['accent'],'Acima':COLORS['accent2']}

        fig = px.bar(dc, x='Defasagem', y='Count', color='Cat',
                     color_discrete_map=color_map, text='Count')
        fig.update_traces(textposition='outside')
        fig.update_layout(**get_layout(height=320))
        st.plotly_chart(fig, use_container_width=True)

        total_def = df['DEFASAGEM_2021'].notna().sum()
        abaixo = (df['DEFASAGEM_2021']<0).sum()
        st.markdown(insight(f"<strong>{abaixo/total_def*100:.0f}% dos alunos estão abaixo do nível ideal</strong> para sua idade — justifica o modelo de Aceleração do Conhecimento.", "warning"), unsafe_allow_html=True)

    with c2:
        st.markdown("#### Notas por disciplina 2022")
        for col in ['NOTA_PORT_2022','NOTA_MAT_2022','NOTA_ING_2022']:
            df[col] = pd.to_numeric(df[col].astype(str).str.replace(',','.'), errors='coerce')
        df_n = df[['INDE_2022','NOTA_PORT_2022','NOTA_MAT_2022','NOTA_ING_2022']].dropna()

        fig2 = go.Figure()
        for col, name, color in [('NOTA_PORT_2022','Português',COLORS['accent2']),
                                   ('NOTA_MAT_2022','Matemática',COLORS['accent']),
                                   ('NOTA_ING_2022','Inglês',COLORS['gold'])]:
            fig2.add_trace(go.Violin(y=df_n[col], name=f"{name} (μ={df_n[col].mean():.2f})",
                                     box_visible=True, meanline_visible=True,
                                     fillcolor=color, opacity=0.5, line_color=color, points=False))
        fig2.update_layout(**get_layout(height=320))
        st.plotly_chart(fig2, use_container_width=True)

        corrs = {
            'Inglês': df_n['NOTA_ING_2022'].corr(df_n['INDE_2022']),
            'Português': df_n['NOTA_PORT_2022'].corr(df_n['INDE_2022']),
            'Matemática': df_n['NOTA_MAT_2022'].corr(df_n['INDE_2022']),
        }
        st.markdown(insight(
            f"<strong>Inglês tem maior correlação com INDE (r=0,72)</strong> vs Português (r=0,70) e Matemática (r=0,69). "
            f"Pode ser proxy de engajamento global — alunos mais comprometidos se saem melhor nas três, mas especialmente no Inglês.",
            "info"
        ), unsafe_allow_html=True)

# ── TAB 5: CORRELAÇÕES ────────────────────────────────────────
with tab5:
    st.markdown("#### Matriz de correlação — indicadores 2022")

    cols_corr = ['INDE_2022','IAA_2022','IEG_2022','IPS_2022','IDA_2022',
                 'IPP_2022','IPV_2022','IAN_2022','NOTA_PORT_2022','NOTA_MAT_2022','NOTA_ING_2022']
    df_corr = df[cols_corr].dropna()
    corr_matrix = df_corr.corr()

    labels_corr = ['INDE','IAA','IEG','IPS','IDA','IPP','IPV','IAN','Port.','Mat.','Ing.']
    fig = go.Figure(go.Heatmap(
        z=corr_matrix.values,
        x=labels_corr, y=labels_corr,
        colorscale=[[0,COLORS['red']],[0.5,'#1A1D27'],[1,COLORS['accent']]],
        zmid=0, zmin=-1, zmax=1,
        text=[[f"{v:.2f}" for v in row] for row in corr_matrix.values],
        texttemplate="%{text}",
        textfont=dict(size=10, color=COLORS['text']),
        hovertemplate='%{x} × %{y}: %{z:.3f}<extra></extra>',
        showscale=True,
        colorbar=dict(tickfont=dict(color=COLORS['muted']), title=dict(text='r', font=dict(color=COLORS['muted']))),
    ))
    apply_layout(fig, height=500, xaxis=dict(**PLOTLY_LAYOUT['xaxis'], side='bottom'),
                  margin=dict(l=16,r=16,t=20,b=16))
    fig.update_layout(hoverlabel=dict(bgcolor="#1A1D27",bordercolor="#2E3350",font=dict(color="#F1F5F9",size=12)))
    st.plotly_chart(fig, use_container_width=True)

    st.markdown(insight(
        "<strong>IDA, IEG e IPV dominam a correlação com INDE</strong> (r > 0,79). "
        "IPS e IPP têm baixa correlação com INDE mas são críticos para bem-estar — "
        "uma limitação do índice: alunos emocionalmente vulneráveis podem ter INDE ok "
        "mas precisar urgentemente de intervenção.",
        "info"
    ), unsafe_allow_html=True)
