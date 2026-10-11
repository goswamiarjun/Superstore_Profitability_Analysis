# Superstore Profitability Analysis (EUR)

Python analysis of the public *Sample Superstore* retail dataset: KPIs, sales trend, category and sub-category profitability, top products, and the effect of discounts on profit. All amounts are converted from USD to EUR.

![Dashboard](docs/dashboard.png)

## Business Question
Where does the retailer make or lose money, and what should management change?

## Dataset
*Sample - Superstore* (public sample dataset, about 10,000 order lines, orders from 2014 to 2017, all in the United States). The file is not included in this repo. Download it from the source (for example Kaggle), save it as `data/Sample_-_Superstore.csv`.

The data is in **US dollars**. The script converts sales and profit to EUR with a fixed rate of **1 USD = 0.89 EUR** (rounded assumption, change it with `--rate`). A single current rate is a simplification for data from 2014 to 2017.

## KPIs
| KPI | Value (EUR) |
|---|---|
| Total sales | 2,044,508.77 |
| Total profit | 254,893.35 |
| Profit margin | 12.47% |
| Total orders | 5,009 |

## Key Findings
1. **Furniture sells a lot but earns almost nothing.** Furniture has EUR 660k in sales but a margin of only 2.49%, compared with 17.40% for Technology and 17.04% for Office Supplies.
2. **Three sub-categories lose money.** Tables (EUR -15.8k, margin -8.56%), Bookcases (EUR -3.1k) and Supplies (EUR -1.1k) are loss-making. Tables alone destroy more profit than any other sub-category.
3. **Heavy discounts are the biggest profit killer.** Orders without discount have a 29.51% margin. Orders with a discount of 20-40% lose EUR 31.9k (-15.30% margin), and orders over 40% lose EUR 88.6k (-77.40% margin).
4. **Profit depends on a few products.** The top 10 products generate 23.2% of total profit. A single copier (Canon imageCLASS 2200) accounts for EUR 22.4k, or 8.8%.
5. **Sales grew, with a strong year-end season.** Annual sales rose from EUR 431k in 2014 to EUR 653k in 2017 (+51%), with peaks in September to December. The highest month was November 2017 (EUR 105k).

## Recommendations
- Cap discounts at 20% and review pricing for Tables and Bookcases, or stop selling the unprofitable items.
- Protect and promote Technology and the high-margin Office Supplies (Paper, Copiers, Accessories).
- Reduce dependence on a few products by growing the next-best performers.
- Plan stock and staffing for the September to December peak.

## Limitations
- Fixed exchange rate, not the historical rate of each order date.
- No cost, return or customer-level data, so the analysis cannot explain *why* margins are low.
- The data shows correlation (discounts and losses), not proof of cause.

## How to Run
```
pip install -r requirements.txt
python analysis.py --data data/Sample_-_Superstore.csv
```
Optional: `--rate 0.89` sets the USD to EUR rate. The script prints all tables, saves them to `results/` and draws `docs/dashboard.png`.

## Power BI Version
`powerbi/dax_measures_eur.dax` contains the DAX measures (sales, profit and margin in EUR, orders, year-over-year growth, loss-making sub-categories) for building the same dashboard in Power BI Desktop.

## Tech Stack
Python (Pandas, Matplotlib) · DAX / Power BI

## Author
Arjun Goswami · B.Sc. Informatik, Bergische Universität Wuppertal
