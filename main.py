import yadisk
import os
import hashlib
from tqdm import tqdm
import datetime as dt
from colorama import Fore, Style
from urllib3.exceptions import ProtocolError
from requests.exceptions import ConnectionError

current_date = str(dt.date.today())
home_username = os.getlogin()


def get_token(error):

    """
    Функция для сохранения токена пользователя.
    Запускается всякий раз при ошибке авторизации пользователя
    :param error: отображаемая ошибка
    """

    print('Ошибка авторизации:', error)
    tok = input('Вставьте токен Яндекс.Диска: ')
    with open('token.txt', 'w', encoding='utf-8') as f:
        f.write(tok)
        print('Токен записан. Он будет использован в дальнейшем\n'
              'Нажмите ENTER и перезапустите приложение')
        input()


# авторизация пользователя
try:
    with open('token.txt', 'r', encoding='utf-8') as f:
        token = f.read()
except FileNotFoundError as e:
    get_token(e)

y = yadisk.YaDisk(token=token)


def get_hash(filename):

    """
    Функция для получения хэш файла
    :param filename: путь к файлу
    :return: хэш файла
    """

    with open(filename, "rb") as f:
        bytes = f.read()  # read entire file as bytes
        readable_hash = hashlib.sha256(bytes).hexdigest()
        return readable_hash


def write_log_errors(error, path1, path2):

    """
    Функция для записи логов ошибок.
    При возникновении ошибок TimeoutError, ProtocolError, ConnectionError, файл не может быть загружен.
    В таком случае на рабочий стол пользователя записывается txt-файл "YandexDiskUploader_LogErrors_ткущая_дата",
    содержащий наименование ошибки, путь к загружаемому файлу на ПК и место, куда он должен был быть загружен.
    Файлы, перечисленные в лог-файле, могут быть загружены вручную. Как правило, это большие файлы.
    :param error: наименование ошибки
    :param path1: путь к файлу на ПК
    :param path2: путь загрузки файла на Яндекс.Диске
    """

    log_filename = 'YandexDiskUploader_LogErrors_' + current_date
    error_log_text = f'{error.upper()}\n' \
                     f'Файл не загружен: "{path1}"\n' \
                     f'Загрузите его вручную в: {path2}\n\n'

    with open(fr'C:\Users\{home_username}\Desktop\{log_filename}.txt', 'a') as f:
        f.write(error_log_text)


def get_current_used_space():

    """
    Функция для отображения текущего занятого пространства на диске
    :return: информация о занятом пространстве
    """

    disk_info = y.get_disk_info()
    used_space = disk_info['used_space']
    return used_space


def get_uploaded_space_and_spent_time(func):
    def wrapper(*args, **kwargs):

        """
        Функция-декоратор для вычисления размера загруженных данных на Яндекс.Диск.
        Предназначена для отображения объёма загруженного контента и времени, затраченного на загрузку.
        :param used_space_before: использованное пространство до выполнения данного скрипта
        :param used_space_after: использованное пространство после выполнения данного скрипта
        """
        disk_info_before = y.get_disk_info()
        used_space_before = disk_info_before['used_space']
        time_before = dt.datetime.now()
        a = func(*args, **kwargs)
        time_after = dt.datetime.now()
        disk_info_after = y.get_disk_info()
        used_space_after = disk_info_after['used_space']
        uploaded_size = used_space_after - used_space_before

        spent_time = time_after - time_before
        spent_time_str = str(spent_time)
        spent_time_list = spent_time_str.split(':')
        hours = spent_time_list[0]
        minutes = spent_time_list[1]
        seconds = spent_time_list[2].split('.')[0]
        spent_time_result = hours + ' ч. ' + minutes + ' мин. ' + seconds + ' сек.'

        if uploaded_size <= 1_073_741_824:
            uploaded_size_str = str(round(uploaded_size / 1024 / 1024, 2)) + ' Мб'
        else:
            uploaded_size_str = str(round(uploaded_size / 1024 / 1024 / 1024, 2)) + ' Гб'

        info = f'Было загружено: {uploaded_size_str}\n' \
               f'Затрачено времени: {spent_time_result}\n'
        print(Fore.WHITE + Style.NORMAL + info)
        return a

    return wrapper


def get_disk_info():

    """
    Функция для передачи общей информации о состоянии Яндекс.Диска:
    - объём диска;
    - занятое пространство;
    - пространство корзины.
    """

    disk_info = y.get_disk_info()

    total_space = disk_info['total_space']
    used_space = disk_info['used_space']
    trash_size = disk_info['trash_size']
    per_of_used_space = round(used_space / total_space * 100, 1)

    total_space_str = str(round(total_space / 1024 / 1024 / 1024 / 1024, 3)) + ' Тб'
    if used_space <= 1_073_741_824:
        used_space_str = str(round(used_space / 1024 / 1024, 2)) + ' Мб'
    else:
        used_space_str = str(round(used_space / 1024 / 1024 / 1024)) + ' Гб'
    if trash_size <= 1_073_741_824:
        trash_size_str = str(round(trash_size / 1024 / 1024, 2)) + ' Мб'
    else:
        trash_size_str = str(round(trash_size / 1024 / 1024 / 1024, 2)) + ' Гб'
    per_of_used_space_str = str(per_of_used_space) + ' %'

    info = f'Объём диска: {total_space_str}\n' \
           f'Занятое пространство: {used_space_str} ({per_of_used_space_str}) \n' \
           f'В корзине: {trash_size_str}\n'

    print(Fore.YELLOW + Style.BRIGHT + '\nИНФОРМАЦИЯ О ДИСКЕ')
    print(Fore.WHITE + Style.NORMAL + info)


def create_folder(folder_name):

    """
    Функция для создания папки на Яндекс.Диске
    :param folder_name: путь, например, "/Фото"
    """

    try:
        y.mkdir(folder_name)
    except yadisk.exceptions.PathExistsError:
        pass


def upload_file(filename, file_path_from, file_path_to):

    """
    Функия для загрузки файла с ПК на Яндекс.Диск.
    Если файлы совпадают по названию и содержимому, загрузка файла не происходит.
    Если только по названию, но содержимое другое, то добавляется приставка с датой и временем последнего изменения
    и файл загружается с этой приставкой.
    В остальных случаях происходит стандартная загрузка файлов
    :param filename: имя загружаемого файла
    :param file_path_from: путь к файлу на ПК
    :param file_path_to: путь к файлу на Яндекс.Диске
    """

    src = file_path_from + '\\' + filename
    dst = file_path_to + '/' + filename

    try:
        y.upload(src, dst)

    except yadisk.exceptions.PathExistsError:
        yd_file_info = y.get_meta(dst)

        # Если названия и хэш совпадают - пропускаем
        if (src.split('\\')[-1] == dst.split('/')[-1]) and (get_hash(src) == yd_file_info['sha256']):
            pass

        # Если сопадает только название, а хэш нет, добавляем к назваанию файла дату последнего изменения
        elif (src.split('\\')[-1] == dst.split('/')[-1]) and (get_hash(src) != yd_file_info['sha256']):
            datetime_of_modification = os.path.getmtime(src)
            datetime_of_modification_h = dt.datetime.fromtimestamp(datetime_of_modification).strftime(
                '%Y-%m-%d %H:%M:%S')
            addition_to_filename = ' (изм ' + datetime_of_modification_h.replace(':', '-') + ')'
            try:
                y.upload(src, dst.split('.')[0] + addition_to_filename + '.' + dst.split('.')[1])
            except yadisk.exceptions.PathExistsError:
                pass

    except yadisk.exceptions.PathNotFoundError:
        pass

    except TimeoutError as e:
        print(f'\n{Fore.RED + Style.NORMAL} Файл "{filename}" из папки "{file_path_from}" не загружен:\n'
              f'{e}{Style.RESET_ALL}\n')
        write_log_errors(str(e), src, dst)

    except ProtocolError as e:
        print(f'\n{Fore.RED + Style.NORMAL} Файл "{filename}" из папки "{file_path_from}" не загружен:\n'
              f'{e}{Style.RESET_ALL}\n')
        write_log_errors(str(e), src, dst)

    except ConnectionError as e:
        print(f'\n{Fore.RED + Style.NORMAL} Файл "{filename}" из папки "{file_path_from}" не загружен:\n'
              f'{e}{Style.RESET_ALL}\n')
        write_log_errors(str(e), src, dst)


@get_uploaded_space_and_spent_time
def upload_folder(folder_from: str, folder_to: str):

    """
    Функция для загрузки папки с ПК на Яндекс.Диск.
    С помощью данной функции роисходит полное копирование директории со всеми папками и файлами внутри.
    :param folder_from: путь к папке на ПК
    :param folder_to: путь к папке на Яндекс.Диске
    :return: загрузка папки
    """

    # создание папки, в которую всё будет загружено
    create_folder(folder_to)

    print(Fore.CYAN + Style.NORMAL + 'Обработка директорий')
    # создание папок на Яндекс.Диске по структуре как на ПК
    for dirpath, dirnames, filenames in os.walk(folder_from):
        # папки venv, .git, .idea, __pychahe__ не создаются
        if ('venv' not in dirpath) and \
                ('.git' not in dirpath) and \
                ('.idea' not in dirpath) and \
                ('__pycache__' not in dirpath):
            for dirname in dirnames:
                if ('venv' not in dirname) and \
                        ('.git' not in dirname) and \
                        ('.idea' not in dirname) and \
                        ('__pycache__' not in dirname):
                    create_folder(dirpath.replace(folder_from, folder_to).replace('\\', '/') + '/' + dirname)
                else:
                    continue
        else:
            continue

    # копирование файлов в папки
    print(Fore.CYAN + Style.NORMAL + '\nЗагрузка файлов')
    for dirpath, dirnames, filenames in os.walk(folder_from):
        # файлы из папок venv, .git, .idea, __pychahe__ не загружаются
        if ('venv' not in dirpath) and \
                ('.git' not in dirpath) and \
                ('.idea' not in dirpath) and \
                ('__pycache__' not in dirpath):
            for filename in tqdm(filenames):
                upload_file(filename, dirpath, dirpath.replace(folder_from, folder_to).replace('\\', '/'))
                print(dirpath.replace(folder_from, folder_to).replace('\\', '/'), filename, sep='/', end='')
        else:
            continue

    print(Fore.CYAN + Style.NORMAL + '\nЗагрузка файлов завершена', end='\n')


def backup_data():

    """
    Бэкап данных из ключевых папок ПК на Яндекс.Диск.
    Содержимое из папок "Documents", "Pictures", "Videos", "Music", "PycharmProjects" ПК
    копируется в папку /BackUp/имя_пользователя_ПК/дата_резервной_копии на Яндекс.Диске
    """

    print(Fore.YELLOW + Style.BRIGHT + '\nРЕЗЕРВНОЕ КОПИРОВАНИЕ\n')
    print(f'{Style.RESET_ALL}Содержимое ПК из папок Documents, "Pictures", "Videos", "Music", "PycharmProjects"\n'
          f'будет загружено в папку "/BackUp/{home_username}/{current_date}"\n')

    # создание папок на Я.Диске
    create_folder('/BackUp')
    create_folder(f'/BackUp/{home_username}')
    create_folder(f'/BackUp/{home_username}/{current_date}')

    # загрузка данных в указанную папку
    # 'Documents', 'Pictures', 'Videos', 'Music', 'PycharmProjects'
    print(Fore.YELLOW + Style.BRIGHT + '\nДокументы')
    upload_folder(fr"C:\Users\{home_username}\Documents", f"/BackUp/{home_username}/{current_date}/Документы")

    print(Fore.YELLOW + Style.BRIGHT + '\nФото')
    upload_folder(fr"C:\Users\{home_username}\Pictures", f"/BackUp/{home_username}/{current_date}/Фото")

    print(Fore.YELLOW + Style.BRIGHT + '\nВидео')
    upload_folder(fr"C:\Users\{home_username}\Videos", f"/BackUp/{home_username}/{current_date}/Видео")

    print(Fore.YELLOW + Style.BRIGHT + '\nМузыка')
    upload_folder(fr"C:\Users\{home_username}\Music", f"/BackUp/{home_username}/{current_date}/Музыка")

    print(Fore.YELLOW + Style.BRIGHT + '\nПрограммирование')
    upload_folder(fr"C:\Users\{home_username}\PycharmProjects",
                  f"/BackUp/{home_username}/{current_date}/Программирование")


def main():

    """
    ИНТЕРФЕЙС

    Пользователь выбирает:
        1) Резервное копирование данных
        2) Обновление папки "Документы"
        3) Обновление папки "Музыка"
        4) Обновление папки "Фото"
        5) Обновление папки "Видео"
        6) Обновление папки "Программирование"
    :return: происходит указанное пользователем действие
    """

    main_menu = f'Выберете действие:\n' \
                f'\t1.{Style.BRIGHT + Fore.YELLOW} Резервное копирование {Style.RESET_ALL}данных\n' \
                f'\t{Style.RESET_ALL}2. Обновить папку {Style.BRIGHT + Fore.YELLOW}"Документы"\n' \
                f'\t{Style.RESET_ALL}3. Обновить папку {Style.BRIGHT + Fore.YELLOW}"Музыка"\n' \
                f'\t{Style.RESET_ALL}4. Обновить папку {Style.BRIGHT + Fore.YELLOW}"Фото"\n' \
                f'\t{Style.RESET_ALL}5. Обновить папку {Style.BRIGHT + Fore.YELLOW}"Видео"\n' \
                f'\t{Style.RESET_ALL}6. Обновить папку {Style.BRIGHT + Fore.YELLOW}"Программирование"\n'

    while True:
        get_disk_info()

        print(Style.RESET_ALL + main_menu)
        choice = input(f'{Style.RESET_ALL}Ваш выбор: ')

        if choice == '1':
            backup_data()
            get_disk_info()

        elif choice == '2':
            print(Fore.YELLOW + Style.BRIGHT + '\nЗАГРУЗКА ДОКУМЕНТОВ')
            upload_folder(fr"C:\Users\{home_username}\Documents", "/Документы")
            get_disk_info()

        elif choice == '3':
            print(Fore.YELLOW + Style.BRIGHT + '\nЗАГРУЗКА МУЗЫКИ')
            upload_folder(fr"C:\Users\{home_username}\Music", "/Музыка")
            get_disk_info()

        elif choice == '4':
            print(Fore.YELLOW + Style.BRIGHT + '\nЗАГРУЗКА ФОТО')
            upload_folder(fr"C:\Users\{home_username}\Pictures", "/Фото")
            get_disk_info()

        elif choice == '5':
            print(Fore.YELLOW + Style.BRIGHT + '\nЗАГРУЗКА ВИДЕО')
            upload_folder(fr"C:\Users\{home_username}\Videos", "/Видео")
            get_disk_info()

        elif choice == '6':
            print(Fore.YELLOW + Style.BRIGHT + '\nЗАГРУЗКА ПРОЕКТОВ')
            upload_folder(fr"C:\Users\{home_username}\PycharmProjects", "/Программирование")
            get_disk_info()

        else:
            pass
        input(f'{Style.RESET_ALL}Для продолжения нажмите {Style.BRIGHT + Fore.YELLOW}ENTER ')


if __name__ == "__main__":
    try:
        main()
    except yadisk.exceptions.ResourceIsLockedError:
        print(f'{Style.RESET_ALL}\nЯндекс.Диск занят другим процессом, Пожалуйста, повторите попытку позже...')
    except yadisk.exceptions.UnauthorizedError as e:
        get_token(e)
    except UnicodeEncodeError:
        get_token('Токен не может содержать кириллические символы')
