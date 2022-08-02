import shutil
import os


def numbermaker(numbers):
    number = ''
    for j in range(len(numbers)):
        if numbers[j] not in '()+':
            if numbers[j] == '8' and str(j) == '0':
                number += '7'
            else:
                number += numbers[j]
    return number


def updatebd():
    crntfile = r'fulllist.txt'
    shutil.copy2(crntfile, 'fulllistcopy.txt')
    file = r'fulllistcopy.txt'
    text = open(file, 'r', encoding="utf8")
    line = text.readline()
    newfile = ''
    while line != '':
        if len(line.split()) > 3:
            if line.split()[3][0] in '+789':
                if len(line.split()) == 4:
                    number = numbermaker(line.split()[3])
                    line = line.split()[0] + ' ' + line.split()[1] + ' ' + line.split()[2] + ' ' + number
                    newfile += line + '\n'
                else:
                    numberlist = ''
                    for i in line.split()[3:]:
                        numberlist += i
                    number = numbermaker(numberlist)
                    line = line.split()[0] + ' ' + line.split()[1] + ' ' + line.split()[2] + ' ' + number
                    newfile += line + '\n'
        line = text.readline()
    text.close()
    rite = open(file, 'w', encoding="utf8")
    rite.write(newfile)
    rite.close()


def closerequest():
    crntfile = r'requests.txt'
    shutil.copy2(crntfile, 'requestscopy.txt')
    file = r'requestscopy.txt'
    text = open(file, 'r', encoding="utf8")
    line = text.readline()
    text2 = open(crntfile, 'w', encoding="utf8")
    text2.write('')
    text2.close()

    text2 = open(crntfile, 'a', encoding="utf8")
    while line != '':
        previousline = line
        line = text.readline()
        if line == '':
            text2.write(str(previousline.split()[:-1]) + ' closed \n')
        else:
            text2.write(previousline)
    collect = previousline.split()[:-1].copy()
    text2.close()
    text.close()
    os.remove(file)
    return collect[-2:][0]