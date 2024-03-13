pipeline {
    agent any

    environment {
        DOCKER_HUB_CREDENTIALS = credentials('BugBuddies-Docker-CRED')
    }

    stages {
        stage('Build Docker Image') {
            steps {
                script {
                    // Retrieve Docker Hub username dynamically
                    DOCKER_USERNAME = credentials('BugBuddies-Docker-CRED').username

                    // Login to Docker Hub
                    withCredentials([string(credentialsId: 'BugBuddies-Docker-CRED', variable: 'DOCKER_PASSWORD')]) {
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
                    sh 'pip install pytest'
                    sh 'pytest'
                }
            }
        }

        stage('HELM Package Build') {
            steps {
                script {
                    // Add commands to build HELM package
                    sh 'helm package ./charts/your_chart_directory'
                }
            }
        }

        stage('Deploy') {
            steps {
                script {
                    // Add commands to deploy the application
                    // This could include applying the HELM chart, deploying to Kubernetes, etc.
                }
            }
        }
    }

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
