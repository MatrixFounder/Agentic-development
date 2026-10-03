#!/usr/bin/env python3
"""Exact planarity test for the simple undirected graph of a flowchart (TASK 108, D21).

A graph with no planar embedding has at least one edge crossing in every drawing, so no layout
engine and no edge order removes it; the author aggregates, splits or uses a table.

Method.
1. Build the simple undirected graph: self-loops and parallel edges are dropped, isolated
   vertices do not count.
2. Edge bounds (Euler): a planar graph with V >= 3 has E <= 3V - 6; a triangle-free planar graph
   has E <= 2V - 4. The second bound catches K3,3 (9 > 8); the first alone misses it (9 <= 12).
3. Exact test per biconnected component (a graph is planar iff each of its blocks is): the
   Demoucron–Malgrange–Pertuiset fragment/face algorithm. It embeds a cycle, then repeatedly
   embeds a path of a fragment into a face that holds all the fragment's attachment vertices,
   preferring a fragment with exactly one such face. A fragment with no such face proves the
   block non-planar, i.e. it holds a subdivision of K5 or K3,3 (Kuratowski).

Standard library only.
"""

from __future__ import annotations

from typing import Iterable, Optional


def simple_graph(edges: Iterable) -> dict:
    """Return the adjacency sets of the simple undirected graph of *edges* (pairs of vertices)."""
    adj: dict = {}
    for u, v in edges:
        if u == v:
            continue
        adj.setdefault(u, set()).add(v)
        adj.setdefault(v, set()).add(u)
    return adj


def _edge_count(adj: dict) -> int:
    return sum(len(n) for n in adj.values()) // 2


def _key(v) -> tuple:
    return (type(v).__name__, repr(v))


def is_triangle_free(adj: dict) -> bool:
    for u in adj:
        for v in adj[u]:
            if _key(u) < _key(v) and adj[u] & adj[v]:
                return False
    return True


def biconnected_components(adj: dict) -> list:
    """Return the blocks of the graph as lists of edges (Tarjan, iterative)."""
    index: dict = {}
    low: dict = {}
    counter = 0
    edge_stack: list = []
    blocks: list = []
    for root in sorted(adj, key=_key):
        if root in index:
            continue
        index[root] = low[root] = counter
        counter += 1
        stack = [(root, None, iter(sorted(adj[root], key=_key)))]
        while stack:
            v, parent, it = stack[-1]
            advanced = False
            for w in it:
                if w not in index:
                    edge_stack.append((v, w))
                    index[w] = low[w] = counter
                    counter += 1
                    stack.append((w, v, iter(sorted(adj[w], key=_key))))
                    advanced = True
                    break
                if w != parent and index[w] < index[v]:
                    edge_stack.append((v, w))
                    low[v] = min(low[v], index[w])
            if advanced:
                continue
            stack.pop()
            if stack:
                u = stack[-1][0]
                low[u] = min(low[u], low[v])
                if low[v] >= index[u]:
                    block = []
                    while edge_stack:
                        e = edge_stack.pop()
                        block.append(e)
                        if e == (u, v):
                            break
                    blocks.append(block)
    return blocks


def _find_cycle(adj: dict) -> Optional[list]:
    start = min(adj, key=_key)
    parent = {start: None}
    path = [start]
    pos = {start: 0}
    stack = [(start, iter(sorted(adj[start], key=_key)))]
    while stack:
        v, it = stack[-1]
        pushed = False
        for w in it:
            if w == parent[v]:
                continue
            if w in pos:
                return path[pos[w]:]
            if w not in parent:
                parent[w] = v
                pos[w] = len(path)
                path.append(w)
                stack.append((w, iter(sorted(adj[w], key=_key))))
                pushed = True
                break
        if not pushed:
            stack.pop()
            path.pop()
            del pos[v]
    return None


class _Fragment:
    __slots__ = ("attach", "inner", "edge")

    def __init__(self, attach: set, inner: set, edge: Optional[tuple] = None):
        self.attach = attach
        self.inner = inner
        self.edge = edge


def _fragments(adj: dict, emb_v: set, emb_e: set) -> list:
    frags = []
    seen = set()
    for u in sorted(emb_v, key=_key):
        for w in sorted(adj[u], key=_key):
            if w in emb_v:
                e = frozenset((u, w))
                if e not in emb_e and e not in seen:
                    seen.add(e)
                    frags.append(_Fragment({u, w}, set(), (u, w)))
    visited = set()
    for s in sorted(adj, key=_key):
        if s in emb_v or s in visited:
            continue
        inner, attach = set(), set()
        todo = [s]
        visited.add(s)
        while todo:
            x = todo.pop()
            inner.add(x)
            for y in adj[x]:
                if y in emb_v:
                    attach.add(y)
                elif y not in visited:
                    visited.add(y)
                    todo.append(y)
        frags.append(_Fragment(attach, inner))
    return frags


def _fragment_path(adj: dict, frag: _Fragment) -> list:
    """A path through the fragment between two distinct attachment vertices."""
    if frag.edge is not None:
        return list(frag.edge)
    attach = sorted(frag.attach, key=_key)
    a = attach[0]
    first = next(x for x in sorted(adj[a], key=_key) if x in frag.inner)
    prev = {first: None}
    queue = [first]
    head = 0
    while head < len(queue):
        x = queue[head]
        head += 1
        ends = [y for y in sorted(adj[x], key=_key) if y in frag.attach and y != a]
        if ends:
            path = [x]
            while prev[path[-1]] is not None:
                path.append(prev[path[-1]])
            path.reverse()
            return [a] + path + [ends[0]]
        for y in sorted(adj[x], key=_key):
            if y in frag.inner and y not in prev:
                prev[y] = x
                queue.append(y)
    raise ValueError("fragment with a single attachment: the block is not biconnected")


def _dmp_planar(adj: dict) -> bool:
    """Demoucron–Malgrange–Pertuiset on a biconnected simple graph with at least 3 vertices."""
    cycle = _find_cycle(adj)
    if cycle is None:
        return True
    emb_v = set(cycle)
    emb_e = {frozenset((cycle[k], cycle[(k + 1) % len(cycle)])) for k in range(len(cycle))}
    faces = [list(cycle), list(reversed(cycle))]
    total = _edge_count(adj)
    while len(emb_e) < total:
        best = None
        for frag in _fragments(adj, emb_v, emb_e):
            admissible = [k for k, face in enumerate(faces) if frag.attach <= set(face)]
            if not admissible:
                return False
            if best is None or len(admissible) < len(best[1]):
                best = (frag, admissible)
                if len(admissible) == 1:
                    break
        frag, admissible = best
        path = _fragment_path(adj, frag)
        face = faces[admissible[0]]
        i = face.index(path[0])
        rotated = face[i:] + face[:i]
        j = rotated.index(path[-1])
        interior = path[1:-1]
        faces[admissible[0]] = rotated[:j + 1] + interior[::-1]
        faces.append(rotated[j:] + [rotated[0]] + interior)
        emb_v.update(interior)
        emb_e.update(frozenset((path[k], path[k + 1])) for k in range(len(path) - 1))
    return True


def is_planar(edges) -> tuple:
    """Return `(planar, reason)` for the simple undirected graph of *edges*.

    *edges* is an iterable of vertex pairs; vertices are any hashable values. Self-loops and
    repeated pairs are ignored. `reason` names the test that decided.
    """
    adj = simple_graph(edges)
    v, e = len(adj), _edge_count(adj)
    if v < 5 or e < 9:
        return True, f"V={v}, E={e}: too small to hold a subdivision of K5 or K3,3"
    if e > 3 * v - 6:
        return False, f"E={e} > 3V-6={3 * v - 6} for V={v}"
    if is_triangle_free(adj) and e > 2 * v - 4:
        return False, f"triangle-free with E={e} > 2V-4={2 * v - 4} for V={v}"
    for block in biconnected_components(adj):
        sub = simple_graph(block)
        bv, be = len(sub), _edge_count(sub)
        if bv < 5 or be < 9:
            continue
        if be > 3 * bv - 6:
            return False, f"a block with E={be} > 3V-6={3 * bv - 6} for V={bv}"
        if not _dmp_planar(sub):
            return False, (f"a block with V={bv}, E={be} has no planar embedding: it holds a "
                           "subdivision of K5 or K3,3")
    return True, f"planar (V={v}, E={e})"
