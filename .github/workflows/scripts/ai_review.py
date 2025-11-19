import subprocess
import json
from openai import OpenAI
import sys

client = OpenAI()

# obter o diff do pull request
diff = subprocess.check_output(["git", "diff", "HEAD^", "HEAD"]).decode()

prompt = f"""
És um Code Reviewer especializado em segurança, clean code e DevSecOps.

Analisa estas alterações ao código:

{diff}

Responde apenas em JSON com o formato:

{{
  "status": "ok" | "fail",
  "issues": ["lista de problemas encontrados"]
}}

A pipeline deve reprovar se encontrares vulnerabilidades, más práticas, 
ou código inseguro.
"""

response = client.chat.completions.create(
    model="gpt-4o-mini",
    messages=[{"role": "user", "content": prompt}]
)

result = json.loads(response.choices[0].message.content)

# Output bonito
print("\n========= IA CODE REVIEW =========")
for issue in result["issues"]:
    print(" -", issue)
print("==================================\n")

# Fail pipeline if necessary
if result["status"] == "fail":
    print("❌ AI Detected problems — blocking merge.")
    sys.exit(1)

print("✔ AI Review Passed — no critical issues detected.")
