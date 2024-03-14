pipeline {
    agent {
        kubernetes {
            label 'ez-joy-friends'
            idleMinutes 5
            yamlFile 'build-pod.yaml'
            defaultContainer 'ez-docker-helm-build'
        }
    }

    environment {
        GITLAB_CREDS = 'kibrik47-gitlab-cred'
        DOCKER_IMAGE = 'kibrik47/bugbuddies'
    }


    stages {
        stage('Checkout Code') {
            steps {
                git branch: 'main',
                    credentialsId: 'kibrik47-gitlab-cred',
                    url: 'https://gitlab.com/sela-tracks/1101/ariel/temp-404.git'
            }
        }
        
        stage('Build Docker image') {
            steps {
                script {
                    dockerImage = docker.build("${DOCKER_IMAGE}:latest", "--no-cache .")
                }
            }
        }

        
        // Add more stages as needed
    }
}
