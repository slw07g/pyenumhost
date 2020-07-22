/* Jenkinsfile (Declarative Pipeline) */
pipeline {
    agent { 
        docker { 
            image 'python:3.8' 
            args '--user 1000:1000'
        } 
    }
    stages {
        stage('prep') {
            steps {
              withEnv(["HOME=${env.WORKSPACE}"]) {
                sh 'python --version'
                sh 'python -m venv .venv'
                sh '.venv/bin/activate'
                sh 'pip3 install pyinstaller'
                sh 'pip3 install -r requirements.txt'
                sh 'pyinstaller --onefile enumhost.py'
                sh 'dist/enumhost --all'
              }
            }
        }
    }
}
