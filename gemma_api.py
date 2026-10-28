"""Chamada à Gemini API usando a biblioteca padrão e sem expor a chave."""
import json
import re
import socket
import ssl
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


class GemmaError(Exception):
    pass


def diagnostico_rede(error):
    """Descreve apenas o tipo e código do erro, sem incluir URL, chave ou prompt."""
    reason = error.reason if isinstance(error, URLError) else error
    if isinstance(reason, socket.gaierror):
        return 'Não foi possível localizar o servidor do Google (falha de DNS). Confira a conexão de rede.'
    if isinstance(reason, ssl.SSLCertVerificationError):
        return 'Não foi possível verificar o certificado do Google. Confira a data e hora do computador e possíveis inspeções HTTPS na rede.'
    if isinstance(reason, ssl.SSLError):
        return 'A conexão segura com o Google falhou. Confira possíveis bloqueios de VPN, proxy ou antivírus.'
    if isinstance(reason, (socket.timeout, TimeoutError)):
        return 'A conexão com a API do Google esgotou o tempo limite. Confira se a rede permite conexões HTTPS na porta 443.'
    code = getattr(reason, 'winerror', None) or getattr(reason, 'errno', None)
    if isinstance(code, int):
        return f'A conexão com a API do Google falhou (código de rede {code}). Confira se a rede permite conexões HTTPS na porta 443.'
    return 'A conexão com a API do Google falhou. Confira se a rede permite conexões HTTPS na porta 443.'


def explicar(api_key, model, prompt):
    if not re.fullmatch(r'[a-zA-Z0-9._-]+', model):
        raise GemmaError('O nome do modelo no .env é inválido. Confira GEMMA_MODEL.')
    body = {'contents': [{'parts': [{'text': prompt}]}]}
    if model.startswith('gemma-4-'):
        # Esta explicação curta não precisa de raciocínio interno prolongado.
        body['generationConfig'] = {'thinkingConfig': {'thinkingLevel': 'minimal'}}
    payload = json.dumps(body).encode('utf-8')
    request = Request(
        f'https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent',
        data=payload,
        headers={'Content-Type': 'application/json', 'x-goog-api-key': api_key},
        method='POST',
    )
    try:
        # A resposta pode demorar mais que uma consulta HTTP simples, sobretudo
        # na primeira geração. O timeout limita operações de conexão/leitura.
        with urlopen(request, timeout=120) as response:
            data = json.load(response)
    except HTTPError as error:
        if error.code in (400, 401, 403):
            raise GemmaError('A API recusou a solicitação. Confira a chave, as permissões do projeto e o acesso ao modelo no Google AI Studio.') from None
        if error.code == 404:
            raise GemmaError('Modelo indisponível para esta API ou conta. Confira GEMMA_MODEL no .env.') from None
        if error.code == 429:
            raise GemmaError('A cota ou o limite de requisições da API foi atingido. Aguarde e confira a cota no Google AI Studio.') from None
        raise GemmaError(f'O serviço do Google retornou um erro HTTP {error.code}. Tente novamente.') from None
    except (URLError, TimeoutError, OSError) as error:
        raise GemmaError(diagnostico_rede(error)) from None
    except (ValueError, UnicodeDecodeError):
        raise GemmaError('A API retornou uma resposta que não pôde ser lida. Tente novamente.') from None

    parts = [part.get('text', '') for candidate in data.get('candidates', []) for part in candidate.get('content', {}).get('parts', []) if not part.get('thought')]
    text = '\n'.join(part for part in parts if part).strip()
    if not text:
        raise GemmaError('A API não retornou uma explicação. Tente novamente ou confira o acesso ao modelo.')
    return text
