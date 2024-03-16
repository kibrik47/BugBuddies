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
                    dockerImage = docker.build("${DOCKER_IMAGE}:latest" "--no-cache .")
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
                        dockerImage.push("latest")
                    }
                }
            }
        }
    }

     stage('Create Merge Request') {
            when {
                not {
                    branch 'main'
                }
            }
            steps {
                script {
                    withCredentials([string(credentialsId: 'dary-gitlab-api', variable: 'GITLAB_API_TOKEN')]) {
                        def response = sh(script: """
                        curl -s -o response.json -w "%{http_code}" --header "PRIVATE-TOKEN: ${GITLAB_API_TOKEN}" -X POST "${GITLAB_URL}/api/v4/projects/${PROJECT_ID}/merge_requests" \
                        --form "source_branch=${env.BRANCH_NAME}" \
                        --form "target_branch=main" \
                        --form "title=MR from ${env.BRANCH_NAME} into main" \
                        --form "remove_source_branch=true"
                        """, returnStdout: true).trim()
                        if (response.startsWith("20")) {
                            echo "Merge request created successfully."
                        } else {
                            echo "Failed to create merge request. Response Code: ${response}"
                            def jsonResponse = readJSON file: 'response.json'
                            echo "Error message: ${jsonResponse.message}"
                            error "Merge request creation failed."
                        }
                    }
                }
            }
        }

}
