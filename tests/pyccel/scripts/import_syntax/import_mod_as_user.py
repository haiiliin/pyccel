# pylint: disable=missing-function-docstring, missing-module-docstring
from pyccel.decorators import types
import user_mod as u

@types('double','double','double')
def fun(xi1, xi2, xi3):
    return u.user_func(xi1, xi2, xi3)

if __name__ == '__main__':
    print(fun(1.0,2.0,3.0))
