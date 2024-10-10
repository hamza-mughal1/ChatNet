from random import randint


def generator(lenght):
    string = "abcdefghijklmnopqrstuvwxyz12345678901234567890.?"
    lis = [string[randint(0, len(string) - 1)] for _ in range(lenght)]
    final_str = ""
    for i in lis:
        final_str += i

    return final_str
