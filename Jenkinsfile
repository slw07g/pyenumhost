/* Jenkinsfile (Declarative Pipeline) */
pipeline {
    agent { 
        docker { 
            image 'python:3.8'
            args '--user 0:0 -v /var/run/docker.sock:/var/run/docker.sock -v /var/jenkins_home:/var/jenkins_home:rw'
            label 'python-docker'
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
                sh 'export PATH=.local/bin:$PATH'
                sh 'pip3 install pyinstaller'
                sh 'pip3 install -r requirements.txt'
                sh '.local/bin/pyinstaller --onefile enumhost.py'
                sh 'dist/enumhost --all'
              }
            }
        }
    }
}
