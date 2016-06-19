Encoder
=======

.. autoclass:: avlogue.encoders.base.BaseEncoder
   :members:

.. autoclass:: avlogue.encoders.ffmpeg.FFMpegEncoder
   :members:


Exceptions
----------
.. automodule:: avlogue.encoders.exceptions
   :members:

.. autoexception:: avlogue.encoders.ffmpeg.FFProbeError

   Subclass of :class:`avlogue.encoders.exceptions.GetFileInfoError`.


.. autoexception:: avlogue.encoders.ffmpeg.FFMpegEncoderError

    Subclass of :class:`avlogue.encoders.exceptions.EncodeError`.