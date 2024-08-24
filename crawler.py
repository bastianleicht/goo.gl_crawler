import mysql.connector
from mysql.connector import Error
import requests
import random
import string
import time
import configparser


# Funktion zur Generierung einer zufälligen URL-Endung
def generate_random_suffix(min_length=3, max_length=7):
    """Generiert einen zufälligen Slug mit variabler Länge."""
    length = random.randint(min_length, max_length)
    return ''.join(random.choice(string.ascii_lowercase + string.digits) for _ in range(length))


# Funktion zur Durchführung der Webabfrage und Ermittlung der Weiterleitungsadresse
def get_redirect_url(base_url, suffix):
    url = f"{base_url}/{suffix}"
    try:
        response = requests.head(url, allow_redirects=False, timeout=5)

        # Prüfe, ob die Antwort einen 302-Statuscode hat
        if response.status_code == 302 and 'Location' in response.headers:
            # Extrahiere die Weiterleitungs-URL aus dem 'Location'-Header
            redirect_url = response.headers['Location']
            # Wenn die Redirect-URL relativ ist, füge die Basis-URL hinzu
            if redirect_url.startswith('/'):
                redirect_url = f"{base_url}{redirect_url}"
            return redirect_url
        else:
            # Keine Weiterleitung oder kein 302-Statuscode, Rückgabe von None
            return None
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


# Funktion zum Überprüfen, ob der Slug bereits existiert
def slug_exists(connection, slug):
    try:
        cursor = connection.cursor()
        cursor.execute("SELECT slug FROM redirects WHERE slug = %s", (slug,))
        result = cursor.fetchone()
        return result is not None  # Wenn es ein Ergebnis gibt, existiert der Slug bereits
    except Error as e:
        print(f"Error checking slug existence: {e}")
        return False


# Hauptskript
def main():
    base_url = "https://goo.gl"

    # Konfigurationsdatei einlesen
    config = configparser.ConfigParser()
    config.read('config.ini')

    # MySQL-Verbindungsdetails aus der config.ini
    db_config = {
        'host': config.get('mysql', 'host'),
        'user': config.get('mysql', 'user'),
        'password': config.get('mysql', 'password'),
        'database': config.get('mysql', 'database')
    }

    try:
        # Verbindung zur MySQL-Datenbank herstellen
        connection = mysql.connector.connect(**db_config)

        # Datenbank und Tabelle erstellen
        create_database(connection)

        while True:
            # Generiere neuen Slug und prüfe, ob dieser bereits existiert
            suffix = generate_random_suffix()
            slug = suffix  # Verwenden des Suffix als Slug

            if slug_exists(connection, slug):
                print(f"Slug {slug} already exists in the database. Skipping.")
                continue  # Neuen Slug generieren

            # Original URL erstellen
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
