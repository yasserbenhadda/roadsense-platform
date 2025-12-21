from shapely.geometry import Point

def compute_fissure_position(base_lon: float, base_lat: float, x: float, y: float) -> Point:
    """
    Calcule la position géographique d'une fissure à partir :
    - de la position GPS de base (base_lon, base_lat)
    - de la position de la box (x, y) en pixels

    Version simple pour l'instant :
    - On ignore x, y
    - On renvoie simplement le point de base (à améliorer plus tard)
    """

    # TODO: plus tard, utiliser x, y + paramètres caméra pour affiner la position
    return Point(base_lon, base_lat)
