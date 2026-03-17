import os
import logging
import asyncio
from typing import Final
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
import agente

# Carregar variáveis de ambiente
load_dotenv()

# Limite do Telegram
MAX_MESSAGE_LENGTH: Final = 4000

TOKEN: Final = os.getenv("TELEGRAM")
if not TOKEN:
    # Tenta carregar do diretório .llm
    load_dotenv("../.llm/.env")
    TOKEN = os.getenv("TELEGRAM")

# Configurar Logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

def salvar_chat_id(chat_id):
    """Salva o Chat ID no arquivo .env se ainda não existir."""
    env_path = ".env"
    chat_id_str = str(chat_id)
    
    # Se o arquivo não existir, cria um básico
    if not os.path.exists(env_path):
        with open(env_path, "w") as f:
            f.write(f"CHAT_ID={chat_id_str}\n")
        os.environ["CHAT_ID"] = chat_id_str
        print(f"[LOG] Novo arquivo .env criado com CHAT_ID={chat_id_str}")
        return

    with open(env_path, "r") as f:
        lines = f.readlines()
    
    if any(line.startswith("CHAT_ID=") for line in lines):
        # Verifica se o ID é o mesmo, senão atualiza
        updated = False
        new_lines = []
        for line in lines:
            if line.startswith("CHAT_ID="):
                current_id = line.strip().split("=")[1]
                if current_id != chat_id_str:
                    new_lines.append(f"CHAT_ID={chat_id_str}\n")
                    updated = True
                else:
                    new_lines.append(line)
            else:
                new_lines.append(line)
        
        if updated:
            with open(env_path, "w") as f:
                f.writelines(new_lines)
            print(f"[LOG] CHAT_ID atualizado para {chat_id_str}")
    else:
        # Adiciona nova linha
        with open(env_path, "a") as f:
            f.write(f"\nCHAT_ID={chat_id_str}\n")
        print(f"[LOG] CHAT_ID={chat_id_str} adicionado ao .env")
    
    os.environ["CHAT_ID"] = chat_id_str

async def safe_send_message(update: Update, text: str):
    """Envia mensagens longas dividindo-as em partes e com fallback de Markdown."""
    if len(text) <= MAX_MESSAGE_LENGTH:
        try:
            await update.message.reply_text(text, parse_mode="Markdown")
        except Exception:
            await update.message.reply_text(text)
    else:
        # Dividir em partes
        for i in range(0, len(text), MAX_MESSAGE_LENGTH):
            part = text[i:i+MAX_MESSAGE_LENGTH]
            try:
                await update.message.reply_text(part, parse_mode="Markdown")
            except Exception:
                await update.message.reply_text(part)
            await asyncio.sleep(0.5) # Evita flood limit

# Handlers
async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.message.chat_id
    salvar_chat_id(chat_id)
    
    msg = (
        "👋 **Olá! Eu sou o seu Assistente de Dados de E-commerce.**\n\n"
        "Estou conectado ao seu banco de dados e pronto para ajudar!\n\n"
        "🚀 **O que posso fazer?**\n"
        "• Me pergunte qualquer coisa sobre vendas, clientes ou preços.\n"
        "• Use `/relatorio` para gerar um resumo executivo completo.\n\n"
        "💡 *Exemplo:* 'Qual foi o produto mais vendido este mês?'"
    )
    await update.message.reply_text(msg, parse_mode="Markdown")

async def relatorio_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("📊 Gerando relatório... isso pode levar alguns segundos.")
    
    try:
        import agente
        relatorio = agente.gerar_relatorio()
        await safe_send_message(update, relatorio)
            
    except Exception as e:
        await update.message.reply_text(f"❌ Erro ao gerar relatório: {e}")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text: str = update.message.text
    chat_id = update.message.chat_id
    salvar_chat_id(chat_id)

    # Mostrar "digitando..."
    await context.bot.send_chat_action(chat_id=chat_id, action="typing")

    try:
        # Chama a função de chat do agente (Gemini)
        response = agente.chat(text)
        await safe_send_message(update, response)
            
    except Exception as e:
        await update.message.reply_text(f"😔 Desculpe, tive um problema ao processar sua pergunta: {e}")

async def error(update: Update, context: ContextTypes.DEFAULT_TYPE):
    print(f'Update {update} causou o erro: {context.error}')

if __name__ == '__main__':
    print('--- Bot Iniciado ---')
    app = Application.builder().token(TOKEN).build()

    # Comandos
    app.add_handler(CommandHandler('start', start_command))
    app.add_handler(CommandHandler('relatorio', relatorio_command))

    # Mensagens de texto
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_message))

    # Erros
    app.add_error_handler(error)

    # Polling
    print('Bot está ouvindo...')
    app.run_polling(poll_interval=3)
