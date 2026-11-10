"""Part placement for each board. Coordinates in mm, origin top-left, +y down; top of the
board = rear of the case (USB-C side). Tuples are (x, y, rotation, side) with side T or B."""

CARRIER_W, CARRIER_H = 62.0, 28.0

CARRIER = {
    # top side. The two FFC sockets sit on the side edges: each adapter is ~9 mm outside the board, so the cables are short.
    "J7": (4.4, 14.0, 270, "T"), "J8": (57.6, 14.0, 90, "T"),
    "U1": (15.8, 8.4, 0, "T"), "J1": (29.5, 5.2, 0, "T"), "SW1": (45.0, 3.2, 0, "T"),
    "J4": (55.5, 3.0, 0, "T"), "J6": (49.5, 24.5, 0, "T"), "U4": (47.5, 13.0, 0, "T"),
    "L1": (39.5, 16.0, 0, "T"), "J3": (57.8, 24.5, 0, "T"), "U6": (34.5, 12.5, 0, "T"),
    "J5": (22.0, 23.0, 0, "T"), "J2": (38.0, 23.0, 0, "T"),
    "C12": (23.5, 13.5, 0, "T"), "C7": (23.5, 15.5, 0, "T"), "R8": (26.0, 15.5, 0, "T"), "R9": (26.0, 17.0, 0, "T"),
    # bottom side
    "U2": (30.0, 17.5, 0, "B"), "C1": (27.0, 13.0, 0, "B"), "C2": (33.0, 13.0, 0, "B"), "C3": (35.0, 18.5, 0, "B"),
    "R3": (26.5, 20.5, 0, "B"), "R4": (29.0, 21.5, 0, "B"), "R5": (31.5, 21.5, 0, "B"), "R6": (24.0, 20.5, 0, "B"),
    "R7": (37.0, 15.0, 0, "B"),
    "U3": (43.0, 17.5, 0, "B"), "C4": (39.5, 12.5, 0, "B"), "C5": (45.5, 12.5, 0, "B"), "C6": (47.5, 18.0, 0, "B"),
    "U5": (53.0, 15.5, 0, "B"), "C10": (56.0, 11.0, 0, "B"), "R12": (51.0, 20.0, 0, "B"),
    "R1": (21.0, 5.0, 0, "B"), "R2": (21.0, 6.8, 0, "B"), "C9": (49.0, 8.0, 0, "B"), "C8": (52.0, 8.0, 0, "B"),
    "R10": (13.0, 22.0, 0, "B"), "R11": (15.5, 22.0, 0, "B"), "C11": (18.0, 22.0, 0, "B"),
    "R13": (11.0, 25.5, 0, "B"), "R14": (13.5, 25.5, 0, "B"), "R15": (16.0, 25.5, 0, "B"), "R16": (18.5, 25.5, 0, "B"),
    "TP1": (4.0, 24.5, 0, "B"), "TP2": (7.0, 24.5, 0, "B"), "TP3": (4.0, 21.5, 0, "B"),
    "TP4": (38.0, 6.0, 0, "B"), "TP5": (41.5, 6.0, 0, "B"),
}
CARRIER_HOLES = []   # no screw holes: the board sits on foam pads between printed locator posts
CARRIER_KEEPOUT = []

# The board is 9 mm longer than a Pro Micro: the FFC connector sits past the end of the pin rows,
# on the side that points at the Sofle PCB edge (nothing there), cable leaving toward the case rear.
ADAPTER_W, ADAPTER_H = 18.0, 40.0
ADAPTER = {"J1": (9.0, 4.3, 180, "T"), "HL": (1.38, 24.2, 0, "T"), "HR": (16.62, 24.2, 0, "T")}
ADAPTER_HOLES = []


def make(which, build):
    if which == "carrier":
        return build("carrier", "carrier", CARRIER_W, CARRIER_H, 4, CARRIER, CARRIER_HOLES, CARRIER_KEEPOUT)
    if which == "adapter_a":
        return build("adapter", "adapter_a", ADAPTER_W, ADAPTER_H, 2, ADAPTER, ADAPTER_HOLES)
    if which == "adapter_b":
        return build("adapter", "adapter_b", ADAPTER_W, ADAPTER_H, 2, ADAPTER, ADAPTER_HOLES, mirror_x=True)
    raise SystemExit(which)
