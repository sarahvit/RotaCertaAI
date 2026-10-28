"""Gera observações inteiramente simuladas, com ruído e resultados posteriores."""
from pathlib import Path
import numpy as np
import pandas as pd

def gerar(n=5000, seed=42):
    rng = np.random.default_rng(seed)
    rows = []
    for i in range(n):
        dia = i % 90  # agrupamento temporal: observações do mesmo dia ficam juntas
        hora = int(rng.integers(5, 23))
        delta = int(rng.integers(-10, 31))
        estado = rng.choice(['normal', 'atraso', 'falha_gps', 'viagem_nao_realizada'], p=[.53, .24, .15, .08])
        gps = int(rng.random() < {'normal': .91, 'atraso': .78, 'falha_gps': .12, 'viagem_nao_realizada': .10}[estado])
        idade = int(rng.integers(0, 5) if gps else rng.integers(6, 50))
        # Evidência independente também pode não estar disponível.
        evidencia = rng.choice([0, 1, np.nan], p=([.65, .05, .30] if estado == 'viagem_nao_realizada' else [.03, .42, .55]))
        atraso = {'normal': 2, 'atraso': 18, 'falha_gps': 7, 'viagem_nao_realizada': 70}[estado] + rng.normal(0, 9)
        chegou = int(atraso - delta <= 20 and estado != 'viagem_nao_realizada')
        rows.append(dict(dia_simulado=dia, linha_id=rng.choice(['L1','L2','L3','L4']), ponto_id=rng.choice(['P1','P2','P3','P4','P5','P6']), dia_semana=dia % 7, hora_consulta=hora, min_desde_horario=delta, gps_disponivel=gps, min_desde_ultimo_gps=idade, viagem_iniciada_confirmada=evidencia, chegou_20min=chegou, situacao_real=estado))
    return pd.DataFrame(rows)

if __name__ == '__main__':
    Path('data').mkdir(exist_ok=True)
    gerar().to_csv('data/viagens_sinteticas.csv', index=False)
    print('Dataset fictício salvo em data/viagens_sinteticas.csv')
