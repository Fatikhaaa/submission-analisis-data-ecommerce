import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st
from babel.numbers import format_currency

sns.set(style='dark')

# Helper function yang digunakan untuk menyiapkan berbagai dataframe
def create_daily_orders_df(df):
    daily_orders_df = df.resample(rule='D', on='order_approved_at').agg({
        "order_id": "nunique",
        "payment_value": "sum"
    })
    daily_orders_df = daily_orders_df.reset_index()
    daily_orders_df.rename(columns={
        "order_id": "order_count",
        "payment_value": "revenue"
    }, inplace=True)
        
    return daily_orders_df

def create_sum_spend_df(df):
    sum_spend_df = df.resample(rule='D', on='order_approved_at').agg({
        "payment_value": "sum"
    })
    sum_spend_df = sum_spend_df.reset_index()
    sum_spend_df.rename(columns={
        "payment_value": "total_spend"
    }, inplace=True)

    return sum_spend_df

def create_sum_order_items_df(df):
    sum_order_items_df = df.groupby("product_category_name_english")["product_id"].count().reset_index()
    sum_order_items_df.rename(columns={
        "product_id": "product_count"
    }, inplace=True)
    sum_order_items_df = sum_order_items_df.sort_values(by='product_count', ascending=False)

    return sum_order_items_df

def review_score_df(df):
    review_scores = df['review_score'].value_counts().sort_values(ascending=False)
    most_common_score = review_scores.idxmax()

    return review_scores, most_common_score

def create_bystate_df(df):
    bystate_df = df.groupby(by="customer_state").customer_id.nunique().reset_index()
    bystate_df.rename(columns={
        "customer_id": "customer_count"
    }, inplace=True)
    most_common_state = bystate_df.loc[bystate_df['customer_count'].idxmax(), 'customer_state']
    bystate_df = bystate_df.sort_values(by='customer_count', ascending=False)

    return bystate_df, most_common_state

def create_bycity_df(df):
    bycity_df = df.groupby(by="customer_city").customer_id.nunique().reset_index()
    bycity_df.rename(columns={
        "customer_id": "total_customer"
    }, inplace=True)
    most_common_city = bycity_df.loc[bycity_df['total_customer'].idxmax(), 'customer_city']
    bycity_df = bycity_df.sort_values(by='total_customer', ascending=False)

    return bycity_df, most_common_city

def create_order_status(df):
    order_status_df = df["order_status"].value_counts().sort_values(ascending=False)
    most_common_status = order_status_df.idxmax()

    return order_status_df, most_common_status

def create_rfm_df(df):
    rfm_df = df.groupby(by="customer_id", as_index=False).agg({
        "order_date": "max", #mengambil tanggal order terakhir
        "order_id": "nunique",
        "total_price": "sum"
    })
    rfm_df.columns = ["customer_id", "max_order_timestamp", "frequency", "monetary"]
    
    rfm_df["max_order_timestamp"] = rfm_df["max_order_timestamp"].dt.date
    recent_date = df["order_date"].dt.date.max()
    rfm_df["recency"] = rfm_df["max_order_timestamp"].apply(lambda x: (recent_date - x).days)
    rfm_df.drop("max_order_timestamp", axis=1, inplace=True)
    
    return rfm_df

# Load Dataset
datetime_columns = ["order_approved_at", "order_delivered_carrier_date", "order_delivered_customer_date", "order_estimated_delivery_date", "order_purchase_timestamp", "shipping_limit_date"]
all_data = pd.read_csv(f"{script_dir}/all_data.csv")
all_data.sort_values(by="order_approved_at", inplace=True)
all_data.reset_index(inplace=True)

for col in datetime_columns:
    all_data[col] = pd.to_datetime(all_data[col])

# Filter data dengan widget input
min_date = all_data["order_approved_at"].min()
max_date = all_data["order_approved_at"].max()

# Sidebar
with st.sidebar:
    #Menambahkan logo
    st.image("logo.png")

    # Mengambil start_date dan end_date  dai date_input
    start_date, end_date = st.date_input(
        label="Masukkan Rentang Waktu",
        min_value=min_date,
        max_value=max_date,
        value=[min_date, max_date]
    )

main_df = all_data[(all_data["order_approved_at"] >= str(start_date)) & 
                 (all_data["order_approved_at"] <= str(end_date))]

# Pastikan kolom "order_date" dan "total_price" tersedia
main_df["order_date"] = main_df["order_approved_at"]
main_df["total_price"] = main_df["payment_value"]

daily_orders_df = create_daily_orders_df(main_df)
sum_spend_df = create_sum_spend_df(main_df)
sum_order_items_df = create_sum_order_items_df(main_df)
review_score, common_score = review_score_df(main_df)
state, most_common_state = create_bystate_df(main_df)
city, most_common_city = create_bycity_df(main_df)
order_status, common_status = create_order_status(main_df)
rfm_df = create_rfm_df(main_df)

# Menambahkan judul Streamlit app
st.title("E-Commerce Public Data Analysis")

# Menambahkan deskripsi Streamlit app
st.write("**Dashboard E-Commerce Public Data Analysis**")

# Total Order
st.subheader("Grafik Total Order")
col1, col2 = st.columns(2)
with col1:
    total_order = daily_orders_df["order_count"].sum()
    formatted_total_order = "{:.2f}".format(total_order)    # Mengonversi angka dengan dua digit di belakang koma
    st.markdown(f"Total Order: **{formatted_total_order}**")

with col2:
    total_revenue = daily_orders_df["revenue"].sum()
    formatted_total_revenue = "{:.2f}".format(total_revenue)
    st.markdown(f"Total Penghasilan: **{formatted_total_revenue}**")

fig, ax = plt.subplots(figsize=(12, 6))
sns.lineplot(
    x=daily_orders_df["order_approved_at"],
    y=daily_orders_df["order_count"],
    marker="o",
    linewidth=2,
    color="#758467"
)
ax.tick_params(axis="x", rotation=45)
ax.tick_params(axis="y", labelsize=15)
ax.set_xlabel("Tanggal Order", fontsize=15)
ax.set_ylabel("Total Order", fontsize=15)
st.pyplot(fig)

# Pendapatan E-commerce
st.subheader("Grafik Pendapatan E-commerce")
col1, col2 = st.columns(2)

with col1:
    total_spend = format_currency(sum_spend_df["total_spend"].sum(), "BRL", locale="pt_BR")
    st.markdown(f"Total Income: **{total_spend}**")

with col2:
    avg_spend = format_currency(sum_spend_df["total_spend"].mean(), "BRL", locale="pt_BR")
    st.markdown(f"Average Income: **{avg_spend}**")

fig, ax = plt.subplots(figsize=(12, 6))
ax.plot(
    sum_spend_df["order_approved_at"],
    sum_spend_df["total_spend"],
    linewidth=1,
    color="#758467"
)
ax.tick_params(axis="x", rotation=15)
ax.tick_params(axis="y", labelsize=15)
st.pyplot(fig)

# Produk yang dipesan
st.subheader("Grafik Penjualan Produk")
col1, col2 = st.columns(2)

with col1:
    total_items = sum_order_items_df["product_count"].sum()
    st.markdown(f"Total Order Item: **{total_items}**")

with col2:
    avg_items = sum_order_items_df["product_count"].mean()
    st.markdown(f"Rata-rata Order Item: **{avg_items}**")

fig, ax = plt.subplots(nrows=1, ncols=2, figsize=(45, 25))

colors = ["#758467", "#CBD5C0", "#CBD5C0", "#CBD5C0", "#CBD5C0"]

sns.barplot(x="product_count", y="product_category_name_english", data=sum_order_items_df.head(5), palette=colors, ax=ax[0])
ax[0].set_ylabel(None)
ax[0].set_xlabel("Jumlah Penjualan", fontsize=80)
ax[0].set_title("Produk paling laris terjual", loc="center", fontsize=90)
ax[0].tick_params(axis ='y', labelsize=55)
ax[0].tick_params(axis ='x', labelsize=50)

sns.barplot(x="product_count", y="product_category_name_english", data=sum_order_items_df.sort_values(by="product_count", ascending=True).head(5), palette=colors, ax=ax[1])
ax[1].set_ylabel(None)
ax[1].set_xlabel("Jumlah Penjualan", fontsize=80)
ax[1].invert_xaxis()
ax[1].yaxis.set_label_position("right")
ax[1].yaxis.tick_right()
ax[1].set_title("Produk paling sedikit terjual", loc="center", fontsize=90)
ax[1].tick_params(axis='y', labelsize=55)
ax[1].tick_params(axis='x', labelsize=50)

st.pyplot(fig)

# Review Score
st.subheader("Review Score")
col1, col2 = st.columns(2)

with col1:
    avg_review_score = review_score.mean()
    st.markdown(f"Rata-rata Skor Penilaian: **{avg_review_score}**")

with col2:
    most_common_review_score = review_score.value_counts().idxmax()
    st.markdown(f"Skor Penilaian paling banyak: **{most_common_review_score}**")

fig, ax = plt.subplots(figsize=(12, 6))

colors = ["#758467", "#CBD5C0", "#CBD5C0", "#CBD5C0", "#CBD5C0"]

sns.barplot(x=review_score.index,
            y=review_score.values,
            order=review_score.index,
            palette=colors)

plt.title("Skor Penilaian pelanggan untuk pelayanan", fontsize=15)
plt.xlabel("Score")
plt.ylabel("Total")
plt.xticks(fontsize=12)
plt.yticks(fontsize=12)

# Menambahkan label di atas setiap bar
for i, v in enumerate(review_score.values):
    ax.text(i, v + 5, str(v), ha='center', va='bottom', fontsize=12, color='black')

st.pyplot(fig)

# Persebaran Customer
st.subheader("Grafik Persebaran Customer Berdasarkan Wilayah")
tab1, tab2 = st.tabs(["State", "City"])

# Fungsi reusable untuk membuat plot
def create_barplot(data, x_column, y_column, title, x_label, y_label):
    fig, ax = plt.subplots(figsize=(12, 6))
    sns.barplot(
        x=x_column,
        y=y_column,
        data=data,
        palette=sns.color_palette("viridis", n_colors=len(data))
    )
    ax.set_title(title, fontsize=15)
    ax.set_xlabel(x_label, fontsize=12)
    ax.set_ylabel(y_label, fontsize=12)
    ax.tick_params(axis="x", labelsize=10, rotation=45)
    ax.tick_params(axis="y", labelsize=10)
    st.pyplot(fig)

# Tab untuk State
with tab1:
    most_common_state = state.customer_state.value_counts().index[0]
    st.markdown(f"State Paling Umum: **{most_common_state}**")
    create_barplot(
        data=state,
        x_column=state.customer_state,
        y_column=state.customer_count,
        title="Jumlah Customer berdasarkan State",
        x_label="State",
        y_label="Jumlah Customer"
    )

# Tab 2: City
with tab2:
    # Filter top 10 cities
    city_top10 = city.nlargest(10, 'total_customer')
    most_common_city = city_top10.loc[city_top10['total_customer'].idxmax(), 'customer_city']
    st.markdown(f"City Paling Umum: **{most_common_city}**")
    create_barplot(
        data=city_top10,
        x_column='customer_city',  # Gunakan string nama kolom
        y_column='total_customer',  # Gunakan string nama kolom
        title="Top 10 Kota dengan Jumlah Customer Terbanyak",
        x_label="City",
        y_label="Jumlah Customer"
    )


# Recency, Frequency, Monetary
st.subheader("Customer Terbaik berdasarkan RFM Analysis")
 
col1, col2, col3 = st.columns(3)
 
with col1:
    avg_recency = round(rfm_df.recency.mean(), 1)
    st.metric("Average Recency (hari)", value=avg_recency)
 
with col2:
    avg_frequency = round(rfm_df.frequency.mean(), 2)
    st.metric("Average Frequency", value=avg_frequency)
 
with col3:
    avg_frequency = format_currency(rfm_df.monetary.mean(), "AUD", locale='es_CO') 
    st.metric("Average Monetary", value=avg_frequency)
 
fig, ax = plt.subplots(nrows=1, ncols=3, figsize=(35, 15))

colors = ["#758467", "#CBD5C0", "#CBD5C0", "#CBD5C0", "#CBD5C0"]
 
sns.barplot(y="recency", x="customer_id", data=rfm_df.sort_values(by="recency", ascending=True).head(5), palette=colors, ax=ax[0])
ax[0].set_ylabel(None)
ax[0].set_xlabel("customer_id", fontsize=30)
ax[0].set_title("Berdasarkan Recency (hari)", loc="center", fontsize=50)
ax[0].tick_params(axis='y', labelsize=30)
ax[0].tick_params(rotation=45, axis='x', labelsize=35)
 
sns.barplot(y="frequency", x="customer_id", data=rfm_df.sort_values(by="frequency", ascending=False).head(5), palette=colors, ax=ax[1])
ax[1].set_ylabel(None)
ax[1].set_xlabel("customer_id", fontsize=30)
ax[1].set_title("Berdasarkan Frequency", loc="center", fontsize=50)
ax[1].tick_params(axis='y', labelsize=30)
ax[1].tick_params(rotation=45, axis='x', labelsize=35)
 
sns.barplot(y="monetary", x="customer_id", data=rfm_df.sort_values(by="monetary", ascending=False).head(5), palette=colors, ax=ax[2])
ax[2].set_ylabel(None)
ax[2].set_xlabel("customer_id", fontsize=30)
ax[2].set_title("Berdasarkan Monetary", loc="center", fontsize=50)
ax[2].tick_params(axis='y', labelsize=30)
ax[2].tick_params(rotation=45, axis='x', labelsize=35)
 
st.pyplot(fig)

# Menambahkan caption
st.caption('Copyright (C) Fatikha Hudi Aryani 2025')
