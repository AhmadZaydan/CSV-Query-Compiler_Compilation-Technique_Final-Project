# main.py
import sys
from parser import parse
from executor import execute_query

def run_interactive():
    print("CSV Query Compiler (Interactive Mode)")
    print("Type your query below. End with an empty line.\n")

    lines = []
    while True:
        line = input()
        if line.strip() == "":
            break
        lines.append(line)

    query_text = "\n".join(lines)

    try:
        query = parse(query_text)
        df = execute_query(query)
        print("\nResult:")
        print(df)
    except Exception as e:
        print("\nError during execution:")
        print(e)


def run_from_file(filename):
    try:
        with open(filename, "r", encoding="utf-8") as f:
            text = f.read()
    except FileNotFoundError:
        print(f"Error: file '{filename}' not found.")
        return

    try:
        query = parse(text)
        df = execute_query(query)
        print(df)
    except Exception as e:
        print("Execution error:")
        print(e)


def main():
    # If a file argument is supplied -> run using that file
    if len(sys.argv) == 2:
        run_from_file(sys.argv[1])
    else:
        # No arguments -> enter interactive mode
        run_interactive()


if __name__ == "__main__":
    main()
