"""Hoja de dimensionamiento: par pico y RMS del hombro del 2R a lo
largo de un movimiento punto a punto, y evaluacion de motores
candidatos con reductor (Bloque 16, Tema 16.6).

Correr con:
    python codigo/bloque_16/hoja_dimensionamiento.py
"""

import sys
from pathlib import Path

import numpy as np
import matplotlib.pyplot as plt

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from robotica.dinamica import newton_euler_plano  # noqa: E402

M1, M2 = 1.3, 0.7      # kg
L1, L2 = 0.30, 0.20    # m


def movimiento_theta1(t, t_final, theta0, theta_f):
    """Perfil suave punto a punto (versoseno): posicion, velocidad y
    aceleracion, con velocidad cero en los extremos."""
    frac = t / t_final
    theta = theta0 + (theta_f - theta0) * (1 - np.cos(np.pi * frac)) / 2
    thetadot = (theta_f - theta0) * (np.pi / t_final) * np.sin(np.pi * frac) / 2
    thetaddot = (theta_f - theta0) * (np.pi / t_final) ** 2 * np.cos(np.pi * frac) / 2
    return theta, thetadot, thetaddot


def par_hombro(t_arr, t_final, theta0, theta_f, theta2_fijo=0.0):
    tau1 = np.zeros_like(t_arr)
    for k, t in enumerate(t_arr):
        th1, th1d, th1dd = movimiento_theta1(t, t_final, theta0, theta_f)
        tau = newton_euler_plano([th1, theta2_fijo], [th1d, 0.0], [th1dd, 0.0],
                                  [M1, M2], [L1, L2], [L1, L2], [0.0, 0.0])
        tau1[k] = tau[0]
    return tau1


def main() -> None:
    t_final = 1.5   # s: movimiento moderado, 90° en 1.5 s
    t_arr = np.linspace(0, t_final, 300)
    tau1 = par_hombro(t_arr, t_final, np.radians(0), np.radians(90))

    tau_pico = np.max(np.abs(tau1))
    tau_rms = np.sqrt(np.mean(tau1**2))
    margen = 1.4

    print(f"Movimiento: hombro de 0° a 90° en {t_final} s")
    print(f"τ pico:  {tau_pico:.3f} N·m")
    print(f"τ RMS:   {tau_rms:.3f} N·m")
    print(f"Con margen de seguridad ({margen}x): "
          f"τ pico={tau_pico*margen:.3f} N·m, τ RMS={tau_rms*margen:.3f} N·m")

    # Catálogo de motores candidatos (V, Kt, Ke, R, tau_continuo)
    motores = {
        "Motor A (pequeño)": dict(V=12, Kt=0.03, Ke=0.03, R=1.5, tau_continuo=0.03),
        "Motor B (mediano)": dict(V=12, Kt=0.06, Ke=0.06, R=1.2, tau_continuo=0.08),
        "Motor C (grande)":  dict(V=24, Kt=0.10, Ke=0.10, R=1.0, tau_continuo=0.15),
    }
    eta = 0.85
    omega1_max = np.max(np.abs(np.gradient(np.unwrap(
        [movimiento_theta1(t, t_final, 0, np.radians(90))[0] for t in t_arr]), t_arr)))

    print(f"\nVelocidad angular máxima del hombro: {omega1_max:.2f} rad/s")
    print(f"\n{'motor':<20s} {'N':>5s} {'τ_parada·N·η':>14s} {'ω_vacío/N':>12s} "
          f"{'τ_continuo·N·η':>16s} {'¿sirve?':>8s}")
    for nombre, m in motores.items():
        for N in (30, 50, 100):
            tau_parada = m["Kt"] * m["V"] / m["R"]
            omega_vacio = m["V"] / m["Ke"]
            tau_disp = tau_parada * N * eta
            omega_disp = omega_vacio / N
            tau_cont_disp = m["tau_continuo"] * N * eta
            sirve = (tau_disp > tau_pico * margen and omega_disp > omega1_max
                     and tau_cont_disp > tau_rms * margen)
            print(f"{nombre:<20s} {N:>5d} {tau_disp:>14.2f} {omega_disp:>12.2f} "
                  f"{tau_cont_disp:>16.2f} {'sí' if sirve else 'no':>8s}")

    fig, ax = plt.subplots(figsize=(8, 5))
    ax.plot(t_arr, tau1, color="tab:blue")
    ax.axhline(tau_pico, color="tab:red", ls="--", label=f"τ pico = {tau_pico:.2f} N·m")
    ax.axhline(tau_rms, color="tab:orange", ls=":", label=f"τ RMS = {tau_rms:.2f} N·m")
    ax.set_xlabel("t [s]")
    ax.set_ylabel("τ hombro [N·m]")
    ax.set_title("Par requerido en el hombro durante el movimiento")
    ax.legend()
    ax.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.show()


if __name__ == "__main__":
    main()
