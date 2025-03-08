# submission-analisis-data-ecommerce

Proyek Akhir dari modul "Belajar Analisis Data dengan Python" pada kelas Dicoding program Coding Camp 2025 powered by DBS Foundation 

Feature
--
E-Commerce Public Dataset adalah kumpulan data publik e-commerce Brasil tentang pesanan yang dibuat di Olist Store.
Disini saya melakukan eksplorasi data dan membuat visualisasi data  untuk :
1. Menampilkan perbandingan antara produk yang memberikan kontribusi terbesar dan produk yang kurang memberikan kontribusi terhadap pendapatan E-Commerce
2. Menampilkan pola waktu penjualan (time series) untuk mengetahui periode tertentu dengan penjualan tertinggi
3. Menampilkan perbedaan jumlah penilaian (rating) yang diberikan oleh para customer terhadap E-Commerce

Requirements
--
Proyek ini menggunakan beberapa library yaitu numpy, pandas, matplotlib, babel, seaborn, dan streamlit.\
Pastikan sudah menginstall python dan untuk install library yang dapat dilihat dalam file requirement.txt.

Setup Environment - PowerShell/Terminal
--
  conda create --name my-env python=3.12\
  conda activate my-env\
  pip install streamlit babel\
  pip install -r requirements.txt

Run steamlit app
--
streamlit run dashboard.py
