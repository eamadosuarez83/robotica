"""Compara el PID en C (pid.c) contra robotica.control.PID, muestra por
muestra, sobre las mismas secuencias (Bloque 18, Tema 18.6).

Primero se simula el lazo en Python (articulación con gravedad, ruido
de medición y saturación) y se guarda cada par (referencia, medición).
Luego esa misma secuencia se le pasa al programa en C, compilado dos
veces: con double (debe coincidir casi al bit) y con float (lo que
corre en un microcontrolador sin FPU doble: diferencias pequeñas).

Necesita gcc. Correr con:
    python codigo/bloque_18/comparar_c_python.py

Salida esperada: para cada caso, la diferencia máxima |u_C - u_Py|.
Con double, exactamente 0 (mismas operaciones en el mismo orden, en
IEEE 754); con float, entre 1e-5 y 1e-3 V (los 7 dígitos de un float,
amplificados por kd/ts cuando la derivada no está filtrada).
"""

import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from robotica.control import PID, pid_por_polos, simular_lazo  # noqa: E402
from articulacion import B_EFF, J, K, U_MAX, dinamica  # noqa: E402

AQUI = Path(__file__).resolve().parent


class Registrador:
    """Envuelve un PID, le suma ruido a la medición y guarda (r, y, u)."""

    def __init__(self, pid, ruido, semilla=0):
        self.pid, self.ts = pid, pid.ts
        self.ruido = ruido
        self.rng = np.random.default_rng(semilla)
        self.registro = []

    def paso(self, r, y):
        y = y + self.rng.normal(0.0, self.ruido)
        u = self.pid.paso(r, y)
        self.registro.append((r, y, u))
        return u


def compilar(carpeta, doble):
    exe = carpeta / ("prueba_doble" if doble else "prueba_float")
    orden = ["gcc", "-O2", "-std=c99", "-Wall", "-Wextra",
             str(AQUI / "pid.c"), str(AQUI / "prueba_pid.c"), "-o", str(exe)]
    if doble:
        orden.insert(1, "-DPID_DOBLE")
    subprocess.run(orden, check=True)
    return exe


def correr_c(exe, pid, registro):
    # repr(float) escribe todos los dígitos necesarios para no perder nada;
    # float(...) evita que NumPy 2 escriba "np.float64(...)".
    parametros = (pid.kp, pid.ki, pid.kd, pid.ts, pid.u_min, pid.u_max, pid.tf)
    encabezado = (" ".join(repr(float(v)) for v in parametros)
                  + f" {int(pid.anti_windup)} {int(pid.derivada_de == 'error')}\n")
    datos = "".join(f"{float(r)!r} {float(y)!r}\n" for r, y, _ in registro)
    salida = subprocess.run([str(exe)], input=encabezado + datos,
                            capture_output=True, text=True, check=True).stdout
    return np.array([float(v) for v in salida.split()])


def main() -> None:
    if shutil.which("gcc") is None:
        sys.exit("No se encontró gcc: instalarlo (en Manjaro: sudo pacman -S gcc).")

    kp, ki, kd = pid_por_polos(J, B_EFF, K, wn=4.0, zeta=0.8, p=4.0)
    casos = {
        "derivada de la medición, filtrada, anti-windup":
            dict(derivada_de="medicion", tf=0.01, anti_windup=True),
        "derivada del error, sin filtro, anti-windup":
            dict(derivada_de="error", tf=0.0, anti_windup=True),
        "derivada de la medición, sin anti-windup":
            dict(derivada_de="medicion", tf=0.01, anti_windup=False),
    }
    # Referencia con escalones grandes, para que sature y se note el windup.
    referencia = lambda t: 1.5 if t < 3.0 else -0.5  # noqa: E731

    with tempfile.TemporaryDirectory() as tmp:
        tmp = Path(tmp)
        exe_doble, exe_float = compilar(tmp, True), compilar(tmp, False)
        print(f"PID: kp={kp:.3f} ki={ki:.3f} kd={kd:.3f}, ts=1 ms, u en [-12, 12] V\n")
        print(f"{'caso':<50s} {'muestras':>8s} {'saturadas':>9s} "
              f"{'máx|dif| double':>16s} {'máx|dif| float':>15s}")
        for nombre, opciones in casos.items():
            pid = PID(kp, ki, kd, ts=0.001, u_min=-U_MAX, u_max=U_MAX, **opciones)
            reg = Registrador(pid, ruido=0.002)
            simular_lazo(dinamica, reg, referencia, [0.0, 0.0], 6.0, subpasos=4)
            u_py = np.array([u for _, _, u in reg.registro])
            # Un PID nuevo en C, con los mismos parámetros, arrancando de cero.
            pid.reiniciar()
            dif_d = np.max(np.abs(correr_c(exe_doble, pid, reg.registro) - u_py))
            dif_f = np.max(np.abs(correr_c(exe_float, pid, reg.registro) - u_py))
            sat = np.sum(np.abs(u_py) >= U_MAX)
            print(f"{nombre:<50s} {len(u_py):>8d} {sat:>9d} {dif_d:>16.2e} {dif_f:>15.2e}")

    print("\nCon double el C reproduce a Python: el port es fiel, línea por línea.")
    print("Con float la diferencia es el redondeo de 7 dígitos; es la que tendría")
    print("el microcontrolador, y es mucho menor que el ruido del sensor.")


if __name__ == "__main__":
    main()
