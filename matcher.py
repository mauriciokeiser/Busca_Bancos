import warnings
# Garante o silenciamento do aviso também neste módulo
warnings.filterwarnings("ignore", message="Using slow pure-python SequenceMatcher")

from thefuzz import fuzz

def buscar_por_aproximacao_nome(termo, bancos, limite=5):
    """Compara o termo com o nome do banco de forma resiliente a erros."""
    resultados = []
    termo_limpo = termo.strip().lower()
    
    for banco in bancos:
        # Garante string válida para o comparador
        nome_banco = (banco["name"] or banco["fullName"] or "").strip().lower()
        if not nome_banco:
            continue
            
        # token_set_ratio é excelente em modo puro para strings pequenas
        score = fuzz.token_set_ratio(termo_limpo, nome_banco)
        
        banco_com_score = banco.copy()
        banco_com_score["score"] = score
        resultados.append(banco_com_score)
        
    resultados.sort(key=lambda x: x["score"], reverse=True)
    return resultados[:limite]

def buscar_por_codigo_tolerante(codigo_alvo, bancos):
    """Busca aproximada de códigos (corrige erros como digitar 340 ao invés de 341)."""
    resultados = []
    str_alvo = str(codigo_alvo).strip()
    
    for banco in bancos:
        str_codigo = str(banco["code"]) if banco["code"] is not None else ""
        if not str_codigo:
            continue
            
        # ratio simples é mais rápido e preciso para strings numéricas curtas
        score = fuzz.ratio(str_alvo, str_codigo)
        
        banco_com_score = banco.copy()
        banco_com_score["score"] = score
        resultados.append(banco_com_score)
        
    resultados.sort(key=lambda x: x["score"], reverse=True)
    return [r for r in resultados if r["score"] > 40][:5]

def agrupar_bancos_similares(bancos, corte_similaridade=85):
    """Agrupa bancos que possuem nomes parecidos."""
    grupos = {}
    visitados = set()
    
    for i, banco_atual in enumerate(bancos):
        nome_atual = (banco_atual["name"] or "").strip()
        if not nome_atual or nome_atual.lower() in visitados:
            continue
            
        grupo_atual = [banco_atual]
        visitados.add(nome_atual.lower())
        
        for j in range(i + 1, len(bancos)):
            banco_comp = bancos[j]
            nome_comp = (banco_comp["name"] or "").strip()
            
            if nome_comp and nome_comp.lower() not in visitados:
                score = fuzz.token_sort_ratio(nome_atual.lower(), nome_comp.lower())
                if score >= corte_similaridade:
                    grupo_atual.append(banco_comp)
                    visitados.add(nome_comp.lower())
                    
        if len(grupo_atual) > 1:
            grupos[nome_atual] = grupo_atual
            
    return grupos