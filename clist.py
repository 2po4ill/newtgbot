import shutil


def numbermaker(numbers):
    number = ''
    for i in numbers:
        if i not in '()+':
            if i == numbers[0] and i == '8':
                number += '7'
            else:
                number += i
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
