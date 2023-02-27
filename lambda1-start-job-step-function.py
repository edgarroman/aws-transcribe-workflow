import json
import boto3
import urllib.parse
import logging

log = logging.getLogger()
log.setLevel(logging.INFO)


def lambda_handler(event, context):
    transcribe = boto3.client("transcribe")
    # s3 = boto3.client("s3")

    log.info("transcribe-workflow-start-job started...")

    if event:
        bucket = event["detail"]["bucket"]["name"]
        encoded_key = event["detail"]["object"]["key"]
        size = event["detail"]["object"]["size"]
        # Eventually we'll probably have to handle non-ASCII named files
        # https://stackoverflow.com/questions/39465220/get-non-ascii-filename-from-s3-notification-event-in-lambda
        key = urllib.parse.unquote_plus(encoded_key)
        s3_uri = create_uri(bucket, key)
        log.info(
            f"transcribe-workflow-start-job: received the following file {bucket} {key} {size} ({encoded_key})"
        )

        # Take the step function Execution Id and use it for the transcribe job name
        job_name = context.aws_request_id

        """
        # Now kick off the transcription job
        tjob = transcribe.start_transcription_job(
            TranscriptionJobName=job_name,
            Media={"MediaFileUri": s3_uri},
            # MediaFormat = file_type,
            LanguageCode="en-US",
        )

        log.info(f"tjob = {json.dumps(tjob)}")
        """

        # Now build data to pass along to the next Step function
        """
        response = {
            "Media" : {
                "MediaFileUri": s3_uri
            },
            "TranscriptionJobName": "$$.Execution.Id",
            "LanguageCode": "en-US"
        }
        """
        response = {"mediaS3Link": s3_uri}

    return response

    # return {"statusCode": 200, "body": json.dumps("Lambda: Start Job Complete")}


def create_uri(bucket_name, file_name):
    return "s3://" + bucket_name + "/" + file_name
