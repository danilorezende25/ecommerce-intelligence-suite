SELECT
    v.id_venda,
    v.id_cliente,
    v.id_produto,
    v.quantidade,
    v.preco_unitario::numeric(10,2) AS preco_venda,
    v.data_venda,
    v.canal_venda,
    -- Colunas calculadas
    (v.quantidade * v.preco_unitario)::numeric(10,2) AS receita_total,
    CASE 
        WHEN v.preco_unitario < 100 THEN 'barato'
        WHEN v.preco_unitario < 500 THEN 'médio'
        ELSE 'caro'
    END AS categoria_preco,
    -- Dimensoes temporais
    DATE(v.data_venda::timestamp) AS data_venda_date,
    EXTRACT(YEAR FROM v.data_venda::timestamp) AS ano_venda,
    EXTRACT(MONTH FROM v.data_venda::timestamp) AS mes_venda,
    EXTRACT(DAY FROM v.data_venda::timestamp) AS dia_venda,
    EXTRACT(DOW FROM v.data_venda::timestamp) AS dia_semana,
    EXTRACT(HOUR FROM v.data_venda::timestamp) AS hora_venda
FROM {{ ref('bronze_vendas') }} v