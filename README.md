# RotaCerta IA

O RotaCerta IA é um protótipo acadêmico que busca ajudar passageiros a lidar com a incerteza sobre a chegada do ônibus. A proposta é complementar informações de aplicativos de transporte coletivo, como o MOCBUS, com estimativas e explicações quando o horário informado parece pouco confiável ou o sinal de GPS está indisponível.

A ideia parte de situações observadas por passageiros em Montes Claros (MG). **O protótipo não é oficial nem integrado ao MOCBUS:** a rede, o histórico, os horários, o GPS, o clima e o trânsito usados na demonstração são fictícios.

## Entendendo o problema

Imagine que você está no ponto e o aplicativo informa que o ônibus deve chegar em **5 minutos**. Você decide esperar porque acredita que ele está perto. Mas passam 5, 10 ou 15 minutos e o ônibus ainda não aparece. Além da frustração, você perde tempo que poderia ter usado para outra atividade e não sabe quanto tempo mais precisará esperar.

Existe também outra situação: às vezes uma viagem ou linha deixa de aparecer no aplicativo. Isso pode ocorrer por uma falha de GPS ou de comunicação, mas a ausência na tela, por si só, não esclarece o que aconteceu. O passageiro fica com perguntas como:

- O ônibus está em circulação, mas perdeu o sinal de localização?
- Ele está atrasado?
- A viagem não será realizada?
- Vale a pena continuar aguardando ou procurar outra opção?

Sem informações adicionais, a pessoa não consegue distinguir essas possibilidades com segurança. A ausência de GPS **não confirma que o ônibus está circulando nem que a viagem foi cancelada**.

## O que propomos

A proposta é usar um histórico de viagens e informações disponíveis no momento da consulta para estimar a chance de o ônibus chegar e mostrar situações operacionais possíveis. Em vez de apresentar uma conclusão definitiva quando não há sinal, o RotaCerta IA busca explicar **o grau de incerteza** e oferecer uma alternativa de deslocamento na rede simulada.

Em uma versão futura com dados reais e validação, a intenção seria ajudar a pessoa a decidir se continua esperando ou se procura outra opção. A precisão das estimativas ainda não foi comprovada: o protótipo atual demonstra a ideia com dados fictícios e não garante que o ônibus vá passar.

### Exemplo fictício

Uma passageira seleciona a **Praça Central (P1)**. A linha L1 aparece com sinal de GPS indisponível. O protótipo mostra uma chance estimada de chegada em até 20 minutos e as probabilidades de situações como atraso e falha de GPS. Esses valores são resultados da simulação, não confirmações sobre uma viagem real.

A passageira também pode pedir uma explicação ao Gemma. Além disso, o programa procura uma alternativa até o ponto final da linha com maior chance simulada de não ser realizada. Se houver caminho, pode mostrar, por exemplo, **L2 com conexão para L3**; se não houver, informa que não encontrou uma opção na rede fictícia. Não são verificadas tarifas ou regras reais de integração.

## Como funciona o protótipo

1. A pessoa seleciona um ponto fictício no mapa.
2. Os cards das linhas que passam pelo ponto mostram a chance estimada de chegada em até 20 minutos e as probabilidades de quatro cenários: operação normal, atraso, falha de GPS e viagem não realizada.
3. A pessoa pode pedir ao **Gemma** uma explicação em linguagem simples para uma linha.
4. Condições fictícias de clima e trânsito aparecem como contexto e podem ser mencionadas pelo Gemma.
5. O programa procura automaticamente uma alternativa direta ou com até uma conexão até o ponto final da linha com maior chance simulada de viagem não realizada. Abaixo de 40%, apresenta a rota como opção de planejamento; a partir de 40%, indica risco simulado elevado. Se não encontrar um caminho, informa essa limitação.

As probabilidades vêm de **dois modelos Random Forest treinados localmente com dados sintéticos**: um estima a chegada em até 20 minutos; o outro compara os quatro cenários operacionais. A probabilidade de chegada vem de um modelo separado e não deve ser somada às probabilidades dos cenários.

O Gemma não foi treinado com esse dataset e não calcula as probabilidades dos cards. Ele recebe os resultados e o contexto fictício para explicá-los. Clima e trânsito não são entradas dos modelos, e seu efeito na previsão não foi calculado.

O destino da alternativa é o **ponto final da linha original**, pois o aplicativo não pergunta onde a pessoa quer descer. O limiar de 40%, os tempos e as esperas são fictícios; risco estimado não confirma cancelamento. O protótipo não fornece uma previsão real de quantos minutos faltam para o ônibus chegar.

## Como rodar no Windows

### 1. Pré-requisitos

- Python 3.12 instalado, com `pip` e suporte a ambientes virtuais.
- Acesso à internet para instalar as dependências e, se quiser usar o Gemma, acessar a API do Google.
- Uma chave da API criada no [Google AI Studio](https://aistudio.google.com/apikey) para a explicação opcional.

### 2. Abra o PowerShell na pasta do projeto

```powershell
cd C:\Users\Sarah\Downloads\hackaton
```

### 3. Crie e ative o ambiente virtual

Se ainda não houver uma pasta `.venv`, execute:

```powershell
python -m venv .venv
```

Ative o ambiente:

```powershell
.\.venv\Scripts\Activate.ps1
```

Se o PowerShell impedir a ativação, você pode usar o Python do ambiente diretamente, como mostrado nos comandos abaixo, sem alterar a política de execução do computador.

### 4. Instale as dependências

```powershell
.\.venv\Scripts\python -m pip install -r requirements.txt
```

O ambiente já preparado nesta máquina pode reutilizar pacotes do Python instalado. Em outra máquina, prefira criar um ambiente virtual novo e instalar os pacotes com o comando acima.

### 5. Configure a chave do Google AI Studio

Se o arquivo `.env` ainda não existir, crie-o a partir do exemplo:

```powershell
Copy-Item .env.example .env
```

Abra o arquivo `.env` e preencha `GEMINI_API_KEY` com o **valor da chave**, não com o nome dado a ela no AI Studio. Não envie nem publique esse arquivo. `GEMMA_MODEL` define o modelo usado; o padrão do projeto é `gemma-4-26b-a4b-it`.

A chave é opcional: sem ela, a consulta e os modelos locais continuam funcionando. Apenas ao clicar em **Entender a análise** os dados fictícios daquela linha são enviados à API do Google. O Gemma 4 usa o nível de raciocínio `minimal` para essa explicação curta; a disponibilidade e o tempo de resposta dependem da API, da conta e da conexão.

### 6. Gere os dados e treine os modelos

```powershell
.\.venv\Scripts\python treinar.py
```

Esse comando gera `data/viagens_sinteticas.csv`, treina os dois modelos e salva os resultados em `models/`. A avaliação fica em `models/metricas.json`; os dias simulados de teste são separados dos dias de treino. Se os modelos não existirem, a aplicação também tenta gerá-los na primeira consulta.

### 7. Inicie o aplicativo

```powershell
.\.venv\Scripts\python -m streamlit run app.py
```

Abra o endereço local indicado no terminal, normalmente `http://localhost:8501`. Para encerrar, volte ao terminal e pressione **Ctrl+C**.

### 8. Faça uma demonstração

Clique em **Praça Central (P1)** no mapa. Os cards de L1 e L2 aparecem abaixo com as estimativas e cenários fictícios. Clique em **Entender a análise** para solicitar ao Gemma uma interpretação de uma das linhas.

## Arquivos principais

- `app.py`: interface, consulta e apresentação dos resultados.
- `mapa/index.html`: mapa fictício e seleção dos pontos.
- `gerar_dados.py`: geração do dataset sintético.
- `treinar.py`: treinamento e avaliação dos modelos.
- `gemma_api.py`: chamada à API do Google e tratamento de erros.
- `rotas.py`: definição das linhas e pontos fictícios utilizados pela interface.
- `.env.example`: exemplo de configuração sem chave.

## Limitações e próximos passos

Para testar a proposta em uma operação real, seria necessário obter e validar horários, históricos de passagem, sinais de GPS e registros operacionais independentes, além de avaliar a qualidade das previsões em períodos posteriores ao treino. A eventual integração com dados reais, fontes de clima e trânsito e o MOCBUS dependeria de disponibilidade e autorização apropriadas.
