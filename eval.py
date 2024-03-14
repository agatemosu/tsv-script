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
        return message


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

    for tokenized_row in tokenized_rows:
        code_value = tokenized_row[code_column]

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

        if tsv.condition_met and tokenized_row[lang_column]:
            print(tokenized_row[lang_column])
            time.sleep(1)
