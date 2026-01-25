"""
State-of-the-art 2026 Streamlit blueprint for the Agentic Silver layer run.
"""
import streamlit as st
import pandas as pd
import yaml
import plotly.express as px
import plotly.graph_objects as go
from pathlib import Path
from datetime import datetime, date

st.set_page_config(
    page_title="Agentic Silver Intelligence",
    page_icon="🧠📊",
    layout="wide",
    initial_sidebar_state="expanded",
)


def apply_professional_theme():
    """Inject modern Streamlit styling that matches 2026 Mesa dashboard expectations."""
    st.markdown(
        """
        <style>
        .stApp { background: #05060a; color: #eef1ff; }
        .stButton button { border-radius: 6px; }
        .stSidebar .stButton button { width: 100%; }
        .stMetric { background: rgba(255,255,255,0.08); border: 1px solid rgba(255,255,255,0.05); border-radius: 12px; }
        .block-container { padding-top: 10px; padding-bottom: 10px; }
        .stMarkdown h1 { margin-bottom: 0.15rem; }
        .stTabs [role='tablist'] { border-bottom: 1px solid rgba(255,255,255,0.1); }
        </style>
        """,
        unsafe_allow_html=True,
    )


def find_repo_root() -> Path:
    """Walk upward until we find a repository that contains src/ and artifacts/."""
    current = Path(__file__).resolve()
    while current != current.parent:
        if (current / "src").exists() and (current / "artifacts").exists():
            return current
        current = current.parent
    return current


@st.cache_data
def load_csv(path: Path, **kwargs) -> pd.DataFrame:
    """Cache CSV reads for repeat interactions."""
    return pd.read_csv(path, **kwargs)


@st.cache_data
def load_yaml(path: Path) -> dict:
    """Load YAML metadata from a Silver artifact directory."""
    if not path.exists():
        return {}
    with path.open("r", encoding="utf-8") as source:
        return yaml.safe_load(source) or {}


def locate_latest_silver_run():
    """Return the newest Silver run directory that still exposes a data/ folder."""
    repo_root = find_repo_root()
    silver_root = repo_root / "artifacts" / "silver"
    if not silver_root.exists():
        return None, None, None
    run_dirs = [d for d in silver_root.iterdir() if d.is_dir() and (d / "data").exists()]
    if not run_dirs:
        return None, None, None
    latest_run = max(run_dirs, key=lambda d: d.name)
    metadata = load_yaml(latest_run / "data" / "metadata.yaml")
    return latest_run.name, latest_run / "data", metadata


def load_silver_tables(data_dir: Path):
    """Load the Silver tables that the dashboard needs."""
    required = {
        "sales": "sales_details.csv",
        "product": "prd_info.csv",
        "customer": "cst_info.csv",
        "location": "LOC_A101.csv",
    }
    tables = {}
    for key, file_name in required.items():
        path = data_dir / file_name
        if not path.exists():
            return None
        tables[key] = load_csv(path)
    return tables


def parse_iso_timestamp(value: str):
    """Convert ISO timestamps (with a 'Z' suffix) into aware datetimes."""
    if not value:
        return None
    if value.endswith("Z"):
        value = value.replace("Z", "+00:00")
    return datetime.fromisoformat(value)


def build_product_lookup(product_df: pd.DataFrame):
    """Build maps from product keys to product names and suffix-based matches."""
    direct = {}
    suffix = {}

    for _, row in product_df.iterrows():
        key = str(row.get("prd_key") or "")
        name = row.get("prd_nm") or ""
        if not key:
            continue
        label = name if name else key
        direct[key] = label
        parts = key.split("-")
        for idx in range(len(parts)):
            suffix_key = "-".join(parts[idx:])
            suffix.setdefault(suffix_key, label)
    return direct, suffix


def resolve_product_name(key: str, lookup: tuple[dict[str, str], dict[str, str]]) -> str | None:
    direct_map, suffix_map = lookup
    if key in direct_map:
        return direct_map[key]
    if key in suffix_map:
        return suffix_map[key]
    return None


def prepare_sales_data(tables: dict) -> tuple[pd.DataFrame, tuple[dict[str, str], dict[str, str]]]:
    """Enrich sales_details with product and customer geography context."""
    sales = tables["sales"].copy()
    product = tables["product"].copy()
    customer = tables["customer"].copy()
    location = tables["location"].copy()

    date_columns = ["sls_order_dt", "sls_ship_dt", "sls_due_dt"]
    for column in date_columns:
        sales[column] = pd.to_datetime(sales[column], errors="coerce")

    sales["sls_sales"] = pd.to_numeric(sales["sls_sales"], errors="coerce")
    sales["sls_price"] = pd.to_numeric(sales["sls_price"], errors="coerce")
    sales["sls_quantity"] = pd.to_numeric(sales["sls_quantity"], errors="coerce")

    customer = customer.assign(
        location_key=customer["cst_key"]
        .astype(str)
        .str.replace("-", "", regex=False)
        .str.upper()
    )
    location = location.assign(
        location_key=location["CID"]
        .astype(str)
        .str.replace("-", "", regex=False)
        .str.upper()
    )
    loc_map = dict(zip(location["location_key"], location["CNTRY"]))
    customer["country"] = customer["location_key"].map(loc_map)
    customer = customer.rename(
        columns={
            "cst_gndr": "customer_gender",
            "cst_marital_status": "customer_marital_status",
        }
    )

    enriched = (
        sales.merge(
            product[["prd_key", "prd_line", "prd_nm", "prd_cost"]],
            left_on="sls_prd_key",
            right_on="prd_key",
            how="left",
        )
        .merge(
            customer[
                [
                    "cst_id",
                    "customer_gender",
                    "customer_marital_status",
                    "country",
                ]
            ],
            left_on="sls_cust_id",
            right_on="cst_id",
            how="left",
        )
    )

    enriched["product_line"] = enriched["prd_line"].fillna("Other").astype(str)
    enriched["product_name"] = enriched["prd_nm"].fillna("Unknown product")
    enriched["customer_gender"] = enriched["customer_gender"].fillna("Unspecified")
    enriched["customer_marital_status"] = enriched["customer_marital_status"].fillna("Unspecified")
    enriched["country"] = enriched["country"].fillna("Unknown")

    enriched["order_dt"] = enriched["sls_order_dt"]
    enriched["order_date"] = enriched["order_dt"].dt.date
    enriched["order_day"] = enriched["order_dt"].dt.day_name()
    enriched["order_week"] = enriched["order_dt"].dt.to_period("W").dt.start_time
    return enriched, build_product_lookup(product)


def session_multiselect(label, options, key, default, help_text=None):
    """Keep multi-select widgets in session state so filters stay bookmarkable."""
    if not options:
        st.sidebar.warning(f"No options available for {label}.")
        return []
    select_all_label = f"Select all {label}"
    if st.sidebar.button(select_all_label, key=f"{key}_sel_all"):
        st.session_state[key] = options
    existing = st.session_state.get(key, default)
    st.sidebar.multiselect(
        label,
        options,
        default=existing,
        key=key,
        help=help_text,
    )
    return st.session_state.get(key, options)


def session_range_slider(key, label, min_value, max_value, value=None, step=None, format=None):
    """Store slider range state so filtering feels deterministic."""
    default_value = st.session_state.get(key, value if value is not None else (min_value, max_value))
    step_value = step
    if step_value is not None:
        if isinstance(min_value, float) or isinstance(max_value, float):
            step_value = float(step_value)
        else:
            step_value = type(min_value)(step_value)
    slider_value = st.sidebar.slider(label, min_value, max_value, default_value, step=step_value, format=format)
    st.session_state[key] = slider_value
    return slider_value


def configure_filters(
    enriched: pd.DataFrame,
    missing_info: dict,
    product_lookup: tuple[dict[str, str], dict[str, str]],
):
    """Render the sidebar filters and explain their dependencies."""
    st.sidebar.header("🧭 Dashboard filters")

    dates = enriched["order_dt"].dropna()
    today = date.today()
    start_date = dates.min().date() if not dates.empty else today
    end_date = dates.max().date() if not dates.empty else today
    st.sidebar.markdown("**Date selection**")
    col_start, col_end = st.sidebar.columns(2)
    start_date_value = col_start.date_input(
        "Start date",
        value=start_date,
        min_value=start_date,
        max_value=end_date,
        key="filter_start_date",
    )
    end_date_value = col_end.date_input(
        "End date",
        value=end_date,
        min_value=start_date_value,
        max_value=end_date,
        key="filter_end_date",
    )
    date_range = (start_date_value, end_date_value)

    available_lines = sorted(enriched["product_line"].dropna().unique())
    selected_lines = session_multiselect(
        "Product lines",
        available_lines,
        "filter_product_lines",
        default=available_lines,
        help_text="Selecting a line automatically trims the available product keys.",
    )

    available_keys = (
        enriched[enriched["product_line"].isin(selected_lines)]["sls_prd_key"]
        .dropna()
        .unique()
    )
    fallback_keys = enriched["sls_prd_key"].dropna().unique()
    key_set = sorted(available_keys) if available_keys.size else sorted(fallback_keys)
    label_options = []
    label_to_key = {}
    for key in key_set:
        name = resolve_product_name(key, product_lookup)
        label = f"{name} ({key})" if name else key
        label_options.append(label)
        label_to_key[label] = key
    selected_labels = session_multiselect(
        "Product names (hierarchical)",
        label_options,
        "filter_product_keys",
        default=label_options,
        help_text="Product-line trimming refreshes this list each time.",
    )
    selected_keys = [label_to_key[label] for label in selected_labels if label in label_to_key]

    country_options = sorted(enriched["country"].unique())
    selected_countries = session_multiselect(
        "Countries / regions",
        country_options,
        "filter_countries",
        default=country_options,
        help_text="Country selection also restricts gender and marital status pools.",
    )

    gender_options = sorted(enriched["customer_gender"].unique())
    selected_genders = session_multiselect(
        "Customer gender",
        gender_options,
        "filter_genders",
        default=gender_options,
    )

    marital_options = sorted(enriched["customer_marital_status"].unique())
    selected_marital = session_multiselect(
        "Customer marital status",
        marital_options,
        "filter_marital_status",
        default=marital_options,
    )

    def _range(series, fallback=0.0):
        valid = series.dropna()
        if valid.empty:
            return fallback, fallback
        return float(valid.min()), float(valid.max())

    sales_min, sales_max = _range(enriched["sls_sales"])
    price_min, price_max = _range(enriched["sls_price"])
    quantity_min, quantity_max = _range(enriched["sls_quantity"])
    quantity_min = int(quantity_min)
    quantity_max = int(quantity_max)

    sales_range = session_range_slider(
        "filter_sales_range",
        "Revenue per record",
        sales_min,
        sales_max,
        value=(sales_min, sales_max),
        format="%.0f",
        step=50,
    )
    price_range = session_range_slider(
        "filter_price_range",
        "Verkaufspreis",
        price_min,
        price_max,
        value=(price_min, price_max),
        format="%.0f",
        step=10,
    )
    quantity_range = session_range_slider(
        "filter_quantity_range",
        "Menge",
        quantity_min,
        quantity_max,
        value=(quantity_min, quantity_max),
        step=1,
    )

    with st.sidebar.expander("Data health & dependency hints", expanded=False):
        st.write(
            f"- Missing `sls_sales`: {missing_info['sales_missing']:,} rows\n"
            f"- Missing `sls_price`: {missing_info['price_missing']:,} rows\n"
            f"- Missing `sls_quantity`: {missing_info['quantity_missing']:,} rows"
        )
        st.caption(
            "Product-line selections cascade into the product-key list; country filters keep the gender and marital pools synchronized."
        )
    st.sidebar.caption("@st.cache_data caches file reads; session state keeps filter combos bookmarkable.")

    return {
        "date_range": date_range,
        "product_lines": selected_lines,
        "product_keys": selected_keys,
        "countries": selected_countries,
        "genders": selected_genders,
        "marital_status": selected_marital,
        "sales_range": sales_range,
        "price_range": price_range,
        "quantity_range": quantity_range,
    }


def apply_filters(df: pd.DataFrame, filters: dict) -> pd.DataFrame:
    """Apply the sidebar filters to the enriched sales data."""
    mask = df["order_dt"].notna()
    start_date, end_date = filters["date_range"]
    mask &= df["order_dt"].dt.date >= start_date
    mask &= df["order_dt"].dt.date <= end_date
    mask &= df["product_line"].isin(filters["product_lines"])
    mask &= df["sls_prd_key"].isin(filters["product_keys"])
    mask &= df["country"].isin(filters["countries"])
    mask &= df["customer_gender"].isin(filters["genders"])
    mask &= df["customer_marital_status"].isin(filters["marital_status"])

    sales_low, sales_high = filters["sales_range"]
    mask &= df["sls_sales"].between(sales_low, sales_high).fillna(False)

    price_low, price_high = filters["price_range"]
    mask &= df["sls_price"].between(price_low, price_high).fillna(False)

    quantity_low, quantity_high = filters["quantity_range"]
    mask &= df["sls_quantity"].between(quantity_low, quantity_high).fillna(False)

    return df.loc[mask].copy()


def render_kpi_cards(filtered: pd.DataFrame, full: pd.DataFrame):
    """Show the filtered KPIs alongside baseline deltas."""
    st.markdown("### KPI deck & filter coverage")
    filtered_revenue = float(filtered["sls_sales"].sum())
    full_revenue = float(full["sls_sales"].sum())
    filtered_orders = filtered["sls_ord_num"].nunique()
    full_orders = full["sls_ord_num"].nunique()
    filtered_customers = filtered["sls_cust_id"].nunique()
    full_customers = full["sls_cust_id"].nunique()
    avg_order_value = filtered_revenue / filtered_orders if filtered_orders else 0.0
    baseline_avg = full_revenue / full_orders if full_orders else 0.0

    cols = st.columns(4)
    cols[0].metric(
        "Revenue (gefiltert)",
        f"€{filtered_revenue:,.0f}",
        delta=filtered_revenue - full_revenue,
    )
    cols[1].metric(
        "Average Order Value",
        f"€{avg_order_value:,.2f}",
        delta=avg_order_value - baseline_avg,
    )
    cols[2].metric(
        "Transactions in view",
        f"{filtered_orders:,}",
        delta=filtered_orders - full_orders,
    )
    cols[3].metric(
        "Customers in view",
        f"{filtered_customers:,}",
        delta=filtered_customers - full_customers,
    )


def render_charts(filtered: pd.DataFrame):
    """Render the interactive Plotly charts and sample table."""
    st.markdown("### Interactive charts")
    if filtered.empty:
        st.warning("No rows after the current filter—adjust the sidebar controls.")
        return

    tab1, tab2, tab3 = st.tabs(["📈 Revenue trajectory", "📊 Product & Geography", "🧪 Order signals"])

    with tab1:
        st.subheader("Revenue trajectory (daily)")
        time_series = (
            filtered.dropna(subset=["order_dt", "sls_sales"])
            .assign(order_date=lambda df: df["order_dt"].dt.date)
            .groupby("order_date", as_index=False)["sls_sales"]
            .sum()
        )
        if not time_series.empty:
            fig = px.line(
                time_series,
                x="order_date",
                y="sls_sales",
                markers=True,
                title="Daily revenue",
                labels={"order_date": "Order date", "sls_sales": "Revenue (€)"},
            )
            fig.update_traces(mode="lines+markers")
            fig.update_layout(hovermode="x unified", yaxis_title="Revenue (€)")
            st.plotly_chart(fig, width="stretch")
        else:
            st.info("No revenue data available for the selected window.")

    with tab2:
        st.subheader("Product-line mix & geopolitical heatmap")
        col1, col2 = st.columns(2)
        with col1:
            product_summary = (
                filtered[["product_line", "sls_sales"]]
                .dropna()
                .groupby("product_line", as_index=False)["sls_sales"]
                .sum()
            )
            if not product_summary.empty:
                total_sales = product_summary["sls_sales"].sum()
                top_lines = (
                    product_summary.sort_values("sls_sales", ascending=False).head(5).copy()
                )
                others_sales = total_sales - top_lines["sls_sales"].sum()
                waterfall_names = top_lines["product_line"].tolist()
                waterfall_values = top_lines["sls_sales"].tolist()
                if others_sales > 0:
                    waterfall_names.append("Other")
                    waterfall_values.append(others_sales)
                waterfall_names.append("Total")
                waterfall_values.append(total_sales)

                measures = ["relative"] * (len(waterfall_values) - 1) + ["total"]
                fig_waterfall = go.Figure(
                    go.Waterfall(
                        name="Revenue bridge",
                        orientation="v",
                        measure=measures,
                        x=waterfall_names,
                        y=waterfall_values,
                        text=[f"€{int(v):,}" for v in waterfall_values],
                        textposition="outside",
                        connector={"line": {"color": "#444"}},
                        increasing={"marker": {"color": "#00CC96"}},
                        decreasing={"marker": {"color": "#EF553B"}},
                        totals={"marker": {"color": "#636EFA"}},
                    )
                )
                fig_waterfall.update_layout(
                    title="Product-line revenue bridge",
                    yaxis_title="Revenue (€)",
                    xaxis_title="Product line",
                    uniformtext_mode="hide",
                    margin=dict(l=0, r=0, t=40, b=40),
                )
                st.plotly_chart(fig_waterfall, width="stretch")
            else:
                st.info("No product lines match the current selection.")
        with col2:
            heatmap_source = (
                filtered.dropna(subset=["order_day", "country", "sls_sales"])
                .groupby(["order_day", "country"], as_index=False)["sls_sales"]
                .sum()
            )
            weekdays = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
            heatmap_source["order_day"] = pd.Categorical(
                heatmap_source["order_day"], categories=weekdays, ordered=True
            )
            pivot = heatmap_source.pivot(index="order_day", columns="country", values="sls_sales").fillna(0)
            if not pivot.empty:
                fig_heat = px.imshow(
                    pivot,
                    labels={"x": "Country", "y": "Weekday", "color": "Revenue (€)"},
                    title="Revenue heatmap by weekday & country",
                    aspect="auto",
                    text_auto=".2s",
                    color_continuous_scale="Teal",
                )
                st.plotly_chart(fig_heat, width="stretch")
            else:
                st.info("Heatmap requires data with country, weekday, and revenue.")

    with tab3:
        st.subheader("Order Signals")
        agg = (
            filtered.dropna(subset=["sls_price", "sls_quantity"])
            .assign(
                price_bucket=lambda df: pd.cut(
                    df["sls_price"],
                    bins=10,
                    include_lowest=True,
                    labels=False,
                )
            )
        )
        if not agg.empty:
            bucket_summary = (
                agg.groupby("price_bucket", as_index=False).agg(
                    price_mean=("sls_price", "mean"),
                    quantity_median=("sls_quantity", "median"),
                    transactions=("sls_ord_num", "nunique"),
                )
            )
            bucket_summary["price_bucket_label"] = bucket_summary["price_mean"].round(0).map(
                lambda v: f"€{int(v):,}"
            )
            fig_bucket = px.bar(
                bucket_summary,
                x="price_bucket_label",
                y="quantity_median",
                color="transactions",
                color_continuous_scale="Viridis",
                labels={"quantity_median": "Median quantity", "price_bucket_label": "Price bucket"},
                title="Median quantity per price bucket & transaction count",
                text="quantity_median",
            )
            fig_bucket.update_layout(xaxis_title="Price bucket", yaxis_title="Median quantity")
            st.plotly_chart(fig_bucket, width="stretch")
        else:
            st.info("No price/quantity information available with the active filters.")

        st.subheader("Filtered sample")
        st.dataframe(
            filtered.sort_values("order_dt", ascending=False)[
                [
                    "sls_ord_num",
                    "order_dt",
                    "product_line",
                    "country",
                    "sls_sales",
                    "sls_quantity",
                    "sls_price",
                ]
            ].head(10),
            width="stretch",
        )


def render_quality_panel(metadata: dict, run_id: str, missing_info: dict):
    """Surface the Silver run metadata, suggested transforms, and missing stats."""
    st.markdown("### Silver run diagnostics")
    run_info = metadata.get("run", {})
    summary = metadata.get("summary", {})
    tables = metadata.get("tables", {})

    started = parse_iso_timestamp(run_info.get("started_utc"))
    ended = parse_iso_timestamp(run_info.get("ended_utc"))
    duration = ended - started if started and ended else None

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Latest Silver run", run_id)
    col2.metric(
        "Started (UTC)",
        started.strftime("%Y-%m-%d %H:%M:%S") if started else "n/a",
    )
    col3.metric("Duration", str(duration).split(".")[0] if duration else "n/a")
    col4.metric("Tables (+metadata)", f"{len(tables)}", delta=summary.get("files_total", 0))

    suggestion_count = sum(
        info.get("transformations_suggested", 0)
        for info in tables.values()
        if isinstance(info, dict)
    )

    with st.expander("Table overview & transformation suggestions", expanded=False):
        table_rows = []
        for table_name, table_info in tables.items():
            table_rows.append(
                {
                    "table": table_name,
                    "rows_out": table_info.get("rows_out"),
                    "transform_hints": table_info.get("transformations_suggested", 0),
                }
            )
        if table_rows:
            st.table(pd.DataFrame(table_rows))
        else:
            st.write("No table-specific metadata found.")
        st.write(f"- Agent recommendations: {suggestion_count}")
        rows_total = summary.get("total_rows")
        rows_display = f"{rows_total:,}" if isinstance(rows_total, (int, float)) else rows_total
        st.write(f"- Rows processed (summary metadata): {rows_display}")

    st.caption(
        f"Data source: artifacts/silver/{run_id}/data · Missing sales: {missing_info['sales_missing']:,}, "
        f"Missing prices: {missing_info['price_missing']:,}"
    )


def main():
    st.title("Agentic Silver Layer Intelligence")
    apply_professional_theme()
    st.markdown(
        "A state-of-the-art Streamlit layer inspired by 2026 analytics best practices "
        "– contextual KPIs, airy spacing, sticky filters, and low-contrast cards for executive focus."
    )
    run_id, data_dir, metadata = locate_latest_silver_run()
    if not run_id:
        st.error("No Silver run found. Please execute the ELT pipeline first.")
        return

    st.success(f"📡 Latest Silver run: {run_id}")
    st.caption(f"Source: {data_dir}")
    tables = load_silver_tables(data_dir)
    if tables is None:
        st.error("Essential Silver tables could not be loaded.")
        return

    enriched, product_lookup = prepare_sales_data(tables)
    missing_info = {
        "sales_missing": int(enriched["sls_sales"].isna().sum()),
        "price_missing": int(enriched["sls_price"].isna().sum()),
        "quantity_missing": int(enriched["sls_quantity"].isna().sum()),
    }
    filters = configure_filters(enriched, missing_info, product_lookup)
    filtered = apply_filters(enriched, filters)
    render_kpi_cards(filtered, enriched)

    st.markdown("### Filter summary & active dependencies")
    with st.expander("Filter overview", expanded=False):
        st.write(f"- Dates: {filters['date_range'][0]} to {filters['date_range'][1]}")
        st.write(f"- Product lines: {', '.join(filters['product_lines'])}")
        st.write(f"- Product keys: {len(filters['product_keys'])} selected (driven by line)")
        st.write(f"- Countries: {', '.join(filters['countries'])}")
        st.write(f"- Genders: {', '.join(filters['genders'])}")
        st.write(f"- Marital statuses: {', '.join(filters['marital_status'])}")

    render_charts(filtered)
    render_quality_panel(metadata, run_id, missing_info)


if __name__ == "__main__":
    main()
