import sqlite3
from basic_forms import *
from tkinter import messagebox
from invoice_view import InvoiceView
from transaction_form import TransactionForm
from summary_view import SaleSummaryView, PurchaseSummaryView

class MainApplication:
    def __init__(self, root):
        self.root = root
        self.root.title("Inventory Management System")
        self.db_conn = sqlite3.connect("../database/inventory.db")

        # Load menu configuration
        with open("layouts/menu_config.json") as f:
            self.menu_config = json.load(f)

        self._setup_ui()

    def _setup_ui(self):
        # Create Menubar
        self.menubar = tk.Menu(self.root)
        self.root.config(menu=self.menubar)

        # Create Notebook
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill="both", expand=True)
        self.open_tabs = {
            "fy_independent": set(),
            "fy_dependent": None
        }
        self.tab_instances = {}

        # Build menus from config
        self._build_menus()

    def _build_menus(self):
        for menu_label, items in self.menu_config["menu_bar"].items():
            menu = tk.Menu(self.menubar, tearoff=0)
            self.menubar.add_cascade(label=menu_label, menu=menu)

            for item_label, class_name in items.items():
                menu.add_command(
                    label=item_label,
                    command=lambda cn=class_name: self._open_tab(cn)
                )

    def _open_tab(self, class_name, no_bind=False, **kw):
        # Determine if this is an FY-dependent view
        is_fy_dependent = class_name in ("SaleSummaryView", "PurchaseSummaryView")

        # Check mutex rules
        if is_fy_dependent and self.open_tabs["fy_dependent"]:
            messagebox.showwarning(
                "Operation Not Allowed",
                "Please close the current FY-dependent view first!"
            )
            return

        # Get the actual class (would need imports)
        tab_class = self._get_class_by_name(class_name)
        if not tab_class:
            messagebox.showerror("Error", f"Class {class_name} not found!")
            return

        tab_names = [self.notebook.tab(i, option="text") for i in self.notebook.tabs()]
        if not "title" in kw.keys():
            title = self._find_menu_label(class_name)
        else:
            title = kw.pop("title")
        if title in tab_names:
            self.notebook.select(tab_names.index(title))
            return

        # Create new tab
        #title = self._find_menu_label(class_name)
        tab_instance = tab_class(self, db_conn=self.db_conn, title=title, **kw)
        tab_instance.root.pack(fill="both", expand=True)

        # # Use the menu label as tab title
        self.notebook.add(tab_instance.root, text=title)
        self.notebook.select(tab_instance.root)

        # Update tracker
        if is_fy_dependent:
            self.open_tabs["fy_dependent"] = title
        else:
            self.open_tabs["fy_independent"].add(title)

        # Bind close event
        if not no_bind:
            tab_instance.root.bind("<Destroy>", lambda e, t=title: self._on_tab_close(t))

        self.tab_instances[title] = tab_instance
        #print("Adding tab. New tabs list = ", list(self.tab_instances.keys()))

    def _get_class_by_name(self, class_name):
        # This would map to actual imported classes
        classes = {
            "FYForm": FyForm,
            "PartyForm": PartyForm,
            "ProductForm": ProductForm,
            "InvoiceView" : InvoiceView,
            "TransactionForm": TransactionForm,
            "SaleSummaryView": SaleSummaryView,
            "PurchaseSummaryView": PurchaseSummaryView,
            "SalePaymentForm": "", #SalePaymentForm,
            "PurchasePaymentForm": "", #PurchasePaymentForm
        }
        return classes.get(class_name)

    def _find_menu_label(self, class_name):
        for menu_items in self.menu_config["menu_bar"].values():
            for label, cn in menu_items.items():
                if cn == class_name:
                    return label
        return class_name

    def _on_tab_close(self, title):
        if title == self.open_tabs["fy_dependent"]:
            self.open_tabs["fy_dependent"] = None
        else:
            self.open_tabs["fy_independent"].discard(title)
        del self.tab_instances[title]


if __name__ == "__main__":
    root = tk.Tk()
    root.geometry("1022x695")
    app = MainApplication(root)
    #root.report_callback_exception = lambda exc=None,msg=None,tb=None : messagebox.showerror("Error",msg)
    root.mainloop()
