import pandas as pd

path_proyecto = "/home/dietpi/evotebox2"
# path_proyecto = "~/Documentos/evotebox2/evotebox2"
nombre_archivo_prop_distr = "presupuestos_distrito.csv"

def search_name_by_id(id, id_camp="id"):
    """
    Busca el nombre del proyecto dado un id
    :param id: Int. Numero del proyecto
    :param id_camp: campo en donde se guardan ls IDs en el csv. id por defecto
    :return: tuple con el nombre del proyecto y su presupuesto
    (String, int)
    """
    search = ["title", "price"]
    try:
        propuestas_df = pd.read_csv("{}/functions/propuestas/bd_propuestas.csv".format(path_proyecto), sep=",", quotechar = '"', error_bad_lines=False)
    except:
        print("no existe el archivo de propuestas")
    propuesta = propuestas_df.loc[propuestas_df[id_camp] == id]
    if propuesta.empty:
        return None

    return propuesta[search[0]].values[0], propuesta[search[1]].values[0]


def comprobar_distrito(distrito, id_proyecto):
    """
    Comprueba si la id del proyecto es del distrito
    :param distrito: int
    :param id_proyecto: int
    :return: True si son del mismo distrito. False si no
    """
    print("comprobar distrito con distrito {} de tipo {} y id_proyecto {} de tipo {}".format(distrito, type(distrito), id_proyecto, type(id_proyecto)))
    search = ["geozone_id"]
    try:
        propuestas_df = pd.read_csv("{}/functions/propuestas/bd_propuestas.csv".format(path_proyecto), sep=",",
                                    quotechar='"', error_bad_lines=False)
    except:
        print("no existe el archivo de propuestas")
    try:
        propuesta = propuestas_df.loc[propuestas_df["id"] == id_proyecto]
        distrito = int(distrito)
        geozone = int(propuesta[search[0]].values[0])
    except:
        print("Fallo al pasar a int")
        return False
    print("Geozone: {} ->{} distrito {} ->{}".format(geozone,type(geozone), distrito, type(distrito)))
    return geozone == distrito

def get_presupuesto_distrito(distrito):
    """
    Devuelve el prsupuesto dado un distrito
    :param distrito: int
    :return: int
    """
    distrito = int(distrito)
    distrito_dict = {}
    try:
        f = open("{}/functions/propuestas/{}".format(path_proyecto,nombre_archivo_prop_distr), "r")
    except:
        print("No se puede abrir el fichero csv con los presupuestos por distritos")
        return False
    lines = f.readlines()

    try:
        for line in lines:
            id_distrito, presupuesto = line.split(",")
            id_distrito = int(id_distrito)
            presupuesto = int(presupuesto)

            distrito_dict[id_distrito] = presupuesto

    except:
        print("Fallo en el formato del csv {}".format(nombre_archivo_prop_distr))
        return False

    res = distrito_dict.get(distrito, None)
    if res is None:
        print("El distrito {} no existe".format(distrito))
        return False

    return res

if __name__ == '__main__':
    print(get_presupuesto_distrito(1))