import logging
import shutil
import subprocess
from absl import app, flags
from enum import Enum, auto
from pathlib import Path
from typing import Iterator, List, Tuple

# Constants: Special LaTeX Commands
BEGIN_CMD = '% __BEGIN'
SLIDE_CMD = '% __SLIDE'
PAUSE_CMD = '% __PAUSE'
ADD_CMD = '% __ADD::'
POP_CMD = '% __POP'
END_CMD = '% __END'

# Logging Setup
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')

# NOTE: One highly popular resolution for YouTube videos is 1920px x 1080px.
# Therefore, we recommend using 6.4in wide LaTex documents and 300dpi.
# Another option would be 3840px x 2160px, also known as 4K resolution.

flags.DEFINE_string('input', 'example.tex', 'Input LaTeX file.')
flags.DEFINE_integer('dpi', 300, 'Resolution in DPI for pdftoppm.')
flags.DEFINE_integer('height', 1080, 'Crop height in pixels for pdftoppm.')

FLAGS = flags.FLAGS


class LatexSlide:
    '''Represents a single LaTeX slide, broken into one or more steps.'''

    def __init__(self, lines: list[str], header: list[str], footer: list[str]):
        self._lines = lines
        self._header = header
        self._footer = footer
        self._steps = self._parse()

    def _parse(self) -> List[List[str]]:
        steps, blocks = [], [[]]
        for line in self._lines + [PAUSE_CMD]:
            if line == PAUSE_CMD:
                steps.append(self._join_blocks(blocks))
                blocks.append([])
            elif line == POP_CMD:
                blocks.pop()
            else:
                blocks[-1].append(line)
        return steps

    def _join_blocks(self, blocks: List[List[str]]) -> List[str]:
        '''Join the given blocks, processing ADD_CMD commands.'''
        return [line[len(ADD_CMD):] if line.startswith(ADD_CMD) and
                idx == len(blocks) - 1 else line
                for idx, block in enumerate(blocks) for line in block]

    @property
    def steps(self) -> Iterator[str]:
        return ('\n'.join(self._header + step + self._footer)
                for step in self._steps)

class LatexSlideDeck:
    '''Generates LaTeX slides for the input LaTeX document.'''

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
        return (LatexSlide(slide_lines, self._header, self._footer)
                for slide_lines in self._slides)

def create_empty_directory(path: Path):
    logging.info(f'Creating empty directory: "{path}"')
    if path.exists():
        shutil.rmtree(path)
    path.mkdir(parents=True)

def read_latex_file(path: Path) -> List[str]:
    logging.info(f'Reading input LaTeX file: "{path}"')
    with path.open('r') as file:
        return file.read().splitlines()

def write_latex_file(path: Path, content: str):
    logging.info(f'Writing LaTeX file: {path}')
    with path.open('w') as output_file:
        output_file.write(content)

def execute_shell_command(command: str) -> str:
    logging.info(f'Executing: {command}')
    process = subprocess.run(
        command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    process.check_returncode()  # raises an error if not 0
    return process.stdout.decode()

def generate_pdf_from_latex(file_path: Path) -> str:
    command = (
        f'pdflatex -synctex=1 -interaction=nonstopmode -file-line-error ' +
        f' -recorder -output-directory="{file_path.parent}" "{file_path}"')
    return execute_shell_command(command)

def convert_pdf_to_png(file_path_no_ext: Path) -> str:
    command = (f'pdftoppm "{file_path_no_ext}.pdf" "{file_path_no_ext}" '
               f'-singlefile -png -r {FLAGS.dpi} -H {FLAGS.height}')
    return execute_shell_command(command)

def cleanup_output_directory(directory: Path):
    logging.info(f'Cleaning up the output directory: "{directory}"')
    for file_path in directory.iterdir():
        if file_path.suffix != '.png':
            file_path.unlink()

def process_deck(deck: LatexSlideDeck, input_path: Path,
                 output_directory: Path):
    for slide_index, slide in enumerate(deck.slides):
        for step_index, step in enumerate(slide.steps):
            output_base = output_directory / (
                f'{input_path.stem}-{slide_index:04}-{step_index:04}')
            output_tex_path = output_base.with_suffix('.tex')
            write_latex_file(output_tex_path, step)
            generate_pdf_from_latex(output_tex_path)
            convert_pdf_to_png(output_base)

def main(_):
    input_path = Path(FLAGS.input).resolve()
    output_directory = input_path.parent / 'out'
    create_empty_directory(output_directory)
    process_deck(LatexSlideDeck(read_latex_file(input_path)),
                 input_path, output_directory)
    cleanup_output_directory(output_directory)
    logging.info('Process finished successfully')

if __name__ == '__main__':
    app.run(main)
