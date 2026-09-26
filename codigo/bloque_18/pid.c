/* PID discreto para microcontrolador (Bloque 18, Tema 18.6).
 * Ver pid.h. Cada bloque de este archivo corresponde a uno de
 * PID.paso en codigo/robotica/control.py, en el mismo orden.
 */
#include "pid.h"

void pid_iniciar(PidControlador *c, real_t kp, real_t ki, real_t kd,
                 real_t ts, real_t u_min, real_t u_max, real_t tf,
                 int anti_windup, int derivada_de_error)
{
    c->kp = kp;
    c->ki = ki;
    c->kd = kd;
    c->ts = ts;
    c->u_min = u_min;
    c->u_max = u_max;
    c->tf = tf;
    c->anti_windup = anti_windup;
    c->derivada_de_error = derivada_de_error;
    pid_reiniciar(c);
}

void pid_reiniciar(PidControlador *c)
{
    c->integral = 0;
    c->derivada = 0;
    c->anterior = 0;
    c->hay_anterior = 0;
}

real_t pid_paso(PidControlador *c, real_t referencia, real_t medicion)
{
    real_t e = referencia - medicion;

    /* Derivada filtrada. En la primera muestra no hay pasado: D = 0. */
    real_t senal = c->derivada_de_error ? e : -medicion;
    if (c->hay_anterior) {
        real_t a = c->tf / (c->tf + c->ts);
        c->derivada = a * c->derivada
                      + c->kd / (c->tf + c->ts) * (senal - c->anterior);
    }
    c->anterior = senal;
    c->hay_anterior = 1;

    /* Integral candidata (Euler hacia atrás) y salida sin saturar. */
    real_t integral_nueva = c->integral + c->ki * c->ts * e;
    real_t u = c->kp * e + integral_nueva + c->derivada;

    /* Saturación y anti-windup por integración condicional. */
    if (u > c->u_max) {
        if (!(c->anti_windup && e > 0))
            c->integral = integral_nueva;
        u = c->u_max;
    } else if (u < c->u_min) {
        if (!(c->anti_windup && e < 0))
            c->integral = integral_nueva;
        u = c->u_min;
    } else {
        c->integral = integral_nueva;
    }
    return u;
}
