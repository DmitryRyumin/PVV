# Playing photo/video data

![PyPI](https://img.shields.io/pypi/v/pvv)
![PyPI - Python Version](https://img.shields.io/pypi/pyversions/pvv)
![PyPI - Implementation](https://img.shields.io/pypi/implementation/pvv)
![PyPI - Status](https://img.shields.io/pypi/status/pvv)
![PyPI - License](https://img.shields.io/pypi/l/pvv)

| [Release history](https://github.com/DmitryRyumin/PVV/blob/master/NOTES.md) | [Documentation in Russian](https://github.com/DmitryRyumin/PVV/blob/master/README_RU.md) |
| --- | --- |

## Installation

```shell script
pip install pvv
```

---

>  **Note for Windows!**

1. Delete `PyOpenGL`

    ```shell script
    pip uninstall PyOpenGL
    ```

2. Download and installing [PyOpenGL](https://www.lfd.uci.edu/~gohlke/pythonlibs/#pyopengl)

---

## Update

```shell script
pip install --upgrade pvv
```

## Required packages

| Packages | Min version | Current version |
| -------- | ----------- | --------------- |
`numpy` | `1.18.4` | ![PyPI](https://img.shields.io/pypi/v/numpy) |
`opencv-contrib-python` | `4.2.0.34` | ![PyPI](https://img.shields.io/pypi/v/opencv-contrib-python) |
`PyOpenGL` | `3.1.5` | ![PyPI](https://img.shields.io/pypi/v/PyOpenGL) |
`Pillow` | `7.1.2` | ![PyPI](https://img.shields.io/pypi/v/Pillow) |

## [Class for playing photo/video data](https://github.com/DmitryRyumin/PVV/blob/master/pvv/viewer.py)

### Command line arguments

| Argument&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; | Type | Description | Valid Values |
| -------------------------- | ---  | -------- | ------------------- |
| command | str | Language<br>`Default value: en` | `en`<br>`ru` |
| --file | str | Path to photo/video file<br>`Default value: 0` | - |
| --config | str | Path to configuration file | - |
| --frames_to_update | int | How many steps to check the configuration file (works with `--automatic_update`)<br>`Default value: 25` | From `0` to `∞` |
| --automatic_update | bool | Automatic verification of the configuration file at the time the program is running (it works with `--config`) | No value |
| --no_clear_shell | bool | Do not clean the console before running | No value |

### [Configuration file](https://github.com/DmitryRyumin/PVV/blob/master/pvv/configs/config.json)

#### Параметры

| `Json` parameter | Type | Description | Valid Values |
| ---------------- | ---  | -------- | ------------------- |
| hide_metadata | bool | Hide metadata | - |
| window_name | str | Window name | - |
| resize | dict | Window size for resize | From `0` to `∞` |
| info_text_color | dict | Text color of information notifications | From `0` to `255` |
| info_background_color | dict | Background color of information notifications | From `0` to `255` |
| info_size | int | Font size for information notification | From `0` to `60` |
| info_stroke | int | Stroke width for information notifications | From `0` to `4` |
| info_stroke_color | int | Stroke color for informational notifications text | From `0` to `255` |
| error_text_color | dict | Text color of error notifications | From `0` to `255` |
| error_background_color | dict | Background color of error notifications | From `0` to `255` |
| error_size | int | Font size for error notification | From `0` to `60` |
| error_stroke | int | Stroke Width for error notifications | From `0` to `4` |
| error_stroke_color | int | Stroke color for error notifications text | From `0` to `255` |
| repeat_text_color | dict | Text color of repeat playing | From `0` to `255` |
| repeat_background_color | dict | Background color of repeat playing | From `0` to `255` |
| repeat_size | int | Font size for repeat playing | From `0` to `120` |
| repeat_stroke | int | Stroke width for repeat playing | From `0` to `4` |
| repeat_stroke_color | int | Stroke color for repeat playing | From `0` to `255` |
| labels_base_coords | int | The start coordinate for the upper left informational notifications | From `0` to `100` |
| labels_padding | int | Padding size for all notification texts | From `0` to `30` |
| labels_distance | int | Text spacing | From `0` to `15` |
| clear_image_buffer | bool | Clear image buffer | - |
| real_time | bool | Playing a photo/video data with a real time of FPS | - |
| repeat | bool | Repeat video stream playback | - |
| fps | int | Custom FPS<br>`"real_time" = true` | From `0` to `60` |
| show_labels | bool | Display labels in the playback window | - |

#### Hotkeys

| Keyboard key | Execution |
| ------------ | -------- |
| `esc` | Closing the app window |
| `r` | Repeat video stream playback |

<h4 align="center"><span style="color:#EC256F;">Examples</span></h4>

---

>  **Note!** Supported Formats

| Video | Photo |
| ----- | ----- |
| `mp4` and `avi` | `png` and `jpg` |

---

1. Playing video file with automatic update of the configuration file (Language: `Russian`)

    > CMD
    >
    > ```shell script
    > pvv_play ru --file path_to_video_file --config path_to_config_file --automatic_update
    > ```

2. Streaming from a WEB-camera with automatic updating of the configuration file every 50 frames (Language: `English`)

    > CMD
    >
    > ```shell script
    > pvv_play en --file 0 --config path_to_config_file --automatic_update --frames_to_update 50
    > ```