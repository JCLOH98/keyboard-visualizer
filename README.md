# keyboard-visualizer
An on-screen keyboard that highlights keys in real-time as you type on your physical keyboard, providing a visual feedback of your input.

##  Customizable style
- keyboard background color
    - `KEYBOARD_BG_COLOR`
- on press color
    - `PRESS_BG_COLOR`
- on release color
    - `RELEASE_BG_COLOR`
- font
    - `FONT_PATH`
- mechanical sound effect
    - `SOUND_PATH`

## Run the program
- `python keyboard-visualizer.py`
    - Default got no sound effect
- `python keyboard-visualizer.py --soundon`
    - use `--soundon` to enable sound effect


## Dependencies
- Python version >= 3.10
- wxPython
    - `pip install wxPython`
- pynput
    - `pip install pynput`
- pygame
    - `pip install pygame`

## Sound effect resource
- **mechanical key soft** by [freesound_community](https://pixabay.com/users/freesound_community-46691455/)
