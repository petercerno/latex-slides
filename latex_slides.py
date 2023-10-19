import ffmpeg
import html
import logging
import shutil
import subprocess
from absl import app, flags
from enum import Enum, auto
from google.cloud import texttospeech
from pathlib import Path
from typing import Iterator, List, Tuple

# Constants: Special LaTeX Commands
BEGIN_CMD = "% __BEGIN"
SLIDE_CMD = "% __SLIDE"
BREAK_CMD = "% __BREAK"
NOTES_CMD = "% __NOTE:"
SUB_CMD = "% __SUB::"
SUB_SEP = "::"
ADD_CMD = "% __ADD::"
POP_CMD = "% __POP"
END_CMD = "% __END"

# Logging Setup
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)

# NOTE: One very popular resolution for YouTube videos is 1920px x 1080px.
# Therefore, we recommend using 6.4in wide LaTex documents and 300dpi.
# Another option would be 3840px x 2160px, also known as 4K resolution.

flags.DEFINE_string("input", "example.tex", "Input LaTeX file.")
flags.DEFINE_integer("dpi", 300, "Resolution in DPI for pdftoppm.")
flags.DEFINE_integer("height", 1080, "Crop height in pixels for pdftoppm.")
flags.DEFINE_bool("use_text_to_speech", True, "Use Google Cloud Text-to-Speech API.")
flags.DEFINE_bool("create_video", True, "Create video by concatenating slides.")

FLAGS = flags.FLAGS


texttospeech_client = texttospeech.TextToSpeechClient()
voice = texttospeech.VoiceSelectionParams(
    language_code="en-US",
    name="en-US-Neural2-F",  # "en-US-Studio-O",
    ssml_gender=texttospeech.SsmlVoiceGender.FEMALE,
)
audio_config = texttospeech.AudioConfig(
    audio_encoding=texttospeech.AudioEncoding.MP3,
)


class LatexSlideStep:
    """Represents one step in a LaTeX slide."""

    def __init__(self, body: List[str], notes: List[str]):
        self.body = body
        self.notes = notes


class LatexSlide:
    """Represents a single LaTeX slide, broken into one or more steps."""

    def __init__(self, lines: List[str], header: List[str], footer: List[str]):
        self._lines = lines
        self._header = header
        self._footer = footer
        self.steps = self._parse()

    def _parse(self) -> List[LatexSlideStep]:
        steps, blocks = [], [[]]
        for line in self._lines + [BREAK_CMD]:
            if line == BREAK_CMD:
                step = LatexSlideStep(
                    self._header + self._join(blocks) + self._footer,
                    self._notes(blocks[-1]),
                )
                steps.append(step)
                blocks.append([])
            elif line.startswith(SUB_CMD):
                [old, new] = line[len(SUB_CMD) :].split(SUB_SEP)
                self._substitute(blocks, old, new)
            elif line == POP_CMD:
                blocks.pop()
            else:
                blocks[-1].append(line)
        return steps

    def _join(self, blocks: List[List[str]]) -> List[str]:
        """Joins the given blocks, processing ADD_CMD commands."""
        return [
            line[len(ADD_CMD) :]
            if line.startswith(ADD_CMD) and idx == len(blocks) - 1
            else line
            for idx, block in enumerate(blocks)
            for line in block
        ]

    def _notes(self, block: List[str]) -> List[str]:
        """Extracts notes from the given block."""
        return [
            line[len(NOTES_CMD) :].strip()
            for line in block
            if line.startswith(NOTES_CMD)
        ]

    def _substitute(self, blocks: List[List[str]], old: str, new: str):
        for i in range(len(blocks)):
            for j in range(len(blocks[i])):
                if old in blocks[i][j]:
                    blocks[i][j] = blocks[i][j].replace(old, new)


class LatexSlideDeck:
    """Generates LaTeX slides for the input LaTeX document."""

    def __init__(self, lines: List[str]):
        self._lines = lines
        self._header = []
        self._slides = []
        self._footer = []
        self._header, self._slides, self._footer = self._parse()

    def _parse(self) -> Tuple[List[str], List[List[str]], List[str]]:
        class ParseState(Enum):
            HEADER = auto()
            SLIDES = auto()
            FOOTER = auto()

        header, slides, footer = [], [], []
        state = ParseState.HEADER
        for line in self._lines:
            if line == BEGIN_CMD:
                state = ParseState.SLIDES
                slides.append([])
            elif line == SLIDE_CMD:
                slides.append([])
            elif line == END_CMD:
                state = ParseState.FOOTER
            else:
                if state == ParseState.HEADER:
                    header.append(line)
                elif state == ParseState.SLIDES:
                    slides[-1].append(line)
                elif state == ParseState.FOOTER:
                    footer.append(line)
        return header, slides, footer

    @property
    def slides(self) -> Iterator[LatexSlide]:
        return (
            LatexSlide(slide_lines, self._header, self._footer)
            for slide_lines in self._slides
        )


def create_empty_directory(path: Path):
    logging.info(f'Creating empty directory: "{path}"')
    if path.exists():
        shutil.rmtree(path)
    path.mkdir(parents=True)


def read_from_file(path: Path) -> List[str]:
    logging.info(f'Reading from file: "{path}"')
    with path.open("r") as file:
        return file.read().splitlines()


def write_to_file(path: Path, content: str):
    logging.info(f"Writing to file: {path}")
    with path.open("w") as file:
        file.write(content)


def execute_shell_command(command: str) -> str:
    logging.info(f"Executing: {command}")
    process = subprocess.run(
        command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE
    )
    process.check_returncode()  # raises an error if not 0
    return process.stdout.decode()


def generate_pdf_from_latex(path: Path) -> str:
    command = (
        f"pdflatex -synctex=1 -interaction=nonstopmode -file-line-error "
        + f' -recorder -output-directory="{path.parent}" "{path}"'
    )
    return execute_shell_command(command)


def convert_pdf_to_png(path_no_ext: Path) -> str:
    command = (
        f'pdftoppm "{path_no_ext}.pdf" "{path_no_ext}" '
        f"-singlefile -png -r {FLAGS.dpi} -H {FLAGS.height}"
    )
    return execute_shell_command(command)


def convert_notes_to_mp3(path: Path, notes: List[str]):
    if len(notes) == 0:
        raise Exception(f"Empty notes for: {path}")
    ssml = "<speak>{}</speak>".format(
        "\n".join(
            [
                html.escape(line)
                .replace("[", '<say-as interpret-as="verbatim">')
                .replace("]", "</say-as>")
                .replace(".", '.<break time="1s"/> ')
                + ('<break time="2s"/>' if line.endswith(".") else "")
                for line in notes
            ]
        )
    )
    synthesis_input = texttospeech.SynthesisInput(ssml=ssml)
    request = texttospeech.SynthesizeSpeechRequest(
        input=synthesis_input, voice=voice, audio_config=audio_config
    )
    response = texttospeech_client.synthesize_speech(request=request)
    logging.info(f"Writing audio response to file: {path}")
    with path.open("wb") as file:
        file.write(response.audio_content)


def cleanup_output_directory(directory: Path):
    logging.info(f'Cleaning up the output directory: "{directory}"')
    for path in directory.iterdir():
        if path.suffix not in [".png", ".txt", ".mp3", ".mp4"]:
            path.unlink()


def create_video_from_images_and_audio(
    image_paths: List[str], audio_paths: List[str], output_path: str
):
    audio_durations = [
        ffmpeg.probe(audio_path)["format"]["duration"] for audio_path in audio_paths
    ]
    image_streams = [
        ffmpeg.input(image_path, loop=1, t=duration)
        for image_path, duration in zip(image_paths, audio_durations)
    ]
    audio_streams = [ffmpeg.input(audio_path) for audio_path in audio_paths]

    video_stream = ffmpeg.concat(*image_streams, v=1, a=0)
    audio_stream = ffmpeg.concat(*audio_streams, v=0, a=1)

    ffmpeg.output(
        video_stream,
        audio_stream,
        output_path,
        vcodec="libx264",
        acodec="aac",
        strict="experimental",
    ).run()


def process_deck(deck: LatexSlideDeck, input_path: Path, output_directory: Path):
    image_paths = []
    audio_paths = []
    subtitles = []
    for slide_index, slide in enumerate(deck.slides):
        for step_index, step in enumerate(slide.steps):
            output_name = f"{input_path.stem}-{slide_index:04}-{step_index:04}"
            output_base = output_directory / output_name
            output_tex_path = output_base.with_suffix(".tex")
            write_to_file(output_tex_path, "\n".join(step.body))
            generate_pdf_from_latex(output_tex_path)
            convert_pdf_to_png(output_base)
            image_paths.append(output_base.with_suffix(".png"))
            output_txt_path = output_base.with_suffix(".txt")
            write_to_file(output_txt_path, "\n".join(step.notes))
            if FLAGS.use_text_to_speech:
                output_mp3_path = output_base.with_suffix(".mp3")
                convert_notes_to_mp3(output_mp3_path, step.notes)
                audio_paths.append(output_mp3_path)
                subtitles = subtitles + step.notes
    if FLAGS.create_video and len(image_paths) == len(audio_paths):
        output_mp4_path = (output_directory / input_path.stem).with_suffix(".mp4")
        create_video_from_images_and_audio(
            image_paths, audio_paths, f"{output_mp4_path}"
        )
        output_subtitles_path = (output_directory / input_path.stem).with_suffix(".txt")
        write_to_file(output_subtitles_path, "\n".join(subtitles))


def main(_):
    input_path = Path(FLAGS.input).resolve()
    output_directory = input_path.parent / "out"
    create_empty_directory(output_directory)
    slide_deck = LatexSlideDeck(read_from_file(input_path))
    process_deck(slide_deck, input_path, output_directory)
    cleanup_output_directory(output_directory)
    logging.info("Process finished successfully")


if __name__ == "__main__":
    app.run(main)
