class ParserError(Exception):
    def __init__(self, line_no: int, message: str) -> None:
        super().__init__(f"Line {line_no}: {message}")

