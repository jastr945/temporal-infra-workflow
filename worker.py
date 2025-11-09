import asyncio
from temporalio.client import Client
from temporalio.worker import Worker
from workflows import InfrastructureWorkflow
from activities import terraform_cmd_init, terraform_cmd_plan, terraform_cmd_apply, terraform_cmd_output


async def main():
    client = await Client.connect("localhost:7233")
    worker = Worker(
        client,
        task_queue="my-task-queue",
        workflows=[InfrastructureWorkflow],
        activities=[terraform_cmd_init, terraform_cmd_plan, terraform_cmd_apply, terraform_cmd_output],
    )
    print("Worker started.")
    await worker.run()

if __name__ == "__main__":
    asyncio.run(main())