with items as (
    select * from {{ ref('stg_fact_order_items') }}
),
dates as (
    select date_key, year, month from {{ source('dw', 'dim_date') }}
)
select
    d.year,
    d.month,
    count(distinct i.order_id) as orders,
    round(sum(i.total_item_value)::numeric, 2) as revenue
from items i
join dates d on i.purchase_date_key = d.date_key
group by d.year, d.month
order by d.year, d.month