from getpass import getuser
from typing import Optional

import aws_cdk
from pydantic import AnyHttpUrl, BaseSettings, Field, HttpUrl, constr

AwsArn = constr(regex=r"^arn:aws:iam::\d{12}:role/.+")
AwsStepArn = constr(regex=r"^arn:aws:states:.+:\d{12}:stateMachine:.+")
AwsOidcArn = constr(regex=r"^arn:aws:iam::\d{12}:oidc-provider/.+")


class Deployment(BaseSettings):
    app_name: str = Field(
        description="Name of the application", default="ghgc-stac-ingestor"
    )
    stage: str = Field(
        description=" ".join(
            [
                "Stage of deployment (e.g. 'dev', 'prod').",
                "Used as suffix for stack name.",
                "Defaults to current username.",
            ]
        ),
        default_factory=getuser,
    )
    owner: str = Field(
        description=" ".join(
            [
                "Name of primary contact for Cloudformation Stack.",
                "Used to tag generated resources",
                "Defaults to current username.",
            ]
        ),
        default_factory=getuser,
    )

    aws_account: str = Field(
        description="AWS account used for deployment",
        env="CDK_DEFAULT_ACCOUNT",
    )
    aws_region: str = Field(
        default="us-west-2",
        description="AWS region used for deployment",
        env="CDK_DEFAULT_REGION",
    )

    userpool_id: str = Field(description="The Cognito Userpool used for authentication")
    client_id: str = Field(description="The Cognito APP client ID")

    stac_db_secret_name: str = Field(
        description="Name of secret containing pgSTAC DB connection information"
    )
    stac_db_vpc_id: str = Field(description="ID of VPC running pgSTAC DB")
    stac_db_security_group_id: str = Field(
        description="ID of Security Group used by pgSTAC DB"
    )
    stac_db_public_subnet: bool = Field(
        description="Boolean indicating whether or not pgSTAC DB is in a public subnet",
        default=True,
    )
    stac_url: HttpUrl = Field(
        description="URL of STAC API",
    )

    raster_url: AnyHttpUrl = Field(description="URL of Raster API")

    data_access_role: Optional[AwsArn] = Field(
        description="ARN of AWS Role used to validate access to S3 data"
    )

    mwaa_env: Optional[str] = Field(
        description="Environment of Airflow deployment",
    )

    oidc_provider_arn: Optional[AwsOidcArn] = Field(
        description="ARN of AWS OIDC provider used for authentication"
    )

    oidc_repo_id: str = Field(
        "NASA-IMPACT/ghgc-stac-ingestor",
        description="ID of AWS ECR repository used for OIDC provider",
    )

    path_prefix: Optional[str] = Field(
        "",
        description="Optional path prefix to add to all api endpoints",
    )

    permissions_boundary_policy_name: Optional[str] = Field(
        None,
        description="Name of IAM policy to define stack permissions boundary",
    )

    class Config:
        env_prefix = ""
        case_sentive = False
        env_file = ".env"

    @property
    def stack_name(self) -> str:
        return f"{self.app_name}-{self.stage}"

    @property
    def env(self) -> aws_cdk.Environment:
        return aws_cdk.Environment(
            account=self.aws_account,
            region=self.aws_region,
        )
