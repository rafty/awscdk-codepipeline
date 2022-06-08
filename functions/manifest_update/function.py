import json
import boto3
from aws_lambda_powertools import Logger

logger = Logger()
client = boto3.client('codepipeline')


def lambda_handler(event, context):

    logger.info(f'handler event: {event}')
    # print(f'handler event: {event}')
    job_data = event['CodePipeline.job']['data']

    user_parameters = json.loads(
        job_data['actionConfiguration']['configuration']['UserParameters'])
    github_repo = user_parameters['github_repo']
    github_owner = user_parameters['github_owner']
    github_branch = user_parameters['github_branch']
    github_oauth_token_name = user_parameters['github_oauth_token_name']
    codepipeline_name = user_parameters['codepipeline_name']
    ecr_repository_name = user_parameters['ecr_repository_name']
    container_image_name = user_parameters['container_image_name']
    container_image_tag = user_parameters['container_image_tag']

    logger.info(
        (
            f'github_repo: {github_repo}',
            f'github_owner: {github_owner}',
            f'github_branch: {github_branch}',
            f'github_oauth_token_name: {github_oauth_token_name}',
            f'codepipeline_name: {codepipeline_name}',
            f'ecr_repository_name: {ecr_repository_name}',
            f'container_image_name: {container_image_name}',
            f'container_image_tag: {container_image_tag}'
        )
    )

    client.put_job_success_result(
        jobId=event['CodePipeline.job']['id'])
    # client.put_job_failure_result(
    #     jobId=event['CodePipeline.job']['id'],
    #     failureDetails={
    #         'type': 'JobFailed',
    #         'message': 'Error: GitHub push Failed.'
    # )
    return
