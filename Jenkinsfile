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
        DOCKER_IMAGE = 'kibrik47/bugbuddies'
    }

    stages {
        stage('Checkout Code') {
            steps {
                checkout scm
            }
        } // Closing brace was added here

        stage('Build Docker Image') {
            steps {
                script {
                    dockerImage = docker.build("${DOCKER_IMAGE}:latest", "--no-cache .") // Fixed the assignment operator
                }
            }
        }

        stage('Run Unit Tests') {
            steps {
                script {
                    // Run unit tests using pytest
                    sh 'docker-compose -f docker-compose.yaml up -d'
                    sh 'docker-compose -f docker-compose.yaml run test_app pytest'
                    sh 'docker-compose -f docker-compose.yaml down'
                }
            }
        }
    }
}
