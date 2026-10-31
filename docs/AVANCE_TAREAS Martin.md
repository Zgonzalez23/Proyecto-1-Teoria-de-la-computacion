# AVANCE DE TAREAS

## Detalle de tareas completadas

### T2 — Integración de la Extensión en GLC / FIRST / FOLLOW

La extensión creativa (operador `NOT` y múltiples acciones con `,`) está integrada en la teoría documentada:

- **GLC final** (`docs/02_glc.md`):
  - `<comparacion> → NOT <comparacion> \| <factor_cond> <op_rel> <factor_cond>`
  - `<acciones_tail> → , <accion> <acciones_tail> \| ε`
  - Gramática sin recursión izquierda, factorizada, LL(1)
- **FIRST / FOLLOW** (`docs/03_first_follow.md`): conjuntos calculados incluyendo `NOT`
- **Tabla LL(1)** (`docs/04_tabla_ll1.md`): 0 conflictos, verificada celda por celda

### T3 — Runner de pruebas automáticas en Python (`test_runner.py`)

Implementa tres capas:

1. **Lexer (analizador léxico):** tokeniza según la tabla de tokens de `docs/01_definicion_dsl.md`
   - Palabras reservadas: `WHEN`, `THEN`, `AND`, `OR`, `NOT`, `TRUE`, `FALSE`
   - Identificadores: `[A-Za-z_][A-Za-z0-9_]*`
   - Números enteros, operadores relacionales (`>= <= == != > <`), símbolos `;`, `,`

2. **Parser LL(1) por descenso recursivo:** implementa todas las producciones de la GLC final
   - Coincide 100% con la gramática documentada (requisito de T10)

3. **Runner de suite:** ejecuta casos, compara esperado vs obtenido, imprime reporte por consola y exporta JSON

**CLI:**
```bash
python3 test_runner.py --casos archivo1.json --casos archivo2.json --salida salida.json
python3 test_runner.py --generar-casos --casos casos_prueba.json
```

### T4 — 10 casos válidos + 10 casos inválidos (`casos_prueba.json`)

**Válidos (10):** condición simple `>` / `<`, booleano `== TRUE`, `AND` / `OR`, `NOT` sobre comparación, múltiples acciones con coma, y combinaciones de la extensión completa.

**Inválidos (10):** falta acción, falta condición tras `NOT`, falta `WHEN`, falta `;`, coma final sin acción, `NOT` seguido de operador relacional, falta coma entre acciones, acción `NUM` en lugar de `ID`, falta valor tras `==`, falta condición completa.

### T5 — 5 casos límite (`casos_limite.json`)

| # | Entrada | Esperado | Descripción |
|---|---------|----------|-------------|
| 1 | Múltiples reglas (`…; WHEN …;`) | válido | Programa recursivo |
| 2 | `WHEN NOT NOT movimiento == TRUE …` | válido | NOT anidado (recursividad en `<comparacion>`) |
| 3 | `WHEN a > 1 AND b < 2 AND c < 3 THEN …` | válido | Cadena de 3 condiciones con AND |
| 4 | `WHEN … THEN a, b, c;` | válido | 3 acciones separadas por coma |
| 5 | `WHEN a > 1 AND THEN …` | inválido | AND colgando sin segunda condición |

### T6 — Ejecución de suite completa y matriz Esperado vs Obtenido

**Comando ejecutado:**
```bash
python3 test_runner.py --casos casos_prueba.json --casos casos_limite.json --salida resultados_obtenidos.json
```

**Resultado final:**
```
Total casos: 25  |  Pasados: 25  |  Fallos: 0
Válidos esperados: 14  |  Inválidos esperados: 11
RESULTADO FINAL: 25/25 casos coinciden | 100% de acierto
```

**Matriz consolidada:** todos los 25 casos muestran `Esperado = Obtenido` con estado `OK`. El reporte detallado se exportó a `resultados_obtenidos.json`.

---

## Archivos en el repositorio

```
Proyecto-1-Teoria-de-la-computacion/
├── README.md
├── test_runner.py              # Runner de pruebas (lexer + parser LL(1) + suite)
├── casos_prueba.json           # 20 casos: 10 válidos + 10 inválidos (T4)
├── casos_limite.json           # 5 casos borde / sintaxis compleja (T5)
├── resultados_obtenidos.json   # Reporte JSON de la suite ejecutada (T6)
└── docs/
    ├── 01_definicion_dsl.md    # DSL, alfabeto, tokens, ejemplos (T1 base)
    ├── 02_glc.md               # GLC final con extensión integrada (T2)
    ├── 03_first_follow.md      # Conjuntos FIRST y FOLLOW (T2)
    ├── 04_tabla_ll1.md         # Tabla LL(1) sin conflictos (T2)
    └── PLAN_FRANCISCO_BENAVIDES.md
```

