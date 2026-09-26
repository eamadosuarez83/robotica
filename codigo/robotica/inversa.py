"""Cinematica inversa: metodo geometrico, desacoplo y numerico (Bloque 12).

Porta el mecanismo de `inversa/geometrica.py` y `inversa/desacoplo.py`
de robotica-manipuladores, adaptado a RADIANES (alla las inversas
devuelven grados; ver nota al inicio del Bloque 12). `inversa_numerica`
es original de este curso: usa una Jacobiana estimada por diferencias
finitas (Bloque 04) porque la Jacobiana analitica se deduce recien en
el Bloque 13.

Convencion: cada funcion devuelve un array (k, n) con las k soluciones
encontradas (una fila por solucion, n articulaciones), o None si el
punto no es alcanzable -- igual que robotica-manipuladores.
"""

from __future__ import annotations

from collections.abc import Callable

import numpy as np

from .dh import directa

__all__ = [
    "inv_2r_geometrica", "inv_3r_geometrica",
    "inv_curso_6gdl", "inv_abb_6gdl",
    "jacobiana_numerica_posicion", "inversa_numerica",
]


# ------------------------------------------------------------- geométrico

def inv_2r_geometrica(x: float, y: float, L1: float, L2: float) -> np.ndarray | None:
    """Inversa geométrica del brazo 2R plano (Bloque 01, Bloque 12 Tema 12.2).

    Devuelve un array (2, 2): [[t1_arriba, t2_arriba], [t1_abajo, t2_abajo]]
    en radianes, o None si (x, y) está fuera de alcance.
    """
    r2 = x * x + y * y
    cos_t2 = (r2 - L1**2 - L2**2) / (2 * L1 * L2)
    if abs(cos_t2) > 1.0:
        return None
    sin_t2 = np.sqrt(1.0 - cos_t2**2)
    t2 = np.array([np.arctan2(sin_t2, cos_t2), np.arctan2(-sin_t2, cos_t2)])

    beta = np.arctan2(y, x)
    alfa = np.arctan2(L2 * np.sin(t2), L1 + L2 * np.cos(t2))
    t1 = beta - alfa

    return np.column_stack([t1, t2])


def inv_3r_geometrica(px: float, py: float, pz: float,
                       L1: float, L2: float, L3: float) -> np.ndarray | None:
    """Inversa geométrica del 3R antropomórfico `curso_3gdl` (Bloque 11):

    tabla DH [[0,L1,0,pi/2,0],[0,0,L2,0,0],[0,0,L3,0,0]]. Desacopla la
    base (t1) y resuelve el resto como un 2R en el plano vertical.

    Devuelve un array (2, 3) con las dos soluciones (codo arriba/abajo)
    en radianes, o None si el punto no es alcanzable.
    """
    t1 = np.arctan2(py, px)
    r = np.hypot(px, py)
    sol_plano = inv_2r_geometrica(r, pz - L1, L2, L3)
    if sol_plano is None:
        return None
    return np.column_stack([np.full(2, t1), sol_plano])


# --------------------------------------------------------------- desacoplo
# Port fiel de inversa/desacoplo.py de robotica-manipuladores (mismo
# mecanismo; unica diferencia: aqui se devuelven RADIANES, no grados).

def _elementos_orientacion(T):
    return T[0, 0], T[1, 0], T[0, 1], T[1, 1], T[0, 2], T[1, 2], T[2, 2]


def inv_curso_6gdl(T: np.ndarray, L1=15.0, L2=12.0, L3=10.0, L4=5.0) -> np.ndarray | None:
    """Inversa por desacoplo cinemático de `curso_6gdl` (Bloque 12, Tema 12.4).

    Port de `inv_curso_6gdl` de robotica-manipuladores (`inv_Six.m`).
    T: pose deseada 4x4 (Bloque 10). Devuelve un array (2, 6) en
    radianes (dos soluciones de muñeca arriba/abajo por cada una de las
    dos de codo), o None si la posición no es alcanzable.
    """
    T = np.asarray(T, dtype=float)
    pm = T[:3, 3] - L4 * T[:3, 2]
    pmx, pmy, pmz = pm
    q1 = np.arctan2(pmy, pmx)
    b = np.sqrt(pmx**2 + pmy**2 + (pmz - L1) ** 2)
    sin_q3 = (b**2 - L2**2 - L3**2) / (2 * L2 * L3)
    if abs(sin_q3) > 1:
        return None
    q3 = np.array([np.arctan2(sin_q3, np.sqrt(1 - sin_q3**2)),
                   np.arctan2(sin_q3, -np.sqrt(1 - sin_q3**2))])
    beta = np.arctan2(pmz - L1, np.hypot(pmx, pmy))
    alfa = np.arctan2(L3 * np.sin(np.pi / 2 - q3), L2 + L3 * np.cos(np.pi / 2 - q3))
    q2 = alfa - beta
    dh3 = [[0, L1, 0, -np.pi / 2, 0], [0, 0, L2, 0, 0], [0, 0, 0, np.pi / 2, 0]]
    soluciones = []
    for q2i, q3i in zip(q2, q3):
        R = np.linalg.inv(directa(dh3, [q1, q2i, q3i])) @ T
        nx, ny, sx, sy, ax, ay, az = _elementos_orientacion(R)
        q4 = np.arctan2(ay, ax)
        q5 = np.arctan2(ax * np.cos(q4) + ay * np.sin(q4), az)
        q6 = np.arctan2(ny * np.cos(q4) - nx * np.sin(q4), sy * np.cos(q4) - sx * np.sin(q4))
        soluciones.append([q1, q2i, q3i, q4, q5, q6])
    return np.array(soluciones)


def inv_abb_6gdl(T: np.ndarray, L1=78.0, L2=32.0, L3=127.5, L4=114.2, L5=20.0) -> np.ndarray | None:
    """Inversa por desacoplo cinemático de `abb_6gdl` (ABB IRB 6600, Bloque 07).

    Port de `inv_abb_6gdl` de robotica-manipuladores (`inv_6.m`). El
    hombro está desplazado L2 respecto al eje 1 (Bloque 11, Tema 11.5),
    por eso se trabaja con `r - L2` en vez de `r`. Devuelve (2, 6) en
    radianes, o None si no es alcanzable.
    """
    T = np.asarray(T, dtype=float)
    pm = T[:3, 3] - L5 * T[:3, 2]
    pmx, pmy, pmz = pm
    q1 = np.arctan2(pmy, pmx)
    r = np.hypot(pmx, pmy)
    b = np.sqrt((r - L2) ** 2 + (pmz - L1) ** 2)
    sin_q3 = (L4**2 + L3**2 - b**2) / (2 * L4 * L3)
    if abs(sin_q3) > 1:
        return None
    q3 = np.array([np.arctan2(sin_q3, np.sqrt(1 - sin_q3**2)),
                   np.arctan2(sin_q3, -np.sqrt(1 - sin_q3**2))])
    beta = np.arctan2(pmz - L1, r - L2)
    alfa = np.arctan2(L4 * np.sin(np.pi / 2 - q3), L3 - L4 * np.cos(np.pi / 2 - q3))
    q2 = np.pi / 2 - beta - alfa
    dh3 = [[0, L1, L2, -np.pi / 2, 0], [-np.pi / 2, 0, L3, 0, 0], [0, 0, 0, -np.pi / 2, 0]]
    soluciones = []
    for q2i, q3i in zip(q2, q3):
        R = np.linalg.inv(directa(dh3, [q1, q2i, q3i])) @ T
        nx, ny, sx, sy, ax, ay, az = _elementos_orientacion(R)
        q4 = np.arctan2(ay, ax)
        q5 = np.arctan2(-ax * np.cos(q4) - ay * np.sin(q4), az)
        q6 = np.arctan2(-nx * np.sin(q4) + ny * np.cos(q4), sy * np.cos(q4) - sx * np.sin(q4))
        soluciones.append([q1, q2i, q3i, q4, q5, q6])
    return np.array(soluciones)


# --------------------------------------------------------------- numérico

def jacobiana_numerica_posicion(dh, q, h: float = 1e-6) -> np.ndarray:
    """Jacobiana de posición (3, n) estimada por diferencias finitas
    (Bloque 04, Tema 4.6). La versión analítica se deduce en el Bloque 13.
    """
    q = np.asarray(q, dtype=float)
    n = len(q)
    J = np.zeros((3, n))
    p0 = directa(dh, q)[:3, 3]
    for j in range(n):
        dq = np.zeros(n)
        dq[j] = h
        p1 = directa(dh, q + dq)[:3, 3]
        J[:, j] = (p1 - p0) / h
    return J


def inversa_numerica(dh, objetivo, q0, metodo: str = "amortiguado",
                      lam: float = 0.05, alpha: float = 1.0,
                      tol: float = 1e-8, max_iter: int = 500,
                      ) -> tuple[np.ndarray, bool]:
    """Cinemática inversa numérica de posición, para cualquier tabla DH.

    metodo: "pseudo_inversa" (Newton-Raphson/Gauss-Newton), "transpuesta"
    (Jacobiana transpuesta, más lenta pero nunca explota), o "amortiguado"
    (mínimos cuadrados amortiguados, Bloque 12 Tema 12.5).

    Devuelve (q, convergio): q es la mejor aproximación encontrada;
    convergio es True si ||error|| < tol al terminar.
    """
    q = np.array(q0, dtype=float)
    objetivo = np.asarray(objetivo, dtype=float)

    for _ in range(max_iter):
        p = directa(dh, q)[:3, 3]
        error = objetivo - p
        if np.linalg.norm(error) < tol:
            return q, True

        J = jacobiana_numerica_posicion(dh, q)

        if metodo == "transpuesta":
            dq = alpha * (J.T @ error)
        elif metodo == "pseudo_inversa":
            dq = np.linalg.pinv(J) @ error
        elif metodo == "amortiguado":
            n = J.shape[0]
            dq = J.T @ np.linalg.solve(J @ J.T + lam**2 * np.eye(n), error)
        else:
            raise ValueError(f"método desconocido: {metodo!r}")

        q = q + dq

    error_final = objetivo - directa(dh, q)[:3, 3]
    return q, bool(np.linalg.norm(error_final) < tol)
