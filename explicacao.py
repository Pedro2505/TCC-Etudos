import pandas as pd
import shap
import numpy as np
import matplotlib.pyplot as plt
from extrator import carregar_artefatos, preparar_para_inferencia

# ==============================================================================
# SCRIPT DE EXPLICABILIDADE DE INTELIGÊNCIA ARTIFICIAL (XAI)
# Utiliza os valores de SHAP (Teoria dos Jogos) para abrir a "Caixa Preta"
# e provar matematicamente O PORQUÊ de um bloqueio ocorrer.
# ==============================================================================

print("1. Carregando os modelos do WAF...")
modelo, vetorizador, metadata = carregar_artefatos()
limiar = metadata.get('limiar_decisao', 0.5)

payload = "<script>alert('Ataque Direto')</script>"
print(f"[*] Payload interceptado: {payload}")

# Usa o caminho único de inferência, o mesmo que o servidor.py executa em produção.
X_payload = preparar_para_inferencia(payload.lower(), vetorizador, metadata.get('colunas'))
probabilidade = float(modelo.predict_proba(X_payload)[0][1])
print(f"[*] Probabilidade de ataque: {probabilidade:.4f} | limiar: {limiar:.3f} | "
      f"decisão: {'BLOQUEADO' if probabilidade >= limiar else 'PERMITIDO'}")

print("\n2. Executando o SHAP TreeExplainer (Dissecando a Árvore de Decisão)...")
# O TreeExplainer calcula a contribuição exata (margem) de cada feature para o resultado
explainer = shap.TreeExplainer(modelo)
shap_values = explainer.shap_values(X_payload)  # type: ignore

# A versão moderna do SHAP retorna uma matriz numpy 3D para RandomForest: (n_samples, n_features, n_classes)
# Queremos a explicação da linha 0, de todas as features, para a Classe 1 (Ataque).
if isinstance(shap_values, list):
    shap_valores_ataque = shap_values[1][0]
elif len(shap_values.shape) == 3:
    shap_valores_ataque = shap_values[0, :, 1]
else:
    shap_valores_ataque = shap_values[0]

# Mapeia as Colunas (Features) vs Valores de Culpa (SHAP Values)
importancias = list(zip(X_payload.columns, shap_valores_ataque))
# Ordena: De quem mais ajudou a bloquear, para quem mais atrapalhou
importancias.sort(key=lambda x: x[1], reverse=True)

print("\n================ DIAGNÓSTICO DO BLOQUEIO ================")
print(f"Decisão do Modelo: ATAQUE DETECTADO")
print("Por quê? (Top 3 Features Condenatórias):")
for feature, peso in importancias[:3]:
    if peso > 0:
        print(f" [+] O fator '{feature}' elevou a suspeita em +{peso:.4f} pontos.")

print("\nO que quase enganou o modelo? (Top Features que apontavam inocência):")
for feature, peso in importancias[-3:]:
    if peso < 0:
        print(f" [-] O fator '{feature}' reduziu a suspeita em {peso:.4f} pontos.")
print("=========================================================\n")

# Gera a prova visual
print("3. Plotando o Gráfico Waterfall de Culpabilidade...")
base_val = explainer.expected_value[1] if isinstance(explainer.expected_value, (list, tuple, np.ndarray)) else explainer.expected_value
shap.waterfall_plot(shap.Explanation(values=shap_valores_ataque, 
                                     base_values=float(base_val),
                                     data=X_payload.iloc[0], 
                                     feature_names=X_payload.columns), show=False)

plt.title(f"XAI: Anatomia de um Bloqueio (SHAP)\nPayload: {payload}")
plt.tight_layout()
caminho_grafico = 'docs/shap_explain_report.png'
plt.savefig(caminho_grafico)
print(f"[OK] Laudo Pericial exportado como imagem: {caminho_grafico}")
