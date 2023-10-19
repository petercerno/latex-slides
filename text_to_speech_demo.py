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

text = """Every mathematical theory introduces some definitions and is subsequently built upon a set of axioms that are universally accepted as true. As our focus is on mathematical analysis, it is necessary to strike the right balance between what we already accept as true and what we aim to prove.
With that in mind, we will not delve into the axioms governing the arithmetic of integers or explore the depths of complex topics like set theory or number theory. Instead, we will assume a basic familiarity with integers and rational numbers."""

output_path = "demo.mp3"

# Instantiates a client
client = texttospeech.TextToSpeechClient()
voice = texttospeech.VoiceSelectionParams(
    language_code="en-US",
    name="en-US-Neural2-F",  # "en-US-Studio-O",
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
ssml = "<speak>{}</speak>".format(
    escaped_lines.replace("\n", '\n<break time="2s"/>').replace(
        ". ", '.<break time="1s"/> '
    )
)

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
