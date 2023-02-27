import json
import boto3
import logging
import datetime

log = logging.getLogger()
log.setLevel(logging.INFO)


def lambda_handler(event, context):
    transcribe = boto3.client("transcribe")

    log.info("transcribe-workflow-start-job started...")

    if event:
        bucket = event["detail"]["bucket"]["name"]
        key = event["detail"]["object"]["key"]
        # The job name is important because the output file will be named after
        # the original audio file name, but 'slugified'.  This means it contains
        # only lower case characters, numbers, and hyphens
        slug_name = slugify(key.split("/")[-1])
        # Have to generate timestamp to make sure the AWS Transcribe job name is unique
        timestamp = "-{:%Y-%m-%d-%H%M%S}".format(datetime.datetime.now())
        job_name = slug_name + timestamp
        log.info(f"Received the following file {bucket} {key}")
        log.info(f"Job Name {job_name}")
        s3_uri = f"s3://{bucket}/{key}"
        # Kick off the transcription job
        transcribe.start_transcription_job(
            TranscriptionJobName=job_name,
            Media={"MediaFileUri": s3_uri},
            LanguageCode="en-US",
            OutputBucketName=bucket,
            OutputKey="output/",
        )

    return {"statusCode": 200, "body": "Lambda: Start Transcribe Complete"}


# Small slugify code taken from:
# https://gist.github.com/gergelypolonkai/1866fd363f75f4da5f86103952e387f6
# Converts "Audio File #3.mp3" to "audio-file-3-mp3"
#
import re
from unicodedata import normalize

_punctuation_re = re.compile(r'[\t !"#$%&\'()*\-/<=>?@\[\\\]^_`{|},.]+')


def slugify(text, delim="-"):
    """
    Generate an ASCII-only slug.
    """

    result = []
    for word in _punctuation_re.split(text.lower()):
        word = normalize("NFKD", word).encode("ascii", "ignore").decode("utf-8")

        if word:
            result.append(word)

    return delim.join(result)
