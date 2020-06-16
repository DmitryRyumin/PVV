#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Воспроизведение фото/видео данных

python pvv/samples/play.py [--file путь_к_фото_видео_файлу --config путь_к_конфигурационному_файлу --automatic_update
    --frames_to_update 25 --no_clear_shell]
"""

# ######################################################################################################################
# Импорт необходимых инструментов
# ######################################################################################################################
import os  # Работа с файловой системой
import time  # Работа со временем
import cv2  # Алгоритмы компьютерного зрения
import numpy as np  # Научные вычисления
import pkg_resources  # Работа с ресурсами внутри пакетов
import sys  # Доступ к некоторым переменным и функциям python

from datetime import datetime  # Работа со временем
from PIL import Image, ImageFont, ImageDraw  # Работа с изображениями
from types import ModuleType, FunctionType, MethodType  # Проверка объектов на модуль, метод, функцию

# Персональные
import pvv  # Воспроизведение фото/видео данных

from pvv.viewer import Viewer  # Воспроизведение фото/видео данных
from pvv import configs  # Конфигурационные файлы
from pvv.modules.trml.shell import Shell  # Работа с Shell


# ######################################################################################################################
# Сообщения
# ######################################################################################################################
class Messages(Viewer):
    """Класс для сообщений"""

    # ------------------------------------------------------------------------------------------------------------------
    # Конструктор
    # ------------------------------------------------------------------------------------------------------------------

    def __init__(self):
        super().__init__()  # Выполнение конструктора из суперкласса

        self._pvv = self._('{}{}PVV - Воспроизведение фото/видео данных ...{}')

        self._run_web = self._('[{}] Запуск WEB камеры ...')
        self._run_web_err = self._('[{}{}{}] Для запуска WEB-камеры необходимо указать --file {} ...')
        self._run_video = self._('[{}] Запуск видео ...')
        self._show_photo = self._('[{}] Отображение фото ...')
        self._web_not_found = self._('[{}{}{}] WEB-камера не найдена ...')
        self._video_not_read = self._('[{}{}{}] Видео повреждено ...')
        self._photo_not_read = self._('[{}{}{}] Фото повреждено ...')

        self._frame_rate = 'FPS: {:.2f}'
        self._frame_rate_static = 'FPS: 60+'

        self._wrong_extension = self._('[{}{}{}] Расширение файла для фото должно быть одним из:'
                                       '\n    "{}" (фото данные)'
                                       '\n    "{}" (видео данные)')

        self._repeat_video = ['R', self._('повтор')]

        self._check_config_file_valid = '    ' + self._('[{}] Проверка данных на валидность ...')
        self._find_font = self._('[{}] Загрузка шрифта ...')
        self._font_not_found = '    ' + self._('[{}{}{}] Шрифт не найден ...')
        self._font_not_load = '    ' + self._('[{}{}{}] Шрифт не загружен ...')

        self._check_config_file_not_valid = self._('Ошибка в конфигурационном файле ...')
        self._labels_in_window = self._('Информация отображается в окне воспроизведения ...')


# ######################################################################################################################
# Выполняем только в том случае, если файл запущен сам по себе
# ######################################################################################################################
class Run(Messages):
    """Класс для воспроизведения фото/видео данных"""

    # ------------------------------------------------------------------------------------------------------------------
    # Конструктор
    # ------------------------------------------------------------------------------------------------------------------

    def __init__(self):
        super().__init__()  # Выполнение конструктора из суперкласса

        # Набор данных
        self._formats_data = (
            'web',  # WEB-камера
            'video',  # Видеофайл
            'photo'  # Фото
        )

        # Поддерживаемые видео форматы
        self._supported_video_formats = ('mp4', 'avi')
        # Поддерживаемые фото форматы
        self._supported_photo_formats = ('png', 'jpg')

        #  Информация по шрифту
        self._font = {
            'path': pkg_resources.resource_filename('pvv', 'configs/fonts'),  # Путь к шрифтам
            'name': 'SegoeUI.ttf',  # Шрифт
            'full_path': None,  # Полный путь к шрифту
            'info': None,  # Шрифт для общих уведомлений
            'error': None,  # Шрифт для ошибок
            'repeat': None  # Шрифт для потвора
        }

        self._cap = None  # Захват фото/видеоданных
        self._source = None  # Ресурс захвата фото/видеоданных
        self._curr_frame = None  # Текущий кадр
        self._curr_frame_transparent = None  # Прозрачное наложение на текущий кадр
        self._curr_frame_pil = None  # Текущий кадр в формате PIL
        self._curr_frame_pil_obj = None  # Объект, который можно использовать для рисования поверх изображения

        self._all_frame_count = 0  # Всего кадров (только для видеопотока)
        self._frame_count = 0  # Счетчик кадров

        self._frames_to_update = 0  # Счетчик автоматической проверки конфигурационного файла в момент работы программ

        # Варианты ошибок при автоматическом обновлении конфигурационного файла
        self._automatic_update = {
            'invalid_config_file': False  # Результат поиска необходимых значений в конфигурационном файле
        }

        self._prev_fps = 0  # Частота кадра

        self._cap_prop_fps = 0  # Частота кадра ресурса извлечения фото/видеоданных

        self._show_notification = False  # Нанесение уведомлений на последний кадр

        self._stdout = ''  # Последняя запись в терминале

    # ------------------------------------------------------------------------------------------------------------------
    #  Внутренние методы
    # ------------------------------------------------------------------------------------------------------------------

    # Построение аргументов командной строки
    def _build_args(self, conv_to_dict = True):
        """
        Построение аргументов командной строки

        ([bool]) -> None or dict

        Аргументы:
            conv_to_dict - Преобразование списка аргументов командной строки в словарь

        Возвращает: dict если парсер командной строки окончательный, в обратном случае None
        """

        super().build_args(False)  # Выполнение функции из суперкласса

        # Добавление аргументов в парсер командной строки
        self._ap.add_argument('--file', default = 0, metavar = self._('ФАЙЛ'),
                              help = self._('Путь к фото/видео файлу, значение по умолчанию:') + ' %(default)s)')
        self._ap.add_argument('--config', metavar = self._('ФАЙЛ'),
                              help = self._('Путь к конфигурационному файлу'))
        self._ap.add_argument('--frames_to_update', metavar = self._('ЦЕЛОЕ_ЧИСЛО'),
                              type = int, default = 25,
                              help = self._('Через какое количество шагов проверять конфигурационный файл '
                                            '(работает при --automatic_update, значение по умолчанию:')+' %(default)s)')

        self._ap.add_argument('--automatic_update', action = 'store_true',
                              help = self._('Автоматическая проверка конфигурационного файла в момент работы программы '
                                            '(работает при заданном') + ' --config')
        self._ap.add_argument('--no_clear_shell', action = 'store_false',
                              help = self._('Не очищать консоль перед выполнением'))

        # Преобразование списка аргументов командной строки в словарь
        if conv_to_dict is True:
            args, _ = self._ap.parse_known_args()
            return vars(args)  # Преобразование списка аргументов командной строки в словарь

    # Проверка JSON файла настроек на валидность
    def _valid_json_config(self, config, out = True):
        """
        Проверка настроек JSON на валидность

        (dict [, bool]) -> bool

        Аргументы:
            config - Словарь из JSON файла
            out    - Печатать процесс выполнения

        Возвращает: True если файл валидный, в обратном случае False
        """

        # Проверка аргументов
        if type(config) is not dict or type(out) is not bool:
            # Вывод сообщения
            if out is True:
                print(self._invalid_arguments.format(
                    self.red, datetime.now().strftime(self._format_time),
                    self.end, __class__.__name__ + '.' + self._valid_json_config.__name__
                ))

            return False

        # Конфигурационный файл пуст
        if len(config) == 0:
            # Вывод сообщения
            if out is True:
                print(self._config_empty.format(self.red, datetime.now().strftime(self._format_time), self.end))

            return False

        # Вывод сообщения
        if out is True:
            print(self._check_config_file_valid.format(datetime.now().strftime(self._format_time)))

        all_layer = 26  # Общее количество разделов
        curr_valid_layer = 0  # Валидное количество разделов

        # Проход по всем разделам конфигурационного файла
        for key, val in config.items():
            # 1. Скрытие метаданных
            # 2. Очистка буфера с изображением
            # 3. Воспроизведение видеопотока с реальным количеством FPS
            # 4. Повторение воспроизведения видеопотока
            # 5. Отображение надписей в окне воспроизведения
            if key == 'hide_metadata' or key == 'clear_image_buffer' or key == 'real_time' or key == 'repeat'\
                    or key == 'show_labels':
                # Проверка значения
                if type(val) is not bool:
                    continue

                curr_valid_layer += 1

            # Размер окна для масштабирования
            if key == 'resize':
                all_layer_2 = 1  # Общее количество подразделов в текущем разделе
                curr_valid_layer_2 = 0  # Валидное количество подразделов в текущем разделе

                # Проверка значения
                if type(val) is not dict or len(val) is 0:
                    continue

                # Проход по всем подразделам текущего раздела
                for k, v in val.items():
                    # Проверка значения
                    if type(v) is not int or v < 0:
                        continue

                    # Ширина окна для масштабирования
                    if k == 'width':
                        curr_valid_layer_2 += 1

                    # Высота окна для масштабирования
                    if k == 'height':
                        all_layer_2 += 1
                        curr_valid_layer_2 += 1

                if all_layer_2 == curr_valid_layer_2:
                    curr_valid_layer += 1

            # 1. Цвет текстов
            # 2. Цвет фона текстов
            if (key == 'info_text_color' or key == 'info_background_color' or
                    key == 'error_text_color' or key == 'error_background_color' or
                    key == 'repeat_text_color' or key == 'repeat_background_color' or
                    key == 'info_stroke_color' or key == 'error_stroke_color' or key == 'repeat_stroke_color'):
                all_layer_2 = 4  # Общее количество подразделов в текущем разделе
                curr_valid_layer_2 = 0  # Валидное количество подразделов в текущем разделе

                # Проверка значения
                if type(val) is not dict or len(val) is 0:
                    continue

                # Проход по всем подразделам текущего раздела
                for k, v in val.items():
                    # Проверка значения
                    if type(v) is not int or v < 0 or v > 255:
                        continue

                    # 1. Красный
                    # 2. Зеленый
                    # 3. Синий
                    # 3. Прозрачность
                    if k == 'red' or k == 'green' or k == 'blue' or k == 'alpha':
                        curr_valid_layer_2 += 1

                if all_layer_2 == curr_valid_layer_2:
                    curr_valid_layer += 1

            # Имя окна
            if key == 'window_name':
                # Проверка значения
                if type(val) is not str or not val:
                    continue

                curr_valid_layer += 1

            # Размер шрифта (информационные и ошибки)
            if key == 'info_size' or key == 'error_size':
                # Проверка значения
                if type(val) is not int or val <= 0 or val > 60:
                    continue

                curr_valid_layer += 1

            # Ширина обводки текста
            if key == 'info_stroke' or key == 'error_stroke' or key == 'repeat_stroke':
                # Проверка значения
                if type(val) is not int or val < 0 or val > 4:
                    continue

                curr_valid_layer += 1

            # Размер шрифта (повтор)
            if key == 'repeat_size':
                # Проверка значения
                if type(val) is not int or val <= 0 or val > 120:
                    continue

                curr_valid_layer += 1

            # Базовые координаты текстов
            if key == 'labels_base_coords':
                all_layer_2 = 2  # Общее количество подразделов в текущем разделе
                curr_valid_layer_2 = 0  # Валидное количество подразделов в текущем разделе

                # Проверка значения
                if type(val) is not dict or len(val) is 0:
                    continue

                # Проход по всем подразделам текущего раздела
                for k, v in val.items():
                    # Проверка значения
                    if type(v) is not int or v < 0 or v > 100:
                        continue

                    # 1. Лево
                    # 2. Вверх
                    if k == 'left' or k == 'top':
                        curr_valid_layer_2 += 1

                if all_layer_2 == curr_valid_layer_2:
                    curr_valid_layer += 1

            # Внутренний отступ для текстов
            if key == 'labels_padding':
                # Проверка значения
                if type(val) is not int or val < 0 or val > 30:
                    continue

                curr_valid_layer += 1

            # Расстояние между текстами
            if key == 'labels_distance':
                # Проверка значения
                if type(val) is not int or val < 0 or val > 15:
                    continue

                curr_valid_layer += 1

            # Частота кадров
            if key == 'fps':
                # Проверка значения
                if type(val) is not int or val < 0 or val > 60:
                    continue

                curr_valid_layer += 1

        # Сравнение общего количества разделов и валидных разделов в конфигурационном файле
        if all_layer != curr_valid_layer:
            # Вывод сообщения
            if out is True:
                print(self._invalid_file.format(
                    self.red, datetime.now().strftime(self._format_time), self.end
                ))

            return False

        return True  # Результат

    # Загрузка и проверка конфигурационного файла
    def _load_config_json(self, resources = configs, out = True):
        """
        Загрузка и проверка конфигурационного файла

        ([module, bool]) -> bool

        Аргументы:
            resources - Модуль с ресурсами
            out       - Печатать процесс выполнения

        Возвращает: True если файл загружен и валиден, в обратном случае False
        """

        # Проверка аргументов
        if type(out) is not bool or not isinstance(resources, ModuleType):
            # Вывод сообщения
            if out is True:
                print(self._invalid_arguments.format(
                    self.red, datetime.now().strftime(self._format_time),
                    self.end, __class__.__name__ + '.' + self._load_config_json.__name__
                ))

            return False

        # Конфигурационный файл передан
        if self._args['config'] is not None:
            config_json = self.load(self._args['config'], False, out)  # Загрузка JSON файла
        else:
            # Загрузка JSON файла из ресурсов модуля
            config_json = self.load_resources(resources, 'config.json', out)

        # Конфигурационный файл не загружен
        if config_json is None:
            return False

        # Проверка конфигурационного файла на валидность
        res_valid_json_config = self._valid_json_config(config_json, out)

        # Конфигурационный файл не валидный
        if res_valid_json_config is False:
            return False

        # Проход по всем разделам конфигурационного файла
        for k, v in config_json.items():
            # Добавление значения из конфигурационного файла в словарь аргументов командной строки
            self._args[k] = v

        return True

    # Автоматическая проверка конфигурационного файла в момент работы программы
    def _update_config_json(self, set_window_name = True):
        """
        Автоматическая проверка конфигурационного файла в момент работы программы

        ([bool]) -> bool

        Аргументы:
            set_window_name - Установка имени окна

        Возвращает: True если аргументы переданы верно, в обратном случае False
        """

        # Проверка аргументов
        if type(set_window_name) is not bool:
            return False

        # Автоматическая проверка конфигурационного файла в момент работы программы
        if self._args['automatic_update'] is True and self._frames_to_update % self._args['frames_to_update'] is 0:
            self._frames_to_update = 0  # Сброс счетчика автоматической проверки конфигурационного файла

            # Установка имени окна
            if set_window_name is True:
                curr_window_name = self._args['window_name']  # Текущее значение имени окна

            curr_resize = self._args['resize']  # Текущее значение размеров окна

            # 1. Загрузка и проверка конфигурационного файла не прошла
            # 2. Шрифт из ресурсов пакета не загружен
            if self._load_config_json(out = False) is False or self._search_font(out = False) is False:
                # Конфигурационный файл был валидный на прошлой проверке
                if self._automatic_update['invalid_config_file'] is False:
                    # Необходимые значения в конфигурационном файле не найдены в момент работы программы
                    self._automatic_update['invalid_config_file'] = True
            else:
                # Необходимые значения в конфигурационном файле найдены в момент работы программы
                self._automatic_update['invalid_config_file'] = False

                # Установка имени окна и имя окна было изменено
                if set_window_name is True and curr_window_name != self._args['window_name']:
                    self.set_window_name(self._args['window_name'])  # Установка имени окна

                # Ширина и высота нулевые
                if self._args['resize']['width'] == 0 and self._args['resize']['height'] == 0:
                    self._args['resize']['height'] = self._curr_frame.shape[0]  # Высота изображения
                    self._args['resize']['width'] = self._curr_frame.shape[1]  # Ширина изображения

                # Размер окна был изменен
                if curr_resize['width'] != self._args['resize']['width'] \
                        or curr_resize['height'] != self._args['resize']['height']:
                    # Установка размеров текущего окна
                    self.set_window_size(self._args['resize']['width'], self._args['resize']['height'])

                self.clear_image_buffer = self._args['clear_image_buffer']  # Очистка буфера с изображением

        # Увеличение счетчика автоматической проверки конфигурационного файла в момент работы программ
        self._frames_to_update += 1

        return True

    # Поиск шрифта из ресурсов пакета
    def _search_font(self, out = True):
        """
        Поиск шрифта из ресурсов пакета

        ([bool]) -> bool

        Аргументы:
            out - Печатать процесс выполнения

        Возвращает: True если шрифт найден, в обратном случае False
        """

        # Проверка аргументов
        if type(out) is not bool:
            return False

        # Вывод сообщения
        if out is True:
            print(self._find_font.format(datetime.now().strftime(self._format_time)))

        # Полный путь к шрифту
        self._font['full_path'] = os.path.join(self._font['path'], self._font['name'])

        # Шрифт не найден
        if os.path.isfile(self._font['full_path']) is not True:
            # Вывод сообщения
            if out is True:
                print(self._font_not_found.format(self.red, datetime.now().strftime(self._format_time), self.end))

            return False

        # Загрузка шрифта из ресурсов пакета
        return self._load_font(out)

    # Загрузка шрифта из ресурсов пакета
    def _load_font(self, out = True):
        """
        Поиск шрифта из ресурсов пакета

        ([bool]) -> bool

        Аргументы:
            out  - Печатать процесс выполнения

        Возвращает: True если шрифт загружен, в обратном случае False
        """

        # Проверка аргументов
        if type(out) is not bool:
            return False

        # Загрузка шрифта из файла
        try:
            for label in ['info', 'error', 'repeat']:
                self._font[label] = ImageFont.truetype(self._font['full_path'], self._args[label + '_size'])
        except IOError:
            # Вывод сообщения
            if out is True:
                print(self._font_not_load.format(self.red, datetime.now().strftime(self._format_time), self.end))

            return False

        return True

    # Захват фото/видеоданных
    def _grab_data(self, out = True):
        """
        Захват фото/видеоданных

        ([bool]) -> bool

        Аргументы:
            out - Печатать процесс выполнения

        Возвращает: True если захват фото/видеоданных произведен, в обратном случае False
        """

        # Проверка аргументов
        if type(out) is not bool:
            return False

        frame = None  # Кадр

        try:
            # Воспроизведение WEB-камеры
            self._args['file'] = int(self._args['file'])  # Попытка приведения названия файла к числу

            if self._args['file'] is not 0:
                # Вывод сообщения
                if out is True:
                    print(self._run_web_err.format(
                        self.red, datetime.now().strftime(self._format_time), self.end, 0
                    ))

                return False

            # Вывод сообщения
            if out is True:
                print(self._run_web.format(datetime.now().strftime(self._format_time)))

            self._cap = cv2.VideoCapture(self._args['file'])  # Открытие камеры для захвата видеопотока
            has_frame, frame = self._cap.read()  # Захват, декодирование и возврат кадра

            # Текущий кадр не получен
            if not has_frame:
                # Вывод сообщения
                if out is True:
                    print(self._web_not_found.format(
                        self.red, datetime.now().strftime(self._format_time), self.end
                    ))

                return False

            self._source = self._formats_data[0]  # Воспроизведение с WEB-камеры
        except ValueError:
            _, ext = os.path.splitext(self._args['file'])  # Расширение файла

            # Поиск файла
            if self.search_file(self._args['file'], ext.replace('.', ''), out = out) is False:
                return False

            # Поддерживаемые фото/видео форматы не найдены
            if (ext.replace('.', '') not in self._supported_video_formats
                    and ext.replace('.', '') not in self._supported_photo_formats):
                # Вывод сообщения
                if out is True:
                    print(self._wrong_extension.format(
                        self.red, datetime.now().strftime(self._format_time), self.end,
                        ', '.join(x for x in self._supported_photo_formats),
                        ', '.join(x for x in self._supported_video_formats)
                    ))

                return False

            # Воспроизведение видеопотока
            if ext.replace('.', '') in self._supported_video_formats:
                # Вывод сообщения
                if out is True:
                    print(self._run_video.format(datetime.now().strftime(self._format_time)))

                # Открытие камеры для захвата видеопотока
                self._cap = cv2.VideoCapture(self._args['file'])

                has_frame, frame = self._cap.read()  # Захват, декодирование и возврат кадра

                # Текущий кадр не получен
                if not has_frame:
                    # Вывод сообщения
                    if out is True:
                        print(self._video_not_read.format(
                            self.red, datetime.now().strftime(self._format_time), self.end
                        ))

                    return False

                self._all_frame_count = int(self._cap.get(cv2.CAP_PROP_FRAME_COUNT))  # Всего кадров в видеопотоке

                self._source = self._formats_data[1]  # Воспроизведение с видеофайла

            # Воспроизведение фото данных
            if ext.replace('.', '') in self._supported_photo_formats:
                # Вывод сообщения
                if out is True:
                    print(self._show_photo.format(datetime.now().strftime(self._format_time)))

                # Загрузка входного изображения
                self._cap = cv2.imread(self._args['file'])

                # Текущее фото не получено
                if self._cap is None:
                    # Вывод сообщения
                    if out is True:
                        print(self._photo_not_read.format(
                            self.red, datetime.now().strftime(self._format_time), self.end
                        ))

                    return False

                self._source = self._formats_data[2]  # Воспроизведение с фото данных

                frame = self._cap  # Текущий кадр

        self._curr_frame = frame  # Текущий кадр

        return True

    # Нанесение информации на изображение
    def _draw_info(self, text, base_coords, background_color, text_color, stroke, stroke_color, font, out = True):
        """
        Нанесение информации на изображение

        (str, tuple, tuple, tuple, int, tuple, PIL.ImageFont.FreeTypeFont [, bool]) -> bool

        Аргументы:
            text             - Текст
            base_coords      - Начальная координата
            background_color - Цвет фона
            text_color       - Цвет текста
            stroke           - Ширина обводки текста
            stroke_color     - Цвет обводки текста
            size             - Шрифт
            out              - Печатать процесс выполнения

        Возвращает: True если информация нанесена, в обратном случае False
        """

        # Проверка аргументов
        if (type(text) is not str or not text or type(base_coords) is not tuple or type(background_color) is not tuple
                or type(text_color) is not tuple or type(stroke) is not int or stroke < 0
                or type(stroke_color) is not tuple or type(font) is not ImageFont.FreeTypeFont
                or type(out) is not bool):
            # Вывод сообщения
            if out is True:
                print(self._invalid_arguments.format(
                    self.red, datetime.now().strftime(self._format_time),
                    self.end, __class__.__name__ + '.' + self._draw_info.__name__
                ))

            return False

        # Размеры текста
        (width_text, height_text), (offset_x, offset_y) = font.font.getsize(text)
        pad = font.getmask(text).getbbox()[0]

        # Нижняя правая точка прямоугольника
        point2 = (
            base_coords[0] + width_text + self._args['labels_padding'] * 2 - pad * 2,
            base_coords[1] + height_text + self._args['labels_padding'] * 2 - 1
        )

        # Рисование прямоугольной области в виде фона текста на изображении
        self._curr_frame_pil_obj.rectangle(
            [base_coords, point2],
            background_color,  # Цвет прямоугольника
        )

        # Нанесение текста на кадр
        self._curr_frame_pil_obj.text(
            (base_coords[0] + self._args['labels_padding'] - pad,
             base_coords[1] + self._args['labels_padding'] - offset_y), text,
            font = font,
            fill = text_color,
            stroke_width = stroke,
            stroke_fill = stroke_color
        )

        return True

    # Формирование итогового кадра
    def _composite(self):
        """
        Формирование итогового кадра

        () -> None
        """

        # Объединение прозрачного наложения с текущим кадром
        image_pil = Image.alpha_composite(self._curr_frame_pil, self._curr_frame_transparent)
        # Конвертация изображения в необходимый формат
        np.copyto(self._curr_frame, np.array(image_pil))

    # Надпись для терминала
    def _stdout_write(self, stdout, out = True):
        """
        Надпись для терминала

        (str [, bool]) -> bool

        Аргументы:
            stdout - Надпись
            out    - Печатать процесс выполнения

        Возвращает: True если надпись отравлена в терминал, в обратном случае False
        """

        # Проверка аргументов
        if type(stdout) is not str or not stdout or type(out) is not bool:
            # Вывод сообщения
            if out is True:
                print(self._invalid_arguments.format(
                    self.red, datetime.now().strftime(self._format_time),
                    self.end, __class__.__name__ + '.' + self._stdout_write.__name__
                ))

            return False

        # Вывод сообщения
        if out is True:
            sys.stdout.write('\r    {}\r    {}'.format(' ' * len(self._stdout), stdout))
            sys.stdout.flush()

        self._stdout = stdout

        return True

    # Циклическое получение кадров из видеопотока
    def _loop(self, other_source = None, func = None, out = True):
        """
        Циклическое получение кадров из фото/видеопотока

        ([bool]) -> bool

        Аргументы:
           other_source - Ресурс извлечения фото/видеоданных
           func         - Функция или метод которые выполняют операцию над изображением
           out          - Печатать процесс выполнения

        Возвращает: True если получение кадров осуществляется, в обратном случае False
        """

        # Проверка аргументов
        if type(out) is not bool:
            return False

        start_time = time.time()  # Отсчет времени выполнения

        # Автоматическая проверка конфигурационного файла в момент работы программы
        self._update_config_json()

        if other_source is None:
            # Блокировка отображения повторных раз фото
            if self._frame_count > 1 and self._source == self._formats_data[2] and self.clear_image_buffer is False:
                return True

            # Видеопоток или WEB-камера
            if self._source != self._formats_data[2]:
                # Повторение воспроизведения видеопотока
                if self._source is self._formats_data[1] and self._frame_count == (self._all_frame_count - 1) and \
                        (self.repeat is True or self._args['repeat'] is True):
                    self._cap.set(cv2.CAP_PROP_POS_FRAMES, 1)  # Сброс видеопотока в начальную позицию

                    self._frame_count = 0  # Сброс счетчика кадров в начальную позицию

                    self.repeat = False  # Повторное воспроизведения видеофайла отключено
                    self._show_notification = False  # Скрытие уведомления

                self.repeat = False  # Повторное воспроизведения видеофайла отключено

                has_frame, frame = self._cap.read()  # Захват, декодирование и возврат кадра

                # Текущий кадр не получен
                if not has_frame:
                    if self._show_notification is False:
                        # Отображение надписей в терминале
                        if self._args['show_labels'] is False:
                            # Надпись для терминала
                            self._stdout_write(
                                '[{}] {} - {}'.format(
                                    datetime.now().strftime(self._format_time),
                                    self._repeat_video[0], self._repeat_video[1]
                                ),
                                out = out
                            )
                        else:
                            # Размеры текста
                            (width_text_top, height_text_top), (offset_x_top, offset_y_top) = \
                                self._font['repeat'].font.getsize(self._repeat_video[0])
                            pad_top = self._font['repeat'].getmask(self._repeat_video[0]).getbbox()[0]

                            width_text_top -= pad_top

                            # Размеры текста
                            (width_text_bottom, height_text_bottom), (offset_x_bottom, offset_y_bottom) = \
                                self._font['info'].font.getsize(self._repeat_video[1])
                            pad_bottom = self._font['info'].getmask(self._repeat_video[1]).getbbox()[0]

                            width_text_bottom -= pad_bottom

                            max_width_text = max([width_text_top, width_text_bottom])  # Максимальная ширина

                            center_x = int(self._curr_frame.shape[1] / 2)  # Ширина
                            center_y = int(self._curr_frame.shape[0] / 2)  # Высота
                            # Координаты для прямоугольной области
                            x_top = int(center_x - max_width_text / 2)
                            y_top = int(center_y -
                                        (height_text_top + height_text_bottom + self._args['labels_distance']) / 2)

                            # Нижняя правая точка прямоугольника
                            point2 = (x_top + max_width_text + self._args['labels_padding'], y_top +
                                      (height_text_top + height_text_bottom + self._args['labels_distance']) +
                                      self._args['labels_padding'])

                            # Рисование прямоугольной области в виде фона текста на изображении
                            self._curr_frame_pil_obj.rectangle(
                                [(x_top - self._args['labels_padding'], y_top - self._args['labels_padding']), point2],
                                # Цвет прямоугольника
                                (self._args['repeat_background_color']['red'],
                                 self._args['repeat_background_color']['green'],
                                 self._args['repeat_background_color']['blue'],
                                 self._args['repeat_background_color']['alpha'])
                            )

                            # Нанесение текста на кадр
                            self._curr_frame_pil_obj.text(
                                (int(center_x - width_text_top / 2) - pad_top, y_top - offset_y_top),
                                self._repeat_video[0],
                                font = self._font['repeat'],
                                fill = (self._args['repeat_text_color']['red'],
                                        self._args['repeat_text_color']['green'],
                                        self._args['repeat_text_color']['blue'],
                                        self._args['repeat_text_color']['alpha']),
                                stroke_width = self._args['repeat_stroke'],
                                stroke_fill = (self._args['repeat_stroke_color']['red'],
                                               self._args['repeat_stroke_color']['green'],
                                               self._args['repeat_stroke_color']['blue'],
                                               self._args['repeat_stroke_color']['alpha']))

                            # Нанесение текста на кадр
                            self._curr_frame_pil_obj.text(
                                (int(center_x - width_text_bottom / 2) - pad_bottom,
                                 y_top + height_text_top + self._args['labels_distance'] - offset_y_bottom),
                                self._repeat_video[1],
                                font = self._font['info'],
                                fill = (self._args['repeat_text_color']['red'],
                                        self._args['repeat_text_color']['green'],
                                        self._args['repeat_text_color']['blue'],
                                        self._args['repeat_text_color']['alpha']),
                                stroke_width = self._args['repeat_stroke'],
                                stroke_fill = (self._args['repeat_stroke_color']['red'],
                                               self._args['repeat_stroke_color']['green'],
                                               self._args['repeat_stroke_color']['blue'],
                                               self._args['repeat_stroke_color']['alpha']))

                            self._composite()  # Формирование итогового кадра

                        self._show_notification = True  # Уведомление показано

                    return True

                    # return -1  # Прерывание цикла
            else:
                frame = self._cap  # Изображение
                self.clear_image_buffer = self._args['clear_image_buffer']  # Очистка буфера с изображением

            self._frame_count += 1  # Номер текущего кадра

            self._curr_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGBA)  # Преобразование изображения

            # Отображение надписей в окне воспроизведения
            if self._args['show_labels'] is True:
                # Прозрачное наложение на текущий кадр
                self._curr_frame_transparent = Image.new('RGBA',
                                                         (self._curr_frame.shape[1], self._curr_frame.shape[0]),
                                                         (255, 255, 255, 0))

                # Текущий кадр в формате PIL
                self._curr_frame_pil = Image.fromarray(np.uint8(self._curr_frame))
                # Создание объекта, который можно использовать для рисования поверх изображения
                self._curr_frame_pil_obj = ImageDraw.Draw(self._curr_frame_transparent, 'RGBA')
        else:
            other_source()  # Извлечение фото/видеоданных из сторонего ресурса

        # Выполнение функции/метода
        if func is not None and (type(func) is MethodType or type(func) is FunctionType) and \
                self._automatic_update['invalid_config_file'] is False:
            func()  # Выполнение операций над изображением

        # Принудительная задержка для воспроизведения видеопотока с реальным количеством FPS
        if self._args['real_time'] is True and self._source != self._formats_data[2]:
            end_time = time.time() - start_time  # Конец времени выполнения

            # Получение реальной частоты кадров
            if self._args['fps'] == 0 or self._source is self._formats_data[0]:
                self._args['fps'] = self._cap.get(cv2.CAP_PROP_FPS) if other_source is None else self._cap_prop_fps

            try:
                delay = 1 / self._args['fps']  # Задержка
            except ZeroDivisionError:
                delay = 0.03 if other_source is None else 0.001  # Задержка (на случай если частота кадров 0 FPS)

            # Необходимо произвести задержку видеопотока
            if delay > end_time:
                time.sleep(delay - end_time)  # Принудительная задержка

        # Количество кадров больше 60
        if self._prev_fps > 60 and self._args['real_time'] is False:
            label_fps = self._frame_rate_static   # Текст с стическим FPS
        else:
            label_fps = self._frame_rate.format(self._prev_fps)  # Текст с FPS

        # Отображение надписей в терминале
        if self._args['show_labels'] is False:
            if self._automatic_update['invalid_config_file'] is False:
                # Надпись для терминала
                self._stdout_write(
                    '[{}] {}'.format(datetime.now().strftime(self._format_time), label_fps),
                    out = out
                )
        else:
            # Нанесение информации на изображение
            self._draw_info(
                text = label_fps,
                base_coords = (self._args['labels_base_coords']['left'], self._args['labels_base_coords']['top']),
                background_color = (self._args['info_background_color']['red'],
                                    self._args['info_background_color']['green'],
                                    self._args['info_background_color']['blue'],
                                    self._args['info_background_color']['alpha']),
                text_color = (self._args['info_text_color']['red'],
                              self._args['info_text_color']['green'],
                              self._args['info_text_color']['blue'],
                              self._args['info_text_color']['alpha']),
                stroke = self._args['info_stroke'],
                stroke_color = (self._args['info_stroke_color']['red'],
                                self._args['info_stroke_color']['green'],
                                self._args['info_stroke_color']['blue'],
                                self._args['info_stroke_color']['alpha']),
                font = self._font['info'],
                out = out
            )

        if self._automatic_update['invalid_config_file'] is True:
            # Отображение надписей в терминале
            if self._args['show_labels'] is False:
                # Надпись для терминала
                self._stdout_write(
                    '[{}] {}'.format(datetime.now().strftime(self._format_time), self._check_config_file_not_valid),
                    out = out
                )
            else:
                # Размеры текста
                (_, height_text), (_, _) = self._font['error'].font.getsize(self._check_config_file_not_valid)

                self._draw_info(
                    text = self._check_config_file_not_valid,
                    base_coords = (0, self._curr_frame.shape[0] - height_text - self._args['labels_padding'] * 2),
                    background_color = (self._args['error_background_color']['red'],
                                        self._args['error_background_color']['green'],
                                        self._args['error_background_color']['blue'],
                                        self._args['error_background_color']['alpha']),
                    text_color = (self._args['error_text_color']['red'],
                                  self._args['error_text_color']['green'],
                                  self._args['error_text_color']['blue'],
                                  self._args['error_text_color']['alpha']),
                    stroke = self._args['error_stroke'],
                    stroke_color = (self._args['error_stroke_color']['red'],
                                    self._args['error_stroke_color']['green'],
                                    self._args['error_stroke_color']['blue'],
                                    self._args['error_stroke_color']['alpha']),
                    font = self._font['error'],
                    out = out
                )

        # Отображение надписей в окне воспроизведения
        if self._args['show_labels'] is True:
            # Надпись для терминала
            self._stdout_write(
                '[{}] {}'.format(datetime.now().strftime(self._format_time), self._labels_in_window),
                out = out
            )

            self._composite()  # Формирование итогового кадра

        self.image_buffer = self._curr_frame  # Отправка изображения в буфер

        try:
            fps = round(1 / (time.time() - start_time), 2)  # FPS

            self._prev_fps = fps  # Частота кадра
        except ZeroDivisionError:
            pass

        return True

    # ------------------------------------------------------------------------------------------------------------------
    #  Внешние методы
    # ------------------------------------------------------------------------------------------------------------------

    # Запуск
    def run(self, metadata = pvv, resources = configs, start = True, out = True):
        """
        Запуск

        ([module, module, bool, bool]) -> None

        Аргументы:
            metadata  - Модуль из которого необходимо извлечь информацию
            resources - Модуль с ресурсами
            start     - Запуск процесса извлечения изображений
            out       - Печатать процесс выполнения
        """

        # Проверка аргументов
        if type(out) is not bool or type(start) is not bool or not isinstance(metadata, ModuleType) \
                or not isinstance(resources, ModuleType):
            # Вывод сообщения
            if out is True:
                print(self._invalid_arguments.format(
                    self.red, datetime.now().strftime(self._format_time),
                    self.end, __class__.__name__ + '.' + self.run.__name__
                ))

            return False

        self._args = self._build_args()  # Построение аргументов командной строки

        self.clear_shell(self._args['no_clear_shell'])  # Очистка консоли перед выполнением

        # Вывод сообщения
        if out is True:
            # Приветствие
            Shell.add_line()  # Добавление линии во весь экран
            print(self._pvv.format(self.bold, self.blue, self.end))
            Shell.add_line()  # Добавление линии во весь экран

        # Загрузка и проверка конфигурационного файла
        if self._load_config_json(resources, out = out) is False:
            return False

        # Поиск шрифта из ресурсов пакета
        if self._search_font(out = out) is False:
            return False

        # Вывод сообщения
        if out is True:
            Shell.add_line()  # Добавление линии во весь экран

        # Запуск
        if self._args['hide_metadata'] is False and out is True:
            print(self._metadata.format(
                datetime.now().strftime(self._format_time),
                metadata.__author__,
                metadata.__email__,
                metadata.__maintainer__,
                metadata.__version__
            ))

            Shell.add_line()  # Добавление линии во весь экран

        # Захват фото/видеоданных
        if self._grab_data(out = out) is False:
            return False

        self.window_name = self._args['window_name']  # Установка имени окна

        # Ширина и высота нулевые
        if self._args['resize']['width'] == 0 and self._args['resize']['height'] == 0:
            self._args['resize']['height'] = self._curr_frame.shape[0]  # Высота изображения
            self._args['resize']['width'] = self._curr_frame.shape[1]  # Ширина изображения

        self.window_width = self._args['resize']['width']  # Установка ширины окна 
        self.window_height = self._args['resize']['height']  # Установка высоты окна

        self._out = out  # Печатать процесс выполнения

        # Запуск процесса извлечения изображений
        if start is True:
            self.set_loop(self._loop)  # Циклическая функция извлечения изображений
            self.start()  # Запуск


def main():
    run = Run()

    run.run()


if __name__ == "__main__":
    main()
