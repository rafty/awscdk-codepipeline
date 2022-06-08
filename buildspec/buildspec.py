buildspec_object = {
    "version": "0.2",
    "env": {
        "exported-variables": ["VAR_CONTAINER_IMAGE_NAME", "VAR_CONTAINER_IMAGE_TAG"]
    },
    "phases": {
        "install": {
            "runtime-versions": {
                    "python": 3.8,
                    "docker": 19
            },
            "commands": [
                'echo --- build spec install ---',
            ]
        },

        "pre_build": {
            "commands": [
                    'echo --- Logging in to Amazon ECR ---',
                    'echo $AWS_DEFAULT_REGION',
                    'echo $AWS_ACCOUNT_ID',
                    'echo $CONTAINER_IMAGE_NAME',
                    'aws ecr get-login-password --region $AWS_DEFAULT_REGION | docker login --username AWS --password-stdin $AWS_ACCOUNT_ID.dkr.ecr.$AWS_DEFAULT_REGION.amazonaws.com',
                    'echo --- Logging in to DockerHub ---',
                    'DOCKERHUB_USER_ID=$(aws --region="$AWS_DEFAULT_REGION" ssm get-parameters --names "/CodeBuild/DOCKERHUB_USER_ID" | jq --raw-output ".Parameters[0].Value")',
                    'DOCKERHUB_PASSWORD=$(aws --region="$AWS_DEFAULT_REGION" ssm get-parameters --names "/CodeBuild/DOCKERHUB_PASSWORD" --with-decryption | jq --raw-output ".Parameters[0].Value")',
                    'echo $DOCKERHUB_PASSWORD | docker login -u $DOCKERHUB_USER_ID --password-stdin',
            ],
        },

        "build": {
            "commands": [
                    'echo --- Building Docker image ---',
                    'cd app',
                    'ECR_URI=$AWS_ACCOUNT_ID.dkr.ecr.$AWS_DEFAULT_REGION.amazonaws.com',
                    'echo $ECR_URI'
                    'COMMIT_HASH=$(echo $CODEBUILD_RESOLVED_SOURCE_VERSION | cut -c 1-8)',
                    'IMAGE_TAG=$(date +%Y-%m-%dH%H.%M.%S)-${COMMIT_HASH:=latest}',
                    'docker build --no-cache -t $CONTAINER_IMAGE_NAME .',
                    'docker tag $CONTAINER_IMAGE_NAME:latest $ECR_URI/$CONTAINER_IMAGE_NAME:$IMAGE_TAG',
            ],
        },

        "post_build": {
            "commands": [
                    'echo --- Pushing the Docker images ---',
                    'docker push $ECR_URI/$CONTAINER_IMAGE_NAME:$IMAGE_TAG',
                    'echo --- CodeBuild BuildEnvironmentVariable---',
                    'export VAR_CONTAINER_IMAGE_NAME=$CONTAINER_IMAGE_NAME',
                    'export VAR_CONTAINER_IMAGE_TAG=$IMAGE_TAG',
                    'echo --- Build completed ---',
            ],
        },
    },
}
