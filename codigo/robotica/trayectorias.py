"""Generacion de trayectorias (Bloque 19).

Espacio articular: interpolador_lineal, perfil_trapezoidal e
interpolador_trapezoidal se portan casi 1:1 de trayectorias.py de
robotica-manipuladores (son agnosticas a la unidad de q: sirven
igual en radianes que en grados). interpolador_cubico,
interpolador_quintico y perfil_s son originales (no estan en
manipuladores).

Espacio cartesiano: linea, circulo, polilinea y resolver_trayectoria
se portan de robotica-manipuladores, adaptando resolver_trayectoria a
que las inversas de este curso (Bloque 12) devuelven RADIANES (alla
grados), por lo que la comprobacion de limites articulares convierte
a grados antes de llamar a Brazo.dentro_de_limites (Bloque 11).
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np

__all__ = [
    "interpolador_lineal", "perfil_trapezoidal", "interpolador_trapezoidal",
    "interpolador_cubico", "interpolador_quintico", "perfil_s",
    "linea", "circulo", "polilinea",
    "ResultadoTrayectoria", "resolver_trayectoria",
]


# ---------------------------------------------------------------- articular

def interpolador_lineal(Q, t, n_puntos=10):
    """Interpolación lineal por tramos.

    ``Q`` son los valores por los que pasa la articulación (cualquier
    unidad); ``t[1]-t[0]`` es la duración de cada tramo y ``t[-1]`` el
    tiempo final. Devuelve ``(Qn, tn)``; ``Qn`` termina exactamente en
    ``Q[-1]`` (ver Bloque 19, Tema 19.6, el error histórico de
    truncar el último punto de cada tramo sin agregar el final).
    """
    Q = np.asarray(Q, dtype=float)
    T = t[1] - t[0]
    ts = np.linspace(0, T, n_puntos)
    tramos = [(q1 - q0) * ts[:-1] / T + q0 for q0, q1 in zip(Q[:-1], Q[1:])]
    Qn = np.concatenate(tramos + [Q[-1:]])
    return Qn, np.linspace(t[0], t[-1], Qn.size)


def perfil_trapezoidal(q0, q1, V=1.0, a=2.0, n_puntos=10):
    """Un tramo con perfil de velocidad trapezoidal.

    Acelera con ``a`` hasta la velocidad ``V``, avanza a velocidad
    constante y frena con ``-a``. Si el tramo es tan corto que no
    alcanza ``V``, el perfil queda triangular. Devuelve
    ``(t, q, qd, qdd)``.
    """
    D, s = abs(q1 - q0), np.sign(q1 - q0)
    if D == 0:
        t = np.zeros(n_puntos)
        return t, np.full(n_puntos, float(q0)), np.zeros(n_puntos), np.zeros(n_puntos)
    Vp = min(V, np.sqrt(a * D))
    tao = Vp / a
    T = D / Vp + tao
    t = np.linspace(0, T, n_puntos)
    acel, crucero, fren = t <= tao, (t > tao) & (t <= T - tao), t > T - tao
    q = np.where(acel, q0 + s * a / 2 * t**2,
                 np.where(crucero, q0 - s * Vp**2 / (2 * a) + s * Vp * t,
                          q1 - s * a / 2 * (T - t) ** 2))
    qd = np.where(acel, s * a * t, np.where(crucero, s * Vp, s * a * (T - t)))
    qdd = np.where(acel, s * a, np.where(crucero, 0.0, -s * a))
    return t, q, qd, qdd


def interpolador_trapezoidal(Q, t, V=1.0, a=2.0, n_puntos=10):
    """Interpolación trapezoidal por tramos (solo usa ``t[0]`` y ``t[-1]``)."""
    Q = np.asarray(Q, dtype=float)
    tramos = [perfil_trapezoidal(q0, q1, V, a, n_puntos)[1][:-1] for q0, q1 in zip(Q[:-1], Q[1:])]
    Qn = np.concatenate(tramos + [Q[-1:]])
    return Qn, np.linspace(t[0], t[-1], Qn.size)


def _resolver_polinomio(condiciones, T):
    """Resuelve los coeficientes de un polinomio dado un conjunto de
    condiciones [(orden_derivada, t, valor), ...]. Sistema lineal
    general, evita transcribir formulas cerradas propensas a error.
    """
    n = len(condiciones)
    A = np.zeros((n, n))
    b = np.zeros(n)
    for fila, (orden, t, valor) in enumerate(condiciones):
        for potencia in range(orden, n):
            coef = 1
            for k in range(orden):
                coef *= (potencia - k)
            A[fila, potencia] = coef * t ** (potencia - orden)
        b[fila] = valor
    return np.linalg.solve(A, b)


def interpolador_cubico(q0, q1, qd0, qd1, T, n_puntos=50):
    """Polinomio cúbico con posición y velocidad de frontera dadas
    (Bloque 19, Tema 19.2). Devuelve ``(t, q, qd, qdd)``.
    """
    coef = _resolver_polinomio([(0, 0, q0), (1, 0, qd0), (0, T, q1), (1, T, qd1)], T)
    t = np.linspace(0, T, n_puntos)
    q = coef[0] + coef[1] * t + coef[2] * t**2 + coef[3] * t**3
    qd = coef[1] + 2 * coef[2] * t + 3 * coef[3] * t**2
    qdd = 2 * coef[2] + 6 * coef[3] * t
    return t, q, qd, qdd


def interpolador_quintico(q0, q1, qd0, qd1, qdd0, qdd1, T, n_puntos=50):
    """Polinomio de quinto orden con posición, velocidad y aceleración
    de frontera dadas (Bloque 19, Tema 19.2). Devuelve ``(t, q, qd, qdd)``.
    """
    coef = _resolver_polinomio([
        (0, 0, q0), (1, 0, qd0), (2, 0, qdd0),
        (0, T, q1), (1, T, qd1), (2, T, qdd1),
    ], T)
    t = np.linspace(0, T, n_puntos)
    potencias = np.vstack([t**k for k in range(6)])
    q = coef @ potencias
    d_coef = coef[1:] * np.arange(1, 6)
    qd = d_coef @ potencias[:5]
    dd_coef = d_coef[1:] * np.arange(1, 5)
    qdd = dd_coef @ potencias[:4]
    return t, q, qd, qdd


def perfil_s(q0, q1, T, n_puntos=50):
    """Perfil en S simplificado: el caso particular del polinomio
    quíntico con velocidad Y aceleración cero en ambos extremos
    (Bloque 19, Tema 19.3). Jerk continuo y acotado -- a diferencia
    del perfil trapezoidal, sin saltos instantáneos de aceleración.

    No es el perfil trapezoidal-con-esquinas-suavizadas de 7 tramos
    que usan algunos controladores industriales (ver Barrientos /
    Lynch & Park para esa versión); esta es una S suave equivalente,
    más simple de deducir y suficiente para los fines del curso.
    """
    return interpolador_quintico(q0, q1, 0.0, 0.0, 0.0, 0.0, T, n_puntos)


# --------------------------------------------------------------- cartesiano

def linea(P1, P2, n_puntos):
    """``n_puntos`` equiespaciados de ``P1`` a ``P2`` (array ``(n, 3)``)."""
    P1, P2 = np.asarray(P1, float), np.asarray(P2, float)
    s = np.linspace(0, 1, n_puntos)[:, None]
    return P1 + s * (P2 - P1)


def circulo(centro, radio, n_puntos, plano="xz"):
    """Círculo en un plano paralelo a los ejes.

    ``plano="xz"`` recorre ``x=xc+R sin(th)``, ``z=zc+R cos(th)``, con
    la coordenada restante constante.
    """
    c = np.asarray(centro, float)
    th = np.linspace(0, 2 * np.pi, n_puntos)
    i, j = {"xy": (0, 1), "xz": (0, 2), "yz": (1, 2)}[plano]
    P = np.tile(c, (n_puntos, 1))
    P[:, i] = c[i] + radio * np.sin(th)
    P[:, j] = c[j] + radio * np.cos(th)
    return P


def polilinea(vertices, n_por_tramo=2):
    """Une los vértices con rectas de ``n_por_tramo`` puntos."""
    V = np.asarray(vertices, float)
    tramos = [linea(p, q, n_por_tramo)[:-1] for p, q in zip(V[:-1], V[1:])]
    return np.vstack(tramos + [V[-1:]])


@dataclass
class ResultadoTrayectoria:
    """Resultado de ``resolver_trayectoria``.

    ``Q`` son los ángulos (RADIANES) de los puntos resueltos. ``estado``
    vale ``"ok"``, ``"sin_solucion"`` (punto fuera del espacio de
    trabajo, Bloque 12 Tema 12.7) o ``"fuera_de_limites"`` (Bloque 07),
    e ``indice_fallo`` indica en qué punto se detuvo.
    """

    Q: np.ndarray
    estado: str
    indice_fallo: int | None = None

    @property
    def ok(self) -> bool:
        return self.estado == "ok"


def resolver_trayectoria(puntos, inversa, robot=None, solucion=0):
    """Aplica una cinemática inversa (Bloque 12) a cada punto de una
    curva cartesiana (Bloque 19, Tema 19.5).

    ``inversa`` recibe ``(px, py, pz)`` y devuelve un array de
    soluciones en RADIANES (o ``None`` si no es alcanzable). Si se da
    ``robot`` (Bloque 11, `Brazo`), se comprueban sus límites
    articulares (en grados: se convierte `q` antes de verificar).
    """
    Q = []
    for k, P in enumerate(np.asarray(puntos, float)):
        sol = inversa(*P)
        if sol is None:
            return ResultadoTrayectoria(np.array(Q), "sin_solucion", k)
        q = sol[solucion]
        if robot is not None and not robot.dentro_de_limites(np.degrees(q)):
            return ResultadoTrayectoria(np.array(Q), "fuera_de_limites", k)
        Q.append(q)
    return ResultadoTrayectoria(np.array(Q), "ok")
