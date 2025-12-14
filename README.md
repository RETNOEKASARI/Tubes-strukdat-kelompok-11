# Deskripsi Aplikasi
Proyek MARS Music Player adalah sebuah aplikasi pemutar musik desktop standalone yang dikembangkan menggunakan bahasa pemrograman Python dengan antarmuka grafis (GUI) yang dibangun menggunakan toolkit Tkinter. Aplikasi ini dirancang untuk mendemonstrasikan implementasi fundamental dari konsep Struktur Data tingkat lanjut, terutama Doubly Linked List, dalam skenario aplikasi nyata (pengelolaan antrian pemutaran/playlist). Selain itu, sistem ini menerapkan manajemen otentikasi sederhana untuk memisahkan hak akses antara Administrator dan Pengguna. Kemudian MARS ini singkatan dari Music Ariba Retno dan Shindy) di ambil dari para pembuat aplikasi tersebut


## Fitur Dan Implementasi Struktur Data
## 1. Sistem Otentikasi dan Kontrol AksesAutentikasi Berjenjang
Menyediakan mode login terpisah untuk Administrator dan Pengguna Biasa (User).Kontrol Akses Terperinci:User: Memiliki hak akses terbatas, seperti memutar lagu, membuat playlist baru, dan melakukan pencarian.Admin: Memegang hak akses penuh (super-user), termasuk semua fitur user ditambah fitur manajemen data (menambah, menghapus, dan mengelola lagu/user).
## 2. Manajemen Lagu & Library (Fungsi Admin)Pemuatan Otomatis (Auto-Load Lagu)
Sistem secara otomatis memindai dan mengimpor file audio (MP3/WAV) dari folder music lokal saat aplikasi dimulai, memudahkan inisialisasi library.Import Manual: Admin dapat menambahkan koleksi lagu baru, baik itu file individual maupun seluruh folder yang berisi banyak lagu.Manajemen Library: Admin memiliki kemampuan untuk menghapus data lagu dari library utama.
## 3. Implementasi Struktur DataDoubly Linked List (DLL) untuk Playlist
Struktur data utama yang digunakan untuk mengelola antrian lagu (Playlist/Queue). Setiap Node dalam DLL merepresentasikan satu objek lagu.Keunggulan DLL: Memungkinkan operasi "Next" (maju ke lagu berikutnya) dan "Previous" (mundur ke lagu sebelumnya) dengan kompleksitas waktu yang efisien. Pencarian Efisien: Mengintegrasikan fitur pencarian yang melakukan iterasi cepat melalui atribut Judul dan Artis, sehingga pengguna dapat menemukan lagu dalam library dengan mudah.


## Cara Menjalankan Aplikasi
## Persyaratan
Untuk menjalankan MARS Music Player, pastikan lingkungan pengembangan Anda memenuhi kriteria berikut:
## 1. Python 3.x: (Direkomendasikan versi terbaru untuk stabilitas).
## 2. Tkinter: (Perlu untuk antarmuka GUI, umumnya sudah terpasang bersama instalasi standar Python).
## 3. Pygame Library: Digunakan khusus untuk modul mixer yang menangani pemutaran audio (playback) secara cross-platform.
## 4. Mutagen Library: Digunakan untuk membaca dan mengekstrak metadata dari file audio (misalnya durasi lagu, judul, dan artis).


## Instalasi
Buka terminal lalu jalankan perintah ini
```bash
pip install pygame mutagen

Eksekusi program
Setelah dependensi terinstal dan file audio (.mp3 atau .wav) sudah dimasukkan ke dalam folder music/, jalankan aplikasi:
```bash
python MARS.py
