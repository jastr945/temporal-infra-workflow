from temporalio import activity
import asyncio
import os
from typing import List


TERRAFORM_FOLDER = "./terraform"

@activity.defn
async def _terraform_cmd_util(args: List[str]) -> str:
    """
    Run a Terraform command in the predefined folder.

    Args:
        args: list of Terraform command arguments, e.g., ["init"], ["plan", "-out=plan.tfplan"]

    Returns:
        stdout/stderr output of the command
    """
    if not os.path.isdir(TERRAFORM_FOLDER):
        return f"Error: Terraform folder {TERRAFORM_FOLDER} does not exist"

    cmd = ["terraform"] + args

    # Run command asynchronously
    process = await asyncio.create_subprocess_exec(
        *cmd,
        cwd=TERRAFORM_FOLDER,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE
    )

    output_lines = []

    async def stream_reader(stream, is_stderr=False):
        while True:
            line = await stream.readline()
            if not line:
                break
            text = line.decode().rstrip()
            output_lines.append(text)
            print(f"{'ERR' if is_stderr else 'OUT'}: {text}")


    await asyncio.gather(
        stream_reader(process.stdout),
        stream_reader(process.stderr, is_stderr=True)
    )

    await process.wait()

    if process.returncode != 0:
        return f"Terraform command failed (exit code {process.returncode}).\nOutput:\n" + "\n".join(output_lines)

    return "Terraform command succeeded:\n" + "\n".join(output_lines)


@activity.defn(name="terraform:init")
async def terraform_cmd_init(args):
    return await _terraform_cmd_util(args)


@activity.defn(name="terraform:plan")
async def terraform_cmd_plan(args):
    return await _terraform_cmd_util(args)


@activity.defn(name="terraform:apply")
async def terraform_cmd_apply(args):
    return await _terraform_cmd_util(args)


@activity.defn(name="terraform:output")
async def terraform_cmd_output(args=None) -> str:
    return await _terraform_cmd_util(args)


@activity.defn(name="terraform:destroy")
async def terraform_cmd_destroy(args=None) -> str:
    return await _terraform_cmd_util(args)