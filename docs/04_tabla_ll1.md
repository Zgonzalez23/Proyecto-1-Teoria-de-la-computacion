# F9 - F10: Tabla LL(1) y Verificación de Conflictos

## F9. Construcción de la Tabla Predictiva LL(1)

**Procedimiento:**
Para cada producción $A \rightarrow \alpha$:
1. Para cada terminal $a \in FIRST(\alpha)$, $a \neq \epsilon$, agregar $A \rightarrow \alpha$ a $M[A,a]$.
2. Si $\epsilon \in FIRST(\alpha)$, para cada terminal $b \in FOLLOW(A)$, agregar $A \rightarrow \alpha$ a $M[A,b]$.
3. Si $\epsilon \in FIRST(\alpha)$ y $\$ \in FOLLOW(A)$, agregar $A \rightarrow \alpha$ a $M[A,\$]$.

### Cálculo por producción

| Producción | FIRST(α) | ¿Contiene ε? | FOLLOW(A) | Entradas en tabla |
|---|---|---|---|---|
| `<programa> → <regla> <programa>'` | $FIRST(\texttt{<regla>}) = \{\texttt{WHEN}\}$ | No | $FOLLOW(\texttt{<programa>}) = \{\$\}$ | $M[\texttt{<programa>}, \texttt{WHEN}] = \texttt{<programa>} \rightarrow \texttt{<regla> <programa>'}$ |
| `<programa>' → <regla> <programa>'` | $FIRST(\texttt{<regla>}) = \{\texttt{WHEN}\}$ | No | $FOLLOW(\texttt{<programa>'}) = \{\$\}$ | $M[\texttt{<programa>'}, \texttt{WHEN}] = \texttt{<programa>'} \rightarrow \texttt{<regla> <programa>'}$ |
| `<programa>' → ε` | $\{\epsilon\}$ | Sí | $FOLLOW(\texttt{<programa>'}) = \{\$\}$ | $M[\texttt{<programa>'}, \$] = \texttt{<programa>'} \rightarrow \epsilon$ |
| `<regla> → WHEN <condicion> THEN <acciones> ;` | $FIRST(\texttt{WHEN}) = \{\texttt{WHEN}\}$ | No | $FOLLOW(\texttt{<regla>}) = \{\$\}$ | $M[\texttt{<regla>}, \texttt{WHEN}] = \texttt{<regla>} \rightarrow \texttt{WHEN <condicion> THEN <acciones> ;}$ |
| `<condicion> → <comparacion> <condicion_tail>` | $FIRST(\texttt{<comparacion>}) = \{\texttt{NOT}, \texttt{ID}, \texttt{NUM}, \texttt{TRUE}, \texttt{FALSE}\}$ | No | $FOLLOW(\texttt{<condicion>}) = \{\texttt{THEN}\}$ | $M[\texttt{<condicion>}, \texttt{NOT}], M[\texttt{<condicion>}, \texttt{ID}], M[\texttt{<condicion>}, \texttt{NUM}], M[\texttt{<condicion>}, \texttt{TRUE}], M[\texttt{<condicion>}, \texttt{FALSE}]$ |
| `<condicion_tail> → AND <comparacion> <condicion_tail>` | $\{\texttt{AND}\}$ | No | $FOLLOW(\texttt{<condicion_tail>}) = \{\texttt{THEN}\}$ | $M[\texttt{<condicion_tail>}, \texttt{AND}] = \texttt{<condicion_tail>} \rightarrow \texttt{AND <comparacion> <condicion_tail>}$ |
| `<condicion_tail> → OR <comparacion> <condicion_tail>` | $\{\texttt{OR}\}$ | No | $FOLLOW(\texttt{<condicion_tail>}) = \{\texttt{THEN}\}$ | $M[\texttt{<condicion_tail>}, \texttt{OR}] = \texttt{<condicion_tail>} \rightarrow \texttt{OR <comparacion> <condicion_tail>}$ |
| `<condicion_tail> → ε` | $\{\epsilon\}$ | Sí | $FOLLOW(\texttt{<condicion_tail>}) = \{\texttt{THEN}\}$ | $M[\texttt{<condicion_tail>}, \texttt{THEN}] = \texttt{<condicion_tail>} \rightarrow \epsilon$ |
| `<comparacion> → NOT <comparacion>` | $\{\texttt{NOT}\}$ | No | $FOLLOW(\texttt{<comparacion>}) = \{\texttt{THEN}, \texttt{AND}, \texttt{OR}\}$ | $M[\texttt{<comparacion>}, \texttt{NOT}] = \texttt{<comparacion>} \rightarrow \texttt{NOT <comparacion>}$ |
| `<comparacion> → <factor_cond> <op_rel> <factor_cond>` | $FIRST(\texttt{<factor_cond>}) = \{\texttt{ID}, \texttt{NUM}, \texttt{TRUE}, \texttt{FALSE}\}$ | No | $FOLLOW(\texttt{<comparacion>}) = \{\texttt{THEN}, \texttt{AND}, \texttt{OR}\}$ | $M[\texttt{<comparacion>}, \texttt{ID}], M[\texttt{<comparacion>}, \texttt{NUM}], M[\texttt{<comparacion>}, \texttt{TRUE}], M[\texttt{<comparacion>}, \texttt{FALSE}]$ |
| `<factor_cond> → ID \| NUM \| TRUE \| FALSE` | Cada uno | No | $FOLLOW(\texttt{<factor_cond>}) = \{>,<,>=,<=,==,!=,\texttt{THEN},\texttt{AND},\texttt{OR}\}$ | Corresponden a sus columnas |
| `<op_rel> → > \| < \| >= \| <= \| == \| !=` | Cada uno | No | $FOLLOW(\texttt{<op_rel>}) = \{\texttt{ID},\texttt{NUM},\texttt{TRUE},\texttt{FALSE}\}$ | Corresponden a sus columnas |
| `<acciones> → <accion> <acciones_tail>` | $FIRST(\texttt{<accion>}) = \{\texttt{ID}\}$ | No | $FOLLOW(\texttt{<acciones>}) = \{;\}$ | $M[\texttt{<acciones>}, \texttt{ID}] = \texttt{<acciones>} \rightarrow \texttt{<accion> <acciones_tail>}$ |
| `<acciones_tail> → , <accion> <acciones_tail>` | $\{,\}$ | No | $FOLLOW(\texttt{<acciones_tail>}) = \{;\}$ | $M[\texttt{<acciones_tail>}, ,] = \texttt{<acciones_tail>} \rightarrow , \texttt{<accion> <acciones_tail>}$ |
| `<acciones_tail> → ε` | $\{\epsilon\}$ | Sí | $FOLLOW(\texttt{<acciones_tail>}) = \{;\}$ | $M[\texttt{<acciones_tail>}, ;] = \texttt{<acciones_tail>} \rightarrow \epsilon$ |
| `<accion> → ID` | $\{\texttt{ID}\}$ | No | $FOLLOW(\texttt{<accion>}) = \{,, ;\}$ | $M[\texttt{<accion>}, \texttt{ID}] = \texttt{<accion>} \rightarrow \texttt{ID}$ |

## F10. Verificación de ausencia de conflictos o justificación de solución

### Verificación celda por celda
| Combinación (NT, Terminal) | Producción(es) | ¿Conflicto? (Sí/No) | Observación |
|---|---|---|---|
| `<programa>, WHEN` | `<programa> → <regla> <programa>'` | No | Única producción. |
| `<programa>, $` | (vacía) | No | Sin producción. |
| `<programa>', WHEN` | `<programa>' → <regla> <programa>'` | No | Única producción. |
| `<programa>', $` | `<programa>' → ε` | No | Única producción (gracias a FOLLOW). |
| `<regla>, WHEN` | `<regla> → WHEN <condicion> THEN <acciones> ;` | No | Única producción. |
| `<condicion>, NOT/ID/NUM/TRUE/FALSE` | `<condicion> → <comparacion> <condicion_tail>` | No | Única producción por FIRST. |
| `<condicion_tail>, AND` | `<condicion_tail> → AND <comparacion> <condicion_tail>` | No | Única producción. |
| `<condicion_tail>, OR` | `<condicion_tail> → OR <comparacion> <condicion_tail>` | No | Única producción. |
| `<condicion_tail>, THEN` | `<condicion_tail> → ε` | No | Única producción por FOLLOW. |
| `<comparacion>, NOT` | `<comparacion> → NOT <comparacion>` | No | Única producción. |
| `<comparacion>, ID/NUM/TRUE/FALSE` | `<comparacion> → <factor_cond> <op_rel> <factor_cond>` | No | Única producción. |
| `<factor_cond>, ID/NUM/TRUE/FALSE` | Correspondiente a cada caso | No | Única producción por FIRST. |
| `<op_rel>, >/<//==/!=/<=/>=` | Correspondiente a cada caso | No | Única producción por FIRST. |
| `<acciones>, ID` | `<acciones> → <accion> <acciones_tail>` | No | Única producción. |
| `<acciones_tail>, ,` | `<acciones_tail> → , <accion> <acciones_tail>` | No | Única producción. |
| `<acciones_tail>, ;` | `<acciones_tail> → ε` | No | Única producción por FOLLOW. |
| `<accion>, ID` | `<accion> → ID` | No | Única producción. |

### Resultado de la verificación
- **¿Es LL(1)?** SÍ
- **Total de celdas con conflicto:** 0
- **Total de celdas vacías:** Las correspondientes a combinaciones no derivables (comportamiento correcto para LL(1))

### Si hay conflictos (justificación obligatoria)
Inicialmente se detectó un **conflicto FIRST/FIRST** entre `<programa> → <regla> <programa>` y `<programa> → <regla>` ya que ambas producían $FIRST = \{\texttt{WHEN}\}$ y afectaban a $FOLLOW(\texttt{<programa>}) = \{\$\}$.

| Celda en conflicto | Producciones en conflicto | FIRST/FOLLOW involucrados | Causa (ambigüedad / falta factorización / recursión izquierda) | Solución aplicada | ¿Resuelto tras corrección? |
|---|---|---|---|---|---|
| `<programa>, WHEN` | `<programa> → <regla> <programa>` / `<programa> → <regla>` | $FIRST(\texttt{<regla>}) = \{\texttt{WHEN}\}$, $FOLLOW(\texttt{<programa>}) = \{\$\}$ | Falta factorización / recursión por la derecha mal factorizada | Se aplicó factorización por la izquierda creando `<programa>'` con producciones `<programa>' → <regla> <programa>' \| ε`. Gramática resultante: `<programa> → <regla> <programa>'`. | SÍ |

### Conclusión F10
La gramática final tras aplicar factorización por la izquierda (eliminando el conflicto FIRST/FIRST en `<programa>`) es **LL(1)**. Todas las celdas de la tabla predictiva tienen 0 o 1 producción. Se ha integrado correctamente la extensión creativa (operador `NOT` y múltiples acciones con `,`) manteniendo la propiedad LL(1). La gramática está lista para ser entregada a Marcelo Matamala para la implementación del parser por descenso recursivo.
