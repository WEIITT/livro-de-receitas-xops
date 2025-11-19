import subprocess
import json
from openai import OpenAI
import sys
import re
import os

client = OpenAI()

# === Obter o diff entre o PR e a main ===
try:
    diff = subprocess.check_output(["git", "diff", "origin/main..."], text=True)
except Exception:
    print("❗ Não foi possível usar 'origin/main...'. A usar fallback 'git diff'.")
    diff = subprocess.check_output(["git", "diff"], text=True)

if not diff.strip():
    print("Nenhuma alteração encontrada — aprovação automática.")
    sys.exit(0)

# === Prompt enviado para a IA ===
prompt = f"""
És um Code Reviewer especializado em segurança, clean code e DevSecOps.

Analisa estas alterações ao código (HTML, CSS, JS):

{diff}

Responde APENAS em JSON válido neste formato:

{{
  "status": "ok" | "fail",
  "issues": ["lista de problemas encontrados (strings curtas)"]
}}

A pipeline deve reprovar se encontrares vulnerabilidades, más práticas
de segurança ou código claramente inseguro.
"""

response = client.chat.completions.create(
    model="gpt-4o-mini",
    messages=[{"role": "user", "content": prompt}],
)

raw_output = response.choices[0].message.content

# === Extrair só o JSON, mesmo que venha texto antes/depois ===
match = re.search(r"\{[\s\S]*\}", raw_output)
if not match:
    print("❌ A IA não devolveu JSON válido:")
    print(raw_output)
    sys.exit(1)

json_str = match.group(0)
result = json.loads(json_str)

# === Output legível nos logs do GitHub Actions ===
print("\n========= IA CODE REVIEW =========")
if result.get("issues"):
    for issue in result["issues"]:
        print(" -", issue)
else:
    print("Nenhum problema encontrado.")
print("==================================\n")

# === Falhar o job se a IA disser 'fail' ===
if result.get("status", "").lower() == "fail":
    print("❌ AI detetou problemas — merge bloqueado.")
    sys.exit(1)

print("✔ AI Review Passed — sem problemas críticos.")
