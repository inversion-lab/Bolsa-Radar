# Estado: Bolsa-Radar (actualizado 2026-11-02)

## En qué vamos
- La página (https://inversion-lab.github.io/Bolsa-Radar/) se actualiza **solo a las 7, 8 y 9 a. m. de Colombia, de
  lunes a viernes**. A otras horas no se actualiza, salvo que Eduardo lo pida explícitamente.
- **En la nube (GitHub Actions):**
  - noticias a las :04;
  - mercado y calendario a las :11;
  - cierre diario y verificación de tesis a las 7:11.
- **En el PC de Eduardo:**
  - videos de Cava y Pablo Gil con extracción de tesis a las :20;
  - publicar tesis, radar y cerebro a las :35;
  - lectura del día con IA a las 8:10.
- **Nuevo (2026-11-02): sección "Operativa del profesor en vivo"** (caja 1). Lee los directos de El Trader Rolo y
  muestra lo que dice el profesor: operaciones con entrada, stop y TP, niveles, oportunidades y hora de Bogotá
  (`local/rolo_vivos.py` → `datos/web/rolo.json`). Ya están el del 30-oct y el del 2-nov por la mañana.
- El portafolio que muestra la página tiene 3 cajas. Desde el 2026-10-28 no hay bots.
- El repositorio es de la organización de Javier (`inversion-lab`) desde el 2026-10-29.

## Lo último que se hizo
- 2026-11-02 · Eduardo pide un respaldo manual: si YouTube bloquea o tarda, el directo sale como "pendiente" en la
  revista y se lee pegando la transcripción (`rolo_vivos.py --pegado archivo --inicio "AAAA-MM-DD HH:MM"`) o desde
  Chrome con `fundamental/receptor.py`. El directo de Asia del 2-nov ya está analizado (leído desde Chrome).
- 2026-11-02 · Eduardo decide el horario de la tarea "Bolsa-Radar en vivos del profesor": L-V 11:30 y 12:00 (Nueva
  York) y 21:40 y 22:00 (Asia). Creada en el Programador de tareas.
- 2026-11-02 · Eduardo pide que, por norma, cada directo del profesor se analice al quedar grabado y salga en la
  revista. Se crea `local/rolo_vivos.py` (mismo método que Cava: transcripción + Claude Code con esquema fijo + citas
  comprobadas). La hora de Nueva York en la página pasa a ~9:15 (fin del horario de verano en EE. UU.).
- 2026-10-30 · Eduardo decide: la lectura y la transcripción de los videos (Cava y Pablo Gil) **siguen en el PC**. YouTube
  bloquea los servidores de GitHub y la extracción de tesis usa el plan Pro.
- 2026-10-30 · Se adopta la metodología común (`C:\Users\franc\Agenda\METODOLOGIA.md`): este `ESTADO.md` reemplaza la
  sección 9 del `CLAUDE.md`.
- 2026-10-29 · Eduardo decide: noticias, mercado y tareas del PC solo a las 7, 8 y 9 a. m. Se desactiva el respaldo
  del PC, que relanzaba los flujos fuera de ese horario.
- 2026-10-29 · Repositorio transferido de `Aigosco` a `inversion-lab`. La página, los scripts del PC y la
  documentación ya apuntan allí.
- 2026-10-28 · Se quitan los bots de la página y del arranque. La caja 1 pasa a "Intradía · corto plazo" (curso Tu
  Primer Trade).

## Qué falta / próximos pasos
1. Cargar saldo en la API de Anthropic para encender `resumen.yml` (lectura con IA en la nube) y apagar la tarea
   "Bolsa-Radar lectura IA" del PC: **Eduardo o Javier**. Después, **la consola** hace el cambio.
2. Hacer privado el repositorio: **Javier**. Al hacerlo, hay que avisar a Agenda.
3. Crear la nueva web privada del equipo desde la organización: **Eduardo y Javier**.

## Bloqueos o esperas
- La lectura con IA en la nube espera saldo en la API (desde el 2026-10-19).
- La privacidad del repositorio y la web nueva esperan a Javier (desde el 2026-10-29).

## Alertas
- A las 11:30 y a las 21:40 el directo puede no tener subtítulos todavía (YouTube tarda en generarlos); si a las
  12:00 o a las 22:00 tampoco están, ese directo no se analiza hasta la siguiente ejecución.
- YouTube bloqueó las descargas automáticas de este PC el 2026-11-02 ("confirma que no eres un bot"). Los directos se
  leyeron desde Chrome con `fundamental/receptor.py`. Si el bloqueo sigue, la tarea automática no podrá bajar
  transcripciones.
- **El repositorio sigue público.** No subir números de cuenta, saldos, resultados en dinero, el portafolio ni
  transcripciones completas.
- Si el PC está apagado entre las 7 y las 9:40 a. m., ese día no hay tesis nuevas de Cava ni publicación del radar y
  del cerebro. Noticias y mercado sí se actualizan, porque corren en GitHub.
- GitHub a veces dispara los horarios con retraso o se salta alguno. El respaldo del PC está desactivado, así que nada
  compensa un horario perdido. Para revisarlo: `gh run list -R inversion-lab/Bolsa-Radar --event schedule`.
