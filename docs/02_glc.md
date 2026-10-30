# F4 - F6: Gramática Libre de Contexto (GLC)

## F4. GLC inicial

- **Símbolo inicial (S):** `<programa>`
- **No terminales (NT) de la gramática final (tras F6):** `<programa>`, `<programa'>`, `<regla>`, `<condicion>`, `<condicion_tail>`, `<comparacion>`, `<factor_cond>`, `<op_rel>`, `<acciones>`, `<acciones_tail>`, `<accion>`
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

## F5. Análisis de recursión izquierda

### Análisis de recursión izquierda
Una producción presenta recursión izquierda directa si es de la forma $A \rightarrow A\alpha$, donde el no terminal de la cabecera aparece como el primer símbolo del cuerpo de la producción. La recursión izquierda es problemática para analizadores predictivos descendentes como LL(1), ya que produce bucles infinitos.

| No terminal | Tipo (directa/indirecta) | Producción(es) analizadas | Observaciones |
|---|---|---|---|
| `<programa>` | No presenta | `<programa> → <regla> <programa> \| <regla>` | El primer símbolo es `<regla>`, no `<programa>`. Presenta recursión derecha y requiere factorización por la izquierda (ver F6), pero no tiene recursión izquierda. |
| `<comparacion>` | No presenta | `<comparacion> → NOT <comparacion> \| <factor_cond> <op_rel> <factor_cond>` | La producción `<comparacion> → NOT <comparacion>` inicia con el terminal `NOT`. Se trata de **recursión derecha / operador prefijo**, no de recursión izquierda. La segunda alternativa inicia con `<factor_cond>`. |
| `<condicion_tail>` | No presenta | `<condicion_tail> → AND <comparacion> <condicion_tail> \| OR <comparacion> <condicion_tail> \| ε` | Inician con terminales `AND`, `OR` o $\epsilon$. Es recursiva por la derecha. |
| `<acciones_tail>` | No presenta | `<acciones_tail> → , <accion> <acciones_tail> \| ε` | Inicia con el separador `,` o $\epsilon$. Es recursiva por la derecha. |
| Resto de NTs | No presenta | `<regla>`, `<condicion>`, `<factor_cond>`, `<op_rel>`, `<acciones>`, `<accion>` | Sus cuerpos inician con terminales u otros no terminales sin ciclos recursivos indirectos. |

### Conclusión F5
Tras revisar exhaustivamente todas las producciones directas y las posibles cadenas de derivación indirecta, **se concluye que la gramática inicial no posee recursión izquierda (ni directa ni indirecta)**. Por lo tanto, no se requiere aplicar el algoritmo de transformación de eliminación de recursión izquierda ($A \rightarrow A\alpha \mid \beta \implies A \rightarrow \beta A', A' \rightarrow \alpha A' \mid \epsilon$). 

La estructura requiere únicamente factorización por la izquierda en `<programa>` para eliminar el prefijo común `<regla>`, lo cual se resuelve en la sección F6.

## F6. Factorización izquierda y ambigüedades

### Factorización izquierda
La factorización por la izquierda se aplica cuando dos o más alternativas para un no terminal comparten un prefijo común (es decir, $A \rightarrow \alpha\beta_1 \mid \alpha\beta_2$). Esto genera conflicto en LL(1) porque al ver un token perteneciente a $FIRST(\alpha)$ el parser no sabría cuál alternativa elegir sin adelantarse.

| No terminal | Prefijos comunes | Factorización aplicada (antes/después) | Resultado |
|---|---|---|---|
| `<programa>` | Prefijo común `<regla>` | **Antes:**<br>`<programa> → <regla> <programa> \| <regla>`<br><br>**Después:**<br>`<programa> → <regla> <programa'>`<br>`<programa'> → <regla> <programa'> \| ε` | Se extrae el prefijo común `<regla>` introduciendo el nuevo no terminal `<programa'>`. Permite análisis predictivo LL(1) determinista. |
| `<comparacion>` | Ninguno | Las alternativas son `NOT <comparacion>` y `<factor_cond> <op_rel> <factor_cond>`. Sus primeros símbolos son disjuntos: $FIRST(\text{rama 1}) = \{\texttt{NOT}\}$ y $FIRST(\text{rama 2}) = \{\texttt{ID}, \texttt{NUM}, \texttt{TRUE}, \texttt{FALSE}\}$. | No requiere factorización. Ambas opciones se distinguen inmediatamente con un lookahead de 1 token. |
| Demás no terminales | Ninguno | `<condicion_tail>` inicia con `AND`, `OR` o $\epsilon$; `<acciones_tail>` inicia con `,` o $\epsilon$. | No presentan prefijos comunes compartidos entre alternativas. |

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

**Observación:** La gramática ha sido factorizada por la izquierda en `<programa>` y se verificó la ausencia de recursión izquierda. Se integra la extensión creativa propuesta por Martín González (Operador NOT y Múltiples Acciones) tal como se especifica en `Tarea T1 Martin Gonzalez.pdf`. La conciliación entre la propuesta T1 y esta gramática final está en `docs/T1_conciliacion.md`.
