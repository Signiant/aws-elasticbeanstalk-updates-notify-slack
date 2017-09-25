# elasticbeanstalk-updates-notify-slack
Posts Slack notifications when an AWS Elastic Beanstalk managed update is applied to an environment

[![Build Status](https://travis-ci.org/Signiant/aws-elasticbeanstalk-updates-notify-slack.svg?branch=master)](https://travis-ci.org/Signiant/aws-elasticbeanstalk-updates-notify-slack)

# Purpose
Notifies a slack channel when an [AWS Elastic beanstalk managed platform update](http://docs.aws.amazon.com/elasticbeanstalk/latest/dg/environment-platform-update-managed.html) is applied to an environment.

# Sample Output

![Sample Slack Posts](https://raw.githubusercontent.com/Signiant/aws-elasticbeanstalk-updates-notify-slack/master/images/slack-sample.jpg)

# Installing and Configuring

## Slack Setup
Before installing anything to AWS, you will need to configure a "bot" in Slack to handle the posts for you.  To do this:
* In Slack, choose _Manage Apps_ -> _Custom Integrations_ -> _Bots_
  * Add a new bot configuration
  * username: beanstalk-notifier
  * Copy the API Token.
  * Don't worry about other parameters - the notifier over-rides them anyway
* In Slack, upload a custom emoji and name it _:elasticbeanstalk:_
  * You can use any image here...one is provided in the _emoji_ folder of this project also

## AWS Setup
* Grab the latest Lambda function zip from [Releases](https://github.com/Signiant/aws-elasticbeanstalk-updates-notify-slack/releases)
* Create a new cloudformation stack using the template in the cfn folder

The stack asks for the function zip file location in S3, the slack API Key and the slack channel to post notifications to. Once the stack is created, a cloudwatch event is created to subscribe the lambda function to the `UpdateEnvironment` elastic beanstalk call. The event is then further interrogated to see if it's an environment update.
