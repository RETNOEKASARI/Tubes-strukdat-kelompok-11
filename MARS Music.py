import tkinter as tk
from tkinter import filedialog, messagebox, ttk, simpledialog
import os
import random
import json

#library audio
try:
    from pygame import mixer
except ImportError:
    mixer = None
    print("WARNING: Pygame tidak terinstall. Audio tidak akan jalan.")

try:
    from mutagen.mp3 import MP3
except ImportError:
    MP3 = None 

#data dan logika
class Lagu:
    def __init__(self, id_lagu, judul, artis, genre, filename):
        self.id = id_lagu
        self.judul = judul
        self.artis = artis
        self.genre = genre
        self.filename = filename 

class Node:
    def __init__(self, data):
        self.data = data
        self.next = None
        self.prev = None

class DoublyLinkedList:
    def __init__(self):
        self.head = None
        self.tail = None
        self.size = 0

    def append(self, data_lagu):
        node_baru = Node(data_lagu)
        if self.head is None:
            self.head = node_baru
            self.tail = node_baru
        else:
            self.tail.next = node_baru
            node_baru.prev = self.tail
            self.tail = node_baru
        self.size += 1
        return node_baru

    def clear(self):
        self.head = None
        self.tail = None
        self.size = 0

    def get_node_at_index(self, index):
        curr = self.head
        count = 0
        while curr:
            if count == index:
                return curr
            curr = curr.next
            count += 1
        return None

    def get_all_nodes(self):
        nodes = []
        curr = self.head
        while curr:
            nodes.append(curr)
            curr = curr.next
        return nodes

#aplikasi utama
class MarsPlayerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("MARS MUSIC PLAYER") 
        self.root.geometry("1100x700")
        self.root.resizable(True, True) 
        self.root.minsize(900, 600)
        
        # --- TEMA BLACK PINK ---
        self.colors = {
            "bg_main": "#000000",      
            "bg_side": "#050505",      
            "player":  "#111111",      
            "accent":  "#FF1493",      
            "accent2": "#C71585",      
            "text":    "#FFFFFF",
            "card_bg": "#1A1A1A",
            "popup_bg": "#1A1A1A",
            "input_bg": "#333333"
        }
        
        self.artist_colors = {} 
        self.preset_colors = ["#FF69B4", "#DDA0DD", "#C71585", "#DB7093", "#FF1493"]

        self.root.configure(bg=self.colors["bg_main"])

        if mixer: 
            try: mixer.init()
            except: pass

        #Data Backend
        self.library = [] 
        self.playlists = { "Mood Today": [] } 
        self.queue_dll = DoublyLinkedList() 
        self.current_node = None
        self.is_playing = False
        self.is_shuffle = False
        self.active_playlist_name = "Mood Today"
        self.last_id = 0
        self.song_length = 0 
        
        #Data User & Load Database
        self.current_user = None
        self.user_role = None 
        self.target_role = None 
        self.users_db_file = "users.json"
        self.users = {} 
        self.load_users()

        #style
        self.style = ttk.Style()
        self.style.theme_use('clam')
        self.style.configure("Horizontal.TScale", background=self.colors["player"], 
                             troughcolor="#424141", borderwidth=0, 
                             lightcolor=self.colors["accent"], darkcolor=self.colors["accent"])
        self.style.configure("Treeview", background=self.colors["bg_main"], foreground="white", fieldbackground=self.colors["bg_main"], borderwidth=0)
        self.style.map('Treeview', background=[('selected', self.colors["accent"])])
        self.style.configure("Treeview.Heading", background="#333", foreground="white", relief="flat")

        #container frame
        self.frame_landing = tk.Frame(self.root, bg=self.colors["bg_main"]) 
        self.frame_login = tk.Frame(self.root, bg=self.colors["bg_main"])   
        self.frame_home = tk.Frame(self.root, bg=self.colors["bg_main"])    
        self.frame_player = tk.Frame(self.root, bg=self.colors["bg_main"])  

        #setup ui
        self.setup_landing_ui()
        self.setup_login_ui()
        self.setup_home_ui()   
        self.setup_player_ui() 
        
        self.update_slider_loop() 
        
        # pilih folder
        self.root.after(500, self.initial_folder_scan)
        
        self.show_landing_page() 

    #auto load
    def initial_folder_scan(self):
        script_dir = os.path.dirname(os.path.abspath(__file__))
        default_folder = os.path.join(script_dir, "music")
        count = self.scan_and_add_songs(default_folder)
        if count == 0:
            if messagebox.askyesno("Musik Tidak Ditemukan", "Aplikasi tidak menemukan folder 'music' atau kosong.\n\nIngin memilih folder lagu di komputer Anda secara manual?"):
                self.pilih_folder_lagu_manual()

    def pilih_folder_lagu_manual(self):
        folder_selected = filedialog.askdirectory(title="Pilih Folder Berisi Lagu")
        if folder_selected:
            count = self.scan_and_add_songs(folder_selected)
            if count > 0:
                self.show_custom_alert("Berhasil", f"Berhasil memuat {count} lagu dari folder tersebut!")
                if self.active_playlist_name:
                    self.refresh_view(self.active_playlist_name)
            else:
                self.show_custom_alert("Info", "Tidak ada file MP3/WAV di folder tersebut.", is_error=True)

    def scan_and_add_songs(self, folder_path):
        if not os.path.exists(folder_path): return 0
        files = os.listdir(folder_path)
        count = 0
        for f in files:
            if f.lower().endswith(('.mp3', '.wav', '.ogg')):
                full_path = os.path.join(folder_path, f)
                exists = False
                for existing in self.library:
                    if existing.filename == full_path:
                        exists = True
                        break
                
                if not exists:
                    clean_name = os.path.splitext(f)[0]
                    if " - " in clean_name:
                        parts = clean_name.split(" - ")
                        artis_lagu = parts[0]
                        judul_lagu = parts[1]
                    else:
                        judul_lagu = clean_name
                        artis_lagu = "Unknown Artist"

                    self.last_id += 1
                    lagu_baru = Lagu(self.last_id, judul_lagu, artis_lagu, "Pop", full_path)
                    self.library.append(lagu_baru)
                    self.playlists["Mood Today"].append(lagu_baru)
                    count += 1
        return count

    #database user
    def load_users(self):
        if not os.path.exists(self.users_db_file):
            self.users = {} 
            self.save_users()
        else:
            try:
                with open(self.users_db_file, "r") as f:
                    self.users = json.load(f)
            except:
                self.users = {} 

    def save_users(self):
        with open(self.users_db_file, "w") as f:
            json.dump(self.users, f, indent=4)

    #helper
    def get_artist_color(self, artist_name):
        key = artist_name.strip().lower()
        if key not in self.artist_colors:
            self.artist_colors[key] = random.choice(self.preset_colors)
        return self.artist_colors[key]

    def bind_recursive(self, widget, event, func):
        widget.bind(event, func)
        for child in widget.winfo_children():
            self.bind_recursive(child, event, func)

    def create_sidebar_btn(self, parent, text, cmd):
        btn = tk.Button(parent, text=text, bg=self.colors["bg_side"], fg="#E0E0E0", bd=0, padx=10, pady=8, font=("Arial", 10), cursor="hand2", anchor="w", activebackground="#1F1F1F", command=cmd)
        btn.pack(fill="x", padx=10)

    #pop up custom
    def show_custom_alert(self, title, message, is_error=False):
        popup = tk.Toplevel(self.root)
        popup.configure(bg=self.colors["bg_main"])
        popup.overrideredirect(True)
        w, h = 400, 200
        x = self.root.winfo_rootx() + (self.root.winfo_width() // 2) - (w // 2)
        y = self.root.winfo_rooty() + (self.root.winfo_height() // 2) - (h // 2)
        popup.geometry(f"{w}x{h}+{x}+{y}")
        border_col = "red" if is_error else self.colors["accent"]
        frame_border = tk.Frame(popup, bg=border_col, padx=2, pady=2)
        frame_border.pack(fill="both", expand=True)
        frame_inner = tk.Frame(frame_border, bg=self.colors["card_bg"], padx=20, pady=20)
        frame_inner.pack(fill="both", expand=True)
        tk.Label(frame_inner, text=title, font=("Arial", 16, "bold"), fg=border_col, bg=self.colors["card_bg"]).pack(pady=(0, 10))
        tk.Label(frame_inner, text=message, font=("Arial", 11), fg="white", bg=self.colors["card_bg"], wraplength=350).pack(pady=(0, 20))
        tk.Button(frame_inner, text="Tutup", command=popup.destroy, bg=border_col, fg="white", font=("Arial", 10, "bold"), bd=0, padx=20, pady=5, cursor="hand2").pack()
        self.root.wait_window(popup)

    def show_custom_input(self, title, prompt):
        self.popup_input_val = None
        popup = tk.Toplevel(self.root)
        popup.title(title)
        popup.configure(bg=self.colors["popup_bg"])
        popup.overrideredirect(True) 
        w, h = 400, 220
        x = self.root.winfo_rootx() + (self.root.winfo_width() // 2) - (w // 2)
        y = self.root.winfo_rooty() + (self.root.winfo_height() // 2) - (h // 2)
        popup.geometry(f"{w}x{h}+{x}+{y}")
        frame_border = tk.Frame(popup, bg=self.colors["accent"], padx=2, pady=2)
        frame_border.pack(fill="both", expand=True)
        frame_inner = tk.Frame(frame_border, bg=self.colors["card_bg"], padx=20, pady=20)
        frame_inner.pack(fill="both", expand=True)
        tk.Label(frame_inner, text=title, font=("Arial", 14, "bold"), fg=self.colors["accent"], bg=self.colors["popup_bg"]).pack(pady=(20, 10))
        tk.Label(frame_inner, text=prompt, font=("Arial", 10), fg="white", bg=self.colors["popup_bg"]).pack(pady=(0, 10))
        entry = tk.Entry(frame_inner, font=("Arial", 12), bg="#333", fg="white", insertbackground="white", relief="flat", justify="center")
        entry.pack(padx=30, ipady=5, fill="x")
        entry.focus_set()
        btn_frame = tk.Frame(frame_inner, bg=self.colors["popup_bg"])
        btn_frame.pack(pady=20)
        def on_ok():
            self.popup_input_val = entry.get()
            popup.destroy()
        def on_cancel():
            popup.destroy()
        tk.Button(btn_frame, text="OK", command=on_ok, bg=self.colors["accent"], fg="white", font=("Arial", 10, "bold"), bd=0, padx=15, pady=5).pack(side="left", padx=10)
        tk.Button(btn_frame, text="BATAL", command=on_cancel, bg="#444", fg="white", font=("Arial", 10), bd=0, padx=15, pady=5).pack(side="left", padx=10)
        self.root.wait_window(popup)
        return self.popup_input_val

    def show_custom_yesno(self, title, message):
        self.popup_yesno_val = False
        popup = tk.Toplevel(self.root)
        popup.configure(bg=self.colors["bg_main"])
        popup.overrideredirect(True)
        w, h = 380, 180
        x = self.root.winfo_rootx() + (self.root.winfo_width() // 2) - (w // 2)
        y = self.root.winfo_rooty() + (self.root.winfo_height() // 2) - (h // 2)
        popup.geometry(f"{w}x{h}+{x}+{y}")
        border_frame = tk.Frame(popup, bg=self.colors["accent"], padx=2, pady=2)
        border_frame.pack(fill="both", expand=True)
        main_frame = tk.Frame(border_frame, bg=self.colors["popup_bg"])
        main_frame.pack(fill="both", expand=True)
        tk.Label(main_frame, text=title, font=("Arial", 14, "bold"), fg=self.colors["accent"], bg=self.colors["popup_bg"]).pack(pady=(25, 10))
        tk.Label(main_frame, text=message, font=("Arial", 10), fg="white", bg=self.colors["popup_bg"], wraplength=300).pack(pady=(0, 20))
        btn_frame = tk.Frame(main_frame, bg=self.colors["popup_bg"])
        btn_frame.pack()
        def on_yes():
            self.popup_yesno_val = True
            popup.destroy()
        def on_no():
            self.popup_yesno_val = False
            popup.destroy()
        tk.Button(btn_frame, text="YA", command=on_yes, bg=self.colors["accent"], fg="white", font=("Arial", 10, "bold"), bd=0, padx=20, pady=5).pack(side="left", padx=10)
        tk.Button(btn_frame, text="TIDAK", command=on_no, bg="#444", fg="white", font=("Arial", 10), bd=0, padx=20, pady=5).pack(side="left", padx=10)
        self.root.wait_window(popup)
        return self.popup_yesno_val

    #navigasi halaman
    def show_landing_page(self):
        self.frame_home.pack_forget()
        self.frame_player.pack_forget()
        self.frame_login.pack_forget()
        self.frame_landing.pack(fill="both", expand=True)

    def select_login_role(self, role):
        self.target_role = role
        title = "LOGIN ADMINISTRATOR" if role == "admin" else "LOGIN PENGGUNA"
        self.lbl_login_title.config(text=title)
        self.entry_username.delete(0, tk.END)
        self.entry_password.delete(0, tk.END)
        self.frame_landing.pack_forget()
        self.frame_login.pack(fill="both", expand=True)

    def show_home_page(self):
        self.frame_landing.pack_forget()
        self.frame_login.pack_forget()
        self.frame_player.pack_forget()
        self.frame_home.pack(fill="both", expand=True)
        
        if self.user_role == "admin":
            self.btn_admin_panel.place(relx=0.05, rely=0.1, anchor="nw")
            self.lbl_role_status.config(text="Mode: Administrator", fg=self.colors["accent"])
            self.btn_add_manual.pack(pady=5)
            self.btn_add_folder.pack(pady=5)
        else:
            self.btn_admin_panel.place_forget()
            self.lbl_role_status.config(text="Mode: Pengguna", fg="gray")
            self.btn_add_manual.pack_forget()
            self.btn_add_folder.pack_forget()

    def show_player_page(self):
        self.frame_home.pack_forget() 
        self.frame_player.pack(fill="both", expand=True) 
        
        #refresh
        for widget in self.library_container.winfo_children():
            widget.destroy()
        
        self.create_sidebar_btn(self.library_container, "✨  Buat Playlist", self.buat_playlist_baru)
        if self.user_role == "admin":
            self.create_sidebar_btn(self.library_container, "➕  Tambah Lagu (Manual)", self.tambah_lagu_file)
            self.create_sidebar_btn(self.library_container, "📂  Tambah Satu Folder", self.tambah_lagu_folder)

        self.refresh_view("Mood Today") 

    def logout(self):
        self.current_user = None
        self.user_role = None
        self.show_landing_page()

    #landing halaman
    def setup_landing_ui(self):
        box = tk.Frame(self.frame_landing, bg=self.colors["card_bg"], padx=60, pady=60)
        box.place(relx=0.5, rely=0.5, anchor="center")

        tk.Label(box, text="MARS MUSIC", font=("Helvetica", 36, "bold"), fg=self.colors["accent"], bg=self.colors["card_bg"]).pack(pady=(0, 10))
        tk.Label(box, text="Silakan pilih jenis akses:", font=("Arial", 11), fg="gray", bg=self.colors["card_bg"]).pack(pady=(0, 30))

        btn_user = tk.Button(box, text="MASUK SEBAGAI PENGGUNA", command=lambda: self.select_login_role("user"), 
                              bg=self.colors["accent"], fg="white", font=("Arial", 12, "bold"), 
                              bd=0, width=30, pady=12, cursor="hand2")
        btn_user.pack(pady=10)

        btn_admin = tk.Button(box, text="MASUK SEBAGAI ADMIN", command=lambda: self.select_login_role("admin"), 
                              bg="#333", fg="white", font=("Arial", 12, "bold"), 
                              bd=0, width=30, pady=12, cursor="hand2")
        btn_admin.pack(pady=10)

        tk.Label(box, text="Belum punya akun?", font=("Arial", 10), fg="gray", bg=self.colors["card_bg"]).pack(pady=(30, 5))
        btn_reg = tk.Button(box, text="DAFTAR BARU", command=self.proses_register_dialog, 
                            bg=self.colors["card_bg"], fg=self.colors["accent"], font=("Arial", 10, "bold", "underline"), 
                            bd=0, cursor="hand2")
        btn_reg.pack()

    #login dan reset
    def setup_login_ui(self):
        login_box = tk.Frame(self.frame_login, bg=self.colors["card_bg"], padx=50, pady=50)
        login_box.place(relx=0.5, rely=0.5, anchor="center")

        self.lbl_login_title = tk.Label(login_box, text="LOGIN", font=("Helvetica", 24, "bold"), fg=self.colors["accent"], bg=self.colors["card_bg"])
        self.lbl_login_title.pack(pady=(0, 30))

        tk.Label(login_box, text="Username", font=("Arial", 10), fg="gray", bg=self.colors["card_bg"]).pack(anchor="w")
        self.entry_username = tk.Entry(login_box, font=("Arial", 12), bg=self.colors["input_bg"], fg="white", insertbackground="white", relief="flat", width=30)
        self.entry_username.pack(fill="x", pady=(5, 20), ipady=5)

        tk.Label(login_box, text="Password", font=("Arial", 10), fg="gray", bg=self.colors["card_bg"]).pack(anchor="w")
        self.entry_password = tk.Entry(login_box, font=("Arial", 12), bg=self.colors["input_bg"], fg="white", insertbackground="white", relief="flat", show="*", width=30)
        self.entry_password.pack(fill="x", pady=(5, 30), ipady=5)

        btn_login = tk.Button(login_box, text="MASUK", command=self.proses_login, 
                              bg=self.colors["accent"], fg="white", font=("Arial", 12, "bold"), 
                              bd=0, padx=20, pady=10, cursor="hand2")
        btn_login.pack(fill="x", pady=(0, 10))

        btn_back = tk.Button(login_box, text="Kembali", command=self.show_landing_page, 
                             bg="#222", fg="gray", font=("Arial", 10), bd=0, pady=5, cursor="hand2")
        btn_back.pack(fill="x")

        tk.Label(login_box, text="", font=("Arial", 5), bg=self.colors["card_bg"]).pack()
        btn_lupa = tk.Button(login_box, text="Lupa Password?", command=self.proses_lupa_password,
                             bg=self.colors["card_bg"], fg=self.colors["accent"], font=("Arial", 9, "underline"),
                             bd=0, cursor="hand2")
        btn_lupa.pack(side="bottom", pady=10)

    def proses_login(self):
        username = self.entry_username.get()
        password = self.entry_password.get()

        if not username or not password:
            self.show_custom_alert("Gagal", "Isi Username dan Password!", is_error=True)
            return

        if username in self.users:
            stored_pass = self.users[username]["password"]
            real_role = self.users[username]["role"]

            if password == stored_pass:
                if self.target_role == "admin" and real_role != "admin":
                    self.show_custom_alert("Akses Ditolak", "Akun ini bukan Admin!\nSilakan login sebagai Pengguna.", is_error=True)
                    return
                if self.target_role == "user" and real_role == "admin":
                    if not self.show_custom_yesno("Info", "Anda adalah Admin. Tetap login di menu Pengguna?"):
                        return

                self.current_user = username
                self.user_role = real_role
                display_name = self.users[username].get("name", username)
                
                self.lbl_greeting.config(text=f"Halo, {display_name}!") 
                self.show_home_page()
            else:
                self.show_custom_alert("Gagal", "Password salah!", is_error=True)
        else:
            self.show_custom_alert("Gagal", "Username tidak ditemukan.\nSilakan Daftar Baru.", is_error=True)

    def proses_register_dialog(self):
        uname = self.show_custom_input("Daftar", "Buat Username Baru:")
        if not uname: return
        if uname in self.users:
            self.show_custom_alert("Gagal", "Username sudah dipakai!", is_error=True)
            return
        
        pwd = self.show_custom_input("Daftar", "Buat Password:")
        if not pwd: return
        
        is_admin = self.show_custom_yesno("Pilih Peran", "Apakah akun ini untuk ADMIN?\n(Pilih YA untuk Admin, TIDAK untuk User Biasa)")
        role_dipilih = "admin" if is_admin else "user"

        if role_dipilih == "admin":
            jumlah_admin = sum(1 for u in self.users.values() if u["role"] == "admin")
            if jumlah_admin >= 3:
                self.show_custom_alert("Gagal", "Kuota Admin sudah penuh (Max 3).\nSilakan daftar sebagai User biasa.", is_error=True)
                return

        self.users[uname] = {"password": pwd, "role": role_dipilih, "name": uname}
        self.save_users()
        
        jenis = "ADMIN" if role_dipilih == "admin" else "USER"
        self.show_custom_alert("Berhasil", f"Akun {jenis} berhasil dibuat!\nSilakan Login.")

    def proses_lupa_password(self):
        uname = self.show_custom_input("Lupa Password", "Masukkan Username Anda:")
        if not uname: return

        if uname not in self.users:
            self.show_custom_alert("Gagal", "Username tidak ditemukan!", is_error=True)
            return
        
        new_pass = self.show_custom_input("Reset Password", f"Masukkan Password Baru untuk {uname}:")
        if not new_pass: return

        self.users[uname]["password"] = new_pass
        self.save_users()
        self.show_custom_alert("Sukses", "Password berhasil diubah.\nSilakan Login kembali.")

    #panel
    def open_admin_panel(self):
        if self.user_role != "admin": return

        panel = tk.Toplevel(self.root)
        panel.title("Panel Admin")
        panel.configure(bg=self.colors["bg_main"])
        panel.geometry("600x450")
        
        tk.Label(panel, text="MANAJEMEN PENGGUNA", font=("Helvetica", 16, "bold"), fg=self.colors["accent"], bg=self.colors["bg_main"]).pack(pady=15)
        
        list_frame = tk.Frame(panel, bg=self.colors["bg_main"])
        list_frame.pack(fill="both", expand=True, padx=20)

        columns = ("Username", "Password", "Role")
        tree = ttk.Treeview(list_frame, columns=columns, show="headings", height=10)
        tree.heading("Username", text="Username")
        tree.heading("Password", text="Password") 
        tree.heading("Role", text="Role")
        tree.column("Username", width=150)
        tree.column("Password", width=150)
        tree.column("Role", width=100)
        tree.pack(side="left", fill="both", expand=True)
        
        scrollbar = ttk.Scrollbar(list_frame, orient="vertical", command=tree.yview)
        scrollbar.pack(side="right", fill="y")
        tree.configure(yscrollcommand=scrollbar.set)

        def refresh_table():
            for item in tree.get_children():
                tree.delete(item)
            for uname, data in self.users.items():
                tree.insert("", "end", values=(uname, data["password"], data["role"]))
        refresh_table()

        btn_frame = tk.Frame(panel, bg=self.colors["bg_main"])
        btn_frame.pack(pady=20)

        def admin_reset_password():
            selected = tree.selection()
            if not selected: 
                self.show_custom_alert("Pilih User", "Pilih user di tabel dulu!", is_error=True)
                return
            uname = tree.item(selected)['values'][0]
            new_pass = simpledialog.askstring("Reset Password", f"Password Baru untuk {uname}:", parent=panel)
            if new_pass:
                self.users[uname]["password"] = new_pass
                self.save_users()
                refresh_table()
                messagebox.showinfo("Sukses", "Password diubah.", parent=panel)

        def delete_user():
            selected = tree.selection()
            if not selected: return
            uname = tree.item(selected)['values'][0]
            if uname == self.current_user:
                messagebox.showerror("Error", "Tidak bisa hapus akun sendiri!", parent=panel)
                return
            if messagebox.askyesno("Hapus", f"Hapus user {uname}?", parent=panel):
                del self.users[uname]
                self.save_users()
                refresh_table()

        tk.Button(btn_frame, text="RESET PASSWORD", command=admin_reset_password, bg=self.colors["accent"], fg="white", width=20, pady=5, bd=0).pack(side="left", padx=10)
        tk.Button(btn_frame, text="HAPUS USER", command=delete_user, bg="red", fg="white", width=20, pady=5, bd=0).pack(side="left", padx=10)

    def change_own_password(self):
        new_pass = self.show_custom_input("Ganti Password", "Masukkan Password Baru:")
        if new_pass:
            self.users[self.current_user]["password"] = new_pass
            self.save_users()
            self.show_custom_alert("Sukses", "Password berhasil diganti!")

    #dashboard home
    def setup_home_ui(self):
        header = tk.Frame(self.frame_home, height=300, bg=self.colors["accent"])
        header.pack(fill="x", side="top")
        header.pack_propagate(False)

        cv = tk.Canvas(header, bg=self.colors["accent"], highlightthickness=0)
        cv.place(relwidth=1, relheight=1)
        cv.create_oval(-100, -100, 400, 400, fill=self.colors["accent2"], outline="")
        cv.create_text(50, 150, text="MARS MUSIC", fill="white", font=("Helvetica", 60, "bold"), anchor="w")
        cv.create_text(55, 210, text="Dengarkan musik sesuai suasana hatimu.", fill="#FFE4E1", font=("Arial", 14), anchor="w")

        self.btn_admin_panel = tk.Button(header, text="🔧 ADMIN PANEL", command=self.open_admin_panel, 
                               bg="#333", fg="white", bd=0, font=("Arial", 10, "bold"), cursor="hand2")
        
        btn_chg_pass = tk.Button(header, text="GANTI PASSWORD", command=self.change_own_password, 
                               bg=self.colors["accent2"], fg="white", bd=0, font=("Arial", 10, "bold"), cursor="hand2")
        btn_chg_pass.place(relx=0.85, rely=0.1, anchor="ne")

        btn_logout = tk.Button(header, text="LOGOUT", command=self.logout, 
                               bg="red", fg="white", bd=0, font=("Arial", 10, "bold"), cursor="hand2")
        btn_logout.place(relx=0.95, rely=0.1, anchor="ne")

        content = tk.Frame(self.frame_home, bg=self.colors["bg_main"])
        content.pack(fill="both", expand=True)

        center = tk.Frame(content, bg=self.colors["bg_main"])
        center.place(relx=0.5, rely=0.4, anchor="center")

        self.lbl_greeting = tk.Label(center, text="Halo, Tamu!", font=("Arial", 35, "bold"), fg="white", bg=self.colors["bg_main"])
        self.lbl_greeting.pack(pady=5)
        
        self.lbl_role_status = tk.Label(center, text="Mode: ...", font=("Arial", 12), fg="gray", bg=self.colors["bg_main"])
        self.lbl_role_status.pack(pady=(0, 30))

        btn_start = tk.Button(center, text="▶  BUKA PLAYLIST", command=self.show_player_page, 
                              bg=self.colors["accent"], fg="white", font=("Arial", 14, "bold"), 
                              bd=0, padx=40, pady=15, cursor="hand2")
        btn_start.pack(pady=10)

        #tambah lagu
        self.btn_add_manual = tk.Button(center, text="➕  Tambah Lagu (Manual)", command=self.tambah_lagu_file, 
                            bg="#333", fg="white", font=("Arial", 11), 
                            bd=0, padx=30, pady=5, cursor="hand2")

        self.btn_add_folder = tk.Button(center, text="📂  Tambah Satu Folder", command=self.tambah_lagu_folder, 
                            bg="#333", fg="white", font=("Arial", 11), 
                            bd=0, padx=30, pady=5, cursor="hand2")

    #player musk
    def setup_player_ui(self):
        sidebar = tk.Frame(self.frame_player, bg=self.colors["bg_side"], width=220)
        sidebar.pack(side="left", fill="y")
        sidebar.pack_propagate(False) 
        
        btn_back = tk.Button(sidebar, text="← Kembali", command=self.show_home_page, 
                             bg=self.colors["bg_side"], fg="gray", bd=0, cursor="hand2", anchor="w", font=("Arial", 9))
        btn_back.pack(fill="x", padx=20, pady=(15, 0))

        tk.Label(sidebar, text="MARS MUSIC", bg=self.colors["bg_side"], fg=self.colors["accent"], font=("Helvetica", 20, "bold")).pack(pady=(10, 30), padx=20, anchor="w")
        
        self.create_sidebar_btn(sidebar, "🏠  Mood Today", self.go_to_mood_today)
        
        tk.Label(sidebar, text="Pencarian", bg=self.colors["bg_side"], fg="grey", font=("Arial", 9, "bold")).pack(anchor="w", padx=25, pady=(20, 5))
        self.entry_search = tk.Entry(sidebar, bg="#242424", fg="white", bd=0, font=("Arial", 10), insertbackground=self.colors["accent"])
        self.entry_search.pack(fill="x", padx=20, ipady=6)
        self.entry_search.bind("<KeyRelease>", self.aksi_cari_lagu)

        tk.Label(sidebar, text="LIBRARY", bg=self.colors["bg_side"], fg="grey", font=("Arial", 9, "bold")).pack(anchor="w", padx=25, pady=(20, 10))
        
        #container tombol dinamis
        self.library_container = tk.Frame(sidebar, bg=self.colors["bg_side"])
        self.library_container.pack(fill="both")

        tk.Label(sidebar, text="PLAYLIST KAMU", bg=self.colors["bg_side"], fg="grey", font=("Arial", 9, "bold")).pack(anchor="w", padx=25, pady=(20, 10))
        self.playlist_sidebar_container = tk.Frame(sidebar, bg=self.colors["bg_side"])
        self.playlist_sidebar_container.pack(fill="both", padx=10)

        #konten utama
        self.main_container = tk.Frame(self.frame_player, bg=self.colors["bg_main"])
        self.main_container.pack(side="top", fill="both", expand=True)

        self.header_frame_container = tk.Frame(self.main_container, height=200, bg=self.colors["accent"])
        self.header_frame_container.pack(fill="x", side="top")
        self.header_frame_container.pack_propagate(False)

        self.header_canvas = tk.Canvas(self.header_frame_container, bg=self.colors["accent"], height=200, highlightthickness=0)
        self.header_canvas.place(x=0, y=0, relwidth=1, relheight=1)

        self.canvas_scroll = tk.Canvas(self.main_container, bg=self.colors["bg_main"], highlightthickness=0)
        self.scrollbar = ttk.Scrollbar(self.main_container, orient="vertical", command=self.canvas_scroll.yview)
        
        self.cards_frame = tk.Frame(self.canvas_scroll, bg=self.colors["bg_main"])
        self.cards_frame.bind("<Configure>", lambda e: self.canvas_scroll.configure(scrollregion=self.canvas_scroll.bbox("all")))
        self.window_id = self.canvas_scroll.create_window((0, 0), window=self.cards_frame, anchor="nw")
        self.canvas_scroll.bind('<Configure>', lambda e: self.canvas_scroll.itemconfig(self.window_id, width=e.width))

        self.canvas_scroll.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")
        self.canvas_scroll.configure(yscrollcommand=self.scrollbar.set)

        #footer
        control_bar = tk.Frame(self.frame_player, bg=self.colors["player"], height=90)
        control_bar.pack(side="bottom", fill="x")
        control_bar.pack_propagate(False)

        self.slider = ttk.Scale(control_bar, from_=0, to=100, orient="horizontal", style="Horizontal.TScale", command=self.geser_slider)
        self.slider.pack(side="top", fill="x")

        player_content = tk.Frame(control_bar, bg=self.colors["player"])
        player_content.pack(fill="both", expand=True, padx=20)
        player_content.columnconfigure(0, weight=1)
        player_content.columnconfigure(1, weight=1)
        player_content.columnconfigure(2, weight=1)

        left_frame = tk.Frame(player_content, bg=self.colors["player"])
        left_frame.grid(row=0, column=0, sticky="w")
        self.lbl_now_playing = tk.Label(left_frame, text="Siap Memutar", bg=self.colors["player"], fg="white", font=("Arial", 11, "bold"), anchor="w")
        self.lbl_now_playing.pack(anchor="w")
        self.lbl_time_status = tk.Label(left_frame, text="--:-- / --:--", bg=self.colors["player"], fg="#B3B3B3", font=("Arial", 9), anchor="w")
        self.lbl_time_status.pack(anchor="w")

        center_frame = tk.Frame(player_content, bg=self.colors["player"])
        center_frame.grid(row=0, column=1)
        
        self.btn_shuffle = tk.Button(center_frame, text="🔀", font=("Arial", 12), bg=self.colors["player"], fg="#B3B3B3", bd=0, cursor="hand2", command=self.toggle_shuffle)
        self.btn_shuffle.pack(side="left", padx=10)
        
        tk.Button(center_frame, text="⏮", font=("Arial", 18), bg=self.colors["player"], fg="white", bd=0, cursor="hand2", command=self.prev_song).pack(side="left", padx=10)
        
        self.play_canvas = tk.Canvas(center_frame, width=54, height=54, bg=self.colors["player"], highlightthickness=0, cursor="hand2")
        self.play_canvas.pack(side="left", padx=15)
        self.play_circle = self.play_canvas.create_oval(2, 2, 52, 52, fill=self.colors["accent"], outline="")
        self.play_icon_tag = self.play_canvas.create_polygon(20, 16, 20, 38, 38, 27, fill="white", tags="icon")
        self.bind_recursive(self.play_canvas, "<Button-1>", lambda e: self.toggle_play())

        tk.Button(center_frame, text="⏭", font=("Arial", 18), bg=self.colors["player"], fg="white", bd=0, cursor="hand2", command=self.next_song).pack(side="left", padx=10)

        right_frame = tk.Frame(player_content, bg=self.colors["player"])
        right_frame.grid(row=0, column=2, sticky="e")
        tk.Button(right_frame, text="🗑️", bg=self.colors["player"], fg=self.colors["accent"], bd=0, font=("Arial", 16), cursor="hand2", command=self.hapus_lagu_terpilih).pack(side="left", padx=10)
        tk.Button(right_frame, text="➜ Pindah", bg=self.colors["player"], fg="white", bd=0, font=("Arial", 10), cursor="hand2", command=self.pindah_playlist_dialog).pack(side="left", padx=10)

    #fungsi aksi lagu pencarian
    def aksi_cari_lagu(self, event):
        keyword = self.entry_search.get().lower()
        sumber = self.playlists[self.active_playlist_name]
        hasil_cari = [l for l in sumber if keyword in l.judul.lower() or keyword in l.artis.lower()]
        for widget in self.cards_frame.winfo_children(): widget.destroy()
        row, col, max_cols = 0, 0, 4
        for index, lagu in enumerate(hasil_cari):
            card = tk.Frame(self.cards_frame, bg="#333333", width=190, height=250)
            card.grid(row=row, column=col, padx=10, pady=15)
            card.pack_propagate(False)
            artist_color = self.get_artist_color(lagu.artis)
            try: idx_asli = sumber.index(lagu)
            except ValueError: continue
            click_cmd = lambda e, idx=idx_asli: self.play_from_index(idx)
            cover = tk.Frame(card, bg=artist_color, height=180)
            cover.pack(fill="x")
            lbl_icon = tk.Label(cover, text="🔍", font=("Arial", 40), bg=artist_color, fg="white")
            lbl_icon.place(relx=0.5, rely=0.5, anchor="center")
            lbl_title = tk.Label(card, text=lagu.judul, font=("Arial", 11, "bold"), bg="#333333", fg="white")
            lbl_title.pack(pady=(10,0))
            self.bind_recursive(card, "<Button-1>", click_cmd)
            col += 1
            if col >= max_cols: col=0; row+=1

    #fungsi lain player
    def go_to_mood_today(self):
        self.active_playlist_name = "Mood Today"
        self.refresh_view("Mood Today")
        self.refresh_sidebar_playlists()

    def tambah_lagu_file(self):
        """Manual Add Single File (Admin)"""
        filepath = filedialog.askopenfilename(filetypes=[("Audio Files", "*.mp3 *.wav")])
        if not filepath: return
        filename = os.path.basename(filepath)
        judul = self.show_custom_input("Tambah Lagu", f"Judul Lagu ({filename}):")
        if not judul: judul = filename
        artis = self.show_custom_input("Tambah Lagu", "Nama Artis:")
        if not artis: artis = "Unknown"

        self.last_id += 1
        lagu_baru = Lagu(self.last_id, judul, artis, "Pop", filepath)
        self.library.append(lagu_baru)
        if lagu_baru not in self.playlists["Mood Today"]:
            self.playlists["Mood Today"].append(lagu_baru)
        if self.active_playlist_name != "Mood Today":
            self.playlists[self.active_playlist_name].append(lagu_baru)
        
        self.refresh_view(self.active_playlist_name)
        self.show_custom_alert("Berhasil", "Lagu berhasil ditambahkan!")

    def tambah_lagu_folder(self):
        """Manual Add Folder (Admin)"""
        folder_selected = filedialog.askdirectory(title="Pilih Folder Lagu")
        if folder_selected:
            count = self.scan_and_add_songs(folder_selected)
            if count > 0:
                self.show_custom_alert("Berhasil", f"Berhasil memuat {count} lagu dari folder tersebut!")
                if self.active_playlist_name:
                    self.refresh_view(self.active_playlist_name)
            else:
                self.show_custom_alert("Info", "Tidak ada file musik baru di folder itu.", is_error=True)

    def open_playlist_detail(self, playlist_name):
        self.active_playlist_name = playlist_name
        self.refresh_view(playlist_name)

    def refresh_sidebar_playlists(self):
        for widget in self.playlist_sidebar_container.winfo_children():
            widget.destroy()
        for name in self.playlists:
            if name != "Mood Today":
                self.create_sidebar_btn(self.playlist_sidebar_container, f"🎵 {name}", lambda n=name: self.open_playlist_detail(n))

    def refresh_view(self, playlist_name):
        self.header_canvas.delete("all")
        self.header_canvas.create_oval(-50, -50, 350, 350, fill=self.colors["accent2"], outline="") 
        display_name = playlist_name.upper()
        self.header_canvas.create_text(50, 90, text=display_name, fill="white", font=("Helvetica", 45, "bold"), anchor="w")
        subtext = "Koleksi Lagu Utama Kamu" if playlist_name == "Mood Today" else "Playlist Pilihanmu"
        self.header_canvas.create_text(52, 140, text=subtext, fill="#FFE4E1", font=("Arial", 12), anchor="w")
        
        if hasattr(self, 'header_play_btn_frame'): self.header_play_btn_frame.destroy()
        self.header_play_btn_frame = tk.Frame(self.header_canvas, bg=self.colors["accent"], cursor="hand2")
        self.header_play_btn_frame.place(relx=0.92, rely=0.5, anchor="center", width=70, height=70)

        btn_cvs = tk.Canvas(self.header_play_btn_frame, bg=self.colors["accent"], highlightthickness=0, cursor="hand2")
        btn_cvs.pack(fill="both", expand=True)
        btn_cvs.create_oval(2, 2, 68, 68, fill="white", outline="")
        btn_cvs.create_polygon(26, 20, 26, 50, 52, 35, fill="black")
        self.bind_recursive(self.header_play_btn_frame, "<Button-1>", lambda e: self.play_playlist_all())

        for widget in self.cards_frame.winfo_children(): widget.destroy()
        lagu_list = self.playlists.get(playlist_name, [])
        self.queue_dll.clear()
        for lagu in lagu_list: self.queue_dll.append(lagu)

        if not lagu_list:
            tk.Label(self.cards_frame, text="(Belum ada lagu)", bg=self.colors["bg_main"], fg="grey", font=("Arial", 12)).pack(pady=50)
            return

        row, col = 0, 0
        screen_w = self.root.winfo_width()
        if screen_w < 100: screen_w = 900
        col_width = 220
        max_cols = max(3, (screen_w - 250) // col_width)

        for index, lagu in enumerate(lagu_list):
            card = tk.Frame(self.cards_frame, bg=self.colors["card_bg"], width=190, height=250, cursor="hand2")
            card.grid(row=row, column=col, padx=10, pady=15)
            card.pack_propagate(False)

            artist_color = self.get_artist_color(lagu.artis)
            click_cmd = lambda e, idx=index: self.play_from_index(idx)
            
            cover = tk.Frame(card, bg=artist_color, height=180)
            cover.pack(fill="x")
            lbl_icon = tk.Label(cover, text="♫", font=("Arial", 50), bg=artist_color, fg="white")
            lbl_icon.place(relx=0.5, rely=0.5, anchor="center")

            info_area = tk.Frame(card, bg=self.colors["card_bg"])
            info_area.pack(fill="both", expand=True, padx=5)

            lbl_title = tk.Label(info_area, text=lagu.judul, font=("Arial", 11, "bold"), bg=self.colors["card_bg"], fg="white", wraplength=170)
            lbl_title.pack(pady=(8, 0))

            lbl_artist = tk.Label(info_area, text=lagu.artis, font=("Arial", 9), bg=self.colors["card_bg"], fg="grey")
            lbl_artist.pack()
            self.bind_recursive(card, "<Button-1>", click_cmd)

            col += 1
            if col >= max_cols: col=0; row+=1
            
    def play_from_index(self, index):
        node = self.queue_dll.get_node_at_index(index)
        if node: self.play_node(node)

    def play_playlist_all(self):
        if self.queue_dll.head:
            self.play_node(self.queue_dll.head)

    def play_node(self, node):
        self.current_node = node
        lagu = node.data
        try:
            if mixer:
                mixer.music.load(lagu.filename)
                mixer.music.play()
                self.is_playing = True
                self.update_play_button_icon()
                self.lbl_now_playing.config(text=f"{lagu.judul} - {lagu.artis}")
                self.song_length = 0
                if MP3:
                    try:
                        audio = MP3(lagu.filename)
                        self.song_length = audio.info.length
                        self.slider.config(to=self.song_length) 
                    except: pass
                else:
                    self.slider.config(to=100)
        except Exception as e:
            self.show_custom_alert("Error File", f"Gagal memutar file: {e}", is_error=True)

    def update_play_button_icon(self):
        self.play_canvas.delete("icon")
        if self.is_playing:
            self.play_canvas.create_rectangle(18, 16, 24, 38, fill="white", outline="", tags="icon")
            self.play_canvas.create_rectangle(30, 16, 36, 38, fill="white", outline="", tags="icon")
        else:
            self.play_canvas.create_polygon(20, 16, 20, 38, 38, 27, fill="white", tags="icon")

    def toggle_play(self):
        if not self.current_node:
            self.play_playlist_all()
            return
        if self.is_playing:
            mixer.music.pause()
            self.is_playing = False
        else:
            mixer.music.unpause()
            self.is_playing = True
        self.update_play_button_icon()

    def next_song(self):
        if not self.current_node: return
        if self.is_shuffle:
            all_nodes = self.queue_dll.get_all_nodes()
            if len(all_nodes) > 1:
                nxt = random.choice(all_nodes)
                self.play_node(nxt)
            return
        if self.current_node.next:
            self.play_node(self.current_node.next)
        elif self.queue_dll.head: 
            self.play_node(self.queue_dll.head)

    def prev_song(self):
        if not self.current_node: return
        if self.current_node.prev:
            self.play_node(self.current_node.prev)
        else:
            self.play_node(self.current_node) 

    def toggle_shuffle(self):
        self.is_shuffle = not self.is_shuffle
        color = self.colors["accent"] if self.is_shuffle else "#B3B3B3"
        self.btn_shuffle.config(fg=color)

    def update_slider_loop(self):
        if self.is_playing and mixer:
            try:
                if mixer.music.get_busy():
                    current_ms = mixer.music.get_pos()
                    if current_ms != -1:
                        current_sec = current_ms / 1000
                        self.slider.set(current_sec)
                        cur_min, cur_s = divmod(int(current_sec), 60)
                        tot_min, tot_s = divmod(int(self.song_length), 60)
                        self.lbl_time_status.config(text=f"{cur_min}:{cur_s:02d} / {tot_min}:{tot_s:02d}")
                        if self.song_length > 0 and current_sec >= self.song_length - 1:
                            self.next_song()
            except:
                pass
        self.root.after(1000, self.update_slider_loop)

    def geser_slider(self, val):
        pass

    def pindah_playlist_dialog(self):
        if not self.current_node:
             self.show_custom_alert("Info", "Putar dulu lagu yang ingin dipindahkan.")
             return
        lagu = self.current_node.data
        opsi = [k for k in self.playlists.keys() if k != "Mood Today"]
        if not opsi:
            self.show_custom_alert("Info", "Kamu belum membuat playlist lain.")
            return

        msg = f"Ketik nama playlist tujuan:\n({', '.join(opsi)})"
        tujuan = self.show_custom_input("Pindah Lagu", msg)

        if tujuan and tujuan in self.playlists:
            if lagu not in self.playlists[tujuan]:
                self.playlists[tujuan].append(lagu)
                self.show_custom_alert("Sukses", f"Lagu disalin ke playlist '{tujuan}'.")
            else:
                self.show_custom_alert("Info", "Lagu sudah ada di playlist tersebut.")
        elif tujuan:
             self.show_custom_alert("Error", "Playlist tidak ditemukan!", is_error=True)

    def hapus_lagu_terpilih(self):
        if not self.current_node:
             self.show_custom_alert("Info", "Putar lagu yang ingin dihapus terlebih dahulu.")
             return
        
        if self.user_role != "admin":
            self.show_custom_alert("Akses Ditolak", "Hanya Admin yang dapat menghapus lagu.", is_error=True)
            return

        lagu = self.current_node.data
        if self.show_custom_yesno("Konfirmasi", f"Yakin hapus '{lagu.judul}'?"):
            if lagu in self.playlists[self.active_playlist_name]:
                self.playlists[self.active_playlist_name].remove(lagu)
            mixer.music.stop()
            self.is_playing = False
            self.lbl_now_playing.config(text="Terhapus")
            self.update_play_button_icon()
            self.refresh_view(self.active_playlist_name)

    #fungsi pencarian
    def aksi_cari_lagu(self, event):
        keyword = self.entry_search.get().lower()
        sumber = self.playlists[self.active_playlist_name]
        hasil_cari = [l for l in sumber if keyword in l.judul.lower() or keyword in l.artis.lower()]
        for widget in self.cards_frame.winfo_children(): widget.destroy()
        row, col, max_cols = 0, 0, 4
        for index, lagu in enumerate(hasil_cari):
            card = tk.Frame(self.cards_frame, bg="#333333", width=190, height=250)
            card.grid(row=row, column=col, padx=10, pady=15)
            card.pack_propagate(False)
            artist_color = self.get_artist_color(lagu.artis)
            try: idx_asli = sumber.index(lagu)
            except ValueError: continue
            click_cmd = lambda e, idx=idx_asli: self.play_from_index(idx)
            cover = tk.Frame(card, bg=artist_color, height=180)
            cover.pack(fill="x")
            lbl_icon = tk.Label(cover, text="🔍", font=("Arial", 40), bg=artist_color, fg="white")
            lbl_icon.place(relx=0.5, rely=0.5, anchor="center")
            lbl_title = tk.Label(card, text=lagu.judul, font=("Arial", 11, "bold"), bg="#333333", fg="white")
            lbl_title.pack(pady=(10,0))
            self.bind_recursive(card, "<Button-1>", click_cmd)
            col += 1
            if col >= max_cols: col=0; row+=1

    #khusus admin fungsi tambahan
    def tambah_lagu_file(self):
        """Manual Add Single File (Admin)"""
        filepath = filedialog.askopenfilename(filetypes=[("Audio Files", "*.mp3 *.wav")])
        if not filepath: return
        filename = os.path.basename(filepath)
        judul = self.show_custom_input("Tambah Lagu", f"Judul Lagu ({filename}):")
        if not judul: judul = filename
        artis = self.show_custom_input("Tambah Lagu", "Nama Artis:")
        if not artis: artis = "Unknown"

        self.last_id += 1
        lagu_baru = Lagu(self.last_id, judul, artis, "Pop", filepath)
        self.library.append(lagu_baru)
        if lagu_baru not in self.playlists["Mood Today"]:
            self.playlists["Mood Today"].append(lagu_baru)
        if self.active_playlist_name != "Mood Today":
            self.playlists[self.active_playlist_name].append(lagu_baru)
        
        self.refresh_view(self.active_playlist_name)
        self.show_custom_alert("Berhasil", "Lagu berhasil ditambahkan!")

    def tambah_lagu_folder(self):
        """Manual Add Folder (Admin)"""
        folder_selected = filedialog.askdirectory(title="Pilih Folder Lagu")
        if folder_selected:
            count = self.scan_and_add_songs(folder_selected)
            if count > 0:
                self.show_custom_alert("Berhasil", f"Berhasil memuat {count} lagu dari folder tersebut!")
                if self.active_playlist_name:
                    self.refresh_view(self.active_playlist_name)
            else:
                self.show_custom_alert("Info", "Tidak ada file musik baru di folder itu.", is_error=True)

    def buat_playlist_baru(self):
        nama = self.show_custom_input("Buat Playlist", "Masukkan Nama Playlist Baru:")
        if nama:
            if nama not in self.playlists:
                self.playlists[nama] = []
                self.refresh_sidebar_playlists() 
                self.open_playlist_detail(nama)
                self.show_custom_alert("Sukses", f"Playlist '{nama}' berhasil dibuat!")
            else:
                self.show_custom_alert("Error", "Nama playlist sudah ada!", is_error=True)

if __name__ == "__main__":
    root = tk.Tk()
    app = MarsPlayerApp(root)
    #scan di panggil setelah window siap
    root.after(500, app.initial_folder_scan)
    root.mainloop()