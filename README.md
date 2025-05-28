# KubeLoom

KubeLoom is a Python-based Chaos Engineering CLI tool for Kubernetes. It allows you to proactively test and improve the resilience of your microservices by automating fault injection experiments (starting with pod deletion) on your Kubernetes cluster.

## Features

- Connects to any Kubernetes cluster using your kubeconfig.
- Lists deployments in any namespace.
- Defines and runs chaos experiments (e.g., randomly deletes pods from a deployment).
- Extensible: Easily add new types of chaos experiments.
- User-friendly CLI with rich output.

## Requirements

- Python 3.8+
- Access to a Kubernetes cluster and a valid kubeconfig file (default: `~/.kube/config`)
- (Optional) [Minikube](https://minikube.sigs.k8s.io/docs/) or [Docker Desktop](https://www.docker.com/products/docker-desktop/) for local clusters

## Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/kubeloom.git
cd kubeloom

# Install dependencies
pip install -r requirements.txt

# Install KubeLoom in development mode
pip install -e .
```

## Usage

### List Deployments

```bash
kubeloom list-deployments --namespace default
```
- Lists all deployments in the `default` namespace.
- Add `--kubeconfig /path/to/your/kubeconfig` if your kubeconfig is not in the default location.

### Run a Pod Deletion Experiment

```bash
kubeloom run-experiment deployment/my-app --namespace default --fault pod-deletion --pods 2
```
- Randomly deletes 2 pods from the deployment `my-app` in the `default` namespace.
- You can change the number of pods, namespace, and target deployment.
- Add `--kubeconfig /path/to/your/kubeconfig` if needed.

### Get Help

```bash
kubeloom --help
kubeloom list-deployments --help
kubeloom run-experiment --help
```

## Example Workflow

1. **List deployments** to find your target:
   ```bash
   kubeloom list-deployments --namespace my-namespace
   ```
2. **Run a chaos experiment**:
   ```bash
   kubeloom run-experiment deployment/my-app --namespace my-namespace --fault pod-deletion --pods 1
   ```
3. **Observe**:
   - KubeLoom will log which pods were deleted.
   - Your deployment should automatically recreate the pods (if configured correctly).
   - Use this to test your system's resilience and alerting.

## Extending KubeLoom

- Add new fault types (e.g., network delay, CPU stress) by implementing new functions in `faults.py` and updating the CLI.
- Add more resource types (e.g., StatefulSets) by extending the experiment and handler logic.

## Development

This project is under active development. The initial version focuses on core functionality with plans to expand features in future iterations.
