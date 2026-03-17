WITH vendas_mensais AS (
    SELECT
        ano_venda,
        mes_venda,
        SUM(receita_total) AS receita_mensal,
        SUM(quantidade) AS quantidade_mensal,
        COUNT(DISTINCT id_venda) AS total_vendas_mensal
    FROM {{ ref('silver_vendas') }}
    GROUP BY 1, 2
),

vendas_ytd AS (
    SELECT
        ano_venda,
        mes_venda,
        receita_mensal,
        quantidade_mensal,
        total_vendas_mensal,
        SUM(receita_mensal) OVER (
            PARTITION BY ano_venda 
            ORDER BY mes_venda 
            ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
        ) AS receita_ytd,
        SUM(quantidade_mensal) OVER (
            PARTITION BY ano_venda 
            ORDER BY mes_venda 
            ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
        ) AS quantidade_ytd
    FROM vendas_mensais
)

SELECT * FROM vendas_ytd
ORDER BY ano_venda DESC, mes_venda DESC
