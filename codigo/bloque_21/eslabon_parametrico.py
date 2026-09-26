"""Eslabones parametricos de curso_3gdl con build123d: masa, centro
de masa y tensor de inercia, verificados contra la formula analitica
del Bloque 06 (Bloque 21, Temas 21.2 y 21.3).

Correr con:
    python codigo/bloque_21/eslabon_parametrico.py
"""

import numpy as np
from build123d import Box, BuildPart

DENSIDAD_ALUMINIO = 2700.0  # kg/m3
ANCHO, ALTO = 0.03, 0.02    # m, seccion transversal del eslabon
L1, L2, L3 = 0.15, 0.12, 0.10  # m, curso_3gdl (Bloque 11)


def construir_eslabon(largo, ancho=ANCHO, alto=ALTO):
    """Prisma de `largo` x `ancho` x `alto`, centrado en el origen,
    largo a lo largo de X (Bloque 06, Tema 6.4)."""
    with BuildPart() as eslabon:
        Box(largo, ancho, alto)
    return eslabon.part


def propiedades_fisicas(part, densidad=DENSIDAD_ALUMINIO):
    """(masa, centro_de_masa, tensor_inercia_fisico).

    build123d da masa/inercia GEOMETRICAS (densidad=1); hay que
    multiplicar por la densidad real (Bloque 21, Tema 21.3).
    """
    masa = part.volume * densidad
    c = part.center()
    com = np.array([c.X, c.Y, c.Z])
    tensor = np.array(part.matrix_of_inertia) * densidad
    return masa, com, tensor


def tensor_analitico(masa, largo, ancho, alto):
    """Formula del Bloque 06, Tema 6.4, para un prisma homogeneo."""
    Ixx = masa * (ancho**2 + alto**2) / 12
    Iyy = masa * (largo**2 + alto**2) / 12
    Izz = masa * (largo**2 + ancho**2) / 12
    return np.diag([Ixx, Iyy, Izz])


def main() -> None:
    for nombre, largo in [("eslabón 1 (L1)", L1), ("eslabón 2 (L2)", L2), ("eslabón 3 (L3)", L3)]:
        part = construir_eslabon(largo)
        masa, com, tensor = propiedades_fisicas(part)
        tensor_esperado = tensor_analitico(masa, largo, ANCHO, ALTO)
        error = np.max(np.abs(tensor - tensor_esperado))

        print(f"\n=== {nombre}: largo={largo*100:.0f} cm ===")
        print(f"  masa: {masa*1000:.1f} g")
        print(f"  centro de masa: {np.round(com, 4)} m")
        print(f"  tensor de inercia (build123d):\n{np.round(tensor, 8)}")
        print(f"  tensor de inercia (analítico, Bloque 06):\n{np.round(tensor_esperado, 8)}")
        print(f"  error máximo: {error:.2e}")
        assert error < 1e-9


if __name__ == "__main__":
    main()
