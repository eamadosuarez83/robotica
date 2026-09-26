"""Verifica la cinematica directa del 2R contra el Bloque 01, calcula
la del 3R antropomorfico real (curso_3gdl, robotica-manipuladores) y
compara con roboticstoolbox.DHRobot (Bloque 11, Temas 11.4 y 11.5).

Correr con:
    python codigo/bloque_11/dh_2r_3r.py
"""

import sys
from pathlib import Path

import numpy as np
from roboticstoolbox import DHRobot, RevoluteDH

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from robotica.dh import directa  # noqa: E402


def verificar_2r():
    L1, L2 = 0.30, 0.20
    dh = [[0, 0, L1, 0, 0], [0, 0, L2, 0, 0]]
    theta1, theta2 = np.radians(40), np.radians(30)
    T = directa(dh, [theta1, theta2])
    x, y = T[0, 3], T[1, 3]
    print("=== 2R plano (Bloque 01) ===")
    print(f"directa(dh,[40°,30°]) -> ({x:.3f}, {y:.3f}) m")
    print("Esperado (Bloque 01, Tema 1.4): (0.298, 0.381) m")
    assert abs(x - 0.298) < 1e-3 and abs(y - 0.381) < 1e-3
    print("OK\n")


def curso_3gdl():
    """Tabla DH de curso_3gdl, robotica-manipuladores/docs/robots.md."""
    L1, L2, L3 = 15.0, 12.0, 10.0   # cm
    dh = [[0, L1, 0, np.pi / 2, 0],
          [0, 0, L2, 0, 0],
          [0, 0, L3, 0, 0]]
    return dh, (L1, L2, L3)


def verificar_3r_vs_roboticstoolbox():
    dh, (L1, L2, L3) = curso_3gdl()

    print("=== curso_3gdl (3R antropomórfico real) ===")
    T0 = directa(dh, [0, 0, 0])
    print(f"q=(0,0,0)  -> pinza en {np.round(T0[:3, 3], 3)} cm "
          f"(esperado: ({L2+L3:.0f}, 0, {L1:.0f}))")
    assert np.allclose(T0[:3, 3], [L2 + L3, 0, L1], atol=1e-9)

    # Comparación con la librería profesional (FILOSOFIA.md: a mano ->
    # propia -> librería profesional).
    robot = DHRobot([
        RevoluteDH(d=L1, a=0, alpha=np.pi / 2),
        RevoluteDH(d=0, a=L2, alpha=0),
        RevoluteDH(d=0, a=L3, alpha=0),
    ], name="curso_3gdl")

    for q_deg in [(0, 0, 0), (30, 45, -20), (90, -30, 60)]:
        q = np.radians(q_deg)
        T_propia = directa(dh, q)
        T_rtb = robot.fkine(q).A
        error = np.max(np.abs(T_propia - T_rtb))
        print(f"q={q_deg}°: error máx. propia vs. roboticstoolbox = {error:.2e}")
        assert error < 1e-9
    print("OK: coincide con roboticstoolbox en todas las posturas probadas.\n")


if __name__ == "__main__":
    verificar_2r()
    verificar_3r_vs_roboticstoolbox()
