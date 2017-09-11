#!groovy
  
// def project = 'chris_ricci'
// def appName = 'hello-world-instrumented'
//def repo = "${env.REPO_NAME}"
//def project = "${env.PROJECT}"
//def appName = "${env.APP_NAME}"
// def feSvcName = "${appName}"
// def namespace = "${env.NAMESPACE}"
//def namespace = 'monitoring-demo'
// def imageTag = "quay.io/${project}/${appName}:v${env.BUILD_NUMBER}"
def imageTag = "${env.REPO_NAME}/${env.PROJECT}/${env.APP_NAME}:v${env.BUILD_NUMBER}"
def prevImageTag = ''
def prevBuildNum = ''
def firstDeploy = false

node {
  // Check if there's a previous deployment, if so, get the image version so we can rollback if needed
  try {
    prevImageTag = sh(
      script: "kubectl get deployment hello-world-canary -n ${env.NAMESPACE} -o jsonpath='{.spec.template.spec.containers[0].image}'",
      returnStdout: true
    ).trim()
    echo "Previous Image: ${prevImageTag}"
    prevBuildNum = prevImageTag.split(':')[1]
    echo "Previous Build Version: ${prevBuildNum}"
  } catch (err) {
    echo "No Previous Deployment"
    firstDeploy = true
  }

  checkout scm
  sh("printenv")
	
  stage 'Login to Quay'
	sh("docker login -u=\"${env.quay_username}\" -p=\"${env.quay_password}\" ${env.REPO_NAME}")
	
  stage 'Build image'
  sh("docker build -t ${env.repo_name}/${env.PROJECT}/${env.APP_NAME}:v${env.BUILD_NUMBER} .")

  stage 'Push image to Quay registry'
  sh("docker push ${env.repo_name}/${env.PROJECT}/${env.APP_NAME}:v${env.BUILD_NUMBER}")

  // If this is the first deployment
  if (firstDeploy) {
    stage 'First Deployment'
    // Update images in manifests with current build
    sh("sed -i.bak 's#${env.REPO_NAME}/${env.PROJECT}/${env.APP_NAME}:.*\$#${env.REPO_NAME}/${env.PROJECT}/${env.APP_NAME}:v${env.BUILD_NUMBER}#' ./k8s/canary/*.yaml")
    sh("sed -i.bak 's#${env.REPO_NAME}/${env.PROJECT}/${env.APP_NAME}:.*\$#${env.REPO_NAME}/${env.PROJECT}/${env.APP_NAME}:v${env.BUILD_NUMBER}#' ./k8s/production/*.yaml")
    sh("kubectl --namespace=${env.NAMESPACE} apply -f k8s/services/")
    sh("kubectl --namespace=${env.NAMESPACE} apply -f k8s/canary/")
    sh("kubectl --namespace=${env.NAMESPACE} label deployment hello-world-canary --overwrite version=v${BUILD_NUMBER}")
    sh("kubectl --namespace=${env.NAMESPACE} label pod  -l env=canary --all --overwrite version=v${BUILD_NUMBER}")

    sh("kubectl --namespace=${env.NAMESPACE} apply -f k8s/production/")
    sh("kubectl --namespace=${env.NAMESPACE} label deployment hello-world-production --overwrite version=v${BUILD_NUMBER}")
    sh("kubectl --namespace=${env.NAMESPACE} label pod  -l env=production --all --overwrite version=v${BUILD_NUMBER}")
    currentBuild.result = 'SUCCESS'   
    return
  } else {
    // Roll out to canary environment
    stage "Deploy Canary"
    
    // Change deployed image in canary to the one we just built
    sh("kubectl --namespace=${env.NAMESPACE} set image deployment/hello-world-canary hello-world=${env.repo_name}/${env.PROJECT}/${env.APP_NAME}:v${env.BUILD_NUMBER}")
    
    // Apply version label to deployment
    sh("kubectl --namespace=${env.NAMESPACE} label deployment hello-world-canary --overwrite version=v${BUILD_NUMBER}")
    sh("kubectl --namespace=${env.NAMESPACE} label pod  -l env=canary --all --overwrite version=v${BUILD_NUMBER}")
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

      // Change deployed image in canary to the previous image
    	sh("kubectl --namespace=${env.NAMESPACE} set image deployment/hello-world-canary hello-world=${prevImageTag}")	
    	sh("kubectl --namespace=${env.NAMESPACE} label deployment hello-world-canary --overwrite version=${prevBuildNum}")
      sh("kubectl --namespace=${env.NAMESPACE} label pod  -l env=canary --all --overwrite version=${prevBuildNum}")

    }
    error('Aborted')
  }

  if (!firstDeploy) {
  stage 'Rollout to Production' 
    // Roll out to production environment
    // Change deployed image in canary to the one we just built
    //sh("sed -i.bak 's#quay.io/${project}/${appName}:.*\$#${imageTag}#' ./k8s/production/*.yaml")
    //sh("kubectl --namespace=${namespace} apply -f k8s/production/")
    sh("kubectl --namespace=${env.NAMESPACE} set image deployment/hello-world-production hello-world=${env.repo_name}/${env.PROJECT}/${env.APP_NAME}:v${env.BUILD_NUMBER}")
    sh("kubectl --namespace=${env.NAMESPACE} label deployment hello-world-production --overwrite version=v${BUILD_NUMBER}")
    sh("kubectl --namespace=${env.NAMESPACE} label pod  -l env=production --all --overwrite version=v${BUILD_NUMBER}")
    currentBuild.result = 'SUCCESS'
  }
}

