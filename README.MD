## ABOUT

This started as an attempt to port the code from both `plataform 1.0.py` and `3d-5.py`, two little programs I made back when I learned python and the use of classes around 2020, and mutated into a sandbox for 2D and 3D rendering experiments using nothing but vanilla built-in python functionality. No 3rd party libraries are required, apart from pynput on macOS to access the keyboard actions.

Proudly made with human brain and human hands. No AI or coding aid involved, apart from: 
- an initial refactoring of a single file codebase into folders with Claude
- setting up requirements, etc., with Claude
- an opt-in multicore PoC with Claude (`fer/multi-thread-support-poc`): the frame is split into a simulate stage and a draw stage that overlap (`--threaded`), with entity/background pixel resolution and buffer conversion spread over a thread pool (`--render-workers N`). On free-threaded python3.14t it gets ~1.7-2x faster frames, with output identical to serial
- occasional questions about python sintax to ChatGPT or Claude lol `(:`