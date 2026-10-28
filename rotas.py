"""Rede fictícia, com tempo de espera por embarque e até uma conexão."""
import networkx as nx

LINHAS = {'L1': ['P1','P2','P4'], 'L2': ['P1','P3','P5'], 'L3': ['P3','P4','P6'], 'L4': ['P2','P4','P5','P6']}
NOMES = {'P1':'Praça Central', 'P2':'Mercado', 'P3':'Terminal Norte', 'P4':'Universidade', 'P5':'Hospital', 'P6':'Parque'}

def alternativa(origem, destino, linha_atual):
    graph = nx.DiGraph()
    for linha, pontos in LINHAS.items():
        if linha == linha_atual:
            continue
        for a, b in zip(pontos, pontos[1:]):
            graph.add_edge((linha, a), (linha, b), weight=6)
        for ponto in pontos:
            graph.add_edge(('origem', ponto), (linha, ponto), weight=5)
            graph.add_edge((linha, ponto), ('destino', ponto), weight=0)
    for ponto in NOMES:
        linhas = [l for l, ps in LINHAS.items() if ponto in ps and l != linha_atual]
        for a in linhas:
            for b in linhas:
                if a != b:
                    graph.add_edge((a, ponto), (b, ponto), weight=8)
    source, target = ('origem', origem), ('destino', destino)
    if source not in graph or target not in graph:
        return None
    # Enumerar caminhos simples nesta rede pequena permite limitar a uma conexão.
    candidates = []
    for path in nx.all_simple_paths(graph, source, target, cutoff=9):
        linhas = [n[0] for n in path[1:-1]]
        trocas = sum(a != b for a, b in zip(linhas, linhas[1:]))
        percorridas = {a[0] for a, b in zip(path[1:-1], path[2:-1]) if a[0] == b[0] and a[1] != b[1]}
        if trocas <= 1 and set(linhas) <= percorridas:
            candidates.append((nx.path_weight(graph, path, 'weight'), path))
    if not candidates:
        return None
    tempo, path = min(candidates, key=lambda x: x[0])
    trechos = []
    for linha, ponto in path[1:-1]:
        if not trechos or trechos[-1]['linha'] != linha:
            trechos.append({'linha': linha, 'inicio': ponto, 'fim': ponto})
        else:
            trechos[-1]['fim'] = ponto
    return {'tempo': tempo, 'trechos': trechos}
