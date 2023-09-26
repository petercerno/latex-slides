from typing import List
import ffmpeg


def create_video_from_images_and_audio(
    image_paths: List[str], audio_paths: List[str], output_path: str
) -> None:
    """
    Creates a video using a list of images and audio clips. Each image will have
    the same duration as its corresponding audio clip.

    Parameters:
    - image_paths: List of paths to images
    - audio_paths: List of paths to audio clips
    - output_path: Path where the final video will be saved
    """

    # Check if the number of images matches the number of audio clips
    if len(image_paths) != len(audio_paths):
        raise ValueError("The number of image paths and audio paths must be equal.")

    # Create a list of durations for each audio clip
    audio_durations = [
        ffmpeg.probe(audio_path)["format"]["duration"] for audio_path in audio_paths
    ]

    # Create a list of input streams for images and set the duration for each image
    image_streams = [
        ffmpeg.input(image_path, loop=1, t=duration)
        for image_path, duration in zip(image_paths, audio_durations)
    ]

    # Create a list of input streams for audio
    audio_streams = [ffmpeg.input(audio_path) for audio_path in audio_paths]

    # Concatenate video and audio streams
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


# Replace these with the paths to your files
image_files = [
    "out/example-0000-0000.png",
    "out/example-0001-0000.png",
    "out/example-0001-0001.png",
]
audio_files = [
    "out/example-0000-0000.mp3",
    "out/example-0001-0000.mp3",
    "out/example-0001-0001.mp3",
]

# Create the video
create_video_from_images_and_audio(image_files, audio_files, "output_video.mp4")
