output "id" {
  description = "The ID of the instance"
  value = try(
    aws_instance.basic.id,
    null,
  )
}

output "arn" {
  description = "The ARN of the instance"
  value = try(
    aws_instance.basic.arn,
    null,
  )
}

output "public_ip" {
  description = "The public IP address assigned to the instance, if applicable."
  value = try(
    aws_instance.basic.public_ip,
    null,
  )
}

output "ssh_command" {
  value = "ssh -i temporal-infra-workflow-key.pem ubuntu@${aws_instance.basic.public_ip}"
}