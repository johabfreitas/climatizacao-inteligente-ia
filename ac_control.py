def determine_ac_state(people_count: int):
    """
    Determina o estado do ar condicionado com base na contagem de pessoas.
    Retorna um dicionário com:
    - status: O status do ar condicionado (str)
    - temp: A temperatura recomendada (str)
    - color: Código hexadecimal de cor correspondente ao estado (para a UI)
    - badge_class: Classe CSS para estilização (str)
    - description: Descrição da regra aplicada (str)
    """
    if people_count == 0:
        return {
            "status": "DESLIGADO",
            "temp": "N/A",
            "color": "#64748b",  # Slate-500
            "badge_class": "status-off",
            "description": "Nenhuma pessoa detectada no ambiente. Ar condicionado desligado para máxima economia."
        }
    elif 1 <= people_count <= 2:
        return {
            "status": "LIGADO - Econômico",
            "temp": "24°C",
            "color": "#10b981",  # Emerald-500
            "badge_class": "status-eco",
            "description": f"Ambiente com {people_count} {'pessoa' if people_count == 1 else 'pessoas'}. Climatização em modo econômico para poupar energia."
        }
    elif 3 <= people_count <= 5:
        return {
            "status": "LIGADO - Moderado",
            "temp": "22°C",
            "color": "#0ea5e9",  # Sky-500
            "badge_class": "status-mod",
            "description": f"Ambiente com {people_count} pessoas. Climatização em modo moderado para conforto térmico padrão."
        }
    else:  # people_count > 5
        return {
            "status": "LIGADO - Potência Máxima",
            "temp": "19°C",
            "color": "#ef4444",  # Red-500
            "badge_class": "status-max",
            "description": f"Ambiente com alta ocupação ({people_count} pessoas). Climatização em modo de potência máxima para resfriamento rápido."
        }
