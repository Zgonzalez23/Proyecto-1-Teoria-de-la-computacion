"""
Runner automático de pruebas sintácticas para el DSL IoT/Smart Home (SmartHomeLang).

Incluye:
  * Lexer con palabras reservadas case-insensitive (M1).
  * Parser LL(1) por descenso recursivo guiado por tabla (M2-M5).
  * AST simple con tipo, valor e hijos, y su impresión jerárquica (M6-M7).
  * Excepciones SyntaxErrorDSL con posición y sugerencia (M8-M9).
  * Runner de casos con reporte por consola y exportación a JSON.

Uso:
  python3 test_runner.py --casos casos_prueba.json --casos casos_limite.json
  python3 test_runner.py --ast "WHEN temperatura > 28 THEN encender_ventilador;"
  python3 test_runner.py --generar-casos --casos casos_prueba.json
"""

from __future__ import annotations

import argparse
import json
import sys
from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Optional, Tuple

# ---------------------------------------------------------------------------
# 1. LEXER
# ---------------------------------------------------------------------------

PALABRAS_RESERVADAS = {
    "WHEN",
    "THEN",
    "AND",
    "OR",
    "NOT",
    "TRUE",
    "FALSE",
}

# Los operadores de 2 caracteres deben probarse antes que los de 1.
OPERADORES_RELACIONALES = {">=", "<=", "==", "!=", ">", "<"}

SIMBOLOS = {
    ";": "PUNTO_COMA",
    ",": "COMA",
}


class Token:
    __slots__ = ("tipo", "valor", "linea", "columna")

    def __init__(self, tipo: str, valor: str, linea: int, columna: int):
        self.tipo = tipo
        self.valor = valor
        self.linea = linea
        self.columna = columna

    def __repr__(self) -> str:
        return f"Token({self.tipo!r}, {self.valor!r}, L{self.linea}:C{self.columna})"


class SyntaxErrorDSL(Exception):
    """Error léxico o sintáctico con posición y sugerencia."""

    def __init__(
        self,
        mensaje: str,
        *,
        linea: Optional[int] = None,
        columna: Optional[int] = None,
        encontrado: Optional[str] = None,
        esperado: Optional[str] = None,
        sugerencia: Optional[str] = None,
    ):
        self.mensaje = mensaje
        self.linea = linea
        self.columna = columna
        self.encontrado = encontrado
        self.esperado = esperado
        self.sugerencia = sugerencia
        super().__init__(self.formatear())

    def formatear(self) -> str:
        partes = [self.mensaje]
        if self.encontrado is not None:
            partes.append(f"encontrado={self.encontrado!r}")
        if self.esperado is not None:
            partes.append(f"esperado={self.esperado!r}")
        if self.linea is not None and self.columna is not None:
            partes.append(f"posición=L{self.linea}:C{self.columna}")
        if self.sugerencia:
            partes.append(f"sugerencia: {self.sugerencia}")
        return " | ".join(partes)


class LexerError(SyntaxErrorDSL):
    """Error léxico: carácter no reconocido."""


class ParserError(SyntaxErrorDSL):
    """Error sintáctico durante el análisis LL(1)."""


def _es_inicio_id(caracter: str) -> bool:
    return caracter == "_" or (caracter.isascii() and caracter.isalpha())


def _es_parte_id(caracter: str) -> bool:
    return caracter == "_" or (caracter.isascii() and caracter.isalnum())


def tokenizar(entrada: str) -> List[Token]:
    """
    Convierte una cadena de entrada en una lista de Token.

    Reconoce:
      * Palabras reservadas sin distinguir mayúsculas/minúsculas.
      * Identificadores [A-Za-z_][A-Za-z0-9_]*
      * Números enteros [0-9]+
      * Operadores relacionales >= <= == != > <
      * Símbolos ; ,
      * Espacios en blanco (ignorados)
    """
    tokens: List[Token] = []
    i = 0
    linea = 1
    columna = 1
    n = len(entrada)

    while i < n:
        c = entrada[i]

        # Espacios en blanco
        if c in " \t\r\n":
            if c == "\n":
                linea += 1
                columna = 1
            else:
                columna += 1
            i += 1
            continue

        # Operadores relacionales de 2 caracteres
        if i + 1 < n:
            dos = entrada[i : i + 2]
            if dos in OPERADORES_RELACIONALES:
                tokens.append(Token("OP_REL", dos, linea, columna))
                i += 2
                columna += 2
                continue

        # Operadores relacionales de 1 carácter
        if c in OPERADORES_RELACIONALES:
            tokens.append(Token("OP_REL", c, linea, columna))
            i += 1
            columna += 1
            continue

        # Símbolos separadores
        if c in SIMBOLOS:
            tokens.append(Token(SIMBOLOS[c], c, linea, columna))
            i += 1
            columna += 1
            continue

        # Identificadores y palabras reservadas
        if _es_inicio_id(c):
            inicio = i
            while i < n and _es_parte_id(entrada[i]):
                i += 1
            lexema = entrada[inicio:i]
            tipo = lexema.upper() if lexema.upper() in PALABRAS_RESERVADAS else "ID"
            valor = lexema.upper() if tipo != "ID" else lexema
            tokens.append(Token(tipo, valor, linea, columna))
            columna += i - inicio
            continue

        # Números enteros
        if c.isascii() and c.isdigit():
            inicio = i
            while i < n and entrada[i].isascii() and entrada[i].isdigit():
                i += 1
            lexema = entrada[inicio:i]
            tokens.append(Token("NUM", lexema, linea, columna))
            columna += i - inicio
            continue

        raise LexerError(
            "Carácter no reconocido",
            linea=linea,
            columna=columna,
            encontrado=c,
            sugerencia="use letras, dígitos, guion bajo, operadores, ';' o ','",
        )

    tokens.append(Token("EOF", "$", linea, columna))
    return tokens


# ---------------------------------------------------------------------------
# 2. AST
# ---------------------------------------------------------------------------


@dataclass
class ASTNode:
    """Nodo simple del AST: tipo, valor opcional e hijos."""

    tipo: str
    valor: Optional[str] = None
    hijos: List["ASTNode"] = field(default_factory=list)


def ast_a_texto(nodo: ASTNode, prefijo: str = "", raiz: bool = True) -> str:
    """Devuelve una representación jerárquica legible del AST."""
    etiqueta = nodo.tipo if nodo.valor is None else f"{nodo.tipo}: {nodo.valor}"
    linea = etiqueta if raiz else f"{prefijo}|-- {etiqueta}"
    lineas = [linea]
    nuevo_prefijo = prefijo + ("    " if raiz else "|   ")
    for hijo in nodo.hijos:
        lineas.append(ast_a_texto(hijo, nuevo_prefijo, False))
    return "\n".join(lineas)


def imprimir_ast(nodo: ASTNode) -> None:
    print(ast_a_texto(nodo))


# ---------------------------------------------------------------------------
# 3. PARSER LL(1)
# ---------------------------------------------------------------------------

# Tabla LL(1) de docs/04_tabla_ll1.md, expresada sobre tipos de token.
# La clave "EOF" representa el símbolo $.
TABLA_LL1: Dict[str, Dict[str, str]] = {
    "programa": {
        "WHEN": "regla programa_prima",
    },
    "programa_prima": {
        "WHEN": "regla programa_prima",
        "EOF": "epsilon",
    },
    "regla": {
        "WHEN": "WHEN condicion THEN acciones ;",
    },
    "condicion": {
        "NOT": "comparacion condicion_tail",
        "ID": "comparacion condicion_tail",
        "NUM": "comparacion condicion_tail",
        "TRUE": "comparacion condicion_tail",
        "FALSE": "comparacion condicion_tail",
    },
    "condicion_tail": {
        "AND": "AND comparacion condicion_tail",
        "OR": "OR comparacion condicion_tail",
        "THEN": "epsilon",
    },
    "comparacion": {
        "NOT": "NOT comparacion",
        "ID": "factor_cond op_rel factor_cond",
        "NUM": "factor_cond op_rel factor_cond",
        "TRUE": "factor_cond op_rel factor_cond",
        "FALSE": "factor_cond op_rel factor_cond",
    },
    "factor_cond": {
        "ID": "ID",
        "NUM": "NUM",
        "TRUE": "TRUE",
        "FALSE": "FALSE",
    },
    "op_rel": {
        "OP_REL": "OP_REL",
    },
    "acciones": {
        "ID": "accion acciones_tail",
    },
    "acciones_tail": {
        "COMA": ", accion acciones_tail",
        "PUNTO_COMA": "epsilon",
    },
    "accion": {
        "ID": "ID",
    },
}


class Parser:
    """Parser LL(1) por descenso recursivo para SmartHomeLang."""

    def __init__(self, tokens: List[Token]):
        self.tokens = tokens
        self.pos = 0

    # Utilidades

    def peek(self) -> Token:
        if self.pos >= len(self.tokens):
            return self.tokens[-1]
        return self.tokens[self.pos]

    def avanzar(self) -> Token:
        tok = self.peek()
        self.pos += 1
        return tok

    def match(self, tipo_esperado: str) -> Token:
        """Consume el token si coincide; si no, lanza ParserError."""
        tok = self.peek()
        if tok.tipo != tipo_esperado:
            raise ParserError(
                "Token inesperado",
                linea=tok.linea,
                columna=tok.columna,
                encontrado=f"{tok.tipo} ({tok.valor})",
                esperado=tipo_esperado,
                sugerencia=f"se esperaba {tipo_esperado}",
            )
        return self.avanzar()

    def consume(self, tipo_esperado: str) -> Token:
        """Alias explícito de match."""
        return self.match(tipo_esperado)

    def produccion(self, no_terminal: str) -> str:
        """Consulta la tabla LL(1) para el lookahead actual."""
        tabla = TABLA_LL1.get(no_terminal)
        if tabla is None:
            raise ParserError(f"No existe tabla LL(1) para <{no_terminal}>")

        tok = self.peek()
        produccion = tabla.get(tok.tipo)
        if produccion is None:
            esperados = ", ".join(sorted(tabla))
            raise ParserError(
                f"No hay producción para <{no_terminal}>",
                linea=tok.linea,
                columna=tok.columna,
                encontrado=f"{tok.tipo} ({tok.valor})",
                esperado=esperados,
                sugerencia=f"según la tabla LL(1) se esperaba: {esperados}",
            )
        return produccion

    # Producciones de la GLC

    def parse_programa(self) -> ASTNode:
        """<programa> → <regla> <programa'>"""
        self.produccion("programa")
        hijos = [self.parse_regla()]
        hijos.extend(self.parse_programa_prima())
        return ASTNode("Programa", hijos=hijos)

    def parse_programa_prima(self) -> List[ASTNode]:
        """<programa'> → <regla> <programa'> | ε"""
        hijos: List[ASTNode] = []
        while self.produccion("programa_prima") != "epsilon":
            hijos.append(self.parse_regla())
        return hijos

    def parse_regla(self) -> ASTNode:
        """<regla> → WHEN <condicion> THEN <acciones> ;"""
        self.produccion("regla")
        self.match("WHEN")
        condicion = self.parse_condicion()
        self.match("THEN")
        acciones = self.parse_acciones()
        self.match("PUNTO_COMA")
        return ASTNode("Regla", hijos=[condicion, acciones])

    def parse_condicion(self) -> ASTNode:
        """<condicion> → <comparacion> <condicion_tail>"""
        self.produccion("condicion")
        primera = self.parse_comparacion()
        cola = self.parse_condicion_tail()
        return ASTNode("Condicion", hijos=[primera] + cola)

    def parse_condicion_tail(self) -> List[ASTNode]:
        """<condicion_tail> → AND <comparacion> <condicion_tail>
                            | OR <comparacion> <condicion_tail>
                            | ε"""
        hijos: List[ASTNode] = []
        while True:
            produccion = self.produccion("condicion_tail")
            if produccion == "epsilon":
                return hijos
            operador = self.peek().tipo
            self.avanzar()
            comparacion = self.parse_comparacion()
            hijos.append(ASTNode("OperadorLogico", valor=operador, hijos=[comparacion]))

    def parse_comparacion(self) -> ASTNode:
        """<comparacion> → NOT <comparacion>
                          | <factor_cond> <op_rel> <factor_cond>"""
        produccion = self.produccion("comparacion")
        if produccion == "NOT comparacion":
            self.match("NOT")
            return ASTNode("Not", hijos=[self.parse_comparacion()])

        izquierda = self.parse_factor_cond()
        operador = self.parse_op_rel()
        derecha = self.parse_factor_cond()
        return ASTNode("Comparacion", valor=operador.valor, hijos=[izquierda, derecha])

    def parse_factor_cond(self) -> ASTNode:
        """<factor_cond> → ID | NUM | TRUE | FALSE"""
        self.produccion("factor_cond")
        tok = self.avanzar()
        return ASTNode("Factor", valor=tok.valor)

    def parse_op_rel(self) -> Token:
        """<op_rel> → > | < | >= | <= | == | !="""
        self.produccion("op_rel")
        return self.match("OP_REL")

    def parse_acciones(self) -> ASTNode:
        """<acciones> → <accion> <acciones_tail>"""
        self.produccion("acciones")
        hijos = [self.parse_accion()]
        hijos.extend(self.parse_acciones_tail())
        return ASTNode("Acciones", hijos=hijos)

    def parse_acciones_tail(self) -> List[ASTNode]:
        """<acciones_tail> → , <accion> <acciones_tail> | ε"""
        hijos: List[ASTNode] = []
        while self.produccion("acciones_tail") != "epsilon":
            self.match("COMA")
            hijos.append(self.parse_accion())
        return hijos

    def parse_accion(self) -> ASTNode:
        """<accion> → ID"""
        self.produccion("accion")
        tok = self.match("ID")
        return ASTNode("Accion", valor=tok.valor)

    # Punto de entrada

    def parse(self) -> ASTNode:
        """Analiza el programa completo y devuelve su AST."""
        ast = self.parse_programa()
        tok = self.peek()
        if tok.tipo != "EOF":
            raise ParserError(
                "Tokens inesperados después del programa",
                linea=tok.linea,
                columna=tok.columna,
                encontrado=f"{tok.tipo} ({tok.valor})",
                esperado="EOF",
                sugerencia="revise si sobra un ';' o una palabra",
            )
        return ast


def parse_fn(entrada: str) -> Tuple[bool, str, Optional[ASTNode]]:
    """Analiza una entrada y devuelve (es_valido, mensaje, ast)."""
    entrada = entrada.strip()
    if not entrada:
        return False, "Entrada vacía", None

    try:
        tokens = tokenizar(entrada)
        parser = Parser(tokens)
        ast = parser.parse()
        return True, "Sintaxis válida (LL(1) por descenso recursivo)", ast
    except LexerError as e:
        return False, f"Error léxico: {e}", None
    except ParserError as e:
        return False, f"Error sintáctico: {e}", None
    except Exception as e:  # pylint: disable=broad-except
        return False, f"Error interno: {e}", None


# ---------------------------------------------------------------------------
# 4. CASOS DE PRUEBA PREDETERMINADOS
# ---------------------------------------------------------------------------

CASOS_PREDETERMINADOS: List[Dict] = [
    # CASOS VÁLIDOS (10)
    {"entrada": "WHEN temperatura > 28 THEN encender_ventilador;", "esperado": "valido", "desc": "Condición simple > (básica)"},
    {"entrada": "WHEN movimiento == TRUE THEN activar_alarma;", "esperado": "valido", "desc": "Condición booleana == TRUE"},
    {"entrada": "WHEN humedad < 40 THEN activar_humidificador;", "esperado": "valido", "desc": "Condición simple <"},
    {"entrada": "WHEN temperatura > 28 AND humedad < 40 THEN encender_ventilador;", "esperado": "valido", "desc": "Compuesta con AND"},
    {"entrada": "WHEN temperatura > 28 OR humedad > 80 THEN encender_aire;", "esperado": "valido", "desc": "Compuesta con OR"},
    {"entrada": "WHEN NOT movimiento == TRUE THEN apagar_luces;", "esperado": "valido", "desc": "NOT sobre comparación"},
    {"entrada": "WHEN NOT humedad < 40 THEN activar_deshumidificador;", "esperado": "valido", "desc": "NOT sobre <"},
    {"entrada": "WHEN temperatura > 28 THEN encender_ventilador, abrir_ventana;", "esperado": "valido", "desc": "Múltiples acciones con coma"},
    {"entrada": "WHEN NOT alarma == TRUE THEN desactivar_sirena, enviar_notificacion;", "esperado": "valido", "desc": "NOT + múltiples acciones"},
    {"entrada": "WHEN NOT movimiento == TRUE AND temperatura < 18 THEN encender_calefaccion;", "esperado": "valido", "desc": "NOT + AND compuesto"},

    # CASOS INVÁLIDOS (10)
    {"entrada": "WHEN temperatura > 28 THEN ;", "esperado": "invalido", "desc": "Falta acción después de THEN"},
    {"entrada": "WHEN NOT THEN encender_luces;", "esperado": "invalido", "desc": "Falta condición tras NOT"},
    {"entrada": "temperatura > 28 THEN encender_ventilador;", "esperado": "invalido", "desc": "Falta palabra reservada WHEN"},
    {"entrada": "WHEN temperatura > 28 THEN encender_ventilador", "esperado": "invalido", "desc": "Falta punto y coma final"},
    {"entrada": "WHEN temperatura > 28 THEN encender_ventilador,", "esperado": "invalido", "desc": "Coma final sin segunda acción"},
    {"entrada": "WHEN NOT > 28 THEN encender_luces;", "esperado": "invalido", "desc": "NOT seguido de operador relacional"},
    {"entrada": "WHEN temperatura > 28 THEN encender_ventilador abrir_ventana;", "esperado": "invalido", "desc": "Falta coma entre acciones"},
    {"entrada": "WHEN temperatura > 28 THEN 123;", "esperado": "invalido", "desc": "Acción no es identificador"},
    {"entrada": "WHEN movimiento == THEN encender_luces;", "esperado": "invalido", "desc": "Falta valor tras operador relacional"},
    {"entrada": "WHEN THEN encender_luces;", "esperado": "invalido", "desc": "Falta condición completa"},
]


# ---------------------------------------------------------------------------
# 5. RUNNER DE PRUEBAS
# ---------------------------------------------------------------------------


def cargar_casos_desde_json(ruta: str) -> List[Dict]:
    with open(ruta, "r", encoding="utf-8") as f:
        return json.load(f)


def guardar_casos_en_json(ruta: str, casos: List[Dict]) -> None:
    with open(ruta, "w", encoding="utf-8") as f:
        json.dump(casos, f, indent=2, ensure_ascii=False)


def ejecutar_caso(
    caso: Dict, parse_fn: Callable[[str], Tuple[bool, str, Any]]
) -> Dict:
    entrada = caso["entrada"]
    esperado = caso["esperado"]
    descripcion = caso.get("desc", "")

    try:
        es_valido, mensaje, ast = parse_fn(entrada)
        obtenido = "valido" if es_valido else "invalido"
        coincidio = obtenido == esperado
    except Exception as e:  # pylint: disable=broad-except
        obtenido = "invalido"
        mensaje = f"Excepción inesperada: {e}"
        coincidio = False

    return {
        "entrada": entrada,
        "descripcion": descripcion,
        "esperado": esperado,
        "obtenido": obtenido,
        "mensaje_parser": mensaje,
        "coincidio": coincidio,
    }


def run_suite(
    casos: List[Dict],
    parse_fn: Callable[[str], Tuple[bool, str, Any]] = parse_fn,
    salida_json: Optional[str] = None,
) -> Dict:
    print("=" * 80)
    print("RUNNER AUTOMÁTICO DE PRUEBAS SINTÁCTICAS - DSL SmartHomeLang")
    print("=" * 80)
    print(f"Total de casos: {len(casos)}\n")

    resultados = []
    for i, caso in enumerate(casos, start=1):
        res = ejecutar_caso(caso, parse_fn)
        resultados.append(res)

        estado = "✓ OK" if res["coincidio"] else "✗ FALLO"
        print(
            f"[{i:02d}] {estado} | Esperado: {res['esperado']:8} | "
            f"Obtenido: {res['obtenido']:8} | {res['entrada'][:65]}"
        )
        if not res["coincidio"]:
            print(f"       └ Mensaje: {res['mensaje_parser']}")

    total = len(resultados)
    pasados = sum(1 for r in resultados if r["coincidio"])
    fallos = total - pasados
    validos_esperados = sum(1 for c in casos if c["esperado"] == "valido")
    invalidos_esperados = sum(1 for c in casos if c["esperado"] == "invalido")

    print("\n" + "=" * 80)
    print(f"RESULTADO FINAL: {pasados}/{total} pasados | {fallos} fallidos")
    print(f"  Casos válidos esperados:   {validos_esperados}")
    print(f"  Casos inválidos esperados: {invalidos_esperados}")
    print("=" * 80)

    resumen = {
        "total": total,
        "pasados": pasados,
        "fallos": fallos,
        "validos_esperados": validos_esperados,
        "invalidos_esperados": invalidos_esperados,
        "todos_pasan": fallos == 0,
        "resultados": resultados,
    }

    if salida_json:
        with open(salida_json, "w", encoding="utf-8") as f:
            json.dump(resumen, f, indent=2, ensure_ascii=False)
        print(f"\nReporte exportado a: {salida_json}")

    return resumen


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Runner automático de pruebas sintácticas para SmartHomeLang"
    )
    parser.add_argument(
        "--casos",
        action="append",
        default=None,
        help="Ruta a un archivo JSON con casos de prueba (se puede repetir)",
    )
    parser.add_argument(
        "--salida",
        default="resultados_obtenidos.json",
        help="Ruta para exportar el reporte JSON",
    )
    parser.add_argument(
        "--generar-casos",
        action="store_true",
        help="Generar el JSON de casos predeterminados y salir",
    )
    parser.add_argument(
        "--ast",
        metavar="ENTRADA",
        default=None,
        help="Mostrar el AST de una entrada y salir",
    )
    args = parser.parse_args()

    if args.ast:
        es_valido, mensaje, ast = parse_fn(args.ast)
        print(mensaje)
        if ast is not None:
            imprimir_ast(ast)
        sys.exit(0 if es_valido else 1)

    if args.generar_casos:
        ruta = (args.casos or ["casos_prueba.json"])[0]
        guardar_casos_en_json(ruta, CASOS_PREDETERMINADOS)
        print(f"Casos de prueba generados en: {ruta}")
        print(f"  Válidos:   {sum(1 for c in CASOS_PREDETERMINADOS if c['esperado'] == 'valido')}")
        print(f"  Inválidos: {sum(1 for c in CASOS_PREDETERMINADOS if c['esperado'] == 'invalido')}")
        return

    if args.casos:
        casos: List[Dict] = []
        for ruta in args.casos:
            casos.extend(cargar_casos_desde_json(ruta))
    else:
        casos = CASOS_PREDETERMINADOS

    resumen = run_suite(casos, parse_fn=parse_fn, salida_json=args.salida)
    sys.exit(0 if resumen["todos_pasan"] else 1)


if __name__ == "__main__":
    main()
