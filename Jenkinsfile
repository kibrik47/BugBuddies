pipeline {
    agent {
        kubernetes {
            label 'ez-joy-friends'
            idleMinutes 5
            yamlFile 'build.pod.yaml'
            defaultContainer 'ez-docker-helm-build'
        }
    }

    environment {
        GITLAB_CREDS = credentials('kibrik47-gitlab-cred')
        DOCKER_IMAGE = 'kibrik47/bugbuddies'
        IMAGE_VERSION = getNextImageVersion()

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
                    dockerImage = docker.build("${DOCKER_IMAGE}:${IMAGE_VERSION}", "--no-cache .")
                }
            }
        }

        
       stage('Test') {
            steps {
                script {
                    sh 'docker-compose -f docker-compose.yml up -d'
                    sh 'docker-compose -f docker-compose.yml run test_app pytest'
                    sh 'docker-compose -f docker-compose.yml down'
                }
            }
        }


        stage('Push Docker image') {
            when {
                branch 'main'
            }
            steps {
                script {
                    docker.withRegistry('https://registry.hub.docker.com', 'kibrik47-docker-cred') {
                        dockerImage.push("${IMAGE_VERSION}")
                    }
                }
            }
        }
    }


    def getNextImageVersion() {
        def versionFile = 'image_version.txt'
        def currentVersion = 0
        if (fileExists(versionFile)) {
            currentVersion = readFile(versionFile).trim().toInteger()
        }
        currentVersion++
        writeFile file: versionFile, text: "${currentVersion}"
        return currentVersion
    }

    def fileExists(filePath) {
        return file(filePath).exists()
    }
}
