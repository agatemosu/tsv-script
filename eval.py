import csv
import time


class BaseTSVParser:
    def parse(self, tsvfile: str) -> list[list[str]]:
        tokenized_rows = []
        reader = csv.reader(tsvfile.splitlines(), delimiter="\t")
        for row in reader:
            if row:
                tokenized_rows.append(row)
        return tokenized_rows


class CustomTSVParser(BaseTSVParser):
    def __init__(self):
        self.condition_met = True
        self.idx = 0

    # This is like a "if" in Python
    def when(self, condition: str):
        self.condition_met = eval(condition)

    def endwhen(self):
        self.condition_met = True

    def chara(self, name: str, action: str = "", position: str = ""):
        # TODO: This will show the character on screen
        if not self.condition_met:
            return

        message = f"{name.title()} appears on the screen"
        if action:
            message += f", visibly {action}"
        if position:
            message += f", positioned on the {position} side"
        print(message)

    def go_to(self, line_id: str):
        if not self.condition_met:
            return

        for index, sublist in enumerate(tokenized_rows):
            if sublist[id_column] == line_id:
                self.idx = index - 1
                break


if __name__ == "__main__":
    file_path = "file.tsv"

    tsv = CustomTSVParser()

    with open("file.tsv", encoding="utf-8") as f:
        content = f.read()

    tokenized_rows = tsv.parse(content)

    id_column = tokenized_rows[0].index("ID")
    code_column = tokenized_rows[0].index("Code")
    lang_column = tokenized_rows[0].index("EN")

    print("ID column index:", id_column)
    print("Code column index:", code_column)
    print()

    while tsv.idx < len(tokenized_rows):
        code_value = tokenized_rows[tsv.idx][code_column]

        # Example of a function:
        #   func:arg1:arg2:arg3
        #
        function_and_args = code_value.split(":")
        function_name = function_and_args[0].strip()
        arguments = function_and_args[1:]

        # Check if function exists in tsv object
        if hasattr(tsv, function_name):
            function = getattr(tsv, function_name)
            result = function(*arguments)

        if tsv.condition_met and tokenized_rows[tsv.idx][lang_column]:
            print(tokenized_rows[tsv.idx][lang_column])
            time.sleep(1)

        tsv.idx += 1