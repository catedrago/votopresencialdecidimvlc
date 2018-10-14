import sqlite3
"""
Como usar la clase Votacion:

Creamos el objecto Votacion.
Creamos la tabla, en caso de ser necesario (create_table)
Usamos votar para anyadir votos
Al acabar con el objeto, cerrar la BD con close_database

Ejemplo en el main
"""
class Votacion:
    """
    Clase para controlar la votacion
    """


    def __init__(self, name):
        """
        Set DB name and connect
        :param name: Database name
        """
        self.conn = None
        self.name_db = name
        self.connect_database()

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
        sql_create_censo_table = """ CREATE TABLE IF NOT EXISTS votacion (
                                                id_proyecto INTEGER PRIMARY KEY,
                                                n_votos INTEGER
                                            ); """
        try:
            c = self.conn.cursor()
            c.execute(sql_create_censo_table)
        except Exception as e:
            print(e)

    def votar(self, id_proyecto):
        """
        Add a voote to table
        :param conn: connection to the database
        :param id_proyecto: id_proyecto (integer)
        :return:
        """


        n_votes = self.get_vote(id_proyecto)
        if n_votes is None:
            try:
                sql = ''' INSERT INTO votacion(id_proyecto, n_votos)
                                  VALUES(?,1) '''
                cur = self.conn.cursor()
                cur.execute(sql, (str(id_proyecto),))
                self.conn.commit()
            except sqlite3.IntegrityError as e:
                print("Ya existe el id_proyecto {}".format(id_proyecto))
        else:
            n_votes += 1
            try:
                sql = ''' UPDATE votacion SET n_votos=? WHERE id_proyecto=?'''
                cur = self.conn.cursor()
                cur.execute(sql, (str(n_votes),str(id_proyecto),))
                self.conn.commit()
            except sqlite3.IntegrityError as e:
                print("Ya existe el id_proyecto {}".format(id_proyecto))

    def get_vote(self, id_proyecto):
        """
        Get number of votes from an id_proyecto
        :param dni: String
        :return: None si no existe el id_proyecto o el numero de votos que tiene el id_proyecto
        """

        cur = self.conn.cursor()
        cur.execute("SELECT n_votos FROM votacion where id_proyecto='{}'".format(id_proyecto))

        row = cur.fetchone()
        if row is not None:
            row = row[0]
        return row

    def get_recuento(self):
        """
        Recoge un recuento de los votos
        :return:
        """
        cur = self.conn.cursor()
        cur.execute("SELECT id_proyecto, n_votos FROM votacion ")

        row = cur.fetchall()


        return row

    def close_database(self):
        """
        Close database conexion
        :return:
        """
        self.conn.commit()
        self.conn.close()









if __name__ == "__main__":
    #Primera vez que te conectas a la BD
    db = Votacion("votacion.db")
    #Creamos la tabla
    db.create_table()
    votos = [
        1004,
        556,
        666,
        1004,
        1384,
        1004
    ]
    for voto in votos:
        db.votar(voto)
    print(db.get_recuento())
    db.close_database() #importante cerrar
