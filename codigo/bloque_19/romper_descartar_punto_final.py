"""Romperlo a proposito: reproduce el error historico documentado en
robotica-manipuladores (docs/correcciones.md, error #5) -- cada tramo
descartaba su ultimo punto (correcto, para no duplicar la union) pero
el destino final NUNCA se agregaba de vuelta -- de modo que el
movimiento se queda corto sin ningun aviso (Bloque 19, Tema 19.6).

Correr con:
    python codigo/bloque_19/romper_descartar_punto_final.py
"""

import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from robotica.trayectorias import interpolador_lineal  # noqa: E402


def interpolador_lineal_con_bug(Q, t, n_puntos=10):
    """Version rota: descarta el ultimo punto de cada tramo (correcto,
    evita duplicar la union) pero SE OLVIDA de agregar Q[-1] al final --
    el error real, ya corregido, de robotica-manipuladores."""
    Q = np.asarray(Q, dtype=float)
    T = t[1] - t[0]
    ts = np.linspace(0, T, n_puntos)
    tramos = [(q1 - q0) * ts[:-1] / T + q0 for q0, q1 in zip(Q[:-1], Q[1:])]
    Qn = np.concatenate(tramos)   # falta "+ [Q[-1:]]" -- el bug es esta ausencia
    return Qn, np.linspace(t[0], t[-1], Qn.size)


def main() -> None:
    Q_deseado = [0.0, 30.0, 60.0, 90.0]   # 4 puntos, 3 tramos

    for n_puntos in (5, 10, 20, 50):
        t = [0.0, 3.0]
        Qn_correcto, _ = interpolador_lineal(Q_deseado, t, n_puntos=n_puntos)
        Qn_roto, _ = interpolador_lineal_con_bug(Q_deseado, t, n_puntos=n_puntos)
        error = Q_deseado[-1] - Qn_roto[-1]
        print(f"n_puntos/tramo={n_puntos:3d}: correcto llega a {Qn_correcto[-1]:6.2f}°, "
              f"con bug se queda en {Qn_roto[-1]:6.2f}° (error {error:+.2f}°, "
              f"{100*error/Q_deseado[-1]:.1f}% del recorrido)")

    print("\nSin ningún mensaje de error: el brazo simplemente se queda corto,")
    print("por una cantidad que depende de cuán fina sea la discretización de")
    print("cada tramo (a más puntos por tramo, menor el error, pero nunca cero).")
    print("Así se documentó el error real en robotica-manipuladores")
    print("(docs/correcciones.md, error #5) antes de corregirse.")


if __name__ == "__main__":
    main()
