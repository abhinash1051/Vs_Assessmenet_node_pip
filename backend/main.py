from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional, Dict, Set

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000", "http://localhost:3001", "http://127.0.0.1:3001"],
    allow_credentials=True,
    allow_methods=["*"]
    ,
    allow_headers=["*"]
)


class Node(BaseModel):
    id: str
    type: Optional[str] = None
    data: Optional[dict] = None


class Edge(BaseModel):
    source: str
    target: str
    # Include optional properties for completeness
    sourceHandle: Optional[str] = None
    targetHandle: Optional[str] = None


class Pipeline(BaseModel):
    nodes: List[Node]
    edges: List[Edge]


@app.get('/')
def read_root():
    return {'Ping': 'Pong'}


@app.post('/pipelines/parse')
def parse_pipeline(pipeline: Pipeline):
    num_nodes = len(pipeline.nodes)
    num_edges = len(pipeline.edges)

    # Build adjacency list
    adj: Dict[str, List[str]] = {}
    indeg: Dict[str, int] = {}
    node_ids: Set[str] = set(n.id for n in pipeline.nodes)
    for nid in node_ids:
        adj[nid] = []
        indeg[nid] = 0

    for e in pipeline.edges:
        # Only consider edges with valid nodes
        if e.source in node_ids and e.target in node_ids:
            adj[e.source].append(e.target)
            indeg[e.target] += 1

    # Kahn's algorithm to detect cycles
    queue = [n for n in node_ids if indeg[n] == 0]
    visited_count = 0
    while queue:
        cur = queue.pop(0)
        visited_count += 1
        for nxt in adj[cur]:
            indeg[nxt] -= 1
            if indeg[nxt] == 0:
                queue.append(nxt)

    is_dag = visited_count == len(node_ids)

    return {"num_nodes": num_nodes, "num_edges": num_edges, "is_dag": is_dag}


@app.get('/features')
def get_features():
    """Return feature flags for clients.

    Currently exposes a single flag to enable Claude Haiku 4.5 for all clients.
    """
    return {"claude_haiku_4_5": True}
