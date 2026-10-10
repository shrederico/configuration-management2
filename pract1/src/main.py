import getpass
import socket


def parse_command(user_input):
    parts = user_input.split()

    command = parts[0]
    arguments = parts[1:]

    return command, arguments


def run_command(command, arguments):
    if command == "ls":
        print("Команда: ls")
        print("Аргументы:", arguments)

    elif command == "cd":
        print("Команда: cd")
        print("Аргументы:", arguments)

    else:
        print(f"Ошибка: неизвестная команда '{command}'")


def main():
    username = getpass.getuser()
    hostname = socket.gethostname()

    while True:
        prompt = f"{username}@{hostname}:~$ "
        user_input = input(prompt)

        if not user_input.strip():
            continue

        command, arguments = parse_command(user_input)

        if command == "exit":
            break

        run_command(command, arguments)


main()