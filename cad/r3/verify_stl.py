"""Check exported binary STL triangle edges and physical bounds (millimetres).

This verifies a closed triangle mesh. It does not test 3D-print tolerance,
component fit, self-intersections, or PCB/firmware correctness.
"""

from collections import Counter
from pathlib import Path
import struct


HERE = Path(__file__).resolve().parent


def inspect(path):
    data = path.read_bytes()
    triangles = []
    if data.startswith(b"solid "):
        vertices = [tuple(round(float(c), 4) for c in line.split()[1:4])
                    for line in data.decode("ascii").splitlines()
                    if line.strip().startswith("vertex ")]
        assert len(vertices) % 3 == 0, f"Invalid ASCII STL: {path.name}"
        triangles = [vertices[i:i+3] for i in range(0, len(vertices), 3)]
    else:
        triangle_count = struct.unpack_from("<I", data, 80)[0]
        assert len(data) == 84 + triangle_count * 50, f"Invalid STL length: {path.name}"
        for n in range(triangle_count):
            v = struct.unpack_from("<9f", data, 84 + n * 50 + 12)
            triangles.append([tuple(round(c, 4) for c in v[i:i+3])
                              for i in (0, 3, 6)])
    edges = Counter()
    points = []
    for vertices in triangles:
        points.extend(vertices)
        for a, b in ((0, 1), (1, 2), (2, 0)):
            edges[tuple(sorted((vertices[a], vertices[b])))] += 1
    invalid_edges = [(k, count) for k, count in edges.items() if count != 2]
    dimensions = [round(max(p[i] for p in points) - min(p[i] for p in points), 2)
                  for i in range(3)]
    print(f"{path.name}: triangles={len(triangles)}, extents_mm={dimensions}, "
          f"non_manifold_edges={len(invalid_edges)}")
    assert not invalid_edges, f"Non-manifold triangle edges: {path.name}"


if __name__ == "__main__":
    for part in ("Unibody_Shell.stl", "Service_Bottom.stl", "TPS43_Retainer.stl"):
        inspect(HERE / part)
    print("PASS: three closed STL triangle meshes")
