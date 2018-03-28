/*
    This is the main pipeline section with the stages of the CI/CD
 */
pipeline {

    options {
        // Build auto timeout
        timeout(time: 60, unit: 'MINUTES')
	}


// In this example, all is built and run from the master
agent { node { label 'master' } }

// Pipeline stages
stages {

    ////////// Step 1 //////////
    stage('Git clone and deploy kube cluster') {
    	steps {
            echo "Check out acme code"
            checkout scm

            // Create kubectl/kops cluster
            kops create -f kopsconfig.yaml
            kops delete secret sshpublickey "admin"
            kops create secret --name datasink1.k8s.local sshpublickey admin -i ~/.ssh/id_rsa.pub
            kops update cluster datasink1.k8s.local --yes

            // Init helm client
            //sh "helm init"

        }
    }    
}
