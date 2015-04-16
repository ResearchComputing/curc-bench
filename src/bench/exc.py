class BenchException (Exception): pass

class BenchError (BenchException): pass

class ParseError (BenchError): pass

class SlurmError (BenchError): pass
