import subprocess
import json
from openai import OpenAI
import sys
import re
import os

client = OpenAI()

# === OBTÉM O DIFF CORRECTO ENTRE O PR E A MAIN ===
try:
    diff = subprocess.check_output(["git", "diff", "origin/main..."], text=True)
except:
    print("❗ Não foi possível obter o diff. A correr fallback.")
    diff = subprocess.check_output(["git", "diff"], text=True)

if not diff.strip():
    print("Nenhuma alteração encontrada — aprovação automática.")
    sys.exit(0)

# === PROMPT PARA A IA ===
prompt = f"""
És um Code Reviewer especializado em segurança, clean code e DevSecOps.

Analisa estas alterações ao código:

{diff}

Responde APENAS em JSON no formato:

{{
  "status": "ok" | "fail",
  "issues": ["lista de problemas"]
}}

A pipeline deve reprovar se encontrares vulnerabilidades, más práticas,
ou código inseguro.
"""

response = client.chat.completions.create(
    model="gpt-4o-mini",
    messages=[{"role": "user", "content": prompt}]
)

raw_output = response.choices[0].message["content"]

# === EXTRAIR JSON MESMO QUE VENHA TEXTO JUNTO ===
json_str = re.search(r"\{[\s\S]*\}", raw_output).group(0)
result = json.loads(json_str)

# === OUTPUT BONITO NO LOG DO GITHUB ACTIONS ===
print("\n========= IA CODE REVIEW =========")
if result["issues"]:
    for issue in result["issues"]:
        print(" -", issue)
else:
    print("Nenhum problema encontrado.")
print("==================================\n")

# === BLOQUEAR MERGE SE NECESSÁRIO ===
if result["status"].lower() == "fail":
    print("❌ AI detetou problemas — merge bloqueado.")
    sys.exit(1)

print("✔ AI Review Passed — sem problemas críticos.")
