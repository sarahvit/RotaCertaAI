"""Treina os modelos e avalia em dias simulados posteriores."""
from pathlib import Path
import json
import joblib
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report, confusion_matrix, brier_score_loss
from gerar_dados import gerar

FEATURES = ['linha_id','ponto_id','dia_semana','hora_consulta','min_desde_horario','gps_disponivel','min_desde_ultimo_gps','viagem_iniciada_confirmada']

def pipeline():
    cat = ['linha_id', 'ponto_id']
    num = [x for x in FEATURES if x not in cat]
    prep = ColumnTransformer([('cat', OneHotEncoder(handle_unknown='ignore'), cat), ('num', SimpleImputer(strategy='median', add_indicator=True), num)])
    return Pipeline([('prep', prep), ('model', RandomForestClassifier(n_estimators=100, min_samples_leaf=5, random_state=42, n_jobs=-1))])

def treinar():
    Path('data').mkdir(exist_ok=True)
    Path('models').mkdir(exist_ok=True)
    df = gerar()
    df.to_csv('data/viagens_sinteticas.csv', index=False)
    train, test = df[df.dia_simulado < 72], df[df.dia_simulado >= 72]
    metrics = {'treino': len(train), 'teste': len(test), 'separacao': 'dias simulados 0–71 / 72–89'}
    for target, name in [('chegou_20min','chegada'), ('situacao_real','situacao')]:
        model = pipeline().fit(train[FEATURES], train[target])
        pred = model.predict(test[FEATURES])
        labels = model.classes_.tolist()
        result = {'classes': labels, 'matriz_confusao': confusion_matrix(test[target], pred, labels=labels).tolist(), 'relatorio': classification_report(test[target], pred, output_dict=True, zero_division=0)}
        if name == 'chegada':
            prob = model.predict_proba(test[FEATURES])[:, list(model.classes_).index(1)]
            result['brier'] = brier_score_loss(test[target], prob)
            # Referência simples: chegada esperada se o horário programado estiver a até 20 minutos.
            baseline = (test.min_desde_horario >= -20).astype(int)
            result['baseline_acuracia'] = float((baseline == test[target]).mean())
        metrics[name] = result
        joblib.dump(model, f'models/{name}.joblib')
    Path('models/metricas.json').write_text(json.dumps(metrics, indent=2, ensure_ascii=False), encoding='utf-8')
    return metrics

if __name__ == '__main__':
    print(json.dumps(treinar(), ensure_ascii=False, indent=2))
