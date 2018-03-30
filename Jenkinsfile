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

        timeout(time: 5, unit: 'MINUTES') {
            waitUntil {
               script {
                 def r = sh script: 'kops validate cluster --name jenkins.k8s.local --state s3://datasink', returnStatus: true
                 return (r == 0);
               }
            }
        }
    }
    stage('Tear down cluster') {
        
        //sh "kops delete cluster --name jenkins.k8s.local --state s3://datasink1 --yes"
    }
}
