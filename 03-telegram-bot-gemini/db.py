import os
import pandas as pd
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

# Carregar variáveis de ambiente
load_dotenv()

def get_engine():
    """Retorna o engine de conexão com o PostgreSQL (Supabase)."""
    # Tenta carregar de caminhos comuns se não encontrar no padrão
    db_url = os.getenv("POSTGRES_URL")
    if not db_url:
        # Tenta carregar do diretório .llm se estiver um nível acima
        load_dotenv("../.llm/.env")
        db_url = os.getenv("POSTGRES_URL")
    
    if not db_url:
        raise ValueError("Erro: Variável de ambiente POSTGRES_URL não encontrada.")
    
    return create_engine(db_url)

def execute_query(sql):
    """
    Executa uma query SQL SELECT/WITH de forma segura.
    Retorna um DataFrame do Pandas.
    """
    engine = get_engine()
    
    # Validação básica de segurança: apenas SELECT ou WITH
    sql_clean = sql.strip().upper()
    if not (sql_clean.startswith("SELECT") or sql_clean.startswith("WITH")):
        raise ValueError("Apenas consultas de leitura (SELECT/WITH) são permitidas.")
    
    with engine.connect() as conn:
        return pd.read_sql(text(sql), conn)

if __name__ == "__main__":
    # Teste simples
    try:
        df = execute_query("SELECT 1 as teste")
        print("Conexão bem-sucedida!")
        print(df)
    except Exception as e:
        print(f"Erro no teste de conexão: {e}")
