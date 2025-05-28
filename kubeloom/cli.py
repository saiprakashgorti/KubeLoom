"""
Command-line interface for KubeLoom.
"""

import typer
from typing import Optional
from rich.console import Console
from rich.table import Table

from .k8s_handler import KubernetesHandler
from .experiment import Experiment, FaultType

app = typer.Typer(help="KubeLoom - Kubernetes Chaos Engineering Platform")
console = Console()


@app.command()
def list_deployments(
    namespace: str = typer.Option(
        "default", "--namespace", "-n", help="Kubernetes namespace to target"
    ),
    kubeconfig: Optional[str] = typer.Option(
        None, "--kubeconfig", "-k", help="Path to kubeconfig file"
    ),
):
    """List all deployments in the specified namespace."""
    try:
        k8s = KubernetesHandler(kubeconfig_path=kubeconfig)
        deployments = k8s.list_deployments(namespace)

        table = Table(title=f"Deployments in namespace: {namespace}")
        table.add_column("Name", style="cyan")
        table.add_column("Replicas", style="green")
        table.add_column("Available", style="green")
        table.add_column("Ready", style="green")

        for dep in deployments:
            table.add_row(
                dep["name"],
                str(dep["replicas"]),
                str(dep["available_replicas"]),
                str(dep["ready_replicas"]),
            )

        console.print(table)
    except Exception as e:
        console.print(f"[red]Error: {str(e)}[/red]")
        raise typer.Exit(1)


@app.command()
def run_experiment(
    target: str = typer.Argument(
        ..., help="Target resource (e.g., 'deployment/my-app')"
    ),
    namespace: str = typer.Option(
        "default", "--namespace", "-n", help="Kubernetes namespace"
    ),
    fault: FaultType = typer.Option(
        ..., "--fault", "-f", help="Type of fault to inject"
    ),
    pods: int = typer.Option(
        1, "--pods", "-p", help="Number of pods to affect (for pod-related faults)"
    ),
    kubeconfig: Optional[str] = typer.Option(
        None, "--kubeconfig", "-k", help="Path to kubeconfig file"
    ),
):
    """Run a chaos experiment."""
    try:
        # Parse target
        kind, name = target.split("/")

        # Create experiment
        experiment = Experiment(
            target_kind=kind,
            target_name=name,
            namespace=namespace,
            fault_type=fault,
            fault_params={"num_pods": pods},
        )

        # Initialize Kubernetes client
        k8s = KubernetesHandler(kubeconfig_path=kubeconfig)

        # Execute experiment based on fault type
        if fault == FaultType.POD_DELETION:
            from .faults import delete_pods

            # Get deployment to find its selector
            dep_list = k8s.apps_v1.list_namespaced_deployment(namespace)
            dep = next((d for d in dep_list.items if d.metadata.name == name), None)
            if not dep:
                console.print(
                    f"[red]Deployment '{name}' not found in namespace '{namespace}'.[/red]"
                )
                raise typer.Exit(1)
            selector = dep.spec.selector.match_labels
            label_selector = ",".join(f"{k}={v}" for k, v in selector.items())

            deleted = delete_pods(k8s.v1, namespace, label_selector, pods)
            console.print(
                f"[green]Successfully deleted pods: {', '.join(deleted)}[/green]"
            )
        else:
            console.print(f"[red]Unsupported fault type: {fault}[/red]")
            raise typer.Exit(1)

    except Exception as e:
        console.print(f"[red]Error: {str(e)}[/red]")
        raise typer.Exit(1)


def main():
    app()
