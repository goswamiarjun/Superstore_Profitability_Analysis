"""Superstore Profitability Analysis (in EUR)

Reads the public 'Sample - Superstore' CSV, converts USD to EUR, calculates
the KPIs, saves result tables to results/ and draws one dashboard image
to docs/dashboard.png.

Usage:
    python analysis.py --data data/Sample_-_Superstore.csv
    python analysis.py --data data/Sample_-_Superstore.csv --rate 0.89
"""
import argparse
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd

ROOT = Path(__file__).resolve().parent
RESULTS = ROOT / "results"
DOCS = ROOT / "docs"

# 1 USD in EUR. The data is in US dollars (Country = United States).
# Check the current ECB reference rate and update this value if needed.
DEFAULT_RATE = 0.89


def load(path, rate):
    df = pd.read_csv(path, encoding="latin-1")
    df["Order Date"] = pd.to_datetime(df["Order Date"], format="%m/%d/%Y")
    df["Sales"] = df["Sales"] * rate      # now in EUR
    df["Profit"] = df["Profit"] * rate    # now in EUR
    return df


def compute(df):
    out = {}
    sales, profit = df["Sales"].sum(), df["Profit"].sum()
    out["kpis"] = pd.DataFrame({
        "kpi": ["Total sales (EUR)", "Total profit (EUR)", "Profit margin (%)", "Total orders"],
        "value": [round(sales, 2), round(profit, 2), round(100 * profit / sales, 2),
                  df["Order ID"].nunique()],
    })

    m = (df.groupby(df["Order Date"].dt.to_period("M"))["Sales"].sum().reset_index())
    m["Order Date"] = m["Order Date"].dt.to_timestamp()
    out["monthly"] = m.rename(columns={"Order Date": "month", "Sales": "sales_eur"})

    def table(by):
        t = df.groupby(by)[["Sales", "Profit"]].sum()
        t["margin_pct"] = 100 * t["Profit"] / t["Sales"]
        return t.round(2).rename(columns={"Sales": "sales_eur", "Profit": "profit_eur"})

    out["category"] = table("Category")
    out["subcategory"] = table("Sub-Category").sort_values("profit_eur")

    top = (df.groupby("Product Name")["Profit"].sum().sort_values(ascending=False).head(10))
    out["top_products"] = top.round(2).reset_index().rename(columns={"Profit": "profit_eur"})

    bands = pd.cut(df["Discount"], [-0.01, 0, 0.2, 0.4, 1.0],
                   labels=["No discount", "Up to 20%", "20-40%", "Over 40%"])
    d = df.groupby(bands, observed=True)[["Sales", "Profit"]].sum()
    d["margin_pct"] = 100 * d["Profit"] / d["Sales"]
    out["discount_bands"] = d.round(2).rename(columns={"Sales": "sales_eur", "Profit": "profit_eur"})
    return out


def draw(df, res, rate):
    k = res["kpis"].set_index("kpi")["value"]
    fig = plt.figure(figsize=(16, 10))
    gs = fig.add_gridspec(3, 12, height_ratios=[0.55, 1.5, 1.6], hspace=0.6, wspace=2.2)
    fig.suptitle("Retail Sales & Profitability Dashboard (EUR)", fontsize=20, fontweight="bold")

    # KPI cards
    cards = [(f"€{k['Total sales (EUR)']/1e6:.2f}M", "Total Sales"),
             (f"€{k['Total profit (EUR)']/1e3:.0f}K", "Total Profit"),
             (f"{k['Profit margin (%)']:.2f}%", "Profit Margin"),
             (f"{int(k['Total orders']):,}", "Total Orders")]
    for i, (value, label) in enumerate(cards):
        ax = fig.add_subplot(gs[0, i * 3:(i + 1) * 3]); ax.axis("off")
        ax.text(0.5, 0.62, value, ha="center", fontsize=24, fontweight="bold")
        ax.text(0.5, 0.15, label, ha="center", fontsize=12, color="gray")

    # Monthly sales trend
    ax = fig.add_subplot(gs[1, 0:7])
    m = res["monthly"]
    ax.plot(m["month"], m["sales_eur"] / 1e3, color="#1f77b4", linewidth=2)
    ax.set_title("Monthly sales trend 2014-2017", loc="left", fontweight="bold")
    ax.set_ylabel("Sales (EUR thousand)"); ax.grid(alpha=0.3)

    # Category sales vs profit
    ax = fig.add_subplot(gs[1, 7:12])
    c = res["category"]
    x = range(len(c)); w = 0.38
    ax.bar([i - w / 2 for i in x], c["sales_eur"] / 1e3, w, label="Sales", color="#1f77b4")
    ax.bar([i + w / 2 for i in x], c["profit_eur"] / 1e3, w, label="Profit", color="#2ca02c")
    ax.set_xticks(list(x)); ax.set_xticklabels(c.index)
    ax.set_title("Sales vs. profit by category", loc="left", fontweight="bold")
    ax.set_ylabel("EUR thousand"); ax.legend(); ax.grid(axis="y", alpha=0.3)

    # Sub-category: sales vs profit
    ax = fig.add_subplot(gs[2, 0:4])
    s = res["subcategory"]
    colors = ["#d62728" if p < 0 else "#1f77b4" for p in s["profit_eur"]]
    ax.scatter(s["sales_eur"] / 1e3, s["profit_eur"] / 1e3, c=colors, s=60)
    for name, row in s.iterrows():
        if row["profit_eur"] < 0 or row["profit_eur"] > 35000:
            ax.annotate(name, (row["sales_eur"] / 1e3, row["profit_eur"] / 1e3),
                        textcoords="offset points", xytext=(5, 5), fontsize=8)
    ax.axhline(0, color="gray", linewidth=0.8)
    ax.set_title("Sub-categories: sales vs. profit (red = loss)", loc="left", fontweight="bold")
    ax.set_xlabel("Sales (EUR thousand)"); ax.set_ylabel("Profit (EUR thousand)"); ax.grid(alpha=0.3)

    # Discount impact
    ax = fig.add_subplot(gs[2, 4:6])
    d = res["discount_bands"]
    ax.bar(d.index.astype(str), d["profit_eur"] / 1e3,
           color=["#2ca02c" if p >= 0 else "#d62728" for p in d["profit_eur"]])
    ax.set_title("Profit by discount level", loc="left", fontweight="bold")
    ax.set_ylabel("EUR thousand"); ax.tick_params(axis="x", rotation=30)
    ax.axhline(0, color="gray", linewidth=0.8); ax.grid(axis="y", alpha=0.3)

    # Top 10 products
    ax = fig.add_subplot(gs[2, 7:12])
    t = res["top_products"].iloc[::-1]
    ax.barh(t["Product Name"].str.slice(0, 26), t["profit_eur"] / 1e3, color="#1f77b4")
    ax.set_title("Top 10 products by profit", loc="left", fontweight="bold")
    ax.set_xlabel("Profit (EUR thousand)"); ax.tick_params(axis="y", labelsize=7)

    fig.text(0.99, 0.005, f"Data: Sample Superstore (USD) converted at 1 USD = {rate} EUR",
             ha="right", fontsize=8, color="gray")
    DOCS.mkdir(exist_ok=True)
    fig.savefig(DOCS / "dashboard.png", dpi=150, bbox_inches="tight")
    plt.close(fig)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--data", required=True, help="path to Sample_-_Superstore.csv")
    ap.add_argument("--rate", type=float, default=DEFAULT_RATE, help="USD to EUR rate")
    a = ap.parse_args()

    df = load(a.data, a.rate)
    res = compute(df)

    RESULTS.mkdir(exist_ok=True)
    for name, table in res.items():
        table.to_csv(RESULTS / f"{name}.csv", index=name not in ("kpis", "monthly", "top_products"))
        print(f"\n=== {name} ===\n{table.to_string()}")
    draw(df, res, a.rate)
    print("\nDashboard saved to docs/dashboard.png")


if __name__ == "__main__":
    main()
