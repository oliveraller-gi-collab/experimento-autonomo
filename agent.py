import os, glob, json
from urllib.request import Request, urlopen

print("=== AGENTE AUTONOMO START ===")
print(f"1) ZAI_API_KEY presente: {'ZAI_API_KEY' in os.environ}")

if "ZAI_API_KEY" not in os.environ:
    raise SystemExit("ERROR: falta el secret ZAI_API_KEY")

API_KEY = os.environ["ZAI_API_KEY"]
API_URL = "https://api.z.ai/api/paas/v4/chat/completions"
MODEL = "glm-4.6"

print("2) Buscando archivos .py...")
py_files = [f for f in glob.glob("*.py") if f != "agent.py"]
print(f"   encontrados: {py_files}")

if not py_files:
    raise SystemExit("ERROR: no hay archivos .py en la raiz del repo (aparte de agent.py)")

code_dump = ""
for f in py_files:
    with open(f) as fp:
        code_dump += f"\n\n### ARCHIVO: {f} ###\n{fp.read()}"

print(f"3) Total de codigo leido: {len(code_dump)} chars")

prompt = f"""Eres un ingeniero senior. Analiza el siguiente codigo y propone UNA mejora concreta.
Responde SOLO con JSON valido (sin markdown, sin triple backticks), con esta estructura:
{{"archivo": "nombre.py", "nuevo_codigo": "...", "razon": "..."}}

CODIGO:
{code_dump}
"""

print("4) Llamando a z.ai API...")
req = Request(API_URL,
    data=json.dumps({
        "model": MODEL,
        "messages": [{"role":"user","content":prompt}],
        "temperature": 0.7
    }).encode(),
    headers={
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    })

try:
    resp = json.loads(urlopen(req, timeout=60).read())
    content = resp["choices"][0]["message"]["content"]
    print(f"5) Respuesta recibida: {len(content)} chars")
except Exception as e:
    print(f"5) ERROR llamando API: {e}")
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
    print(f"   contenido recibido: {content[:500]}")
    raise

print(f"6) Mejora propuesta para: {result.get('archivo')}")

with open(result["archivo"], "w") as f:
    f.write(result["nuevo_codigo"])

print(f"7) OK - Aplicado a {result['archivo']}")
print(f"   Razon: {result.get('razon','(sin razon)')}")
print("=== AGENTE TERMINADO ===")
