# SmartHomeLang

Proyecto de Teoría de la Computación que implementa un analizador para
**SmartHomeLang**, un lenguaje específico de dominio (DSL) para describir reglas
de automatización de una casa inteligente. El programa tokeniza y valida la
sintaxis de las reglas mediante un parser LL(1) por descenso recursivo, construye
un árbol de sintaxis abstracta (AST) y muestra errores léxicos o sintácticos con
su ubicación.

El proyecto valida programas; no ejecuta acciones ni controla dispositivos.

## Requisitos

- Python 3.10 o superior.
- No requiere dependencias externas.

## Inicio rápido

Desde la raíz del proyecto, ejecuta la suite de pruebas:

```bash
python3 test_runner.py --casos casos_prueba.json --casos casos_limite.json
```

El runner imprime el resultado de cada caso y guarda un reporte JSON en
`resultados_obtenidos.json`. Para elegir otra ubicación para el reporte:

```bash
python3 test_runner.py \
  --casos casos_prueba.json \
  --casos casos_limite.json \
  --salida reporte.json
```

La suite incluye 25 casos: 10 válidos y 10 inválidos en `casos_prueba.json`, más
4 válidos y 1 inválido en `casos_limite.json`.

## Sintaxis del lenguaje

Un programa contiene una o más reglas. Cada regla empieza con `WHEN`, expresa
una condición, separa las acciones con `THEN` y termina en punto y coma:

```text
WHEN <condición> THEN <acción>[, <acción>...];
```

La condición se construye con comparaciones, `NOT`, y los conectores `AND` y
`OR`. Una comparación tiene la forma `<factor> <operador-relacional> <factor>`.
Los factores pueden ser identificadores, números enteros o los literales
booleanos `TRUE` y `FALSE`.

Ejemplo con una condición compuesta y varias acciones:

```text
WHEN NOT movimiento == TRUE AND temperatura < 18
THEN encender_calefaccion, enviar_notificacion;
```

Se permiten varias reglas en una misma entrada:

```text
WHEN temperatura > 28 THEN encender_ventilador;
WHEN humedad < 40 THEN activar_humidificador;
```

### Tokens admitidos

| Elemento | Formato |
|---|---|
| Palabras reservadas | `WHEN`, `THEN`, `AND`, `OR`, `NOT`, `TRUE`, `FALSE` |
| Identificadores | `[A-Za-z_][A-Za-z0-9_]*` |
| Números | Enteros no negativos, por ejemplo `18` o `28` |
| Operadores relacionales | `>`, `<`, `>=`, `<=`, `==`, `!=` |
| Separadores | `,` entre acciones y `;` al final de cada regla |
| Espacios en blanco | Espacios, tabuladores y saltos de línea; se ignoran |

Las palabras reservadas no distinguen mayúsculas de minúsculas. Los
identificadores conservan la forma en que fueron escritos y no pueden coincidir
con una palabra reservada.

## Comandos

Mostrar el AST de una entrada válida:

```bash
python3 test_runner.py --ast \
  "WHEN temperatura > 28 THEN encender_ventilador, abrir_ventana;"
```

El modo `--ast` imprime un mensaje de validación y la estructura jerárquica del
AST. Si la entrada no es válida, muestra el error y termina con un código de
salida distinto de cero.

Generar un archivo JSON con los 20 casos predeterminados:

```bash
python3 test_runner.py --generar-casos --casos casos_generados.json
```

Consultar todas las opciones:

```bash
python3 test_runner.py --help
```

Los archivos de casos JSON contienen una lista de objetos con los campos
`entrada` y `esperado` (`"valido"` o `"invalido"`); también pueden incluir
`desc` para describir el caso. Se pueden cargar varios archivos repitiendo
`--casos`.

## Estructura del proyecto

| Ruta | Descripción |
|---|---|
| `test_runner.py` | Lexer, tabla LL(1), parser, construcción e impresión del AST y runner de pruebas. |
| `casos_prueba.json` | 20 casos: 10 válidos y 10 inválidos. |
| `casos_limite.json` | 5 casos límite: 4 válidos y 1 inválido. |
| `resultados_obtenidos.json` | Reporte JSON generado por la última ejecución del runner. |
| `docs/01_definicion_dsl.md` | Dominio, alfabeto, tokens y ejemplos del DSL. |
| `docs/02_glc.md` | Gramática libre de contexto, recursión y factorización. |
| `docs/03_first_follow.md` | Cálculo de los conjuntos FIRST y FOLLOW. |
| `docs/04_tabla_ll1.md` | Construcción de la tabla predictiva y revisión de conflictos. |
| `docs/PLAN_FRANCISCO_BENAVIDES.md` | Documento de planificación del proyecto. |
