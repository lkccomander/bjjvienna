import ast
import sys

class TkinterStructureValidator(ast.NodeVisitor):
    def __init__(self):
        self.tk_count = 0
        self.notebook_count = 0
        self.tab_defs = {}
        self.notebook_adds = []

    def visit_Call(self, node):
        # Detect tk.Tk()
        if isinstance(node.func, ast.Attribute):
            if node.func.attr == "Tk":
                self.tk_count += 1

            if node.func.attr == "Notebook":
                self.notebook_count += 1

            if node.func.attr == "add":
                if node.args:
                    self.notebook_adds.append(ast.unparse(node.args[0]))

        self.generic_visit(node)

    def visit_Assign(self, node):
        for target in node.targets:
            if isinstance(target, ast.Name) and target.id.startswith("tab_"):
                self.tab_defs.setdefault(target.id, 0)
                self.tab_defs[target.id] += 1
        self.generic_visit(node)


def validate(file_path):
    with open(file_path, "r", encoding="utf-8") as f:
        tree = ast.parse(f.read())

    v = TkinterStructureValidator()
    v.visit(tree)

    errors = []

    if v.tk_count != 1:
        errors.append(f"❌ tk.Tk() count = {v.tk_count} (must be 1)")

    if v.notebook_count != 1:
        errors.append(f"❌ ttk.Notebook count = {v.notebook_count} (must be 1)")

    for tab, count in v.tab_defs.items():
        if count > 1:
            errors.append(f"❌ {tab} defined {count} times")

    defined_tabs = set(v.tab_defs.keys())
    added_tabs = set(v.notebook_adds)

    for tab in defined_tabs:
        if tab not in added_tabs:
            errors.append(f"❌ {tab} defined but NOT added to notebook")

    if errors:
        print("\nSTRUCTURE ERRORS FOUND:\n")
        for e in errors:
            print(e)
        sys.exit(1)

    print("✅ GUI STRUCTURE OK — no structural issues found")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python validate_gui_structure.py gui.py")
        sys.exit(1)

    validate(sys.argv[1])
