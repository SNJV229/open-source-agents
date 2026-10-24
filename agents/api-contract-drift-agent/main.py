import argparse
import sys
from pathlib import Path
from dotenv import load_dotenv
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from analyzer import analyze_drift
from schemas import DriftSeverity
from guardrails import validate_file_path, GuardrailValidationError

load_dotenv()
console = Console()


def main():
    parser = argparse.ArgumentParser(
        description="API Contract Drift Agent: Detect schema mismatches with built-in security guardrails."
    )
    parser.add_argument(
        "--code",
        type=str,
        default="samples/UserController.java",
        help="Path to backend controller file",
    )
    parser.add_argument(
        "--spec",
        type=str,
        default="samples/openapi.json",
        help="Path to OpenAPI/Swagger spec file",
    )
    parser.add_argument(
        "--output-md",
        type=str,
        default="drift_report.md",
        help="Markdown file path to save report",
    )

    args = parser.parse_args()

    try:
        code_path = validate_file_path(Path(args.code))
        spec_path = validate_file_path(Path(args.spec))
    except GuardrailValidationError as gv_err:
        console.print(Panel(f"[bold red]Input Guardrail Violation:[/bold red]\n{gv_err}", title="Security Guardrail", border_style="red"))
        sys.exit(1)

    console.print(
        Panel.fit(
            f"[bold cyan]API Contract Drift Agent (Guarded)[/bold cyan]\n"
            f"Code: [dim]{code_path}[/dim] | Spec: [dim]{spec_path}[/dim]\n"
            f"Guardrails: [green]Active (Secret Scanner, Input Bounder, Patch Validator)[/green]",
            border_style="cyan",
        )
    )

    code_content = code_path.read_text(encoding="utf-8")
    spec_content = spec_path.read_text(encoding="utf-8")

    with console.status("[bold green]Executing guarded drift analysis with Gemini 3.8 Flash..."):
        try:
            report = analyze_drift(code_content, spec_content)
        except GuardrailValidationError as gv_err:
            console.print(Panel(f"[bold red]Execution Halted by Guardrail:[/bold red]\n{gv_err}", title="Security Triggered", border_style="red"))
            sys.exit(1)
        except Exception as e:
            console.print(f"[bold red]Runtime Error:[/bold red] {e}")
            sys.exit(1)

    status_color = "red" if report.has_breaking_changes else "green"
    status_label = "CRITICAL DRIFT DETECTED" if report.has_breaking_changes else "CONTRACT COMPLIANT"
    console.print(
        Panel(
            f"[bold {status_color}]{status_label}[/bold {status_color}]\n\n{report.summary}",
            title="Analysis Summary",
            border_style=status_color,
        )
    )

    table = Table(title="Detected Contract Drift Items", show_header=True, header_style="bold magenta")
    table.add_column("Severity", width=12)
    table.add_column("Endpoint", width=22)
    table.add_column("Type", width=20)
    table.add_column("Spec vs Code", width=35)
    table.add_column("Remediation", width=30)

    for item in report.drift_items:
        sev_color = "red" if item.severity == DriftSeverity.BREAKING else ("yellow" if item.severity == DriftSeverity.WARNING else "blue")
        table.add_row(
            f"[{sev_color}]{item.severity.value}[/{sev_color}]",
            item.endpoint,
            item.drift_type.value,
            f"[dim]Spec:[/dim] {item.spec_state}\n[dim]Code:[/dim] {item.code_state}",
            item.remediation,
        )

    console.print(table)

    md_content = f"# API Contract Drift Report\n\n**Status:** {'BREAKING CHANGES FOUND' if report.has_breaking_changes else 'COMPLIANT'}\n\n"
    md_content += f"## Summary\n{report.summary}\n\n## Drift Occurrences\n"
    for item in report.drift_items:
        md_content += f"- **[{item.severity.value}] `{item.endpoint}` - `{item.drift_type.value}`**\n"
        md_content += f"  - Spec: {item.spec_state}\n"
        md_content += f"  - Code: {item.code_state}\n"
        md_content += f"  - Remediation: {item.remediation}\n\n"

    if report.suggested_spec_patch:
        md_content += f"## Suggested OpenAPI Spec Patch\n```json\n{report.suggested_spec_patch}\n```\n"

    Path(args.output_md).write_text(md_content, encoding="utf-8")
    console.print(f"\n[bold green]✓[/bold green] Full Markdown report generated: [underline]{args.output_md}[/underline]")


if __name__ == "__main__":
    main()