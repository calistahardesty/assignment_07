"""
3_Analysis.py — Part 3: where are we high or low, and what are we missing?

Two tabs. Prices: how many prices are below and above the market, then our price
next to every rival's for each item and size, with where we stand — filtered to
the products the owner picks. Gaps: what the rivals sell that we don't
(most-sold first), and what only we sell.

Items the owner has not reviewed yet are left out, with a warning that says so.

Test it: pytest tests/test_pipeline.py -k analysis_page
"""

import os

import pandas as pd
import streamlit as st

from rivals import (
    ABOVE_ALL,
    ABOVE_AVERAGE,
    BELOW_ALL,
    BELOW_AVERAGE,
    DECISIONS_FILE,
    MENUS_FILE,
    add_canonical,
    compare_prices,
    gap_analysis,
    match_items,
    price_table,
)
from rivals.settings import DECISION_COLUMNS

# 1. Heading and data
st.set_page_config(layout="wide")
st.title("Salt City: Prices and Gaps")

if not os.path.exists(MENUS_FILE):
    st.info("No menus yet — scrape the rivals on the Scrape page first.")
    st.stop()

menus = pd.read_csv(MENUS_FILE)
if os.path.exists(DECISIONS_FILE):
    decisions = pd.read_csv(DECISIONS_FILE)
else:
    decisions = pd.DataFrame(columns=DECISION_COLUMNS)
matches = match_items(menus, decisions)

waiting = int((matches["status"] == "unreviewed").sum())
if waiting:
    st.warning(
        f"{waiting} rival items are waiting for review and are left out below. "
        "Finish them on the Review Matches page."
    )

# 2. The analysis — all of it is in the package
menus = add_canonical(menus, matches)
prices = price_table(menus)
comparison = compare_prices(prices)
gaps = gap_analysis(menus)

# 3. Two tabs
prices_tab, gaps_tab = st.tabs(["Prices", "Gaps"])

# 4. The Prices tab
with prices_tab:
    below = comparison["our_position"].isin([BELOW_ALL, BELOW_AVERAGE])
    above = comparison["our_position"].isin([ABOVE_ALL, ABOVE_AVERAGE])
    col1, col2 = st.columns(2)
    col1.metric("Priced below the market", int(below.sum()))
    col2.metric("Priced above the market", int(above.sum()))

    products = st.multiselect(
        "Products",
        sorted(comparison["canonical"].unique()),
        key="products",
        placeholder="All products",
    )
    if products:
        shown = comparison[comparison["canonical"].isin(products)]
    else:
        shown = comparison
    st.dataframe(shown, hide_index=True)
    st.caption(
        "👍👍 lower than all of them · 👍 lower than their average · "
        "👉👈 average · 👎 higher than their average · "
        "👎👎 higher than all of them"
    )

# 5. The Gaps tab
with gaps_tab:
    st.subheader("Only them — what we don't sell yet")
    st.dataframe(gaps[gaps["where"] == "only them"], hide_index=True)
    st.subheader("Only us — what sets us apart")
    st.dataframe(gaps[gaps["where"] == "only us"], hide_index=True)
