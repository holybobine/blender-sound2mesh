# Sound2Mesh
Sound2Mesh is an attempt at making a fully functionnal 3D spectrogram in blender.

It relies on FFmpeg's function [showspectrumpic](https://ffmpeg.org/ffmpeg-filters.html#showspectrumpic), which creates 2D spectrogram images from audio files. I then use this image to displace a plane using geometry nodes.

If you're interested in the full process I go into more details  [here](https://blenderartists.org/t/making-a-spectrogram-with-geometry-nodes/1486152).
