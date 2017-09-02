# coding: utf-8

import os
from pyccel.printers import fcode
from pyccel.parser  import PyccelParser
from pyccel.syntax import ( \
                           # statements
                           DeclarationStmt, \
                           ConstructorStmt, \
                           DelStmt, \
                           PassStmt, \
                           AssignStmt, MultiAssignStmt, \
                           IfStmt, ForStmt,WhileStmt, FunctionDefStmt, \
                           ImportFromStmt, \
                           CommentStmt, \
                           # Multi-threading
                           ThreadStmt, \
                           # python standard library statements
                           PythonPrintStmt, \
                           # numpy statments
                           NumpyZerosStmt, NumpyZerosLikeStmt, \
                           NumpyOnesStmt, NumpyLinspaceStmt,NumpyArrayStmt \
                           )

from pyccel.openmp.syntax import OpenmpStmt


__all__ = ["PyccelCodegen"]

# ...
def clean(filename):
    name = filename.split('.py')[0]
    for ext in ["f90", "pyccel"]:
        f_name = name + "." + ext
        cmd = "rm -f " + f_name
        os.system(cmd)
# ...

# ...
def make_tmp_file(filename):
    name = filename.split('.py')[0]
    return name + ".pyccel"
# ...

# ...
def preprocess(filename, filename_out):
    f = open(filename)
    lines = f.readlines()
    f.close()

    # to be sure that we dedent at the end
    lines += "\n"

    lines_new = ""

    def delta(line):
        l = line.lstrip(' ')
        n = len(line) - len(l)
        return n

    tab   = 4
    depth = 0
    for i,line in enumerate(lines):
        n = delta(line)

        if n == depth * tab + tab:
            depth += 1
            lines_new += "indent" + "\n"
            lines_new += line
        else:

            d = n // tab
            if (d > 0) or (n==0):
                old = delta(lines[i-1])
                m = (old - n) // tab
                depth -= m
                for j in range(0, m):
                    lines_new += "dedent" + "\n"

            lines_new += line
    f = open(filename_out, "w")
    for line in lines_new:
        f.write(line)
    f.close()
# ...

# ...
def execute_file(binary):

    cmd = binary
    if not ('/' in binary):
        cmd = "./" + binary
    os.system(cmd)
# ...

class Codegen(object):
    """Abstract class for code generation."""
    def __init__(self, \
                 filename=None, \
                 name=None, \
                 imports=None, \
                 preludes=None, \
                 body=None, \
                 routines=None, \
                 modules=None, \
                 is_module=False):
        """Constructor for the Codegen class.

        body: list
            list of statements.
        """
        # ... TODO improve once TextX will handle indentation
        clean(filename)

        filename_tmp = make_tmp_file(filename)
        preprocess(filename, filename_tmp)
        filename = filename_tmp
        # ...

        if name is None:
            name = "main"
        if body is None:
            body = []
        if routines is None:
            routines = []
        if modules is None:
            modules = []

        self._filename     = filename
        self._filename_out = None
        self._language     = None
        self._imports      = imports
        self._name         = name
        self._is_module    = is_module
        self._body         = body
        self._preludes     = preludes
        self._routines     = routines
        self._modules      = modules

    @property
    def filename(self):
        """Returns the name of the file to convert."""
        return self._filename

    @property
    def filename_out(self):
        """Returns the name of the output file."""
        return self._filename_out

    @property
    def code(self):
        """Returns the generated code"""
        return self._code

    @property
    def language(self):
        """Returns the used language"""
        return self._language

    @property
    def name(self):
        """Returns the name of the Codegen class"""
        return self._name

    @property
    def imports(self):
        """Returns the imports of the Codegen class"""
        return self._imports

    @property
    def preludes(self):
        """Returns the preludes of the Codegen class"""
        return self._preludes

    @property
    def body(self):
        """Returns the body of the Codegen class"""
        return self._body

    @property
    def routines(self):
        """Returns the routines of the Codegen class"""
        return self._routines

    @property
    def modules(self):
        """Returns the modules of the Codegen class"""
        return self._modules

    @property
    def is_module(self):
        """Returns True if we are treating a module."""
        return self._is_module

    def as_module(self):
        """Generate code as a module. Every extension must implement this method."""
        pass

    def as_program(self):
        """Generate code as a program. Every extension must implement this method."""
        pass

    def doprint(self, language, accelerator=None):
        """Generate code for a given language.

        language: str
            target language. Possible values {"fortran"}
        """
        # ...
        filename = self.filename
        imports  = ""
        preludes = ""
        body     = ""
        routines = ""
        modules  = []
        # ...

        # ...
        if language.lower() == "fortran":
            printer = fcode
        else:
            raise ValueError("Only fortran is available")
        # ...

        # ... TODO improve. mv somewhere else
        if not (accelerator is None):
            if accelerator == "openmp":
                imports += "use omp_lib "
            else:
                raise ValueError("Only openmp is available")
        # ...

        # ...
        pyccel = PyccelParser()
        ast    = pyccel.parse_from_file(filename)
        # ...

        # ...
        for stmt in ast.statements:
            if isinstance(stmt, CommentStmt):
                body += printer(stmt.expr) + "\n"
#            elif isinstance(stmt, AnnotatedStmt):
#                body += printer(stmt.expr) + "\n"
            elif isinstance(stmt, ImportFromStmt):
                imports += printer(stmt.expr) + "\n"
                modules += stmt.dotted_name.names
            elif isinstance(stmt, DeclarationStmt):
                decs = stmt.expr
            elif isinstance(stmt, NumpyZerosStmt):
                body += printer(stmt.expr) + "\n"
            elif isinstance(stmt, NumpyZerosLikeStmt):
                body += printer(stmt.expr) + "\n"
            elif isinstance(stmt, NumpyOnesStmt):
                body += printer(stmt.expr) + "\n"
            elif isinstance(stmt, NumpyLinspaceStmt):
                body += printer(stmt.expr) + "\n"
            elif isinstance(stmt, NumpyArrayStmt):
                body += printer(stmt.expr) + "\n"
            elif isinstance(stmt, AssignStmt):
                body += printer(stmt.expr) + "\n"
            elif isinstance(stmt, MultiAssignStmt):
                body += printer(stmt.expr) + "\n"
            elif isinstance(stmt, ForStmt):
                body += printer(stmt.expr) + "\n"
            elif isinstance(stmt,WhileStmt):
                body += printer(stmt.expr) + "\n"
            elif isinstance(stmt, IfStmt):
                body += printer(stmt.expr) + "\n"
            elif isinstance(stmt, FunctionDefStmt):
                sep = separator()
                routines += sep + printer(stmt.expr) + "\n" \
                          + sep + '\n'
            elif isinstance(stmt, PythonPrintStmt):
                body += printer(stmt.expr) + "\n"
            elif isinstance(stmt, ConstructorStmt):
                # this statement does not generate any code
                stmt.expr
            elif isinstance(stmt, OpenmpStmt):
                body += printer(stmt.expr) + "\n"
            elif isinstance(stmt, ThreadStmt):
                body += printer(stmt.expr) + "\n"
            else:
                if True:
                    print "> uncovered statement of type : ", type(stmt)
                else:

                    raise Exception('Statement not yet handled.')
        # ...

        # ...
        for key, dec in ast.declarations.items():
            preludes += printer(dec) + "\n"
        # ...

        # ...
        if not self.is_module:
            is_module = True
            for stmt in ast.statements:
                if not(isinstance(stmt, (CommentStmt, ConstructorStmt, FunctionDefStmt))):
                    is_module = False
                    break
        else:
            is_module = True
        # ...

        # ...
        self._ast       = ast
        self._imports   = imports
        self._preludes  = preludes
        self._body      = body
        self._routines  = routines
        self._modules   = modules
        self._is_module = is_module
        self._language  = language
        # ...

        # ...
        if is_module:
#            name = filename.split(".pyccel")[0]
#            name = name.split('/')[-1]
            code = self.as_module()
        else:
            code = self.as_program()
        # ...

        self._code         = code
        self._filename_out = write_to_file(code, filename, language)


        return code


class FCodegen(Codegen):
    """Code generation for Fortran."""
    def __init__(self, *args, **kwargs):
        """
        """
        super(FCodegen, self).__init__(*args, **kwargs)

    def as_module(self):
        """Generate code as a module."""
        name     = self.name
        imports  = self.imports
        preludes = self.preludes
        body     = self.body
        routines = self.routines
        modules  = self.modules

        code  = "module " + str(name)     + "\n"
        code += imports                   + "\n"
        code += "implicit none"           + "\n"
        code += preludes                  + "\n"

        if len(routines) > 0:
            code += "contains"            + "\n"
            code += routines              + "\n"
        code += "end module " + str(name) + "\n"

        return code

    def as_program(self):
        """Generate code as a program."""
        name     = self.name
        imports  = self.imports
        preludes = self.preludes
        body     = self.body
        routines = self.routines
        modules  = self.modules

        code  = "program " + str(name)    + "\n"
        code += imports                   + "\n"
        code += "implicit none"           + "\n"
        code += preludes                  + "\n"

        if len(body) > 0:
            code += body                  + "\n"
        if len(routines) > 0:
            code += "contains"            + "\n"
            code += routines              + "\n"
        code += "end"                     + "\n"

        return code

class PyccelCodegen(Codegen):
    """Code generation for the Pyccel Grammar"""
    def __init__(self, *args, **kwargs):
        """
        """
        super(PyccelCodegen, self).__init__(*args, **kwargs)

def get_extension(language):
    if language == "fortran":
        return "f90"
    else:
        raise ValueError("Only fortran is available")


# ...
def separator(n=40):
    txt = "."*n
    comment = '!'
    return '{0} {1}\n'.format(comment, txt)
# ...


# ...
def write_to_file(code, filename, language):
    if not(language == "fortran"):
        raise ValueError("Only fortran is available")

    ext = get_extension(language)
    f90_file = filename.split(".py")[0] + "." + ext
    f = open(f90_file, "w")
    for line in code:
        f.write(line)
    f.close()


    return f90_file
# ...

class Compiler(object):
    """Code compiler for the Pyccel Grammar"""
    def __init__(self, codegen, compiler, \
                 flags=None, accelerator=None, \
                 binary=None, debug=False, inline=False):
        """
        """
        self._codegen     = codegen
        self._compiler    = compiler
        self._binary      = binary
        self._debug       = debug
        self._inline      = inline
        self._accelerator = accelerator

        if flags:
            self._flags = flags
        else:
            self._flags = self.construct_flags()

    @property
    def codegen(self):
        """Returns the used codegen"""
        return self._codegen

    @property
    def compiler(self):
        """Returns the used compiler"""
        return self._compiler

    @property
    def flags(self):
        """Returns the used flags"""
        return self._flags

    @property
    def binary(self):
        """Returns the used binary"""
        return self._binary

    @property
    def debug(self):
        """Returns True if in debug mode"""
        return self._debug

    @property
    def inline(self):
        """Returns True if in inline mode"""
        return self._inline

    @property
    def accelerator(self):
        """Returns the used accelerator"""
        return self._accelerator

    def construct_flags(self):
        compiler    = self.compiler
        debug       = self.debug
        inline      = self.inline
        accelerator = self.accelerator

        flags = " -O2 "
        if compiler == "gfortran":
            if debug:
                flags += " -fbounds-check "

            if not (accelerator is None):
                if accelerator == "openmp":
                    flags += " -fopenmp "
                else:
                    raise ValueError("Only openmp is available")
        else:
            raise ValueError("Only gfortran is available")

        return flags

    def compile(self, verbose=False):
        compiler  = self.compiler
        flags     = self.flags
        inline    = self.inline
        filename  = self.codegen.filename_out
        is_module = self.codegen.is_module
        modules   = self.codegen.modules

        binary = ""
        if self.binary is None:
            if not is_module:
                binary = filename.split('.')[0]
        else:
            binary = self.binary

        o_code = ''
        if not inline:
            if not is_module:
                o_code = "-o"
            else:
                flags += ' -c '
        else:
            o_code = '-m'
            flags  = '--quiet -c'
            binary = 'external'
            # TODO improve
            compiler = 'f2py'

        m_code = ' '.join('{}.o '.format(m) for m in modules)

        cmd = '{0} {1} {2} {3} {4} {5}'.format( \
            compiler, flags, m_code, filename, o_code, binary)

        if verbose:
            print cmd

        os.system(cmd)

        self._binary = binary
# ...

# ...
def build_file(filename, language, compiler, \
               execute=False, accelerator=None, \
               debug=False, verbose=False, show=False, \
               inline=False, name="main"):
    """User friendly interface for code generation."""
    # ...
    from pyccel.patterns.utilities import find_imports

    imports = find_imports(filename=filename)
    ms = []
    for module, names in imports.items():
        codegen_m = FCodegen(filename=module+".py", name=module, is_module=True)
        codegen_m.doprint(language=language, accelerator=accelerator)
        ms.append(codegen_m)


    codegen = FCodegen(filename=filename, name=name)
    s=codegen.doprint(language=language, accelerator=accelerator)
    if show:
        print('========Fortran_Code========')
        print(s)
        print('============================')
        print ">>> Codegen :", name, " done."

    modules   = codegen.modules

    # ...

    # ...
    if compiler:
        for codegen_m in ms:
            compiler_m = Compiler(codegen_m, \
                                  compiler=compiler, \
                                  accelerator=accelerator, \
                                  debug=debug)
            compiler_m.compile(verbose=verbose)

        c = Compiler(codegen, \
                     compiler=compiler, \
                     inline=inline, \
                     accelerator=accelerator, \
                     debug=debug)
        c.compile(verbose=verbose)

        if execute:
            execute_file(c.binary)
    # ...
# ...

# ...
# TODO improve args
def load_module(filename, language="fortran", compiler="gfortran"):
    # ...
    name = filename.split(".")[0]
    name = 'pyccel_m_{0}'.format(name)
    # ...

    # ...
    build_file(filename=filename, language=language, compiler=compiler, \
               execute=False, accelerator=None, \
               debug=False, verbose=True, show=True, inline=True, name=name)
    # ...

    # ...
    try:
        import external
        reload(external)
    except:
        pass
    import external
    # ...

    module = getattr(external, '{0}'.format(name))

    return module
# ...