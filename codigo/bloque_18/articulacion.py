"""La articulación de todo el Bloque 18: la misma del Bloque 17
(motor DC + reductor + eslabón), ahora con gravedad.

    J θ'' + b_eff θ' = K u - τ_g cos θ

u: voltaje [V], saturado en ±U_MAX por el driver.
θ: ángulo del eslabón medido desde la horizontal [rad].
K = Kt/R: par por voltio a velocidad cero [N·m/V].
τ_g: par de gravedad con el eslabón horizontal, ya visto desde el lado
del motor (dividido por el reductor, Bloque 16) [N·m].

No se corre solo: lo importan los demás scripts del bloque.
"""

import control
import numpy as np

J, b, Kt, Ke, R = 0.02, 0.01, 0.05, 0.05, 2.0   # Bloque 17
B_EFF = b + Kt * Ke / R          # 0.01125 N·m·s
K = Kt / R                       # 0.025 N·m/V
TAU_G = 0.1                      # N·m  -> 4 V para sostenerlo horizontal
U_MAX = 12.0                     # V

# Planta lineal sin gravedad, para python-control (Bloque 17, Tema 17.3).
G = control.tf([K], [J, B_EFF, 0])


def dinamica(x, u, tau_g=TAU_G):
    """dx/dt para x = [θ, θ']; la medición es θ = x[0]."""
    theta, omega = x
    return np.array([omega, (K * u - B_EFF * omega - tau_g * np.cos(theta)) / J])


def metricas(t, y, referencia, banda=0.02):
    """Sobrepaso [%], tiempo de establecimiento [s] y error final [rad]
    de una respuesta y(t) que arranca en y[0] y va hacia `referencia`."""
    salto = referencia - y[0]
    sobrepaso = max(0.0, (np.max((y - y[0]) / salto) - 1) * 100)
    fuera = np.abs(y - referencia) > banda * abs(salto)
    if not fuera.any():
        t_est = 0.0
    elif fuera[-1]:
        t_est = np.nan          # nunca entró a la banda para quedarse
    else:
        t_est = t[np.where(fuera)[0][-1] + 1]
    return sobrepaso, t_est, referencia - y[-1]
