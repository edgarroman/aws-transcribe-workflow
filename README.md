# aws-transcribe-workflow

An experiment to Transcribe speech to text for files uploaded to S3 using Step Functions and EventBridge

My sister brought up an interesting case where a friend needed help transcribing speech to text.

This is a quick prototype to show how to:

1. Upload a sound file to S3
1. Get the sound file to AWS transcribe
1. Output the text of the sound file to S3
