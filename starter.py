import asyncio
import uuid
from temporalio.client import Client
from workflows import InfrastructureWorkflow

async def main():
    client = await Client.connect("localhost:7233")
    result = await client.execute_workflow(
        InfrastructureWorkflow.run,
        id=f"infrastructure-workflow-{uuid.uuid4()}",
        task_queue="terraform-infra-dev",
    )
    print("Workflow result:", result)

if __name__ == "__main__":
    asyncio.run(main())