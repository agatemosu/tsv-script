import csv
import time


class BaseTSVParser:
    def parse(self, tsvfile: str) -> list[list[str]]:
        tokenized_rows = []
        reader = csv.reader(tsvfile.splitlines(), delimiter="\t")
        for row in reader:
            if any(row):
                tokenized_rows.append(row)
        return tokenized_rows


class CustomTSVParser(BaseTSVParser):
    def __init__(self):
        self.when_stack = []
        self.until_stack = []
        self.idx = 1
        self.id_to_index = {}

    def enable_go_to(self, tokenized_rows: list[list[str]]):
        for index, row in enumerate(tokenized_rows):
            self.id_to_index[row[id_column]] = index

    # This is like an "if" in Python
    def when(self, condition: str):
        self.when_stack.append(eval(condition))

    def endwhen(self):
        if self.when_stack:
            self.when_stack.pop()

    # This is like a "do-while" in C
    def until(self, condition: str):
        if not all(self.when_stack):
            return

        self.until_stack.append((condition, self.idx))

    def enduntil(self):
        if not all(self.when_stack):
            return

        condition, index = self.until_stack[-1]
        if eval(condition):
            self.until_stack.pop()
        else:
            self.idx = index

    def log(self, content: str = ""):
        if not all(self.when_stack):
            return

        print(content)

    def chara(self, name: str, action: str = "", position: str = ""):
        if not all(self.when_stack):
            return

        message = f"{name.title()} appears on the screen"
        if action:
            message += f", visibly {action}"
        if position:
            message += f", positioned on the {position} side"
        print(message)

    def go_to(self, line_id: str):
        if not all(self.when_stack):
            return

        self.idx = self.id_to_index[line_id] - 1


if __name__ == "__main__":
    file_path = "file.tsv"

    tsv = CustomTSVParser()

    with open("file.tsv", encoding="utf-8") as f:
        content = f.read()

    rows = tsv.parse(content)

    id_column = rows[0].index("ID")
    code_column = rows[0].index("Code")
    name_column = rows[0].index("Name")
    lang_column = rows[0].index("EN")

    tsv.enable_go_to(rows)

    print("ID column index:", id_column)
    print("Code column index:", code_column)
    print("Name column index:", name_column)
    print()

    while tsv.idx < len(rows):
        code_value = rows[tsv.idx][code_column]

        # Example of a function:
        #   func:arg1:arg2:arg3
        #
        function_and_args = code_value.split(":")
        function_name = function_and_args[0].strip()
        arguments = function_and_args[1:]

        # Check if function exists in tsv object
        if hasattr(tsv, function_name):
            function = getattr(tsv, function_name)
            function(*arguments)

        if all(tsv.when_stack):
            if rows[tsv.idx][lang_column]:
                print(
                    rows[tsv.idx][name_column],
                    "says:",
                    rows[tsv.idx][lang_column],
                )

            time.sleep(0.5)

        tsv.idx += 1
