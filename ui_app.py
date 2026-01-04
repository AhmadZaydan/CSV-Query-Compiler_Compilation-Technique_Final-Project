# ui_app.py
import tkinter as tk
from tkinter import ttk, messagebox

from parser import parse
from executor import execute_query

# Optional: if you have these helpers in main.py, you can reuse them.
# If not, this UI will just print Query(...) for now.
def describe_query(query) -> str:
    # Minimal description (safe even if you haven't updated AST for DISTINCT/AS/etc.)
    lines = []
    lines.append(f"FROM: {query.from_clause.filename}")
    try:
        # old version: query.select_clause.columns
        cols = getattr(query.select_clause, "columns", None)
        if cols is not None:
            lines.append("SELECT: " + ", ".join(cols))
        else:
            # new version (items/distinct) if you implemented it
            lines.append("SELECT: (see AST)")
    except Exception:
        lines.append("SELECT: (unknown)")

    lines.append("WHERE: " + ("(exists)" if query.where_expr else "(none)"))
    lines.append("ORDER BY: " + (f"{query.order_by.column} {'ASC' if query.order_by.ascending else 'DESC'}" if query.order_by else "(none)"))
    lines.append("LIMIT: " + (str(query.limit.count) if query.limit else "(none)"))
    # if you add offset later:
    off = getattr(query, "offset", None)
    lines.append("OFFSET: " + (str(off.count) if off else "(none)"))
    return "\n".join(lines)


class CSVQueryUI(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("CSV Query Compiler UI")
        self.geometry("1100x700")

        # --- Top frame: query input ---
        top = ttk.Frame(self, padding=10)
        top.pack(side=tk.TOP, fill=tk.BOTH, expand=False)

        ttk.Label(top, text="Query Input").pack(anchor="w")

        self.query_text = tk.Text(top, height=10, wrap="none")
        self.query_text.pack(fill=tk.BOTH, expand=True, pady=6)

        # Example query (you can delete this)
        self.query_text.insert(
            "1.0",
            'FROM "HARGA RUMAH JAKSEL.csv"\n'
            "SELECT HARGA, LT\n"
            "WHERE HARGA >= 10000000000 AND LT <= 1000\n"
            "ORDER BY HARGA DESC\n"
            "LIMIT 10\n"
        )

        btns = ttk.Frame(top)
        btns.pack(fill=tk.X)

        ttk.Button(btns, text="Run Query", command=self.run_query).pack(side=tk.LEFT)
        ttk.Button(btns, text="Clear", command=self.clear_all).pack(side=tk.LEFT, padx=8)

        # --- Middle frame: parsed description / errors ---
        mid = ttk.Frame(self, padding=10)
        mid.pack(side=tk.TOP, fill=tk.BOTH, expand=False)

        ttk.Label(mid, text="Parsed Summary / Errors").pack(anchor="w")
        self.summary = tk.Text(mid, height=7, wrap="word", state="disabled")
        self.summary.pack(fill=tk.BOTH, expand=True, pady=6)

        # --- Bottom frame: results table ---
        bottom = ttk.Frame(self, padding=10)
        bottom.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        ttk.Label(bottom, text="Result Table").pack(anchor="w")

        self.tree = ttk.Treeview(bottom, show="headings")
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        yscroll = ttk.Scrollbar(bottom, orient="vertical", command=self.tree.yview)
        yscroll.pack(side=tk.RIGHT, fill=tk.Y)
        self.tree.configure(yscrollcommand=yscroll.set)

    def clear_all(self):
        self.query_text.delete("1.0", tk.END)
        self._set_summary("")
        self._clear_table()

    def _set_summary(self, text: str):
        self.summary.configure(state="normal")
        self.summary.delete("1.0", tk.END)
        self.summary.insert("1.0", text)
        self.summary.configure(state="disabled")

    def _clear_table(self):
        for col in self.tree["columns"]:
            self.tree.heading(col, text="")
        self.tree["columns"] = ()
        self.tree.delete(*self.tree.get_children())

    def _load_df_to_table(self, df):
        self._clear_table()

        cols = list(df.columns)
        self.tree["columns"] = cols
        for c in cols:
            self.tree.heading(c, text=c)
            self.tree.column(c, width=120, anchor="w")

        # Insert rows (limit displayed rows to keep UI fast)
        max_rows = 500
        for i, row in enumerate(df.itertuples(index=False, name=None)):
            if i >= max_rows:
                break
            self.tree.insert("", "end", values=row)

        if len(df) > max_rows:
            self._set_summary(self.summary.get("1.0", tk.END).strip() + f"\n\n(Showing first {max_rows} rows out of {len(df)})")

    def run_query(self):
        text = self.query_text.get("1.0", tk.END).strip()
        if not text:
            messagebox.showinfo("Info", "Please enter a query first.")
            return

        try:
            q = parse(text)
            desc = describe_query(q)
            self._set_summary("Parsed Query:\n" + desc)

            df = execute_query(q)
            self._load_df_to_table(df)

        except Exception as e:
            self._set_summary("Error:\n" + str(e))
            self._clear_table()


if __name__ == "__main__":
    app = CSVQueryUI()
    app.mainloop()
