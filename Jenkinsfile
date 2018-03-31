/*
    This is the main pipeline section with the stages of the CI/CD
 */

node {

    stage('Clone repository') {
        /* Let's make sure we have the repository cloned to our workspace */

        checkout scm
    }

    stage('Deploy kube cluster') {

        sh "kops create cluster  --name jenkins.k8s.local --state s3://datasink1 --zones us-west-1a"
        sh "kops delete secret sshpublickey admin --name jenkins.k8s.local --state s3://datasink1"
        sh "kops create secret --name jenkins.k8s.local sshpublickey admin -i ~/.ssh/id_rsa.pub --state s3://datasink1"
        sh "kops update cluster jenkins.k8s.local --state s3://datasink1 --yes"

    }
    stage('Validate cluster creation') {

        timeout(time: 6, unit: 'MINUTES') {
            waitUntil {
               script {
                 def r = sh script: "kops validate cluster --name jenkins.k8s.local --state s3://datasink1", returnStatus: true
                 return (r == 0);
               }
            }
        }
    }
    stage('Deploy Kafka Helm Chart') {

        sh "kubectl create secret generic docker-config --from-file=$HELM_HOME/.docker/config.json"
        
        echo 'helm init deployes tiller in kube cluster'
        sh "helm init"
        sh "helm repo add dskafka https://cranfss.github.io/dskafka"
        echo  'Starting sleep to allow tiller startup'
        sleep 10
        echo  'Finished sleep'
        sh "helm install --name kafka dskafka/dfkafka"

    }
    stage('Tear down cluster') {
        
        //sh "kops delete cluster --name jenkins.k8s.local --state s3://datasink1 --yes"
    }
}
