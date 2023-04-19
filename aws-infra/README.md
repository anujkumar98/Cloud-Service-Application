# aws-infra terraform code

## Steps to setup:

<ul>
<li>Configure AWS user in AWS Management Console</li>
<li>Create a Access key and Secret for the user</li>
<li>Setup the AWS Terminal : https://docs.aws.amazon.com/cli/latest/userguide/getting-started-install.html
<li>Setup AWS profile in AWS Terminal : https://docs.aws.amazon.com/cli/latest/userguide/cli-configure-quickstart.html </li>
<br>

```
$ aws configure --profile profile_name
```
<li>Install Terraform : https://developer.hashicorp.com/terraform/tutorials/aws-get-started/install-cli </li>
</ul>

## Steps to run:

<ul>
<li>
    Run Terraform format command
</li>
<br>

```
$ terraform fmt
```
<li>
    Run Terraform initialization command
</li>
<br>

```
$ terraform init
```
<li>
    Run Terraform apply command
</li>
<br>

```
$ terraform apply --var-file filename.tfvars
```

<li>
    Run Terraform destroy to delete the infrastructure</li>
<br>

```
$ terraform destroy
```

</ul>
