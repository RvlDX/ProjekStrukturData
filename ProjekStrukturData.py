import mysql.connector
import random
import os
from tabulate import tabulate

# Fungsi untuk melakukan koneksi ke database
def connect_to_database():
    return mysql.connector.connect(
        host        = "127.0.0.1",
        user        = "root",           # username database 
        password    = "",               # password database 
        database    = "tiket_pesawat"   # nama database
    )

# Fungsi untuk login
def login():
    print("============================ Login ================================")
    username = input("Username   : ")
    password = input("Password   : ")
    print("===================================================================")
    conn     = connect_to_database()
    cursor   = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE username=%s", (username,))
    user_by_username = cursor.fetchone()
    cursor.execute("SELECT * FROM users WHERE username=%s AND password=%s", (username, password))
    user     = cursor.fetchone()
    cursor.close()
    conn.close()
    if user:
        return user
    elif user_by_username:
        print("Password salah.")
    else:
        print("Username tidak ditemukan.")
    return None

# Fungsi untuk registrasi
def register():
    print("============================ Registrasi ===========================")
    username = input("Username   : ")
    password = input("Password   : ")
    print("===================================================================")
    conn     = connect_to_database()
    cursor   = conn.cursor()
    cursor.execute("INSERT INTO users (username, password) VALUES (%s, %s)", (username, password))
    conn.commit()
    cursor.close()
    conn.close()
    print("Registrasi berhasil. Silakan login.")

# Fungsi untuk menampilkan tujuan penerbangan dari database dalam bentuk tabel
def show_flight_destinations():
    conn    = connect_to_database()
    cursor  = conn.cursor()
    cursor.execute("SELECT * FROM flights")
    destinations = cursor.fetchall()
    cursor.close()
    conn.close()
    
    headers = ["ID", "Nama Pesawat", "Kelas", "Tujuan", "Tanggal Berangkat", "Jam Berangkat", "Harga" ]
    
    # Memformat harga sebelum menampilkannya
    formatted_destinations = []
    for dest in destinations:
        formatted_dest = list(dest)
        formatted_dest[6] = "Rp. {:,}".format(int(dest[6]))  # Format harga tanpa desimal
        formatted_destinations.append(formatted_dest)
        
    print(tabulate(formatted_destinations, headers=headers))

# Fungsi untuk membuat kode tiket
def generate_ticket_code():
    return f"PSWT-{random.randint(1000, 9999)}"

# Fungsi untuk melakukan pembelian tiket
def buy_ticket(user):
    while True:
        print("\n========================= Pembelian Tiket =========================")
        show_flight_destinations()
        print("===================================================================")
        choice          = input("Pilih tujuan penerbangan (ID) : ")
        passenger_count = int(input("Jumlah penumpang              : "))
        print("===================================================================")
        conn            = connect_to_database()
        cursor          = conn.cursor()
        cursor.execute("SELECT * FROM flights WHERE id=%s", (choice,))
        flight          = cursor.fetchone()
        cursor.close()
        total_price     = int(flight[6]) * passenger_count
        
        ticket_code     = generate_ticket_code()
        
        cursor          = conn.cursor()
        cursor.execute("INSERT INTO bookings (user_id, flight_id, ticket_code, airline  , class    , destination, departure_date, departure_time, passengers, price) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)", 
                                             (user[0], flight[0], ticket_code, flight[1], flight[2], flight[3]  , flight[4]     , flight[5]     , passenger_count , flight[6]))

        conn.commit()
        cursor.close()
        conn.close()
        
        print("Invoice:")
        print("===================================================================")
        print("Kode Tiket                 :", ticket_code)
        print("Nama Pesawat               :", flight[1])
        print("Kelas                      :", flight[5])
        print("Tujuan Penerbangan         :", flight[1])
        print("Tanggal Berangkat          :", flight[2])
        print("Jam Berangkat              :", flight[3])
        print("Jumlah Penumpang           :", passenger_count)
        print("Harga                      : Rp.", "{:,}".format(int(flight[6])))
        print("Total Harga                : Rp.", "{:,}".format(total_price))
        print("===================================================================")
        payment = int(input("Masukkan uang bayar        : Rp. "))
        change = payment - total_price
        print("Kembalian                  : Rp.", "{:,}".format(change))
        print("===================================================================")
        
        another = input("Apakah Anda ingin membeli tiket lagi? (y/n)    : ").lower()
        if another != 'y':
            break

# Fungsi untuk cek kode pemesanan
def check_booking_code(user):
    ticket_code = input("Masukkan kode tiket Anda : ")
    conn   = connect_to_database()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM bookings WHERE user_id=%s AND ticket_code=%s", (user[0], ticket_code))
    booking = cursor.fetchone()
    cursor.close()
    conn.close()
    
    if booking:
        headers         = ["Kode Tiket", "Nama Pesawat", "Kelas"   , "Tujuan"  , "Tanggal Berangkat", "Jam Berangkat", "Jumlah Penumpang", "Harga"     ]
        harga           = booking[10] * booking[9]
        # Menyiapkan data untuk tabulasi
        formatted_data  = [[booking[3] , booking[4]    , booking[5], booking[6], booking[7]         , booking[8]     , booking[9]        , harga]]
        
        # Menampilkan dalam bentuk tabel
        print("Rincian Pemesanan:")
        print("===================================================================")
        print(tabulate(formatted_data, headers=headers))
    else:
        print("Tidak ada pemesanan ditemukan dengan kode tiket tersebut.")


# Fungsi utama setelah login
def main_menu(user):
    while True:
        print("\n============================ Menu Utama ===========================")
        print("1. Pesan Tiket Pesawat")
        print("2. Cek Kode Pemesanan")
        print("3. Logout")
        print("===================================================================")
        choice = input("Pilih menu : ")
        print("===================================================================")

        if choice == "1":
            buy_ticket(user)
        elif choice == "2":
            check_booking_code(user)
        elif choice == "3":
            print("Logout berhasil.")
            return
        else:
            print("Pilihan tidak valid. Silakan pilih lagi.")

# Fungsi utama
def main():
    while True:
        print("\n============================== Menu ===============================")
        print("1. Login")
        print("2. Registrasi")
        print("3. Exit")
        print("===================================================================")
        choice = input("Pilih menu : ")

        if choice == "1":
            user = login()
            if user:
                print("Login berhasil.")
                main_menu(user)
            else:
                print("Login gagal")

        elif choice == "2":
            register()

        elif choice == "3":
            print("Terima kasih telah menggunakan layanan kami.")
            break

        else:
            print("Pilihan tidak valid. Silakan pilih lagi.")

if __name__ == "__main__":
    main()
