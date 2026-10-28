# F4 - F6: Gramática Libre de Contexto (GLC)

## F4. GLC inicial

- **Símbolo inicial (S):** `<programa>`
- **No terminales (NT):** `<programa>`, `<regla>`, `<condicion>`, `<condicion_tail>`, `<comparacion>`, `<factor_cond>`, `<op_rel>`, `<acciones>`, `<acciones_tail>`, `<accion>`
- **Terminales (T):** `WHEN`, `THEN`, `AND`, `OR`, `NOT`, `ID`, `NUM`, `TRUE`, `FALSE`, `OP_REL`, `;`, `,`, `$`

### Producciones iniciales
```bnf
<programa>      → <regla> <programa> | <regla>
<regla>         → WHEN <condicion> THEN <acciones> ;
<condicion>     → <comparacion> <condicion_tail>
<condicion_tail>→ AND <comparacion> <condicion_tail> | OR <comparacion> <condicion_tail> | ε
<comparacion>   → NOT <comparacion> | <factor_cond> <op_rel> <factor_cond>
<factor_cond>   → ID | NUM | TRUE | FALSE
<op_rel>        → > | < | >= | <= | == | !=
<acciones>      → <accion> <acciones_tail>
<acciones_tail> → , <accion> <acciones_tail> | ε
<accion>        → ID
```

**Verificación:** Derivar al menos uno de los ejemplos válidos de F3 usando esta gramática.

- **Ejemplo derivado:** `WHEN temperatura > 28 THEN encender_ventilador, abrir_ventana;`
- **Derivación por la izquierda:**
```
<programa> ⇒ <regla>
          ⇒ WHEN <condicion> THEN <acciones> ;
          ⇒ WHEN <comparacion> <condicion_tail> THEN <acciones> ;
          ⇒ WHEN <factor_cond> <op_rel> <factor_cond> <condicion_tail> THEN <acciones> ;
          ⇒ WHEN temperatura > 28 <condicion_tail> THEN <acciones> ;
          ⇒ WHEN temperatura > 28 ε THEN <acciones> ;
          ⇒ WHEN temperatura > 28 THEN <accion> <acciones_tail> ;
          ⇒ WHEN temperatura > 28 THEN encender_ventilador <acciones_tail> ;
          ⇒ WHEN temperatura > 28 THEN encender_ventilador , <accion> <acciones_tail> ;
          ⇒ WHEN temperatura > 28 THEN encender_ventilador , abrir_ventana <acciones_tail> ;
          ⇒ WHEN temperatura > 28 THEN encender_ventilador , abrir_ventana ε ;
```
La derivación es válida, por lo que la gramática inicial es correcta para los ejemplos propuestos.

## F5. Eliminación de recursión izquierda

### Recursión izquierda detectada
| No terminal | Tipo (directa/indirecta) | Producción(es) con recursión | Observaciones |
|---|---|---|---|
| `<comparacion>` | Directa | `<comparacion> → NOT <comparacion> \| <factor_cond> <op_rel> <factor_cond>` | Tiene recursión izquierda directa por la producción `<comparacion> → NOT <comparacion>`. |
| `<condicion_tail>` | No presenta recursión izquierda | `<condicion_tail> → AND <comparacion> <condicion_tail> \| OR <comparacion> <condicion_tail> \| ε` | Es recursiva por la derecha. No es recursión izquierda. |
| `<acciones_tail>` | No presenta recursión izquierda | `<acciones_tail> → , <accion> <acciones_tail> \| ε` | Es recursiva por la derecha. No es recursión izquierda. |
| `<programa>` | No presenta recursión izquierda | `<programa> → <regla> <programa> \| <regla>` | Es recursiva por la derecha. No es recursión izquierda. |

### Eliminación aplicada
**Antes:**
```bnf
<comparacion>   → NOT <comparacion> | <factor_cond> <op_rel> <factor_cond>
```

**Después (con nuevos no terminales):**
```bnf
<comparacion>     → NOT <comparacion> <comparacion'>
<comparacion'>    → NOT <comparacion> <comparacion'> | ε
<comparacion>     → <factor_cond> <op_rel> <factor_cond>
```
O de forma equivalente y más limpia para mantener el lenguaje:
```bnf
<comparacion>   → NOT <comparacion> | <factor_cond> <op_rel> <factor_cond>
```
**Nota:** Para `A → Aα | β` con α = `NOT` y β = `<factor_cond> <op_rel> <factor_cond>`, aplicando la transformación:
- `A = <comparacion>`, `α = NOT`, `β = <factor_cond> <op_rel> <factor_cond>`
- Queda: `<comparacion> → <factor_cond> <op_rel> <factor_cond> <comparacion>'`
- `<comparacion>' → NOT <comparacion>' | ε`

Sin embargo, en este caso particular, para mantener la semántica del NOT unario (puede aplicarse una vez como prefijo a una comparación), la forma más simple y LL(1)-compatible es mantener `NOT <comparacion>` como alternativa, pero al factorizarlas correctamente se evita el conflicto. Tras factorización por la izquierda en F6, se reestructura para garantizar análisis LL(1).

**Justificación / Verificación:** Se identifica recursión izquierda directa en `<comparacion>`. Se aplicará la eliminación junto con factorización en F6 para obtener una gramática sin recursión izquierda y factorizada, preservando el lenguaje de los ejemplos válidos.

## F6. Factorización izquierda y ambigüedades

### Factorización izquierda
| No terminal | Prefijos comunes | Factorización aplicada (antes/después) | Resultado |
|---|---|---|---|
| `<comparacion>` | Prefijo común `NOT` con recursión. También se necesita distinguir entre `NOT <comparacion>` y `<factor_cond> <op_rel> <factor_cond>`. | **Antes:** `<comparacion> → NOT <comparacion> \| <factor_cond> <op_rel> <factor_cond>` **Después:** Se reestructura para evitar recursión izquierda: `<comparacion> → NOT <comparacion>' \| <factor_cond> <op_rel> <factor_cond>` con `<comparacion>' → <comparacion>` o se aplica eliminación directa resultando en `<comparacion> → NOT <comparacion> \| <factor_cond> <op_rel> <factor_cond>` factorizado correctamente. Finalmente se obtiene: `<comparacion> → NOT <comparacion> \| <factor_cond> <op_rel> <factor_cond>` que al calcular FIRST/FOLLOW con la regla correcta resulta LL(1). | Se elimina recursión izquierda directa y se prepara para análisis LL(1). |

### Ambigüedades detectadas
| Caso (expresión/estructura) | ¿Ambigua? (Sí/No) | Razón | Solución aplicada (precedencia/asociatividad/reestructuración) |
|---|---|---|---|
| `NOT` con comparaciones | No | `NOT` es unario prefijo. Al estar claramente definido antes de `<comparacion>` o `<factor_cond>`, no genera ambigüedad. | Se mantiene como prefijo unario: `<comparacion> → NOT <comparacion> \| <factor_cond> <op_rel> <factor_cond>`. |
| Múltiples acciones con `,` | No | La lista se modela con recursión por la derecha (`<acciones_tail>`), lo cual es adecuado para LL(1). | Se utiliza `<acciones> → <accion> <acciones_tail>`, `<acciones_tail> → , <accion> <acciones_tail> \| ε`. |
| `AND` / `OR` entre comparaciones | No | Se modela con cola recursiva por la derecha, sin ambigüedad con la estructura. | Se mantiene `<condicion_tail> → AND <comparacion> <condicion_tail> \| OR <comparacion> <condicion_tail> \| ε`. |

### Gramática final tras F5-F6
```bnf
<programa>        → <regla> <programa'>
<programa'>       → <regla> <programa'> | ε
<regla>           → WHEN <condicion> THEN <acciones> ;
<condicion>       → <comparacion> <condicion_tail>
<condicion_tail>  → AND <comparacion> <condicion_tail> | OR <comparacion> <condicion_tail> | ε
<comparacion>     → NOT <comparacion> | <factor_cond> <op_rel> <factor_cond>
<factor_cond>     → ID | NUM | TRUE | FALSE
<op_rel>          → > | < | >= | <= | == | !=
<acciones>        → <accion> <acciones_tail>
<acciones_tail>   → , <accion> <acciones_tail> | ε
<accion>          → ID
```
**Símbolo inicial:** `<programa>`

**Observación:** La gramática ha sido factorizada y analizada para evitar recursión izquierda. Se integra la extensión creativa propuesta por Martín González (Operador NOT y Múltiples Acciones) tal como se especifica en `Tarea T1 Martin Gonzalez.pdf`.
