import shutil
import json
import yaml
import boto3
from aws_lambda_powertools import Logger
from dulwich import porcelain

logger = Logger()
code_pipeline_client = boto3.client('codepipeline')
secrets_manager_client = boto3.client('secretsmanager')


def replace_image_tag(manifest, container_image_tag: str):

    image = manifest['spec']['template']['spec']['containers'][0]['image']
    _list = image.rsplit(':')
    _list[1] = container_image_tag  # tagを更新
    image_value = ':'.join(_list)
    manifest['spec']['template']['spec']['containers'][0]['image'] = image_value  # manifestを更新
    return manifest


def update_manifest(target_manifest, container_image_tag: str):
    with open(target_manifest, 'r', encoding='utf-8') as f:
        manifest = yaml.safe_load(f)
        # pprint.pprint(manifest)
        replaced_manifest = replace_image_tag(manifest, container_image_tag=container_image_tag)

    with open(target_manifest, 'w', encoding='utf-8') as f:
        yaml.dump(
            data=replaced_manifest,
            stream=f,
            sort_keys=False)  # Keyの順番を維持するためにsort_key=Falseを指定


def get_secret(conf: dict) -> str:
    response = secrets_manager_client.get_secret_value(
        SecretId=conf['github_token_name'])
    return response['SecretString']


def github_manifest_update(conf: dict):
    loca_repo_path = '/tmp/repo'  # lambda local path
    target_manifest = loca_repo_path + '/flask_workshop/frontend/dev/flask-frontend-dep.yaml'
    # Todo: move to CDK.json
    github_personal_access_token = get_secret(conf=conf)  # From Amazon Secrets Manager

    # git clone
    local_repo = porcelain.clone(
        source=conf['github_target_repository'],
        branch=conf['github_branch'].encode('utf-8'),
        password=github_personal_access_token,
        username='not relevant',
        target=loca_repo_path,
        checkout=True
    )

    # update container image tag
    update_manifest(
        target_manifest=target_manifest,
        container_image_tag=conf['container_image_tag'])

    # git add
    porcelain.add(repo=local_repo, paths=target_manifest)

    # git commit
    author = 'aws-codepipeline-lambda <lambda@example.com>'
    porcelain.commit(
        repo=local_repo,
        message='Updated Image Tag.',
        author=author,
        committer=author
    )

    # git push
    porcelain.push(
        repo=local_repo,
        remote_location=conf['github_target_repository'],
        refspecs=conf['github_branch'].encode('utf-8'),
        password=github_personal_access_token,
        username='not relevant',
    )

    shutil.rmtree(loca_repo_path)  # lambda "/tmp" cleanup


def extruct_user_parameters(event: dict) -> dict:
    job_data = event['CodePipeline.job']['data']
    user_parameters = json.loads(job_data['actionConfiguration']['configuration']['UserParameters'])
    conf = {
        'github_target_repository': user_parameters['github_target_repository'],
        'github_token_name': user_parameters['github_token_name'],
        'github_branch': user_parameters['github_branch'],  # master
        'container_image_tag': user_parameters['container_image_tag']['value']  # from Build Stage
    }
    return conf


def lambda_handler(event, context):
    logger.info(f'event: {event}')
    try:
        conf = extruct_user_parameters(event=event)
        github_manifest_update(conf=conf)

        # Complete notification to CodePipeline
        logger.info('Success: Updating image tag of manifest.')
        code_pipeline_client.put_job_success_result(jobId=event['CodePipeline.job']['id'])

    except Exception as e:
        logger.info(e)
        # Failure notification to CodePipeline
        code_pipeline_client.put_job_failure_result(jobId=event['CodePipeline.job']['id'],
                                                    failureDetails={
                                                        'type': 'JobFailed',
                                                        'message': 'Error: GitHub Push Failed.'
                                                    })
    return
