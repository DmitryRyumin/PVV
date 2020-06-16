#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Глобальный файл настроек
"""

# ######################################################################################################################
# Импорт необходимых инструментов
# ######################################################################################################################
# Интернационализация (I18N) и локализация (L10N) (см. https://www.loc.gov/standards/iso639-2/php/code_list.php)
import gettext
import argparse  # Парсинг аргументов и параметров командной строки
import os  # Взаимодействие с файловой системой
import sys  # Доступ к некоторым переменным и функциям Python


# ######################################################################################################################
# Класс для определения языка
# ######################################################################################################################
class Language:
    """Класс для определения языка"""

    # ------------------------------------------------------------------------------------------------------------------
    # Конструктор
    # ------------------------------------------------------------------------------------------------------------------

    def __init__(self):
        # Директория с поддерживаемыми языками
        self._path_to_locales = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'locales'))
        self._lang_default = 'en'  # Язык по умолчанию

        self._locales = self._get_languages()  # Поддерживаемые языки

        self._ = self.set_locale()  # Получение языка для всего приложения

    # ------------------------------------------------------------------------------------------------------------------
    # Свойства
    # ------------------------------------------------------------------------------------------------------------------

    @property
    def path_to_locales(self):
        return os.path.normpath(self._path_to_locales)  # Нормализация пути

    @property
    def locales(self):
        return self._locales

    # ------------------------------------------------------------------------------------------------------------------
    #  Внутренние методы
    # ------------------------------------------------------------------------------------------------------------------

    # Получение списка поддерживаемых языков
    def _get_languages(self):
        """
        Получение списка поддерживаемых языков

        () -> list

        Возвращает: список поддерживаемых языков
        """

        # Директория с языками найдена
        if os.path.exists(self.path_to_locales):
            # Формирование списка с подерживаемыми языками
            return next(os.walk(self.path_to_locales))[1]

        return []

    # ------------------------------------------------------------------------------------------------------------------
    # Внешние методы
    # ------------------------------------------------------------------------------------------------------------------

    # Установка языка
    def set_locale(self):
        """
        Установка языка

        () -> GNUTranslations.gettext

        Возвращает: метод перевода строк
        """

        # Проход по всем языкам
        for lang in self.locales:
            # В аргументах командной строки не найден язык
            if lang not in sys.argv:
                continue

            self._lang_default = lang  # Изменения языка

        el = gettext.translation(
            'pvv',  # Домен
            localedir = self.path_to_locales,  # Директория с поддерживаемыми языками
            languages = [self._lang_default],  # Язык
            fallback = True  # Отключение ошибки
        )

        tr = gettext.translation(
            'argparse',  # Домен
            localedir = self.path_to_locales,  # Директория с поддерживаемыми языками
            languages = [self._lang_default],  # Язык
            fallback = True  # Отключение ошибки
        )

        argparse._ = tr.gettext

        return el.gettext


# ######################################################################################################################
# Класс для выделения текста
# ######################################################################################################################
class Color(Language):
    """Класс для выделения текста"""

    # ------------------------------------------------------------------------------------------------------------------
    # Конструктор
    # ------------------------------------------------------------------------------------------------------------------

    def __init__(self):
        super().__init__()  # Выполнение конструктора из суперкласса

        self._green = '\033[92m'  # Зеленый
        self._red = '\033[91m'    # Красный
        self._blue = '\033[94m'   # Синий
        self._bold = '\033[1m'    # Жирный
        self._end = '\033[0m'     # Выход

    # ------------------------------------------------------------------------------------------------------------------
    # Свойства
    # ------------------------------------------------------------------------------------------------------------------

    @property
    def green(self):
        return self._green

    @property
    def red(self):
        return self._red

    @property
    def blue(self):
        return self._blue

    @property
    def bold(self):
        return self._bold

    @property
    def end(self):
        return self._end


# ######################################################################################################################
# Класс для сообщений
# ######################################################################################################################
class Messages(Color):
    """Класс для сообщений"""

    # ------------------------------------------------------------------------------------------------------------------
    # Конструктор
    # ------------------------------------------------------------------------------------------------------------------

    def __init__(self):
        super().__init__()  # Выполнение конструктора из суперкласса

        self._metadata = self._(
            '[{}] Запуск: \n    '
            'Автор: {}\n    '
            'Email: {}\n    '
            'Сопровождающие: {}\n    '
            'Версия: {}')

        self._format_time = '%Y-%m-%d %H:%M:%S'  # Формат времени

        self._invalid_arguments = self._('[{}{}{}] Неверные типы аргументов в "{}" ...')

        self._invalid_args = self._('[{}{}{}] Необходимые значения в командной строке не найдены ...')
