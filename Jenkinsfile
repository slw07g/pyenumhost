/* Jenkinsfile (Declarative Pipeline) */
pipeline {
    agent { docker { image 'python:3.8' } }
    stages {
        stage('build') {
            steps {
                sh 'python --version'
                sh 'pip3 install pyinstaller'
                sh 'pip3 install -r requirements.txt'
            }
        }
    }
}
