import json
import os
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

import joblib
import numpy as np
import pandas as pd
import streamlit as st
import streamlit.components.v1 as components
from dotenv import load_dotenv

from rotas import LINHAS, NOMES, alternativa
from treinar import FEATURES, treinar
from gemma_api import GemmaError, explicar

load_dotenv()
st.set_page_config(page_title='RotaCerta IA', page_icon='🚌', layout='wide', initial_sidebar_state='collapsed')
mapa = components.declare_component('mapa_pontos', path=str(Path(__file__).parent / 'mapa'))
st.markdown('''<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&display=swap');
/* Mantém a barra de rolagem visível na área principal do Streamlit. */
section[data-testid="stMain"]{overflow-y:scroll !important;scrollbar-width:auto;scrollbar-color:#789487 #e5eee7}
section[data-testid="stMain"]::-webkit-scrollbar{width:11px}
section[data-testid="stMain"]::-webkit-scrollbar-track{background:#e5eee7}
section[data-testid="stMain"]::-webkit-scrollbar-thumb{background:#789487;border:2px solid #e5eee7;border-radius:8px}
section[data-testid="stMain"]::-webkit-scrollbar-thumb:hover{background:#426d5b}

html,body,[class*="css"],.stApp{font-family:'DM Sans',system-ui,sans-serif;color:#173a32}.stApp{background:#f5f8f5}header[data-testid="stHeader"]{background:transparent}#MainMenu,footer{visibility:hidden}.block-container{max-width:1250px;padding:1.5rem 2.3rem 3rem}h1,h2,h3{letter-spacing:-.025em;color:#173a32}h1{font-size:2rem;line-height:1.2;margin:0}h2{font-size:1.35rem}h3{font-size:1.08rem}.topbar{display:flex;align-items:center;justify-content:space-between;border-bottom:1px solid #dce8df;padding:0 0 20px;margin-bottom:28px}.brand{display:flex;align-items:center;gap:10px;font-size:18px;font-weight:800;letter-spacing:-.03em}.brand-icon{display:grid;place-items:center;width:35px;height:35px;border-radius:10px;background:#245b48;color:#fff}.top-tag{font-size:12px;font-weight:700;color:#245b48;background:#e3f0e7;padding:7px 11px;border-radius:20px}.intro{margin:0 0 24px}.intro p{color:#557268;margin:8px 0 0;font-size:15px}.section-head{display:flex;justify-content:space-between;align-items:end;margin:0 0 12px}.section-head strong{font-size:16px;color:#173a32}.section-head span{font-size:12px;color:#557268}.panel-title{font-size:18px;font-weight:700;color:#173a32;margin:0 0 5px}.panel-copy{font-size:13px;line-height:1.5;color:#557268;margin:0 0 18px}.selected-point{background:#e4f0e7;border-radius:12px;padding:15px 16px;margin:2px 0 12px}.selected-point small{display:block;color:#446b59;font-size:12px;font-weight:700;margin-bottom:5px}.selected-point strong{font-size:17px;color:#173a32}.selected-point span{color:#557268;font-size:12px;margin-left:6px}.empty{background:#eaf3ec;border-radius:12px;padding:22px 18px;color:#416456;font-size:14px;line-height:1.5}.fineprint{color:#557268;font-size:12px;line-height:1.5;margin-top:14px}.line-card{background:white;border:1px solid #dce8df;border-radius:12px;padding:16px;margin:0 0 12px}.line-top{display:flex;align-items:flex-start;justify-content:space-between;gap:12px}.line-id{display:inline-block;background:#245b48;color:white;border-radius:7px;font-weight:700;font-size:14px;padding:5px 9px}.line-name{color:#557268;font-size:13px;margin-top:8px}.arrival{text-align:right;color:#173a32;white-space:nowrap}.arrival strong{font-size:24px;line-height:1}.arrival span{display:block;font-size:11px;color:#557268;margin-top:5px}.model-line{border-top:1px solid #e6eee7;margin-top:14px;padding-top:12px;color:#315f4e;font-size:13px}.scenarios{display:grid;grid-template-columns:1fr 1fr;gap:7px 16px;margin-top:12px}.scenario{display:flex;justify-content:space-between;gap:8px;color:#557268;font-size:12px}.scenario b{color:#173a32;font-variant-numeric:tabular-nums}.scenario.gps-failure,.scenario.gps-failure b,.gps-failure-label{color:#b42318}.section-divider{border-top:1px solid #dce8df;margin:24px 0 18px}.route-box{background:#eaf3ec;border-radius:12px;padding:16px;color:#244a3c}.route-box strong{color:#173a32}.route-box p{font-size:13px;color:#557268;margin:7px 0 0}div.stButton>button{background:#245b48 !important;color:#fff !important;border:1px solid #245b48 !important;border-radius:9px;min-height:44px;font-weight:700}div.stButton>button:hover{background:#173a32 !important;border-color:#173a32 !important}div.stButton>button:focus,div.stButton>button:active{background:#245b48 !important;color:#d3dad5 !important;border-color:#245b48 !important}div.stButton>button:focus p,div.stButton>button:active p{color:#d3dad5 !important}iframe{border:0}label{font-weight:600} @media(max-width:700px){.block-container{padding:1rem 1rem 2rem}h1{font-size:1.7rem}.topbar{margin-bottom:20px}.top-tag{font-size:10px}}
</style>''', unsafe_allow_html=True)
st.markdown('''<div class="topbar"><div class="brand"><span class="brand-icon"><svg width="19" height="19" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" aria-hidden="true"><rect x="5" y="3" width="14" height="16" rx="3"/><path d="M5 12h14M8 19v2m8-2v2M8 15h.01M16 15h.01"/></svg></span>RotaCerta IA</div><span class="top-tag">Demonstração fictícia</span></div><div class="intro"><h1>Encontre seu próximo ônibus</h1><p>Toque em um ponto para ver as linhas e as estimativas disponíveis.</p></div>''', unsafe_allow_html=True)

LABELS = {'normal':'Operação normal', 'atraso':'Possível atraso', 'falha_gps':'Possível falha de GPS', 'viagem_nao_realizada':'Possível viagem não realizada'}
# Entradas inventadas apenas para demonstrar o funcionamento dos modelos.
MINUTOS_ANTES_HORARIO_SIMULADO = 5
# Contexto ilustrativo por ponto: não é consulta a serviços de trânsito ou clima.
CONDICOES_SIMULADAS = {
    'P1': {'clima': 'Chuva leve', 'transito': 'Intenso'},
    'P2': {'clima': 'Chuva leve', 'transito': 'Moderado'},
    'P3': {'clima': 'Nublado, sem chuva', 'transito': 'Intenso'},
    'P4': {'clima': 'Nublado, sem chuva', 'transito': 'Moderado'},
    'P5': {'clima': 'Sem chuva', 'transito': 'Tranquilo'},
    'P6': {'clima': 'Sem chuva', 'transito': 'Tranquilo'},
}

@st.cache_resource
def modelos():
    if not Path('models/chegada.joblib').exists() or not Path('models/situacao.joblib').exists():
        treinar()
    return joblib.load('models/chegada.joblib'), joblib.load('models/situacao.joblib')

def consultar_ponto(ponto):
    agora = datetime.now(ZoneInfo('America/Sao_Paulo'))
    chegada, situacao = modelos()
    resultados = []
    for linha in [l for l, pontos in LINHAS.items() if ponto in pontos]:
        # Snapshot fictício: L1 e L3 sem sinal, demais com sinal recente.
        gps = int(linha in ('L2', 'L4'))
        entrada = dict(linha_id=linha, ponto_id=ponto, dia_semana=agora.weekday(), hora_consulta=agora.hour, min_desde_horario=-MINUTOS_ANTES_HORARIO_SIMULADO, gps_disponivel=gps, min_desde_ultimo_gps=2 if gps else 12, viagem_iniciada_confirmada=np.nan)
        x = pd.DataFrame([entrada], columns=FEATURES)
        prob = float(chegada.predict_proba(x)[0][list(chegada.classes_).index(1)])
        probs = dict(zip(situacao.classes_, situacao.predict_proba(x)[0]))
        resultados.append({'linha':linha, 'gps':gps, 'prob':prob, 'probs':probs, 'entrada':x.fillna('desconhecido').to_dict(orient='records')[0]})
    return resultados

st.markdown('<div class="section-head"><strong>Escolha um ponto</strong><span>Mapa fictício</span></div>', unsafe_allow_html=True)
ponto = mapa(selected=st.session_state.get('mapa'), key='mapa', default=None)
st.markdown('<p class="fineprint">Mapa ilustrativo. Não usamos sua localização e não há rastreamento de ônibus real.</p>', unsafe_allow_html=True)
st.markdown('<div id="analises-ponto" class="section-divider"></div><div class="panel-title">Ônibus neste ponto</div><p class="panel-copy">Selecione um marcador no mapa para ver as linhas.</p>', unsafe_allow_html=True)
if not ponto:
    st.markdown('<div class="empty"><strong>Selecione um ponto</strong><br>Toque em um dos marcadores no mapa para ver as linhas.</div>', unsafe_allow_html=True)
else:
    st.markdown(f'<div class="selected-point"><small>Ponto selecionado</small><strong>{NOMES[ponto]}</strong><span> {ponto}</span></div>', unsafe_allow_html=True)
    condicoes = CONDICOES_SIMULADAS[ponto]
    st.markdown(f'<div class="selected-point"><small>Condições fictícias para demonstração</small><strong>{condicoes["clima"]}</strong><span> · Trânsito {condicoes["transito"].lower()}</span></div>', unsafe_allow_html=True)
    st.caption('Clima, trânsito e sinais são simulados; não há dados em tempo real.')
    resultados = consultar_ponto(ponto)
    colunas = st.columns(2, gap='medium')
    for indice, r in enumerate(resultados):
        with colunas[indice % 2]:
            estado = max(r['probs'], key=r['probs'].get)
            cenarios = ''.join(f'<div class="scenario {"gps-failure" if k == "falha_gps" else ""}"><span>{LABELS[k]}</span><b>{r["probs"][k]:.0%}</b></div>' for k in LABELS)
            sinal = 'Sinal simulado disponível' if r['gps'] else 'Sinal simulado indisponível'
            classe_estado = 'gps-failure-label' if estado == 'falha_gps' else ''
            st.markdown(f'''<div class="line-card"><div class="line-top"><div><span class="line-id">{r['linha']}</span><div class="line-name">{sinal}</div></div></div><div class="model-line"><strong>{r['prob']:.0%}</strong> de chance de chegar em até 20 min<br>Situação mais provável: <strong class="{classe_estado}">{LABELS[estado]}</strong></div><div class="scenarios">{cenarios}</div></div>''', unsafe_allow_html=True)
            if st.button(f"Entender a análise da {r['linha']}", key=f"explicar-{ponto}-{r['linha']}", use_container_width=True):
                if not os.getenv('GEMINI_API_KEY'):
                    st.info('Configure GEMINI_API_KEY no arquivo .env para ativar a explicação.')
                else:
                    contexto = {'ponto_ficticio': NOMES[ponto], 'linha_ficticia': r['linha'], 'condicoes_ficticias': condicoes, 'gps_simulado_disponivel': bool(r['gps']), 'chance_chegada_20min': round(r['prob'], 3), 'situacoes': {k: round(float(v), 3) for k, v in r['probs'].items()}}
                    prompt = ('Você ajuda passageiros a interpretar uma demonstração acadêmica de transporte. '
                              'Com base exclusivamente nos dados fictícios abaixo, explique em português brasileiro, em até quatro frases curtas: '
                              'a chance de chegada em 20 minutos, o cenário operacional mais provável, as condições simuladas de clima e trânsito e a incerteza mais relevante. '
                              'Clima e trânsito são contexto ilustrativo: não são entradas dos modelos e não se conhece seu efeito nesta previsão. Não afirme que causaram atraso ou influenciaram as probabilidades. '
                              'Use linguagem simples e clara. Lembre que a ausência de sinal não confirma cancelamento e que dados fictícios não descrevem a operação real. '
                              'Não invente horários, minutos, distâncias, rotas, confirmações ou novos fatos; não recomende uma decisão como certa. '
                              'A probabilidade de chegada é de um modelo separado das probabilidades dos cenários. Dados: '
                              + json.dumps(contexto, ensure_ascii=False))
                    try:
                        with st.spinner('Preparando análise da linha. A resposta do modelo pode levar até alguns minutos…'):
                            resposta = explicar(os.environ['GEMINI_API_KEY'], os.getenv('GEMMA_MODEL', 'gemma-4-26b-a4b-it'), prompt)
                        st.write(resposta)
                    except GemmaError as erro:
                        st.error(str(erro))
    candidatas = [r for r in resultados if LINHAS[r['linha']][-1] != ponto]
    if candidatas:
        maior_risco = max(candidatas, key=lambda item: item['probs'].get('viagem_nao_realizada', 0))
        destino = LINHAS[maior_risco['linha']][-1]
        prob_nao_realizada = maior_risco['probs'].get('viagem_nao_realizada', 0)
        rota = alternativa(ponto, destino, maior_risco['linha'])
        st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)
        st.subheader('Alternativa de deslocamento')
        st.caption(f'Para a linha {maior_risco["linha"]}, com maior chance simulada de viagem não realizada neste ponto ({prob_nao_realizada:.0%}). O destino considerado é o ponto final da linha: {NOMES[destino]}.')
        if rota:
            trechos = ' → '.join(f"{t['linha']}: {NOMES[t['inicio']]} até {NOMES[t['fim']]}" for t in rota['trechos'])
            contexto_risco = 'Risco simulado elevado; isso não confirma cancelamento.' if prob_nao_realizada >= 0.40 else 'Opção de planejamento: o risco simulado está abaixo de 40%; não há confirmação de cancelamento.'
            st.markdown(f'<div class="route-box"><strong>Alternativa sugerida</strong><p>{trechos}</p><p>{contexto_risco}</p><p>Tempo fictício: {rota["tempo"]} min, incluindo esperas. Tarifas e integração não foram verificadas.</p></div>', unsafe_allow_html=True)
        else:
            st.markdown(f'<div class="route-box"><strong>Sem alternativa nesta simulação</strong><p>Não encontramos outra rota até {NOMES[destino]} com até uma conexão na rede fictícia.</p></div>', unsafe_allow_html=True)
    st.markdown('<p class="fineprint">Os cenários são probabilidades de um modelo; a chance de chegada vem de outro. Falta de GPS não confirma cancelamento. Não há previsão de minutos neste protótipo.</p>', unsafe_allow_html=True)
    st.caption('O Gemma explica os resultados simulados dos modelos locais. Apenas dados fictícios da linha escolhida são enviados ao Google ao clicar.')

st.markdown('<p class="fineprint">RotaCerta IA · Protótipo acadêmico · Não integrado ao MOCBUS</p>', unsafe_allow_html=True)
