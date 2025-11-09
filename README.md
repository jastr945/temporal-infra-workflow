# VM Factories with Temporal

VM Factories with Temporal is a workflow that allows your teams to provision EC2 instances on AWS with SSH access reliably. Anyone in your organization who needs a virtual machine can use this workflow. If provisioning fails, Temporal ensures the workflow retries — making it a workflow that never fails.

> **Note:** Terraform is used for provisioning the infrastructure. The typical Terraform stages - `init`, `plan`, `apply`, and `output` - are executed as activities inside the Temporal workflow.

## Features

- Automatic EC2 provisioning with SSH access
- Reliable workflow execution with Temporal

The following infrastructure will be provisioned in AWS with this workflow:
| Resource | Purpose |
|----------|---------|
| AWS VPC | Isolated virtual network providing subnetting, routing, and security boundaries. |
| Public Subnets | Subnets in multiple availability zones for high availability; host public-facing resources. |
| Internet Gateway | Enables internet connectivity for resources in public subnets. |
| Route Tables | Routes traffic between subnets and the internet; default route table manages default networking. |
| Route Table Associations | Associates subnets with route tables to control network traffic flow. |
| Default Network ACL | Provides network-level security rules for all subnets in the VPC. |
| Default Security Group | Instance-level security controls for resources in the VPC. |
| Custom Security Group for SSH | Allows SSH access (port 22) from anywhere for administrative purposes. |
| EC2 Instance | Virtual server (t3.micro) deployed in a public subnet for running applications or workflows. |
| EC2 Key Pair | SSH key used to securely connect to the EC2 instance. |
| Local PEM File | Stores the private key locally for SSH access to the EC2 instance. |
| TLS Private Key | Cryptographic key generation for secure access and potential use in other cryptographic operations. |


## Prerequisites

- Python 3.8+
- Terraform 1.13+
- AWS account access + configured AWS credentials. Terraform requires an AWS Access Key ID and AWS Secret Access Key to provision resources. Make sure these credentials are configured in your environment.


## Getting Started (Local Development)

1. Clone the repository and navigate to the workflow directory:
```sh
cd temporal-infra-workflow
```
2. Create a virtual environment and activate it:
```sh
python3 -m venv env
source env/bin/activate
```
3. Install the Temporal Python SDK:
```sh
ppip install temporalio
```
4. Install the Temporal CLI (see [documntation for other operating systems](https://docs.temporal.io/develop/python/set-up-your-local-python#install-temporal-cli))
```sh
# macOS
brew install temporal
```
5. Start the Temporal development server:
```sh
temporal server start-dev
```
6. Run the worker in a new terminal:
```sh
source env/bin/activate
python3 worker.py
```
7. Trigger the workflow in another terminal:
```sh
source env/bin/activate
python3 starter.py
```
8. Monitor workflow progress in the Temporal Web UI.

## Cleanup

To destroy provisioned resources:
```sh
python3 destroyer.py
```