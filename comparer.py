import os
import subprocess
import hashlib


NEW_SUFFIX = '_rebuild'

def filter_results(lst, flt):
    return list(filter(flt, lst))

def get_failed_processes(lst):
    return filter_results(lst, lambda x: x[1].returncode != 0)

def get_good_processes(lst):
    return filter_results(lst, lambda x: x[1].returncode == 0)


def get_hash(f):
    h = hashlib.sha256()
    with open(f, 'rb') as fp:
        h.update(fp.read())
    return h.hexdigest()

def get_two_hashes(name):
    return (get_hash(f'{name}.trg'), get_hash(f'{name}{NEW_SUFFIX}.trg'))


def main():

    files = os.listdir()
    files = map(lambda x: x.lower(), files)
    files = filter(lambda x: x.endswith('.trg'), files)
    trgs = list(files)
    trgs_no_ext = list(map(lambda x: x.split('.')[0], trgs))

    decompiled = []

    for i, entry in enumerate(trgs_no_ext):
        decompiled.append((entry, subprocess.run(['trg-disasm.exe', '-s', f'{entry}.trg', f'{entry}'], stdout=subprocess.DEVNULL)))
        print(f'Decompiled {entry} {i+1}/{len(trgs_no_ext)}')



    failed = get_failed_processes(decompiled)
    if failed:
        print('There were failures when rebuilding')
        for fail in failed:
            print(f'{fail[0]} has failed decompilation')


    goods = get_good_processes(decompiled)
    rebuild = []
    for i, entry in enumerate(goods):
        good = entry[0]
        rebuild.append((good, subprocess.run(['trg-disasm.exe', '-c', f'{good}', f'{good}{NEW_SUFFIX}.trg'], stdout=subprocess.DEVNULL)))
        print(f'Recompiled {good} {i+1}/{len(goods)}')


    failed = get_failed_processes(rebuild)
    if failed:
        print('There were failures when rebuilding')
        for fail in failed:
            print(f'{fail[0]} has failed compilation')

    
    goods = get_good_processes(rebuild)

    hash_result = []
    for entry in goods:
        good = entry[0]
        hashes = get_two_hashes(good)
        hash_result.append((good, hashes[0]==hashes[1]))


    hash_result.sort(key=lambda x: x[1], reverse=True)

    for entry in hash_result:
        print(f'{entry[0]} match result: {entry[1]}')



if __name__ == '__main__':
    main()

