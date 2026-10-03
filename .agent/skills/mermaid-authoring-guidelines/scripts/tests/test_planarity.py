"""Tests for planarity.py (TASK 108, D21): the exact planarity test of a flowchart's simple graph.

Known graphs pin the verdict and the deciding test. A brute-force Kuratowski-minor search,
written here independently of the module, cross-checks every graph on at most 6 vertices and
seeded samples on 7 and 8 vertices (Wagner: a graph is planar iff it has no K5 and no K3,3 minor).
"""
import random
import sys
import unittest
from itertools import combinations
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import planarity as pl  # noqa: E402


# --------------------------------------------------------------------------- graph families

def complete(n):
    return list(combinations(range(n), 2))


def complete_bipartite(m, n):
    return [(f"a{i}", f"b{j}") for i in range(m) for j in range(n)]


def cycle(n, offset=0):
    return [(offset + i, offset + (i + 1) % n) for i in range(n)]


def subdivide(edges, which=None):
    """Replace each chosen edge u-v by u-s-v with a new vertex s."""
    out = []
    for k, (u, v) in enumerate(edges):
        if which is None or k in which:
            s = ("s", k)
            out += [(u, s), (s, v)]
        else:
            out.append((u, v))
    return out


def generalized_petersen(n, k):
    return ([(i, (i + 1) % n) for i in range(n)] + [(i, n + i) for i in range(n)]
            + [(n + i, n + (i + k) % n) for i in range(n)])


PETERSEN = generalized_petersen(5, 2)
DODECAHEDRON = generalized_petersen(10, 2)
CUBE = cycle(4) + cycle(4, 4) + [(i, i + 4) for i in range(4)]
OCTAHEDRON = [p for p in complete(6) if p not in ((0, 1), (2, 3), (4, 5))]
WAGNER = cycle(8) + [(i, i + 4) for i in range(4)]


def icosahedron():
    edges = [(0, 1 + i) for i in range(5)] + [(11, 6 + i) for i in range(5)]
    edges += [(1 + i, 1 + (i + 1) % 5) for i in range(5)] + [(6 + i, 6 + (i + 1) % 5) for i in range(5)]
    edges += [(1 + i, 6 + i) for i in range(5)] + [(1 + i, 6 + (i + 1) % 5) for i in range(5)]
    return edges


def wheel(n):
    return cycle(n) + [("hub", i) for i in range(n)]


def grid(m, n):
    edges = []
    for r in range(m):
        for c in range(n):
            if c + 1 < n:
                edges.append(((r, c), (r, c + 1)))
            if r + 1 < m:
                edges.append(((r, c), (r + 1, c)))
    return edges


def prism(n):
    return cycle(n) + cycle(n, n) + [(i, n + i) for i in range(n)]


def apollonian(steps, seed):
    """A maximal planar graph: insert vertices into triangular faces (E = 3V - 6)."""
    rng = random.Random(seed)
    edges = [(0, 1), (1, 2), (0, 2)]
    faces = [(0, 1, 2)]
    for v in range(3, 3 + steps):
        a, b, c = faces.pop(rng.randrange(len(faces)))
        edges += [(v, a), (v, b), (v, c)]
        faces += [(a, b, v), (b, c, v), (a, c, v)]
    return edges


def random_tree(n, seed):
    rng = random.Random(seed)
    return [(i, rng.randrange(i)) for i in range(1, n)]


# --------------------------------------------------------------------------- brute force (independent)

def _reduce(edges):
    """Delete vertices of degree <= 1 and smooth vertices of degree 2. Both keep the existence of
    a K5 or K3,3 minor, since every vertex of K5 and K3,3 has degree >= 3."""
    adj = {}
    for e in edges:
        a, b = tuple(e)
        adj.setdefault(a, set()).add(b)
        adj.setdefault(b, set()).add(a)
    changed = True
    while changed:
        changed = False
        for v in list(adj):
            if v not in adj:
                continue
            if len(adj[v]) <= 1:
                for w in adj[v]:
                    adj[w].discard(v)
                del adj[v]
                changed = True
            elif len(adj[v]) == 2:
                u, w = sorted(adj[v], key=repr)
                adj[u].discard(v)
                adj[w].discard(v)
                del adj[v]
                adj[u].add(w)
                adj[w].add(u)
                changed = True
    return frozenset(frozenset((a, b)) for a in adj for b in adj[a])


def _vertices(edges):
    out = set()
    for e in edges:
        out |= e
    return out


def _has_k5(edges, vs):
    return any(all(frozenset(p) in edges for p in combinations(c, 2))
               for c in combinations(sorted(vs, key=repr), 5))


def _has_k33(edges, vs):
    for c in combinations(sorted(vs, key=repr), 6):
        for rest in combinations(c[1:], 2):
            side_a = (c[0],) + rest
            side_b = [x for x in c if x not in side_a]
            if all(frozenset((a, b)) in edges for a in side_a for b in side_b):
                return True
    return False


def _contract(edges, keep, drop):
    out = set()
    for e in edges:
        a, b = tuple(e)
        a = keep if a == drop else a
        b = keep if b == drop else b
        if a != b:
            out.add(frozenset((a, b)))
    return frozenset(out)


def has_kuratowski_minor(edges, memo=None):
    """True when the graph has a K5 or K3,3 minor: contract edges, then look for the subgraph."""
    memo = {} if memo is None else memo
    edges = _reduce(edges)
    if edges in memo:
        return memo[edges]
    vs = _vertices(edges)
    found = False
    if len(vs) >= 5 and len(edges) >= 9:
        if _has_k5(edges, vs) or (len(vs) >= 6 and _has_k33(edges, vs)):
            found = True
        elif len(vs) > 5:
            for e in edges:
                keep, drop = sorted(e, key=repr)
                if has_kuratowski_minor(_contract(edges, keep, drop), memo):
                    found = True
                    break
    memo[edges] = found
    return found


def brute_force_planar(edges):
    return not has_kuratowski_minor(frozenset(frozenset(e) for e in edges if e[0] != e[1]))


# --------------------------------------------------------------------------- tests

class TestKnownNonPlanar(unittest.TestCase):
    def assertNonPlanar(self, edges, reason_part=None):
        planar, reason = pl.is_planar(edges)
        self.assertFalse(planar, reason)
        if reason_part:
            self.assertIn(reason_part, reason)

    def test_k5_by_edge_bound(self):
        self.assertNonPlanar(complete(5), "3V-6")

    def test_k33_by_triangle_free_bound(self):
        # 9 edges <= 3V-6 = 12, so only the triangle-free bound 2V-4 = 8 rejects it (TASK D21)
        self.assertNonPlanar(complete_bipartite(3, 3), "2V-4")

    def test_k6_k34_k44(self):
        for edges in (complete(6), complete_bipartite(3, 4), complete_bipartite(4, 4)):
            self.assertNonPlanar(edges)

    def test_k5_subdivisions_need_the_exact_test(self):
        self.assertNonPlanar(subdivide(complete(5), {0}), "no planar embedding")
        self.assertNonPlanar(subdivide(complete(5)), "no planar embedding")

    def test_k33_subdivisions_need_the_exact_test(self):
        self.assertNonPlanar(subdivide(complete_bipartite(3, 3), {0}), "no planar embedding")
        self.assertNonPlanar(subdivide(complete_bipartite(3, 3)), "no planar embedding")
        self.assertNonPlanar(subdivide(subdivide(complete_bipartite(3, 3), {2, 5})))

    def test_petersen(self):
        self.assertNonPlanar(PETERSEN, "no planar embedding")

    def test_petersen_minus_a_vertex_is_a_k33_subdivision(self):
        self.assertNonPlanar([e for e in PETERSEN if 0 not in e], "no planar embedding")

    def test_wagner_graph(self):
        self.assertNonPlanar(WAGNER)

    def test_non_planar_block_inside_a_planar_graph(self):
        edges = complete_bipartite(3, 3) + [("a0", "t1"), ("t1", "t2"), ("t2", "t3")] + cycle(5, 100)
        edges.append(("t3", 100))
        self.assertNonPlanar(edges)


class TestKnownPlanar(unittest.TestCase):
    def assertPlanar(self, edges):
        planar, reason = pl.is_planar(edges)
        self.assertTrue(planar, reason)

    def test_polyhedra(self):
        for edges in (CUBE, OCTAHEDRON, icosahedron(), DODECAHEDRON, complete(4)):
            self.assertPlanar(edges)

    def test_maximal_planar_reaches_the_bound(self):
        for seed in range(5):
            edges = apollonian(12, seed)
            v = 15
            self.assertEqual(len(edges), 3 * v - 6)
            self.assertPlanar(edges)

    def test_wheels_prisms_grids_trees(self):
        for n in range(3, 13):
            self.assertPlanar(wheel(n))
            self.assertPlanar(prism(n))
        for m, n in ((3, 3), (4, 5), (6, 6)):
            self.assertPlanar(grid(m, n))
        for seed in range(5):
            self.assertPlanar(random_tree(18, seed))

    def test_almost_kuratowski(self):
        self.assertPlanar(complete(5)[1:])
        self.assertPlanar(complete_bipartite(3, 3)[1:])
        self.assertPlanar(complete_bipartite(2, 7))

    def test_loops_parallel_edges_and_string_labels(self):
        edges = [("api", "db"), ("db", "api"), ("api", "api"), ("api", "cache"), ("cache", "db")]
        self.assertPlanar(edges)
        self.assertEqual(pl.simple_graph(edges), {"api": {"db", "cache"}, "db": {"api", "cache"},
                                                  "cache": {"api", "db"}})

    def test_empty_and_tiny(self):
        self.assertTrue(pl.is_planar([])[0])
        self.assertTrue(pl.is_planar([(1, 2)])[0])


class TestHelpers(unittest.TestCase):
    def test_triangle_free(self):
        self.assertTrue(pl.is_triangle_free(pl.simple_graph(complete_bipartite(3, 3))))
        self.assertFalse(pl.is_triangle_free(pl.simple_graph(complete(4))))

    def test_blocks_of_a_bowtie_and_a_bridge(self):
        edges = [(0, 1), (1, 2), (2, 0), (2, 3), (3, 4), (4, 2), (4, 5)]
        blocks = pl.biconnected_components(pl.simple_graph(edges))
        sizes = sorted(len(b) for b in blocks)
        self.assertEqual(sizes, [1, 3, 3])
        self.assertEqual(sum(sizes), len(edges))


class TestCrossCheckAgainstBruteForce(unittest.TestCase):
    """Every verdict equals a Kuratowski-minor search written independently in this file."""

    def _compare(self, edge_sets):
        for edges in edge_sets:
            planar, reason = pl.is_planar(edges)
            self.assertEqual(planar, brute_force_planar(edges), f"{edges}: {reason}")

    def test_brute_force_knows_the_kuratowski_graphs(self):
        self.assertFalse(brute_force_planar(complete(5)))
        self.assertFalse(brute_force_planar(complete_bipartite(3, 3)))
        self.assertTrue(brute_force_planar(OCTAHEDRON))

    def test_every_graph_on_at_most_6_vertices(self):
        for n in range(2, 7):
            pairs = complete(n)
            self._compare([[p for k, p in enumerate(pairs) if mask >> k & 1] for mask in range(1 << len(pairs))])

    def test_seeded_samples_on_7_and_8_vertices(self):
        rng = random.Random(108)
        pairs7, pairs8 = complete(7), complete(8)
        self._compare([rng.sample(pairs7, rng.randint(9, 15)) for _ in range(1500)])
        self._compare([rng.sample(pairs8, rng.randint(10, 18)) for _ in range(600)])


if __name__ == "__main__":
    unittest.main()
