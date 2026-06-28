PHASE_TWO_GRAPH_ARCHITECTURE = """
User Query
  ↓
FastAPI /api/v1/chat
  ↓
Planner Node
  ↓
Router Node
  ↓
Conditional Branches
  ├─ documents placeholder
  ├─ web placeholder
  └─ sql placeholder
  ↓
Phase 2 Terminal
  ↓
Planned response
"""
