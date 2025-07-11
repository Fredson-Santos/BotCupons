# 🤖 Bot Cupons Telegram

Bot automatizado que monitora múltiplos canais de cupons no Telegram e reencaminha mensagens para um canal de destino, substituindo links de afiliado da Shopee pelos seus próprios links.

## ✨ Funcionalidades

- 🔍 **Monitoramento múltiplo** de canais de origem
- 🔗 **Conversão automática** de links Shopee para seus links de afiliado
- 📝 **Substituição de palavras** específicas nas mensagens
- ��️ **Suporte a mídia** (fotos, documentos, webpages)
- 🔎 **Filtro por palavras-chave** opcional
- ⚡ **Expansão de shortlinks** Shopee antes da conversão

## �� Instalação

### 1. Clone o repositório
```bash
git clone https://github.com/seu-usuario/bot-cupons.git
cd bot-cupons
```

### 2. Instale as dependências
```bash
pip install -r requirements.txt
```

### 3. Configure as credenciais
```bash
python configurar_bot.py
```

## 🔧 Configuração

### Credenciais necessárias:

1. **API ID e API HASH do Telegram**
   - Acesse: https://my.telegram.org
   - Faça login com sua conta pessoal
   - Vá em "API development tools"
   - Crie um novo app e copie as credenciais

2. **Credenciais da Shopee**
   - Acesse: https://open-api.affiliate.shopee.com.br/
   - Faça login com sua conta de afiliado
   - Vá em "Minhas Aplicações"
   - Copie o App ID e Secret

### Arquivo .env
```env
API_ID=12345678
API_HASH=abcdef1234567890abcdef1234567890
CANAL_ORIGEM=@canal1,@canal2,@canal3
CANAL_DESTINO=@meu_canal_destino
SHOPEE_APP_ID=seu_app_id
SHOPEE_SECRET=seu_secret
PALAVRAS_CHAVE=cupom,oferta,shopee
SUBSTITUICOES=@exemplo:@meu_usuario,#cupom:#oferta
```

## 🏃‍♂️ Como usar

### Execução manual
```bash
python bot_cupons.py
```

### Execução em background (Linux/Mac)
```bash
nohup python bot_cupons.py > bot.log 2>&1 &
```

### Testes
```bash
python teste_conexao.py
```

## 📁 Estrutura do projeto 