import getpass
import psycopg2
from psycopg2 import OperationalError
import logging
from prettytable import PrettyTable
import sys
import time


def banner():
    print("\033[94m" + """
    ##############################################
    /+/ PostgreSQLChecking /+/ 
                by https://github.com/hidayatimam
    ###############################################
    """ + "\033[0m")


# Konfigurasi logging
logging.basicConfig(filename='postgres.log', level=logging.DEBUG,   
                    format='%(asctime)s [%(levelname)s]: %(message)s')

def get_valid_input(prompt, default=None, empty_message=None):
    while True:
        try:
            user_input = input(prompt)
            if not user_input and default is not None:
                return default
            elif not user_input and default is None:
                if empty_message:
                    print(empty_message)
                else:
                    print("Input tidak boleh kosong.")
            else:
                return user_input
        except KeyboardInterrupt:
            raise
        except Exception as e:
            print(f"Terjadi kesalahan: {e}")
            logging.error(f"Terjadi kesalahan: {e}")

def print_loading_animation():
    animation = "|/-\\"
    for _ in range(10):
        for char in animation:
            sys.stdout.write(char)
            sys.stdout.flush()
            time.sleep(0.1)
            sys.stdout.write("\b")

def check_postgresql_connection(host, port, database, user, password):
    connection = None  # Initialize connection to None for proper cleanup in finally block
    try:
        # Membuat koneksi ke database PostgreSQL
        print("Menghubungkan ke database... ", end='', flush=True)
        print_loading_animation()

        connection = psycopg2.connect(
            host=host,
            port=port,
            database=database,
            user=user,
            password=password
        )

        # Mengeksekusi query sederhana untuk memastikan koneksi berhasil
        with connection.cursor() as cursor:
            cursor.execute("SELECT version();")
            result = cursor.fetchone()
            print(f"Koneksi berhasil ke {result[0]}")

            # Output informasi tentang pengguna saat ini
            cursor.execute("SELECT current_user;")
            username_result = cursor.fetchone()

            # Membuat tabel PrettyTable
            table = PrettyTable()
            table.field_names = ["Username", "Database", "Host" , "Port" , "Password"]
            table.add_row([username_result[0], database, host, port, password])

            # Menampilkan tabel
            print("\nInformasi Pengguna:")
            print(table)

            # Log access information
            logging.info(f"Access - User: {username_result[0]}, Database: {database}")

    except OperationalError as op_err:
        # Catch OperationalError for authentication failures
        if "authentication failed" in str(op_err):
            print("Kesalahan: Autentikasi gagal. Periksa kembali nama pengguna dan kata sandi.")
        else:
            print(f"Terjadi kesalahan: {op_err}")
            logging.error(f"Terjadi kesalahan: {op_err}")
    except Exception as e:
        print(f"Terjadi kesalahan: {e}")
        logging.error(f"Terjadi kesalahan: {e}")
    finally:
        # Menutup koneksi
        if connection:
            connection.close()

if __name__ == "__main__":
    banner()
    try:
        host = get_valid_input("Masukkan host PostgreSQL: ", empty_message="Host tidak boleh kosong.")
        port = get_valid_input("Masukkan port PostgreSQL: ", empty_message="Port tidak boleh kosong.")
        database = get_valid_input("Masukkan nama database PostgreSQL: ", empty_message="Nama database tidak boleh kosong.")
        user = get_valid_input("Masukkan nama pengguna PostgreSQL: ", empty_message="Nama pengguna tidak boleh kosong.")
        password = getpass.getpass("Masukkan kata sandi PostgreSQL: ")

        # Memanggil fungsi untuk mengecek koneksi
        check_postgresql_connection(host, port, database, user, password)
    except KeyboardInterrupt:  
        print("")
        print("Bye..")
        sys.exit(0)
