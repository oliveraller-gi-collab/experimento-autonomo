import os, glob, json, base64, time
from urllib.request import Request, urlopen

API_KEY  = os.environ["ZAI_API_KEY"]
API_URL  = "https://api.z.ai/api/paas/v4/chat/completions"
MODEL    = "glm-4.6"

# 1) Leer todos los archivos .py del repo
py_files = glob.glob("*.py")
code_dump = ""
for f in py_files:
    if f == "agent.py":   # el agente no se edita a sí mismo
        continue
    with open(f) as fp:
        code_dump += f"\n\n### ARCHIVO: {f} ###\n{fp.read()}"

# 2) Prompt: pide al LLM que proponga mejoras
prompt = f"""
Eres un ingeniero senior. Analiza el siguiente código de un experimento
y propón UNA mejora concreta. Devuelve en formato JSON:
{{"archivo": "nombre.py", "nuevo_codigo": "...", "razon": "..."}}

CÓDIGO ACTUAL:
{code_dump}
"""

# 3) Llamar a la API
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

resp = json.loads(urlopen(req).read())
content = resp["choices"][0]["message"]["content"]

# Limpiar markdown si viene con ```json
content = content.strip().strip("`")
if content.startswith("json"):
    content = content[4:].strip()

result = json.loads(content)

# 4) Aplicar el cambio
with open(result["archivo"], "w") as f:
    f.write(result["nuevo_codigo"])

print(f"✅ Mejora aplicada en {result['archivo']}: {result['razon']}")
