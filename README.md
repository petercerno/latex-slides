# LaTeX-to-Slides Converter

Easily convert LaTeX documents into visually appealing slides with the look and feel of the original LaTeX format. See this [Example Lecture](https://www.youtube.com/watch?v=Kl6WqrZHWFc), or this [Playlist](https://youtube.com/playlist?list=PLn_PVMBSJNp0Ci0u7XiNgyP1OorIRmBKV&si=dyT1cIsRO04V-3pG) (Principles of Mathematical Analysis).

## 🚀 Features

- **Maintain Original Formatting**: Keep the aesthetic and structure of your original LaTeX document.
- **Customizable Slide Breaks**: Define your slide transitions through simple comment insertions into the LaTeX source.
- **Voice and Video Support**: Leverage [Google Text-to-Speech API](https://cloud.google.com/text-to-speech) to enhance slides with auditory commentary and create high-quality video lectures.

## 🛠 Dependencies

Ensure you have the following dependencies installed:

* [Python 3.10+](https://www.python.org/)
* [Abseil Flags](https://abseil.io/docs/python/guides/flags)
* [LaTeX](https://www.latex-project.org/get/)
* [Poppler](https://poppler.freedesktop.org/)
* [FFmpeg](https://ffmpeg.org/) and [ffmpeg-python](https://pypi.org/project/ffmpeg-python/)
* [Text-to-Speech Client Libraries](https://cloud.google.com/text-to-speech/docs/libraries)

We recommend utilizing [Miniconda](https://docs.conda.io/projects/miniconda/en/latest/) for managing Python and [Visual Studio Code](https://code.visualstudio.com/) as your code editor.

> **Note**: For using [Google Cloud Text-to-Speech API](https://cloud.google.com/text-to-speech) locally, make sure to set up [Application Default Credentials](https://cloud.google.com/docs/authentication/provide-credentials-adc) (ADC). Ensure the `GOOGLE_APPLICATION_CREDENTIALS` environment variable points to the ADC JSON config and `GCLOUD_PROJECT` points to the Google Cloud Project with the enabled Cloud Text-to-Speech API.

This tool has been validated on macOS.

## 🎓 Ideal for Educators

Designed with educators and lecturers in mind, this tool enables you to:

- **Transform Comprehensive Documents**: Effortlessly convert detailed mathematical or scientific documents into comprehensive lecture slides.
- **Produce Video Lectures**: Generate video lectures, ensuring accessibility and facilitating an engaging learning experience.

Stay tuned for more exciting features and improvements!