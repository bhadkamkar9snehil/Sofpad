"""Build a KiCad schematic from a netlist described in Python.

One Design object holds parts and nets. It writes:
  * <name>.kicad_sch   every pin gets a global label (its net) or a no-connect flag
  * <name>.net.json    ref -> footprint and net -> [ref.pin] for the board builder
Pin numbers come straight from the KiCad symbol libraries (kilib), and are checked
against the footprint pad names, so schematic and board cannot disagree.
"""
import json
import uuid
from pathlib import Path

import kilib

CUSTOM_SYMBOLS = {}   # "Sofpad:Name" -> (text, pins)


def uid():
    return str(uuid.uuid4())


class Design:
    def __init__(self, name):
        self.name = name
        self.parts = {}       # ref -> dict(lib, sym, fp, value, props)
        self.nets = {}        # net -> list of "REF.PIN"
        self.flags = []       # nets that get a PWR_FLAG

    def part(self, ref, lib, sym, fp, value="", **props):
        self.parts[ref] = dict(lib=lib, sym=sym, fp=fp, value=value or sym, props=props)

    def conn(self, net, *pins):
        self.nets.setdefault(net, []).extend(pins)

    def pins_of(self, ref):
        p = self.parts[ref]
        if p["lib"] == "Sofpad":
            return CUSTOM_SYMBOLS[f"Sofpad:{p['sym']}"][1]
        return kilib.symbol_pins(p["lib"], p["sym"])

    # ------------------------------------------------------------------ checks
    def check(self):
        errs = []
        used = {}
        for net, pins in self.nets.items():
            for rp in pins:
                ref, pin = rp.split(".", 1)
                if ref not in self.parts:
                    errs.append(f"{net}: unknown part {ref}")
                    continue
                if (ref, pin) in used:
                    errs.append(f"{ref}.{pin} is in two nets: {used[(ref, pin)]} and {net}")
                used[(ref, pin)] = net
        for ref, p in self.parts.items():
            sympins = {x[0] for x in self.pins_of(ref)}
            pads = kilib.footprint_pads(p["fp"]) if p["fp"] else set()
            for (r, pin), net in used.items():
                if r != ref:
                    continue
                if pin not in sympins:
                    errs.append(f"{ref}.{pin} ({net}) is not a pin of {p['lib']}:{p['sym']}")
                if p["fp"] and pin not in pads:
                    errs.append(f"{ref}.{pin} ({net}) is not a pad of {p['fp']}")
        return errs

    # ------------------------------------------------------------- schematic
    def write(self, outdir):
        outdir = Path(outdir)
        outdir.mkdir(parents=True, exist_ok=True)
        errs = self.check()
        if errs:
            raise SystemExit("netlist errors:\n  " + "\n  ".join(errs))
        pin_net = {}
        for net, pins in self.nets.items():
            for rp in pins:
                ref, pin = rp.split(".", 1)
                pin_net[(ref, pin)] = net

        lib_ids = {}
        for ref, p in self.parts.items():
            lib_ids[f"{p['lib']}:{p['sym']}"] = (p["lib"], p["sym"])
        flag_sym = ("power", "PWR_FLAG")
        if self.flags:
            lib_ids["power:PWR_FLAG"] = flag_sym

        root = uid()
        out = ['(kicad_sch', '\t(version 20231120)', '\t(generator "sofpad_kigen")', '\t(generator_version "1.0")',
               f'\t(uuid "{root}")', '\t(paper "A2")', '\t(lib_symbols']
        for lid, (lib, sym) in lib_ids.items():
            if lib == "Sofpad":
                text = CUSTOM_SYMBOLS[lid][0]
            else:
                text = kilib.symbol_text(lib, sym)
            out.append("\t\t" + text.replace("\n", "\n\t\t"))
        out.append("\t)")

        x0, y0 = 30.0, 30.0
        col_w, cursor_x, cursor_y, row_h = 95.0, x0, y0, 0.0
        placed = []
        n = 0
        for ref, p in self.parts.items():
            pins = self.pins_of(ref)
            ys = [q[4] for q in pins] or [0]
            xs = [q[3] for q in pins] or [0]
            h = (max(ys) - min(ys)) + 12.0
            if n and n % 4 == 0:
                cursor_x = x0
                cursor_y += row_h + 8
                row_h = 0
            row_h = max(row_h, h)
            ox = round((cursor_x - min(xs) + 22) / 2.54) * 2.54
            oy = round((cursor_y + max(ys) + 6) / 2.54) * 2.54
            cursor_x += col_w
            n += 1
            lid = f"{p['lib']}:{p['sym']}"
            out.append(f'\t(symbol (lib_id "{lid}") (at {ox:.2f} {oy:.2f} 0) (unit 1) (exclude_from_sim no) (in_bom yes) (on_board yes) (dnp no)')
            out.append(f'\t\t(uuid "{uid()}")')
            out.append(f'\t\t(property "Reference" "{ref}" (at {ox:.2f} {oy - max(ys) - 4:.2f} 0) (effects (font (size 1.27 1.27))))')
            out.append(f'\t\t(property "Value" "{p["value"]}" (at {ox:.2f} {oy - max(ys) - 2:.2f} 0) (effects (font (size 1.27 1.27))))')
            out.append(f'\t\t(property "Footprint" "{p["fp"]}" (at {ox:.2f} {oy:.2f} 0) (effects (font (size 1.27 1.27)) hide))')
            out.append(f'\t\t(property "Datasheet" "" (at {ox:.2f} {oy:.2f} 0) (effects (font (size 1.27 1.27)) hide))')
            for k, v in p["props"].items():
                out.append(f'\t\t(property "{k}" "{v}" (at {ox:.2f} {oy:.2f} 0) (effects (font (size 1.27 1.27)) hide))')
            for q in pins:
                out.append(f'\t\t(pin "{q[0]}" (uuid "{uid()}"))')
            out.append("\t\t(instances")
            out.append(f'\t\t\t(project "{self.name}" (path "/{root}" (reference "{ref}") (unit 1)))')
            out.append("\t\t)")
            out.append("\t)")
            placed.append((ref, ox, oy, pins))

        seen_lab = set()
        for ref, ox, oy, pins in placed:
            seen_nc = set()
            for num, pname, ptype, px, py, pang in pins:
                wx, wy = ox + px, oy - py
                net = pin_net.get((ref, num))
                if net and (round(wx, 2), round(wy, 2), net) in seen_lab:
                    continue
                if net:
                    seen_lab.add((round(wx, 2), round(wy, 2), net))
                    lang = (pang + 180) % 360
                    out.append(f'\t(global_label "{net}" (shape passive) (at {wx:.2f} {wy:.2f} {lang}) (fields_autoplaced yes)')
                    out.append('\t\t(effects (font (size 1.27 1.27)) (justify left))')
                    out.append(f'\t\t(uuid "{uid()}")')
                    out.append('\t\t(property "Intersheetrefs" "${INTERSHEET_REFS}" (at 0 0 0) (effects (font (size 1.27 1.27)) hide))')
                    out.append("\t)")
                elif ptype != "no_connect" and (wx, wy) not in seen_nc:
                    seen_nc.add((wx, wy))
                    out.append(f'\t(no_connect (at {wx:.2f} {wy:.2f}) (uuid "{uid()}"))')

        # power flags
        fx, fy = 30.48, round((cursor_y + row_h + 40) / 2.54) * 2.54
        for i, net in enumerate(self.flags):
            ox, oy = fx + round(i * 30 / 2.54) * 2.54, fy
            out.append(f'\t(symbol (lib_id "power:PWR_FLAG") (at {ox:.2f} {oy:.2f} 0) (unit 1) (exclude_from_sim no) (in_bom no) (on_board no) (dnp no)')
            out.append(f'\t\t(uuid "{uid()}")')
            out.append(f'\t\t(property "Reference" "#FLG0{i + 1}" (at {ox:.2f} {oy + 3:.2f} 0) (effects (font (size 1.27 1.27)) hide))')
            out.append(f'\t\t(property "Value" "PWR_FLAG" (at {ox:.2f} {oy + 5:.2f} 0) (effects (font (size 1.27 1.27))))')
            out.append(f'\t\t(property "Footprint" "" (at {ox:.2f} {oy:.2f} 0) (effects (font (size 1.27 1.27)) hide))')
            out.append(f'\t\t(property "Datasheet" "~" (at {ox:.2f} {oy:.2f} 0) (effects (font (size 1.27 1.27)) hide))')
            out.append(f'\t\t(pin "1" (uuid "{uid()}"))')
            out.append("\t\t(instances")
            out.append(f'\t\t\t(project "{self.name}" (path "/{root}" (reference "#FLG0{i + 1}") (unit 1)))')
            out.append("\t\t)")
            out.append("\t)")
            fp = kilib.symbol_pins("power", "PWR_FLAG")[0]
            wx, wy = ox + fp[3], oy - fp[4]
            out.append(f'\t(global_label "{net}" (shape passive) (at {wx:.2f} {wy:.2f} {(fp[5] + 180) % 360}) (fields_autoplaced yes)')
            out.append('\t\t(effects (font (size 1.27 1.27)) (justify left))')
            out.append(f'\t\t(uuid "{uid()}")')
            out.append('\t\t(property "Intersheetrefs" "${INTERSHEET_REFS}" (at 0 0 0) (effects (font (size 1.27 1.27)) hide))')
            out.append("\t)")
        out.append('\t(sheet_instances (path "/" (page "1")))')
        out.append(")")
        (outdir / f"{self.name}.kicad_sch").write_text("\n".join(out) + "\n", encoding="utf-8")

        pro = {"meta": {"version": 1}, "sheets": [[root, "Root"]]}
        (outdir / f"{self.name}.kicad_pro").write_text(json.dumps(pro, indent=2), encoding="utf-8")
        self._tables(outdir, lib_ids)
        data = {
            "parts": {r: {"fp": p["fp"], "value": p["value"], "sym": f"{p['lib']}:{p['sym']}"} for r, p in self.parts.items()},
            "nets": self.nets,
        }
        (outdir / f"{self.name}.net.json").write_text(json.dumps(data, indent=1), encoding="utf-8")
        return outdir / f"{self.name}.kicad_sch"

    def _tables(self, outdir, lib_ids):
        syms = sorted({lib for lib, _ in lib_ids.values() if lib != "Sofpad"})
        t = ["(sym_lib_table", "  (version 7)"]
        for lib in syms:
            t.append(f'  (lib (name "{lib}")(type "KiCad")(uri "${{KICAD10_SYMBOL_DIR}}/{lib}.kicad_sym")(options "")(descr ""))')
        if any(lib == "Sofpad" for lib, _ in lib_ids.values()):
            t.append('  (lib (name "Sofpad")(type "KiCad")(uri "${KIPRJMOD}/sofpad.kicad_sym")(options "")(descr ""))')
            body = "\n".join(v[0] for k, v in CUSTOM_SYMBOLS.items()).replace('"Sofpad:', '"')
            (outdir / "sofpad.kicad_sym").write_text(
                '(kicad_symbol_lib (version 20231120) (generator "sofpad_kigen")\n' + body + "\n)\n", encoding="utf-8")
        t.append(")")
        (outdir / "sym-lib-table").write_text("\n".join(t) + "\n", encoding="utf-8")
        fps = sorted({p["fp"].split(":")[0] for p in self.parts.values() if p["fp"]})
        t = ["(fp_lib_table", "  (version 7)"]
        for lib in fps:
            t.append(f'  (lib (name "{lib}")(type "KiCad")(uri "${{KICAD10_FOOTPRINT_DIR}}/{lib}.pretty")(options "")(descr ""))')
        t.append(")")
        (outdir / "fp-lib-table").write_text("\n".join(t) + "\n", encoding="utf-8")
