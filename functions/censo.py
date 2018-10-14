import sqlite3, time
"""
Como usar la clase Censo:

Creamos el objecto censo.
Creamos la tabla, en caso de ser necesario (create_table)
Usamos add_DNI para anyadir DNIs
Usamos check_census para ver si existe el DNI en la BD
Al acabar con el objeto, cerrar la BD con close_database

Ejemplo en el main
"""
class Censo:
    """
    Clase para controlar el censo
    """

    anonimo = True

    def __init__(self, name, anonimo=True):
        """
        Set DB name and connect
        :param name: Database name
        :param anonimo: True or False. Indica si el sistema de voto es anonimo o no
        """
        self.conn = None
        self.name_db = name
        self.connect_database()
        self.anonimo = anonimo

    def connect_database(self):
        """
        Connect or create a database and return the conn
        """
        self.conn=sqlite3.connect(self.name_db)

    def create_table(self):
        """
        Create table only with DNIs
        :param conn: connection to the database
        :return:
        """
        sql_create_censo_table = """ CREATE TABLE IF NOT EXISTS censo (
                                                dni text PRIMARY KEY,
                                                ha_votado INTEGER ,
                                                hora INTEGER,
                                                votos TEXT
                                            ); """
        try:
            c = self.conn.cursor()
            c.execute(sql_create_censo_table)
        except Exception as e:
            print(e)

    def add_DNI(self, dni):
        """
        Add a dni/nie to table
        :param dni: dni or nie (String)
        :return:
        """
        if self.anonimo:
            sql = ''' INSERT INTO censo(dni, ha_votado, votos)
                      VALUES(?,?, ?) '''
            try:
                cur = self.conn.cursor()
                if self.anonimo:
                    cur.execute(sql, (dni, 0, "Anonimo"))
                else: #Sobra
                    cur.execute(sql, (dni, 0, "-"))
                self.conn.commit()
            except sqlite3.IntegrityError as e:
                print("Ya existe el DNI {}".format(dni))
        else:
            sql = ''' INSERT INTO censo(dni, ha_votado)
                                  VALUES(?,?) '''
            try:
                cur = self.conn.cursor()
                cur.execute(sql, (dni, 0))
                self.conn.commit()
            except sqlite3.IntegrityError as e:
                print("Ya existe el DNI {}".format(dni))

    def check_census(self, dni):
        """
        Check if a DNI or NIE exists
        :param dni: String
        :return: Boolean
        """

        cur = self.conn.cursor()
        cur.execute("SELECT dni FROM censo where dni='{}'".format(dni))

        row = cur.fetchone()
        # print(row) #Debe devolver (0,)
        return row is not None

    def check_voted(self, hash_dni):
        """
        Check if a DNI or NIE has voted
        :param dni: String
        :return: Boolean
        """

        cur = self.conn.cursor()
        cur.execute("SELECT dni FROM censo where dni='{}' and ha_votado=1".format(hash_dni))

        row = cur.fetchone()

        return row is not None

    def vote(self, hash_dni, votos=[]):
        """
        Set vote
        :param dni: String
        :return: True si va bien, "No aparece" o "Ha votado ya"
        """
        print("votando {}".format(hash_dni))
        if not self.check_census(hash_dni):
            return "No aparece"
        elif self.check_voted(hash_dni):
            return "Ha votado ya"
        cur = self.conn.cursor()
        if self.anonimo:
            cur.execute("""UPDATE censo SET ha_votado=1, hora=? WHERE dni=? AND ha_votado=0""", (time.time() + 7200, hash_dni))
            # cur.execute("""UPDATE censo SET ha_votado=1, hora=? WHERE dni=? AND ha_votado=0""", (time.time(), hash_dni))
        else:

            # cur.execute("""UPDATE censo SET ha_votado=1, hora=?, votos=? WHERE dni=? AND ha_votado=0""", (time.time(),str(votos), hash_dni))
            cur.execute("""UPDATE censo SET ha_votado=1, hora=?, votos=? WHERE dni=? AND ha_votado=0""", (time.time() + 7200,str(votos), hash_dni))

        self.conn.commit()
        return True

    def check_voted_decidimVlc(self, hash_dni):
        """
        Check if a DNI or NIE has voted
        :param dni: String
        :return: Boolean
        """

        cur = self.conn.cursor()
        cur.execute("SELECT dni FROM censo where dni='{}'".format(hash_dni))

        row = cur.fetchone()

        return row is not None

    def vote_decidimVlc(self, hash_dni, votos=[]):
        """
        Set vote
        :param dni: String
        :return: True si va bien, "No aparece" o "Ha votado ya"
        """
        print("votando {}".format(hash_dni))
        if self.check_voted_decidimVlc(hash_dni):
            return "Ha votado ya"
        cur = self.conn.cursor()
        sql = ''' INSERT INTO censo(dni, ha_votado, hora, votos)
                             VALUES(?,?,?,?) '''
        cur.execute(sql, (hash_dni, 1, time.time() + 7200,str(votos)) )
        # cur.execute(sql, (hash_dni, 1, time.time(),str(votos)) )

        self.conn.commit()
        return True

    def hora_voted(self, hash_dni):
        """
        Comprueba si el DNI ha votado, y en caso de haber votado devuelve la hora (timestamp)
        :param dni:
        :return: False or timestamp (integer)
        """
        cur = self.conn.cursor()
        cur.execute("SELECT hora FROM censo where dni='{}' and ha_votado=1".format(hash_dni))

        row = cur.fetchone()

        if row is not None:
            return row[0]
        else:
            return row

    def get_votos(self):
        """
        Funcion que solo sirve si el sistema NO es anonimo.
        Devuelve los votos que ha realizado cada DNI
        :return:
            [
                ("dni" ,[votos_ints], timestamp_hora_votado)
            ]
        """
        if self.anonimo:
            return False
        res = []
        cur = self.conn.cursor()
        cur.execute("SELECT * FROM censo")

        row = cur.fetchall()

        # for dni, ha_votado, timestamp, votos in row:
        #     res.append()


        return row


    def close_database(self):
        """
        Close database conexion
        :return:
        """
        self.conn.commit()
        self.conn.close()









if __name__ == "__main__":
    anonimo = False
    #Primera vez que te conectas a la BD
    db = Censo("censo.db", anonimo=anonimo)
    #Creamos la tabla
    db.create_table()
    DNIs = [
        "1224578V",
        "12345678G",
        "123456789A",
        "123456789Z"
    ]
    for dni in DNIs[:-1]:
        db.add_DNI(dni)
    if not db.check_voted(DNIs[1]):
        print(db.vote(DNIs[1], votos=[5,8]))
    print(db.vote(DNIs[0], votos=[1,8]))
    print(db.vote(DNIs[1], votos=[5,8]))
    print(db.vote(DNIs[-1], votos=[5,8]))
    db.close_database() #importante cerrar


    db = Censo("censo.db")

    if anonimo:
        for dni in DNIs:
            print("El dni '> {} <' esta en la BD? -> {} y ha votado? {}".format(dni, db.check_census(dni), db.check_voted(dni)))

    else:
        rows = db.get_votos()
        for i in rows:
            print(i)

    db.close_database()  # importante cerrar
