/*
    This is the main pipeline section with the stages of the CI/CD
 */

pipeline {
    agent any
    environment {
            DOCKERHUB_PW = credentials('dockerhub-pw')
            
            /* AWS_ACCESS_KEY_ID = credentials('aws-access-key-id')
            AWS_SECRET_ACCESS_KEY = credentials('aws-secret-access-key') */

            AWS_CREDENTIALS = credentials('aws-cred')
            AWS_ACCESS_KEY_ID = "${env.AWS_CREDENTIALS_USR}"
            AWS_SECRET_ACCESS_KEY = "${env.AWS_CREDENTIALS_PSW}"
            
            /* KUBECONFIG = credentials('kubernetes-operator_kubernetes') */
    }
    stages {
        stage('Clone repository') {
            /* Let's make sure we have the repository cloned to our workspace */
            steps {
                checkout scm

                sh 'printenv'
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

                sh 'kubectl create secret docker-registry docker-secret --docker-username=datasinkio --docker-password=$DOCKERHUB_PW --docker-email=datasinkio'
                /*sh "kubectl patch serviceaccount default -p '{\'imagePullSecrets\': [{\'name\': \'docker-secret\'}]}'"*/

                sh 'chmod +x ./serviceaccount.sh'
                sh './serviceaccount.sh'
                echo 'Done - Running serveraccount.sh script'


                echo 'helm init deployes tiller in kube cluster'
                sh "helm init"
                sh "helm repo add dskafka https://cranfss.github.io/dskafka"
                echo  'Starting sleep to allow tiller startup'
                sleep 20
                echo  'Finished sleep'
                sh "helm install --name kafka dskafka/dfkafka"
            }
        }
        /*stage('Tear down cluster') {
            
            sh "kops delete cluster --name jenkins.k8s.local --state s3://datasink1 --yes"
        }*/
    }
}
