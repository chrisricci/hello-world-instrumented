#!groovy
  
def project = 'chris_ricci'
def appName = 'hello-world-instrumented'
def feSvcName = "${appName}"
def namespace = 'monitoring-demo'
def imageTag = "quay.io/${project}/${appName}:v${env.BUILD_NUMBER}"
def prevImageTag = ''
def prevBuildNum = ''

node {
  try {
    prevImageTag = sh(
      script: "kubectl get deployment hello-world-canary -n ${namespace} -o jsonpath='{.spec.template.spec.containers[0].image}'",
      returnStdout: true
    ).trim()
    echo "Previous Image: ${prevImageTag}"
    prevBuildNum = prevImageTag.split(':')[1]
    echo "Previous Build Version: ${prevBuildNum}"
  } catch (err) {
    echo "No Previous Deployment"
  }

  checkout scm
  sh("printenv")
	
  stage 'Login to Quay.io'
  sh("docker login -u=\"${env.quay_username}\" -p=\"${env.quay_password}\" quay.io")
	
  stage 'Build image'
  sh("docker build -t ${imageTag} .")

  stage 'Push image to Quay.io registry'
  sh("docker push ${imageTag}")

  stage "Deploy Canary"
  // Roll out to canary environment
  // Change deployed image in canary to the one we just built
  sh("sed -i.bak 's#quay.io/${project}/${appName}:.*\$#${imageTag}#' ./k8s/canary/*.yaml")
  sh("sed -i.bak 's#version:.*\$#version: v${env.BUILD_NUMBER}#' ./k8s/canary/*.yaml")
  sh("kubectl --namespace=${namespace} apply -f k8s/services/")
  sh("kubectl --namespace=${namespace} apply -f k8s/canary/")
}
stage 'Verify Canary'
def didTimeout = false
def userInput = true
try {
  timeout(time:1, unit:'DAYS') {
      userInput = input(id: 'promoteToProd', message: 'Approve rollout to production?')
      echo "userInput: [${userInput}]" 
  }
} catch(err) { // timeout reached or input false
    stage 'Rolling Back Canary'
    echo "Rollout Aborted"
    echo "userInput: [${userInput}]"
    currentBuild.result = 'FAILURE'

    // If there was a previous deployment, roll it back
    if (prevImageTag != '') {
      echo "Rolling back to: ${prevImageTag}"
      node{
        checkout scm 
        sh("sed -i.bak 's#${imageTag}\$#${prevImageTag}#' ./k8s/canary/*.yaml")
        sh("sed -i.bak 's#version:.*\$#version: ${prevBuildNum}#' ./k8s/canary/*.yaml")
        sh("kubectl --namespace=${namespace} apply -f k8s/services/")
        sh("kubectl --namespace=${namespace} apply -f k8s/canary/")
      }
    }
    error('Aborted')
}

stage 'Rollout to Production'
node{ 
  checkout scm 
  // Roll out to production environment
  // Change deployed image in canary to the one we just built
  sh("sed -i.bak 's#quay.io/${project}/${appName}:.*\$#${imageTag}#' ./k8s/production/*.yaml")
  sh("sed -i.bak 's#version:.*\$#version: v${env.BUILD_NUMBER}#' ./k8s/production/*.yaml")
  sh("kubectl --namespace=${namespace} apply -f k8s/production/")
  currentBuild.result = 'SUCCESS'
}
