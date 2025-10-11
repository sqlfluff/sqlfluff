"""For autogenerating rust dialects."""


def generate_use():
    """Generates the `use` statements."""
    print("#[allow(clippy::needless_raw_string_hashes)]")
    print("pub mod matcher;")
    print("// pub mod parser;")


if __name__ == "__main__":
    print("/* This is a generated file! */")
    print()
    generate_use()
