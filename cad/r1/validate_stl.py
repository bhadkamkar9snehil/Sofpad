#!/usr/bin/env python3
"""Read a binary STL and report size, edge closure, and surface components.

No nonstandard Python packages are needed.
"""

from __future__ import annotations

import argparse
import collections
import pathlib
import struct


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("stl", type=pathlib.Path)
    args = parser.parse_args()
    data = args.stl.read_bytes()
    count = struct.unpack_from("<I", data, 80)[0]
    if len(data) != 84 + count * 50:
        raise ValueError("Not a standard binary STL")

    points: dict[tuple[float, float, float], int] = {}
    by_id: list[tuple[float, float, float]] = []
    adjacency: dict[int, set[int]] = collections.defaultdict(set)
    edge_count: collections.Counter[tuple[int, int]] = collections.Counter()
    mins = [float("inf")] * 3
    maxs = [-float("inf")] * 3

    for i in range(count):
        coords = struct.unpack_from("<9f", data, 84 + i * 50 + 12)
        ids = []
        for k in range(0, 9, 3):
            pt = coords[k : k + 3]
            if pt not in points:
                points[pt] = len(points)
                by_id.append(pt)
            ids.append(points[pt])
            for axis in range(3):
                mins[axis] = min(mins[axis], pt[axis])
                maxs[axis] = max(maxs[axis], pt[axis])
        for a, b in ((0, 1), (1, 2), (2, 0)):
            p, q = ids[a], ids[b]
            edge_count[tuple(sorted((p, q)))] += 1
            adjacency[p].add(q)
            adjacency[q].add(p)

    visited: set[int] = set()
    components: list[tuple[int, list[float], list[float]]] = []
    for start in points.values():
        if start in visited:
            continue
        stack = [start]
        visited.add(start)
        size = 0
        low = [float("inf")] * 3
        high = [-float("inf")] * 3
        while stack:
            node = stack.pop()
            size += 1
            for axis in range(3):
                low[axis] = min(low[axis],by_id[node][axis])
                high[axis] = max(high[axis],by_id[node][axis])
            for other in adjacency[node]:
                if other not in visited:
                    visited.add(other)
                    stack.append(other)
        components.append((size, low, high))

    open_edges = sum(1 for n in edge_count.values() if n != 2)
    dims = [round(maxs[a] - mins[a], 2) for a in range(3)]
    components.sort(key=lambda x:x[0], reverse=True)
    print(f"STL: {args.stl.name}")
    print(f"Size (X×Y×Z): {dims[0]} × {dims[1]} × {dims[2]} mm")
    print(f"Triangles: {count}; vertices: {len(points)}")
    print(f"Surface components: {len(components)}; vertex counts: {[c[0] for c in components]}")
    for count_vertices, low, high in components:
        if count_vertices < 100:
            print(f"  Small component bounds: {low} to {high}")
    print(f"Edges not shared by exactly two triangles: {open_edges}")
    if len(components) != 1 or open_edges:
        raise SystemExit("FAIL: STL is not one closed connected shell")
    print("PASS: STL is one closed connected shell")


if __name__ == "__main__":
    main()
