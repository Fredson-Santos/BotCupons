#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de teste para verificar conexões com APIs
"""

import os
import asyncio
from telethon import TelegramClient
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
            if data.get("errors"): 
                print(f"❌ Erro GraphQL: {data['errors']}")
                return None
            link = data.get("data", {}).get("generateShortLink", {}).get("shortLink")
            if link: return link
            print("❌ Link não encontrado na resposta.")
            return None
        except requests.exceptions.RequestException as e: 
            print(f"❌ Falha na requisição: {e}")
            return None
        except json.JSONDecodeError as e: 
            print(f"❌ Falha ao analisar JSON: {e}")
            return None
        except Exception as e: 
            print(f"❌ Erro inesperado: {e}")
            return None

class Configuracao:
    def __init__(self):
        api_id_raw = os.getenv('API_ID')
        api_hash_raw = os.getenv('API_HASH')
        if not api_id_raw or not api_hash_raw:
            raise ValueError('API_ID e API_HASH devem estar definidos no .env!')
        self.api_id = int(api_id_raw)
        self.api_hash = str(api_hash_raw)
        canais_origem_raw = os.getenv('CANAL_ORIGEM', '')
        self.canais_origem = [c.strip() for c in canais_origem_raw.split(',') if c.strip()]
        self.canal_destino = str(os.getenv('CANAL_DESTINO'))
        self.shopee_app_id = os.getenv('SHOPEE_APP_ID')
        self.shopee_secret = os.getenv('SHOPEE_SECRET')
        if not all([self.api_id, self.api_hash, self.canais_origem, self.canal_destino, self.shopee_app_id, self.shopee_secret]):
            raise ValueError('Todas as variáveis obrigatórias devem estar definidas no .env!')

async def testar_telegram(config: Configuracao):
    """Testa a conexão com o Telegram"""
    print("🔍 Testando conexão com Telegram...")
    try:
        client = TelegramClient('teste_session', config.api_id, config.api_hash)
        await client.start()
        
        # Testa se consegue obter informações do próprio usuário
        me = await client.get_me()
        print(f"✅ Telegram OK - Conectado como: {me.first_name} (@{me.username})")
        
        # Testa acesso aos canais
        print(f"📥 Canais de origem configurados: {config.canais_origem}")
        for canal in config.canais_origem:
            try:
                entity = await client.get_entity(canal)
                print(f"✅ Canal de origem '{canal}' acessível")
            except Exception as e:
                print(f"❌ Erro ao acessar canal '{canal}': {e}")
        
        # Testa acesso ao canal de destino
        try:
            entity = await client.get_entity(config.canal_destino)
            print(f"✅ Canal de destino '{config.canal_destino}' acessível")
        except Exception as e:
            print(f"❌ Erro ao acessar canal de destino '{config.canal_destino}': {e}")
        
        await client.disconnect()
        return True
    except Exception as e:
        print(f"❌ Falha na conexão com Telegram: {e}")
        return False

def testar_shopee(config: Configuracao):
    """Testa a conexão com a API da Shopee"""
    print("\n🔍 Testando conexão com API da Shopee...")
    try:
        shopee_api = ShopeeAPI(config.shopee_app_id, config.shopee_secret)
        
        # URL de teste (produto fictício da Shopee)
        url_teste = "https://shopee.com.br/produto-teste-123"
        print(f"🧪 Testando conversão de link: {url_teste}")
        
        link_convertido = shopee_api.gen_link(url_teste)
        if link_convertido:
            print(f"✅ Shopee API OK - Link convertido: {link_convertido}")
            return True
        else:
            print("❌ Falha ao converter link de teste")
            return False
    except Exception as e:
        print(f"❌ Falha na conexão com Shopee API: {e}")
        return False

def main():
    print("🧪 TESTE DE CONEXÕES - BOT CUPONS")
    print("=" * 50)
    
    try:
        config = Configuracao()
        print("✅ Configuração carregada com sucesso")
        
        # Testa Telegram
        telegram_ok = asyncio.run(testar_telegram(config))
        
        # Testa Shopee
        shopee_ok = testar_shopee(config)
        
        print("\n" + "=" * 50)
        print("📊 RESULTADO DOS TESTES:")
        print(f"Telegram: {'✅ OK' if telegram_ok else '❌ FALHOU'}")
        print(f"Shopee API: {'✅ OK' if shopee_ok else '❌ FALHOU'}")
        
        if telegram_ok and shopee_ok:
            print("\n🎉 Todos os testes passaram! O bot está pronto para uso.")
            print("💡 Execute: python bot_cupons.py")
        else:
            print("\n⚠️ Alguns testes falharam. Verifique as configurações no .env")
            
    except Exception as e:
        print(f"❌ Erro durante os testes: {e}")

if __name__ == "__main__":
    main() 