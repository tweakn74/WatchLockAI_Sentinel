import subprocess
import time
from rich.console import Console
from rich.live import Live
from rich.spinner import Spinner

console = Console()

# Max seconds to wait before triggering timeout
OLLAMA_TIMEOUT = 60


def stream_ollama(prompt):
    """Spawn Ollama subprocess and stream output line by line."""
    try:
        console.print("[yellow][DEBUG] Starting Ollama subprocess...[/yellow]")

        process = subprocess.Popen(
            ["ollama", "run", "mistral"],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            bufsize=1,
        )

        # Send prompt to Ollama
        process.stdin.write(prompt)
        process.stdin.close()

        output_lines = []
        start_time = time.time()

        with Live(
            Spinner("dots", text="Calling Mistral via Ollama..."), refresh_per_second=4
        ):
            while True:
                line = process.stdout.readline()
                if line:
                    console.print("[cyan][Ollama]:[/cyan]", line.strip())
                    output_lines.append(line.strip())
                elif process.poll() is not None:
                    break

                if time.time() - start_time > OLLAMA_TIMEOUT:
                    process.kill()
                    raise TimeoutError("Ollama response timed out after 60 seconds")

        stderr = process.stderr.read()
        if stderr:
            console.print(f"[red][WARN] Ollama stderr:[/red] {stderr.strip()}")

        return output_lines

    except TimeoutError as e:
        console.print(f"[red][FAIL] Timeout:[/red] {e}")
        return []

    except Exception as e:
        console.print(f"[red][FAIL] Unexpected failure:[/red] {e}")
        return []


def plan_tasks(goal: str):
    prompt = f"""
You are an autonomous AI software engineer.

Given this goal: "{goal}", generate a clear, step-by-step dev plan (3-6 items), each as a single sentence.

Only output the plan list.
"""
    console.print("\n:brain: [bold cyan]Thinking about your request...[/bold cyan]")
    console.print("[dim]Internal: Preparing high-level plan based on prompt[/dim]")
    console.print(
        "\n:brain: [bold magenta]Generating development plan...[/bold magenta]"
    )

    lines = stream_ollama(prompt)
    steps = [line.strip("-*1234567890. ").strip() for line in lines if line.strip()]

    if not steps:
        console.print("[yellow][WARN] Using fallback planning...[/yellow]")
        return fallback(goal)

    return steps


def fallback(goal):
    return [
        f"Understand the goal: {goal}",
        "Create folder structure",
        "Write starter code",
        "Write README and install instructions",
        "Test the application locally",
    ]
