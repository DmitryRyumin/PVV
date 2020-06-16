# Воспроизведение фото/видео данных

![PyPI](https://img.shields.io/pypi/v/pvv)
![PyPI - Python Version](https://img.shields.io/pypi/pyversions/pvv)
![PyPI - Implementation](https://img.shields.io/pypi/implementation/pvv)
![PyPI - Status](https://img.shields.io/pypi/status/pvv)
![PyPI - License](https://img.shields.io/pypi/l/pvv)

| [История релизов](https://github.com/DmitryRyumin/PVV/blob/master/NOTES_RU.md) | [Документация на английском](https://github.com/DmitryRyumin/PVV/blob/master/README.md) |
| --- | --- |

## Установка

```shell script
pip install pvv
```

---

>  **Примечание для Windows!**

1. Удалить `PyOpenGL`

    ```shell script
    pip uninstall PyOpenGL
    ```

2. Скачать и установить [PyOpenGL](https://www.lfd.uci.edu/~gohlke/pythonlibs/#pyopengl)

---

## Обновление

```shell script
pip install --upgrade pvv
```

## Зависимости

| Пакеты | Минимальная версия | Текущая версия |
| ------ | ------------------ | -------------- |
`numpy` | `1.18.4` | ![PyPI](https://img.shields.io/pypi/v/numpy) |
`opencv-contrib-python` | `4.2.0.34` | ![PyPI](https://img.shields.io/pypi/v/opencv-contrib-python) |
`PyOpenGL` | `3.1.5` | ![PyPI](https://img.shields.io/pypi/v/PyOpenGL) |
`Pillow` | `7.1.2` | ![PyPI](https://img.shields.io/pypi/v/Pillow) |

## Класс для воспроизведения фото/видео данных - [смотреть](https://github.com/DmitryRyumin/PVV/blob/master/pvv/viewer.py)

### Аргументы командной строки

| Аргумент&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; | Тип | Описание | Допустимые значения |
| -------------------------- | ---  | -------- | ------------------- |
| command | str | Язык<br>`Значение по умолчанию: en` | `en`<br>`ru` |
| --file | str | Путь к фото/видео файлу<br>`Значение по умолчанию: 0` | - |
| --config | str | Путь к конфигурационному файлу | - |
| --frames_to_update | int | Через какое количество шагов проверять конфигурационный файл (работает при `--automatic_update`)<br>`Значение по умолчанию: 25` | От `0` до `∞` |
| --automatic_update | bool | Автоматическая проверка конфигурационного файла в момент работы программы (работает при заданном`--config`) | Без значений |
| --no_clear_shell | bool | Не очищать консоль перед выполнением | Без значений |

### [Конфигурационный файл](https://github.com/DmitryRyumin/PVV/blob/master/pvv/configs/config.json)

#### Параметры

| Параметр `json` | Тип | Описание | Допустимые значения |
| ---------------- | ---  | -------- | ------------------- |
| hide_metadata | bool | Скрытие метаданных | - |
| window_name | str | Имя окна | - |
| resize | dict | Размер окна для масштабирования | От `0` до `∞` |
| info_text_color | dict | Цвет текстов информационных уведомлений | От `0` до `255` |
| info_background_color | dict | Цвет фона информационных уведомлений | От `0` до `255` |
| info_size | int | Размер шрифта информационных уведомлений | От `0` до `60` |
| info_stroke | int | Ширина обводки текста информационных уведомлений | От `0` до `4` |
| info_stroke_color | int | Цвет обводки текста информационных уведомлений | От `0` до `255` |
| error_text_color | dict | Цвет текстов уведомлений об ошибках | От `0` до `255` |
| error_background_color | dict | Цвет фона уведомлений об ошибках | От `0` до `255` |
| error_size | int | Размер шрифта уведомлений об ошибках | От `0` до `60` |
| error_stroke | int | Ширина обводки текста уведомлений об ошибках | От `0` до `4` |
| error_stroke_color | int | Цвет обводки текста уведомлений об ошибках | От `0` до `255` |
| repeat_text_color | dict | Цвет текста повтора воспроизведения | От `0` до `255` |
| repeat_background_color | dict | Цвет фона повтора воспроизведения | От `0` до `255` |
| repeat_size | int | Размер шрифта текста повтора воспроизведения | От `0` до `120` |
| repeat_stroke | int | Ширина обводки текста повтора воспроизведения | От `0` до `4` |
| repeat_stroke_color | int | Цвет обводки текста повтора воспроизведения | От `0` до `255` |
| labels_base_coords | int | Начальные координаты верхних левых информационных уведомлений | От `0` до `100` |
| labels_padding | int | Внутренний отступ для всех текстов уведомлений | От `0` до `30` |
| labels_distance | int | Расстояние между текстами | От `0` до `15` |
| clear_image_buffer | bool | Очистка буфера с изображением | - |
| real_time | bool | Воспроизведение фото/видеопотока с реальным количеством FPS | - |
| repeat | bool | Повторение воспроизведения видеопотока | - |
| fps | int | Пользовательский FPS<br>`"real_time" = true` | От `0` до `60` |
| show_labels | bool | Отображение надписей в окне воспроизведения | - |

#### Горячие клавиши

| Клавиши | Сценарий |
| ------- | -------  |
| `esc` | Закрытие окна приложения |
| `r` | Повторение воспроизведения видеопотока |

<h4 align="center"><span style="color:#EC256F;">Примеры</span></h4>

---

>  **Примечание!**
>
> Поддерживаемые видео форматы: `mp4` и `avi`
> Поддерживаемые фото форматы: `png` и `jpg`

---

1. Воспроизведение видео файла с автоматическим обновлением конфигурационного файла (Язык: `Русский`)

    > CMD
    >
    > ```shell script
    > pvv_play ru --file путь_к_видео_файлу --config путь_к_конфигурационному_файлу --automatic_update
    > ```

2. Стриминг с WEB-камеры с автоматическим обновлением конфигурационного файла каждые 50 кадров (Язык: `Английский`)

    > CMD
    >
    > ```shell script
    > pvv_play ru --file 0 --config путь_к_конфигурационному_файлу --automatic_update  --frames_to_update 50
    > ```