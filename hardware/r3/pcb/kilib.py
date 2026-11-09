"""Tiny KiCad library helpers: s-expression parser, symbol pin lookup, footprint pad lookup.

Used by gen_carrier.py to build the schematic and board from one netlist, so the
two can never disagree on pin numbers.
"""
import os
import re
from functools import lru_cache
from pathlib import Path

KICAD = Path(os.environ.get("KICAD_ROOT", r"C:\Users\Admin\AppData\Local\Programs\KiCad\10.0"))
SYMBOLS = KICAD / "share" / "kicad" / "symbols"
FOOTPRINTS = KICAD / "share" / "kicad" / "footprints"


def tokenize(text):
    return re.findall(r'\(|\)|"(?:[^"\\]|\\.)*"|[^\s()"]+', text)


def parse(text):
    toks = tokenize(text)
    pos = 0

    def node():
        nonlocal pos
        assert toks[pos] == "("
        pos += 1
        out = []
        while toks[pos] != ")":
            if toks[pos] == "(":
                out.append(node())
            else:
                t = toks[pos]
                out.append(t[1:-1].replace('\\"', '"') if t.startswith('"') else t)
                pos += 1
        pos += 1
        return out

    return node()


@lru_cache(maxsize=None)
def _symlib(lib):
    text = (SYMBOLS / f"{lib}.kicad_sym").read_text(encoding="utf-8")
    return text, parse(text)


def symbol_text(lib, name):
    """Raw text of one symbol block (for embedding in a schematic) with its lib prefix.

    A symbol that `extends` a parent is flattened: the parent's graphics and pins are
    embedded under the child's name, as KiCad itself does when it saves a schematic.
    """
    text, _ = _symlib(lib)
    ext = [c for c in symbol_node(lib, name) if isinstance(c, list) and c and c[0] == "extends"]
    if ext:
        parent = ext[0][1]
        body = symbol_text(lib, parent)
        body = body.replace(f'(symbol "{lib}:{parent}"', f'(symbol "{lib}:{name}"', 1)
        body = body.replace(f'(symbol "{parent}_', f'(symbol "{name}_')
        return body
    start = text.index(f'(symbol "{name}"')
    depth = 0
    for i in range(start, len(text)):
        if text[i] == "(":
            depth += 1
        elif text[i] == ")":
            depth -= 1
            if depth == 0:
                block = text[start:i + 1]
                return block.replace(f'(symbol "{name}"', f'(symbol "{lib}:{name}"', 1)
    raise KeyError(name)


def symbol_node(lib, name):
    _, tree = _symlib(lib)
    for n in tree[1:]:
        if isinstance(n, list) and n and n[0] == "symbol" and n[1] == name:
            return n
    raise KeyError(f"{lib}:{name}")


def _flatten(node, found):
    for c in node:
        if isinstance(c, list):
            if c and c[0] == "pin":
                found.append(c)
            else:
                _flatten(c, found)


def symbol_pins(lib, name):
    """[(number, name, type, x, y, angle)] for a symbol, following `extends`."""
    node = symbol_node(lib, name)
    ext = [c for c in node if isinstance(c, list) and c and c[0] == "extends"]
    if ext:
        node = symbol_node(lib, ext[0][1])
    pins = []
    _flatten(node, pins)
    out = []
    for p in pins:
        at = next(c for c in p if isinstance(c, list) and c[0] == "at")
        nm = next(c for c in p if isinstance(c, list) and c[0] == "name")[1]
        num = next(c for c in p if isinstance(c, list) and c[0] == "number")[1]
        out.append((num, nm, p[1], float(at[1]), float(at[2]), int(float(at[3]))))
    return out


def symbol_prop(lib, name, prop):
    node = symbol_node(lib, name)
    for c in node:
        if isinstance(c, list) and c and c[0] == "property" and c[1] == prop:
            return c[2]
    return ""


def footprint_path(fp):
    lib, name = fp.split(":")
    return FOOTPRINTS / f"{lib}.pretty" / f"{name}.kicad_mod"


def footprint_pads(fp):
    """Set of pad names in a footprint."""
    text = footprint_path(fp).read_text(encoding="utf-8")
    return {m for m in re.findall(r'\(pad "([^"]*)"', text) if m}
