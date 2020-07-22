/* Jenkinsfile (Declarative Pipeline) */
pipeline {
    agent { 
        docker { 
            image 'python:3.8' 
            args '--user 0:0'
        } 
    }
    stages {
        stage('prep') {
            steps {
              withEnv(["HOME=${env.WORKSPACE}"]) {
                sh 'python --version'
                sh 'pip3 install --user pyinstaller'
                sh 'pip3 install --user -r requirements.txt'
                sh 'pyinstaller --onefile enumhost.py'
                sh 'dis/enumhost --all'
              }
            }
        }
    }
}
