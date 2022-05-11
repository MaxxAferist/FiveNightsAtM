path = "data\Transitions_copy"
import os

dirs = os.listdir(path)
for dir in dirs:
    cur_path = path + '/' + dir
    files = os.listdir(cur_path)
    photos = []
    for file in files:
        if file.endswith(('png', 'jpg')):
            photos.append(file)
    for photo in enumerate(photos):
        if photo[0] % 3 != 0:
            os.remove(f'{cur_path}/{photo[1]}')