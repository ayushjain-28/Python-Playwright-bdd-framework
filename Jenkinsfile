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
                bat 'py -m pip install --upgrade pip'
                bat 'py -m pip install .'
                bat 'py -m playwright install chromium'
            }
        }

        stage('Run tests') {
            steps {
                bat 'py -m pytest'
            }
        }
    }
}
