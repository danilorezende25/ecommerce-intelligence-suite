import os
import datetime
import google.generativeai as genai
from db import execute_query
from dotenv import load_dotenv
import pandas as pd
import requests

# Carregar variáveis de ambiente
load_dotenv()

# Configurar Gemini
GEMINI_KEY = os.getenv("GEMINI_API_KEY")
if not GEMINI_KEY:
    # Tenta carregar do diretório .llm
    load_dotenv("../.llm/.env")
    GEMINI_KEY = os.getenv("GEMINI_API_KEY")

genai.configure(api_key=GEMINI_KEY)

# Schema Context para o Gemini
SCHEMA_CONTEXT = """
Você tem acesso a 3 tabelas no schema Gold (PostgreSQL):

1. public_gold_sales.vendas_temporais:
   - data_venda (DATE), ano_venda, mes_venda, dia_venda, dia_semana_nome
   - hora_venda (0-23)
   - receita_total (NUMERIC), quantidade_total, total_vendas, total_clientes_unicos, ticket_medio

2. public_gold_cs.clientes_segmentacao:
   - cliente_id, nome_cliente, estado
   - receita_total, total_compras, ticket_medio
   - primeira_compra, ultima_compra, segmento_cliente (VIP, TOP_TIER, REGULAR)
   - ranking_receita (1 = maior receita)

3. public_gold_pricing.precos_competitividade:
   - produto_id, nome_produto, categoria, marca
   - nosso_preco, preco_medio_concorrentes, preco_minimo_concorrentes, preco_maximo_concorrentes
   - total_concorrentes, diferenca_percentual_vs_media, classificacao_preco
   - receita_total, quantidade_total
"""

# Definir Ferramenta (Tool) para o Gemini
def executar_sql(sql: str):
    """Executa uma query SQL SELECT no banco de dados do e-commerce."""
    try:
        df = execute_query(sql)
        return df.to_dict(orient="records")
    except Exception as e:
        return {"error": str(e)}

# Inicializar Modelo com Tools
model = genai.GenerativeModel(
    model_name='gemini-2.5-flash',
    tools=[executar_sql]
)

def chat(pergunta: str):
    """Responde qualquer pergunta usando tool use (SQL)."""
    chat_session = model.start_chat(enable_automatic_function_calling=True)
    
    prompt = f"""
    Você é um analista de dados senior de um e-commerce brasileiro.
    Use os dados do banco para responder perguntas.
    Responda sempre em português. Formate valores monetários em R$.
    
    {SCHEMA_CONTEXT}
    
    Pergunta do usuário: {pergunta}
    """
    
    response = chat_session.send_message(prompt)
    return response.text

def gerar_relatorio():
    """Gera o relatório executivo diário."""
    print("[LOG] Iniciando geração do relatório...")
    
    # 1. Dados de Vendas (últimos 7 dias)
    q1 = """
    SELECT data_venda, dia_semana_nome,
        SUM(receita_total) AS receita,
        SUM(total_vendas) AS vendas,
        SUM(total_clientes_unicos) AS clientes,
        AVG(ticket_medio) AS ticket_medio
    FROM public_gold_sales.vendas_temporais
    GROUP BY data_venda, dia_semana_nome
    ORDER BY data_venda DESC
    LIMIT 7
    """
    
    # 2. Segmentação de Clientes
    q2 = """
    SELECT segmento_cliente,
        COUNT(*) AS total_clientes,
        SUM(receita_total) AS receita_total,
        AVG(ticket_medio) AS ticket_medio_avg
    FROM public_gold_cs.clientes_segmentacao
    GROUP BY segmento_cliente
    ORDER BY receita_total DESC
    """
    
    # 3. Alertas de Pricing
    q3 = """
    SELECT classificacao_preco,
        COUNT(*) AS total_produtos,
        AVG(diferenca_percentual_vs_media) AS dif_media_pct
    FROM public_gold_pricing.precos_competitividade
    GROUP BY classificacao_preco
    ORDER BY total_produtos DESC
    """
    
    # 4. Produtos Críticos
    q4 = """
    SELECT nome_produto, categoria, nosso_preco,
        preco_medio_concorrentes,
        diferenca_percentual_vs_media
    FROM public_gold_pricing.precos_competitividade
    WHERE classificacao_preco = 'MAIS_CARO_QUE_TODOS'
    ORDER BY diferenca_percentual_vs_media DESC
    LIMIT 5
    """
    
    # Executar Queries
    try:
        df_vendas = execute_query(q1)
        df_cs = execute_query(q2)
        df_pricing = execute_query(q3)
        df_criticos = execute_query(q4)
    except Exception as e:
        return f"Erro ao consultar o banco: {e}"

    # Prompt para o Gemini consolidar
    prompt = f"""
    Como Analista Senior, gere um relatório executivo para a diretoria.
    Baseie-se nos dados abaixo:
    
    VENDAS (7 DIAS):
    {df_vendas.to_markdown()}
    
    CLIENTES:
    {df_cs.to_markdown()}
    
    PRICING:
    {df_pricing.to_markdown()}
    
    PRODUTOS CRÍTICOS:
    {df_criticos.to_markdown()}
    
    O relatório deve ter 3 seções: Comercial, CS e Pricing.
    Seja estratégico e direto. Use valores em R$.
    AVISO: Evite usar sublinhados (_) fora de blocos de código, pois eles quebram a formatação do Telegram.
    """
    
    response = model.generate_content(prompt)
    report_text = response.text
    
    # Salvar em arquivo
    filename = f"relatorio_{datetime.date.today()}.md"
    with open(filename, "w", encoding="utf-8") as f:
        f.write(report_text)
    
    print(f"[LOG] Relatório gerado: {filename}")
    return report_text

def enviar_telegram(texto: str):
    """Envia mensagem direta via API HTTP do Telegram."""
    token = os.getenv("TELEGRAM")
    chat_id = os.getenv("CHAT_ID")
    
    if not token or not chat_id:
        print("[AVISO] Telegram Token ou CHAT_ID não configurados. Bot não pode enviar.")
        return False
    
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    
    # Dividir texto se for longo (limite do Telegram é ~4096)
    parts = [texto[i:i+4000] for i in range(0, len(texto), 4000)]
    
    for part in parts:
        payload = {
            "chat_id": chat_id,
            "text": part,
            "parse_mode": "Markdown"
        }
        try:
            r = requests.post(url, json=payload)
            if r.status_code != 200:
                # Tenta enviar como texto puro se falhar o markdown
                payload.pop("parse_mode")
                requests.post(url, json=payload)
        except Exception as e:
            print(f"[ERRO] Falha ao enviar Telegram: {e}")
            return False
            
    print(f"[LOG] Mensagem enviada para Telegram (Chat ID: {chat_id})")
    return True

if __name__ == "__main__":
    # Teste de execução direta: Gera relatório e tenta enviar
    rel = gerar_relatorio()
    print("\n--- RELATÓRIO GERADO ---")
    print(rel)
    enviar_telegram(rel)
