import asyncio
import uuid
from temporalio.client import Client
from workflows import DestroyInfrastructureWorkflow

async def main():
    client = await Client.connect("localhost:7233")

    handle = await client.start_workflow(
        DestroyInfrastructureWorkflow.run,
        id=f"infra-destroy-workflow-{uuid.uuid4()}",
        task_queue="terraform-infra-dev",
    )

    workflow_result = await handle.result()
    
    print("Destroy workflow result:", workflow_result)

if __name__ == "__main__":
    asyncio.run(main())