/*
    This is the main pipeline section with the stages of the CI/CD
 */

pipeline {
    agent any
    environment {
            DOCKERHUB_PW = credentials('dockerhub-pw')

            AWS_CREDENTIALS = credentials('aws-cred')
            AWS_ACCESS_KEY_ID = "${env.AWS_CREDENTIALS_USR}"
            AWS_SECRET_ACCESS_KEY = "${env.AWS_CREDENTIALS_PSW}"
    }
    stages {
        stage('Clone repository') {
            /* Let's make sure we have the repository cloned to our workspace */
            steps {
                checkout scm
            }
        }
        stage('Create Kube Cluster Configuration') {
            steps {
                /*sh "kops create cluster  --name jenkins.k8s.local --state s3://datasink1 --zones us-west-1a --node-size=t2.large"*/
                sh "kops create cluster  --name jenkins.k8s.local --state s3://datasink1 --zones us-west-1a --node-size=t2.large --image 099720109477/ubuntu/images/hvm-ssd/ubuntu-xenial-16.04-amd64-server-20180306"
                sh "kops delete secret sshpublickey admin --name jenkins.k8s.local --state s3://datasink1"
                sh "kops create secret --name jenkins.k8s.local sshpublickey admin -i ~/.ssh/id_rsa.pub --state s3://datasink1"
                sh "kops update cluster jenkins.k8s.local --state s3://datasink1 --yes"
            }
        }
        stage('Deploying Kube Cluster') {
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
        stage('Deploying Kafka Helm Chart') {
            steps {

                sh 'kubectl create secret docker-registry docker-secret --docker-username=datasinkio --docker-password=$DOCKERHUB_PW --docker-email=datasinkio'

                sh 'chmod +x ./serviceaccount.sh'
                sh './serviceaccount.sh'

                echo 'helm init deployes tiller in kube cluster'
                sh "helm init"
                sh "helm repo add dskafka https://cranfss.github.io/dskafka"
                echo  'Starting sleep to allow tiller startup'
                sleep 20
                echo  'Finished sleep'
                sh "helm install --name kafka dskafka/dfkafka"

                echo 'Verify Kafka Cluster if available'
                
                sh 'chmod +x ./verify-release.sh'
                sh './verify-release.sh default'
                
            }
        }
        stage('Verify Kafka produce/consume') {
            steps {
                sh "helm test kafka --timeout 300 --debug"
            }
        }
        stage('Deploy Prometheus') {
            steps {
                sh "helm install -f ./prometheus-values.yaml stable/prometheus --name prometheus --set rbac.create=false"
            }
        }
    }
}
