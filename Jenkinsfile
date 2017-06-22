node {
  def project = 'chris_ricci'
  def appName = 'hello-world-instrumented'
  def feSvcName = "${appName}"
  def namespace = 'monitoring-demo'
  def imageTag = "quay.io/${project}/${appName}:${env.BRANCH_NAME}.v${env.BUILD_NUMBER}"
  checkout scm

  stage 'Printenv'
  sh("printenv")
	
  stage 'Login to Quay.io'
  sh("docker login -u=\"${env.quay_username}\" -p=\"${env.quay_password}\" quay.io")
	
  stage 'Build image'
  sh("docker build -t ${imageTag} .")

//  stage 'Run Go tests '
//  sh("docker run ${imageTag} go test")

  stage 'Push image to Quay.io registry'
  sh("docker push ${imageTag}")

  stage "Deploy Application"
  switch (env.BRANCH_NAME) {
     case "canary":  
         // Roll out to canary environment
         // Change deployed image in canary to the one we just built
         sh("sed -i.bak 's#quay.io/${project}/${appName}:.*\$#${imageTag}#' ./k8s/canary/*.yaml")
//	 sh("sed -i.bak 's#python-api-canary#python-api-v${env.BUILD_NUMBER}#' ./k8s/canary/*.yaml")
         sh("kubectl --namespace=${namespace} apply -f k8s/services/")
         sh("kubectl --namespace=${namespace} apply -f k8s/canary/")
    break

    case "production":
         // Roll out to production environment
         // Change deployed image in canary to the one we just built
         sh("sed -i.bak 's#quay.io/${project}/${appName}:.*\$#${imageTag}#' ./k8s/production/*.yaml")
//	 sh("sed -i.bak 's#python-api-production#python-api-v${env.BUILD_NUMBER}#' ./k8s/production/*.yaml")
         sh("kubectl --namespace=${namespace} apply -f k8s/services/")
         sh("kubectl --namespace=${namespace} apply -f k8s/production/")
    break

    default:
    break    
  }
}
