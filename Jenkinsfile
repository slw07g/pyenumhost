/* Jenkinsfile (Declarative Pipeline) */
pipeline {
    agent { docker { image 'python:3.8' } }
    stages {
        stage('prep') {
            steps {
              withEnv(["HOME=${env.WORKSPACE}"]) {
                sh 'python --version'
                sh 'pip3 install pyinstaller'
                sh 'pip3 install -r requirements.txt'
              }
            }
        }
        stage('build') {
            steps {
              withEnv(["HOME=${env.WORKSPACE}"]) {
                sh 'pyinstaller --onefile enumhost.py'
               	sh 'dis/enumhost --all'
              }
            }
        }

    }
}
