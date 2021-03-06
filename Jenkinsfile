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

                sh "echo clustername=${clustername}.prod.datasinkcloud.com zones=${awszone} node-count=${nodes} node-size=${instancesize}"
                sh "kops create cluster  --name ${clustername}.prod.datasinkcloud.com \
                    --zones ${awszone} \
                    --node-count ${nodes} \
                    --node-size ${instancesize} \
                    --state s3://datasink1 \
                    --authorization=AlwaysAllow \
                    --dns-zone prod.datasinkcloud.com \
                    --networking calico \
                    --cloud aws \
                    --vpc vpc-011182937a1c08a0c \
                    --node-security-groups sg-0e4c56374753a2917 \
                    --image 099720109477/ubuntu/images/hvm-ssd/ubuntu-xenial-16.04-amd64-server-20180306"

                sh "kops delete secret sshpublickey admin --name ${clustername}.prod.datasinkcloud.com --state s3://datasink1"
                sh "kops create secret --name ${clustername}.prod.datasinkcloud.com sshpublickey admin -i ~/.ssh/id_rsa.pub --state s3://datasink1"
                sh "kops update cluster ${clustername}.prod.datasinkcloud.com --state s3://datasink1 --yes"
            }
        }
        stage('Deploying Kube Cluster') {
            steps {
                timeout(time: 10, unit: 'MINUTES') {
                    waitUntil {
                       script {
                         def r = sh script: "kops validate cluster --name ${clustername}.prod.datasinkcloud.com --state s3://datasink1", returnStatus: true
                         return (r == 0);
                       }
                    }
                }
            }
        }
        stage('Deploying Kafka Helm Chart') {
            steps {
                timeout(time: 10, unit: 'MINUTES') {
                    sh 'kubectl create secret docker-registry docker-secret --docker-username=datasinkio --docker-password=$DOCKERHUB_PW --docker-email=datasinkio'

                    sh 'chmod +x ./scripts/serviceaccount.sh'
                    sh './scripts/serviceaccount.sh'

                    echo 'helm init deployes tiller in kube cluster'
                    sh "helm init"
                    echo  'Starting sleep to allow tiller startup'
                    sleep 20
                    echo  'Finished sleep'

                    sh "helm repo add dskafka https://cranfss.github.io/dskafka"

                    /* helm install --name ${clustername} dskafka/dfkafka stopped working */
                    sh "helm fetch dskafka/dskafka"
                    
                    /*sh "helm install --name ${clustername} dskafka/dfkafka"*/
                    sh "helm install --name ${clustername} dskafka-0.7.1.tgz"

                    echo 'Verify Kafka Cluster if available'
                    
                    sh 'chmod +x ./scripts/verify-release.sh'
                    sh './scripts/verify-release.sh default'
                }
            }
        }
        stage('Internal - verify Kafka produce/consume') {
            steps {
                sh "helm test ${clustername} --timeout 300 --debug"
            }
        }
        stage('External - verify Kafka produce/consume') {
            steps {
                      sh 'chmod +x ./scripts/verifyexternalkafka.py'
                      sh './scripts/verifyexternalkafka.py --numnodes ${nodes} '
            }
        }/*
        stage('Deploy Prometheus') {
            steps {
                sh "helm install -f ./prometheus-values.yaml stable/prometheus --name prometheus --set rbac.create=false"
            }
        }*/
    }
}
