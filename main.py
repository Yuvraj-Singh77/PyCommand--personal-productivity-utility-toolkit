
import os
from abc import ABC, abstractmethod



# CUSTOM EXCEPTION

class CommandError(Exception):
    pass


# ABSTRACT BASE CLASS


class BaseCommand(ABC):

    @abstractmethod
    def execute(self, args, terminal):
        pass

    @abstractmethod
    def description(self):
        pass



# 1. SMART WORKFLOW AUTOMATION

class CollegeSetupCommand(BaseCommand):

    def execute(self, args, terminal):

        if len(args) > 1:
            raise CommandError(
                "Usage: college_setup [folder_name]"
            )

        folder_name = args[0] if args else "CollegeWorkspace"

        main_folder = os.path.join(
            terminal.current_dir, folder_name
        )

        folders = [
            "Assignments",
            "Notes",
            "Projects",
            "Practicals",
            "Resources"
        ]

        try:

            os.makedirs(main_folder, exist_ok=True)

            print("\nCreating College Workspace...\n")

            for folder in folders:

                path = os.path.join(main_folder, folder)

                if not os.path.exists(path):
                    os.makedirs(path)
                    print("[CREATED]", folder)
                else:
                    print("[EXISTS] ", folder)

            print("\nCollege workspace ready!")

            print("Location:", main_folder)

        except OSError as error:
            raise CommandError(
                "Unable to create workspace: " + str(error)
            )

    def description(self):
        return "college_setup [name] - Create college workspace"


# 2. SMART DUPLICATE DETECTOR

class DuplicateScanCommand(BaseCommand):

    def compare_files(self, file1, file2):

        try:

            if os.path.getsize(file1) != os.path.getsize(file2):
                return False

            with open(file1, "rb") as f1:
                with open(file2, "rb") as f2:

                    while True:

                        data1 = f1.read(4096)
                        data2 = f2.read(4096)

                        if data1 != data2:
                            return False

                        if not data1:
                            return True

        except OSError as error:

            print("Unable to compare files:", error)
            return False

    def execute(self, args, terminal):

        if len(args) > 1:
            raise CommandError(
                "Usage: duplicate_scan [directory]"
            )

        folder = (
            terminal.get_path(args[0])
            if args
            else terminal.current_dir
        )

        if not os.path.isdir(folder):
            raise CommandError("Invalid directory!")

        print("\nScanning for duplicate files...")
        print("Location:", folder)

        # Groups files according to their sizes
        size_groups = {}

        for root, dirs, files in os.walk(folder):

            for filename in files:

                path = os.path.join(root, filename)

                try:

                    size = os.path.getsize(path)

                    if size not in size_groups:
                        size_groups[size] = []

                    size_groups[size].append(path)

                except OSError:
                    print("Skipping inaccessible file:", path)

        duplicate_groups = []

        # Compare files having the same size

        for size, paths in size_groups.items():

            if len(paths) < 2:
                continue

            groups = []

            for path in paths:

                matched = False

                for group in groups:

                    if self.compare_files(path, group[0]):
                        group.append(path)
                        matched = True
                        break

                if not matched:
                    groups.append([path])

            for group in groups:

                if len(group) > 1:
                    duplicate_groups.append(group)

        # Display results

        if not duplicate_groups:

            print("\nNo duplicate files found!")

        else:

            print("\nDuplicate files found!\n")

            for index, group in enumerate(
                duplicate_groups, 1
            ):

                print("Duplicate Group", index)

                for path in group:

                    print(
                        " -",
                        os.path.relpath(path, folder)
                    )

                print()

            print(
                "Total duplicate groups:",
                len(duplicate_groups)
            )

        print("\nScan completed.")

    def description(self):
        return "duplicate_scan [directory] - Find duplicate files"


# 3. SECURE PASSWORD GENERATOR

class PasswordCommand(BaseCommand):

    def secure_index(self, limit):

        # Uses operating-system random bytes
        # Rejection sampling avoids modulo bias

        maximum = 256 - (256 % limit)

        while True:

            value = os.urandom(1)[0]

            if value < maximum:
                return value % limit

    def secure_choice(self, characters):

        index = self.secure_index(len(characters))

        return characters[index]

    def execute(self, args, terminal):

        if len(args) != 1:
            raise CommandError(
                "Usage: generate_password <length>"
            )

        try:
            length = int(args[0])

        except ValueError:
            raise CommandError("Length must be a number!")

        if length < 8 or length > 128:
            raise CommandError(
                "Password length must be between 8 and 128."
            )

        uppercase = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
        lowercase = "abcdefghijklmnopqrstuvwxyz"
        numbers = "0123456789"
        symbols = "!@#$%^&*()-_+="

        all_characters = (
            uppercase + lowercase + numbers + symbols
        )

        # Ensure at least one character from each category
        password = [
            self.secure_choice(uppercase),
            self.secure_choice(lowercase),
            self.secure_choice(numbers),
            self.secure_choice(symbols)
        ]

        # Fill remaining positions
        for i in range(length - 4):

            password.append(
                self.secure_choice(all_characters)
            )

        # Securely shuffle the password
        for i in range(len(password) - 1, 0, -1):

            j = self.secure_index(i + 1)

            password[i], password[j] = (
                password[j], password[i]
            )

        final_password = "".join(password)

        print("\nGenerated Password:")
        print(final_password)

        print("\nPassword length:", length)

        print("Contains uppercase, lowercase, numbers and symbols.")

    def description(self):
        return "generate_password <length> - Generate a strong password"



# ECHO COMMAND

class EchoCommand(BaseCommand):

    def execute(self, args, terminal):
        print(" ".join(args))

    def description(self):
        return "echo <message> - Display a message"


# DIRECTORY COMMANDS

class LsCommand(BaseCommand):

    def execute(self, args, terminal):

        if len(args) > 1:
            raise CommandError("Usage: ls [directory]")

        path = (
            terminal.get_path(args[0])
            if args
            else terminal.current_dir
        )

        if not os.path.isdir(path):
            raise CommandError("Directory not found!")

        items = os.listdir(path)

        for item in sorted(items):

            full_path = os.path.join(path, item)

            if os.path.isdir(full_path):
                print("[DIR] ", item)
            else:
                print("[FILE]", item)

        if not items:
            print("Directory is empty.")

    def description(self):
        return "ls [directory] - List directory contents"


class CdCommand(BaseCommand):

    def execute(self, args, terminal):

        if len(args) != 1:
            raise CommandError("Usage: cd <directory>")

        path = terminal.get_path(args[0])

        if not os.path.isdir(path):
            raise CommandError("Directory does not exist!")

        terminal.current_dir = os.path.abspath(path)

        print("Directory changed successfully.")

    def description(self):
        return "cd <directory> - Change directory"


class PwdCommand(BaseCommand):

    def execute(self, args, terminal):
        print(terminal.current_dir)

    def description(self):
        return "pwd - Show current directory"


# HISTORY COMMAND

class HistoryCommand(BaseCommand):

    def execute(self, args, terminal):

        if not terminal.history:
            print("No history available.")
            return

        for index, command in enumerate(
            terminal.history, 1
        ):
            print(index, command)

    def description(self):
        return "history - Show command history"


# HELP COMMAND

class HelpCommand(BaseCommand):

    def execute(self, args, terminal):

        print("\nAVAILABLE COMMANDS")
        print("-" * 60)

        for command in terminal.commands.values():
            print(command.description())

        print("-" * 60)

    def description(self):
        return "help - Show available commands"


# CLEAR COMMAND

class ClearCommand(BaseCommand):

    def execute(self, args, terminal):
        os.system("cls" if os.name == "nt" else "clear")

    def description(self):
        return "clear - Clear screen"


# EXIT COMMAND

class ExitCommand(BaseCommand):

    def execute(self, args, terminal):

        print("Thank you for using PyCommand!")

        terminal.running = False

    def description(self):
        return "exit - Close application"


# MAIN TERMINAL CLASS

class Terminal:

    def __init__(self):

        self.current_dir = os.getcwd()
        self.running = True

        self.history_file = os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            "history.txt"
        )

        self.history = []

        self.commands = {}

        self.load_history()
        self.register_commands()

    # PATH HANDLING

    def get_path(self, name):

        if os.path.isabs(name):
            return os.path.abspath(name)

        return os.path.abspath(
            os.path.join(self.current_dir, name)
        )

    # COMMAND REGISTRATION

    def register(self, name, command):

        self.commands[name] = command

    def register_commands(self):

        self.register(
            "college_setup", CollegeSetupCommand()
        )

        self.register(
            "duplicate_scan", DuplicateScanCommand()
        )

        self.register(
            "generate_password", PasswordCommand()
        )

        self.register("echo", EchoCommand())
        self.register("ls", LsCommand())
        self.register("cd", CdCommand())
        self.register("pwd", PwdCommand())
        self.register("history", HistoryCommand())
        self.register("help", HelpCommand())
        self.register("clear", ClearCommand())
        self.register("exit", ExitCommand())

    # FILE HANDLING

    def load_history(self):

        try:

            if os.path.exists(self.history_file):

                with open(self.history_file, "r") as file:

                    self.history = [
                        line.rstrip("\n")
                        for line in file
                        if line.strip()
                    ]

        except (OSError, UnicodeError) as error:

            print("History loading error:", error)

    def save_history(self, command):

        try:

            with open(self.history_file, "a") as file:

                file.write(command + "\n")

            self.history.append(command)

        except OSError as error:

            print("History saving error:", error)

    # COMMAND EXECUTION

    def execute_command(self, user_input):

        try:

            parts = user_input.split()

            if not parts:
                return

            command_name = parts[0].lower()
            args = parts[1:]

            if command_name not in self.commands:

                raise CommandError(
                    "Unknown command! Type help."
                )

            self.commands[command_name].execute(
                args, self
            )

        except CommandError as error:

            print("Error:", error)

        except ValueError:

            print("Invalid input!")

        except PermissionError:

            print("Permission denied!")

        except FileNotFoundError:

            print("File or folder not found!")

        except OSError as error:

            print("System error:", error)

        except Exception as error:

            print("Unexpected error:", error)

    # START TERMINAL

    def start(self):

        print("=" * 55)
        print("          WELCOME TO PYCOMMAND")
        print("=" * 55)

        print("Your Personal Productivity Toolkit")
        print("Type 'help' to see available commands.")
        print("Type 'exit' to close.\n")

        while self.running:

            try:

                user_input = input(
                    "PyCommand> "
                ).strip()

                if not user_input:
                    continue

                self.save_history(user_input)

                self.execute_command(user_input)

            except KeyboardInterrupt:

                print("\nUse exit to close the application.")

            except EOFError:

                print("\nClosing PyCommand...")
                self.running = False


# PROGRAM EXECUTION

if __name__ == "__main__":

    try:

        app = Terminal()
        app.start()

    except Exception as error:

        print("Startup error:", error)
