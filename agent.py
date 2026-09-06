import os, glob, json
from urllib.request import Request, urlopen
from urllib.error import HTTPError

print("=== AGENTE AUTONOMO START ===")

if "GEMINI_API_KEY" not in os.environ:
    raise SystemExit("ERROR: falta el secret GEMINI_API_KEY")

API_KEY = os.environ["GEMINI_API_KEY"].strip()
print(f"1) API key length: {len(API_KEY)} chars")

API_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key=" + API_KEY

print("2) Buscando archivos .py...")
py_files = [f for f in glob.glob("*.py") if f != "agent.py"]
print(f"   encontrados: {py_files}")

if not py_files:
    raise SystemExit("ERROR: no hay archivos .py en la raiz (aparte de agent.py)")

code_dump = ""
for f in py_files:
    with open(f) as fp:
        code_dump += f"\n\n### ARCHIVO: {f} ###\n{fp.read()}"

print(f"3) Total codigo leido: {len(code_dump)} chars")

prompt = f"""Eres un ingeniero senior. Analiza el siguiente codigo y propone UNA mejora concreta.
Responde SOLO con JSON valido (sin markdown, sin backticks), con esta estructura:
{{"archivo": "nombre.py", "nuevo_codigo": "...", "razon": "..."}}

CODIGO:
{code_dump}
"""

print("4) Llamando a Gemini API...")
req = Request(API_URL,
    data=json.dumps({
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {"temperature": 0.7}
    }).encode(),
    headers={"Content-Type": "application/json"}
)

try:
    resp = json.loads(urlopen(req, timeout=60).read())
    content = resp["candidates"][0]["content"]["parts"][0]["text"]
    print(f"5) Respuesta recibida: {len(content)} chars")
except HTTPError as e:
    error_body = e.read().decode('utf-8', errors='replace')
    print(f"5) ERROR HTTP {e.code}: {e.reason}")
    print(f"   Cuerpo: {error_body[:500]}")
    raise
except Exception as e:
    print(f"5) ERROR: {type(e).__name__}: {e}")
    raise

content = content.strip()
if content.startswith("```"):
    content = content.split("```")[1]
    if content.startswith("json"):
        content = content[4:]
    content = content.strip()

try:
    result = json.loads(content)
except Exception as e:
    print(f"6) ERROR parseando JSON: {e}")
    print(f"   contenido: {content[:500]}")
    raise

print(f"6) Mejora para: {result.get('archivo')}")

with open(result["archivo"], "w") as f:
    f.write(result["nuevo_codigo"])

print(f"7) OK - Aplicado a {result['archivo']}")
print(f"   Razon: {result.get('razon','(sin razon)')}")
print("=== AGENTE TERMINADO ===")
