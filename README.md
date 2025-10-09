# D11
Nama anggota:
- Ahmad Omar Mohammed Maknoon
- Raditya Amoret
- Chris Darren Imanuel
- Raihana Nur Azizah
- Renata Gracia Adli


# SPORTSCOPE TODAY [Aplikasi Web Majalah Olahraga Interaktif]
SPORTSCOPE TODAY adalah platform majalah olahraga digital yang menyajikan berita, hasil pertandingan, serta forum diskusi interaktif bagi para penggemar olahraga. Pengguna dapat mengikuti berita terkini, menandai konten favorit, berdiskusi di forum komunitas.


# Datasets:
berita:https://www.kaggle.com/datasets/hammadjavaid/football-news-articles 

history pertandingan: https://www.kaggle.com/datasets/marcohuiii/english-premier-league-epl-match-data-2000-2025

statistik tim Premier League: https://www.kaggle.com/datasets/flynn28/2025-premier-league-stats-matches-salaries

daftar pemain fifa: https://www.kaggle.com/datasets (we lost the url, can't find it in history either)


# URL PWS
https://ahmad-omar-sportscopetoday.pbp.cs.ui.ac.id/

# Modul untuk setiap anggota: modul 2-6 pakai pageination
## 1. dashboard
Menampilkan ringkasan konten utama seperti:
- Berita olahraga terbaru dari berbagai cabang (football, basketball, dll).
- Highlight hasil pertandingan terbaru
- Notifikasi aktivitas komunitas (misalnya: komentar baru atau thread populer).
Fungsi utamanya: jadi beranda utama pengguna untuk memantau semua update penting secara cepat.

## 2. halaman news 
Berisi daftar berita olahraga yang disusun berdasarkan kategori atau tanggal rilis.
Fitur yang tersedia:
- Filter berita per cabang olahraga.
- Fitur pencarian berita tertentu.
- Tombol Bookmark untuk menyimpan berita favorit.
- Tampilan detail berita.

## 3. halaman bookmark news
Menampilkan kumpulan berita yang telah disimpan (bookmark) oleh pengguna.
- Pengguna bisa melihat, membuka kembali, atau menghapus bookmark.
- Disusun berdasarkan waktu penandaan atau kategori olahraga.
- Dapat disinkronkan dengan akun pengguna untuk akses lintas perangkat.

## 4. halaman bookmark forum
Berisi thread/forum yang telah di-bookmark oleh pengguna.
- Cocok untuk menyimpan diskusi penting seperti analisis pertandingan, gosip transfer, atau prediksi turnamen.
- Pengguna bisa langsung menuju ke posting terakhir yang dibaca sebelumnya.

## 5. history pertandingan
Fitur ini menampilkan rekap hasil pertandingan sebelumnya.
- Data mencakup skor akhir pertandingan.
- Pengguna dapat melihat history by team atau by competition.

## 6. forum general and by category
Ruang diskusi komunitas yang mirip konsepnya dengan Reddit/Quora.

Forum General: tempat untuk membahas topik umum seputar olahraga.
Forum by Category: membahas topik spesifik seperti liga tertentu, klub favorit, atau pemain.

# Role User: 
- Admin : Bisa melakukan create, edit, and delete sports article, bisa edit juga, bookmark, menambah history match dalam page, dan post, comment, and delete forum.
- User: Bisa comment dan post forum, serta bookmark.



