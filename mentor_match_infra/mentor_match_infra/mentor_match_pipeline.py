from aws_cdk import Stack, Environment
from aws_cdk.pipelines import (
    CodePipeline,
    ShellStep,
    CodePipelineSource,
    ManualApprovalStep,
)
from constructs import Construct

from .custom_steps import DeleteStack
from .mentor_match_stage import MentorMatchAppStage


class MentorMatchPipeline(Stack):
    def __init__(self, scope: Construct, construct_id: str, **kwargs):
        super().__init__(scope, construct_id, **kwargs)
        pipeline = CodePipeline(
            self,
            "MentorMatchPipeline",
            pipeline_name="Pipeline",
            cross_account_keys=True,
            synth=ShellStep(
                "Synth",
                input=CodePipelineSource.connection(
                    "mentor-matching-online/mentor-match",
                    branch="main",
                    connection_arn="arn:aws:codestar-connections:eu-west-2:661101848753:connection/99c2d217-1c7c-4ff5-9769-eebe35880557",  # noqa
                    action_name="github_source",
                ),
                commands=[
                    "npm install -g aws-cdk",
                    "cd mentor_match_infra",
                    "python -m pip install -r requirements.txt",
                    "cdk synth",
                ],
                primary_output_directory="mentor_match_infra/cdk.out",
            ),
        )
        testing_stage = MentorMatchAppStage(
            self, "testing", env=Environment(account="661101848753", region="eu-west-2")
        )
        pipeline.add_stage(testing_stage, post=[DeleteStack(testing_stage.service)])

        production_stage = pipeline.add_stage(
            MentorMatchAppStage(
                self,
                "production",
                env=Environment(account="661101848753", region="eu-west-2"),
            )
        )
        production_stage.add_pre(ManualApprovalStep("approval"))
