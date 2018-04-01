/*
    This is the main pipeline section with the stages of the CI/CD
 */

pipeline {
    agent any
    /*environment {
            DOCKERHUB_PW = credentials('dockerhub-pw')
    }*/
    stages {
        stage('Clone repository') {
            /* Let's make sure we have the repository cloned to our workspace */
            steps {
                checkout scm
            }
        }
        stage('Deploy kube cluster') {
            steps {
                sh "kops create cluster  --name jenkins.k8s.local --state s3://datasink1 --zones us-west-1a"
                sh "kops delete secret sshpublickey admin --name jenkins.k8s.local --state s3://datasink1"
                sh "kops create secret --name jenkins.k8s.local sshpublickey admin -i ~/.ssh/id_rsa.pub --state s3://datasink1"
                sh "kops update cluster jenkins.k8s.local --state s3://datasink1 --yes"
            }
        }
        stage('Validate cluster creation') {
            steps {
                timeout(time: 8, unit: 'MINUTES') {
                    waitUntil {
                       script {
                         def r = sh script: "kops validate cluster --name jenkins.k8s.local --state s3://datasink1", returnStatus: true
                         return (r == 0);
                       }
                    }
                }
            }
        }
        stage('Deploy Kafka Helm Chart') {
            steps {

                sh 'kubectl create secret docker-registry docker-secret --docker-username=datasinkio --docker-password=Lanz#Pe0rl --docker-email=datasinkio'
                sh 'kubectl patch serviceaccount default -p "{\"imagePullSecrets\": [{\"name\": \"docker-secret\"}]}"'

                echo 'helm init deployes tiller in kube cluster'
                sh "helm init"
                sh "helm repo add dskafka https://cranfss.github.io/dskafka"
                echo  'Starting sleep to allow tiller startup'
                sleep 10
                echo  'Finished sleep'
                sh "helm install --name kafka dskafka/dfkafka"
            }
        }
        /*stage('Tear down cluster') {
            
            sh "kops delete cluster --name jenkins.k8s.local --state s3://datasink1 --yes"
        }*/
    }
}
