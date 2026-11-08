def aproximar(atual, alvo, taxa, dt):
    """Move 'atual' suavemente em direcao a 'alvo' (suavizacao exponencial)."""
    return atual + (alvo - atual) * min(1.0, taxa * dt)


def limitar(v, minimo, maximo):
    return max(minimo, min(maximo, v))
