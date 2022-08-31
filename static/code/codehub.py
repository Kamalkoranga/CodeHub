# CodeHub Cli

import os
import glob
import typer
from rich import print


def add():
    fileName = input('File name: ')
    f = open(f'files/{fileName}', 'w')
    print('Write your program: ')
    while True:
        line = input()
        f.write(line + '\n')
        if line:
            pass
        else:
            break
    print('PROGRAM ADDED!!')


def path(folder_path):
    path = os.getcwd()
    dir_path = f'{path}/{folder_path}'
    count = 0
    for path in os.listdir(dir_path):
        if os.path.isfile(os.path.join(dir_path, path)):
            count += 1
    return count


def view():
    i = 1
    fileName = []
    parent_dir = os.getcwd() + '/files'
    print('All Programs: ')
    for pdf_file in glob.glob(os.path.join(parent_dir, '*.py')):
        file = os.path.basename(pdf_file)
        f_name, f_ext = os.path.splitext(file)
        print(f'{i}: {f_name}')
        i += 1
        fileName.append(file)
    count = path('files')
    if count >= 1:
        which = int(
            input('Enter the no according to the file you want to see: '))
        # print(count)
        for i in range(1, count+1):
            if which == i:
                f = open(f'files/{fileName[i-1]}', 'r')
                print('------------------------------------------------------')
                print(' ')
                print(f.read())
                print('------------------------------------------------------')
    else:
        print('OOPS! No program is added!!')


def run():
    i = 1
    fileName = []
    parent_dir = os.getcwd() + '/files'
    print('All Programs: ')
    for pdf_file in glob.glob(os.path.join(parent_dir, '*.py')):
        file = os.path.basename(pdf_file)
        f_name, f_ext = os.path.splitext(file)
        print(f'  {i}: {f_name}')
        i += 1
        fileName.append(file)
    count = path('files')
    if count >= 1:
        which = int(
            input('Enter the no according to the file you want to run: '))
        # print(count)
        for i in range(1, count+1):
            # print(i)
            if which == i:
                # print(fileName[i-1])
                print('------------------------------------------------------')
                print(' ')
                try:
                    exec(open(f'files/{fileName[i-1]}').read())
                except:
                    print('Error!')
                print(' ')
                print('------------------------------------------------------')
    else:
        print('OOPS! No program is added!!')


def delete():
    i = 1
    fileName = []
    parent_dir = os.getcwd() + '/files'
    print('All Programs: ')
    for pdf_file in glob.glob(os.path.join(parent_dir, '*.py')):
        file = os.path.basename(pdf_file)
        f_name, f_ext = os.path.splitext(file)
        print(f'  {i}: {f_name}')
        i += 1
        fileName.append(file)
    count = path('files')
    if count >= 1:
        which = int(
            input('Enter the no according to the file you want to delete: '))
        for i in range(1, count+1):
            if which == i:
                f = fileName[i-1]
                os.remove(f'files/{f}')
                print('FILE DELETED!')
    else:
        print('OOPS! No program is added!!')


def main():
    i = 0
    while i == 0:
        print(' ')
        h1 = '--------------> CODEHUB <---------------'
        print(h1)
        menu = '''
        Features:- 
            1 - Add program
            2 - View program
            3 - Run program
            4 - Delete program
            5 - Exit
            '''
        print(menu)
        which = int(
            input('Enter the no according to the task you have to do: '))

        if which == 1:
            add()
        elif which == 2:
            view()
        elif which == 3:
            run()
        elif which == 4:
            delete()
        elif which == 5:
            i = 1
        else:
            print('INVALID INPUT!')


# main()
