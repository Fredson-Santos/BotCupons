import os
import re
import asyncio
from telethon import TelegramClient, events
from dotenv import load_dotenv
import requests
import json
import hashlib
import time
from typing import Dict, Optional

# Carregar variáveis do .env
load_dotenv()

class ShopeeAPI:
    def __init__(self, app_id: str, secret: str):
        self.app_id = app_id
        self.secret = secret
        self.base_url = "https://open-api.affiliate.shopee.com.br"
        self.endpoint = "/graphql"
    def _gen_sig(self, payload: str) -> tuple[str, str]:
        ts = str(int(time.time()))
        msg = f"{self.app_id}{ts}{payload}{self.secret}"
        sig = hashlib.sha256(msg.encode('utf-8')).hexdigest()
        return sig, ts
    def _auth_header(self, payload: str) -> Dict[str, str]:
        sig, ts = self._gen_sig(payload)
        auth_h = f"SHA256 Credential={self.app_id}, Timestamp={ts}, Signature={sig}"
        return {"Authorization": auth_h, "Content-Type": "application/json"}
    def gen_link(self, url: str, sub_ids: Optional[list[str]] = None) -> Optional[str]:
        if sub_ids is None: sub_ids = ["s1", "s2", "s3", "s4", "s5"]
        gq = {"query": f'''mutation {{ generateShortLink(input: {{ originUrl: \"{url}\", subIds: {json.dumps(sub_ids)} }}) {{ shortLink }} }}'''}
        p = json.dumps(gq)
        h = self._auth_header(p)
        try:
            resp = requests.post(url=f"{self.base_url}{self.endpoint}", headers=h, json=gq, timeout=30)
            resp.raise_for_status()
            data = resp.json()
            if data.get("errors"): print(f"Erro GraphQL: {data['errors']}"); return None
            link = data.get("data", {}).get("generateShortLink", {}).get("shortLink")
            if link: return link
            print("Link não encontrado na resposta.")
            print(f"Resposta: {data}")
            return None
        except requests.exceptions.RequestException as e: print(f"Falha na requisição: {e}"); return None
        except json.JSONDecodeError as e: print(f"Falha ao analisar JSON: {e}"); return None
        except Exception as e: print(f"Erro inesperado: {e}"); return None

def expandir_shortlink(link: str) -> str:
    """Expande um shortlink Shopee para o link de produto real."""
    try:
        resp = requests.get(link, allow_redirects=True, timeout=10)
        final_url = resp.url
        print(f"[INFO] Shortlink expandido: {link} -> {final_url}")
        return final_url
    except Exception as e:
        print(f"[ERRO] Falha ao expandir shortlink {link}: {e}")
        return link

def is_shopee_url(url: str) -> bool:
    domains = ["shopee.com", "shopee.co.id", "shopee.com.my", "shopee.com.sg", 
               "shopee.com.ph", "shopee.co.th", "shopee.vn", "shopee.com.tw", "shopee.com.br"]
    return any(d in url.lower() for d in domains)

def substituir_palavras_especificas(texto: str, substituicoes: dict) -> str:
    """Substitui palavras específicas no texto"""
    if not substituicoes:
        return texto
    
    texto_modificado = texto
    for palavra_original, palavra_nova in substituicoes.items():
        # Substitui a palavra exata (case insensitive)
        pattern = re.compile(re.escape(palavra_original), re.IGNORECASE)
        texto_modificado = pattern.sub(palavra_nova, texto_modificado)
        print(f"[INFO] Substituído: '{palavra_original}' -> '{palavra_nova}'")
    
    return texto_modificado

class Configuracao:
    def __init__(self):
        api_id_raw = os.getenv('API_ID')
        api_hash_raw = os.getenv('API_HASH')
        if not api_id_raw or not api_hash_raw:
            raise ValueError('API_ID e API_HASH devem estar definidos no .env!')
        self.api_id = int(api_id_raw)
        self.api_hash = str(api_hash_raw)
        # Lista de canais de origem (separados por vírgula)
        canais_origem_raw = os.getenv('CANAL_ORIGEM', '')
        self.canais_origem = [c.strip() for c in canais_origem_raw.split(',') if c.strip()]
        self.canal_destino = str(os.getenv('CANAL_DESTINO'))
        self.shopee_app_id = os.getenv('SHOPEE_APP_ID')
        self.shopee_secret = os.getenv('SHOPEE_SECRET')
        self.palavras_chave = [p.strip().lower() for p in os.getenv('PALAVRAS_CHAVE', '').split(',') if p.strip()]
        # Lista de palavras bloqueadas (mensagens com essas palavras não serão enviadas)
        self.palavras_bloqueadas = [p.strip().lower() for p in os.getenv('PALAVRAS_BLOQUEADAS', '').split(',') if p.strip()]
        # Mapeamento de palavras para substituir (formato: palavra_original:nova_palavra)
        substituicoes_raw = os.getenv('SUBSTITUICOES', '')
        self.substituicoes = {}
        if substituicoes_raw:
            for item in substituicoes_raw.split(','):
                if ':' in item:
                    original, nova = item.split(':', 1)
                    self.substituicoes[original.strip()] = nova.strip()
        if not all([self.api_id, self.api_hash, self.canais_origem, self.canal_destino, self.shopee_app_id, self.shopee_secret]):
            raise ValueError('Todas as variáveis obrigatórias devem estar definidas no .env!')
        if not self.canais_origem:
            raise ValueError('Pelo menos um CANAL_ORIGEM deve estar definido no .env!')

config = Configuracao()
if not config.shopee_app_id or not config.shopee_secret:
    raise ValueError('SHOPEE_APP_ID e SHOPEE_SECRET devem estar definidos no .env!')
shopee_api = ShopeeAPI(config.shopee_app_id, config.shopee_secret)

REGEX_SHOPEE = r'https?://(?:s\.)?shopee\.com(?:\.br)?/[^\s\)\]\"]+'

client = TelegramClient('session_cupons', config.api_id, config.api_hash)

async def substituir_links_shopee(texto):
    links = re.findall(REGEX_SHOPEE, texto)
    if links:
        print(f"[INFO] Link(s) Shopee original(is) encontrado(s): {links}")
    for link in links:
        # Se for shortlink, expanda antes de converter
        if 's.shopee.com.br' in link:
            link_expandido = expandir_shortlink(link)
            url_para_converter = link_expandido
        else:
            url_para_converter = link
        if is_shopee_url(url_para_converter):
            novo_link = shopee_api.gen_link(url_para_converter)
            if novo_link:
                print(f"[OK] Link convertido: {novo_link}")
                texto = texto.replace(link, novo_link)
            else:
                print(f"[ERRO] Falha ao converter o link: {url_para_converter}")
        else:
            print(f"[ERRO] URL não reconhecida como Shopee: {url_para_converter}")
    return texto

@client.on(events.NewMessage(chats=config.canais_origem))
async def handler(event):
    mensagem = event.message
    texto = mensagem.text or mensagem.message or ''
    
    # Verificar se a mensagem contém links Shopee
    links_shopee = re.findall(REGEX_SHOPEE, texto)
    if not links_shopee:
        print(f"[IGNORADO] Mensagem sem links Shopee: {texto[:50]}...")
        return
    
    # Verificar palavras-chave (se configuradas)
    if config.palavras_chave:
        if not any(p in texto.lower() for p in config.palavras_chave):
            return
    
    # Verificar palavras bloqueadas
    if config.palavras_bloqueadas:
        if any(p in texto.lower() for p in config.palavras_bloqueadas):
            print(f"[BLOQUEADO] Mensagem bloqueada por conter palavra proibida: {texto[:50]}...")
            return
    
    # Substituir links Shopee
    texto_modificado = await substituir_links_shopee(texto)
    # Substituir palavras específicas
    texto_modificado = substituir_palavras_especificas(texto_modificado, config.substituicoes)
    if mensagem.media:
        await client.send_file(config.canal_destino, mensagem.media, caption=texto_modificado)
        print(f"[OK] Mensagem com mídia encaminhada para {config.canal_destino}")
    else:
        await client.send_message(config.canal_destino, texto_modificado)
        print(f"[OK] Mensagem de texto encaminhada para {config.canal_destino}")

if __name__ == '__main__':
    print("Bot de Cupons iniciado. Monitorando mensagens...")
    print(f"Canais de origem: {config.canais_origem}")
    print(f"Canal de destino: {config.canal_destino}")
    print("🔗 Apenas mensagens com links Shopee serão processadas")
    if config.palavras_chave:
        print(f"Palavras-chave filtradas: {config.palavras_chave}")
    if config.palavras_bloqueadas:
        print(f"Palavras bloqueadas: {config.palavras_bloqueadas}")
    if config.substituicoes:
        print(f"Substituições configuradas: {config.substituicoes}")
    with client:
        client.run_until_disconnected() 
