

OverflowError: Python int too large to convert to C ssize_t
Traceback (most recent call last):
  File "/home/hive/Workspace/sustainability/./main.py", line 407, in <module>
    main()
  File "/home/hive/Workspace/sustainability/./main.py", line 287, in main
    if pygame_movie.draw(pygame_screen, (0, 0), force_draw=False):
       ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/home/hive/.local/lib/python3.11/site-packages/pyvidplayer2/video.py", line 287, in draw
    if (self._update() or force_draw) and self.frame_surf is not None:
        ^^^^^^^^^^^^^^
  File "/home/hive/.local/lib/python3.11/site-packages/pyvidplayer2/video.py", line 182, in _update
    self._audio.load(self._chunks.pop(0))
  File "/home/hive/.local/lib/python3.11/site-packages/pyvidplayer2/mixer_handler.py", line 14, in load
    pygame.mixer.music.load(BytesIO(bytes))
pygame.error: Unrecognized audio format