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
                sh 'python -m venv .venv'
                sh 'ls -al .venv/bin'
                sh 'chmod +x .venv/bin/activate'
                sh '.venv/bin/activate'
                sh 'export PATH=`pwd`/.local/bin:$PATH'
                sh 'pip3 install pyinstaller'
                sh 'find . | grep pyinstaller'
                sh 'pip3 install -r requirements.txt'
                sh 'pyinstaller --onefile enumhost.py'
                sh 'dist/enumhost --all'
              }
            }
        }
    }
}
