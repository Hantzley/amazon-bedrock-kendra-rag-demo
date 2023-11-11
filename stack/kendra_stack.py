from aws_cdk import (
    Stack,
    aws_ec2 as ec2,
    aws_kendra as kendra,
    aws_iam as iam,
    aws_s3 as s3,
    aws_ssm as ssm,
    aws_lambda as _lambda,
    triggers,
    RemovalPolicy,
    Duration
)
from constructs import Construct

class KendraStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, vpc: ec2.IVpc, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # Create an S3 bucket
        s3_bucket = s3.Bucket(
            self, "GenAI-RAG-Doc-Bucket",
            removal_policy=RemovalPolicy.DESTROY,
            auto_delete_objects = True
        )
        
        # Create role for Kendra
        role=iam.Role(self, "KendraRole", assumed_by=iam.ServicePrincipal("kendra.amazonaws.com"))
        role.add_managed_policy(iam.ManagedPolicy.from_aws_managed_policy_name("AmazonKendraFullAccess"))
        role.add_managed_policy(iam.ManagedPolicy.from_aws_managed_policy_name("AmazonS3FullAccess"))
        role.add_managed_policy(iam.ManagedPolicy.from_aws_managed_policy_name("CloudWatchLogsFullAccess"))
        role.add_managed_policy(iam.ManagedPolicy.from_aws_managed_policy_name("CloudWatchFullAccess"))

        
        # Create role for the AWS Lambda functions
        lambda_role = iam.Role(self, "Gen-AI-Lambda-Policy", assumed_by=iam.ServicePrincipal("lambda.amazonaws.com"))
        lambda_role.add_managed_policy(iam.ManagedPolicy.from_aws_managed_policy_name("service-role/AWSLambdaBasicExecutionRole"))
        lambda_role.add_managed_policy(iam.ManagedPolicy.from_aws_managed_policy_name("service-role/AWSLambdaVPCAccessExecutionRole"))
        lambda_role.attach_inline_policy(iam.Policy(self, "lambda-s3-policy",
            statements=[iam.PolicyStatement(
                effect=iam.Effect.ALLOW,
                actions=["s3:*"],
                resources=["arn:aws:s3:::*"]
            )]
        ))
        lambda_role.attach_inline_policy(iam.Policy(self, "lambda-kendra-policy",
            statements=[iam.PolicyStatement(
                effect=iam.Effect.ALLOW,
                actions=["kendra:*"],
                resources=["*"]
            )]
        ))
        lambda_role.attach_inline_policy(iam.Policy(self, "lambda-logs-policy",
            statements=[iam.PolicyStatement(
                effect=iam.Effect.ALLOW,
                actions=["logs:*"],
                resources=["*"]
            )]
        ))        
        lambda_role.attach_inline_policy(iam.Policy(self, "lambda-ssm-policy",
            statements=[iam.PolicyStatement(
            effect=iam.Effect.ALLOW,
            actions = ["ssm:GetParameter"],
            resources = ["arn:aws:ssm:*"],
            )]
        ))          
        
        # Create Kendra index
        kendra_cfn_index = kendra.CfnIndex(self, "MyKendraCfnIndex",
            edition="DEVELOPER_EDITION",
            name="genai-rag-index-cdk",
            role_arn=role.role_arn)
        
        # Create Kendra data source
        s3_cfn_data_source = kendra.CfnDataSource(self, "MyS3CfnDataSource",
            index_id=kendra_cfn_index.attr_id,
            name="GenAI-S3-Data-Source",
            type="S3",
            role_arn=role.role_arn,
            data_source_configuration=kendra.CfnDataSource.DataSourceConfigurationProperty(
                s3_configuration=kendra.CfnDataSource.S3DataSourceConfigurationProperty(
                    bucket_name=s3_bucket.bucket_name,
                    inclusion_prefixes=["Documents/"],
                    documents_metadata_configuration=kendra.CfnDataSource.DocumentsMetadataConfigurationProperty(
                        s3_prefix="Metadata/"
                    )
                )
            )
        )
        
        # Defines an AWS Lambda function for Kendra boostrapping
        kendra_bootstrap = _lambda.Function(
            self, "kendra_bootstrap",
            runtime=_lambda.Runtime.PYTHON_3_9,
            code=_lambda.Code.from_asset("lambda/bootstrap_kendra"),
            handler="init_kendra.lambda_handler",
            role=lambda_role,
            timeout=Duration.minutes(10),
            memory_size=1024,
            vpc_subnets=ec2.SubnetSelection(
                subnet_type=ec2.SubnetType.PRIVATE_WITH_EGRESS
            ),
            vpc=vpc
        )        
        
        # Define the lambda trigger
        lambda_trigger = triggers.Trigger(self, "KendraBoostrapTrigger",
            handler=kendra_bootstrap,
            timeout=Duration.minutes(10),
            invocation_type=triggers.InvocationType.EVENT
        )
        
        # Execute trigger after Kendra data source is created
        lambda_trigger.execute_after(s3_cfn_data_source)
        
        # Storing parameters in SSM Parameter Store
        ssm.StringParameter(self, "genai_s3_bucket", parameter_name="genai_s3_bucket", string_value=s3_bucket.bucket_name)
        ssm.StringParameter(self, "kendra_index_id", parameter_name="genai_kendra_index_id", string_value=kendra_cfn_index.attr_id)
        ssm.StringParameter(self, "s3_data_source_id", parameter_name="genai_s3_data_source_id", string_value=s3_cfn_data_source.attr_id)
        
        