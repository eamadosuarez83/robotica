"""Romperlo a proposito (Bloque 11, Tema 11.6):
1) evaluar una tabla DH MODIFICADA con la formula ESTANDAR (error de
   convencion), y
2) invertir el signo de un alpha en una tabla estandar valida.

Correr con:
    python codigo/bloque_11/romper_convencion_dh.py
"""

import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from robotica.dh import directa, matriz_dh  # noqa: E402
from robotica.rotaciones import rotx, rotz  # noqa: E402


def matriz_dh_modificada(theta, d, a, alpha):
    """A_mod = rotx(alpha_prev) @ translx(a_prev) @ rotz(theta) @ translz(d).

    Aquí, por simplicidad del ejemplo, alpha y a en la fila i ya son
    los "alpha_{i-1}, a_{i-1}" de la convención modificada (Craig).
    """
    Rx = np.eye(4)
    Rx[:3, :3] = rotx(alpha)
    Tx = np.eye(4)
    Tx[0, 3] = a
    Rz = np.eye(4)
    Rz[:3, :3] = rotz(theta)
    Tz = np.eye(4)
    Tz[2, 3] = d
    return Rx @ Tx @ Rz @ Tz


def parte1_convencion_equivocada():
    # Tabla DH pensada en convención MODIFICADA para un brazo simple de 2 GDL.
    dh_mod = [[0, 0, 0, 0, 0], [0, 0, 10.0, np.pi / 2, 0]]
    q = [np.radians(30), np.radians(45)]

    T_correcta = np.eye(4)
    for fila, qi in zip(dh_mod, q):
        theta, d, a, alpha, _ = fila
        T_correcta = T_correcta @ matriz_dh_modificada(theta + qi, d, a, alpha)

    T_incorrecta = directa(dh_mod, q)   # error: fórmula estándar sobre tabla modificada

    print("=== Evaluar una tabla MODIFICADA con la fórmula ESTÁNDAR ===")
    print(f"Posición correcta (fórmula modificada):   {np.round(T_correcta[:3,3], 3)}")
    print(f"Posición incorrecta (fórmula estándar):   {np.round(T_incorrecta[:3,3], 3)}")
    print(f"Coinciden: {np.allclose(T_correcta, T_incorrecta)}\n")


def parte2_signo_de_alpha():
    L1, L2, L3 = 15.0, 12.0, 10.0
    dh_correcta = [[0, L1, 0, np.pi / 2, 0], [0, 0, L2, 0, 0], [0, 0, L3, 0, 0]]
    dh_alpha_invertido = [[0, L1, 0, -np.pi / 2, 0], [0, 0, L2, 0, 0], [0, 0, L3, 0, 0]]

    # Con q2=q3=0 el brazo queda extendido en un plano que oculta el
    # efecto del signo de alpha1 en la posición (aunque la orientación ya
    # difiere). Con q2 != 0 la diferencia se ve también en la posición.
    q = [np.radians(30), np.radians(45), 0.0]
    T_correcta = directa(dh_correcta, q)
    T_roto = directa(dh_alpha_invertido, q)

    print("=== Invertir el signo de alpha en la primera fila (q1=30°) ===")
    print(f"Posición correcta (alpha1=+90°): {np.round(T_correcta[:3,3], 2)}")
    print(f"Posición con alpha1=-90°:        {np.round(T_roto[:3,3], 2)}")
    print("El brazo cambia de plano de trabajo: alpha define la torsión entre ejes")
    print("consecutivos, y su signo decide de qué lado queda el siguiente eslabón.")


if __name__ == "__main__":
    parte1_convencion_equivocada()
    parte2_signo_de_alpha()
