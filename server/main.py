import hug

@hug.get()
def say_hello():
    return "Hello World from hug"

def main():
    say_hello.interface.cli()

if __name__ == "__main__":
    main()