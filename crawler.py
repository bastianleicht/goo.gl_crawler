import mysql.connector
from mysql.connector import Error
import requests
import random
import string
import time


# Funktion zur Generierung einer zufälligen URL-Endung
def generate_random_suffix(min_length=3, max_length=7):
    """Generiert einen zufälligen Slug mit variabler Länge."""
    length = random.randint(min_length, max_length)
    return ''.join(random.choice(string.ascii_lowercase + string.digits) for _ in range(length))


# Funktion zur Durchführung der Webabfrage und Ermittlung der Weiterleitungsadresse
def get_redirect_url(base_url, suffix):
    url = f"{base_url}/{suffix}"
    try:
        response = requests.head(url, allow_redirects=True)
        return response.url if response.url != url else None
    except requests.RequestException as e:
        print(f"Error fetching URL: {url} - {e}")
        return None


# Funktion zum Erstellen der MySQL-Datenbank und der Tabelle
def create_database(connection):
    try:
        cursor = connection.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS redirects (
                slug VARCHAR(255) PRIMARY KEY,
                original_url TEXT,
                redirect_url TEXT
            )
        ''')
        connection.commit()
    except Error as e:
        print(f"Error creating database table: {e}")


# Funktion zum Einfügen der URLs in die MySQL-Datenbank
def insert_into_database(connection, slug, original_url, redirect_url):
    try:
        cursor = connection.cursor()
        cursor.execute("""
            INSERT INTO redirects (slug, original_url, redirect_url)
            VALUES (%s, %s, %s)
            ON DUPLICATE KEY UPDATE redirect_url = VALUES(redirect_url)
        """, (slug, original_url, redirect_url))
        connection.commit()
    except Error as e:
        print(f"Error inserting into database: {e}")


# Hauptskript
def main():
    base_url = "https://goo.gl"

    # MySQL-Verbindungsdetails
    config = {
        'host': 'host1.bastianleicht.de',
        'user': 'c1scraper_user',
        'password': 'vbpT@B6Z5',
        'database': 'c1googl_scraper'
    }

    try:
        # Verbindung zur MySQL-Datenbank herstellen
        connection = mysql.connector.connect(**config)

        # Datenbank und Tabelle erstellen
        create_database(connection)

        while True:
            suffix = generate_random_suffix()
            slug = suffix  # Verwenden des Suffix als Slug
            original_url = f"{base_url}/{suffix}"
            redirect_url = get_redirect_url(base_url, suffix)

            if redirect_url:
                print(f"Original URL: {original_url} -> Redirect URL: {redirect_url}")
                insert_into_database(connection, slug, original_url, redirect_url)
            else:
                print(f"Original URL: {original_url} has no redirection.")

            # Wartezeit einfügen, um Serverüberlastung zu vermeiden
            time.sleep(random.uniform(1, 3))  # Wartezeit zwischen 1 und 3 Sekunden

    except Error as e:
        print(f"Error connecting to MySQL: {e}")

    finally:
        if connection.is_connected():
            connection.close()


if __name__ == "__main__":
    main()
