"""Dos fallas reales de interpoladores por tramos (Bloque 19, Tema 19.2).

1. El bug documentado en robotica-manipuladores (docs/correcciones.md,
   caso 5): `Interpolador_lineal.m` descartaba el último punto de cada
   tramo (para no repetirlo en el siguiente) y nunca agregaba el punto
   final. De 0° a 90° el brazo terminaba en 80°. Aquí se reproduce la
   lógica original, traducida línea por línea.

2. La versión corregida de manipuladores ya llega, pero reparte los
   puntos en un eje de tiempo uniforme, linspace(t0, tf, n). Cada tramo
   trapezoidal dura lo que sus límites piden; si los tramos duran
   distinto, estirarlos todos a la misma cantidad de puntos por segundo
   cambia sus velocidades: los límites dejan de cumplirse.

Correr con:
    python codigo/bloque_19/romper_ultimo_punto.py

Salida esperada: el original termina en 80° en vez de 90°; con tiempo
uniforme la velocidad máxima medida no es la pedida, y con el tiempo
real (robotica.trayectorias) sí.
"""

import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from robotica.trayectorias import interpolador_lineal, interpolador_trapezoidal  # noqa: E402


def interpolador_lineal_original(Q, t):
    """Traducción línea por línea del Interpolador_lineal.m ANTES de la
    corrección de 2026 (N = 10 puntos por tramo)."""
    T = t[1] - t[0]
    N = 10
    Qn = []
    for i in range(1, len(Q)):
        q0, q1 = Q[i - 1], Q[i]
        ts = np.linspace(0, T, N)
        q = (q1 - q0) * ts / T + q0
        Qn.extend(q[:-1])          # q(1:end-1): el último es el primero del siguiente...
    return np.array(Qn)            # ...pero el del último tramo nunca se agrega


def main() -> None:
    print("1. Interpolador lineal original (antes de la corrección)")
    for Q in ([0, np.pi / 2], [0, np.pi / 2, -np.pi / 6]):
        Qn = interpolador_lineal_original(Q, [0, 1])
        _, Qc = interpolador_lineal(Q, np.arange(len(Q)))
        print(f"   pedido: {np.degrees(Q[-1]):6.1f}°, original termina en "
              f"{np.degrees(Qn[-1]):6.1f}°, corregido en {np.degrees(Qc[-1]):6.1f}°")
    print("   Con N puntos por tramo se pierde 1/(N-1) del último tramo: 90°/9 = 10°.")

    print("\n2. Tiempo uniforme contra tiempo real (V = 1 rad/s, a = 2 rad/s²)")
    Q = [0.0, 1.5, 1.2, -0.5]
    V, a = 1.0, 2.0
    t_real, Qn = interpolador_trapezoidal(Q, V=V, a=a, n_puntos=200)
    for nombre, t in (("tiempo real", t_real),
                      ("uniforme en [0, 4] s", np.linspace(0, 4, Qn.size)),
                      ("uniforme en [0, t_real]", np.linspace(0, t_real[-1], Qn.size))):
        v = np.gradient(Qn, t)
        print(f"   {nombre:<24s} dura {t[-1]:.2f} s, |v| máx medida = {np.abs(v).max():.3f} rad/s")
    print("   Aun con la duración total correcta, el tiempo uniforme le da a cada tramo")
    print("   la misma cantidad de puntos por segundo: el tramo corto (1.5 -> 1.2 rad)")
    print("   se estira y los largos se aprietan por encima de V.")


if __name__ == "__main__":
    main()
