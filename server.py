#!/usr/bin/env python3
"""Dashboard de la mesa POLY (Polymarket EN PAPEL). Solo librería estándar."""
import base64, hmac, json, os, sys, time
from http.server import ThreadingHTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs

POLY_DIR = os.path.realpath(os.environ.get("POLY_DIR", "/workspace/poly"))
PORT = int(os.environ.get("PORT", "8080"))
USERS = {"alberto": os.environ.get("POLY_PASS_ALBERTO", ""), "nacho": os.environ.get("POLY_PASS_NACHO", "")}
if not all(USERS.values()):
    sys.stderr.write("ERROR: faltan POLY_PASS_ALBERTO y/o POLY_PASS_NACHO. No arranco.\n"); sys.exit(1)
HERE = os.path.dirname(os.path.abspath(__file__))
FASES = ["escaneado", "aprobado", "confirmado", "valorado", "ejecutado", "resuelto"]

def load(name, default):
    try:
        with open(os.path.join(POLY_DIR, name), encoding="utf-8") as f: return json.load(f)
    except Exception: return default

def safe_path(rel):
    if not rel or "\x00" in rel or rel.startswith("/") or ".." in rel.replace("\\", "/").split("/"): return None
    p = os.path.realpath(os.path.join(POLY_DIR, rel))
    if os.path.commonpath([p, POLY_DIR]) != POLY_DIR or not os.path.isfile(p): return None
    return p

def list_files():
    out = []
    for root, dirs, files in os.walk(POLY_DIR):
        dirs[:] = [d for d in dirs if not d.startswith(".")]
        for fn in sorted(files):
            full = os.path.join(root, fn)
            if os.path.islink(full): continue
            out.append({"path": os.path.relpath(full, POLY_DIR), "size": os.path.getsize(full)})
    return out

def data():
    markets = load("markets.json", []); markets = markets if isinstance(markets, list) else markets.get("mercados", [])
    paper = load("paper.json", {}); state = load("state.json", {}); act = load("activity.json", [])
    act = act if isinstance(act, list) else act.get("eventos", [])
    por_fase = {f: [] for f in FASES}
    for m in markets:
        f = str(m.get("fase", m.get("estado", "escaneado"))).lower()
        por_fase.setdefault(f, []).append(m)
    ini = float(paper.get("saldo_inicial_usd", state.get("saldo_inicial_usd", 50)) or 50)
    saldo = float(paper.get("saldo_usd", state.get("saldo_usd", ini)) or 0)
    return {"ts": time.time(), "fases": FASES, "por_fase": por_fase, "saldo_usd": saldo, "saldo_inicial_usd": ini,
            "pnl_usd": round(saldo - ini, 2), "posiciones": paper.get("posiciones", []),
            "mesa_parada": state.get("mesa_parada", False), "perdida_diaria_usd": state.get("perdida_diaria_usd", 0),
            "actividad": act[-50:][::-1], "archivos": list_files()}

class H(BaseHTTPRequestHandler):
    server_version = "PolyDash"
    def log_message(self, fmt, *a):  # no registra cabeceras (ni credenciales)
        sys.stderr.write("%s %s\n" % (self.command, urlparse(self.path).path))
    def auth_ok(self):
        h = self.headers.get("Authorization", "")
        if not h.startswith("Basic "): return False
        try: u, _, p = base64.b64decode(h[6:]).decode("utf-8").partition(":")
        except Exception: return False
        return u in USERS and hmac.compare_digest(p.encode(), USERS[u].encode())
    def send(self, code, body, ctype="application/json; charset=utf-8"):
        b = body if isinstance(body, bytes) else body.encode("utf-8")
        self.send_response(code); self.send_header("Content-Type", ctype); self.send_header("Content-Length", str(len(b)))
        self.send_header("Cache-Control", "no-store"); self.send_header("X-Content-Type-Options", "nosniff")
        if code == 401: self.send_header("WWW-Authenticate", 'Basic realm="Mesa POLY", charset="UTF-8"')
        self.end_headers(); self.wfile.write(b)
    def do_GET(self):
        if not self.auth_ok(): return self.send(401, '{"error":"no autorizado"}')
        u = urlparse(self.path)
        if u.path == "/":
            with open(os.path.join(HERE, "index.html"), "rb") as f: return self.send(200, f.read(), "text/html; charset=utf-8")
        if u.path == "/api/data": return self.send(200, json.dumps(data(), ensure_ascii=False))
        if u.path == "/api/file":
            p = safe_path(parse_qs(u.query).get("path", [""])[0])
            if not p: return self.send(400, '{"error":"ruta no permitida"}')
            with open(p, "rb") as f: c = f.read(512 * 1024)
            return self.send(200, c, "text/plain; charset=utf-8")
        self.send(404, '{"error":"no encontrado"}')
    def do_POST(self): self.send(405, '{"error":"solo lectura"}')
    do_PUT = do_DELETE = do_PATCH = do_POST

if __name__ == "__main__":
    print(f"Mesa POLY dashboard en http://0.0.0.0:{PORT} (datos: {POLY_DIR})", flush=True)
    ThreadingHTTPServer(("0.0.0.0", PORT), H).serve_forever()
