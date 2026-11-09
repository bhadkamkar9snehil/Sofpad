"""Part placement for each board. Coordinates in mm, origin top-left, +y down; top of the
board = rear of the case (USB-C side). Tuples are (x, y, rotation, side) with side T or B."""

CARRIER_W, CARRIER_H = 62.0, 28.0

CARRIER = {
    # top side
    "U1": (7.2, 8.4, 0, "T"), "J1": (22.5, 5.2, 0, "T"), "SW1": (45.0, 3.2, 0, "T"),
    "J4": (55.5, 4.0, 0, "T"), "J6": (34.0, 3.0, 0, "T"), "U4": (47.5, 12.0, 0, "T"),
    "L1": (39.0, 15.5, 0, "T"), "J3": (59.0, 11.5, 0, "T"), "U6": (30.0, 12.5, 0, "T"),
    "J7": (8.2, 24.0, 0, "T"), "J5": (25.4, 23.6, 0, "T"), "J8": (43.2, 24.0, 0, "T"),
    "J2": (56.5, 23.4, 0, "T"),
    "C12": (16.0, 13.5, 0, "T"), "C7": (16.0, 15.5, 0, "T"), "R8": (19.0, 15.5, 0, "T"), "R9": (19.0, 17.0, 0, "T"),
    # bottom side
    "U2": (28.0, 14.5, 0, "B"), "C1": (24.0, 11.0, 0, "B"), "C2": (32.0, 11.0, 0, "B"), "C3": (32.0, 17.5, 0, "B"),
    "R3": (24.5, 18.5, 0, "B"), "R4": (27.0, 19.5, 0, "B"), "R5": (29.5, 19.5, 0, "B"), "R6": (22.0, 17.0, 0, "B"),
    "R7": (35.5, 13.5, 0, "B"),
    "U3": (40.5, 14.5, 0, "B"), "C4": (37.5, 11.0, 0, "B"), "C5": (43.5, 11.0, 0, "B"), "C6": (45.5, 15.0, 0, "B"),
    "U5": (52.0, 15.5, 0, "B"), "C10": (55.5, 12.0, 0, "B"), "R12": (49.5, 18.5, 0, "B"),
    "R1": (17.0, 9.0, 0, "B"), "R2": (17.0, 10.8, 0, "B"), "C9": (47.0, 8.0, 0, "B"), "C8": (51.0, 8.0, 0, "B"),
    "R10": (18.0, 20.0, 0, "B"), "R11": (20.5, 20.0, 0, "B"), "C11": (23.0, 20.0, 0, "B"),
    "TP1": (6.0, 17.5, 0, "B"), "TP2": (9.0, 17.5, 0, "B"), "TP3": (12.0, 17.5, 0, "B"),
    "TP4": (30.0, 6.0, 0, "B"), "TP5": (34.0, 6.0, 0, "B"),
}
CARRIER_HOLES = []   # no screw holes: the board sits on foam pads between printed locator posts
CARRIER_KEEPOUT = []

ADAPTER_W, ADAPTER_H = 18.0, 33.0
ADAPTER = {"J1": (9.0, 24.0, 0, "T"), "HL": (1.38, 2.5, 0, "T"), "HR": (16.62, 30.44, 180, "T")}
ADAPTER_HOLES = []


def make(which, build):
    if which == "carrier":
        return build("carrier", "carrier", CARRIER_W, CARRIER_H, 4, CARRIER, CARRIER_HOLES, CARRIER_KEEPOUT)
    if which == "adapter_a":
        return build("adapter", "adapter_a", ADAPTER_W, ADAPTER_H, 2, ADAPTER, ADAPTER_HOLES)
    if which == "adapter_b":
        return build("adapter", "adapter_b", ADAPTER_W, ADAPTER_H, 2, ADAPTER, ADAPTER_HOLES, mirror_x=True)
    raise SystemExit(which)
