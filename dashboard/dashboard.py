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

############################################

latest_year = all_df["order_purchase_timestamp"].dt.year.max()


latest_year_orders = all_df[all_df["order_purchase_timestamp"].dt.year == latest_year]
latest_year = int(all_df["order_purchase_timestamp"].dt.year.max())

start_date = pd.to_datetime(f"{latest_year}-01-01")
end_date = pd.to_datetime(f"{latest_year}-12-31")
selected_date_range = st.date_input(
    "Select Date Range",
    value=(start_date, end_date),
    min_value=start_date,
    max_value=end_date,
)

latest_year_orders["order_purchase_date"] = latest_year_orders[
    "order_purchase_timestamp"
].dt.date

filtered_orders = latest_year_orders[
    (latest_year_orders["order_purchase_date"] >= selected_date_range[0])
    & (latest_year_orders["order_purchase_date"] <= selected_date_range[1])
]

orders_per_day = filtered_orders.groupby(
    filtered_orders["order_purchase_date"]
).size()

# display the bar chart
st.title(f"Number of Orders in {latest_year}")
st.bar_chart(orders_per_day, height=400)


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

# Menampilkan rating
rating_counts = all_df["review_score"].value_counts().sort_index()
percentage_ratings = (rating_counts / rating_counts.sum()) * 100
percentage_ratings.index = percentage_ratings.index.astype(int)
labels = [f"{rating} star" for rating in percentage_ratings.index]

# Plot
fig, ax = plt.subplots(figsize=(8, 6))
ax.pie(percentage_ratings, labels=labels, autopct="%1.1f%%", startangle=140)
ax.set_title("Percentage of Review Ratings")
ax.axis("equal")

# Tampilkan di Streamlit
st.pyplot(fig)