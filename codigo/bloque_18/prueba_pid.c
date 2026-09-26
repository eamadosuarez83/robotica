/* Banco de prueba del PID en C (Bloque 18, Tema 18.6).
 *
 * Lee de la entrada estándar:
 *   línea 1: kp ki kd ts u_min u_max tf anti_windup derivada_de_error
 *   luego:   referencia medicion   (una muestra por línea)
 * y escribe la salida u de cada muestra, una por línea.
 *
 * No se usa solo: comparar_c_python.py lo compila, le pasa la misma
 * secuencia que al PID de Python y compara las salidas.
 */
#include <stdio.h>
#include "pid.h"

int main(void)
{
    double kp, ki, kd, ts, u_min, u_max, tf;
    int aw, de;
    if (scanf("%lf %lf %lf %lf %lf %lf %lf %d %d",
              &kp, &ki, &kd, &ts, &u_min, &u_max, &tf, &aw, &de) != 9) {
        fprintf(stderr, "encabezado inválido\n");
        return 1;
    }
    PidControlador c;
    pid_iniciar(&c, (real_t)kp, (real_t)ki, (real_t)kd, (real_t)ts,
                (real_t)u_min, (real_t)u_max, (real_t)tf, aw, de);

    double r, y;
    while (scanf("%lf %lf", &r, &y) == 2)
        printf("%.17g\n", (double)pid_paso(&c, (real_t)r, (real_t)y));
    return 0;
}
