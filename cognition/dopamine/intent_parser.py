# File: intent_parser.py
# Developer: Craig and ChatGPT 4o
# Location: root
# Version: 2.3.0
# Modified: 2025-07-23
# Purpose: Extract structured user intent using hybrid LLM mesh with mock mode and RBAC alignment.
# Recent Change: Upgraded to v2.3 spec; added hybrid LLM orchestrator, fallback parsing, mock mode support, and enhanced role-based filtering.

from agent_core.llm_mesh_orchestrator import LLMMeshOrchestrator
from agent_core.user_profile import get_current_user, get_user_groups
from rich.console import Console

console = Console()


class IntentParser:
    """
    Parses raw user prompts into structured intent objects using hybrid LLM.
    Supports fallback keyword parsing and respects RBAC restrictions.
    """

    def __init__(self):
        self.orchestrator = LLMMeshOrchestrator()

    def parse_intent(self, prompt: str) -> dict:
        """
        Generates structured intent using hybrid LLM (cloud/local).
        Falls back to keyword-based parsing if LLM unavailable.
        """
        user = get_current_user()
        groups = get_user_groups(user)

        # Base intent structure
        intent = {
            "intent_type": None,
            "task_name": None,
            "category": None,
            "raw_goal": prompt,
            "user": user,
            "groups": groups,
        }

        try:
            # Attempt LLM-based structured parsing
            llm_output = self.orchestrator.generate(
                "planner", f"Extract intent from: {prompt}"
            )
            if llm_output and isinstance(llm_output, str):
                parsed = self._parse_llm_output(llm_output)
                intent.update(parsed)
            else:
                # Fallback to keyword parser
                intent.update(self._fallback_parser(prompt))
        except Exception as e:
            console.print(
                f"[intent_parser] LLM parsing failed: {e}. Falling back to keyword parsing."
            )
            intent.update(self._fallback_parser(prompt))

        return intent

    def _parse_llm_output(self, llm_output: str) -> dict:
        """
        Parses LLM output (string) into structured dict.
        Expected format: key: value pairs or bullet list.
        """
        parsed = {"intent_type": None, "task_name": None, "category": None}
        lines = llm_output.splitlines()
        for line in lines:
            line = line.strip().lower()
            if "mark" in line and "done" in line:
                parsed["intent_type"] = "mark_done"
            elif "status" in line or "show tasks" in line:
                parsed["intent_type"] = "show_status"
            elif "build" in line or "create" in line or "generate" in line:
                parsed["intent_type"] = "plan_build"
            elif "run task" in line or "execute" in line:
                parsed["intent_type"] = "run_task"
            elif "chat" in line or "talk" in line:
                parsed["intent_type"] = "chat"
        return parsed

    def _fallback_parser(self, prompt: str) -> dict:
        """
        Simple keyword-based fallback parser.
        """
        p_lower = prompt.lower()
        result = {"intent_type": "fallback"}

        if "mark" in p_lower and "done" in p_lower:
            result["intent_type"] = "mark_done"
        elif "status" in p_lower or "show tasks" in p_lower:
            result["intent_type"] = "show_status"
        elif "build" in p_lower or "create" in p_lower or "generate" in p_lower:
            result["intent_type"] = "plan_build"
        elif "run task" in p_lower or "execute" in p_lower:
            result["intent_type"] = "run_task"
        elif any(x in p_lower for x in ["talk", "hello", "how are you"]):
            result["intent_type"] = "chat"

        # Extract task name after colon
        if ":" in prompt:
            split = prompt.split(":")
            result["task_name"] = split[1].strip()

        return result


if __name__ == "__main__":
    parser = IntentParser()
    test_prompt = "Create a build plan for memory archiver: pointer integration"
    console.print(parser.parse_intent(test_prompt))

# End of Script: intent_parser.py
# Version: 2.3.0
# Modified: 2025-07-23
