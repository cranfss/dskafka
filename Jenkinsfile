/*
    This is the main pipeline section with the stages of the CI/CD
 */

node {

    stage('Clone repository') {
        /* Let's make sure we have the repository cloned to our workspace */

        checkout scm
    }

    stage('Deploy kube cluster') {

        kops create -f kopsconfig.yaml
        kops create secret --name datasink1.k8s.local sshpublickey admin -i ~/.ssh/id_rsa.pub
        kops update cluster datasink1.k8s.local --yes

    }
}
