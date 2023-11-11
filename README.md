# LaTeX-to-Slides Converter

Easily convert LaTeX documents into visually appealing slides with the look and feel of the original LaTeX format. See e.g. this [YouTube Playlist](https://www.youtube.com/playlist?list=PLn_PVMBSJNp0Ci0u7XiNgyP1OorIRmBKV) (Principles of Mathematical Analysis).

## 🚀 Features

- **Maintain Original Formatting**: Keep the aesthetic and structure of your original LaTeX document.
- **Customizable Slide Breaks**: Define your slide transitions through simple comment insertions into the LaTeX source.
- **Voice and Video Support**: Leverage [Google](https://cloud.google.com/text-to-speech) or [OpenAI](https://platform.openai.com/docs/guides/text-to-speech) Text-to-Speech API to enhance slides with auditory commentary and create high-quality video lectures.

## 🛠 Dependencies

Ensure you have the following dependencies installed:

* [Python 3.10+](https://www.python.org/)
* [Abseil Flags](https://abseil.io/docs/python/guides/flags)
* [LaTeX](https://www.latex-project.org/get/)
* [Poppler](https://poppler.freedesktop.org/)
* [FFmpeg](https://ffmpeg.org/) and [ffmpeg-python](https://pypi.org/project/ffmpeg-python/)
* [Google Text-to-Speech Client Libraries](https://cloud.google.com/text-to-speech/docs/libraries)
* [OpenAI Python Library](https://platform.openai.com/docs/api-reference/introduction)

We recommend utilizing [Miniconda](https://docs.conda.io/projects/miniconda/en/latest/) for managing Python and [Visual Studio Code](https://code.visualstudio.com/) as your code editor.

> **Note**: If you are using [Google Cloud Text-to-Speech API](https://cloud.google.com/text-to-speech) locally, make sure to set up [Application Default Credentials](https://cloud.google.com/docs/authentication/provide-credentials-adc) (ADC). Ensure that the `GOOGLE_APPLICATION_CREDENTIALS` environment variable points to the ADC JSON config and `GCLOUD_PROJECT` points to the Google Cloud Project with the enabled Cloud Text-to-Speech API.

> **Note**: If you are using [OpenAI Text-to-Speech API](https://platform.openai.com/docs/guides/text-to-speech) locally, simply set up the `OPENAI_API_KEY` environment variable.

This tool has been validated on macOS.

## 🎓 Ideal for Educators

Designed with educators and lecturers in mind, this tool enables you to:

- **Transform Comprehensive Documents**: Effortlessly convert detailed mathematical or scientific documents into comprehensive lecture slides.
- **Produce Video Lectures**: Generate video lectures, ensuring accessibility and facilitating an engaging learning experience.

Stay tuned for more exciting features and improvements!