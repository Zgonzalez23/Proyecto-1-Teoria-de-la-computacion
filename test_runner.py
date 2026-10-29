"""
Runner automático de pruebas sintácticas para el DSL IoT/Smart Home (SmartHomeLang).

Implementa:
  * Analizador léxico (lexer) basado en la tabla de tokens de docs/01_definicion_dsl.md
  * Parser LL(1) por descenso recursivo basado en la GLC de docs/02_glc.md
    (extensión ya integrada: operador NOT y múltiples acciones con coma)
  * Ejecutorio de suite de pruebas con reporte por consola y exportación a JSON

Extensión integrada en la GLC:
  - <comparacion>   → NOT <comparacion> | <factor_cond> <op_rel> <factor_cond>
  - <acciones_tail> → , <accion> <acciones_tail> | ε

Uso:
  python test_runner.py [--casos ruta.json] [--salida ruta.json]
"""

import argparse
import json
import sys
from typing import Callable, List, Dict, Tuple, Any, Optional

# 1. ANALIZADOR LÉXICO (LEXER)

# Palabras reservadas del DSL (incluye la extensión NOT)
PALABRAS_RESERVADAS = {
    "WHEN": "WHEN",
    "THEN": "THEN",
    "AND": "AND",
    "OR": "OR",
    "NOT": "NOT",
    "TRUE": "TRUE",
    "FALSE": "FALSE",
}

# Operadores relacionales (debe probarse primero el de 2 caracteres)
OPERADORES_RELACIONALES = {
    ">=": ">=",
    "<=": "<=",
    "==": "==",
    "!=": "!=",
    ">": ">",
    "<": "<",
}

# Símbolos separadores
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


class LexerError(Exception):
    """Error léxico: carácter no reconocido."""


def tokenizar(entrada: str) -> List[Token]:
    """
    Convierte una cadena de entrada en una lista de Token.

    Reconoce:
      * Palabras reservadas: WHEN, THEN, AND, OR, NOT, TRUE, FALSE
      * Identificadores:  [A-Za-z_][A-Za-z0-9_]*
      * Números enteros:    [0-9]+
      * Operadores relacionales: >= <= == != > <
      * Símbolos: ; ,
      * Espacios en blanco: ignorados
    """
    tokens: List[Token] = []
    i = 0
    linea = 1
    columna = 1
    n = len(entrada)

    while i < n:
        c = entrada[i]

        # Espacios en blanco (incluye tab y salto de línea)
        if c in " \t\r\n":
            if c == "\n":
                linea += 1
                columna = 1
            else:
                columna += 1
            i += 1
            continue

        # Operadores relacionales de 2 caracteres (prioridad)
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
        if c.isalpha() or c == "_":
            inicio = i
            while i < n and (entrada[i].isalnum() or entrada[i] == "_"):
                i += 1
            lexema = entrada[inicio:i]
            tipo = PALABRAS_RESERVADAS.get(lexema, "ID")
            tokens.append(Token(tipo, lexema, linea, columna))
            columna += i - inicio
            continue

        # Números enteros
        if c.isdigit():
            inicio = i
            while i < n and entrada[i].isdigit():
                i += 1
            lexema = entrada[inicio:i]
            tokens.append(Token("NUM", lexema, linea, columna))
            columna += i - inicio
            continue

        # Carácter no reconocido
        raise LexerError(
            f"Carácter no reconocido '{c}' en línea {linea}, columna {columna}"
        )

    # Marcador de fin de entrada
    tokens.append(Token("EOF", "$", linea, columna))
    return tokens


# 2. PARSER LL(1) POR DESCENSO RECURSIVO

# GLC final (docs/02_glc.md) con extensión integrada:
#
# <programa>        → <regla> <programa'>
# <programa'>       → <regla> <programa'> | ε
# <regla>           → WHEN <condicion> THEN <acciones> ;
# <condicion>       → <comparacion> <condicion_tail>
# <condicion_tail>  → AND <comparacion> <condicion_tail>
#                   |   OR <comparacion> <condicion_tail>
#                   |   ε
# <comparacion>     → NOT <comparacion>
#                   |   <factor_cond> <op_rel> <factor_cond>
# <factor_cond>     → ID | NUM | TRUE | FALSE
# <op_rel>          → > | < | >= | <= | == | !=
# <acciones>        → <accion> <acciones_tail>
# <acciones_tail>   → , <accion> <acciones_tail> | ε
# <accion>          → ID
#
# Símbolo inicial: <programa>

# Conjuntos FIRST para decisiones del parser (derivados de docs/03_first_follow.md)
FIRST_COMPARACION = {"NOT", "ID", "NUM", "TRUE", "FALSE"}
FIRST_CONDICION_TAIL = {"AND", "OR"}
FIRST_ACCIONES_TAIL = {","}
FOLLOW_ACCIONES_TAIL = {";"}
FOLLOW_CONDICION_TAIL = {"THEN"}


class ParserError(Exception):
    """Error sintáctico durante el análisis LL(1)."""


class Parser:
    """Parser LL(1) por descenso recursivo para SmartHomeLang."""

    def __init__(self, tokens: List[Token]):
        self.tokens = tokens
        self.pos = 0

    # utils

    def peek(self) -> Token:
        return self.tokens[self.pos]

    def avanzar(self) -> Token:
        tok = self.tokens[self.pos]
        self.pos += 1
        return tok

    def esperar(self, tipo_esperado: str) -> Token:
        tok = self.peek()
        if tok.tipo != tipo_esperado:
            raise ParserError(
                f"Se esperaba '{tipo_esperado}' pero se encontró '{tok.tipo}' "
                f"({tok.valor!r}) en L{tok.linea}:C{tok.columna}"
            )
        return self.avanzar()

    # producciones de la GLC 

    def programa(self) -> None:
        """<programa> → <regla> <programa'>"""
        self.regla()
        self.programa_prima()

    def programa_prima(self) -> None:
        """<programa'> → <regla> <programa'> | ε"""
        if self.peek().tipo == "WHEN":
            self.regla()
            self.programa_prima()
        # ε: no hacer nada

    def regla(self) -> None:
        """<regla> → WHEN <condicion> THEN <acciones> ;"""
        self.esperar("WHEN")
        self.condicion()
        self.esperar("THEN")
        self.acciones()
        self.esperar("PUNTO_COMA")

    def condicion(self) -> None:
        """<condicion> → <comparacion> <condicion_tail>"""
        self.comparacion()
        self.condicion_tail()

    def condicion_tail(self) -> None:
        """<condicion_tail> → AND <comparacion> <condicion_tail>
                          | OR <comparacion> <condicion_tail>
                          | ε"""
        if self.peek().tipo in ("AND", "OR"):
            self.avanzar()  # consume AND u OR
            self.comparacion()
            self.condicion_tail()
        # ε: no hacer nada

    def comparacion(self) -> None:
        """<comparacion> → NOT <comparacion>
                          | <factor_cond> <op_rel> <factor_cond>"""
        if self.peek().tipo == "NOT":
            self.avanzar()  # consume NOT
            self.comparacion()
        else:
            self.factor_cond()
            self.op_rel()
            self.factor_cond()

    def factor_cond(self) -> None:
        """<factor_cond> → ID | NUM | TRUE | FALSE"""
        if self.peek().tipo in ("ID", "NUM", "TRUE", "FALSE"):
            self.avanzar()
        else:
            raise ParserError(
                f"Se esperaba un factor (ID, NUM, TRUE o FALSE) pero se encontró "
                f"'{self.peek().tipo}' ({self.peek().valor!r}) en "
                f"L{self.peek().linea}:C{self.peek().columna}"
            )

    def op_rel(self) -> None:
        """<op_rel> → > | < | >= | <= | == | !="""
        if self.peek().tipo == "OP_REL":
            self.avanzar()
        else:
            raise ParserError(
                f"Se esperaba un operador relacional pero se encontró "
                f"'{self.peek().tipo}' ({self.peek().valor!r}) en "
                f"L{self.peek().linea}:C{self.peek().columna}"
            )

    def acciones(self) -> None:
        """<acciones> → <accion> <acciones_tail>"""
        self.accion()
        self.acciones_tail()

    def acciones_tail(self) -> None:
        """<acciones_tail> → , <accion> <acciones_tail> | ε"""
        if self.peek().tipo == "COMA":
            self.avanzar()  # consume ,
            self.accion()
            self.acciones_tail()
        # ε: no hacer nada

    def accion(self) -> None:
        """<accion> → ID"""
        self.esperar("ID")

    # punto de entrada 

    def parse(self) -> bool:
        """
        Ejecuta el análisis sintáctico completo.

        Returns True si la entrada es sintácticamente válida según la GLC,
        False en caso contrario.
        """
        try:
            self.programa()
            # Después del programa debe venir EOF
            if self.peek().tipo != "EOF":
                raise ParserError(
                    f"Tokens inesperados después del programa: "
                    f"'{self.peek().tipo}' ({self.peek().valor!r}) en "
                    f"L{self.peek().linea}:C{self.peek().columna}"
                )
            return True
        except ParserError:
            return False


def parse_fn(entrada: str) -> Tuple[bool, str, Any]:
    """
    Función de análisis que el runner invoca para cada caso de prueba.

    Returns:
        (es_valido, mensaje, ast) donde ast es None (no se construye AST
        en esta versión; el parser solo valida sintaxis).
    """
    entrada = entrada.strip()
    if not entrada:
        return False, "Entrada vacía", None

    try:
        tokens = tokenizar(entrada)
        parser = Parser(tokens)
        valido = parser.parse()
        if valido:
            return True, "Sintaxis válida (LL(1) por descenso recursivo)", None
        return False, "Error de sintaxis", None
    except LexerError as e:
        return False, f"Error léxico: {e}", None
    except ParserError as e:
        return False, f"Error de sintaxis: {e}", None
    except Exception as e:  # pylint: disable=broad-except
        return False, f"Excepción inesperada: {e}", None


# 3. CASOS DE PRUEBA

CASOS_PREDETERMINADOS: List[Dict] = [
    # CASOS VÁLIDOS (10) — extensión incluida: NOT y múltiples acciones
    {"entrada": "WHEN temperatura > 28 THEN encender_ventilador;", "esperado": "valido", "desc": "Condición simple > (básica)"},
    {"entrada": "WHEN movimiento == TRUE THEN activar_alarma;", "esperado": "valido", "desc": "Condición booleana == TRUE"},
    {"entrada": "WHEN humedad < 40 THEN activar_humidificador;", "esperado": "valido", "desc": "Condición simple <"},
    {"entrada": "WHEN temperatura > 28 AND humedad < 40 THEN encender_ventilador;", "esperado": "valido", "desc": "Compuesta con AND (extensión condicional)"},
    {"entrada": "WHEN temperatura > 28 OR humedad > 80 THEN encender_aire;", "esperado": "valido", "desc": "Compuesta con OR (extensión condicional)"},
    {"entrada": "WHEN NOT movimiento == TRUE THEN apagar_luces;", "esperado": "valido", "desc": "NOT sobre comparación (extensión NOT)"},
    {"entrada": "WHEN NOT humedad < 40 THEN activar_deshumidificador;", "esperado": "valido", "desc": "NOT sobre < (extensión NOT)"},
    {"entrada": "WHEN temperatura > 28 THEN encender_ventilador, abrir_ventana;", "esperado": "valido", "desc": "Múltiples acciones con coma (extensión acciones)"},
    {"entrada": "WHEN NOT alarma == TRUE THEN desactivar_sirena, enviar_notificacion;", "esperado": "valido", "desc": "NOT + múltiples acciones (extensión combinada)"},
    {"entrada": "WHEN NOT movimiento == TRUE AND temperatura < 18 THEN encender_calefaccion;", "esperado": "valido", "desc": "NOT + AND compuesto (extensión completa)"},

    # CASOS SINTÁCTICAMENTE INVÁLIDOS (10)
    {"entrada": "WHEN temperatura > 28 THEN ;", "esperado": "invalido", "desc": "Falta acción después de THEN"},
    {"entrada": "WHEN NOT THEN encender_luces;", "esperado": "invalido", "desc": "Falta condición tras NOT"},
    {"entrada": "temperatura > 28 THEN encender_ventilador;", "esperado": "invalido", "desc": "Falta palabra reservada WHEN"},
    {"entrada": "WHEN temperatura > 28 THEN encender_ventilador", "esperado": "invalido", "desc": "Falta punto y coma final"},
    {"entrada": "WHEN temperatura > 28 THEN encender_ventilador,", "esperado": "invalido", "desc": "Coma final sin segunda acción"},
    {"entrada": "WHEN NOT > 28 THEN encender_luces;", "esperado": "invalido", "desc": "NOT seguido de operador relacional (no es factor)"},
    {"entrada": "WHEN temperatura > 28 THEN encender_ventilador abrir_ventana;", "esperado": "invalido", "desc": "Falta coma entre acciones"},
    {"entrada": "WHEN temperatura > 28 THEN 123;", "esperado": "invalido", "desc": "Acción no es identificador (es NUM)"},
    {"entrada": "WHEN movimiento == THEN encender_luces;", "esperado": "invalido", "desc": "Falta valor tras operador relacional =="},
    {"entrada": "WHEN THEN encender_luces;", "esperado": "invalido", "desc": "Falta condición completa"},
]


# 4. RUNNER DE PRUEBAS

def cargar_casos_desde_json(ruta: str) -> List[Dict]:
    """Carga casos de prueba desde un archivo JSON."""
    with open(ruta, "r", encoding="utf-8") as f:
        return json.load(f)


def guardar_casos_en_json(ruta: str, casos: List[Dict]) -> None:
    """Guarda casos de prueba en un archivo JSON."""
    with open(ruta, "w", encoding="utf-8") as f:
        json.dump(casos, f, indent=2, ensure_ascii=False)


def ejecutar_caso(
    caso: Dict, parse_fn: Callable[[str], Tuple[bool, str, Any]]
) -> Dict:
    """Ejecuta un único caso de prueba y devuelve el resultado detallado."""
    entrada = caso["entrada"]
    esperado = caso["esperado"]
    descripcion = caso.get("desc", "")

    try:
        es_valido, mensaje, ast = parse_fn(entrada)
        obtenido = "valido" if es_valido else "invalido"
        coincidio = obtenido == esperado
    except Exception as e:  # pylint: disable=broad-except
        es_valido = False
        mensaje = f"Excepción: {e}"
        obtenido = "invalido"
        coincidio = esperado == "invalido"

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
    """
    Ejecuta la suite completa de pruebas.

    Returns un diccionario con el resumen de resultados.
    """
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

    # Resumen
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

    # Exportar a JSON
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
        help="Ruta a un archivo JSON con casos de prueba (se puede repetir para varios archivos)",
    )
    parser.add_argument(
        "--salida",
        default="resultados_obtenidos.json",
        help="Ruta para exportar el reporte JSON (default: resultados_obtenidos.json)",
    )
    parser.add_argument(
        "--generar-casos",
        action="store_true",
        help="Generar el archivo JSON de casos de prueba predeterminados y salir",
    )
    args = parser.parse_args()

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

    run_suite(casos, parse_fn=parse_fn, salida_json=args.salida)
    sys.exit(0)


if __name__ == "__main__":
    main()
