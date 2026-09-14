"""
Small helper so every agent records a consistent trace entry
(name, timing, input/output summary) without repeating boilerplate.
"""
import time
from contextlib import contextmanager

from app.agents.state import SupportGraphState


@contextmanager
def trace_step(state: SupportGraphState, agent_name: str, input_summary: str):
    start = time.perf_counter()
    result_holder: dict[str, str] = {"output_summary": ""}
    try:
        yield result_holder
    finally:
        duration_ms = int((time.perf_counter() - start) * 1000)
        trace = state.setdefault("agent_trace", [])
        trace.append(
            {
                "agent_name": agent_name,
                "step_order": len(trace) + 1,
                "input_summary": input_summary[:500],
                "output_summary": result_holder["output_summary"][:500],
                "duration_ms": duration_ms,
            }
        )
