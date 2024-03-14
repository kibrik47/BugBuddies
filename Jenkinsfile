pipeline {
    agent {
        kubernetes {
            label 'ez-joy-friends'
            idleMinutes 5
            yamlFile 'build-pod.yaml'
            defaultContainer 'ez-docker-helm-build'

        }
    }


    stages {
        stage('Checkout Code') {
            steps{
                checkout scm
            }
        }


        stage('Build Docker Image') {
            steps {
                script {
                    dockerImage - docker.build("${DOCKER_IMAGE}:latest", "--no-cache .")
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
                emailext subject: "Failed: ${currentBuild.fullDisplayName}",
                          body: 'Something went wrong. Please investigate.',
                          to: 'ariel.kibrik2@gmail.com',
                          mimeType: 'text/html'
            }
        }
    }
}
