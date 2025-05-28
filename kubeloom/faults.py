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


def evict_pods(
    api_client: client.CoreV1Api, namespace: str, label_selector: str, num_pods: int = 1
) -> List[str]:
    """
    Evict a specified number of random pods matching the label selector.
    """
    try:
        pods = api_client.list_namespaced_pod(namespace, label_selector=label_selector)
        if not pods.items:
            raise FaultInjectionError(
                f"No pods found matching selector: {label_selector}"
            )

        pods_to_evict = random.sample(pods.items, min(num_pods, len(pods.items)))
        evicted_pods = []

        for pod in pods_to_evict:
            eviction = client.V1Eviction(
                metadata=client.V1ObjectMeta(
                    name=pod.metadata.name, namespace=namespace
                )
            )
            try:
                api_client.create_namespaced_pod_eviction(
                    name=pod.metadata.name, namespace=namespace, body=eviction
                )
                evicted_pods.append(pod.metadata.name)
                console.print(f"[yellow]Evicted pod: {pod.metadata.name}[/yellow]")
            except ApiException as e:
                console.print(
                    f"[red]Failed to evict pod {pod.metadata.name}: {str(e)}[/red]"
                )
                raise FaultInjectionError(f"Failed to evict pod: {str(e)}")

        return evicted_pods

    except ApiException as e:
        console.print(f"[red]Failed to list pods: {str(e)}[/red]")
        raise FaultInjectionError(f"Failed to list pods: {str(e)}")


def restart_pods(
    api_client: client.CoreV1Api, namespace: str, label_selector: str, num_pods: int = 1
) -> List[str]:
    """
    Restart a specified number of random pods by deleting them (Kubernetes will recreate them).
    """
    # This is functionally similar to delete_pods, but logs as a restart
    try:
        pods = api_client.list_namespaced_pod(namespace, label_selector=label_selector)
        if not pods.items:
            raise FaultInjectionError(
                f"No pods found matching selector: {label_selector}"
            )

        pods_to_restart = random.sample(pods.items, min(num_pods, len(pods.items)))
        restarted_pods = []

        for pod in pods_to_restart:
            try:
                api_client.delete_namespaced_pod(
                    name=pod.metadata.name, namespace=namespace
                )
                restarted_pods.append(pod.metadata.name)
                console.print(f"[yellow]Restarted pod: {pod.metadata.name}[/yellow]")
            except ApiException as e:
                console.print(
                    f"[red]Failed to restart pod {pod.metadata.name}: {str(e)}[/red]"
                )
                raise FaultInjectionError(f"Failed to restart pod: {str(e)}")

        return restarted_pods

    except ApiException as e:
        console.print(f"[red]Failed to list pods: {str(e)}[/red]")
        raise FaultInjectionError(f"Failed to list pods: {str(e)}")


# Note: CPU/Network stress would require a sidecar or privileged container, or using tools like chaos-mesh or kube-monkey.
# For MVP, these are the basic faults you can implement with the Kubernetes API alone.
