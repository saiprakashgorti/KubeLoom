"""
Fault injection module for KubeLoom.
"""

import random
from typing import List, Optional
from kubernetes import client
from kubernetes.client.rest import ApiException
from rich.console import Console

console = Console()


class FaultInjectionError(Exception):
    """Base exception for fault injection errors."""

    pass


def delete_pods(
    api_client: client.CoreV1Api, namespace: str, label_selector: str, num_pods: int = 1
) -> List[str]:
    """
    Delete a specified number of random pods matching the label selector.

    Args:
        api_client: Kubernetes API client
        namespace: Target namespace
        label_selector: Label selector to identify target pods
        num_pods: Number of pods to delete

    Returns:
        List of deleted pod names

    Raises:
        FaultInjectionError: If the fault injection fails
    """
    try:
        # List pods matching the selector
        pods = api_client.list_namespaced_pod(namespace, label_selector=label_selector)

        if not pods.items:
            raise FaultInjectionError(
                f"No pods found matching selector: {label_selector}"
            )

        # Select random pods to delete
        pods_to_delete = random.sample(pods.items, min(num_pods, len(pods.items)))
        deleted_pods = []

        for pod in pods_to_delete:
            try:
                api_client.delete_namespaced_pod(
                    name=pod.metadata.name, namespace=namespace
                )
                deleted_pods.append(pod.metadata.name)
                console.print(f"[yellow]Deleted pod: {pod.metadata.name}[/yellow]")
            except ApiException as e:
                console.print(
                    f"[red]Failed to delete pod {pod.metadata.name}: {str(e)}[/red]"
                )
                raise FaultInjectionError(f"Failed to delete pod: {str(e)}")

        return deleted_pods

    except ApiException as e:
        console.print(f"[red]Failed to list pods: {str(e)}[/red]")
        raise FaultInjectionError(f"Failed to list pods: {str(e)}")
