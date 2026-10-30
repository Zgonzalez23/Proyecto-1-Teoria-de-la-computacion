# Proyecto-1-Teoria-de-la-computacion

DSL **SmartHomeLang** para reglas de automatización de casa inteligente, con análisis
léxico, parser LL(1) por descenso recursivo, AST y manejo de errores sintácticos.

## Requisitos

- Python 3.10 o superior.
- Sin dependencias externas.

## Ejecución

```bash
# Suite completa (25 casos: 20 de casos_prueba.json + 5 de casos_limite.json)
python3 test_runner.py --casos casos_prueba.json --casos casos_limite.json

# Guardar el reporte en JSON
python3 test_runner.py --casos casos_prueba.json --casos casos_limite.json \
  --salida resultados_obtenidos.json

# Mostrar el AST de una entrada
python3 test_runner.py --ast "WHEN temperatura > 28 THEN encender_ventilador, abrir_ventana;"
```

## Estructura

| Archivo | Contenido |
|---|---|
| `test_runner.py` | Lexer, parser LL(1), AST, errores y runner de pruebas. |
| `casos_prueba.json` | 10 casos válidos y 10 inválidos. |
| `casos_limite.json` | 5 casos límite. |
| `resultados_obtenidos.json` | Reporte de la última ejecución. |
| `docs/01_definicion_dsl.md` | F1-F3: dominio, tokens y ejemplos. |
| `docs/02_glc.md` | F4-F6: gramática, recursión y factorización. |
| `docs/03_first_follow.md` | F7-F8: FIRST y FOLLOW. |
| `docs/04_tabla_ll1.md` | F9-F10: tabla LL(1) y conflictos. |
| `docs/T1_conciliacion.md` | Ajuste de la extensión creativa a la gramática final. |
| `docs/T1_errores_lexicos.md` | Errores léxicos y sintácticos detectados en los ejemplos de la T1. |

## Notación

La gramática usa la notación formal y el código usa identificadores de Python. La
correspondencia es:

| Formal (GLC) | Token / código |
|---|---|
| `<programa'>` | `programa_prima` |
| `;` | `PUNTO_COMA` |
| `,` | `COMA` |
| `$` | `EOF` |
| `>`, `<`, `>=`, `<=`, `==`, `!=` | `OP_REL` |
| `ε` | `"epsilon"` |

## Ejemplo

```text
WHEN NOT movimiento == TRUE THEN apagar_luces, enviar_notificacion;
```

Tokens principales: `WHEN`, `NOT`, `ID`, `OP_REL`, `TRUE`, `THEN`, `ID`, `COMA`, `ID`,
`PUNTO_COMA`, `EOF`.

## Resultado esperado

```text
RESULTADO FINAL: 25/25 pasados | 0 fallidos
```
