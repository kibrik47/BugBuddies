pipeline {
    agent any

    stages {
        stage('Checkout') {
            steps {
                // Checkout source code from GitLab
                git 'https://gitlab.com/your/repository.git'
            }
        }
        stage('Build Docker Image') {
            steps {
                // Build Docker image
                script {
                    docker.build('your-docker-image:latest')
                }
            }
        }
    }
}
