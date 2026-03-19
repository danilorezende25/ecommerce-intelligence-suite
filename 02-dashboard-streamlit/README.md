# 📊 Módulo 02: Visual Intelligence (Streamlit)

Este módulo fornece a interface visual do projeto, permitindo que usuários de negócio explorem os indicadores gerados na Camada Gold do dbt de forma interativa e dinâmica.

## 📈 Funcionalidades Principais

O dashboard é dividido em três visões estratégicas:

1.  **Visão de Vendas**: Acompanhamento de receita total, ticket médio e volume de transações por período (dia/mês/hora).
2.  **Visão de Clientes**: Segmentação da base em tiers (VIP, Top Tier, Regular) e análise geográfica (UF).
3.  **Visão de Pricing**: Comparativo em tempo real do nosso preço vs. média da concorrência, com alertas de "Mais Caro que Todos" ou "Oportunidade de Preço".

## 🎨 Design e UX

- **Tema Dinâmico**: Suporte nativo a Light/Dark Mode.
- **Performance**: Utilização de `st.cache_resource` para otimizar a conexão com o Supabase e acelerar o carregamento dos gráficos.
- **Interatividade**: Filtros globais por categoria e período que impactam todo o dashboard.

## 🚀 Como Executar

1.  Acesse a pasta do módulo e instale as dependências:
    ```bash
    pip install -r requirements.txt
    ```
2.  Configure o arquivo `.env` com sua `SUPABASE_URL`.
3.  Execute o app:
    ```bash
    streamlit run app.py
    ```

---
*Módulo focado em Data Storytelling e entrega de insights acionáveis.*
