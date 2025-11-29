# D11
Nama anggota:
- Ahmad Omar Mohammed Maknoon
- Raditya Amoret
- Chris Darren Imanuel
- Raihana Nur Azizah
- Renata Gracia Adli


# SPORTSCOPE TODAY [Aplikasi Web Majalah Olahraga Interaktif]
Sportscope Today adalah platform majalah olahraga digital interaktif yang menyajikan berita terkini, hasil pertandingan, serta forum diskusi bagi para penggemar sepak bola.
Pengguna dapat membaca artikel terbaru, menandai konten favorit, serta berdiskusi di forum komunitas yang dinamis.

Aplikasi ini dirancang untuk menjadi pusat informasi dan interaksi bagi pecinta Liga Premier Inggris maupun penggemar sepak bola secara umum.

# Datasets:
Sumber berita : https://www.kaggle.com/datasets/hammadjavaid/football-news-articles 

Sumber history pertandingan: https://www.kaggle.com/datasets/marcohuiii/english-premier-league-epl-match-data-2000-2025

Statistik tim Premier League: https://www.kaggle.com/datasets/flynn28/2025-premier-league-stats-matches-salaries

Daftar pemain FIFA: https://www.kaggle.com/datasets (we lost the url, can't find it in history either)


# URL PWS
https://ahmad-omar-sportscopetoday.pbp.cs.ui.ac.id/

# Modul untuk setiap anggota: modul 2-6 pakai pageination
## 1. Dashboard
Berfungsi sebagai beranda utama yang menampilkan ringkasan konten penting:
- Halaman utama yang berisikan navigasi ke modul lain

## 2. Halaman News 
Berisi daftar berita olahraga yang disusun berdasarkan kategori atau tanggal rilis.
Fitur yang tersedia:
- Filter berita dari latest ke oldest.
- Fitur pencarian berita tertentu.
- Tombol Bookmark untuk menyimpan berita favorit.
- Tampilan detail berita.

## 3. Halaman Bookmark Forum
Berisi thread/forum yang telah di-bookmark oleh pengguna.
- Cocok untuk menyimpan diskusi penting seperti analisis pertandingan, gosip transfer, atau prediksi turnamen.
- Pengguna bisa langsung menuju ke posting terakhir yang dibaca sebelumnya.

## 4. History Pertandingan
Fitur ini menampilkan rekap hasil pertandingan sebelumnya.
- Data mencakup skor akhir pertandingan.
- Pengguna dapat melihat history by team atau by competition.

## 5. Forum General
Ruang diskusi komunitas yang mirip konsepnya dengan Reddit/Quora.
Forum General: tempat untuk membahas topik umum seputar olahraga.
Forum by Category: membahas topik spesifik seperti liga tertentu, klub favorit, atau pemain.

## 6. Daftar Pemain FIFA
Berisi data dan profil pemain sepak bola dari database FIFA.

Fiturnya dapat menampilkan data pemain lengkap seperti nama, posisi, tim, dan statistik performa. Dapat diurutkan berdasarkan posisi, rating, atau popularitas (likes). Menyediakan fitur pencarian untuk menemukan pemain tertentu. Modul ini juga dapat menampilkan gambar pemain secara otomatis berdasarkan slug yang sesuai.

# Role User: 
Admin
1. Dapat membuat, mengedit, dan menghapus artikel berita olahraga.
2. Dapat menambahkan dan mengedit history match di halaman terkait.
3. Dapat membuat, mengomentari, serta menghapus posting di forum.
4. Dapat melakukan bookmark berita dan forum.
5. Dapat memperbarui dan menambah tim yang berada di beranda utama.
6. Dapat memberikan love pada daftar pemain sepak pola.

User

1. Dapat membuat postingan, mengedit postingan yang dibuat, dan mengomentrasi postingan orang lain di forum.
2. Dapat bookmark berita dan thread forum.
3. Dapat memberikan love pada daftar pemain sepak pola.


