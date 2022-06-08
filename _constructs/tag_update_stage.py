import aws_cdk
from constructs import Construct
from aws_cdk import aws_codepipeline
from aws_cdk import aws_codepipeline_actions
from aws_cdk import aws_secretsmanager
from aws_cdk import aws_lambda
from aws_cdk import aws_codebuild



class TagUpdateStage(Construct):
    # ----------------------------------------------------------
    # ----------------------------------------------------------

    def __init__(self, scope: Construct, id: str, info: dict, env: dict, **kwargs) -> None:
        super().__init__(scope, id)
        self._region = env.get('region')
        self._pipeline_name = info.get('pipeline_name')
        self._ecr_repository_name = info.get('ecr_repository_name')
        self._container_image_name = info.get('container_image_name')
        self._container_image_tag = info.get('container_image_tag')
        # self.source_output = aws_codepipeline.Artifact('source_stage_output')

    def github_tag_update_action(self):
        # Todo: cdk.jsonから取得する
        # owner = 'rafty'
        # repo = 'sample_flask_frontend_app'
        # branch = 'master'
        # Todo: ASMから取得する
        # oauth_token = aws_cdk.SecretValue.secrets_manager('GithubPersonalAccessToken')

        fn = self.create_lambda_function()

        lambda_invoke_action = aws_codepipeline_actions.LambdaInvokeAction(
            action_name='github-manifest-tag-update',
            user_parameters={
                'github_repo': 'hoge_app',
                'github_owner': 'rafty',
                'github_branch': 'master',
                'github_oauth_token_name': 'GithubPersonalAccessToken',
                'codepipeline_name': self._pipeline_name,
                'ecr_repository_name': self._ecr_repository_name,
                'container_image_name': self._container_image_name,
                'container_image_tag': self._container_image_tag,
            },
            lambda_=fn,
        )
        return lambda_invoke_action

    def create_lambda_function(self):

        _powertools_layer = aws_lambda.LayerVersion.from_layer_version_arn(
            self,
            id='lambda-powertools',
            layer_version_arn=(f'arn:aws:lambda:{self._region}:017000801446:'
                               'layer:AWSLambdaPowertoolsPython:19')
        )

        function = aws_lambda.Function(
            self,
            'LambdaInvokeFunction',
            function_name='GithubManifestTagUpdate',
            handler='function.lambda_handler',
            runtime=aws_lambda.Runtime.PYTHON_3_8,
            # code=aws_lambda.Code.from_inline(function_inline_code),
            code=aws_lambda.Code.from_asset('./functions/manifest_update'),
            layers=[_powertools_layer],
            environment={
                'POWERTOOLS_SERVICE_NAME': 'GitOpsPipelineAction',  # for Powertools
                'LOG_LEVEL': 'INFO',  # for Powertools
            },
            memory_size=128,
            timeout=aws_cdk.Duration.seconds(60),
            # dead_letter_queue_enabled=True
        )
        return function
