## Demonstration of Canary Release Continuous Delivery Pipeline on Kubernetes With Automated Rollbacks
### Abstract

The rise of CI/CD adoption in the enterprise has been one of the major trends that has fueled the adoption of container technologies like Docker and Kubernetes. Containerization and advanced orchestration go hand-in-hand with the rapid iterations of CI/CD-based development.

In this overview and demonstration, you will learn how to quickly and easily spin up a continuous delivery pipeline using Kubernetes, Jenkins, and Helm. In addition, we will show how you can minimize risk by finding production issues early using prometheus for application monitoring and perform automated rollbacks.

[The accompanying webinar](https://www.brighttalk.com/webcast/14601/267207/continuous-deployment-and-monitoring-with-tectonic-prometheus-and-jenkins) will cover why CI/CD tools like Jenkins and Kubernetes platforms like CoreOS Tectonic are a perfect match. We will also describe common integration patterns, how to configure the Jenkins Plugin for Kubernetes, and show how to build advanced deployment pipelines with Jenkinsfiles.

### Supporting continuous delivery and deployment on CoreOS Tectonic

Marc Andreessen famously declared that software is eating the world. Business processes and even whole industries are being displaced by software, and the trend isn't slowing down. The pressure to deliver change faster continues to mount in tandem with software’s increasing reach and sophistication. Continuous delivery and deployment processes are becoming the norm to shorten development cycles as organizations adapt to stay competitive.

Cloud and DevOps are key enablers to accelerated application delivery. Yet enterprises face many challenges, both organizationally and technically, that keep them from achieving their goals. Saying you'll implement a continuous delivery and deployment pipeline is one thing, but actually succeeding at it is another.

An organization must have complete confidence in its deployment process, not just in its ability to deliver high quality, bug-free code, but also in its ability to respond and recover quickly if things go sideways with the latest release. Concerns about risk and quality become inhibitors to success. This is where containerization can help.

Containerization technology has emerged as an important ingredient for DevOps transformations and a safe and easy on-ramp into the cloud. At CoreOS, we've led the creation of the containerization market since 2014 and have been working with large organizations to implement their container strategies using Tectonic, our enterprise-ready Kubernetes platform. And as it happens, Tectonic makes it easy to set up advanced deployment processes.

### A Canary on Kubernetes

For example, let's say you wanted to set up a canary deployment model. If you are not familiar with the concept, a canary test is a DevOps pattern for continuous deployment where you deliver new versions of your application to just a small subset of your user base at first. This allows you to get feedback from production users without the risk of deploying a breaking change to your entire user base. If the canary tests are successful, then you can roll the change out to the rest of the end users. If they are not successful, it’s easy to roll the change back.

Using Tectonic, one way to set up the canary deployment might be to use a combination of Deployments, Services, and Labels/Selectors. For example, you might have two Deployments – Production and Canary – and a Service that load balances between them. To ensure that too much traffic doesn't go to the Canary, you'd deploy Production with four replicas and Canary with only one, which would direct 20 percent of the traffic to the Canary.

[Webinar: Continuous Deployment and Monitoring with Tectonic, Prometheus, and Jenkins](https://www.brighttalk.com/webcast/14601/267207/continuous-deployment-and-monitoring-with-tectonic-prometheus-and-jenkins)

[Click here](https://www.brighttalk.com/webcast/14601/267207/continuous-deployment-and-monitoring-with-tectonic-prometheus-and-jenkins) to see a video demo of how to set up a Canary deployment on Tectonic.

Using a Jenkins Pipeline, when changes are committed to the Canary branch a build will be triggered and the new version will be rolled out to all replicas in the Canary deployment (in this case, just one). Once the change is validated, usually via some automated testing and health checks, the changes can be pushed to the Production branch, which will trigger the Jenkins Pipeline to update all replicas in the Production deployment.

If you'd like to see how it's done, we've put together [a webinar to walk you through the process](https://www.brighttalk.com/webcast/14601/267207/continuous-deployment-and-monitoring-with-tectonic-prometheus-and-jenkins). As an added bonus, we'll show you how to use Tectonic's fully integrated monitoring capabilities powered by Prometheus. While we include built-in monitoring for the Tectonic infrastructure, this demo shows how you can extend these capabilities to your own applications running on Tectonic, giving you the feedback you need to confidently deliver changes at the speed of your organization.

If you'd like to follow along with the demo on your own system, it's easy to get started. You can [try out Tectonic](https://coreos.com/tectonic) with a license that lets you deploy up to 10 nodes for free. If you need additional help getting set up, we have a selection of [hands-on tutorials](https://coreos.com/tectonic/docs/latest/tutorials/) available.
