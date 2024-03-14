pipeline {
    agent any

    stages {
        stage('Checkout') {
            steps {
                // Checkout source code from GitLab
                git 'https://gitlab.com/sela-tracks/1101/ariel/temp-404.git'
            }
        }
        stage('Build Docker Image') {
            steps {
                // Build Docker image
                script {
                    docker.build('kibrik47/bugbuddies:latest')
                }
            }
        }
    }
}
