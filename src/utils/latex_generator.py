__author__ = 'Anthony Rouneau'


def generate_longtable(titles, file_name, table):
    assert(len(titles) == len(table[0]))
    latex = "\\documentclass[letterpaper, 12pt]{article}\n\\usepackage{longtable}\n" \
            "\\begin{document}\n\\begin{longtable}"
    latex = latex + "{|" + "c|" * len(titles) + "}" + "\n"
    latex += ("\\hline" + "\n")
    for i, title in enumerate(titles):
        latex += ("\\textbf{" + str(title) + "}")
        if i != len(titles) - 1:
            latex += " & "
        else:
            latex = latex + " \\\\\n" + "\\hline\n"
    for line in table:
        for k, elem in enumerate(line):
            latex += str(elem)
            if k != len(line) - 1:
                latex += " & "
            else:
                latex = latex + " \\\\\n" + "\\hline\n"
    latex += "\\end{longtable}"
    latex += "\\end{document}"
    output = open(file_name + ".tex", mode="w")
    output.write(latex)
    output.close()

