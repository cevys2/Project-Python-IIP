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
    menu = ["Inventaris", "Penjualan", "Laporan"]
    choice = st.sidebar.selectbox("Menu", menu)

    # Threshold for restocking
    restock_threshold = 10

    if choice == "Inventaris":
        st.title("Manajemen Inventaris")
        
        # Display Inventory Table
        inventory = data[["product_id", "product_name", "quantity_y", "price"]]
        inventory.columns = ["ID Produk", "Nama Produk", "Stok", "Harga"]
        st.dataframe(inventory)

        # Check for low stock
        st.subheader("Pemeriksaan Stok Rendah")
        low_stock = data[data["quantity_y"] <= restock_threshold]
        if not low_stock.empty:
            st.warning("Beberapa produk memiliki stok rendah:")
            st.dataframe(low_stock[["product_id", "product_name", "quantity_y"]])

            # Display supplier info for low stock products
            for _, row in low_stock.iterrows():
                supplier_info = suppliers[suppliers["product_id"] == row["product_id"]]
                if not supplier_info.empty:
                    st.write(f"Produk: {row['product_name']} (ID: {row['product_id']})")
                    st.write(f"Supplier: {supplier_info['supplier_name'].values[0]} - Kontak: {supplier_info['contact'].values[0]}")

        # Add or Reduce Stock
        st.subheader("Perbarui Stok")
        product_id = st.selectbox("Pilih Produk", inventory["ID Produk"].unique())
        update_type = st.radio("Tipe Pembaruan", ["Tambah", "Kurangi"])
        amount = st.number_input("Jumlah", min_value=1, step=1)

        if st.button("Perbarui Stok"):
            if update_type == "Tambah":
                data.loc[data["product_id"] == product_id, "quantity_y"] += amount
            else:
                data.loc[data["product_id"] == product_id, "quantity_y"] -= amount
            st.success("Stok berhasil diperbarui!")

    elif choice == "Penjualan":
        st.title("Sistem Penjualan")

        # Sales Form
        st.subheader("Tambah Penjualan Baru")
        product_id = st.selectbox("Pilih Produk", data["product_id"].unique())
        quantity = st.number_input("Jumlah", min_value=1, step=1)

        if st.button("Tambah Penjualan"):
            available_stock = data.loc[data["product_id"] == product_id, "quantity_y"].values[0]
            if quantity > available_stock:
                st.error("Stok tidak mencukupi untuk penjualan ini.")
            else:
                price_per_unit = data.loc[data["product_id"] == product_id, "price_per_unit"].values[0]
                total_price = price_per_unit * quantity
                current_time = pd.Timestamp.now()

                # Check for duplicate entry
                duplicate_check = data[(data["product_id"] == product_id) &
                                       (data["quantity_x"] == quantity) &
                                       (data["order_date"] == current_time)]

                if not duplicate_check.empty:
                    st.error("Transaksi ini sudah tercatat sebelumnya.")
                else:
                    # Reduce stock
                    data.loc[data["product_id"] == product_id, "quantity_y"] -= quantity

                    # Check if stock falls below threshold after sale
                    new_stock = data.loc[data["product_id"] == product_id, "quantity_y"].values[0]
                    if new_stock <= restock_threshold:
                        supplier_info = suppliers[suppliers["product_id"] == product_id]
                        if not supplier_info.empty:
                            st.warning(f"Stok untuk produk {product_id} rendah. Hubungi {supplier_info['supplier_name'].values[0]} di {supplier_info['contact'].values[0]} untuk restock.")

                    # Add sale record
                    new_sale = {
                        "sales_id": len(data) + 1,
                        "order_id": len(data) + 1,
                        "product_id": product_id,
                        "price_per_unit": price_per_unit,
                        "quantity_x": quantity,
                        "total_price": total_price,
                        "order_date": current_time,
                    }
                    data = data.append(new_sale, ignore_index=True)
                    st.success("Penjualan berhasil ditambahkan dan stok diperbarui!")

    elif choice == "Laporan":
        st.title("Laporan Penjualan & Inventaris")

        # Sales Over Time
        st.subheader("Grafik Penjualan")
        data["order_date"] = pd.to_datetime(data["order_date"])
        sales_trend = data.groupby(data["order_date"].dt.to_period("M")).sum()

        # Line Chart
        st.subheader("Line Chart: Tren Penjualan Bulanan")
        fig, ax = plt.subplots()
        ax.plot(sales_trend.index.to_timestamp(), sales_trend["total_price"], marker='o', label="Total Penjualan")
        ax.set_title("Tren Penjualan")
        ax.set_xlabel("Bulan")
        ax.set_ylabel("Total Penjualan")
        ax.legend()
        st.pyplot(fig)

        # Bar Chart
        st.subheader("Bar Chart: Penjualan per Produk")
        sales_per_product = data.groupby("product_name")["total_price"].sum()
        fig, ax = plt.subplots()
        sales_per_product.plot(kind="bar", ax=ax, color="skyblue")
        ax.set_title("Penjualan per Produk")
        ax.set_ylabel("Total Penjualan")
        st.pyplot(fig)

        # Area Chart
        st.subheader("Area Chart: Akumulasi Penjualan")
        cumulative_sales = sales_trend["total_price"].cumsum()
        fig, ax = plt.subplots()
        ax.fill_between(sales_trend.index.to_timestamp(), cumulative_sales, color="lightgreen", alpha=0.6)
        ax.set_title("Akumulasi Penjualan")
        ax.set_xlabel("Bulan")
        ax.set_ylabel("Total Penjualan")
        st.pyplot(fig)

        # Bubble Chart
        st.subheader("Bubble Chart: Penjualan dan Stok")
        product_sales = data.groupby("product_name").agg({"total_price": "sum", "quantity_y": "sum"})
        fig, ax = plt.subplots()
        scatter = ax.scatter(product_sales["quantity_y"], product_sales["total_price"], 
                             s=product_sales["total_price"] / 10, alpha=0.5, label="Produk")
        ax.set_title("Penjualan vs Stok")
        ax.set_xlabel("Sisa Stok")
        ax.set_ylabel("Total Penjualan")
        st.pyplot(fig)

    # Save updated data back to CSV
    st.sidebar.download_button(
        label="Unduh Data yang Diperbarui",
        data=data.to_csv(index=False).encode('utf-8'),
        file_name="updated_data.csv",
        mime="text/csv",
    )

else:
    st.info("Silakan unggah file CSV untuk memulai.")
