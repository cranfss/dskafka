/*
    This is the main pipeline section with the stages of the CI/CD
 */

node {

    stage('Clone repository') {
        /* Let's make sure we have the repository cloned to our workspace */

        checkout scm
    }

    stage('Deploy kube cluster') {

        //sh "/usr/local/bin/kops create cluster  --name jenkins.k8s.local --state s3://datasink1 --zones us-west-1a"
        sh "/usr/local/bin/kops delete secret sshpublickey admin --name jenkins.k8s.local"
        sh "/usr/local/bin/kops create secret --name jenkins.k8s.local sshpublickey admin -i ~/.ssh/id_rsa.pub --state s3://datasink1"
        sh "/usr/local/bin/kops update cluster jenkins.k8s.local --state s3://datasink1 --yes"

    }
    stage('Validate cluster creation') {

        //sh "/usr/local/bin/kops validate cluster --state s3://datasink1"
    }
    stage('Tear down cluster') {
        
        //sh "/usr/local/bin/kops delete cluster --name jenkins.k8s.local --state s3://datasink1 --yes"
    }
}
