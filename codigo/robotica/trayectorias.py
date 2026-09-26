"""Generación de trayectorias (Bloque 19).

Porta `robotica/trayectorias.py` de robotica-manipuladores
(`perfil_trapezoidal`, `interpolador_lineal`, `interpolador_trapezoidal`,
`linea`, `circulo`, `polilinea`, `resolver_trayectoria`), con tres
cambios:

- radianes y metros (allá, grados y milímetros);
- los interpoladores por tramos devuelven el tiempo real de cada punto.
  Allá se reparte `linspace(t[0], t[-1])` sobre todos los puntos, lo que
  deforma el tiempo cuando los tramos duran distinto (Tema 19.2);
- `resolver_trayectoria` recibe la inversa como una función de un solo
  punto y los límites como un array, en vez de un objeto `Robot`.

Originales de este curso: `cubica`, `quintica`, `perfil_s` (jerk
limitado) y `spline_cubica`.
"""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass

import numpy as np

__all__ = [
    "cubica", "quintica", "perfil_trapezoidal", "perfil_s",
    "interpolador_lineal", "interpolador_trapezoidal", "spline_cubica",
    "linea", "circulo", "polilinea", "ResultadoTrayectoria", "resolver_trayectoria",
]


# ----------------------------------------------------------------------------
# Espacio articular: un tramo
# ----------------------------------------------------------------------------

def cubica(q0, qf, T, t, v0=0.0, vf=0.0):
    """Polinomio de grado 3 de q0 a qf en T segundos (Tema 19.2).

    q(t) = a0 + a1 t + a2 t² + a3 t³ con q(0)=q0, q(T)=qf, q'(0)=v0,
    q'(T)=vf. Fuera de [0, T] se queda en el extremo, quieto.
    Devuelve (q, qd, qdd) evaluados en `t`.
    """
    t = np.clip(np.asarray(t, dtype=float), 0.0, T)
    D = qf - q0
    a0, a1 = q0, v0
    a2 = (3 * D - (2 * v0 + vf) * T) / T**2
    a3 = (-2 * D + (v0 + vf) * T) / T**3
    q = a0 + a1 * t + a2 * t**2 + a3 * t**3
    qd = a1 + 2 * a2 * t + 3 * a3 * t**2
    qdd = 2 * a2 + 6 * a3 * t
    return q, qd, qdd


def quintica(q0, qf, T, t, v0=0.0, vf=0.0, a0=0.0, af=0.0):
    """Polinomio de grado 5 de q0 a qf en T segundos (Tema 19.2).

    Fija posición, velocidad y aceleración en los dos extremos: seis
    condiciones, seis coeficientes. Fuera de [0, T] se queda en el
    extremo. Devuelve (q, qd, qdd) evaluados en `t`.
    """
    t = np.clip(np.asarray(t, dtype=float), 0.0, T)
    D = qf - q0
    c0, c1, c2 = q0, v0, a0 / 2
    c3 = (20 * D - (8 * vf + 12 * v0) * T - (3 * a0 - af) * T**2) / (2 * T**3)
    c4 = (-30 * D + (14 * vf + 16 * v0) * T + (3 * a0 - 2 * af) * T**2) / (2 * T**4)
    c5 = (12 * D - 6 * (vf + v0) * T + (af - a0) * T**2) / (2 * T**5)
    q = c0 + c1 * t + c2 * t**2 + c3 * t**3 + c4 * t**4 + c5 * t**5
    qd = c1 + 2 * c2 * t + 3 * c3 * t**2 + 4 * c4 * t**3 + 5 * c5 * t**4
    qdd = 2 * c2 + 6 * c3 * t + 12 * c4 * t**2 + 20 * c5 * t**3
    return q, qd, qdd


def perfil_trapezoidal(q0, q1, V=1.0, a=2.0, n_puntos=10):
    """Un tramo con perfil de velocidad trapezoidal (Tema 19.3).

    Portado de robotica-manipuladores (`Inter_trapezoidal.m`). Acelera
    con `a` [rad/s²] hasta la velocidad `V` [rad/s], avanza a velocidad
    constante y frena con -a. Si el tramo es tan corto que no alcanza V,
    el perfil queda triangular.

    Devuelve (t, q, qd, qdd): tiempo, posición, velocidad y aceleración.
    """
    D, s = abs(q1 - q0), np.sign(q1 - q0)
    if D == 0:
        t = np.zeros(n_puntos)
        return t, np.full(n_puntos, float(q0)), np.zeros(n_puntos), np.zeros(n_puntos)
    Vp = min(V, np.sqrt(a * D))          # velocidad pico
    tao = Vp / a                         # duración de la aceleración
    T = D / Vp + tao                     # duración total
    t = np.linspace(0, T, n_puntos)
    acel, crucero = t <= tao, (t > tao) & (t <= T - tao)
    q = np.where(acel, q0 + s * a / 2 * t**2,
                 np.where(crucero, q0 - s * Vp**2 / (2 * a) + s * Vp * t,
                          q1 - s * a / 2 * (T - t) ** 2))
    qd = np.where(acel, s * a * t, np.where(crucero, s * Vp, s * a * (T - t)))
    qdd = np.where(acel, s * a, np.where(crucero, 0.0, -s * a))
    return t, q, qd, qdd


def _tiempos_s(D, V, A, J):
    """Duraciones (Tj, Ta, Tv) del perfil en S simétrico, con velocidad
    inicial y final cero (Biagiotti y Melchiorri, cap. 3).

    Tj: cada fase de jerk; Ta: toda la aceleración (incluye 2 Tj);
    Tv: crucero. Si D es corto, se bajan V y luego A hasta que quepa.
    """
    # ¿Alcanza a llegar a A antes de llegar a V?
    if V * J >= A**2:
        Tj, Ta = A / J, A / J + V / A
    else:
        Tj = np.sqrt(V / J)
        Ta = 2 * Tj
    Tv = D / V - Ta
    if Tv >= 0:
        return Tj, Ta, Tv
    # No alcanza V: sin crucero.
    if D >= 2 * A**3 / J**2:
        Tj = A / J
        Ta = Tj / 2 + np.sqrt((Tj / 2) ** 2 + D / A)
    else:
        Tj = (D / (2 * J)) ** (1 / 3)
        Ta = 2 * Tj
    return Tj, Ta, 0.0


def perfil_s(q0, q1, V=1.0, A=2.0, J=10.0, n_puntos=100):
    """Un tramo con perfil en S: jerk limitado (Tema 19.3). Original.

    Siete fases de jerk constante (+J, 0, -J, 0, -J, 0, +J): la
    aceleración sube en rampa en vez de saltar. `V` [rad/s], `A`
    [rad/s²] y `J` [rad/s³] son los límites. Si el tramo es corto, no se
    alcanzan V y/o A.

    Como el jerk es constante por fases, cada fase se integra exacta
    (polinomio de grado 3) partiendo del estado al final de la anterior.
    Devuelve (t, q, qd, qdd).
    """
    D, s = abs(q1 - q0), np.sign(q1 - q0)
    if D == 0:
        t = np.zeros(n_puntos)
        return t, np.full(n_puntos, float(q0)), np.zeros(n_puntos), np.zeros(n_puntos)
    Tj, Ta, Tv = _tiempos_s(D, V, A, J)
    fases = [(Tj, J), (Ta - 2 * Tj, 0.0), (Tj, -J), (Tv, 0.0),
             (Tj, -J), (Ta - 2 * Tj, 0.0), (Tj, J)]
    T = 2 * Ta + Tv
    t = np.linspace(0, T, n_puntos)
    q, qd, qdd = np.empty_like(t), np.empty_like(t), np.empty_like(t)

    inicio, p, v, ac = 0.0, 0.0, 0.0, 0.0
    asignado = np.zeros(t.size, dtype=bool)
    for k, (dur, j) in enumerate(fases):
        fin = inicio + dur
        dentro = (~asignado) & ((t <= fin) | (k == len(fases) - 1))
        tau = t[dentro] - inicio
        q[dentro] = p + v * tau + ac * tau**2 / 2 + j * tau**3 / 6
        qd[dentro] = v + ac * tau + j * tau**2 / 2
        qdd[dentro] = ac + j * tau
        asignado |= dentro
        p, v, ac = (p + v * dur + ac * dur**2 / 2 + j * dur**3 / 6,
                    v + ac * dur + j * dur**2 / 2, ac + j * dur)
        inicio = fin
    return t, q0 + s * q, s * qd, s * qdd


# ----------------------------------------------------------------------------
# Espacio articular: varios tramos
# ----------------------------------------------------------------------------

def interpolador_lineal(Q, t_puntos, n_puntos=10):
    """Interpolación lineal por tramos (Tema 19.2).

    Portado de robotica-manipuladores, con el tiempo corregido: `t_puntos`
    es el instante en que se pasa por cada valor de `Q` (mismo largo).
    Devuelve (tn, Qn); Qn termina exactamente en Q[-1].
    """
    Q = np.asarray(Q, dtype=float)
    t_puntos = np.asarray(t_puntos, dtype=float)
    s = np.linspace(0, 1, n_puntos)[:-1]      # el último es el primero del siguiente
    tn = [ta + s * (tb - ta) for ta, tb in zip(t_puntos[:-1], t_puntos[1:])]
    Qn = [qa + s * (qb - qa) for qa, qb in zip(Q[:-1], Q[1:])]
    return np.concatenate(tn + [t_puntos[-1:]]), np.concatenate(Qn + [Q[-1:]])


def interpolador_trapezoidal(Q, V=1.0, a=2.0, n_puntos=10, t0=0.0):
    """Interpolación trapezoidal por tramos (Tema 19.3).

    Portado de robotica-manipuladores, con el tiempo corregido: cada
    tramo dura lo que su perfil necesita, y los tiempos se encadenan.
    Cada tramo arranca y termina quieto. Devuelve (tn, Qn).
    """
    Q = np.asarray(Q, dtype=float)
    tn, Qn, inicio = [], [], t0
    for q0, q1 in zip(Q[:-1], Q[1:]):
        t, q, _, _ = perfil_trapezoidal(q0, q1, V, a, n_puntos)
        tn.append(inicio + t[:-1])
        Qn.append(q[:-1])
        inicio += t[-1]
    return np.concatenate(tn + [[inicio]]), np.concatenate(Qn + [Q[-1:]])


def spline_cubica(t_puntos, Q, t, v0=0.0, vf=0.0):
    """Spline cúbico por los puntos (t_puntos, Q), con velocidad v0 al
    inicio y vf al final (Tema 19.4). Original.

    Un cúbico por tramo; las velocidades en los puntos intermedios se
    eligen para que la aceleración sea continua. Eso da un sistema
    tridiagonal de n-2 ecuaciones (deducido en el Tema 19.4).
    Devuelve (q, qd, qdd) evaluados en `t`.
    """
    tp = np.asarray(t_puntos, dtype=float)
    Q = np.asarray(Q, dtype=float)
    h = np.diff(tp)
    n = len(Q)
    v = np.zeros(n)
    v[0], v[-1] = v0, vf
    if n > 2:
        A = np.zeros((n - 2, n - 2))
        b = np.zeros(n - 2)
        for i in range(1, n - 1):
            fila = i - 1
            if fila > 0:
                A[fila, fila - 1] = h[i]
            A[fila, fila] = 2 * (h[i - 1] + h[i])
            if fila < n - 3:
                A[fila, fila + 1] = h[i - 1]
            b[fila] = 3 * (h[i] * (Q[i] - Q[i - 1]) / h[i - 1]
                           + h[i - 1] * (Q[i + 1] - Q[i]) / h[i])
        b[0] -= h[1] * v0
        b[-1] -= h[n - 3] * vf
        v[1:-1] = np.linalg.solve(A, b)

    t = np.clip(np.asarray(t, dtype=float), tp[0], tp[-1])
    k = np.clip(np.searchsorted(tp, t, side="right") - 1, 0, n - 2)
    q, qd, qdd = cubica(Q[k], Q[k + 1], h[k], t - tp[k], v[k], v[k + 1])
    return q, qd, qdd


# ----------------------------------------------------------------------------
# Espacio cartesiano: curvas (portadas de robotica-manipuladores)
# ----------------------------------------------------------------------------

def linea(P1, P2, n_puntos):
    """`n_puntos` equiespaciados de P1 a P2 (array (n, dim))."""
    P1, P2 = np.asarray(P1, float), np.asarray(P2, float)
    s = np.linspace(0, 1, n_puntos)[:, None]
    return P1 + s * (P2 - P1)


def circulo(centro, radio, n_puntos, plano="xz"):
    """Círculo en un plano paralelo a los ejes (`trayectoria_circulo.m`).

    `plano="xz"` recorre x = xc + R sin(th), z = zc + R cos(th) con y
    constante, igual que el script original.
    """
    c = np.asarray(centro, float)
    th = np.linspace(0, 2 * np.pi, n_puntos)
    i, j = {"xy": (0, 1), "xz": (0, 2), "yz": (1, 2)}[plano]
    P = np.tile(c, (n_puntos, 1))
    P[:, i] = c[i] + radio * np.sin(th)
    P[:, j] = c[j] + radio * np.cos(th)
    return P


def polilinea(vertices, n_por_tramo=2):
    """Une los vértices con rectas de `n_por_tramo` puntos (`trayectoria_dibujo.m`)."""
    V = np.asarray(vertices, float)
    tramos = [linea(p, q, n_por_tramo)[:-1] for p, q in zip(V[:-1], V[1:])]
    return np.vstack(tramos + [V[-1:]])


# ----------------------------------------------------------------------------
# Espacio cartesiano: resolver con la inversa
# ----------------------------------------------------------------------------

@dataclass
class ResultadoTrayectoria:
    """Resultado de `resolver_trayectoria`.

    `Q`: ángulos (rad) de los puntos resueltos, uno por fila. `estado`:
    "ok", "sin_solucion" (punto fuera del espacio de trabajo) o
    "fuera_de_limites". `indice_fallo`: en qué punto se detuvo.
    """
    Q: np.ndarray
    estado: str
    indice_fallo: int | None = None

    @property
    def ok(self) -> bool:
        return self.estado == "ok"


def resolver_trayectoria(puntos, inversa: Callable, solucion: int = 0,
                         limites=None) -> ResultadoTrayectoria:
    """Aplica la cinemática inversa a cada punto de una curva (Tema 19.5).

    `inversa(P)`: recibe un punto y devuelve un array (k, n) con sus
    soluciones, o None (convención de `robotica.inversa`).
    `solucion`: qué fila usar (por ejemplo, 0 = codo arriba en el 2R).
    `limites`: array (n, 2) opcional con [mín, máx] de cada articulación.
    """
    Q = []
    for k, P in enumerate(np.asarray(puntos, float)):
        sol = inversa(P)
        if sol is None:
            return ResultadoTrayectoria(np.array(Q), "sin_solucion", k)
        q = np.asarray(sol[solucion], dtype=float)
        if limites is not None:
            lim = np.asarray(limites, dtype=float)
            if np.any(q < lim[:, 0]) or np.any(q > lim[:, 1]):
                return ResultadoTrayectoria(np.array(Q), "fuera_de_limites", k)
        Q.append(q)
    return ResultadoTrayectoria(np.array(Q), "ok")
