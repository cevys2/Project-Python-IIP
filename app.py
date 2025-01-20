import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

# Set Page Configuration
st.set_page_config(page_title="Dashboard Manajemen", layout="wide")

# Upload Data File
st.sidebar.title("Upload Data")
uploaded_file = st.sidebar.file_uploader("Upload file CSV", type="csv")

if uploaded_file is not None:
    data = pd.read_csv(uploaded_file)

    # Supplier Data
    supplier_data = {
        "product_id": [1, 2, 3],
        "supplier_name": ["Supplier A", "Supplier B", "Supplier C"],
        "contact": ["a@example.com", "b@example.com", "c@example.com"]
    }
    suppliers = pd.DataFrame(supplier_data)

    # Sidebar Navigation
    menu = ["Dashboard", "Inventaris", "Penjualan", "Laporan"]
    choice = st.sidebar.selectbox("Menu", menu)

    # Threshold for restocking
    restock_threshold = 10

    if choice == "Dashboard":
        st.title("Dashboard Manajemen")

        # Display Key Metrics
        total_sales = data["total_price"].sum()
        total_products = data["product_id"].nunique()
        st.metric(label="Total Penjualan", value=f"Rp {total_sales:,.2f}")
        st.metric(label="Jumlah Produk", value=total_products)

    elif choice == "Inventaris":
        st.title("Manajemen Inventaris")
        
        # Display Inventory Table
        inventory_data = data[["product_id", "product_name", "quantity_y", "price"]].drop_duplicates()
        inventory_data.columns = ["ID Produk", "Nama Produk", "Stok", "Harga"]
        st.dataframe(inventory_data)

        # Low Stock Warning
        st.subheader("Peringatan Stok Rendah")
        low_stock = inventory_data[inventory_data["Stok"] <= restock_threshold]
        if not low_stock.empty:
            st.warning("Produk dengan stok rendah:")
            st.dataframe(low_stock)

        # Update Stock
        st.subheader("Perbarui Stok")
        product_id = st.selectbox("Pilih Produk", inventory_data["ID Produk"])
        update_type = st.radio("Tipe Pembaruan", ["Tambah", "Kurangi"])
        quantity = st.number_input("Jumlah", min_value=1, step=1)

        if st.button("Perbarui Stok"):
            if update_type == "Tambah":
                data.loc[data["product_id"] == product_id, "quantity_y"] += quantity
            else:
                data.loc[data["product_id"] == product_id, "quantity_y"] -= quantity
            st.success("Stok berhasil diperbarui!")

    elif choice == "Penjualan":
        st.title("Tambah Penjualan")

        # Display Sales Data
        st.subheader("Data Penjualan")
        sales_data = data[["sales_id", "order_id", "product_id", "quantity_x", "total_price", "order_date"]]
        st.dataframe(sales_data)

        # Sales Form
        product_id = st.selectbox("Pilih Produk", data["product_id"].unique())
        quantity = st.number_input("Jumlah", min_value=1, step=1)

        if st.button("Tambahkan Penjualan"):
            available_stock = data.loc[data["product_id"] == product_id, "quantity_y"].values[0]
            if quantity > available_stock:
                st.error("Stok tidak mencukupi untuk penjualan ini.")
            else:
                price_per_unit = data.loc[data["product_id"] == product_id, "price"].values[0]
                total_price = price_per_unit * quantity

                # Reduce stock
                data.loc[data["product_id"] == product_id, "quantity_y"] -= quantity

                # Add sale record
                new_sale = {
                    "sales_id": len(data) + 1,
                    "order_id": len(data) + 1,
                    "product_id": product_id,
                    "price_per_unit": price_per_unit,
                    "quantity_x": quantity,
                    "total_price": total_price,
                    "order_date": pd.Timestamp.now(),
                }
                data = pd.concat([data, pd.DataFrame([new_sale])], ignore_index=True)
                st.success("Penjualan berhasil ditambahkan!")

    elif choice == "Laporan":
        st.title("Laporan Penjualan & Inventaris")

        # Convert order_date to datetime
        data["order_date"] = pd.to_datetime(data["order_date"], errors='coerce')

        # Filter valid dates
        valid_data = data.dropna(subset=["order_date"])

        # Sales Over Time
        st.subheader("Grafik Penjualan Bulanan")
        sales_trend = valid_data.groupby(valid_data["order_date"].dt.to_period("M")).agg({
            "total_price": "sum",
            "quantity_x": "sum"
        })

        # Line Chart
        fig, ax = plt.subplots()
        sales_trend.index = sales_trend.index.to_timestamp()
        ax.plot(sales_trend.index, sales_trend["total_price"], marker="o", label="Total Penjualan")
        ax.set_title("Tren Penjualan")
        ax.set_xlabel("Bulan")
        ax.set_ylabel("Total Penjualan")
        ax.legend()
        st.pyplot(fig)

        # Bar Chart for Products
        st.subheader("Penjualan per Produk")
        sales_per_product = data.groupby("product_name").agg({
            "total_price": "sum"
        }).sort_values(by="total_price", ascending=False)
        fig, ax = plt.subplots()
        sales_per_product.plot(kind="bar", ax=ax, color="skyblue")
        ax.set_title("Penjualan per Produk")
        ax.set_ylabel("Total Penjualan")
        st.pyplot(fig)

        # Download Updated Data
        st.sidebar.download_button(
            label="Unduh Data yang Diperbarui",
            data=data.to_csv(index=False).encode('utf-8'),
            file_name="updated_data.csv",
            mime="text/csv",
        )

else:
    st.info("Silakan unggah file CSV untuk memulai.")

    
