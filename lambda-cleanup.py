import json
import boto3
import logging

log = logging.getLogger()
log.setLevel(logging.INFO)


def lambda_handler(event, context):

    transcribe = boto3.client("transcribe")
    s3 = boto3.client("s3")

    log.info(f"transcribe-workflow-cleanup started...")

    if event:
        job_name = event["detail"]["TranscriptionJobName"]
        log.info(f"Transcribe job: {job_name}")

        response = transcribe.get_transcription_job(TranscriptionJobName=job_name)
        if not response:
            return {"statusCode": 404, "body": "Job not found"}

        # Now extract the name of the original file
        # in the form:
        # s3://transcribe-workflow-experiment/uploads/Sample Audio.mp3
        original_audio_s3_uri = response["TranscriptionJob"]["Media"]["MediaFileUri"]
        # Use [5:] to remove the 's3://' and partition returns the string split by the first '/'
        bucket, _, key = original_audio_s3_uri[5:].partition("/")
        _, _, media_file = key.partition("/")
        log.info(f"Media file {media_file} is at: key {key} in bucket {bucket}")

        # Job status will either be "COMPLETED" or "FAILED"
        job_status = event["detail"]["TranscriptionJobStatus"]

        new_folder = "completed/"
        if job_status == "FAILED":
            new_folder = "failed/"

        # Tell AWS to 'move' the file in S3 which really means making a copy and deleting the original
        s3.copy_object(
            Bucket=bucket,
            CopySource=f"{bucket}/{key}",
            Key=f"{new_folder}{media_file}",
        )
        s3.delete_object(Bucket=bucket, Key=key)

    return {"statusCode": 200, "body": "Lambda: Transcribe Cleanup Complete"}
