# F1 - F3: Definición del DSL

## F1. Nombre, dominio y propósito

- **Nombre del DSL:** `SmartHomeLang`
- **Dominio:** IoT / Smart Home
- **Propósito:** Desarrollar un lenguaje de dominio específico (DSL) para definir reglas de automatización en una casa inteligente. Permite expresar sentencias del tipo "SI ocurre una condición ENTONCES ejecutar una o más acciones", facilitando el control automatizado de dispositivos como luces, ventiladores, alarmas, sensores, etc.
- **Audiencia / Alcance:** Dirigido a la definición de reglas simples de automatización. El lenguaje se limita a reglas condicionales con operadores relacionales y lógicos, acciones sobre dispositivos e inclusión de la extensión creativa (operador NOT y múltiples acciones). No contempla bucles complejos, funciones ni estructuras anidadas avanzadas.

## F2. Alfabeto, tokens, palabras reservadas e identificadores

### Alfabeto
Se consideran los siguientes caracteres permitidos:
- Letras: `A-Z`, `a-z`
- Dígitos: `0-9`
- Símbolos: `>`, `<`, `=`, `!`, `;`, `,`, `(`, `)`, espacio, tabulador, salto de línea
- Guion bajo: `_`

### Palabras reservadas (mínimo 4)
| Palabra reservada | Descripción |
|---|---|
| `WHEN` | Inicia una regla de automatización. Indica la condición a evaluar. |
| `THEN` | Separa la condición de las acciones a ejecutar. |
| `AND` | Operador lógico de conjunción entre comparaciones. |
| `OR` | Operador lógico de disyunción entre comparaciones. |
| `NOT` | Operador lógico unario para negación de una condición (Extensión Creativa). |
| `TRUE` | Valor booleano verdadero. |
| `FALSE` | Valor booleano falso. |

### Identificadores
- **Regla:** `[A-Za-z_][A-Za-z0-9_]*`
- **Restricciones:** Deben comenzar con letra o guion bajo, pueden contener letras, dígitos o guion bajo. No pueden ser palabras reservadas. Se utilizan para nombrar dispositivos, sensores o acciones (ej: `temperatura`, `movimiento`, `encender_luces`).

### Números / Literales
- **Números enteros:** `[0-9]+` (ej: `28`, `40`, `100`)
- **Valores booleanos:** `TRUE`, `FALSE`

### Tabla de tokens
| Token | Tipo | Expresión / Descripción |
|---|---|---|
| `WHEN` | PALABRA_RESERVADA | `WHEN` |
| `THEN` | PALABRA_RESERVADA | `THEN` |
| `AND` | PALABRA_RESERVADA | `AND` |
| `OR` | PALABRA_RESERVADA | `OR` |
| `NOT` | PALABRA_RESERVADA (Extensión) | `NOT` |
| `TRUE` | PALABRA_RESERVADA/LITERAL | `TRUE` |
| `FALSE` | PALABRA_RESERVADA/LITERAL | `FALSE` |
| `ID` | IDENTIFICADOR | `[A-Za-z_][A-Za-z0-9_]*` |
| `NUM` | NUMERO | `[0-9]+` |
| `OP_REL` | OPERADOR RELACIONAL | `>= \| <= \| == \| != \| > \| <` |
| `PUNTO_COMA` | SEPARADOR | `;` |
| `COMA` | SEPARADOR (Extensión) | `,` |
| `PARENT_IZQ` | SEPARADOR | `\(` |
| `PARENT_DER` | SEPARADOR | `\)` |
| `ESPACIO` | IGNORAR | `[ \t\n]+` |
| `ERROR` | ERROR | `.` |

## F3. Ejemplos válidos e inválidos

### Ejemplos válidos (5)
| # | Código / Expresión | Explicación |
|---|---|---|
| 1 | `WHEN temperatura > 28 THEN encender_ventilador;` | Regla básica con comparación relacional. |
| 2 | `WHEN movimiento == TRUE AND humedad < 40 THEN activar_alarma;` | Regla con operador lógico AND y dos comparaciones. |
| 3 | `WHEN NOT movimiento == TRUE THEN apagar_luces;` | Uso del operador NOT (Extensión Creativa). |
| 4 | `WHEN temperatura > 28 THEN encender_ventilador, abrir_ventana;` | Múltiples acciones separadas por coma (Extensión Creativa). |
| 5 | `WHEN NOT alarma == TRUE THEN desactivar_sirena, enviar_notificacion;` | Combinación de NOT con múltiples acciones (Extensión Creativa). |

### Ejemplos inválidos (5)
| # | Código / Expresión | Error intencional | Explicación de por qué es inválido |
|---|---|---|---|
| 1 | `WHEN NOT THEN encender_luces;` | Falta condición después de NOT | Tras `NOT` debe venir una condición o comparación, no directamente `THEN`. |
| 2 | `WHEN temperatura > 28 THEN ;` | Falta acción | Después de `THEN` debe existir al menos una acción, el punto y coma no es suficiente. |
| 3 | `WHEN temperatura > 28 THEN encender_ventilador,;` | Coma final sin acción | Hay una coma pero no hay una acción después de ella. |
| 4 | `WHEN temperatura > 28 THEN encender_ventilador abrir_ventana;` | Falta coma entre acciones | Para múltiples acciones se requiere separar con `,`. |
| 5 | `WHEN temperatura > 28 encender_ventilador;` | Falta palabra reservada THEN | La estructura `WHEN <condicion> THEN <acciones> ;` no se cumple, falta `THEN`. |
