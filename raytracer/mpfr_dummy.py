"""
Dummy functions and classes to use when gmpy2 is not present
"""

class precDummy:
    precision = None

def get_context():
    return precDummy()
    
def mpfr(val):
    return float(val)
