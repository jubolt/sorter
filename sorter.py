import os
import shutil
import datetime

# Пути к папкам
in_folder = 'in'
out_folder = 'out'
log_folder = 'log'

# Создаем папки, если они не существуют
for folder in [in_folder, out_folder, log_folder]:
    os.makedirs(folder, exist_ok=True)

# Словарь для подсчета количества перемещенных файлов
move_count = {}

# Проходим по всем файлам в папке in
for filename in os.listdir(in_folder):
    file_path = os.path.join(in_folder, filename)
    
    if os.path.isfile(file_path):
        # Проходим по всем папкам в out
        for folder_name in os.listdir(out_folder):
            folder_path = os.path.join(out_folder, folder_name)

            if os.path.isdir(folder_path):
                # Извлекаем часть после "_", если она есть
                folder_parts = folder_name.split('_', 1)
                keyword = folder_parts[1] if len(folder_parts) > 1 else folder_parts[0]

                # Проверяем, содержится ли keyword в названии файла
                if keyword in filename:
                    shutil.move(file_path, os.path.join(folder_path, filename))
                    move_count[keyword] = move_count.get(keyword, 0) + 1

# Записываем лог
date = datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
log_file_path = os.path.join(log_folder, f'log{date}.txt')

with open(log_file_path, 'w', encoding='utf8') as log_file:
    for folder_name, count in move_count.items():
        log_file.write(f'В папку "{folder_name}" перемещено {count} файлов\n')

print("Файлы успешно перемещены. Лог записан.")
