pipeline {
    agent any

    environment {
        DOCKER_HUB_CREDENTIALS = credentials('kibrik47-docker-cred')
    }

    stages {
        stage('Build Docker Image') {
            steps {
                script {
                    // Retrieve Docker Hub username dynamically
                    DOCKER_USERNAME = credentials('kibrik47-docker-cred').username

                    // Login to Docker Hub
                    withCredentials([string(credentialsId: 'kibrik47-docker-cred', variable: 'DOCKER_PASSWORD')]) {
                        sh "docker login -u $DOCKER_USERNAME -p $DOCKER_PASSWORD"

                        // Build Docker image
                        sh 'docker build -t kibrik47/bugbuddies:v2 .'
                    }
                }
            }
        }

        stage('Run Unit Tests') {
            steps {
                script {
                    // Run unit tests using pytest
                    sh 'docker-compose up'
                    sh 'docker-compose run test_app'
                }
            }
        }
    } // Close the stages block

    post {
        failure {
            script {
                // Send email notification for failed builds
                emailext subject: 'Failed: ${currentBuild.fullDisplayName}',
                          body: 'Something went wrong. Please investigate.',
                          to: 'ariel.kibrik2@gmail.com',
                          mimeType: 'text/html'
            }
        }
    }
}
