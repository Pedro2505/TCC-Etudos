import requests
import base64
import urllib.parse
import time

print("="*60)
print("TESTE DE EVASÃO - WAF (Adversarial Robustness)")
print("Objetivo: Tentar bypassar o firewall usando ofuscação.")
print("="*60)

url = "http://127.0.0.1:8000/busca"
payload_original = "<script>alert('Fui hackeado')</script>"

# Lista de técnicas que hackers usam para burlar Filtros/WAFs
payloads_ofuscados = {
    "1. Texto Puro": payload_original,
    "2. URL Encode Simples": urllib.parse.quote(payload_original),
    "3. Double URL Encode": urllib.parse.quote(urllib.parse.quote(payload_original)),
    "4. Base64 Puro": base64.b64encode(payload_original.encode()).decode(),
    "5. Case Mixing (Caixa Alta/Baixa)": "<ScRiPt>aLeRt('Fui hackeado')</sCrIpT>"
}

for nome, payload in payloads_ofuscados.items():
    try:
        # A requisição simula um acesso do navegador
        res = requests.get(f"{url}?q={payload}", timeout=3)
        
        if res.status_code == 403:
            print(f"[BLOQUEADO] {nome: <35} -> WAF vitorioso.")
        else:
            print(f"[BYPASS CRÍTICO] {nome: <30} -> O ataque passou!")
            
    except requests.exceptions.ConnectionError:
        print(f"[ERRO] Falha de conexão. O servidor (servidor.py) está rodando na porta 8000?")
        break
        
    time.sleep(0.2)
print("="*60)
