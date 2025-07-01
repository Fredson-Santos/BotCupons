#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script interativo para configurar o Bot de Cupons Telegram
"""

import os
from pathlib import Path

def criar_arquivo_env():
    """Cria o arquivo .env com as configurações do usuário"""
    print("🤖 CONFIGURAÇÃO DO BOT CUPONS TELEGRAM")
    print("=" * 50)
    print("Este script vai ajudar você a configurar o bot de encaminhamento de cupons.")
    print("Você precisará das seguintes informações:")
    print("")
    print("📋 INFORMAÇÕES NECESSÁRIAS:")
    print("• API ID e API HASH do Telegram (https://my.telegram.org)")
    print("• Nome ou ID dos canais de origem (separados por vírgula)")
    print("• Nome ou ID do canal de destino (para onde as mensagens serão encaminhadas)")
    print("• SHOPEE APP ID e SHOPEE SECRET (https://open-api.affiliate.shopee.com.br/)")
    print("")

    # Verificar se já existe arquivo .env
    if os.path.exists('.env'):
        resposta = input("⚠️ Arquivo .env já existe. Deseja sobrescrever? (s/n): ")
        if resposta.lower() != 's':
            print("❌ Configuração cancelada.")
            return False

    print("🔧 Vamos configurar suas credenciais:")
    print("")

    api_id = input("🔑 API ID: ").strip()
    api_hash = input("🔐 API HASH: ").strip()
    canais_origem = input("📥 CANAIS ORIGEM (separados por vírgula, ex: @canal1,@canal2): ").strip()
    canal_destino = input("📤 CANAL DESTINO (@nome_canal ou ID): ").strip()
    shopee_app_id = input("🛒 SHOPEE APP ID: ").strip()
    shopee_secret = input("🛡️ SHOPEE SECRET: ").strip()

    # Configuração opcional
    print("")
    print("⚙️ Configuração opcional:")
    palavras_chave = input("🔎 Palavras-chave para filtrar mensagens (separadas por vírgula, opcional): ").strip()
    substituicoes = input("🔄 Substituições (formato: palavra_original:nova_palavra, separadas por vírgula, opcional): ").strip()

    conteudo = f"""# ========================================
# CONFIGURAÇÕES DO BOT CUPONS TELEGRAM
# ========================================

API_ID={api_id}
API_HASH={api_hash}
CANAL_ORIGEM={canais_origem}
CANAL_DESTINO={canal_destino}
SHOPEE_APP_ID={shopee_app_id}
SHOPEE_SECRET={shopee_secret}
PALAVRAS_CHAVE={palavras_chave}
SUBSTITUICOES={substituicoes}
"""

    try:
        with open('.env', 'w', encoding='utf-8') as f:
            f.write(conteudo)
        print("")
        print("✅ Arquivo .env criado com sucesso!")
        print("")
        print("📋 PRÓXIMOS PASSOS:")
        print("1. Execute: python bot_cupons.py")
        print("2. O bot irá encaminhar mensagens dos canais de origem para o canal de destino, substituindo links de afiliado.")
        return True
    except Exception as e:
        print(f"❌ Erro ao criar arquivo .env: {e}")
        return False

def mostrar_ajuda():
    """Mostra informações de ajuda para obter as credenciais"""
    print("")
    print("📖 GUIA PARA OBTER CREDENCIAIS")
    print("=" * 50)
    print("")
    print("🔑 API ID e API HASH:")
    print("1. Acesse: https://my.telegram.org")
    print("2. Faça login com seu número de telefone")
    print("3. Vá em 'API development tools'")
    print("4. Crie um novo app e copie o API ID e API HASH")
    print("")
    print("📥 CANAIS ORIGEM e 📤 CANAL DESTINO:")
    print("• Para canais públicos: use @nome_do_canal")
    print("• Para canais privados: use o ID numérico (ex: -1001234567890)")
    print("• Múltiplos canais de origem: separe por vírgula (ex: @canal1,@canal2,@canal3)")
    print("• Apenas um canal de destino é permitido")
    print("")
    print("🛒 SHOPEE APP ID e 🛡️ SHOPEE SECRET:")
    print("1. Acesse: https://open-api.affiliate.shopee.com.br/")
    print("2. Faça login com sua conta de afiliado")
    print("3. Vá em 'Minhas Aplicações' e crie/veja seu App")
    print("4. Copie o App ID e o Secret gerados")
    print("")
    print("🔎 PALAVRAS-CHAVE:")
    print("• Se quiser filtrar mensagens, informe palavras separadas por vírgula (ex: Shopee, cupom, oferta)")
    print("• Deixe em branco para encaminhar todas as mensagens.")
    print("")
    print("🔄 SUBSTITUIÇÕES:")
    print("• Formato: palavra_original:nova_palavra")
    print("• Múltiplas substituições: separe por vírgula")
    print("• Exemplos:")
    print("  - @exemplo:@meu_usuario")
    print("  - #cupom:#oferta")
    print("  - promoção:oferta")
    print("• Deixe em branco para não fazer substituições")
    print("")
    print("💡 DICAS:")
    print("• Mantenha suas credenciais seguras")
    print("• Nunca compartilhe o arquivo .env")
    print("• O arquivo .env já está no .gitignore para segurança")
    print("• O bot monitora todos os canais de origem simultaneamente")

def main():
    print("🚀 ASSISTENTE DE CONFIGURAÇÃO BOT CUPONS")
    print("=" * 50)
    while True:
        print("")
        print("Escolha uma opção:")
        print("1. 🔧 Configurar credenciais")
        print("2. 📖 Ver guia de credenciais")
        print("3. 🧪 Executar testes de conexão")
        print("4. 🚪 Sair")
        opcao = input("\nDigite sua escolha (1-4): ").strip()
        if opcao == "1":
            criar_arquivo_env()
        elif opcao == "2":
            mostrar_ajuda()
        elif opcao == "3":
            if os.path.exists('.env'):
                print("")
                print("🧪 Executando testes de conexão...")
                script_dir = os.path.dirname(os.path.abspath(__file__))
                teste_path = os.path.join(script_dir, 'teste_conexao.py')
                os.system(f'python "{teste_path}"')
            else:
                print("❌ Arquivo .env não encontrado. Configure as credenciais primeiro.")
        elif opcao == "4":
            print("👋 Até logo!")
            break
        else:
            print("❌ Opção inválida. Tente novamente.")

if __name__ == "__main__":
    main() 