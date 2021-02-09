class SemanticError(Exception):
	def __init__(self, message="", line=None, col=None):
		self.message = message
		self.line = line
		self.col = col

	def __str__(self) -> str:
		return f"l{self.line}-c{self.col}:: {self.message}"
