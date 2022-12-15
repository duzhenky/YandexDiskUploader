# YandexDiskUploader

***Программа выполняет резервное копирование данных, а также создание и/или обновление папок Документы, Музыка, Фото, Видео, 
PycharmProjects на Яндекс.Диске*** 

*Совместима только c ОС Windows*

### Использование

При первом запуске пользователь должен пройти OAuth-авторизацию, т.е. ввести OAuth-токен Яндекс.Диска.
[Подробная информация о том, что такое OAuth и как получить OAuth-токен на официальном сайте Яндекса.](https://yandex.ru/dev/id/doc/dg/oauth/concepts/about.html)
Введённый пользователем токен сохраняется в файле *token.txt* в директории проекта, после чего нужно перезапустить программу. 
При повторном запуске он будет подгружен автоматически.

На данный момент в программе предусмотрен следующий функционал:
1) Резервное копирование данных
2) Загрузка/обновление папки Документы
3) --//-- Музыка
4) --//-- Фото
5) --//-- Видео
6) --//-- Программирование


### Некоторые особенности и преимущества перед стандартным загрузчиком:

1) резервное копирование включает в себя копирование папок **Документы**, **Музыка**, **Фото** и **Видео** 
(действие 1). Резервное копирование выполняется в отдельную папку *BackUp/имя_пользователя/дата_резервного_копирвоания*. При 
необходимости такая директория будет создана на **Яндекс.Диске**;
2) папки **Документы**, **Музыка**, **Фото** и **Видео** загружаются на **Яндекс.Диск** из соответствующих директорий на ПК пользователя.
Если на **Диске** до этого не было директорий с аналогичными названиями, то они будут созданы в корне автоматически 
(действия 2-5, действие 6 - **PycharmProjects** загружается в папку **Программирование**).
3) при загрузке игнорируются папки, содержащие названия  **venv, .git, .idea, \_\_pycache__**, в частности 
это касается **PycharmProjects** (действие 6); 
4) при загрузке файлов с ПК на **Яндекс.Диск** программа определяет содержатся ли они уже на 
**Диске** в соответствующей директории. Если файлы совпадают по названию и содержимому, загрузка не происходит.
Если только по названию, но содержимое другое, то добавляется постфикс с датой и временем последнего изменения 
файла на ПК и он загружается с этим постфиксом. В остальных случаях происходит стандартная загрузка файлов;
5) после загрузки на **Яндекс.Диск** в консоли выводится сообщение об объёме загруженного контента и времени,
затраченного на загрузку.

### Недостатки:
1) отсутствует возможность загрузки больших файлов. Мне не удалось исправить эту ошибку. Это связано с 
TimeoutError, ProtocolError, ConnectionError. При возникновении таких ошибок файлы не могут быть загружены.
В таком случае на рабочий стол пользователя записывается txt-файл *YandexDiskUploader_LogErrors_текущая_дата*,
содержащий наименование ошибки, путь к загружаемому файлу на ПК и место, куда он должен был быть загружен.
Файлы, перечисленные в лог-файле, могут быть загружены вручную.
