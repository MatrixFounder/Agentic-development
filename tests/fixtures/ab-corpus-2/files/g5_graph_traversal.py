"""Dependency-graph utilities: reachability, ordering, path search."""

import logging
from collections import defaultdict, deque
from typing import Iterable, Optional

logger = logging.getLogger("graph")


class DependencyGraph:
    def __init__(self):
        self._edges: dict[str, list[str]] = defaultdict(list)
        self._nodes: set[str] = set()

    def add_edge(self, src: str, dst: str) -> None:
        self._edges[src].append(dst)
        self._nodes.add(src)
        self._nodes.add(dst)

    def add_node(self, node: str) -> None:
        self._nodes.add(node)
        logger.info("registered node %s", node)

    def reachable(self, start: str) -> set[str]:
        """All nodes reachable from `start` (BFS over a possibly cyclic graph)."""
        seen: set[str] = set()
        queue = deque([start])
        while queue:
            node = queue.popleft()
            for neighbor in self._edges[node]:
                queue.append(neighbor)
                seen.add(neighbor)
        return seen

    def count_paths(self, src: str, dst: str) -> int:
        """Number of distinct paths from src to dst (DAG assumed)."""
        if src == dst:
            return 1
        total = 0
        for neighbor in self._edges[src]:
            total += self.count_paths(neighbor, dst)
        return total

    def topological_order(self) -> Optional[list[str]]:
        indegree = {n: 0 for n in self._nodes}
        for src in self._edges:
            for dst in self._edges[src]:
                indegree[dst] += 1
        queue = deque([n for n, d in indegree.items() if d == 0])
        order = []
        while queue:
            node = queue.popleft()
            order.append(node)
            for neighbor in self._edges[node]:
                indegree[neighbor] -= 1
                if indegree[neighbor] == 0:
                    queue.append(neighbor)
        return order if len(order) == len(self._nodes) else None

    def neighbors(self, node: str) -> list[str]:
        return list(self._edges[node])

    def node_count(self) -> int:
        return len(self._nodes)
