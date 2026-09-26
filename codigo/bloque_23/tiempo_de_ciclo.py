"""Tiempo de ciclo real (no de computo) de la tarea de recoger y
dejar: cada tramo se ejecuta con un perfil trapezoidal por
articulacion (Bloque 19), sincronizado a la articulacion mas lenta.
Compara dos rutas: pasando por 'reposo' entre recoger y depositar
(mas segura) contra ir directo (mas rapida) (Bloque 23, Tema 23.5).

Correr con:
    python codigo/bloque_23/tiempo_de_ciclo.py
"""

import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from robotica.inversa import inv_3r_geometrica  # noqa: E402
from robotica.trayectorias import perfil_trapezoidal  # noqa: E402

L1, L2, L3 = 0.15, 0.12, 0.10
V_MAX = np.radians(90)    # rad/s, por articulación
A_MAX = np.radians(180)   # rad/s², por articulación

PUNTOS = {
    "reposo": np.array([0.10, 0.00, 0.20]),
    "aprox_recoger": np.array([0.18, 0.05, 0.13]),
    "recoger": np.array([0.18, 0.05, 0.09]),
    "aprox_depositar": np.array([0.10, -0.15, 0.13]),
    "depositar": np.array([0.10, -0.15, 0.09]),
}


def inversa(px, py, pz):
    return inv_3r_geometrica(px, py, pz, L1, L2, L3)


def angulos(nombre):
    return inversa(*PUNTOS[nombre])[0]


def duracion_tramo(nombre_a, nombre_b):
    """Duración del movimiento sincronizado (Bloque 19): cada
    articulación usa un perfil trapezoidal propio, y el tramo completo
    dura lo que tarda la articulación MÁS LENTA."""
    qa, qb = angulos(nombre_a), angulos(nombre_b)
    duraciones = []
    for q0, q1 in zip(qa, qb):
        t, _, _, _ = perfil_trapezoidal(q0, q1, V=V_MAX, a=A_MAX, n_puntos=5)
        duraciones.append(t[-1])
    return max(duraciones)


def duracion_ruta(ruta):
    return sum(duracion_tramo(ruta[i], ruta[i + 1]) for i in range(len(ruta) - 1))


def main() -> None:
    ruta_segura = ["reposo", "aprox_recoger", "recoger", "aprox_recoger",
                   "reposo", "aprox_depositar", "depositar", "aprox_depositar", "reposo"]
    ruta_directa = ["reposo", "aprox_recoger", "recoger", "aprox_recoger",
                    "aprox_depositar", "depositar", "aprox_depositar", "reposo"]

    t_segura = duracion_ruta(ruta_segura)
    t_directa = duracion_ruta(ruta_directa)

    print("Ruta 'segura' (pasa por reposo entre recoger y depositar):")
    print(f"  tramos: {' -> '.join(ruta_segura)}")
    print(f"  duración total: {t_segura:.3f} s")

    print("\nRuta 'directa' (va de aprox_recoger a aprox_depositar sin pasar por reposo):")
    print(f"  tramos: {' -> '.join(ruta_directa)}")
    print(f"  duración total: {t_directa:.3f} s")

    ahorro = (t_segura - t_directa) / t_segura * 100
    print(f"\nAhorro: {t_segura - t_directa:.3f} s por ciclo ({ahorro:.1f}%)")

    ciclos_por_hora_segura = 3600 / t_segura
    ciclos_por_hora_directa = 3600 / t_directa
    print(f"\nCiclos por hora, ruta segura:  {ciclos_por_hora_segura:.0f}")
    print(f"Ciclos por hora, ruta directa: {ciclos_por_hora_directa:.0f} "
          f"({ciclos_por_hora_directa - ciclos_por_hora_segura:+.0f})")


if __name__ == "__main__":
    main()
