# Notes

Personal notes to keep track of stuff while I'm working on getting this up and running.

## Steps

1.  Create IAM role
    'AWS Service'
    Start with 'Step Functions' use case

    role name: transcribe-workflow-experiment

1.  Create bucket
    Called: transcribe-workflow-experiment
1.  Configure bucket
    Once created, click on bucket then click on 'Properties'
    Scroll down to Event notifications and under 'Amazon EventBridge' click Edit -> Enable

1.  Create Lambda Functions
    First one: transcribe-workflow-start-job
    Second one: transcribe-workflow-cleanup-job

1.  Create a Step Function state machine

        Add two lambda functions and map them to new functions above
        On the 2nd function, select 'Wait for Callback'
        name: transcribe-workflow-statemachine
        Create new role
        Set logging to All for debugging
        --- > Add AmazonTranscribeFullAccess (good idea? maybe)

    1. Edit step function create transcribe job

        ```json
        "Parameters": {
            "Media": {
                "MediaFileUri.$": "$.mediaS3Link"
            },
            "TranscriptionJobName.$": "$$.Execution.Name",
            "LanguageCode": "en-US"
        }
        ```

1.  Event Bridge

        We'll use default event bridge for this.  You could create custom bus but we'll use the default

        Create some rules

        1. Rule 1:
            Name: transcribe-workflow-experiment-new-file
            Description: Notifies Step Function there is a new audio file in S3 in the '/uploads' key
            Event bus: default
            Enable the rule
            Rule Type: Rule with an event pattern

            Event Source: AWS events or EventBridge partner events
            Sample Event: search for S3 Object created to get sample event for later
            Sample Event will look like:

            ```json
            {
                "version": "0",
                "id": "17793124-05d4-b198-2fde-7ededc63b103",
                "detail-type": "Object Created",
                "source": "aws.s3",
                "account": "123456789012",
                "time": "2021-11-12T00:00:00Z",
                "region": "ca-central-1",
                "resources": ["arn:aws:s3:::example-bucket"],
                "detail": {
                    "version": "0",
                    "bucket": {
                        "name": "example-bucket"
                    },
                    "object": {
                        "key": "example-key",
                        "size": 5,
                        "etag": "b1946ac92492d2347c6235b4d2611184",
                        "version-id": "IYV3p45BT0ac8hjHg1houSdS1a.Mro8e",
                        "sequencer": "00617F08299329D189"
                    },
                    "request-id": "N4N7GDK58NMKJ12R",
                    "requester": "123456789012",
                    "source-ip-address": "1.2.3.4",
                    "reason": "PutObject"
                }
            }
            ```

            Creation method: Use pattern form
            Event Source: AWS services
            AWS Service: S3
            Event Type: S3 event notification
            Specific Event: Object Created
            Specific Bucket: transcribe-workflow-experiment

            You get:

            ```json
            {
                "source": ["aws.s3"],
                "detail-type": ["Object Created"],
                "detail": {
                    "bucket": {
                        "name": ["transcribe-workflow-experiment"]
                    }
                }
            }
            ```

            But we want to trigger only on new files with key/folder of 'uploads'
            https://stackoverflow.com/questions/72725831/eventbridge-notification-on-amazon-s3-folder

            so we modify the event pattern to be:

            ```json
            {
                "source": ["aws.s3"],
                "detail-type": ["Object Created"],
                "detail": {
                    "bucket": {
                        "name": ["transcribe-workflow-experiment"]
                    },
                    "object": {
                        "key": [
                            {
                                "prefix": "uploads"
                            }
                        ]
                    }
                }
            }
            ```

            also if we want to filter on filename we can:
            https://docs.aws.amazon.com/eventbridge/latest/userguide/eb-event-patterns-content-based-filtering.html#eb-filtering-suffix-matching

            But difficult to target both

        1. Select Targets
            Use AWS Service: Step Functions

1.  Create Event Bridge for Transcription done

        Name: transcribe-workflow-experiment-transcribe-complete
        Description: Triggers when a transcription is complete
        default event bus
        rule with event pattern

        Sample event: Transcribe Job State Change
        Looks like:

        ```json
        {
            "version": "0",
            "id": "999cccaa-eaaa-0000-1111-123456789012",
            "detail-type": "Transcribe Job State Change",
            "source": "aws.transcribe",
            "account": "123456789012",
            "time": "2016-12-16T20:57:47Z",
            "region": "us-east-1",
            "resources": [],
            "detail": {
                "TranscriptionJobStatus": ["COMPLETED"]
            }
        }
        ```

        TranscriptionJobStatus will be COMPLETED or FAILED

## Stuck here

well, i can't go any further because the Transcribe service has no way to store the callback token of Step Functions.
Can't put it in a tag since it's longer than 256 chars.

### Possible Solutions

-   I would need to store the token with the filename in like dynamodb or something goofy
-   Implement loop in Step Functions to poll job status and then continue
-   In theory, based on execution name, lookup the token using StateEnteredEventDetails from GetExecutionHistory
    https://stackoverflow.com/questions/57704931/aws-sdk-in-java-how-to-get-activities-from-worker-when-multple-execution-on-go

Will end up rewriting it using two lambda functions and event bridge to detect when the transcribe job is complete.
