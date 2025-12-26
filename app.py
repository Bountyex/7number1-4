import streamlit as st
import pandas as pd
import random

st.set_page_config(page_title="Lowest Payout Lottery Finder", layout="wide")
st.title("🎯 Lowest Payout Lottery Combination Finder")

# =============================
# UPLOAD FILE
# =============================
uploaded_file = st.file_uploader("📂 Upload Excel file (tickets in Column A)", type=["xlsx"])

if not uploaded_file:
    st.stop()

df = pd.read_excel(uploaded_file)

# =============================
# READ & PREPARE TICKETS
# =============================
tickets = set()

for val in df.iloc[:, 0]:
    try:
        nums = tuple(sorted(map(int, str(val).split(","))))
        if len(nums) == 7:
            tickets.add(frozenset(nums))
    except:
        pass

tickets = list(tickets)
st.success(f"🎟️ Total unique tickets loaded: {len(tickets)}")

# =============================
# CONFIG
# =============================
NUMBERS = list(range(1, 38))

TARGET_RESULTS = st.number_input("🎯 Target results", 1, 100, 20)
MAX_ITERATIONS = st.number_input("🔁 Max iterations", 1000, 5_000_000, 800_000)
PAYOUT_LIMIT = st.number_input("💰 Max payout limit", 100, 10000, 3000)

start = st.button("🚀 Start Search")

# =============================
# PAYOUT FUNCTION (OPTIMIZED)
# =============================
def calculate_payout(combo_set):
    total = 0
    match4 = 0

    for ticket in tickets:
        m = len(combo_set & ticket)

        if m >= 5:
            return None

        if m == 4:
            match4 += 1
            if match4 > 1:
                return None
            total += 1000

        elif m == 3:
            total += 15

        if total > PAYOUT_LIMIT:
            return None

    if match4 != 1:
        return None

    return total

# =============================
# SEARCH
# =============================
if start:
    results = {}
    seen = set()

    progress = st.progress(0)
    status = st.empty()

    update_every = max(1, MAX_ITERATIONS // 200)

    for i in range(int(MAX_ITERATIONS)):
        combo = tuple(sorted(random.sample(NUMBERS, 7)))

        if combo in seen:
            continue

        seen.add(combo)
        combo_set = frozenset(combo)

        payout = calculate_payout(combo_set)
        if payout is not None:
            results[combo] = payout
            status.write(f"✅ Found {len(results)} | {combo} → ₹{payout}")

        if i % update_every == 0:
            progress.progress(i / MAX_ITERATIONS)

        if len(results) >= TARGET_RESULTS:
            break

    progress.progress(1.0)

    # =============================
    # FINAL OUTPUT
    # =============================
    st.subheader("🎯 Lowest Payout Results")

    final = sorted(results.items(), key=lambda x: x[1])
    out_df = pd.DataFrame(final, columns=["Combination", "Total Payout"])
    st.dataframe(out_df, use_container_width=True)

    st.success(f"✅ Completed after {len(seen)} combinations tested")
