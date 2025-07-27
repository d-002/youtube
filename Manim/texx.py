from theme import *
from manim import *

t2c = {'x_A': COL1, 'y_A': COL1, 'x_B': COL2, 'y_B': COL2, 'x_C': COL3, 'y_C': COL3, 'x_P': COL4, 'y_P': COL4, 'A': COL1, 'B': COL2, 'C': COL3, 'P': COL4}

def set_template():
    global template, texcolors

    template = TexTemplate(preamble=r'\usepackage{xcolor}\usepackage{amsmath}')
    texcolors = {}
    name_ord = 65

    for col in t2c.values():
        name = chr(name_ord)
        name_ord += 1
        template.add_to_preamble('\\definecolor{'+name+'}{HTML}{'+col.to_hex()[1:]+'}')
        texcolors[col] = name

    return template # for use from other files
set_template()

class Texx(Tex):
    def __init__(self, *args, **kwargs):
        args = [f'${arg}$' for arg in args]
        args = self.colorize(args)

        super().__init__(*args, **kwargs)
        self.arrange(RIGHT, buff=.1)

    def colorize(self, args):
        newargs = []
        for arg in args:
            newarg = ''

            L = len(arg)
            i = 0
            while i < L:
                found = False

                for word, col in t2c.items():
                    l = len(word)

                    if arg[i:i+l] == word:
                        newarg += r'\textcolor{'+texcolors[col]+'}{'+word+'} '
                        i += l
                        found = True
                        break

                if not found:
                    newarg += arg[i]
                    i += 1

            newargs.append(newarg)

        return newargs
