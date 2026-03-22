# 🔢 Sudoku — Terminal + Interface Gráfica

> Implementação completa do jogo **Sudoku** em Python, com versão no terminal e interface gráfica interativa com Tkinter. Fork e evolução do projeto da [Digital Innovation One](https://github.com/digitalinnovationone/sudoku).

<div align="center">

![Python](https://img.shields.io/badge/Python-3.11+-3776AB?style=flat&logo=python&logoColor=white)
![Tkinter](https://img.shields.io/badge/UI-Tkinter-FF6B35?style=flat)
![License](https://img.shields.io/badge/License-MIT-green?style=flat)

</div>

---

## 📋 Funcionalidades

| Feature | Terminal | Interface Gráfica |
|---------|----------|-------------------|
| Tabuleiro 9×9 | ✅ | ✅ |
| Células fixas (pré-preenchidas) | ✅ | ✅ |
| Validação de movimentos | ✅ | ✅ |
| Detecção de vitória | ✅ | ✅ |
| Highlight de erros | ❌ | ✅ |
| Botão de dica | ❌ | ✅ |
| Verificar solução | ❌ | ✅ |
| Novo jogo | ❌ | ✅ |
| Timer | ❌ | ✅ |

---

## 🚀 Como Rodar

### Terminal (branch main)

```bash
git clone https://github.com/SEU_USUARIO/sudoku.git
cd sudoku
python src/main_terminal.py
```

### Com argumentos de posição

```bash
python src/main_terminal.py \
  "0,0;4,false 1,0;7,false 2,0;9,true ..."
```

### Interface Gráfica (branch ui)

```bash
python src/main_ui.py
```

---

## 📐 Formato dos Argumentos

Cada célula é definida como `col,row;valor,fixo`:

```
0,0;4,false   → coluna=0, linha=0, valor=4, não-fixo (editável)
2,0;9,true    → coluna=2, linha=0, valor=9, fixo (pré-preenchido)
```

### Tabuleiro de exemplo (usado nos testes)

```
0,0;4,false 1,0;7,false 2,0;9,true 3,0;5,false 4,0;8,true 5,0;6,true 6,0;2,true 7,0;3,false 8,0;1,false ...
```

---

## 🗂️ Estrutura

```
sudoku/
├── src/
│   ├── sudoku.py          # Modelo — lógica do tabuleiro
│   ├── main_terminal.py   # Branch main — jogo no terminal
│   └── main_ui.py         # Branch ui — interface gráfica Tkinter
├── docs/
│   └── architecture.md    # Diagrama da arquitetura
├── README.md
└── requirements.txt
```

---

## 🧠 Arquitetura

```
┌─────────────────────────────────────┐
│           SudokuBoard               │
│  • grid: list[list[Cell]]           │
│  • parse_args(args_string) → grid   │
│  • is_valid_move(col, row, val)      │
│  • is_complete() → bool             │
│  • get_hint() → (col, row, val)     │
└──────────────┬──────────────────────┘
               │
       ┌───────┴───────┐
       │               │
┌──────▼──────┐  ┌─────▼──────────┐
│  Terminal   │  │  Tkinter UI    │
│  main_      │  │  SudokuUI      │
│  terminal   │  │  Canvas + Grid │
└─────────────┘  └────────────────┘
```

---

## 📚 Referências

- [Repositório original DIO](https://github.com/digitalinnovationone/sudoku)
- [Draw.io — diagramas](https://app.diagrams.net)
