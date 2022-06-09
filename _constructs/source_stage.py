import aws_cdk
from constructs import Construct
from aws_cdk import aws_codepipeline
from aws_cdk import aws_codepipeline_actions
from aws_cdk import aws_secretsmanager


class SourceStage(Construct):
    # ----------------------------------------------------------
    # ----------------------------------------------------------

    def __init__(self, scope: Construct, id: str, **kwargs) -> None:
        super().__init__(scope, id)

        self.source_output = aws_codepipeline.Artifact('source_stage_output')

    def github_source_action(self):
        owner = 'rafty'
        repo = 'sample_flask_frontend_app'
        # todo: cdk.jsonから取得する
        # branch = 'master'
        asm_secret_name = self.node.try_get_context('github_token_name')
        oauth_token = aws_cdk.SecretValue.secrets_manager(asm_secret_name)

        source_action = aws_codepipeline_actions.GitHubSourceAction(
            action_name='github-source-action',
            owner=owner,
            repo=repo,
            trigger=aws_codepipeline_actions.GitHubTrigger.POLL,
            oauth_token=oauth_token,
            output=self.source_output
        )
        return source_action
