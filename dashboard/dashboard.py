import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st
from babel.numbers import format_currency
sns.set(style='dark')

all_df = pd.read_csv("main_data.csv")

all_df["order_purchase_timestamp"] = pd.to_datetime(all_df["order_purchase_timestamp"])
all_df["order_delivered_customer_date"] = pd.to_datetime(all_df["order_delivered_customer_date"])

st.set_page_config(page_title="Sales Dashboard", layout="wide")

#############################################
def create_monthly_orders_df(df):
    monthly_orders_df = df.resample(rule='D', on='order_purchase_timestamp').agg({
    "order_id": "nunique",
    "price": "sum"
    })
    monthly_orders_df.index = monthly_orders_df.index.strftime('%B %Y')
    monthly_orders_df = monthly_orders_df.reset_index()
    monthly_orders_df.rename(columns={
        "order_id": "order_count",
        "price": "revenue"
    }, inplace=True)
    return monthly_orders_df

def create_sum_order_items_df(df):
    sum_order_items_df = df.groupby('product_category_name').size().reset_index(name='count')
    return sum_order_items_df

monthly_orders_df = create_monthly_orders_df(all_df)
sum_order_items_df = create_sum_order_items_df(all_df)

st.header('Dicoding E-Commerce Dashboard :sparkles:')

st.subheader('monthly Orders')
 
col1, col2 = st.columns(2)

with col1:
    st.markdown("---")
    total_orders = monthly_orders_df.order_count.sum()
    st.metric("Total orders", value=total_orders)
    st.markdown("---")

with col2:
    st.markdown("---")
    total_revenue = format_currency(monthly_orders_df.revenue.sum(), "AUD", locale='es_CO')
    st.metric("Total Revenue", value=total_revenue)
    st.markdown("---")
 
min_date = all_df["order_purchase_timestamp"].min()
max_date = all_df["order_purchase_timestamp"].max()

start_date, end_date = st.date_input(
        label='Rentang Waktu',min_value=min_date,
        max_value=max_date,
        value=[min_date, max_date]
    )

main_df = all_df[(all_df["order_purchase_timestamp"] >= str(start_date)) & 
                (all_df["order_purchase_timestamp"] <= str(end_date))]

plt.figure(figsize=(10, 5)) 
plt.plot(monthly_orders_df["order_purchase_timestamp"], monthly_orders_df["order_count"], marker='o', linewidth=2, color="#72BCD4") 
plt.title("Number of Orders per Month", loc="center", fontsize=20) 
plt.xticks(fontsize=10, rotation=90) 
plt.yticks(fontsize=10) 

# Menampilkan plot menggunakan st.pyplot()
st.pyplot(plt)

##########################

st.subheader("Best & Worst Selling Product")
    
fig, ax = plt.subplots(nrows=1, ncols=2, figsize=(35, 15))
    
colors = ["#90CAF9", "#D3D3D3", "#D3D3D3", "#D3D3D3", "#D3D3D3"]

sns.barplot(x="count", y="product_category_name", data=sum_order_items_df.sort_values(by="count", ascending=False).head(5), palette=colors, ax=ax[0])
ax[0].set_ylabel(None)
ax[0].set_xlabel("Number of Sales", fontsize=30)
ax[0].set_title("Best Performing Product", loc="center", fontsize=50)
ax[0].tick_params(axis='y', labelsize=35)
ax[0].tick_params(axis='x', labelsize=30)

    
sns.barplot(x="count", y="product_category_name", data=sum_order_items_df.sort_values(by="count", ascending=True).head(5), palette=colors, ax=ax[1])
ax[1].set_ylabel(None)
ax[1].set_xlabel("Number of Sales", fontsize=30)
ax[1].invert_xaxis()
ax[1].yaxis.set_label_position("right")
ax[1].yaxis.tick_right()
ax[1].set_title("Worst Performing Product", loc="center", fontsize=50)
ax[1].tick_params(axis='y', labelsize=35)
ax[1].tick_params(axis='x', labelsize=30)
    
st.pyplot(fig)