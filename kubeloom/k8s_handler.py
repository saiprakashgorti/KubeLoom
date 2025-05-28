"""
Kubernetes cluster interaction module for KubeLoom.
"""

from typing import List, Optional
from kubernetes import client, config
from kubernetes.client.rest import ApiException
from rich.console import Console

console = Console()


class KubernetesHandler:
    def __init__(self, kubeconfig_path: Optional[str] = None):
        """
        Initialize the Kubernetes client.

        Args:
            kubeconfig_path: Optional path to kubeconfig file. If None, uses default.
        """
        try:
            if kubeconfig_path:
                config.load_kube_config(kubeconfig_path)
            else:
                config.load_kube_config()

            self.v1 = client.CoreV1Api()
            self.apps_v1 = client.AppsV1Api()
            console.print("[green]Successfully connected to Kubernetes cluster[/green]")
        except Exception as e:
            console.print(
                f"[red]Failed to initialize Kubernetes client: {str(e)}[/red]"
            )
            raise

    def list_deployments(self, namespace: str = "default") -> List[dict]:
        """
        List all deployments in the specified namespace.

        Args:
            namespace: The namespace to list deployments from.

        Returns:
            List of deployment information dictionaries.
        """
        try:
            deployments = self.apps_v1.list_namespaced_deployment(namespace)
            return [
                {
                    "name": dep.metadata.name,
                    "replicas": dep.spec.replicas,
                    "available_replicas": dep.status.available_replicas,
                    "ready_replicas": dep.status.ready_replicas,
                }
                for dep in deployments.items
            ]
        except ApiException as e:
            console.print(f"[red]Failed to list deployments: {str(e)}[/red]")
            raise

    def list_pods(
        self, namespace: str = "default", label_selector: Optional[str] = None
    ) -> List[dict]:
        """
        List pods in the specified namespace, optionally filtered by label selector.

        Args:
            namespace: The namespace to list pods from.
            label_selector: Optional label selector to filter pods.

        Returns:
            List of pod information dictionaries.
        """
        try:
            pods = self.v1.list_namespaced_pod(namespace, label_selector=label_selector)
            return [
                {
                    "name": pod.metadata.name,
                    "phase": pod.status.phase,
                    "ip": pod.status.pod_ip,
                    "node": pod.spec.node_name,
                }
                for pod in pods.items
            ]
        except ApiException as e:
            console.print(f"[red]Failed to list pods: {str(e)}[/red]")
            raise
