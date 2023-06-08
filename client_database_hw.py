import psycopg2
from pprint import pprint


def delete_db(conn):
        cur.execute(""" 
        DROP TABLE clients_phones;
        DROP TABLE clients;
        """)
        conn.commit()
    
def create_db(conn):
        cur.execute("""
        CREATE TABLE IF NOT EXISTS clients(
        id SERIAL PRIMARY KEY,
        name VARCHAR(20) NOT NULL,
        surname VARCHAR(30) NOT NULL,
        email VARCHAR(30) UNIQUE 
        );
        """)

        cur.execute("""
        CREATE TABLE IF NOT EXISTS clients_phones(
        client_id INTEGER REFERENCES clients(id),
        phone VARCHAR(20) UNIQUE
        );
        """)
        conn.commit()

def add_client(conn, name, surname, email, phone = None):
        cur.execute("""
        INSERT INTO clients(
        name, surname, email
        )
        VALUES(%s, %s, %s) RETURNING id;
        """, (name, surname, email))
        id = cur.fetchone()[0]
        if phone is not None:
            cur.execute("""
            INSERT INTO clients_phones(
            phone, client_id)
            VALUES(%s, %s);
            """, (phone, id))
        conn.commit()

def add_phone(conn, client_id, phone):
        cur.execute("""
        INSERT INTO clients_phones(
        client_id, phone
        )
        VALUES(%s, %s);
        """, (client_id, phone))
        conn.commit()
        
def update_clients(conn, client_id, name = None, surname = None, email = None):
        cur.execute("""
        SELECT * FROM clients
        WHERE id = %s;
        """, (client_id,))
        client_info = cur.fetchone()

        if name is None:
                name = client_info[1]
        if surname is None:
                surname = client_info[2]
        if email is None:
                email = client_info[3]
        cur.execute("""
        UPDATE clients
        SET name = %s, surname = %s, email = %s
        WHERE id = %s;
        """, (name, surname, email, client_id))
        conn.commit()

def delete_phone(conn, client_id, phone):
        cur.execute("""
        SELECT client_id FROM clients_phones
        WHERE client_id = %s; 
        """, (client_id,))
        res = cur.fetchone()
        if res is not None:
                cur.execute("""
                DELETE FROM clients_phones
                WHERE client_id = %s AND phone = %s;
                """, (client_id, phone))
        else:
                pprint('Клиент с таким ID не найден')
        conn.commit()

def delete_client(conn, client_id):
        cur.execute("""
        SELECT id FROM clients
        WHERE id = %s;
        """, (client_id,))
        res = cur.fetchone()
        if res is not None:
                cur.execute("""
                DELETE FROM clients_phones WHERE client_id = %s;
                DELETE FROM clients WHERE id = %s;
                """, (client_id, client_id))
        else:
                pprint('Клиент с таким ID не найден')
        conn.commit()

def find_client(conn, name=None, surname=None, email=None, phone=None):
        if name is not None or surname is not None or email is not None or phone is not None:
            cur.execute("""
            SELECT id, name, surname, email, phone FROM clients
            LEFT JOIN clients_phones ON clients.id = clients_phones.client_id
            WHERE name=%s OR surname=%s OR email=%s  OR phone=%s;
            """, (name, surname, email, phone,))
            pprint(cur.fetchone())




with psycopg2.connect(database="client_data", user="postgres", password="tgntityrj") as conn:
           with conn.cursor() as cur:
                delete_db(conn)   
                create_db(conn)
                add_client(conn, 'Ivan', 'Ivanov', 'ivan@gmail')
                add_client(conn, 'Petr', 'Petrov', None, '89881234455')
                add_client(conn, 'Semen', 'Semenov', 'semen@mail', '89995556633')
                add_phone(conn, 1, '81127778899')
                add_phone(conn, 3, '82324447766')
                update_clients(conn, 1, None, 'Ivanchenko', None)
                delete_phone(conn, 2, '89881234455')
                find_client(conn, 'Ivan', None, 'ivan@gmail', None)
