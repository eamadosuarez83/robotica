"""Dinamica por Lagrange (Bloque 14) y por Newton-Euler recursivo,
caso planar (Bloque 15).

Original de este curso: robotica-manipuladores solo tiene el tensor
de inercia de un prisma (que va al Bloque 06), no dinamica de
manipuladores completa.
"""

from __future__ import annotations

import numpy as np
import sympy as sp

__all__ = [
    "deducir_lagrange", "matriz_masas", "separar_gravedad_y_coriolis",
    "newton_euler_plano",
]


def deducir_lagrange(K, U, coords, t):
    """Deduce las ecuaciones de Lagrange d/dt(dL/dq̇_i) - dL/dq_i = tau_i.

    `K`, `U`: energía cinética y potencial (expresiones de SymPy) en
    función de `coords` (lista de `sp.Function('nombre')(t)`, funciones
    del tiempo) y sus derivadas.
    `t`: el símbolo del tiempo.

    Devuelve `(ecuaciones, q, qdot, qddot)`: las n ecuaciones (lado
    izquierdo; tau_i queda implícito del lado derecho) ya expresadas
    en símbolos algebraicos limpios `q_i`, `q_ip` (q̇_i), `q_ipp` (q̈_i),
    en vez de funciones del tiempo.
    """
    nombres = [str(c.func) for c in coords]
    q = list(sp.symbols(nombres))
    qdot = list(sp.symbols([n + "p" for n in nombres]))
    qddot = list(sp.symbols([n + "pp" for n in nombres]))

    L = K - U
    ecuaciones = []
    for qi_t in coords:
        qi_dot_t = sp.diff(qi_t, t)
        dL_dqidot = sp.diff(L, qi_dot_t)
        d_dt_termino = sp.diff(dL_dqidot, t)
        dL_dqi = sp.diff(L, qi_t)
        ecuaciones.append(sp.expand(d_dt_termino - dL_dqi))

    subs = {}
    for qi_t, qs, qd, qdd in zip(coords, q, qdot, qddot):
        subs[sp.diff(qi_t, t, 2)] = qdd
        subs[sp.diff(qi_t, t)] = qd
        subs[qi_t] = qs
    ecuaciones = [sp.simplify(eq.subs(subs)) for eq in ecuaciones]
    return ecuaciones, q, qdot, qddot


def matriz_masas(ecuaciones, qddot) -> sp.Matrix:
    """M(q): matriz de masas/inercia, los coeficientes de q̈ en cada ecuación.

    Simétrica y definida positiva (Bloque 14, Tema 14.6) para cualquier
    sistema físico bien formado.
    """
    n = len(ecuaciones)
    M = sp.zeros(n, n)
    for i, eq in enumerate(ecuaciones):
        for j, qddj in enumerate(qddot):
            M[i, j] = sp.diff(eq, qddj)
    return sp.simplify(M)


def separar_gravedad_y_coriolis(ecuaciones, qdot, qddot) -> tuple[sp.Matrix, sp.Matrix]:
    """Separa lo que queda de cada ecuación tras quitar M(q)q̈ en G(q)
    (evaluando en q̇=0) y C(q,q̇)q̇ (el resto): M(q)q̈ + C(q,q̇)q̇ + G(q) = tau.

    Cada ecuación es afín en q̈ (M(q) no depende de q̈, Tema 14.4), así
    que el resto sin q̈ se obtiene evaluando directamente en q̈=0 --
    exacto por construcción, sin depender de que una resta simbólica
    como `eq - M·q̈` cancele: si M[i,j] y el coeficiente real de q̈_j
    llegan en formas trigonométricas distintas (p.ej. sin²(q) vs.
    cos(2q)), esa resta puede dejar un residuo de q̈ que ni `expand()`
    ni `simplify()` garantizan cancelar.
    """
    ceros_qddot = {qdd: 0 for qdd in qddot}
    resto = [eq.subs(ceros_qddot) for eq in ecuaciones]
    ceros_qdot = {qd: 0 for qd in qdot}
    G = sp.Matrix([r.subs(ceros_qdot) for r in resto])
    C_qdot = sp.Matrix([sp.simplify(resto[i] - G[i]) for i in range(len(resto))])
    return G, C_qdot


def newton_euler_plano(theta, thetadot, thetaddot, m, L, lc, I, g: float = 9.81) -> np.ndarray:
    """Dinámica inversa por Newton-Euler recursivo, cadena planar de n
    eslabones rotacionales (Bloque 15, Tema 15.1).

    Parámetros (todos array-like de longitud n, SALVO g):
        theta, thetadot, thetaddot : ángulos e incrementos articulares (rad)
        m   : masa de cada eslabón (kg)
        L   : longitud de cada eslabón (m)
        lc  : distancia del origen del eslabón a su centro de masa (m)
        I   : momento de inercia de cada eslabón respecto a su propio
              centro de masa, eje perpendicular al plano (kg·m²)

    Devuelve el vector de pares articulares tau (n,), en el mismo orden
    que las articulaciones (motor 1 primero).

    Recorre las velocidades y aceleraciones hacia afuera (base -> punta,
    Tema 15.1) y las fuerzas hacia adentro (punta -> base), con el truco
    estándar de tratar la gravedad como una aceleración de la base
    (a[0] = [0, g, 0]) para no arrastrar un término G(q) por separado.
    """
    n = len(theta)
    theta = np.asarray(theta, dtype=float)
    thetadot = np.asarray(thetadot, dtype=float)
    thetaddot = np.asarray(thetaddot, dtype=float)

    O = [np.zeros(3)]
    angulos_acumulados = []
    angulo = 0.0
    for i in range(n):
        angulo += theta[i]
        angulos_acumulados.append(angulo)
        O.append(O[-1] + L[i] * np.array([np.cos(angulo), np.sin(angulo), 0.0]))
    C = [O[i] + lc[i] * np.array([np.cos(angulos_acumulados[i]),
                                   np.sin(angulos_acumulados[i]), 0.0])
         for i in range(n)]

    # --- hacia afuera: velocidades y aceleraciones angulares y lineales ---
    omega = [np.zeros(3)]
    alfa = [np.zeros(3)]
    a = [np.array([0.0, g, 0.0])]   # truco de gravedad
    ac = [None]
    for i in range(1, n + 1):
        w = omega[i - 1] + np.array([0.0, 0.0, thetadot[i - 1]])
        al = alfa[i - 1] + np.array([0.0, 0.0, thetaddot[i - 1]])
        r = O[i] - O[i - 1]
        ai = a[i - 1] + np.cross(al, r) + np.cross(w, np.cross(w, r))
        rc = C[i - 1] - O[i - 1]
        aci = a[i - 1] + np.cross(al, rc) + np.cross(w, np.cross(w, rc))
        omega.append(w)
        alfa.append(al)
        a.append(ai)
        ac.append(aci)

    F = [None] + [m[i - 1] * ac[i] for i in range(1, n + 1)]
    N = [None] + [I[i - 1] * alfa[i] for i in range(1, n + 1)]

    # --- hacia adentro: fuerzas y pares en cada articulación ---
    f = [np.zeros(3) for _ in range(n + 2)]
    n_momento = [np.zeros(3) for _ in range(n + 2)]
    tau = np.zeros(n)
    for i in range(n, 0, -1):
        f[i] = f[i + 1] + F[i]
        n_momento[i] = (n_momento[i + 1]
                         + np.cross(C[i - 1] - O[i - 1], F[i])
                         + np.cross(O[i] - O[i - 1], f[i + 1])
                         + N[i])
        tau[i - 1] = n_momento[i][2]
    return tau
