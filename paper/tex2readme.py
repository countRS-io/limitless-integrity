"""
Generate README.md from paper/limitless.tex, followed by the repository guide in paper/readme_repo.md.

Handles the subset of LaTeX the paper uses: sections, abstract, paragraphs, \\texttt, \\emph, \\textbf, \\href, \\url, \\nolinkurl, itemize and enumerate, booktabs tables, figures (shown as their PNG), \\ref and \\label.
"""

import os, re

HERE = os.path.dirname(os.path.abspath(__file__))
TEX = os.path.join(HERE, "limitless.tex")
TAIL = os.path.join(HERE, "readme_repo.md")
OUT = os.path.join(HERE, "..", "README.md")


def strip_comments(s):
    # A % not preceded by a backslash starts a comment.
    return "\n".join(re.sub(r"(?<!\\)%.*$", "", line) for line in s.splitlines())


def _unescape_url(u):
    return u.replace("\\%", "%").replace("\\_", "_").replace("\\#", "#").replace("\\&", "&")


def inline(s):
    # Link text may hold one level of braces, as in \href{url}{\texttt{0xabc}}.
    s = re.sub(r"\\href\{([^}]*)\}\{((?:[^{}]|\{[^{}]*\})*)\}",
               lambda m: f"[{inline(m.group(2))}]({_unescape_url(m.group(1))})", s)
    s = re.sub(r"\\url\{([^}]*)\}", lambda m: f"<{_unescape_url(m.group(1))}>", s)
    s = re.sub(r"\\nolinkurl\{([^}]*)\}", lambda m: "`" + m.group(1) + "`", s)
    s = re.sub(r"\\texttt\{([^}]*)\}", lambda m: "`" + m.group(1).replace("\\ldots ", "…").replace("\\ldots", "…").replace("\\ ", " ") + "`", s)
    s = re.sub(r"\\emph\{([^}]*)\}", r"*\1*", s)
    s = re.sub(r"\\textbf\{([^}]*)\}", r"**\1**", s)
    s = s.replace("``", "“").replace("''", "”").replace("\\ldots", "…")
    s = s.replace("\\%", "%").replace("\\&", "&").replace("\\_", "_").replace("\\#", "#")
    s = s.replace("~", " ").replace("\\\\", "")
    return re.sub(r"[ \t]+", " ", s).strip()


def table(body, caption, n):
    rows = [r.strip() for r in re.split(r"\\\\", body)]
    rows = [r for r in rows if r and not re.match(r"^\\(toprule|midrule|bottomrule)$", r)]
    rows = [re.sub(r"\\(toprule|midrule|bottomrule)", "", r).strip() for r in rows]
    cells = [[inline(c) for c in r.split("&")] for r in rows if r]
    head, rest = cells[0], cells[1:]
    md = ["| " + " | ".join(head) + " |", "|" + "|".join("---" for _ in head) + "|"]
    md += ["| " + " | ".join(r) + " |" for r in rest]
    return f"**Table {n}.** {inline(caption)}\n\n" + "\n".join(md)


def main():
    s = strip_comments(open(TEX).read())
    title = re.search(r"\\title\{(.*?)\}", s).group(1)
    body = s[s.index("\\maketitle") + len("\\maketitle"):s.index("\\end{document}")]

    # Number figures and tables in order, then resolve \ref.
    labels, counts = {}, {"figure": 0, "table": 0}
    for m in re.finditer(r"\\begin\{(figure|table)\}.*?\\label\{(.*?)\}.*?\\end\{\1\}", body, re.S):
        counts[m.group(1)] += 1
        labels[m.group(2)] = counts[m.group(1)]
    body = re.sub(r"(Figure|Table)~?\\ref\{(.*?)\}", lambda m: f"{m.group(1)} {labels[m.group(2)]}", body)

    def fig(m):
        block = m.group(0)
        path = re.search(r"\\includegraphics(?:\[.*?\])?\{(.*?)\}", block).group(1)
        cap = re.search(r"\\caption\{(.*)\}\s*\\label", block, re.S).group(1)
        n = labels[re.search(r"\\label\{(.*?)\}", block).group(1)]
        png = "paper/" + os.path.splitext(path)[0] + ".png"
        return f"\n\n![Figure {n}]({png})\n\n*Figure {n}. {inline(cap)}*\n\n"

    def tab(m):
        block = m.group(0)
        tb = re.search(r"\\begin\{tabular\}\{.*?\}(.*?)\\end\{tabular\}", block, re.S).group(1)
        cap = re.search(r"\\caption\{(.*)\}\s*\\label", block, re.S).group(1)
        n = labels[re.search(r"\\label\{(.*?)\}", block).group(1)]
        return "\n\n" + table(tb, cap, n) + "\n\n"

    body = re.sub(r"\\begin\{figure\}.*?\\end\{figure\}", fig, body, flags=re.S)
    body = re.sub(r"\\begin\{table\}.*?\\end\{table\}", tab, body, flags=re.S)
    body = re.sub(r"\\begin\{abstract\}(.*?)\\end\{abstract\}",
                  lambda m: "\n\n## Summary\n\n" + m.group(1) + "\n\n", body, flags=re.S)
    def lst(m):
        kind, inner = m.group(1), m.group(2)
        items = [i.strip() for i in re.split(r"\\item\s+", inner) if i.strip()]
        mark = (lambda k: f"{k}. ") if kind == "enumerate" else (lambda k: "- ")
        return "\n\n" + "\n".join(mark(k) + inline(" ".join(i.split())) for k, i in enumerate(items, 1)) + "\n\n"

    body = re.sub(r"\\begin\{(itemize|enumerate)\}(.*?)\\end\{\1\}", lst, body, flags=re.S)
    body = re.sub(r"\\section\*?\{(.*?)\}", lambda m: f"\n\n## {inline(m.group(1))}\n\n", body)
    body = re.sub(r"\\subsection\*?\{(.*?)\}", lambda m: f"\n\n### {inline(m.group(1))}\n\n", body)
    body = body.replace("\\appendix", "")

    out = []
    for para in re.split(r"\n\s*\n", body):
        p = para.strip()
        if not p:
            continue
        if p.startswith(("#", "|", "![", "*Figure", "**Table", "- ", "1. ")):
            out.append(p)
        else:
            out.append(inline(" ".join(p.split("\n"))))
    head = f"# {title}\n\nRead [DISCLAIMER.md](DISCLAIMER.md) first."
    text = head + "\n\n" + "\n\n".join(out) + "\n\n---\n\n" + open(TAIL).read().strip() + "\n"
    open(OUT, "w").write(text)
    print("wrote", os.path.relpath(OUT))


if __name__ == "__main__":
    main()
