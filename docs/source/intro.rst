
Introduction
============

AVlogue is a Django reusable app to manage, and automatically convert, audio and video files.

Use case: When a client – usually, a Web browser on a computer or mobile device – needs to play back an audio/video file, it is necessary to provide it with an appropriate stream. The container and codecs must be supported by the client itself, the audio frequency/resolution must be supported, and the video resolution must be suitable for the device's screen.

The typical usage of AVlogue
----------------------------

A user uploads one high-resolution video file.

AVlogue compiles a list of video formats – each comprising the file container, the codecs, the resolution, the file bitrate – into which the file must be made available, discarding those formats whose quality is higher than the original input, making sure to include one suitable format for every supported device.

AVlogue uses a task runner to trigger the conversion of the uploaded file into each of the formats in the list. The task runner must store the final output of each conversion so that it can be later accessed through a URL.

As conversions are finished, AVlogue is notified so that other modules, or AVlogue itself, may make the new content available.

Features
--------

 - AVlogue handles both audio and video objects (separately).

 - AVlogue stores the relevant metadata for the objects (e.g. length).

 - AVlogue may use different storage backends to store both the input file and the results of the conversion tasks.

 - AVlogue uses Celery, through ``django-celery``, as a task runner.

 - AVlogue stores information about different AV output formats in the database; it picks the needed output formats at run-time when a video is uploaded, or it can be asked to perform conversions at a later time.

 - AVlogue stores information about each uploaded or generated file in the database, including relevant metadata (e.g. resolution, codecs, container format, bitrate). The uploaded file and the generated converted files are linked to the same Audio or Video object. 

 - AVlogue exposes an API for other applications to access the list of available resource for a certain Audio or Video objects.

 - AVlogue provides template tags to include Audio and Video objects in HTML5 output.




 