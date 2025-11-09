from datetime import timedelta
from temporalio import workflow
from temporalio.common import RetryPolicy
from activities import terraform_cmd_init, terraform_cmd_plan, terraform_cmd_apply, terraform_cmd_output, terraform_cmd_destroy


@workflow.defn
class InfrastructureWorkflow:
    @workflow.run
    async def run(self):
        """
        Run Terraform stages: init>plan>apply>output sequentially.
        Stops if any stage fails.
        """
        retry_policy = RetryPolicy(
            initial_interval=timedelta(seconds=10),
            backoff_coefficient=2.0,
            maximum_interval=timedelta(minutes=5),
            maximum_attempts=5,
        )

        results = {}

        # Terraform init
        result_init = await workflow.execute_activity(
            terraform_cmd_init,
            ["init", "-no-color"], 
            start_to_close_timeout=timedelta(minutes=5),
            retry_policy=retry_policy,
        )
        results["init"] = result_init
        if "failed" in result_init.lower():
            workflow.logger.error("Terraform init failed. Stopping workflow.")
            raise Exception(f"Terraform plan failed:\n{result_init}")

        # Terraform plan
        result_plan = await workflow.execute_activity(
            terraform_cmd_plan,
            ["plan", "-out=plan.tfplan", "-no-color"],
            start_to_close_timeout=timedelta(minutes=10),
            retry_policy=retry_policy,
        )
        results["plan"] = result_plan
        if "failed" in result_plan.lower():
            workflow.logger.error("Terraform plan failed. Stopping workflow.")
            raise Exception(f"Terraform plan failed:\n{result_plan}")

        # Terraform apply
        result_apply = await workflow.execute_activity(
            terraform_cmd_apply,
            ["apply", "-auto-approve", "-no-color"],
            start_to_close_timeout=timedelta(minutes=15),
            retry_policy=retry_policy,
        )
        results["apply"] = result_apply
        if "failed" in result_apply.lower():
            workflow.logger.error("Terraform apply failed.")
            raise Exception(f"Terraform plan failed:\n{result_apply}")
        
        # Terraform output
        result_output = await workflow.execute_activity(
            terraform_cmd_output,
            ["output", "-json", "-no-color"],
            start_to_close_timeout=timedelta(minutes=1)
        )

        workflow.logger.info("Terraform workflow completed successfully.")
        return results


@workflow.defn
class DestroyInfrastructureWorkflow:
    @workflow.run
    async def run(self):
        """
        Run `terraform destroy` to teardown the infrastructure.
        Stops if the destroy fails.
        """
        retry_policy = RetryPolicy(
            initial_interval=timedelta(seconds=10),
            backoff_coefficient=2.0,
            maximum_interval=timedelta(minutes=5),
            maximum_attempts=5,
        )

        results = {}

        result_destroy = await workflow.execute_activity(
            terraform_cmd_destroy,
            ["destroy", "-auto-approve", "-no-color"],
            start_to_close_timeout=timedelta(minutes=15),
            retry_policy=retry_policy,
        )
        results["destroy"] = result_destroy

        if "failed" in result_destroy.lower():
            workflow.logger.error("Terraform destroy failed.")
            raise Exception(f"Terraform plan failed:\n{result_destroy}")

        workflow.logger.info("Terraform destroy completed successfully.")
        return results