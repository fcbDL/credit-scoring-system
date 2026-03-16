"""LangGraph state machine for multi-agent credit scoring workflow.

This module defines the LangGraph workflow that orchestrates:
1. Numeric analysis agent (XGBoost + rules)
2. Semantic analysis agent (text analysis + RAG)
3. Supervisor agent (decision making + conflict handling)
"""

from functools import partial
from typing import Literal

from langgraph.graph import StateGraph, END

from .state import CreditState
from .agents import NumericAgent, SemanticAgent, SupervisorAgent


def create_credit_graph(
    numeric_agent: NumericAgent,
    semantic_agent: SemanticAgent,
    supervisor_agent: SupervisorAgent,
) -> StateGraph:
    """Create LangGraph workflow for credit scoring.

    Args:
        numeric_agent: Agent for numeric analysis
        semantic_agent: Agent for semantic analysis
        supervisor_agent: Supervisor agent for orchestration

    Returns:
        Compiled LangGraph StateGraph
    """

    # Create the graph
    workflow = StateGraph(CreditState)

    # Add nodes with partial to bind agent
    workflow.add_node("supervisor", partial(supervisor_node, agent=supervisor_agent))
    workflow.add_node("numeric", partial(numeric_node, agent=numeric_agent))
    workflow.add_node("semantic", partial(semantic_node, agent=semantic_agent))
    workflow.add_node("audit", partial(audit_node, agent=supervisor_agent))
    workflow.add_node("decision", partial(decision_node, agent=supervisor_agent))

    # Set entry point
    workflow.set_entry_point("supervisor")

    # Define edges
    workflow.add_edge("supervisor", "numeric")
    workflow.add_edge("numeric", "semantic")
    workflow.add_edge("semantic", "audit")

    # Conditional edge: check if conflict detected
    workflow.add_conditional_edges(
        "audit",
        should_audit,
        {
            "continue": "decision",
            "audit_again": "audit",
        },
    )

    # Edge to END
    workflow.add_edge("decision", END)

    # Compile
    return workflow.compile()


# Node functions
async def supervisor_node(state: CreditState, agent: SupervisorAgent) -> CreditState:
    """Supervisor node: decides which agents to invoke."""
    # For now, invoke both agents in parallel
    state["trace"].append({
        "node": "supervisor",
        "action": "plan",
        "plan": "Invoke numeric and semantic agents",
    })
    return state


async def numeric_node(state: CreditState, agent: NumericAgent) -> CreditState:
    """Numeric analysis node."""
    return await agent.run(state)


async def semantic_node(state: CreditState, agent: SemanticAgent) -> CreditState:
    """Semantic analysis node."""
    return await agent.run(state)


async def audit_node(state: CreditState, agent: SupervisorAgent) -> CreditState:
    """Audit node: handles conflict detection and resolution.

    If conflict is detected, this node initiates multi-round
    debate/resolution process.
    """
    if state.get("conflict_detected"):
        # Increment audit iteration
        state["audit_iterations"] = state.get("audit_iterations", 0) + 1

        # Max 3 audit rounds
        if state["audit_iterations"] >= 3:
            state["trace"].append({
                "node": "audit",
                "action": "max_iterations_reached",
                "iterations": state["audit_iterations"],
            })
            # Force decision even with conflict
            return state

        # Trigger conflict resolution (multi-round debate)
        state["trace"].append({
            "node": "audit",
            "action": "conflict_resolution_start",
            "iteration": state["audit_iterations"],
            "conflict": state.get("conflict_details"),
        })

        # TODO: Implement multi-round debate logic here
        # This would involve re-invoking the relevant agents
        # with conflict-specific prompts

    return state


async def decision_node(state: CreditState, agent: SupervisorAgent) -> CreditState:
    """Decision node: generates final decision."""
    return await agent.run(state)


# Conditional edge function
def should_audit(state: CreditState) -> Literal["continue", "audit_again"]:
    """Determine if audit should continue or proceed to decision.

    Returns:
        "continue" - Proceed to decision
        "audit_again" - Run audit again (for multi-round resolution)
    """
    if not state.get("conflict_detected"):
        return "continue"

    # Check if max iterations reached
    if state.get("audit_iterations", 0) >= 3:
        return "continue"

    # Check if audit has converged (could add convergence check)
    # For now, proceed to decision after one audit round
    return "continue"


# Helper to run the graph
async def run_credit_workflow(
    graph: StateGraph,
    initial_state: CreditState,
) -> CreditState:
    """Run the credit scoring workflow.

    Args:
        graph: Compiled LangGraph
        initial_state: Initial state with user input

    Returns:
        Final state with decision
    """
    # Initialize state
    if "trace" not in initial_state:
        initial_state["trace"] = []
    if "errors" not in initial_state:
        initial_state["errors"] = []
    if "audit_iterations" not in initial_state:
        initial_state["audit_iterations"] = 0

    # Invoke the graph
    result = await graph.ainvoke(initial_state)

    return result
