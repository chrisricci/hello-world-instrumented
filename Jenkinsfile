#!groovy
  
def project = 'chris_ricci'
def appName = 'hello-world-instrumented'
def feSvcName = "${appName}"
def namespace = 'monitoring-demo'
def imageTag = "quay.io/${project}/${appName}:v${env.BUILD_NUMBER}"

node {
  checkout scm
  sh("printenv")
	
  stage 'Login to Quay.io'
  sh("docker login -u=\"${env.quay_username}\" -p=\"${env.quay_password}\" quay.io")
	
  stage 'Build image'
  sh("docker build -t ${imageTag} .")

//  stage 'Run Go tests '
//  sh("docker run ${imageTag} go test")

  stage 'Push image to Quay.io registry'
  sh("docker push ${imageTag}")

  stage "Deploy Canary"
//  switch (env.BRANCH_NAME) {
//     case "master":  
         // Roll out to canary environment
         // Change deployed image in canary to the one we just built
         sh("sed -i.bak 's#quay.io/${project}/${appName}:.*\$#${imageTag}#' ./k8s/canary/*.yaml")
//	 sh("sed -i.bak 's#python-api-canary#python-api-v${env.BUILD_NUMBER}#' ./k8s/canary/*.yaml")
         sh("kubectl --namespace=${namespace} apply -f k8s/services/")
         sh("kubectl --namespace=${namespace} apply -f k8s/canary/")
//    break
//    default:
//    break
//  }
}
def didTimeout = false
def userInput = true
try {
  timeout(time:5, unit:'DAYS') {
    userInput = input(
      id: 'promoteToProd', message: 'Approve rollout to production?', parameters: [
      [$class: 'BooleanParameterDefinition', defaultValue: 'true', description: 'Approve', name: 'Approve?']
    ])
  }
} catch(Exception err) { // timeout reached or input false
  def user = err.getCause()[0].getUser()
  if('SYSTEM' == user.toString()) { //SYSTEM means timeout reached
    didTimeout = true
  } else {
    userInput = false
    echo "Aborted by: [${user}]"
  }
}

node{ 
  if (didTimeout) {
    // Perhaps roll back?
    echo "no input received before timeout"
  } else if (userInput == true) {         
    // Roll out to production environment
    // Change deployed image in canary to the one we just built
    sh("sed -i.bak 's#quay.io/${project}/${appName}:.*\$#${imageTag}#' ./k8s/production/*.yaml")
    //sh("kubectl --namespace=${namespace} apply -f k8s/services/")
    sh("kubectl --namespace=${namespace} apply -f k8s/production/")
  } else {
    // Roll back?
    echo "Rollout Aborted"
    currentBuild.result = 'FAILURE'
  }  
}
