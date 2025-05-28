# Jogo de Zumbis vs Azuis

Este projeto é um jogo em um tabuleiro 50x50 onde elementos azuis tentam chegar ao lado direito enquanto zumbis tentam infectá-los. O jogo termina quando todos os elementos viram zumbis ou quando um azul chega à coluna 49.

## Como Executar
1. Instale o Python 3.1 ou superior ([baixe aqui](https://www.python.org/)).
2. Instale o Pygame: abra o terminal e digite `pip install pygame`.
3. Clone este repositório ou salve o código em um arquivo `.py`.
4. Execute no terminal: `python jogo_concorrente.py`.
- Recomendado para melhor desempenho ou uso offline.

## Sobre o Código
O jogo usa **programação concorrente** com **threads** para simular movimentos simultâneos:
- Cada elemento (azul ou zumbi) roda em sua própria thread.
- Um **lock** evita conflitos no tabuleiro.
- O loop principal sincroniza os turnos com `t.join()`.

Veja o código completo [aqui](jogo_concorrente.py) para mais detalhes.

## Requisitos
- Python 3.1+
- Biblioteca Pygame