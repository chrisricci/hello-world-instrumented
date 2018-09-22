openshift.withCluster() {
    env.APP_NAME = 'hello-world-instrumented'
    env.APP_NAME_CANARY = "${APP_NAME}-canary"
    env.CICD_NAMESPACE = 'myproject'
    env.DEPLOY_NAMESPACE = 'hello'
    replicaCount = 3
}

pipeline {
    agent any
    stages {

        /*************
         * Build
         *************/
        stage("Create build config") {
            when{
                not { expression {
                        openshift.withCluster() {
                            return openshift.selector('bc', APP_NAME).exists()
                        }
                    }
                }
            }
            steps {
                echo "Create build config ${APP_NAME} in namespace " + openshift.withCluster() { openshift.project() }
                script {
                    openshift.withCluster() {
                        //Binary build config, so it has no git source, and not started automatically.
                        //Must be started manually by giving the 'from-dir'
                        openshift.newBuild("--binary", "--name=${APP_NAME}" , "--strategy=docker")
                    }
                }
            }
        }

        stage("Build image") {
            steps {
                script {
                    openshift.withCluster() {
                        buildSelector = openshift.selector('bc', APP_NAME).startBuild("--from-dir=.", "--wait")
                        //if (buildSelector.object().status.phase != "Complete") error("Build failed: ${buildSelector.object().status.message}") //Process stops without this
                        echo "Build complete: " + buildSelector.names()
                    }
                }
            }
        }

        /*************
         * Canary deployment
         *************/
        //Need permission: oc policy add-role-to-user edit system:serviceaccount:myproject:jenkins -n $DEPLOY_PROJECT
        stage("Canary deployment") {
            steps {
                script {
                    openshift.withCluster() {
                        openshift.withProject("$DEPLOY_NAMESPACE") {
                            //Tag latest rom build namespace
                            openshift.tag("$CICD_NAMESPACE/$APP_NAME:latest", "$DEPLOY_NAMESPACE/$APP_NAME_CANARY:latest")

                            if (!openshift.selector('dc', APP_NAME_CANARY).exists()) {
                                /***
                                 * First deployment
                                 **/
                                echo "Create deployment config ${APP_NAME_CANARY} in namespace ${DEPLOY_NAMESPACE}"

                                //The canary deployment also has it's own image stream in this namespace.
                                //Create new app
                                def newAppSelector = openshift.newApp("$DEPLOY_NAMESPACE/$APP_NAME_CANARY", "--name=${APP_NAME_CANARY}",  "--labels=service=${APP_NAME}")

                                //Optionally add readiness/liveness probes
                                //openshift.set("probe dc/$APP_NAME_CANARY --readiness --get-url=http://:8080/health --initial-delay-seconds=10 --failure-threshold=10 --period-seconds=10")
                                //openshift.set("probe dc/$APP_NAME_CANARY --liveness  --get-url=http://:8080/health --initial-delay-seconds=120 --failure-threshold=10 --period-seconds=10")

                                //wait for rollout
                                def rolloutResult = openshift.selector('dc', APP_NAME_CANARY).rollout().status()
                                if (rolloutResult.status != 0) error("First rollout for DeploymentConfig ${APP_NAME_CANARY} failed.")
                                //wait for pods to start
                                def latestVersion = openshift.selector('dc', APP_NAME_CANARY).object().status.latestVersion
                                timeout(2) {
                                    openshift.selector('rc', "${APP_NAME_CANARY}-${latestVersion}").untilEach(1) {
                                        def rcMap = it.object()
                                        return (rcMap.status.replicas.equals(rcMap.status.readyReplicas))
                                    }
                                }
                                echo "Canary pods up: " + newAppSelector.narrow("dc").related("pods").names()

                                //Remove automatic trigger from DeploymentConfig. It may stop the first deployment if removed too early
                                openshift.set("triggers", "dc/$APP_NAME_CANARY", "--manual")
                                //Delete service and is, not needed
                                newAppSelector.narrow("svc").delete()

                            } else {
                                /***
                                 * Rollout
                                 **/
                                openshift.selector('dc', APP_NAME_CANARY).rollout().latest()
                                //wait for rollout
                                def rolloutResult = openshift.selector('dc', APP_NAME_CANARY).rollout().status()
                                if (rolloutResult.status != 0) error("Rollout for DeploymentConfig ${APP_NAME_CANARY} failed.")
                                //wait for pods to start
                                def latestVersion = openshift.selector('dc', APP_NAME_CANARY).object().status.latestVersion
                                timeout(2) {
                                    openshift.selector('rc', "${APP_NAME_CANARY}-${latestVersion}").untilEach(1) {
                                        def rcMap = it.object()
                                        return (rcMap.status.replicas.equals(rcMap.status.readyReplicas))
                                    }
                                }
                                echo "Canary pods up: " + openshift.selector('pod',['deployment':"$APP_NAME_CANARY-${latestVersion}"]).names()
                            }
                        }
                    }
                }
            }
        }


        /*************
         * Ask to promote - when productionDc.exists()
         *************/
        stage("Input to promote") {
            when { //Only if production deployment already exists, otherwise automatically deploy there
                expression {
                    openshift.withCluster() {
                        openshift.withProject("$DEPLOY_NAMESPACE") {
                            return openshift.selector('dc', APP_NAME).exists()
                        }
                    }

                }
            }
            steps {
                script {
                    promoteOrRollback = input message: 'Promote or rollback canary deployment?',
                            parameters: [choice(name: "Promote or Rollback?", choices: 'Promote\nRollback', description: '')]
                }
            }
        }

        stage("Rollback canary"){
            when{
                expression {
                    return binding.hasVariable('promoteOrRollback') && promoteOrRollback == 'Rollback'
                }
            }
            steps{
                echo "Rollback for canary deployment."
                script {
                    openshift.withCluster {
                        openshift.withProject("$DEPLOY_NAMESPACE") {
                            def rolloutResult = openshift.selector('dc', APP_NAME_CANARY).rollout().undo()
                            if (rolloutResult.status != 0) error("Rollback for DeploymentConfig ${APP_NAME_CANARY} failed.")
                            //wait for pods to start
                            def latestVersion = openshift.selector('dc', APP_NAME_CANARY).object().status.latestVersion
                            timeout(2) {
                                openshift.selector('rc', "${APP_NAME_CANARY}-${latestVersion}").untilEach(1) {
                                    def rcMap = it.object()
                                    return (rcMap.status.replicas.equals(rcMap.status.readyReplicas))
                                }
                            }
                            echo "Canary pods rolled back: " + openshift.selector('pod',['deployment':"$APP_NAME_CANARY-${latestVersion}"]).names()
                            openshift.tag("$DEPLOY_NAMESPACE/$APP_NAME:latest", "$DEPLOY_NAMESPACE/$APP_NAME_CANARY:latest")
                        }
                    }
                }

            }
        }



        /*************
         * Production deployment
         *************/
        stage("Production deployment") {
            when{
                not {
                    expression {
                        return binding.hasVariable('promoteOrRollback') && promoteOrRollback == 'Rollback'
                    }
                }
            }
            steps {
                script {
                    openshift.withCluster() {
                        openshift.withProject("$DEPLOY_NAMESPACE") {
                            //Tag latest from build namespace
                            openshift.tag("$CICD_NAMESPACE/$APP_NAME:latest", "$DEPLOY_NAMESPACE/$APP_NAME:latest")

                            if (!openshift.selector('dc', APP_NAME).exists()) {
                                /***
                                 * First deployment
                                 **/
                                echo "Create deployment config ${APP_NAME} in namespace ${DEPLOY_NAMESPACE}"

                                //Create new app
                                def newAppSelector = openshift.newApp("$DEPLOY_NAMESPACE/$APP_NAME", "--name=${APP_NAME}", "--labels=service=${APP_NAME}")
                                //wait for rollout
                                def rolloutResult = openshift.selector('dc', APP_NAME).rollout().status()
                                if (rolloutResult.status != 0) error("First rollout for DeploymentConfig ${APP_NAME} failed.")

                                //Scale up
                                openshift.selector('dc', APP_NAME).scale("--replicas=${replicaCount}")
                                //wait for pods to start
                                def latestVersion = openshift.selector('dc', APP_NAME).object().status.latestVersion
                                timeout(3) {
                                    openshift.selector('rc', "${APP_NAME}-${latestVersion}").untilEach(1) {
                                        def rcMap = it.object()
                                        return (rcMap.status.replicas.equals(rcMap.status.readyReplicas))
                                    }
                                }
                                echo "Pods up: " + newAppSelector.narrow("dc").related("pods").names()

                                //Remove automatic trigger from DeploymentConfig
                                openshift.set("triggers", "dc/$APP_NAME", "--manual")

                                //Modify Service so the canary pods are also included, remove deploymentconfig label from selector
                                def newService = newAppSelector.narrow("svc").object()
                                newService.spec.selector = ['service': "$APP_NAME"]
                                openshift.replace(newService)
                                //Create route
                                newAppSelector.narrow("svc").expose()

                            } else {
                                /***
                                 * Rollout
                                 **/
                                openshift.selector('dc', APP_NAME).rollout().latest()
                                //wait for rollout
                                def rolloutResult = openshift.selector('dc', APP_NAME).rollout().status()
                                if (rolloutResult.status != 0) error("Rollout for DeploymentConfig ${APP_NAME} failed.")

                                //wait for pods to start
                                def latestVersion = openshift.selector('dc', APP_NAME).object().status.latestVersion
                                timeout(3) {
                                    openshift.selector('rc', "${APP_NAME}-${latestVersion}").untilEach(1) {
                                        def rcMap = it.object()
                                        return (rcMap.status.replicas.equals(rcMap.status.readyReplicas))
                                    }
                                }
                                echo "Pods up: " + openshift.selector('pod',['deployment':"$APP_NAME-${latestVersion}"]).names()
                            }

                        }
                    }
                }
            }
        }
    }
}