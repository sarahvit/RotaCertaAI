# RotaCerta IA

O RotaCerta IA é um protótipo acadêmico que propõe complementar as informações de transporte coletivo apresentadas por aplicativos como o MOCBUS. A ideia surgiu a partir de situações observadas por passageiros em Montes Claros (MG): a previsão de chegada pode não corresponder ao tempo real de espera, e uma falha no sinal de GPS pode fazer com que uma linha ou viagem deixe de aparecer causando dúvida ao passageiro se deve continuar esperando ainda o onibus ou não.

Pela falta de datasets disponíveis, o projeto **não usa dados reais da operação**. Linhas, pontos, sinais, clima, trânsito e histórico usados na demonstração são fictícios.

## Qual problema queremos resolver?

Ao consultar o aplicativo, uma pessoa pode ver que um ônibus está próximo e organizar sua rotina com base nessa informação. Se o tempo exibido não for fiel, ela pode acabar esperando mais de cinco minutos além do esperado — tempo que poderia usar para realizar outra atividade. A espera fica ainda mais difícil de planejar quando o aplicativo deixa de apresentar uma linha ou viagem por falta de sinal.

A ausência da linha na tela pode gerar uma dúvida: o ônibus deixou de circular ou apenas perdeu a comunicação do GPS? A proposta do RotaCerta IA é **reduzir essa incerteza**, apresentando uma estimativa baseada em histórico e indicando situações possíveis. Assim, o passageiro pode tomar uma decisão mais informada sobre esperar ou buscar outra informação.

**Uma falha de GPS não confirma que o ônibus está circulando, assim como a falta de sinal não confirma o cancelamento.** O protótipo apresenta probabilidades, não uma garantia de que o ônibus passará. Para afirmar o que aconteceu numa viagem real, seriam necessários dados confiáveis e independentes do GPS.

## Como funciona o protótipo

1. A pessoa seleciona um ponto fictício no mapa.
2. Os cards das linhas que passam pelo ponto mostram a chance estimada de chegada em até 20 minutos e as probabilidades de quatro cenários: operação normal, atraso, falha de GPS e viagem não realizada.
3. O passageiro pode pedir ao **Gemma** uma explicação, em linguagem simples, para a linha escolhida.
4. Condições fictícias de clima e trânsito aparecem como contexto da demonstração e podem ser mencionadas pelo Gemma.

As probabilidades são calculadas por **dois modelos Random Forest treinados localmente com um dataset sintético**: um para a chegada e outro para a situação da viagem. O Gemma não foi treinado com esse dataset; ele explica os resultados e o contexto fictício enviados a ele. Clima e trânsito não são entradas dos modelos e não foi calculado seu efeito sobre as estimativas.

O mapa é ilustrativo: não utiliza a localização do passageiro, ruas reais ou GPS de ônibus. O aplicativo não informa uma previsão real de quantos minutos faltam para a chegada. O desempenho medido em dados simulados não demonstra precisão em Montes Claros.

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
