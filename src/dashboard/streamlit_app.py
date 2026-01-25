"""
Business Intelligence Dashboard
Interactive Streamlit dashboard for C-Level and team analytics
"""

import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
import json
from datetime import datetime

# Page config
st.set_page_config(
    page_title="Business Intelligence Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

def find_repo_root():
    """Find repository root directory"""
    current = Path(__file__).resolve()
    while current != current.parent:
        if (current / "src").exists() and (current / "artifacts").exists():
            return current
        current = current.parent
    return Path(__file__).resolve().parent.parent.parent

def load_latest_run_data():
    """Load data from the latest pipeline run"""
    repo_root = find_repo_root()
    reports_dir = repo_root / "artifacts" / "reports"
    
    if not reports_dir.exists():
        return None, None, None
    
    # Find latest run
    run_dirs = [d for d in reports_dir.iterdir() if d.is_dir()]
    if not run_dirs:
        return None, None, None
    
    latest_run = max(run_dirs, key=lambda x: x.name)
    run_id = latest_run.name
    
    # Load data
    gold_data_dir = repo_root / "artifacts" / "gold" / "marts" / run_id / "data"
    summary_file = latest_run / "summary_report.json"
    
    summary_data = {}
    if summary_file.exists():
        with open(summary_file, 'r') as f:
            summary_data = json.load(f)
    
    return run_id, gold_data_dir, summary_data

def load_business_data(gold_data_dir):
    """Load business data from Gold layer"""
    data = {}
    
    # Load customer data
    customer_file = gold_data_dir / "gold_dim_customer.csv"
    if customer_file.exists():
        data['customers'] = pd.read_csv(customer_file)
    
    # Load product data
    product_file = gold_data_dir / "gold_dim_product.csv"
    if product_file.exists():
        data['products'] = pd.read_csv(product_file)
    
    # Load sales data
    sales_file = gold_data_dir / "gold_fact_sales.csv"
    if sales_file.exists():
        data['sales'] = pd.read_csv(sales_file)
    
    # Load KPIs
    kpi_file = gold_data_dir / "gold_agg_exec_kpis.csv"
    if kpi_file.exists():
        data['kpis'] = pd.read_csv(kpi_file)
    
    return data

def main():
    st.title("🏢 Business Intelligence Dashboard")
    st.markdown("---")
    
    # Load data
    run_id, gold_data_dir, summary_data = load_latest_run_data()
    
    if not run_id:
        st.error("No pipeline run data found. Please run the pipeline first.")
        return
    
    st.success(f"📈 Latest Run: {run_id}")
    
    # Load business data
    data = load_business_data(gold_data_dir)
    
    if not data:
        st.error("No business data found in Gold layer.")
        return
    
    # Sidebar filters
    st.sidebar.header("🎛️ Filters")
    
    # Main dashboard tabs
    tab1, tab2, tab3, tab4 = st.tabs(["📊 Executive Summary", "👥 Customer Analytics", "📦 Product Performance", "💰 Revenue Analysis"])
    
    with tab1:
        st.header("Executive Summary")
        
        # KPI metrics
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            if 'customers' in data:
                customer_count = len(data['customers'])
                st.metric("Total Customers", f"{customer_count:,}")
        
        with col2:
            if 'products' in data:
                product_count = len(data['products'])
                st.metric("Total Products", f"{product_count:,}")
        
        with col3:
            if 'sales' in data and 'sales_amount' in data['sales'].columns:
                total_revenue = data['sales']['sales_amount'].sum()
                st.metric("Total Revenue", f"€{total_revenue:,.0f}")
        
        with col4:
            if 'sales' in data:
                transaction_count = len(data['sales'])
                st.metric("Transactions", f"{transaction_count:,}")
        
        # Executive KPIs Chart
        if 'kpis' in data:
            st.subheader("Revenue by Customer Segment")
            fig, ax = plt.subplots(figsize=(10, 6))
            
            df_kpis = data['kpis']
            segments = df_kpis['customer_segment'].fillna('Unknown')
            sales = df_kpis['total_sales']
            
            bars = ax.bar(segments, sales, color=['#2E8B57', '#4682B4', '#FF6347'])
            ax.set_title('Revenue by Customer Segment', fontsize=16, fontweight='bold')
            ax.set_ylabel('Revenue (€)')
            ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'€{x:,.0f}'))
            
            # Add value labels
            for bar, value in zip(bars, sales):
                height = bar.get_height()
                ax.text(bar.get_x() + bar.get_width()/2., height + height*0.01,
                       f'€{value:,.0f}', ha='center', va='bottom', fontweight='bold')
            
            st.pyplot(fig)
    
    with tab2:
        st.header("Customer Analytics")
        
        if 'customers' in data:
            df_customers = data['customers']
            
            col1, col2 = st.columns(2)
            
            with col1:
                if 'country' in df_customers.columns:
                    st.subheader("Top Markets")
                    top_countries = df_customers['country'].value_counts().head(10)
                    
                    fig, ax = plt.subplots(figsize=(8, 6))
                    bars = ax.bar(top_countries.index, top_countries.values, color='#4682B4')
                    ax.set_title('Customer Distribution by Country')
                    ax.set_ylabel('Customer Count')
                    plt.xticks(rotation=45)
                    
                    # Add value labels
                    for bar in bars:
                        height = bar.get_height()
                        ax.text(bar.get_x() + bar.get_width()/2., height + height*0.01,
                               f'{int(height):,}', ha='center', va='bottom')
                    
                    st.pyplot(fig)
            
            with col2:
                if 'gender' in df_customers.columns:
                    st.subheader("Customer Demographics")
                    gender_dist = df_customers['gender'].value_counts()
                    
                    fig, ax = plt.subplots(figsize=(6, 6))
                    ax.pie(gender_dist.values, labels=gender_dist.index, autopct='%1.1f%%', startangle=90)
                    ax.set_title('Gender Distribution')
                    st.pyplot(fig)
    
    with tab3:
        st.header("Product Performance")
        
        if 'products' in data:
            df_products = data['products']
            
            if 'category' in df_products.columns:
                st.subheader("Product Categories")
                category_dist = df_products['category'].value_counts()
                
                fig, ax = plt.subplots(figsize=(10, 6))
                bars = ax.bar(category_dist.index, category_dist.values, color='#FF6347')
                ax.set_title('Products by Category')
                ax.set_ylabel('Product Count')
                plt.xticks(rotation=45)
                
                # Add value labels
                for bar in bars:
                    height = bar.get_height()
                    ax.text(bar.get_x() + bar.get_width()/2., height + height*0.01,
                           f'{int(height)}', ha='center', va='bottom')
                
                st.pyplot(fig)
    
    with tab4:
        st.header("Revenue Analysis")
        
        if 'sales' in data and 'sales_amount' in data['sales'].columns:
            df_sales = data['sales']
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.subheader("Transaction Value Distribution")
                fig, ax = plt.subplots(figsize=(8, 6))
                ax.hist(df_sales['sales_amount'], bins=30, alpha=0.7, color='#2E8B57', edgecolor='black')
                ax.set_title('Transaction Amount Distribution')
                ax.set_xlabel('Transaction Amount (€)')
                ax.set_ylabel('Frequency')
                ax.xaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'€{x:,.0f}'))
                st.pyplot(fig)
            
            with col2:
                st.subheader("Revenue Metrics")
                avg_transaction = df_sales['sales_amount'].mean()
                max_transaction = df_sales['sales_amount'].max()
                min_transaction = df_sales['sales_amount'].min()
                
                st.metric("Average Transaction", f"€{avg_transaction:.2f}")
                st.metric("Highest Transaction", f"€{max_transaction:.2f}")
                st.metric("Lowest Transaction", f"€{min_transaction:.2f}")
    
    # Footer
    st.markdown("---")
    st.markdown(f"**Data Source:** Pipeline Run {run_id} | **Last Updated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

if __name__ == "__main__":
    main()