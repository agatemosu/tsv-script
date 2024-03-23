import csv
import re
import time


def parse(tsvfile: str) -> list[list[str]]:
    reader = csv.reader(tsvfile.splitlines(), delimiter="\t")

    tokenized_rows = []
    for tokenized_row in reader:
        if any(tokenized_row):
            tokenized_rows.append(tokenized_row)

    return tokenized_rows


def replace_variables_wrapper(func):
    def wrapper(self, *args):
        replaced_args = []
        for arg in args:
            if "$" in arg:
                arg = self._replace_variables(arg)
            replaced_args.append(arg)

        return func(self, *replaced_args)

    return wrapper


def check_when_stack(func):
    def wrapper(self, *args):
        if all(self.when_stack):
            return func(self, *args)

    return wrapper


def red(text: str) -> str:
    return "\033[91m" + text + "\033[0m"


class TSVExecuter:
    def __init__(self, tokenized_rows: list[list[str]], id_column: int):
        self.when_stack = []
        self.until_stack = []
        self.idx = 1
        self.id_to_index = {}
        self.variables = {}

        for index, tokenized_row in enumerate(tokenized_rows):
            self.id_to_index[tokenized_row[id_column]] = index

    def _replace_variables(self, argument: str) -> str:
        variables = re.findall(r"\$([A-Za-z_]\w*)", argument)

        for variable in variables:
            argument = argument.replace(f"${variable}", str(self.variables[variable]))

        return argument

    # This is like an "if" in Python
    @replace_variables_wrapper
    def when(self, condition: str):
        self.when_stack.append(eval(condition))

    def endwhen(self):
        self.when_stack.pop()

    # This is like a "do-while" in C
    @check_when_stack
    def until(self, condition: str):
        self.until_stack.append((condition, self.idx))

    @check_when_stack
    def enduntil(self):
        condition, index = self.until_stack[-1]
        condition = self._replace_variables(condition)

        if eval(condition):
            self.until_stack.pop()
        else:
            self.idx = index

    @check_when_stack
    def var(self, name: str, value: str):
        if "$" in name:
            raise Exception(f"Do not put {red('$')}var on the name.")

        if "$" in value:
            value = self._replace_variables(value)

        self.variables[name] = eval(value)

    @check_when_stack
    @replace_variables_wrapper
    def log(self, *args):
        for arg in args:
            print(arg, end=" ")

        print()

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
    file_path = "file.tsv"

    with open("file.tsv", encoding="utf-8") as f:
        file_content = f.read()

    rows = parse(file_content)

    id_col = rows[0].index("ID")
    code_col = rows[0].index("Code")
    name_col = rows[0].index("Name")
    text_col = rows[0].index("EN")

    print("ID column index:", id_col)
    print("Code column index:", code_col)
    print("Name column index:", name_col)
    print()

    tsv = TSVExecuter(rows, id_col)

    while tsv.idx < len(rows):
        row = rows[tsv.idx]
        code_value = row[code_col]

        # Example of a function:
        #   func1:arg1:arg2:arg3
        #   func2:arg1::arg3
        #   func3:arg1:$var
        #
        function_and_args = code_value.split(":")
        function_name = function_and_args[0].strip()
        arguments = function_and_args[1:]

        # Check if function exists in tsv object
        if function_name and not function_name.startswith("#"):
            function = getattr(tsv, function_name)
            function(*arguments)

        if all(tsv.when_stack):
            if row[text_col]:
                print(row[name_col], "says:", row[text_col])

            time.sleep(0.5)

        tsv.idx += 1
