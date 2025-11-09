from datetime import timedelta
from temporalio import workflow
from activities import terraform_cmd_init, terraform_cmd_plan, terraform_cmd_apply, terraform_cmd_output


@workflow.defn
class InfrastructureWorkflow:
    @workflow.run
    async def run(self):
        """
        Run Terraform stages: init -> plan -> apply sequentially.
        Stops if any stage fails.
        """
        results = {}

        # Terraform init
        result_init = await workflow.execute_activity(
            terraform_cmd_init,
            ["init"], 
            start_to_close_timeout=timedelta(minutes=5)
        )
        results["init"] = result_init
        if "failed" in result_init.lower():
            workflow.logger.error("Terraform init failed. Stopping workflow.")
            return {"error": "Terraform init failed", "results": results}

        # Terraform plan
        result_plan = await workflow.execute_activity(
            terraform_cmd_plan,
            ["plan", "-out=plan.tfplan"],
            start_to_close_timeout=timedelta(minutes=10)
        )
        results["plan"] = result_plan
        if "failed" in result_plan.lower():
            workflow.logger.error("Terraform plan failed. Stopping workflow.")
            return {"error": "Terraform plan failed", "results": results}

        # Terraform apply
        result_apply = await workflow.execute_activity(
            terraform_cmd_apply,
            ["apply", "-auto-approve"],
            start_to_close_timeout=timedelta(minutes=15)
        )
        results["apply"] = result_apply
        if "failed" in result_apply.lower():
            workflow.logger.error("Terraform apply failed.")
            return {"error": "Terraform apply failed", "results": results}
        
        # Terraform output
        result_apply = await workflow.execute_activity(
            terraform_cmd_output,
            ["output", "-json"],
            start_to_close_timeout=timedelta(minutes=1)
        )

        workflow.logger.info("Terraform workflow completed successfully.")
        return results
