## About The Project

If the presenter is provided with objective feedback on the presentation, the presenter can improve their own shortcomings and grow.

This service provides feedback on presentations to presenters at seminars, lectures, conferences, and speeches.

During the presentation, a camera captures the audience and analyzes their facial expressions to predict their emotions and moods.

The predicted data is processed and visualized as a time series, and after the presentation, the presenter can view the results through a dashboard.
For example, a presenter can check why people were focused and bored during a speech.

In addition, it can be used to analyze audience reactions in concert halls, classical concerts, and magic shows.


### Architecture Diagram
<p align="center">
  <img width="720px" src="https://user-images.githubusercontent.com/64878866/147388208-ceb1e322-41f8-4793-be6a-fe8ee9882cee.png" />
</p>


### Built With
- Python, Flask, Elasticsearch, Kibana
- Raspberry Pi 4B, PiCamera, OpenCV, GPIO
- AWS : S3, SQS, Lambda, Rekognition, Opensearch


## Project Demo
1. Setting Camera & Start
   <p float="left">
     <img width="40%" src="https://user-images.githubusercontent.com/64878866/147388711-03aa9a16-f794-4ffb-bd23-2f4e2bc1a3af.png" />
     <img width="40%" src="https://user-images.githubusercontent.com/64878866/147388714-796f84d1-ebf6-49fc-a9a4-8a0409ac18b4.jpg" />
   </p>
   (Due to the pandemic, gatherings were limited, so the demo was replaced with BTS' YouTube video.)

2. S3 Bucket & SQS Pipeline
   <p float="left">
     <img width="40%" src="https://user-images.githubusercontent.com/64878866/147388875-e354cfc3-772a-4e7b-b938-a439e4f611df.png" />
     <img width="40%" src="https://user-images.githubusercontent.com/64878866/147388878-273b51e4-8441-4c6b-a124-2c3cc02bd187.png" />
   </p>

3. Lambda & Elasticsearch
   <p float="left">
     <img width="40%" src="https://user-images.githubusercontent.com/64878866/147389055-e1262d24-e585-479b-bbb6-80702a8c48b5.png" />
     <img width="40%" src="https://user-images.githubusercontent.com/64878866/147389072-92320c21-8df0-4dfe-b12c-5a23da3a6076.png" />
   </p>

4. Kibana Dashboard
   <p float="left">
     <img width="780px" src="https://user-images.githubusercontent.com/64878866/147389364-aa5cb9c7-dce8-4d02-80c1-332292c8e50d.png" />
   </p>



## Getting Started

#### Raspberry Pi
1. Camera Module
   - Used Accessory : Raspberry Pi Camera Module V2
   - Raspbian Setting
      ```
      # P1 Camera Enable
      $ sudo raspi-config
       3. Interface Options -> P1 Camera -> Enable -> reboot
      
      # check picamera
      $ vcgencmd get_camera
        supported=1 detected=1
      ```

2. Flask Web Application
   - Install & Dependencies
      ```
      $ sudo apt-get update
      $ sudo apt-get upgrade
      $ sudo apt-get install python3-flask
      
      $ sudo pip3 install numpy
      $ sudo pip3 install opencv-contrib-python
      $ sudo pip3 install opencv-python
      $ sudo pip3 install imutils
      $ sudo pip3 install boto3
      ```

3. Port forwarding
   - Port forwarding for external Internet access
      <p float="left">
         <img width="40%" src="https://user-images.githubusercontent.com/64878866/153058269-5a340d9d-7490-4a12-b2a9-a23b0a25ca94.png" />
      </p>

4. GPIO (led)

   ...

#### AWS
1. IAM
   - Name : FS-raspberrypi
   - Policy : AmazonS3FullAccess

2. S3 Bucket
   - Name : project-feedback-speech
   - Event notification
      - Name : FS-new-image
      - Types : All object create events
      - Destination type : SQS queue
      - Destination : FS-image-queue

3. SQS
   - Name : FS-image-queue
   - Policy
      ```
      {
        "Version": "2012-10-17",
        "Id": "Policy1639729333648",
        "Statement": [
          {
            "Sid": "Stmt1639729326911",
            "Effect": "Allow",
            "Principal": "*",
            "Action": "sqs:SendMessage",
            "Resource": "arn:aws:sqs:ap-northeast-2:{$Account_ID}:FS-image-queue",
            "Condition": {
              "StringEquals": {
                "aws:SourceArn": "arn:aws:s3:::project-feedback-speech"
              }
            }
          }
        ]
      }
      ```

4. Lambda
   - Name : facial-analysis-function
   - Runtime : Python3.7
   - Execution role : FS-lambda-role
   - Role Policy : AmazonSQSFullAccess, AmazonRekognitionFullAccess, AmazonOpenSearchServiceFullAccess, AmazonLambdaS3ExecutionRole, AmazonLambdaRekognitionReadOnlyAccessExecutionRole, AWSLambdaBasicExecutionRole
   - Trigger
      - SQS : FS-image-queue (Enabled)
      - Batch size : 1

5. Opensearch
   -  Amazon OpenSearch (successor to Amazon Elasticsearch)
   - Domain name : fs-elasticsearch
   - Deployment type : Development and testing
   - Version : Elasticsearch 6.8
   - Instance type : t3.small.search (2Core 2GB)
   - Number of nodes : 1
   - Storage type : EBS (General Purpose SSD)
   - Network : Public Access (보안을 위해 추후 VPC 구성 필요)
   - Master user type : Internal user database
   - Access Policy
      ```
      {
        "Version": "2012-10-17",
        "Statement": [
          {
            "Effect": "Allow",
            "Principal": {
              "AWS": "*"
            },
            "Action": "es:*",
            "Resource": "arn:aws:es:ap-northeast-2:{$Account_ID}:domain/fs-elasticsearch",
          }
        ]
      }
      ```


## Usage

