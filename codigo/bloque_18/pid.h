/* PID discreto para microcontrolador (Bloque 18, Tema 18.6).
 *
 * Port línea por línea de robotica.control.PID (codigo/robotica/control.py).
 * Sin memoria dinámica, sin math.h: solo sumas, productos y comparaciones.
 *
 * real_t es float por defecto (lo que tiene un microcontrolador con FPU
 * de precisión simple); compilar con -DPID_DOBLE para usar double, que
 * es lo que usa comparar_c_python.py para contrastar contra Python.
 */
#ifndef PID_H
#define PID_H

#ifdef PID_DOBLE
typedef double real_t;
#else
typedef float real_t;
#endif

typedef struct {
    /* Parámetros (se fijan con pid_iniciar) */
    real_t kp, ki, kd;
    real_t ts;            /* periodo de muestreo [s] */
    real_t u_min, u_max;  /* límites del actuador */
    real_t tf;            /* filtro de la derivada [s], 0 = sin filtro */
    int anti_windup;      /* 1 = integración condicional */
    int derivada_de_error;/* 0 = deriva -medición (recomendado), 1 = deriva el error */

    /* Estado (memoria entre muestras) */
    real_t integral;
    real_t derivada;
    real_t anterior;
    int hay_anterior;
} PidControlador;

void pid_iniciar(PidControlador *c, real_t kp, real_t ki, real_t kd,
                 real_t ts, real_t u_min, real_t u_max, real_t tf,
                 int anti_windup, int derivada_de_error);
void pid_reiniciar(PidControlador *c);
real_t pid_paso(PidControlador *c, real_t referencia, real_t medicion);

#endif
