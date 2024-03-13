pipeline {
    agent any

    stages {
        stage('Build Docker Image') {
            steps {
                script {
                    // Build and tag Docker image for feature branches
                    sh 'docker build -t kibrik47/bugbuddies:v2 .'
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
