pipeline {
    agent any

    stages {
        stage('Get code') {
            steps {
                checkout scm
            }
        }

        stage('Install Python dependencies') {
            steps {
                bat 'py -3.13 -m pip install --upgrade pip'
                bat 'py -3.13 -m pip install .'
                bat 'py -3.13 -m playwright install chromium'
            }
        }

        stage('Run tests') {
            steps {
                withCredentials([usernamePassword(
                    credentialsId: 'orangehrm-login',
                    usernameVariable: 'APP_USERNAME',
                    passwordVariable: 'APP_PASSWORD'
                )]) {
                    bat 'py -3.13 -m pytest'
                }
            }
        }
    }
}