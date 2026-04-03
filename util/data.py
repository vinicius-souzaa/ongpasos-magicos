import pandas as pd
import numpy as np
import streamlit as st

@st.cache_data
def load_all():
    df = pd.read_csv("PEDE_PASSOS_DATASET_MERGED.csv")
    for col in df.columns:
        if any(x in col for x in ['INDE','IAA','IEG','IPS','IDA','IPP','IPV','IAN','NOTA_','FASE_','DEFASAGEM']):
            df[col] = pd.to_numeric(df[col].astype(str).str.replace(',', '.'), errors='coerce')
    for col in ['PEDRA_2020','PEDRA_2021','PEDRA_2022']:
        if col in df.columns:
            df[col] = df[col].replace({'D9891/2A': np.nan, '#NULO!': np.nan})
    return df

@st.cache_data
def load_turma():
    df = pd.read_csv("TbAlunoTurma_enriched.csv")
    return df

@st.cache_data
def load_motivos():
    return pd.read_csv("TbMotivoInativacao.csv")

PEDRA_ORDER  = ['Quartzo', 'Ágata', 'Ametista', 'Topázio']
PEDRA_COLORS = {'Quartzo':'#67E8F9','Ágata':'#F9A8D4','Ametista':'#A78BFA','Topázio':'#FCD34D'}
ANOS         = ['2020', '2021', '2022']
IND_LABELS   = {
    'IDA':'Desempenho Acadêmico','IEG':'Engajamento','IPV':'Ponto de Virada',
    'IAA':'Autoavaliação','IPS':'Psicossocial','IPP':'Psicopedagógico','IAN':'Nível de Aprendizado',
}
IND_PESOS    = {'IDA':20,'IEG':20,'IPV':20,'IAA':10,'IPS':10,'IPP':10,'IAN':10}
