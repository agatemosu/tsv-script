import csv
import re
import shlex
import time
from typing import Callable


def replace_variables_wrapper(func: Callable[..., None]) -> Callable[..., None]:
    def wrapper(self: "TSVExecutor", *args: str, **kwargs: str):
        replaced_args = [
            self._replace_variables(arg) if "$" in arg else arg for arg in args
        ]
        func(self, *replaced_args, **kwargs)

    return wrapper


def check_when_stack(func: Callable[..., None]) -> Callable[..., None]:
    def wrapper(self: "TSVExecutor", *args: str, **kwargs: str):
        if all(self.when_stack):
            func(self, *args, **kwargs)

    return wrapper


def parse_command(input: str) -> tuple[str, list[str], dict[str, str]]:
    tokens = shlex.split(input)

    command = tokens[0]
    args = []
    kwargs = {}

    for token in tokens[1:]:
        if "=" in token:
            key, value = token.split("=", 1)
            kwargs[key] = value
        else:
            args.append(token)

    return command, args, kwargs


def red(text: str) -> str:
    return "\033[91m" + text + "\033[0m"


class TSVExecutor:
    def __init__(self, file_path: str, lang: str = "EN"):
        with open(file_path, encoding="utf-8") as f:
            file_content = f.read()

        self.when_stack = []
        self.until_stack = []
        self.stack_trace = []
        self.idx = 1
        self.variables = {}
        self.rows = [
            row
            for row in csv.reader(file_content.splitlines(), delimiter="\t")
            if any(row)
        ]
        self.columns = {
            "id": self.rows[0].index("ID"),
            "code": self.rows[0].index("Code"),
            "name": self.rows[0].index("Name"),
            "text": self.rows[0].index(lang),
        }
        self.id_to_index = {
            row[self.columns["id"]]: index for index, row in enumerate(self.rows)
        }

        print("ID column index:", self.columns["id"])
        print("Code column index:", self.columns["code"])
        print("Name column index:", self.columns["name"])
        print("Text column index:", self.columns["text"])
        print()

        self._execute()

    def _execute(self):
        while self.idx < len(self.rows):
            row = self.rows[self.idx]
            code_value = row[self.columns["code"]]

            # Example of valid functions:
            #   func1 arg1 arg2 arg3
            #   func2 arg1 param3=arg3
            #   func3 $arg1 $arg2
            #
            # Run the function if it's not a comment
            if code_value and not code_value.startswith("#"):
                function_name, args, kwargs = parse_command(code_value)

                function = getattr(self, function_name)
                function(*args, **kwargs)

            if all(self.when_stack):
                if row[self.columns["text"]]:
                    print(row[self.columns["name"]], "says:", row[self.columns["text"]])

                time.sleep(0.5)

            self.idx += 1

        if self.stack_trace:
            raise Exception("Stack trace not ended:", self.stack_trace)

    def _replace_variables(self, argument: str) -> str:
        variables = re.findall(r"\$([A-Za-z_]\w*)", argument)

        for variable in variables:
            argument = argument.replace(f"${variable}", str(self.variables[variable]))

        return argument

    # This is like an "if" in Python
    @replace_variables_wrapper
    def when(self, condition: str):
        self.when_stack.append(eval(condition))
        self.stack_trace.append("when")

    def endwhen(self):
        if self.stack_trace[-1] != "when":
            raise Exception(
                f'Expected "end{self.stack_trace[-1]}" on line {self.idx + 1}'
            )

        self.when_stack.pop()
        self.stack_trace.pop()

    # This is like a "do-while" in C
    @check_when_stack
    def until(self, condition: str):
        self.until_stack.append((condition, self.idx))
        self.stack_trace.append("until")

    @check_when_stack
    def enduntil(self):
        if self.stack_trace[-1] != "until":
            raise Exception(
                f'Expected "end{self.stack_trace[-1]}" on line {self.idx + 1}'
            )

        condition, index = self.until_stack[-1]
        condition = self._replace_variables(condition)

        if eval(condition):
            self.until_stack.pop()
            self.stack_trace.pop()
        else:
            self.idx = index

    @check_when_stack
    def var(self, **kwargs: str):
        name, value = kwargs.popitem()

        if not re.match(r"^[A-Za-z_]\w*$", name):
            raise Exception(
                f"The variable name {red(name)} does not have the correct format."
            )

        if "$" in value:
            value = self._replace_variables(value)

        self.variables[name] = eval(value)

    @check_when_stack
    @replace_variables_wrapper
    def log(self, *args: str):
        print(*args)

    @check_when_stack
    @replace_variables_wrapper
    def chara(self, name: str, action: str = None, position: str = None):
        message = f"{name.title()} appears on the screen"
        if action:
            message += f", visibly {action}"
        if position:
            message += f", positioned on the {position} side"
        print(f"{message}.")

    @check_when_stack
    @replace_variables_wrapper
    def go_to(self, line_id: str):
        self.idx = self.id_to_index[line_id] - 1


if __name__ == "__main__":
    tsv = TSVExecutor("file.tsv", "EN")
