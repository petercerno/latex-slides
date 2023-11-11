from pathlib import Path
from openai import OpenAI

client = OpenAI()

text = """Every mathematical theory introduces some definitions and is subsequently built upon a set of axioms that are universally accepted as true. As our focus is on mathematical analysis, it is necessary to strike the right balance between what we already accept as true and what we aim to prove.
With that in mind, we will not delve into the axioms governing the arithmetic of integers or explore the depths of complex topics like set theory or number theory. Instead, we will assume a basic familiarity with integers and rational numbers."""

speech_file_path = Path(__file__).parent / "demo_openai.mp3"
response = client.audio.speech.create(
    model="tts-1-hd",
    voice="fable",
    input=text,
    speed=1.0,
)

response.stream_to_file(speech_file_path)
