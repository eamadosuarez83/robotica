"""Escena mesa-base-camara-huevo-pinza: calcula la pose del huevo
vista desde la pinza cerrando el grafo de transformaciones, y verifica
cerrando un ciclo completo (Bloque 10, Tema 10.6).

Correr con:
    python codigo/bloque_10/escena_mesa_camara_huevo.py
"""

import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from robotica.homogeneas import inversa_homogenea, rt2homogenea  # noqa: E402
from robotica.rotaciones import rotz  # noqa: E402


def main() -> None:
    # Transformaciones conocidas de la escena (Tema 10.6, figura del bloque).
    T_mesa_base = rt2homogenea(np.eye(3), (0.50, 0.0, 0.0))
    T_base_camara = rt2homogenea(rotz(np.radians(180)), (0.10, 0.0, 0.60))
    T_camara_huevo = rt2homogenea(np.eye(3), (0.05, 0.02, 0.40))
    T_base_pinza = rt2homogenea(rotz(np.radians(30)), (0.30, 0.15, 0.10))

    # Lo que se busca: T_pinza_huevo, sin ninguna medición directa entre ambos.
    T_base_huevo = T_base_camara @ T_camara_huevo
    T_pinza_huevo = inversa_homogenea(T_base_pinza) @ T_base_huevo

    print("T_base_huevo (vía cámara):\n", np.round(T_base_huevo, 4))
    print("\nT_pinza_huevo (lo buscado):\n", np.round(T_pinza_huevo, 4))
    print(f"\nEl huevo está a {np.linalg.norm(T_pinza_huevo[:3, 3]):.3f} m de la pinza.")

    # Verificación: cerrar el ciclo completo mesa -> base -> pinza -> huevo ->
    # cámara -> base -> mesa debe dar la identidad.
    ciclo = (
        T_mesa_base
        @ T_base_pinza
        @ T_pinza_huevo
        @ inversa_homogenea(T_camara_huevo)
        @ inversa_homogenea(T_base_camara)
        @ inversa_homogenea(T_mesa_base)
    )
    print("\nCiclo cerrado (debe ser la identidad):\n", np.round(ciclo, 6))
    assert np.allclose(ciclo, np.eye(4), atol=1e-9)
    print("\nOK: el ciclo cierra en la identidad, las transformaciones son consistentes.")


if __name__ == "__main__":
    main()
