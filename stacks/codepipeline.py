from aws_cdk import Stack
from constructs import Construct
from aws_cdk import aws_ecr
from aws_cdk import aws_codepipeline
from aws_cdk import aws_codebuild
from _constructs.source_stage import SourceStage
from _constructs.build_stage import BuildStage
from _constructs.tag_update_stage import TagUpdateStage


class CodepipelineStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        env = {
            'account': self.account,
            'region': self.region
        }

        # ECR Repositoryの作成
        ecr_repository_name = self.node.try_get_context('ecr_repository_name')
        self.__ecr_repo = aws_ecr.Repository(
            self,
            id=f'{ecr_repository_name}-Stack',
            repository_name=ecr_repository_name,
            # image_scan_on_push=True,  # Image Scan
            # removal_policy=aws_cdk.RemovalPolicy.DESTROY, # stack削除時の動作
            # lifecycle_rules=[removal_old_image]  # imageの世代管理
        )

        # CodePipelineの作成
        pipeline_name = self.node.try_get_context('pipeline_name')
        codepipeline = aws_codepipeline.Pipeline(
            self,
            id='sample_codepipeline',
            pipeline_name=pipeline_name,
            # cross_account_keys=False
        )

        # Stage - Source
        source_stage = SourceStage(self, 'SourceStage')
        source_action = source_stage.github_source_action()
        codepipeline.add_stage(
            stage_name='Source',
            actions=[source_action]
        )

        # Stage - Build
        build_stage = BuildStage(
            self,
            'BuildStage',
            source_output=source_stage.source_output,
            env=env)
        build_action = build_stage.creation()
        codepipeline.add_stage(
            stage_name='Build',
            actions=[build_action]
        )

        # Stage - Manifest Tag Update (GitHub)
        info = {
            'container_image_name': aws_codebuild.BuildEnvironmentVariable(
                value=build_action.variable('VAR_CONTAINER_IMAGE_NAME')),
            'container_image_tag': aws_codebuild.BuildEnvironmentVariable(
                value=build_action.variable('VAR_CONTAINER_IMAGE_TAG'))
        }
        tag_update_stage = TagUpdateStage(
            self,
            'TagUpdateStage',
            info=info,
            env=env)
        tag_update_action = tag_update_stage.github_tag_update_action()
        codepipeline.add_stage(
            stage_name='TagUpdate',
            actions=[tag_update_action]
        )
