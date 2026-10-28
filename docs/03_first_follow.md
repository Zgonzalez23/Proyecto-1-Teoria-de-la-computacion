# F7 - F8: Conjuntos FIRST y FOLLOW

## F7. Conjuntos FIRST

**Reglas para calcular FIRST:**
1. Si $X$ es un terminal, $FIRST(X) = \{X\}$.
2. Si $X$ es un no terminal y $X \rightarrow \epsilon$ es una producción, añadir $\epsilon$ a $FIRST(X)$.
3. Si $X \rightarrow Y_1 Y_2 ... Y_k$ es una producción:
   - Añadir $FIRST(Y_1) \setminus \{\epsilon\}$ a $FIRST(X)$.
   - Si $\epsilon \in FIRST(Y_1)$, añadir $FIRST(Y_2) \setminus \{\epsilon\}$, etc.
   - Si $\epsilon \in FIRST(Y_1) \cap ... \cap FIRST(Y_k)$, añadir $\epsilon$ a $FIRST(X)$.

### Cálculo paso a paso

| No Terminal | Producciones | Cálculo | FIRST(X) |
|---|---|---|---|
| `<factor_cond>` | `<factor_cond> → ID \| NUM \| TRUE \| FALSE` | Son terminales directos. | $FIRST(\texttt{<factor_cond>}) = \{\texttt{ID}, \texttt{NUM}, \texttt{TRUE}, \texttt{FALSE}\}$ |
| `<op_rel>` | `<op_rel> → > \| < \| >= \| <= \| == \| !=` | Son terminales directos. | $FIRST(\texttt{<op_rel>}) = \{>, <, >=, <=, ==, !=\}$ |
| `<accion>` | `<accion> → ID` | Terminal directo. | $FIRST(\texttt{<accion>}) = \{\texttt{ID}\}$ |
| `<comparacion>` | `<comparacion> → NOT <comparacion> \| <factor_cond> <op_rel> <factor_cond>` | Primera producción empieza con `NOT`. Segunda empieza con $FIRST(\texttt{<factor_cond>})$. | $FIRST(\texttt{<comparacion>}) = \{\texttt{NOT}, \texttt{ID}, \texttt{NUM}, \texttt{TRUE}, \texttt{FALSE}\}$ |
| `<condicion_tail>` | `<condicion_tail> → AND <comparacion> <condicion_tail> \| OR <comparacion> <condicion_tail> \| ε` | Tiene producción con ε. Además empieza con `AND`, `OR`. | $FIRST(\texttt{<condicion_tail>}) = \{\texttt{AND}, \texttt{OR}, \epsilon\}$ |
| `<condicion>` | `<condicion> → <comparacion> <condicion_tail>` | Empieza con $FIRST(\texttt{<comparacion>})$ ya que $\epsilon \notin FIRST(\texttt{<comparacion>})$. | $FIRST(\texttt{<condicion>}) = \{\texttt{NOT}, \texttt{ID}, \texttt{NUM}, \texttt{TRUE}, \texttt{FALSE}\}$ |
| `<acciones_tail>` | `<acciones_tail> → , <accion> <acciones_tail> \| ε` | Tiene ε y empieza con `,`. | $FIRST(\texttt{<acciones_tail>}) = \{,, \epsilon\}$ |
| `<acciones>` | `<acciones> → <accion> <acciones_tail>` | Empieza con $FIRST(\texttt{<accion>}) = \{\texttt{ID}\}$, $\epsilon \notin FIRST(\texttt{<accion>})$. | $FIRST(\texttt{<acciones>}) = \{\texttt{ID}\}$ |
| `<regla>` | `<regla> → WHEN <condicion> THEN <acciones> ;` | Empieza con terminal `WHEN`. | $FIRST(\texttt{<regla>}) = \{\texttt{WHEN}\}$ |
| `<programa>` | `<programa> → <regla> <programa>'` | Empieza con $FIRST(\texttt{<regla>}) = \{\texttt{WHEN}\}$. | $FIRST(\texttt{<programa>}) = \{\texttt{WHEN}\}$ |
| `<programa'>` | `<programa>' → <regla> <programa>' \| ε` | Empieza con $FIRST(\texttt{<regla>}) = \{\texttt{WHEN}\}$ y tiene ε. | $FIRST(\texttt{<programa>'}) = \{\texttt{WHEN}, \epsilon\}$ |

**Tabla resumen FIRST:**
```
FIRST(<factor_cond>)   = {ID, NUM, TRUE, FALSE}
FIRST(<op_rel>)        = {>, <, >=, <=, ==, !=}
FIRST(<accion>)        = {ID}
FIRST(<comparacion>)   = {NOT, ID, NUM, TRUE, FALSE}
FIRST(<condicion_tail>)= {AND, OR, ε}
FIRST(<condicion>)     = {NOT, ID, NUM, TRUE, FALSE}
FIRST(<acciones_tail>) = {,, ε}
FIRST(<acciones>)      = {ID}
FIRST(<regla>)         = {WHEN}
FIRST(<programa>)      = {WHEN}
FIRST(<programa>')     = {WHEN, ε}
```

## F8. Conjuntos FOLLOW

**Reglas para calcular FOLLOW:**
1. Para el símbolo inicial $S$, añadir $\$$ a $FOLLOW(S)$.
2. Si $A \rightarrow \alpha B \beta$ es una producción, añadir $FIRST(\beta) \setminus \{\epsilon\}$ a $FOLLOW(B)$.
3. Si $A \rightarrow \alpha B$ es una producción o $A \rightarrow \alpha B \beta$ y $\epsilon \in FIRST(\beta)$, añadir $FOLLOW(A)$ a $FOLLOW(B)$.

**Importante:** Calcular iterativamente hasta alcanzar punto fijo.

### Cálculo paso a paso (mostrar iteraciones)

**Iteración 1:**

| No Terminal | Aplicación de reglas | FOLLOW(X) |
|---|---|---|
| `<programa>` | Regla 1 (símbolo inicial): $FOLLOW(\texttt{<programa>}) = \{\$\}$. | $FOLLOW(\texttt{<programa>}) = \{\$\}$ |
| `<programa>'` | En `<programa> → <regla> <programa>'$, `β = <programa>'$, $\epsilon \in FIRST(\texttt{<programa>'})$ por lo que añadimos $FOLLOW(\texttt{<programa>}) = \{\$\}$ a $FOLLOW(\texttt{<programa>'})$. En `<programa>' → <regla> <programa>'$, al tener `<programa>'$ al final, añadimos $FOLLOW(\texttt{<programa>'})$. | $FOLLOW(\texttt{<programa>'}) = \{\$\}$ |
| `<regla>` | En `<programa> → <regla> <programa>'$, `β = <programa>'$, $\epsilon \in FIRST(\texttt{<programa>'})$ por lo que añadimos $FOLLOW(\texttt{<programa>}) = \{\$\}$ a $FOLLOW(\texttt{<regla>})$. En `<programa>' → <regla> <programa>'$, `β = <programa>'$, $\epsilon \in FIRST(\texttt{<programa>'})$ por lo que añadimos $FOLLOW(\texttt{<programa>'}) = \{\$\}$ a $FOLLOW(\texttt{<regla>})$. | $FOLLOW(\texttt{<regla>}) = \{\$\}$ |
| `<condicion>` | En `<regla> → WHEN <condicion> THEN <acciones> ;`, `β = THEN <acciones> ;`, $FIRST(THEN) = \{\texttt{THEN}\}$, añadimos a $FOLLOW(\texttt{<condicion>})$. | $FOLLOW(\texttt{<condicion>}) = \{\texttt{THEN}\}$ |
| `<condicion_tail>` | En `<condicion> → <comparacion> <condicion_tail>`, `β = ε`, aplicamos regla 3: añadimos $FOLLOW(\texttt{<condicion>}) = \{\texttt{THEN}\}$ a $FOLLOW(\texttt{<condicion_tail>})$. También en sus propias producciones al final con ε se aplicará regla 3. | $FOLLOW(\texttt{<condicion_tail>}) = \{\texttt{THEN}\}$ |
| `<comparacion>` | En `<condicion> → <comparacion> <condicion_tail>`, `β = <condicion_tail>`, $\epsilon \in FIRST(\texttt{<condicion_tail>})$ por lo que añadimos $FOLLOW(\texttt{<condicion>}) = \{\texttt{THEN}\}$ a $FOLLOW(\texttt{<comparacion>})$. En `<condicion_tail> → AND <comparacion> <condicion_tail>$ y `OR <comparacion> <condicion_tail>`, `β = <condicion_tail>`, $\epsilon \in FIRST(\texttt{<condicion_tail>})$ por lo que añadimos $FOLLOW(\texttt{<condicion_tail>}) = \{\texttt{THEN}\}$ a $FOLLOW(\texttt{<comparacion>})$. En `<comparacion> → NOT <comparacion>`, `<comparacion>` está al final, añadimos $FOLLOW(\texttt{<comparacion>})$ a sí mismo (recursivo). | $FOLLOW(\texttt{<comparacion>}) = \{\texttt{THEN}, \texttt{AND}, \texttt{OR}\}$ |
| `<factor_cond>` | En `<comparacion> → <factor_cond> <op_rel> <factor_cond>`, para el primer `<factor_cond>` con `β = <op_rel> <factor_cond>`, $FIRST(<op_rel>)=\{>,<,>=,<=,==,!=\}$ no contiene ε, añadimos $FIRST(<op_rel>)\setminus\{\epsilon\}$ a $FOLLOW(\texttt{<factor_cond>})$. Para el segundo `<factor_cond>` al final, añadimos $FOLLOW(\texttt{<comparacion>}) = \{\texttt{THEN}, \texttt{AND}, \texttt{OR}\}$ a $FOLLOW(\texttt{<factor_cond>})$. | $FOLLOW(\texttt{<factor_cond>}) = \{>, <, >=, <=, ==, !=, \texttt{THEN}, \texttt{AND}, \texttt{OR}\}$ |
| `<op_rel>` | En `<comparacion> → <factor_cond> <op_rel> <factor_cond>`, `β = <factor_cond>`, $FIRST(\texttt{<factor_cond>}) = \{\texttt{ID},\texttt{NUM},\texttt{TRUE},\texttt{FALSE}\}$ no contiene ε, añadimos a $FOLLOW(\texttt{<op_rel>})$. | $FOLLOW(\texttt{<op_rel>}) = \{\texttt{ID}, \texttt{NUM}, \texttt{TRUE}, \texttt{FALSE}\}$ |
| `<acciones>` | En `<regla> → WHEN <condicion> THEN <acciones> ;`, `β = ;`, $FIRST(;) = \{;\}$, añadimos a $FOLLOW(\texttt{<acciones>})$. | $FOLLOW(\texttt{<acciones>}) = \{;\}$ |
| `<acciones_tail>` | En `<acciones> → <accion> <acciones_tail>`, `β = ε`, añadimos $FOLLOW(\texttt{<acciones>}) = \{;\}$ a $FOLLOW(\texttt{<acciones_tail>})$. En sus propias producciones al final con ε. | $FOLLOW(\texttt{<acciones_tail>}) = \{;\}$ |
| `<accion>` | En `<acciones> → <accion> <acciones_tail>`, `β = <acciones_tail>`, $\epsilon \in FIRST(\texttt{<acciones_tail>})$ por lo que añadimos $FOLLOW(\texttt{<acciones>}) = \{;\}$ a $FOLLOW(\texttt{<accion>})$. En `<acciones_tail> → , <accion> <acciones_tail>`, `β = <acciones_tail>`, $\epsilon \in FIRST(\texttt{<acciones_tail>})$ por lo que añadimos $FOLLOW(\texttt{<acciones_tail>}) = \{;\}$ a $FOLLOW(\texttt{<accion>})$. | $FOLLOW(\texttt{<accion>}) = \{,, ;\}$ |

**Iteración 2 (verificación - sin cambios):** Los conjuntos ya alcanzaron punto fijo.

**Tabla resumen FOLLOW:**
```
FOLLOW(<programa>)      = {$}
FOLLOW(<programa>')     = {$}
FOLLOW(<regla>)         = {$}
FOLLOW(<condicion>)     = {THEN}
FOLLOW(<condicion_tail>)= {THEN}
FOLLOW(<comparacion>)   = {THEN, AND, OR}
FOLLOW(<factor_cond>)   = {>, <, >=, <=, ==, !=, THEN, AND, OR}
FOLLOW(<op_rel>)        = {ID, NUM, TRUE, FALSE}
FOLLOW(<acciones>)      = {;}
FOLLOW(<acciones_tail>) = {;}
FOLLOW(<accion>)        = {,, ;}
```

**Verificación cruzada:** Se ha añadido `$` a $FOLLOW(\texttt{<programa>})$ (símbolo inicial). Se han aplicado correctamente las reglas 2 y 3 en todas las producciones. Los conjuntos son estables tras iteración 2.
