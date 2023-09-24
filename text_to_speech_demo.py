import html

# NOTE: Using Google Cloud Text-to-Speech API requires properly set up
# Application Default Credentials (ADC), see:
# https://cloud.google.com/docs/authentication/provide-credentials-adc
# We assume that the environment variable GOOGLE_APPLICATION_CREDENTIALS
# points to the Application Default Credentials (ADC) JSON config and that
# the environment variable GCLOUD_PROJECT points to the Google Cloud project
# with enabled Cloud Text-to-Speech API.

# Imports the Google Cloud client libraries
from google.cloud import texttospeech

text = """Chapter 1: The Real and Complex Number Systems.
These are my solutions to exercises from the book Principles of Mathematical Analysis by Walter Rudin, third edition.

Exercise 6

Assume that m, n, p, q are integers, n is bigger than 0, q is bigger than 0, and r is equal to m over n, which is equal to p over q.
First, we would like to prove that if we raise b to the power of m, and then compute its nth root, we get the same result as if we raise b to the power of p, and then compute its quth root.
This would allow us to define the power to the rational number r, since it does not matter how the rational number r is represented.
"""

output_path = "demo.mp3"

# Instantiates a client
client = texttospeech.TextToSpeechClient()
voice = texttospeech.VoiceSelectionParams(
    language_code="en-US",
    name="en-US-Studio-O",
    ssml_gender=texttospeech.SsmlVoiceGender.FEMALE,
)
audio_config = texttospeech.AudioConfig(audio_encoding=texttospeech.AudioEncoding.MP3)

# Replace special characters with HTML Ampersand Character Codes
# These Codes prevent the API from confusing text with
# SSML commands
# For example, '<' --> '&lt;' and '&' --> '&amp;'
escaped_lines = html.escape(text)

# Convert plaintext to SSML in order to wait one second
# between each line in synthetic speech
ssml = "<speak>{}</speak>".format(escaped_lines.replace("\n", '\n<break time="1s"/>'))

# Sets the text input to be synthesized
synthesis_input = texttospeech.SynthesisInput(ssml=ssml)

# Performs the text-to-speech request on the text input with the selected
# voice parameters and audio file type
request = texttospeech.SynthesizeSpeechRequest(
    input=synthesis_input, voice=voice, audio_config=audio_config
)

response = client.synthesize_speech(request=request)

# Writes the synthetic audio to the output file.
with open(output_path, "wb") as file:
    file.write(response.audio_content)
    print("Audio content written to file " + output_path)
