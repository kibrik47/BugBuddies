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
        GITLAB_CREDS = 'BugBuddiesGLToken'
        DOCKER_IMAGE = 'kibrik47/bugbuddies'
        MONGODB_URI = 'mongodb://mongo:27017/your_database'
        PROJECT_ID = ''
        GITLAB_URL = 'https://gitlab.com'
    }


    stages {
        stage('Checkout') {
            steps {
                // Checkout the repository
                checkout scm
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
