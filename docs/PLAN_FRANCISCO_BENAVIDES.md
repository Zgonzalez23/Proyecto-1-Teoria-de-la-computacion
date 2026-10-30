# PLAN COMPLETO - FRANCISCO BENAVIDES (F1 - F10)

**Responsable:** Francisco Benavides  
**Fase:** Diseño Teórico - DSL, GLC, FIRST/FOLLOW, Tabla LL(1)  
**Fechas:** Días 1-3 según planificación  
**Integración:** Debe entregar insumos a Marcelo (tokens) y recibir/coordinar con Martín (extensión)

## Contexto del Proyecto

- **Dominio:** IoT / Smart Home (sugerido)
- **Extensión creativa:** NOT y Múltiples acciones (propuesta por Martín T1)
- **Parser objetivo:** LL(1) por descenso recursivo
- **Lexer provisto:** `analizador_lexico1.ipynb` (adaptable por Marcelo)

## Tareas Asignadas

### FASE 1: DEFINICIÓN DEL DSL (Día 1)

#### F1. Definir nombre, dominio (IoT/Smart Home) y propósito del lenguaje
**Objetivo:** Definir formalmente el DSL.

**Subtareas:**
- [ ] Elegir un nombre único para el lenguaje (ej: `SmartHomeDSL`, `IoTRules`, `CasaLang`)
- [ ] Justificar el dominio IoT/Smart Home
- [ ] Definir propósito concreto: ¿Qué problema resuelve? ¿Qué reglas permite expresar?
- [ ] Delimitar alcance (qué SÍ y qué NO hará el lenguaje)

**Entregable:** Sección en `docs/01_definicion_dsl.md` - F1

**Posibles errores y prevención:**
- **Error:** Dominio muy ambiguo o complejo → **Solución:** Limitar a sentencias `WHEN ... THEN ... ;` con condiciones y acciones
- **Error:** Propósito vago → **Solución:** Ser concreto: "DSL para definir reglas de automatización en casa inteligente"

---

#### F2. Listar alfabeto, tokens, 4+ palabras reservadas e identificadores
**Objetivo:** Especificación léxica completa.

**Subtareas:**
- [ ] Definir alfabeto (letras, dígitos, espacios, símbolos)
- [ ] Listar **mínimo 4 palabras reservadas**. El lexer ya tiene: `WHEN, THEN, AND, OR, NOT, TRUE, FALSE`
- [ ] Definir regla para identificadores: `[A-Za-z_][A-Za-z0-9_]*`
- [ ] Definir números: `[0-9]+`
- [ ] Definir operadores relacionales: `>, <, >=, <=, ==, !=`
- [ ] Definir separadores/símbolos: `;`, `,` (para múltiples acciones - extensión), `(`, `)` (posible)
- [ ] Crear tabla completa de tokens

**Entregable:** Sección en `docs/01_definicion_dsl.md` - F2 + **ENTREGAR A MARCELO (H-01)**

**Importante:** 
- Debes entregar a Marcelo la **lista final de tokens y expresiones regulares exactas** el **Día 1 (Tarde)** para que adapte el lexer
- El lexer provisto ya tiene la base. Coordínate con Marcelo para asegurar compatibilidad

**Posibles errores y prevención:**
- **Error:** Confundir identificadores con palabras reservadas → **Solución:** Especificar que palabras reservadas tienen mayor prioridad
- **Error:** Olvidar separadores como `;` o `,` → **Solución:** Incluir explícitamente en tabla de tokens

---

#### F3. Redactar 5 ejemplos válidos y 5 inválidos del mini-lenguaje
**Objetivo:** Ejemplificar el lenguaje incluyendo la extensión.

**Subtareas:**
- [ ] Crear **5 ejemplos válidos** que cubran:
  1. Regla básica: `WHEN temperatura > 28 THEN encender_ventilador;`
  2. Con operador lógico AND/OR
  3. Con NOT (extensión): `WHEN NOT movimiento == TRUE THEN apagar_luces;`
  4. Con múltiples acciones (extensión): `WHEN temperatura > 28 THEN encender_ventilador, abrir_ventana;`
  5. Combinando extensión: `WHEN NOT alarma == TRUE THEN desactivar_sirena, enviar_notificacion;`
- [ ] Crear **5 ejemplos inválidos** con errores SINTÁCTICOS (no solo léxicos):
  1. Falta condición después de NOT: `WHEN NOT THEN encender_luces;`
  2. Falta acción: `WHEN temperatura > 28 THEN ;`
  3. Coma final sin acción: `WHEN temperatura > 28 THEN encender_ventilador,;`
  4. Falta coma entre acciones: `WHEN temperatura > 28 THEN encender_ventilador abrir_ventana;`
  5. Estructura incorrecta: `WHEN temperatura > 28 encender_ventilador;` (falta THEN)

**Entregable:** Sección en `docs/01_definicion_dsl.md` - F3

**Posibles errores y prevención:**
- **Error:** Ejemplos inválidos solo con tokens desconocidos → **Solución:** Crear con tokens VÁLIDOS pero orden/sintaxis incorrecta
- **Error:** Ejemplos muy complejos para la GLC inicial → **Solución:** Mantener coherentes con lo que podrás modelar

---

### FASE 2: GRAMÁTICA LIBRE DE CONTEXTO (Día 2)

#### F4. Escribir la GLC inicial (símbolo inicial, no terminales, terminales)
**Objetivo:** Construir GLC desde ejemplos válidos.

**Subtareas:**
- [ ] Identificar **Símbolo inicial** S (ej: `<programa>` o `<reglas>`)
- [ ] Listar **terminales** (palabras reservadas, ID, NUM, OP_REL, `;`, `,`, `TRUE`, `FALSE`, `$`)
- [ ] Listar **no terminales** (todos los símbolos entre <>)
- [ ] Escribir **producciones** basadas en ejemplos válidos
- [ ] **Derivar al menos 1 ejemplo válido** a mano para verificar
- [ ] Coordinar con Martín (T1) sobre extensión - **RECIBIR PROPUESTA DÍA 1 NOCHE (H-02)**

**Sugerencia de estructura inicial (orientativa):**
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

**Entregable:** Sección en `docs/02_glc.md` - F4

**Posibles errores y prevención:**
- **Error:** Recursión izquierda desde inicio → **Solución:** Revisar todas las producciones
- **Error:** GLC muy compleja → **Solución:** Empezar simple, agregar extensión después
- **Error:** No deriva ejemplos válidos → **Solución:** Verificar con derivación manual

---

#### F5. Analizar e identificar recursión izquierda, aplicando eliminación
**Objetivo:** Eliminar recursión izquierda (directa e indirecta).

**Subtareas:**
- [ ] Revisar todas las producciones buscando recursión izquierda
- [ ] Identificar recursión directa: `A → A α | β`
- [ ] Identificar recursión indirecta si existe
- [ ] Aplicar transformación: `A → β A'`, `A' → α A' | ε`
- [ ] Mostrar **ANTES/DESPUÉS** claramente
- [ ] Verificar equivalencia con ejemplo

**Fórmula obligatoria a usar:**
$$
A \rightarrow A\alpha \mid \beta \implies \begin{cases}
A \rightarrow \beta A'\\
A' \rightarrow \alpha A' \mid \epsilon
\end{cases}
$$

**Entregable:** Sección en `docs/02_glc.md` - F5

**Posibles errores y prevención:**
- **Error:** Crear NT nuevos incorrectamente → **Solución:** Seguir fórmula estrictamente
- **Error:** Olvidar recursión indirecta → **Solución:** Verificar todas las producciones

---

#### F6. Analizar e identificar factorización izquierda y ambigüedades
**Objetivo:** Factorizar y resolver ambigüedades para lograr LL(1).

**Subtareas:**
- [ ] Buscar prefijos comunes: `A → α β1 | α β2 | ...`
- [ ] Factorizar: `A → α A'`, `A' → β1 | β2 | ...`
- [ ] Revisar ambigüedad *dangling else* si aplica (aunque con THEN es menos común)
- [ ] Considerar precedencia/agrupación
- [ ] Integrar extensión correctamente (NOT como prefijo, múltiples acciones)
- [ ] Generar **GLC FINAL** lista para FIRST/FOLLOW

**Entregable:** Sección en `docs/02_glc.md` - F6 + **ENTREGAR GLC LIMPIA A MARCELO (H-03)** Día 2 (Noche)

**Posibles errores y prevención:**
- **Error:** Factorización incompleta → **Solución:** Revisar todas las producciones con mismo lado izquierdo
- **Error:** Solución crea nueva ambigüedad → **Solución:** Verificar con ejemplos

---

### FASE 3: FIRST Y FOLLOW (Día 3)

#### F7. Calcular conjuntos FIRST para todos los no terminales de la GLC
**Objetivo:** Calcular FIRST correctamente.

**Subtareas:**
- [ ] Calcular FIRST para cada terminal: `FIRST(a) = {a}`
- [ ] Para producciones con ε: añadir ε
- [ ] Para concatenaciones `Y1 Y2 ... Yk`: aplicar regla correctamente
- [ ] Mostrar **cálculo paso a paso** por no terminal
- [ ] Crear tabla resumen

**Reglas a seguir:**
1. Si $X \in T$, $FIRST(X)=\{X\}$
2. Si $X \in NT$ y $X \rightarrow \epsilon \in P$, $\epsilon \in FIRST(X)$
3. Si $X \rightarrow Y_1...Y_k$, añadir $FIRST(Y_i)\setminus\{\epsilon\}$ si todos $Y_1..Y_{i-1}$ derivan ε

**Entregable:** Sección en `docs/03_first_follow.md` - F7

---

#### F8. Calcular conjuntos FOLLOW para todos los no terminales de la GLC
**Objetivo:** Calcular FOLLOW correctamente.

**Subtareas:**
- [ ] **SIEMPRE** iniciar: $FOLLOW(S) = \{\$\}$ donde S es símbolo inicial
- [ ] Aplicar regla 2: si $A \rightarrow \alpha B \beta$, añadir $FIRST(\beta)\setminus\{\epsilon\}$ a $FOLLOW(B)$
- [ ] Aplicar regla 3: si $B$ está al final o $\epsilon \in FIRST(\beta)$, añadir $FOLLOW(A)$ a $FOLLOW(B)$
- [ ] **Iterar hasta punto fijo** (puede tomar 2-3 iteraciones)
- [ ] Mostrar iteraciones
- [ ] Crear tabla resumen

**Entregable:** Sección en `docs/03_first_follow.md` - F8

**Posibles errores y prevención:**
- **Error:** Olvidar $ en FOLLOW(S) → **Solución:** Regla 1 obligatoria
- **Error:** No iterar hasta punto fijo → **Solución:** Repetir hasta que no cambien los conjuntos

---

### FASE 4: TABLA LL(1) Y VERIFICACIÓN (Día 3)

#### F9. Construir la Tabla Predictiva LL(1) basada en FIRST/FOLLOW
**Objetivo:** Construir tabla M[A,a].

**Subtareas:**
- [ ] Para cada producción $A \rightarrow \alpha$:
  - Para todo $a \in FIRST(\alpha)$, $a \neq \epsilon$: $M[A,a] = A \rightarrow \alpha$
  - Si $\epsilon \in FIRST(\alpha)$: para todo $b \in FOLLOW(A)$: $M[A,b] = A \rightarrow \alpha$
- [ ] Incluir todas las columnas (terminales + $)
- [ ] Formatear tabla en Markdown
- [ ] Calcular por producción (mostrar en tabla)
- [ ] **ENTREGAR TABLA A MARCELO (H-04)** Día 3 (Tarde)

**Entregable:** Sección en `docs/04_tabla_ll1.md` - F9

---

#### F10. Verificar ausencia de conflictos o justificar solución de colisiones
**Objetivo:** Verificar que sea LL(1).

**Subtareas:**
- [ ] Revisar **CELDA POR CELDA** toda la tabla
- [ ] Verificar que NO haya entradas múltiples
- [ ] Si hay conflicto: identificarlo (FIRST/FIRST o FIRST/FOLLOW)
- [ ] Si hay conflicto: **VOLVER A F5/F6** - factorizar o eliminar recursión
- [ ] Recalcular FIRST/FOLLOW si modificaste gramática
- [ ] Reconstruir tabla
- [ ] Documentar todo el proceso si hubo correcciones
- [ ] Concluir: ¿Es LL(1)? SÍ/NO con justificación

**Criterio de aprobación:** Gramática LL(1) = **sin celdas con múltiples producciones**

**Entregable:** Sección en `docs/04_tabla_ll1.md` - F10

**Posibles errores y prevención:**
- **Error:** Decir "es LL(1)" con conflictos → **Solución:** Verificación estricta celda por celda
- **Error:** No corregir conflictos → **Solución:** Obligatorio refactorizar hasta eliminar conflictos

---

## COORDINACIÓN CON EL EQUIPO

### Hand-offs que debes cumplir

| Handoff | A quién | Cuándo | Insumo | Importancia |
|---|---|---|---|---|
| **H-01** | Marcelo (M1) | Día 1 (Tarde) | Lista final de tokens y expresiones regulares exactas | **CRÍTICO** - Sin esto no puede hacer lexer |
| **H-02** | Recibes de Martín (T1) | Día 1 (Noche) | Propuesta formal de Extensión Creativa (NOT + múltiples acciones) | **CRÍTICO** - Debes integrarla a GLC |
| **H-03** | Marcelo (M2) | Día 2 (Noche) | GLC limpia, factorizada y sin recursión izquierda | **CRÍTICO** - Sin esto no puede hacer parser por descenso recursivo |
| **H-04** | Marcelo (M4) | Día 3 (Tarde) | Tabla Predictiva LL(1) completada | **CRÍTICO** - Necesaria para implementar lógica con if-elif según tabla |

### Colaboración
- **Con Martín (T2):** Coordinar integración de extensión en GLC/FIRST/FOLLOW (Día 3)
- **Con Marcelo:** Revisión cruzada constante para asegurar coherencia entre teoría y código
- **Con todo el equipo (G1):** Revisión cruzada final - **verificar que código coincide 100% con GLC**

---

## CHECKLIST FINAL

### Documentación completa
- [ ] `docs/01_definicion_dsl.md` - F1, F2, F3 completos
- [ ] `docs/02_glc.md` - F4 (con derivación), F5 (antes/después), F6 (factorización + GLC final)
- [ ] `docs/03_first_follow.md` - F7 y F8 con cálculos paso a paso e iteraciones
- [ ] `docs/04_tabla_ll1.md` - F9 (tabla completa) y F10 (verificación celda por celda)

### Entregables críticos
- [ ] Tokens entregados a Marcelo (H-01)
- [ ] GLC integrada con extensión entregada a Marcelo (H-03)
- [ ] Tabla LL(1) entregada a Marcelo (H-04)
- [ ] Todo documentado para informe técnico

### Validación
- [ ] Al menos 1 derivación manual exitosa
- [ ] Gramática sin recursión izquierda
- [ ] Gramática factorizada
- [ ] FIRST y FOLLOW calculados correctamente
- [ ] Tabla LL(1) SIN CONFLICTOS (verificado celda por celda)
- [ ] Coherencia con ejemplos válidos/invalidos
- [ ] Extensión (NOT + múltiples acciones) integrada

---

## RECOMENDACIONES

1. **Orden estricto:** F1-F3 → F4 → F5-F6 (con extensión) → F7-F8 → F9-F10
2. **Documenta TODO:** Muestra cálculos paso a paso, no solo resultados finales
3. **Verifica constantemente:** Cada transformación debe mantener el lenguaje de ejemplos válidos
4. **Coordínate temprano:** No esperes último momento para hand-offs - son críticos
5. **Sé estricto con LL(1):** Si hay conflictos, DEBES corregirlos. No es aceptable dejar tabla con celdas múltiples
6. **Trabaja con equipo:** La revisión cruzada (G1) es obligatoria - código debe coincidir 100% con GLC

**Recuerda:** Según rúbrica, "La falta de correspondencia entre informe, gramática y código afecta el criterio respectivo". Tu trabajo teórico debe coincidir EXACTAMENTE con lo que implemente Marcelo.
