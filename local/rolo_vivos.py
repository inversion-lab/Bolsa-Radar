"""En vivos del profesor del curso (El Trader Rolo) → transcripción → operativa (operaciones, niveles, oportunidades)
con Claude Code en el PC → revista (caja 1 · intradía).

Corre EN EL PC (YouTube bloquea a los servidores de GitHub). El profesor opera en vivo la sesión de Nueva York
(empieza 8:30–9:30 a. m. Bogotá, ~2 h) y la de Asia (7:15–7:45 p. m., ~2 h); YouTube tarda unas horas en generar los
subtítulos del directo grabado, así que "sin subtítulos todavía" es normal y se reintenta en la siguiente ejecución.

  1. Mira solo la pestaña de directos del canal (los últimos N; nunca el canal entero) y anota los programados.
  2. Por cada directo terminado sin operativa: baja SOLO la transcripción (fundamental/youtube.py del proyecto local).
     Si YouTube bloquea la IP, queda la vía del navegador: fundamental/receptor.py (autor "rolo").
  3. Claude Code (plan Pro) lee la transcripción completa y devuelve el JSON de ESQUEMA: lo que dice el PROFESOR
     (no los alumnos) sobre operaciones abiertas y cerradas, entradas, stops, take profits, niveles y oportunidades.
  4. Comprueba que cada cita existe en la transcripción y calcula la hora de Bogotá de cada momento.
  5. Guarda fuentes/rolo/<id>/operativa.json (proyecto local; la transcripción NO se publica: derechos de autor) y
     publica datos/rolo/<id>.json y datos/web/rolo.json (últimos directos + programados) en este repo.

  python local/rolo_vivos.py [--ultimos 6] [--video ID] [--sin-push] [--solo-web]
  python local/rolo_vivos.py --pegado transcripcion.txt [--inicio "AAAA-MM-DD HH:MM"]   # respaldo manual

Respaldo manual (decisión de Eduardo, 2026-11-02): si YouTube bloquea la descarga o tarda, el directo queda como
PENDIENTE en la revista. Se resuelve de dos formas: (a) Claude en sesión lo lee desde Chrome con fundamental/receptor.py,
o (b) Eduardo copia la transcripción de YouTube ("Mostrar transcripción" → copiar, formato "(mm:ss) texto") y se procesa
con --pegado; --inicio (hora de Bogotá en que empezó el directo) permite calcular la hora de cada momento.
"""
import argparse
import json
import os
import re
import subprocess
import sys
from datetime import date, datetime, timedelta, timezone
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
TRADING = Path(os.environ.get("TRADING_DIR", r"C:\Users\franc\OneDrive\Desktop\Proyectos Python\Trading"))
sys.path.insert(0, str(TRADING))
sys.path.insert(0, str(REPO / "local"))
from fundamental import youtube as Y  # noqa: E402
from cava_diario import CLAUDE, NO_HERRAMIENTAS, comprobar_citas  # noqa: E402

AUTOR = "rolo"
CANAL = "https://www.youtube.com/@ElTraderRolo/streams"
FUENTES = TRADING / "fuentes" / AUTOR
SALIDA = REPO / "datos" / "rolo"
WEB = REPO / "datos" / "web" / "rolo.json"
BOGOTA = timezone(timedelta(hours=-5))
EN_WEB = 6  # directos que muestra la revista

# Plantillas de zonas del profesor (MT5 del PC). Código de colores dicho por el profesor en la clase 03 (1:10:43):
# blanco = impacto alto, azul = medio, amarillo = altísimo ("las que mandan la parada"). Decisión de Eduardo
# (2026-11-03): SOLO la lógica del profesor; cualquier otro color (rojo, cian, verde) queda "sin clasificar".
# Jerarquía (Eduardo, 2026-11-03): los niveles firmes son las líneas de las plantillas (más los dos precios que
# Eduardo añadió al oro). Los precios dichos en los directos son comentarios de scalp del día: se marca si caen
# sobre una línea ("zonas") o no (color None = sin línea de plantilla).
PLANTILLAS = Path(os.environ.get("MT5_PLANTILLAS", os.path.expandvars(
    r"%APPDATA%\MetaQuotes\Terminal\010E047102812FC0C18890992854220E\MQL5\Profiles\Templates")))
COLORES = {"FFFFFF": "blanca", "FFFFF0": "blanca", "F0FFF0": "blanca", "F5F5F5": "blanca",
           "0000CD": "azul", "000080": "azul", "87CEFA": "azul",
           "FFFF00": "amarilla"}  # el resto: sin clasificar
FUERZA = {"azul": "medio", "blanca": "alto", "amarilla": "altísimo"}
TOLERANCIA = 0.0025  # 0,25 % del precio: ~10 en el oro, ~190 en BTC, ~70 en el Nasdaq

NUM = {"type": ["number", "null"]}
TXT = {"type": "string"}
TXTN = {"type": ["string", "null"]}
SIMBOLO = {"type": "string", "description": "clave: XAUUSD, XAGUSD, BTCUSD, ETHUSD, USTEC (Nasdaq 100), US500, US30, "
                                           "XTIUSD (petróleo WTI), XBRUSD, EURUSD, GBPUSD, USDJPY, DXY…; otro: el nombre"}
ESQUEMA = {
    "type": "object", "additionalProperties": False,
    "required": ["resumen", "sesion", "contexto", "operaciones", "niveles", "oportunidades", "lecciones", "avisos"],
    "properties": {
        "resumen": {"type": "string", "description": "5-8 frases: cómo se operó, con qué sesgo y el resultado"},
        "sesion": {"type": "string", "enum": ["Nueva York", "Asia", "cierre semanal", "otra"]},
        "contexto": {"type": "string", "description": "2-4 frases sobre el mercado según el profesor"},
        "operaciones": {"type": "array", "items": {
            "type": "object", "additionalProperties": False,
            "required": ["activo", "simbolo", "direccion", "estado", "entrada", "stop", "take_profit", "temporalidad",
                         "tipo", "quien", "minuto", "cita", "notas"],
            "properties": {
                "activo": TXT, "simbolo": SIMBOLO,
                "direccion": {"type": "string", "enum": ["compra", "venta"]},
                "estado": {"type": "string", "enum": ["abierta", "cerrada con ganancia", "cerrada con pérdida",
                                                      "cerrada en break even", "cerrada", "parcial", "desconocido"]},
                "entrada": NUM, "stop": NUM, "take_profit": NUM, "temporalidad": TXTN,
                "tipo": {"type": "string", "enum": ["scalp", "intradía", "swing", "desconocido"]},
                "quien": {"type": "string", "enum": ["profesor", "alumno", "dudoso"]},
                "minuto": TXT, "cita": TXT, "notas": TXT}}},
        "niveles": {"type": "array", "items": {
            "type": "object", "additionalProperties": False,
            "required": ["activo", "simbolo", "nivel", "nivel_hasta", "tipo", "temporalidad", "minuto", "cita", "notas"],
            "properties": {
                "activo": TXT, "simbolo": SIMBOLO, "nivel": {"type": "number"}, "nivel_hasta": NUM,
                "tipo": {"type": "string", "enum": ["soporte", "resistencia", "zona de trabajo", "objetivo",
                                                    "ineficiencia", "liquidez", "mínimo", "máximo", "otro"]},
                "temporalidad": TXTN, "minuto": TXT, "cita": TXT, "notas": TXT}}},
        "oportunidades": {"type": "array", "items": {
            "type": "object", "additionalProperties": False,
            "required": ["activo", "simbolo", "direccion", "condicion", "entrada", "stop", "objetivo", "temporalidad",
                         "minuto", "cita"],
            "properties": {
                "activo": TXT, "simbolo": SIMBOLO,
                "direccion": {"type": "string", "enum": ["compra", "venta", "esperar", "no operar"]},
                "condicion": TXT, "entrada": NUM, "stop": NUM, "objetivo": NUM, "temporalidad": TXTN,
                "minuto": TXT, "cita": TXT}}},
        "lecciones": {"type": "array", "items": {
            "type": "object", "additionalProperties": False, "required": ["texto", "minuto"],
            "properties": {"texto": TXT, "minuto": TXT}}},
        "avisos": {"type": "array", "items": TXT,
                   "description": "límites prácticos que menciona (p. ej. qué activos no admite la plataforma)"},
    }}

SISTEMA = """Eres el analista de un equipo que opera intradía y scalp guiado por un profesor de trading (El Trader Rolo,
Alejandro Rodríguez). Recibes la transcripción automática COMPLETA de uno de sus directos de YouTube: opera en vivo con
sus alumnos (a la vez en Zoom). Devuelve SOLO el JSON del esquema. Reglas:

QUIÉN HABLA. La transcripción no marca quién habla. El PROFESOR es el anfitrión: saluda a "mis estimados traders" y
"muchachos", lee el chat por nombre, muestra "sus" operaciones y las de la comunidad, da instrucciones ("alarguen
ganancias", "no me metan compras") y responde las preguntas. Los ALUMNOS lo llaman "profe" y preguntan o cuentan lo
suyo ("yo entré...", "yo vengo en corto desde..."). Alejo es su asistente. Solo cuenta como operación del profesor lo
que él dice que tiene, abrió, cerró o protege ("tenemos", "entramos", "estamos en venta"). Lo de un alumno va con
quien="alumno"; si no se puede saber, quien="dudoso". Nunca atribuyas al profesor lo que dijo un alumno.

PRECIOS. Solo los dichos. El profesor abrevia ("los 53" con el oro cerca de 4.000 = 4053; "los 99 95" = 99,95). Completa
la cifra SOLO si el contexto del mismo momento la deja inequívoca y explícalo en notas ("dijo 'los 53'"); si no, null.
Nunca inventes entrada, stop ni take profit: si no los dijo, null (él a veces dice que no tienen TP calculado: dilo en
notas). No confundas el precio de un activo con el de otro.

CITAS. "cita" es LITERAL de la transcripción (puedes recortar con [...]; corrige una palabra mal reconocida entre
corchetes: "[Nasdaq]"). "minuto" es la marca [h:mm:ss] o [m:ss] del bloque donde empieza la cita, tal cual.

QUÉ RECOGER.
- operaciones: cada posición mencionada (abierta, cerrada, protegida), una vez por activo y dirección salvo que sean
  entradas distintas; estado al final de lo que se oye.
- niveles: soportes, resistencias, zonas de trabajo, objetivos, ineficiencias o zonas de liquidez con precio.
- oportunidades: lo que el profesor dice que haría o esperaría (incluye "no comprar", "esperar pullback a la EMA 20").
- lecciones: reglas de gestión o de método que repite (máximo 8, en una frase cada una).
- tipo: scalp si la operación dura minutos o se habla de 1-5 minutos; intradía si es de la sesión; swing si es de días.
- Material de estudio, no consejo: no añadas opiniones propias.
Fecha de hoy: {hoy}. El directo empezó {inicio} (hora de Bogotá)."""


def directos(n):
    """Últimos n de la pestaña de directos: (terminados, programados)."""
    r = subprocess.run([sys.executable, "-m", "yt_dlp", "--flat-playlist", "--playlist-end", str(n), "--print",
                        "%(id)s|%(live_status)s|%(title)s", CANAL], capture_output=True, text=True, encoding="utf-8",
                       timeout=180)
    if "not a bot" in (r.stderr or ""):
        raise Y.Bloqueo("YouTube pide confirmar que no eres un bot")
    filas = [ln.split("|", 2) for ln in r.stdout.splitlines() if ln.count("|") >= 2]
    return ([(i, t) for i, e, t in filas if e == "was_live"],
            [{"id": i, "titulo": t, "url": f"https://www.youtube.com/watch?v={i}"} for i, e, t in filas
             if e in ("is_upcoming", "is_live")])


def seg(m):
    """'1:02:03' / '12:05' / '725' → segundos."""
    p = [int(x) for x in re.findall(r"\d+", str(m))]
    return sum(v * 60 ** i for i, v in enumerate(reversed(p))) if p else None


def hms(s):
    return f"{s // 3600}:{s % 3600 // 60:02d}:{s % 60:02d}" if s >= 3600 else f"{s // 60}:{s % 60:02d}"


def inicio_de(info):
    """Inicio del directo (datetime con zona) desde info.json; el receptor guarda el ISO de YouTube."""
    v = info.get("inicio_directo") or info.get("fecha_publicacion") or ""
    try:
        d = datetime.fromisoformat(str(v).replace("Z", "+00:00"))
        return d if d.tzinfo else None
    except ValueError:
        return None


def extraer(carpeta):
    info = json.loads((carpeta / "info.json").read_text(encoding="utf-8"))
    crudo = (carpeta / "transcripcion.txt").read_text(encoding="utf-8", errors="replace")
    # el receptor del navegador marca segundos ([725]); se pasan a [m:ss] como las de yt-dlp
    trans = re.sub(r"^\[(\d+)\]", lambda m: f"[{hms(int(m.group(1)))}]", crudo, flags=re.M)
    ini = inicio_de(info)
    ini_txt = ini.astimezone(BOGOTA).strftime("%Y-%m-%d %H:%M") if ini else "sin dato"
    entrada = f"Directo: {info.get('titulo')} | canal {info.get('canal')} | inicio {ini_txt}\n\n{trans}"
    r = subprocess.run([CLAUDE, "-p", "--output-format", "json", "--json-schema", json.dumps(ESQUEMA),
                        "--system-prompt", SISTEMA.format(hoy=date.today().isoformat(), inicio=ini_txt),
                        "--disallowedTools", NO_HERRAMIENTAS, "--no-session-persistence"],
                       input=entrada, capture_output=True, text=True, encoding="utf-8", timeout=2400,
                       cwd=os.environ.get("TEMP", str(REPO)))
    salida = json.loads(r.stdout)
    d = salida.get("structured_output")
    if salida.get("is_error") or not isinstance(d, dict) or "operaciones" not in d:
        raise RuntimeError(f"extracción inválida: {salida.get('subtype')} {str(salida.get('result'))[:200]}")
    citables = d["operaciones"] + d["niveles"] + d["oportunidades"]
    malas = comprobar_citas(citables, trans)
    for x in citables:  # hora de Bogotá de cada momento
        s = seg(x.get("minuto"))
        x["hora_bogota"] = (ini + timedelta(seconds=s)).astimezone(BOGOTA).strftime("%H:%M") if ini and s is not None else None
    modelo = next(iter(salida.get("modelUsage", {}) or {"claude": 0}))
    d.update({"video_id": carpeta.name, "titulo": info.get("titulo"),
              "url": f"https://www.youtube.com/watch?v={carpeta.name}",
              "inicio": ini.astimezone(BOGOTA).isoformat() if ini else None, "duracion_seg": info.get("duracion_seg") or info.get("duracion"),
              "origen": f"claude-code automático ({modelo}, plan Pro)", "fecha_extraccion": date.today().isoformat(),
              "comprobacion_citas": {"citas": len(citables), "fragmentos_no_literales": malas}})
    (carpeta / "operativa.json").write_text(json.dumps(d, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"{carpeta.name}: {len(d['operaciones'])} operaciones · {len(d['niveles'])} niveles · "
          f"{len(d['oportunidades'])} oportunidades · citas no literales: {len(malas)} · "
          f"{salida.get('duration_ms', 0) / 1000:.0f} s")
    return d


def pegado(archivo, vid=None, inicio=None):
    """Transcripción copiada a mano de YouTube ("(1:02:03) texto", con título y URL arriba) → carpeta del directo."""
    txt = Path(archivo).read_text(encoding="utf-8", errors="replace")
    vid = vid or (re.search(r"(?:v=|youtu\.be/|/live/)([\w-]{11})", txt) or [None, None])[1]
    if not vid:
        raise SystemExit("no encuentro el id del video: pásalo con --video")
    titulo = next((ln.strip() for ln in txt.splitlines() if ln.strip()), "")
    titulo = re.sub(r"^\(\d+\)\s*|\s*-\s*YouTube$", "", titulo)
    partes = re.split(r"\((\d{1,2}(?::\d{2}){1,2})\)", txt)
    bloques = [(seg(partes[i]), " ".join(partes[i + 1].split())) for i in range(1, len(partes) - 1, 2)]
    bloques = [(t, x) for t, x in bloques if x]
    if len(bloques) < 20:
        raise SystemExit(f"solo {len(bloques)} bloques con marca de tiempo: ¿es la transcripción completa?")
    ini = datetime.strptime(inicio, "%Y-%m-%d %H:%M").replace(tzinfo=BOGOTA) if inicio else None
    carpeta = FUENTES / vid
    carpeta.mkdir(parents=True, exist_ok=True)
    info = {"id": vid, "titulo": titulo, "canal": "El Trader Rolo", "inicio_directo": ini.isoformat() if ini else None,
            "duracion_seg": bloques[-1][0], "subtitulos": {"origen": "transcripción copiada a mano de YouTube"}}
    (carpeta / "info.json").write_text(json.dumps(info, ensure_ascii=False, indent=2), encoding="utf-8")
    (carpeta / "transcripcion.txt").write_text(
        f"# {titulo} | El Trader Rolo | transcripción copiada a mano\n\n" +
        "\n".join(f"[{hms(t)}] {x}" for t, x in bloques) + "\n", encoding="utf-8")
    print(f"{vid}: {len(bloques)} bloques pegados · {titulo}")
    return carpeta


def lineas_plantillas():
    """Líneas horizontales de las plantillas de MT5 del profesor → {símbolo: [(precio, grupo de color)]}.
    El símbolo sale de la propia plantilla (XAUUSDm → XAUUSD). Las plantillas son material del curso: aquí solo se
    leen; lo único que se publica es el color de la línea que coincide con un precio que el profesor dijo en directo."""
    lineas = {}
    for f in PLANTILLAS.glob("*.tpl"):
        try:
            s = f.read_text(encoding="utf-16")
        except (OSError, UnicodeError):
            continue
        sim = re.search(r"^symbol=(\S+)", s, re.M)
        if not sim:
            continue
        clave = re.sub(r"m$", "", sim.group(1))
        for o in re.findall(r"<object>(.*?)</object>", s, re.S):
            d = dict(ln.split("=", 1) for ln in o.strip().splitlines() if "=" in ln)
            if d.get("type") != "1" or "value1" not in d:  # solo líneas horizontales
                continue
            c = int(d["color"]) if "color" in d else None  # sin color guardado = el de MT5 por defecto
            hexa = "defecto" if c is None else "%02X%02X%02X" % (c & 255, (c >> 8) & 255, (c >> 16) & 255)
            lineas.setdefault(clave, []).append((float(d["value1"]), COLORES.get(hexa, "sin clasificar")))
    return lineas


def marcar_zonas(d, lineas):
    """A cada precio del directo le añade la línea de plantilla más cercana (si está a ≤ TOLERANCIA del precio)."""
    for clave, campos in (("operaciones", ("entrada", "stop", "take_profit")), ("niveles", ("nivel", "nivel_hasta")),
                          ("oportunidades", ("entrada", "stop", "objetivo"))):
        for x in d.get(clave, []):
            x.pop("zonas", None)
            zz = {}
            for campo in campos:
                p = x.get(campo)
                ll = lineas.get(x.get("simbolo"))
                if not isinstance(p, (int, float)) or not p or not ll:
                    continue
                v, g = min(ll, key=lambda t: abs(t[0] - p))
                if abs(v - p) <= TOLERANCIA * p:
                    zz[campo] = {"color": g, "fuerza": FUERZA.get(g), "distancia": round(v - p, 3)}
                else:  # el activo tiene plantilla, pero ese precio no cae sobre ninguna línea
                    zz[campo] = {"color": None}
            if zz:
                x["zonas"] = zz
    return d


def publicar(programados, pendientes=None):
    """Copia las operativas al repo y arma web/rolo.json (los EN_WEB directos más recientes + programados + pendientes).
    pendientes=None conserva los de la publicación anterior que sigan sin operativa."""
    SALIDA.mkdir(parents=True, exist_ok=True)
    todos = []
    lineas = lineas_plantillas()
    for f in FUENTES.glob("*/operativa.json"):
        d = marcar_zonas(json.loads(f.read_text(encoding="utf-8")), lineas)
        (SALIDA / f"{d['video_id']}.json").write_text(json.dumps(d, ensure_ascii=False, indent=1), encoding="utf-8")
        todos.append(d)
    todos.sort(key=lambda d: d.get("inicio") or "", reverse=True)
    hechos = {d["video_id"] for d in todos}
    if pendientes is None:
        try:
            pendientes = json.loads(WEB.read_text(encoding="utf-8")).get("pendientes", [])
        except (OSError, ValueError):
            pendientes = []
    pendientes = [p for p in pendientes if p["id"] not in hechos]
    web = {"generado": datetime.now(BOGOTA).isoformat(timespec="minutes"), "canal": CANAL,
           "programados": programados, "pendientes": pendientes, "directos": todos[:EN_WEB]}
    WEB.write_text(json.dumps(web, ensure_ascii=False, separators=(",", ":")) + "\n", encoding="utf-8")
    print(f"web/rolo.json: {len(web['directos'])} directos, {len(programados)} programados, {len(pendientes)} pendientes")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--ultimos", type=int, default=6)
    ap.add_argument("--video")
    ap.add_argument("--sin-push", action="store_true")
    ap.add_argument("--solo-web", action="store_true", help="solo rehace rolo.json con lo ya extraído")
    ap.add_argument("--pegado", help="archivo con la transcripción copiada a mano de YouTube (respaldo manual)")
    ap.add_argument("--inicio", help='hora de Bogotá en que empezó el directo, "AAAA-MM-DD HH:MM" (con --pegado)')
    a = ap.parse_args()
    if a.pegado:
        extraer(pegado(a.pegado, a.video, a.inicio))
        publicar([])
        if not a.sin_push:
            import publicar_desde_pc as P
            P.git_push()
        return
    programados, lista, pendientes, listado = [], [], {}, False
    try:
        terminados, programados = directos(a.ultimos + 4)
        lista = [(a.video, "")] if a.video else terminados[:a.ultimos]
        listado = True
    except (Y.Bloqueo, subprocess.TimeoutExpired) as ex:
        print(f"lista de directos: {ex}")
        lista = [(a.video, "")] if a.video else []
    nuevos = 0
    hechos = {f.parent.name for f in FUENTES.glob("*/operativa.json")}
    for vid, titulo in lista:  # pendientes = directos más nuevos que el último analizado
        if vid in hechos:
            break
        pendientes[vid] = {"id": vid, "titulo": titulo, "url": f"https://www.youtube.com/watch?v={vid}",
                           "motivo": "aún sin revisar"}
    for vid, _ in ([] if a.solo_web else lista):
        carpeta = FUENTES / vid
        if (carpeta / "operativa.json").exists():
            continue
        if not (carpeta / "transcripcion.txt").exists():
            try:
                res, ok = Y.bajar(vid, carpeta)
            except Y.Bloqueo:
                print(f"{vid}: YouTube bloquea; se detiene sin insistir (respaldo manual: --pegado o receptor.py)")
                for p in pendientes.values():
                    if p["motivo"] == "aún sin revisar":
                        p["motivo"] = "YouTube bloqueó la descarga automática: hace falta la lectura manual"
                break
            if not ok:
                print(f"{vid}: sin subtítulos todavía; se reintentará en la próxima ejecución")
                if vid in pendientes:
                    pendientes[vid]["motivo"] = "YouTube aún no generó los subtítulos; se reintenta en la próxima revisión"
                continue
            print(f"{vid}: transcripción bajada · {res.get('titulo')}")
        try:
            extraer(carpeta)
            nuevos += 1
        except Exception as ex:  # noqa: BLE001 — un directo fallido no impide los demás
            print(f"{vid}: fallo en la extracción ({ex})")
    print(f"directos nuevos analizados: {nuevos}")
    publicar(programados, list(pendientes.values()) if listado and not a.solo_web else None)
    if not a.sin_push:
        import publicar_desde_pc as P
        P.git_push()


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    main()
