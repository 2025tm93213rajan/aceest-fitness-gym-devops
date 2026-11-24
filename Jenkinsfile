// Jenkins BUILD pipeline for ACEest Fitness & Gym.
// Second validation layer after GitHub Actions: pulls the latest code from GitHub
// and does a clean build + test in a controlled environment.
pipeline {
    agent any

    options {
        disableConcurrentBuilds()
        buildDiscarder(logRotator(numToKeepStr: '10'))
    }

    // Jenkins runs on a laptop here so GitHub can't send webhooks to it,
    // polling the repo every few minutes is the simple alternative.
    triggers {
        pollSCM('H/5 * * * *')
    }

    environment {
        IMAGE = "aceest-fitness:jenkins-${env.BUILD_NUMBER}"
        TEST_IMAGE = "aceest-fitness:jenkins-test-${env.BUILD_NUMBER}"
    }

    stages {
        stage('Clean Checkout') {
            steps {
                // wipe the workspace first so every build starts from scratch
                deleteDir()
                checkout scm
            }
        }

        stage('Setup Environment') {
            steps {
                sh '''
                    python3 -m venv .venv
                    . .venv/bin/activate
                    pip install --quiet -r requirements-dev.txt
                '''
            }
        }

        stage('Lint') {
            steps {
                sh '''
                    . .venv/bin/activate
                    python -m compileall -q app.py aceest tests
                    flake8 app.py aceest tests
                '''
            }
        }

        stage('Unit Tests') {
            steps {
                sh '''
                    . .venv/bin/activate
                    python -m pytest
                '''
            }
            post {
                always {
                    junit allowEmptyResults: true, testResults: 'reports/junit.xml'
                }
            }
        }

        stage('SonarQube Analysis') {
            steps {
                sh '''
                    if command -v sonar-scanner >/dev/null 2>&1; then
                        sonar-scanner -Dsonar.host.url=http://localhost:9000 || true
                    else
                        docker run --rm --network host -v $(pwd):/usr/src sonarsource/sonar-scanner-cli -Dsonar.host.url=http://localhost:9000 || true
                    fi
                '''
            }
        }

        stage('Docker Build') {
            steps {
                sh '''
                    docker build --target runtime --build-arg APP_VERSION=2.0.0 --build-arg APP_RELEASE=v2-analytics -t $IMAGE .
                    docker tag $IMAGE aceest-fitness:v2.0.0
                    docker tag $IMAGE aceest-fitness:latest
                '''
            }
        }

        // same check GitHub Actions does: run the suite inside the container
        stage('Docker Tests') {
            steps {
                sh '''
                    docker build --target test -t $TEST_IMAGE .
                    docker run --rm $TEST_IMAGE
                '''
            }
        }
    }

    post {
        always {
            // don't let old build images pile up on the docker host
            sh 'docker rmi $IMAGE $TEST_IMAGE || true'
        }
        success {
            echo 'BUILD SUCCESS - code compiles, tests pass and the image builds.'
        }
        failure {
            echo 'BUILD FAILED - check the stage that turned red.'
        }
    }
}
