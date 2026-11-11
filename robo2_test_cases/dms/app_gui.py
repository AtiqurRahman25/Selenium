"""
Robo2mation Test Automation Suite Desktop Client
Supports Module Selection (DMS, Core, Workflow, Reports),
real-time log streaming, and standalone PyInstaller compilation.
"""
import importlib
import os
import queue
import subprocess
import sys
import threading
import time
from datetime import datetime
from pathlib import Path
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from tkinter.scrolledtext import ScrolledText

# Determine root folder whether running in source code or PyInstaller frozen bundle
if getattr(sys, "frozen", False):
    APP_DIR = Path(sys.executable).resolve().parent
    BUNDLE_DIR = Path(sys._MEIPASS)
else:
    APP_DIR = Path(__file__).resolve().parent
    BUNDLE_DIR = APP_DIR

# Ensure APP_DIR is at the top of sys.path
if str(APP_DIR) not in sys.path:
    sys.path.insert(0, str(APP_DIR))

# ==============================================================================
# SUBPROCESS WORKER DISPATCHER
# Allows child processes to run isolated tests inside the compiled EXE
# ==============================================================================
def run_as_worker():
    """Runs a single test case file in process isolation when called with CLI args."""
    if len(sys.argv) >= 3 and sys.argv[1] == "--worker-test":
        test_module_name = sys.argv[2]
        sheet_name = sys.argv[3] if len(sys.argv) > 3 else "DMS"
        os.environ["SHEET_NAME"] = sheet_name

        try:
            # Strip .py extension if provided
            mod_stem = Path(test_module_name).stem
            mod = importlib.import_module(mod_stem)
            if hasattr(mod, "main"):
                mod.main()
            sys.exit(0)
        except SystemExit as se:
            sys.exit(se.code if se.code is not None else 0)
        except Exception as err:
            import traceback
            traceback.print_exc()
            sys.exit(1)


# ==============================================================================
# MODULE DEFINITIONS (Add Core, Workflow, Reports here as scripts are added)
# ==============================================================================
MODULES = {
    "DMS": {
        "sheet_name": "DMS",
        "script_pattern": "tc*.py",
        # Explicit test files for DMS
        "tests": [
            ("DMS-TC002", "tc002_document_attach.py", "Document Attach (18 file types)"),
            ("DMS-TC003", "tc003_doc_view_grid.py", "Document View (Grid View)"),
            ("DMS-TC009", "tc009_Upload_Document.py", "Upload Document (Required metadata)"),
            ("DMS-TC011", "tc011_Multiple_pdf_merge.py", "Multiple PDF Merge"),
            ("DMS-TC012", "tc012_document_name_convention.py", "Document Name Convention"),
            ("DMS-TC014", "tc014_version_doc_upload.py", "Version Doc Upload"),
            ("DMS-TC015", "tc015_download_version_doc.py", "Download Version Doc"),
            ("DMS-TC016", "tc016_delete_version_doc.py", "Delete Version Doc"),
            ("DMS-TC019", "tc019_edit_metadata.py", "Edit Metadata"),
            ("DMS-TC020", "tc020_check_out_doc.py", "Check-Out Document"),
            ("DMS-TC021", "tc021_cancel_checkout_doc.py", "Cancel Check-Out"),
            ("DMS-TC022", "tc022_download_document.py", "Download Document"),
            ("DMS-TC023", "tc023_multiple_doc_download.py", "Multiple Document Download (Zip)"),
            ("DMS-TC024", "tc024_document_full_view.py", "Document Full View (New Tab)"),
            ("DMS-TC025", "tc025_archive_doc.py", "Archive Document"),
            ("DMS-TC026", "tc026_restore_archived_doc.py", "Restore Archived Document"),
            ("DMS-TC027", "tc027_delete_document.py", "Delete Document"),
            ("DMS-TC028", "tc028_restore_deleted_doc.py", "Restore Deleted Document"),
            ("DMS-TC030", "tc030_add_related_files.py", "Add Related Files"),
            ("DMS-TC031", "tc031_delete_related_files.py", "Delete Related Files"),
            ("DMS-TC032", "tc032_share_documents_users_groups_all.py", "Share Documents (Users/Groups/All)"),
            ("DMS-TC033", "tc033_share_documents_external.py", "Share Documents (Public Share)"),
            ("DMS-TC034", "tc034_share_documents_delete.py", "Share Documents (Delete Share)"),
            ("DMS-TC036", "tc036_share_documents_email.py", "Share Documents (Email)"),
            ("DMS-TC037", "tc037_document_ocr.py", "Document OCR"),
            ("DMS-TC042", "tc042_watermark_custom_text.py", "Watermark (Custom Text)"),
            ("DMS-TC045", "tc045_watermark_upload.py", "Watermark (Upload File)"),
            ("DMS-TC046", "tc046_search_water_mark.py", "Search Watermark"),
            ("DMS-TC049", "tc049_document_watermark.py", "Document Watermark (Attach)"),
            ("DMS-TC050", "tc050_delete_watermark.py", "Delete Watermark"),
            ("DMS-TC051", "tc051_my_documents.py", "My Documents (Permissions)"),
            ("DMS-TC055", "tc055_grid_view_on_my_documents.py", "Grid View on My Documents"),
            ("DMS-TC056", "tc056_list_view_on_my_documents.py", "List View on My Documents"),
            ("DMS-TC057", "tc057_default_sorting_on_my_documents.py", "Default Sorting (Date Descending)"),
            ("DMS-TC058", "tc058_sorting_name_ascending_on_my_documents.py", "Sorting (Name Ascending)"),
            ("DMS-TC059", "tc059_sorting_name_descending_on_my_documents.py", "Sorting (Name Descending)"),
            ("DMS-TC060", "tc060_sorting_date_ascending_on_my_documents.py", "Sorting (Date Ascending)"),
            ("DMS-TC061", "tc061_sorting_date_descending_on_my_documents.py", "Sorting (Date Descending)"),
            ("DMS-TC062", "tc062_default_sorting_category_doc_type.py", "Category Default Sorting"),
            ("DMS-TC067", "tc067_categorization_doc_type_creation.py", "Doc-Type Creation"),
            ("DMS-TC069", "tc069_update_category_doc_type.py", "Update Category/Doc-Type"),
            ("DMS-TC073", "tc073_delete_category_doc_type.py", "Delete Category/Doc-Type"),
            ("DMS-TC075", "tc075_deleted_category_map.py", "Deleted Category Map"),
            ("DMS-TC076", "tc076_deleted_category_restore.py", "Deleted Category Restore"),
            ("DMS-TC077", "tc077_deleted_category_permanent_deletion.py", "Deleted Category Permanent Delete"),
            ("DMS-TC078", "tc078_deleted_category_full_path.py", "Deleted Category Full Path"),
            ("DMS-TC080", "tc080_publish_doc_type.py", "Publish Doc-Type"),
            ("DMS-TC081", "tc081_assign_access_group_in_doc_type.py", "Assign Access Group"),
            ("DMS-TC082", "tc082_assign_owner_group_in_doc_type.py", "Assign Owner Group"),
            ("DMS-TC083", "tc083_document_notify_on.py", "Document Notify On"),
            ("DMS-TC084", "tc084_document_notify_off.py", "Document Notify Off"),
            ("DMS-TC085", "tc085_create_metadata.py", "Create Metadata Field"),
            ("DMS-TC086", "tc086_update_metadata.py", "Update Metadata Field"),
            ("DMS-TC087", "tc087_delete_metadata.py", "Delete Metadata Field"),
            ("DMS-TC090", "tc090_metadata_uniqueness.py", "Metadata Uniqueness (Single)"),
            ("DMS-TC091", "tc091_metadata_uniqueness_or.py", "Metadata Uniqueness (OR)"),
            ("DMS-TC092", "tc092_metadata_uniqueness_and.py", "Metadata Uniqueness (AND)"),
            ("DMS-TC093", "tc093_bulk_upload_template_download.py", "Bulk Upload Template Download"),
            ("DMS-TC094", "tc094_bulk_upload_template_upload_invalid.py", "Bulk Upload Validation (Errors)"),
            ("DMS-TC095", "tc095_bulk_upload_template_upload_valid.py", "Bulk Upload Valid Template"),
            ("DMS-TC101", "tc101_master_table_method_fetch_multiple_record.py", "Master Table Method (Multiple Record)"),
            ("DMS-TC102", "tc102_master_table_method_fetch_single_record.py", "Master Table Method (Single Record)"),
            ("DMS-TC103", "tc103_master_table_method_update_multiple_record.py", "Master Table Method Update (Multiple)"),
            ("DMS-TC104", "tc104_master_table_method_update_single_record.py", "Master Table Method Update (Single)"),
            ("DMS-TC105", "tc105_master_table_method_delete.py", "Master Table Method Delete"),
            ("DMS-TC106", "tc106_master_table_method_filter_by_doc_type.py", "Master Table Filter By Doc-Type"),
            ("DMS-TC107", "tc107_master_table_method_search.py", "Master Table Method Search"),
            ("DMS-TC108", "tc108_master_table_method_disable.py", "Master Table Method Disable"),
            ("DMS-TC109", "tc109_master_table_method_enable.py", "Master Table Method Enable"),
            ("DMS-TC110", "tc110_master_table_method_clone.py", "Master Table Method Clone"),
            ("DMS-TC112", "tc112_master_table_method_assign.py", "Master Table Method Assign"),
            ("DMS-TC119", "tc119_quick_search.py", "Quick Search"),
            ("DMS-TC121", "tc121_advanced_search_enable_match_all.py", "Advanced Search (Match All ON)"),
            ("DMS-TC122", "tc122_advanced_search_disable_match_all.py", "Advanced Search (Match All OFF)"),
            ("DMS-TC124", "tc124_advanced_search_enable_archive.py", "Advanced Search (Include Archive)"),
            ("DMS-TC125", "tc125_save_search.py", "Save Advanced Search"),
            ("DMS-TC126", "tc126_saved_search_list.py", "Saved Search List"),
            ("DMS-TC127", "tc127_document_maker_checker_feature.py", "Maker-Checker Upload & Review"),
            ("DMS-TC128", "tc128_pending_for_review_requested_by_me.py", "Pending Review: Requested By Me"),
            ("DMS-TC130", "tc130_document_review_by_checker.py", "Pending Review: Checker Options"),
            ("DMS-TC131", "tc131_document_approve_reject.py", "Document Approve & Reject"),
            ("DMS-TC132", "tc132_bulk_upload.py", "Bulk Upload Large Files"),
            ("DMS-TC136", "tc136_pdf_document_ocr_from_advanced_search.py", "OCR Advanced Search"),
            ("DMS-TC137", "tc137_pdf_document_ocr_from_my_documents_search.py", "OCR Explorer Search"),
            ("DMS-TC139", "tc139_chat_with_pdf.py", "Chat With PDF (Ask Effy AI)"),
        ],
    },
    "Core": {
        "sheet_name": "Core",
        "script_pattern": "cor_tc*.py",
        "tests": [
            # ("COR-TC001", "cor_tc001_login.py", "Core Valid Login"),
            # Placeholder for future Core scripts
        ],
    },
    "Workflow": {
        "sheet_name": "Workflow",
        "script_pattern": "wf_tc*.py",
        "tests": [
            # Placeholder for future Workflow scripts
        ],
    },
    "Report": {
        "sheet_name": "Report",
        "script_pattern": "rep_tc*.py",
        "tests": [
            # Placeholder for future Report scripts
        ],
    },
}


# ==============================================================================
# MAIN GUI APPLICATION
# ==============================================================================
class AutomationRunnerGUI(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Robo2mation Automated QA Test Runner v6.0")
        self.geometry("980x740")
        self.minsize(850, 600)

        # Execution State
        self.is_running = False
        self.stop_requested = False
        self.log_queue = queue.Queue()
        self.current_process = None

        # Build UI Elements
        self._setup_styles()
        self._build_header()
        self._build_config_bar()
        self._build_main_split()
        self._build_status_footer()

        # Start listening for incoming log stream
        self.after(100, self._process_log_queue)

    def _setup_styles(self):
        self.style = ttk.Style(self)
        self.style.theme_use("clam")

        # Palette
        self.configure(bg="#F4F6F9")
        self.style.configure("TFrame", background="#F4F6F9")
        self.style.configure("TLabelframe", background="#FFFFFF", relief="solid", borderwidth=1)
        self.style.configure("TLabelframe.Label", background="#FFFFFF", font=("Segoe UI", 10, "bold"), foreground="#2D3748")
        self.style.configure("Header.TFrame", background="#1E293B")
        self.style.configure("Header.TLabel", background="#1E293B", foreground="#FFFFFF")
        
        self.style.configure("Run.TButton", font=("Segoe UI", 10, "bold"), background="#10B981", foreground="#FFFFFF")
        self.style.map("Run.TButton", background=[("active", "#059669"), ("disabled", "#CBD5E1")])
        self.style.configure("Stop.TButton", font=("Segoe UI", 10, "bold"), background="#EF4444", foreground="#FFFFFF")
        self.style.map("Stop.TButton", background=[("active", "#DC2626"), ("disabled", "#CBD5E1")])

    def _build_header(self):
        header = ttk.Frame(self, style="Header.TFrame", padding=(20, 14))
        header.pack(fill=tk.X, side=tk.TOP)

        title = ttk.Label(header, text="Robo2mation Automated Sanity Suite", font=("Segoe UI", 16, "bold"), style="Header.TLabel")
        title.pack(anchor=tk.W)

        subtitle = ttk.Label(header, text="Select module, review target test cases, and execute with live browser monitoring.", font=("Segoe UI", 9), style="Header.TLabel")
        subtitle.pack(anchor=tk.W)

    def _build_config_bar(self):
        bar = ttk.LabelFrame(self, text=" Configuration & Target Module ", padding=(15, 10))
        bar.pack(fill=tk.X, padx=15, pady=(10, 5))

        # Module Dropdown
        ttk.Label(bar, text="Module / Sheet:", font=("Segoe UI", 9, "bold")).grid(row=0, column=0, sticky=tk.W, padx=(0, 6), pady=4)
        self.module_var = tk.StringVar(value="DMS")
        self.module_dropdown = ttk.Combobox(bar, textvariable=self.module_var, values=list(MODULES.keys()), state="readonly", width=14, font=("Segoe UI", 9))
        self.module_dropdown.grid(row=0, column=1, sticky=tk.W, padx=(0, 20), pady=4)
        self.module_dropdown.bind("<<ComboboxSelected>>", self._on_module_changed)

        # Excel File Path
        ttk.Label(bar, text="Excel Report:", font=("Segoe UI", 9, "bold")).grid(row=0, column=2, sticky=tk.W, padx=(0, 6), pady=4)
        default_excel = os.getenv("EXCEL_PATH", str(APP_DIR / "Robo2mation_26Q1_Sanity_Test_Case_Doc.xlsx"))
        self.excel_var = tk.StringVar(value=default_excel)
        excel_entry = ttk.Entry(bar, textvariable=self.excel_var, width=42, font=("Segoe UI", 9))
        excel_entry.grid(row=0, column=3, sticky=tk.EW, padx=(0, 8), pady=4)
        browse_btn = ttk.Button(bar, text="Browse...", command=self._browse_excel, width=9)
        browse_btn.grid(row=0, column=4, sticky=tk.W, pady=4)

        bar.columnconfigure(3, weight=1)

    def _build_main_split(self):
        paned = ttk.PanedWindow(self, orient=tk.HORIZONTAL)
        paned.pack(fill=tk.BOTH, expand=True, padx=15, pady=5)

        # Left Column: Test Case Selection
        left_frame = ttk.LabelFrame(paned, text=" Available Test Cases ", padding=(10, 8))
        paned.add(left_frame, weight=3)

        list_toolbar = ttk.Frame(left_frame)
        list_toolbar.pack(fill=tk.X, pady=(0, 6))

        ttk.Button(list_toolbar, text="Select All", command=self._select_all_tests, width=11).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(list_toolbar, text="Deselect All", command=self._deselect_all_tests, width=11).pack(side=tk.LEFT)

        # Scrollable Frame for Test Cases
        canvas = tk.Canvas(left_frame, bg="#FFFFFF", highlightthickness=0)
        scrollbar = ttk.Scrollbar(left_frame, orient=tk.VERTICAL, command=canvas.yview)
        self.test_list_frame = ttk.Frame(canvas, style="TFrame")
        self.test_list_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))

        canvas.create_window((0, 0), window=self.test_list_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Right Column: Console Stream & Progress Controls
        right_frame = ttk.LabelFrame(paned, text=" Execution Output & Controls ", padding=(10, 8))
        paned.add(right_frame, weight=5)

        ctrl_box = ttk.Frame(right_frame)
        ctrl_box.pack(fill=tk.X, pady=(0, 8))

        self.run_btn = ttk.Button(ctrl_box, text="► Run Selected Tests", style="Run.TButton", command=self._start_run, width=20)
        self.run_btn.pack(side=tk.LEFT, padx=(0, 10))

        self.stop_btn = ttk.Button(ctrl_box, text="■ Stop Execution", style="Stop.TButton", command=self._stop_run, width=16, state=tk.DISABLED)
        self.stop_btn.pack(side=tk.LEFT)

        self.clear_btn = ttk.Button(ctrl_box, text="Clear Log", command=self._clear_logs, width=10)
        self.clear_btn.pack(side=tk.RIGHT)

        # Console Log Area
        self.log_text = ScrolledText(right_frame, wrap=tk.WORD, bg="#0F172A", fg="#E2E8F0", insertbackground="#38BDF8", font=("Consolas", 9))
        self.log_text.pack(fill=tk.BOTH, expand=True)

        # Populate initial test list
        self.test_vars = {}
        self._populate_test_list("DMS")

    def _build_status_footer(self):
        footer = ttk.Frame(self, padding=(15, 8))
        footer.pack(fill=tk.X, side=tk.BOTTOM)

        self.progress_bar = ttk.Progressbar(footer, orient=tk.HORIZONTAL, mode="determinate")
        self.progress_bar.pack(fill=tk.X, side=tk.TOP, pady=(0, 6))

        stats_box = ttk.Frame(footer)
        stats_box.pack(fill=tk.X, side=tk.BOTTOM)

        self.status_lbl = ttk.Label(stats_box, text="Ready", font=("Segoe UI", 9, "italic"), foreground="#475569")
        self.status_lbl.pack(side=tk.LEFT)

        self.summary_lbl = ttk.Label(stats_box, text="Total: 0  |  Passed: 0  |  Failed: 0", font=("Segoe UI", 9, "bold"), foreground="#1E293B")
        self.summary_lbl.pack(side=tk.RIGHT)

    # ==========================================================================
    # LOGIC & EVENT HANDLERS
    # ==========================================================================
    def _browse_excel(self):
        f = filedialog.askopenfilename(
            title="Select Test Case Excel File",
            filetypes=[("Excel Files", "*.xlsx *.xls"), ("All Files", "*.*")],
            initialdir=str(APP_DIR),
        )
        if f:
            self.excel_var.set(f)

    def _on_module_changed(self, event=None):
        mod = self.module_var.get()
        self._populate_test_list(mod)

    def _populate_test_list(self, module_name):
        for widget in self.test_list_frame.winfo_children():
            widget.destroy()
        self.test_vars.clear()

        tests = MODULES.get(module_name, {}).get("tests", [])
        if not tests:
            lbl = ttk.Label(self.test_list_frame, text=f"No automated tests configured for '{module_name}' yet.", font=("Segoe UI", 9, "italic"), foreground="#64748B")
            lbl.pack(anchor=tk.W, padx=5, pady=8)
            return

        for test_id, script_name, description in tests:
            var = tk.BooleanVar(value=True)
            self.test_vars[script_name] = (var, test_id, description)

            chk = ttk.Checkbutton(
                self.test_list_frame,
                text=f"{test_id}: {description}",
                variable=var,
            )
            chk.pack(anchor=tk.W, padx=4, pady=2)

    def _select_all_tests(self):
        for var, _, _ in self.test_vars.values():
            var.set(True)

    def _deselect_all_tests(self):
        for var, _, _ in self.test_vars.values():
            var.set(False)

    def _clear_logs(self):
        self.log_text.delete("1.0", tk.END)

    def _log(self, text):
        self.log_queue.put(text)

    def _process_log_queue(self):
        while not self.log_queue.empty():
            msg = self.log_queue.get_nowait()
            self.log_text.insert(tk.END, msg + "\n")
            self.log_text.see(tk.END)
        self.after(100, self._process_log_queue)

    def _start_run(self):
        if self.is_running:
            return

        selected_tests = [
            (script, tid, desc)
            for script, (var, tid, desc) in self.test_vars.items()
            if var.get()
        ]

        if not selected_tests:
            messagebox.showwarning("No Selection", "Please check at least one test case to execute.")
            return

        excel_path = self.excel_var.get().strip()
        if not os.path.isfile(excel_path):
            messagebox.showerror("Excel Missing", f"Could not find the Excel file:\n{excel_path}\nPlease browse and select a valid workbook.")
            return

        # Check if Excel is locked by Excel software
        try:
            with open(excel_path, "ab"):
                pass
        except PermissionError:
            messagebox.showerror("File Locked", f"The Excel file is currently open in Microsoft Excel.\nPlease save and close it before running tests.")
            return

        self.is_running = True
        self.stop_requested = False
        self.run_btn.configure(state=tk.DISABLED)
        self.stop_btn.configure(state=tk.NORMAL)
        self.module_dropdown.configure(state=tk.DISABLED)

        # Start execution in a dedicated background thread
        thread = threading.Thread(target=self._run_suite_thread, args=(selected_tests, excel_path), daemon=True)
        thread.start()

    def _stop_run(self):
        if self.is_running:
            self.stop_requested = True
            self._log("\n[!] User requested termination. Stopping after current step...")
            if self.current_process and self.current_process.poll() is None:
                try:
                    self.current_process.terminate()
                except Exception:
                    pass

    def _run_suite_thread(self, selected_tests, excel_path):
        module_name = self.module_var.get()
        sheet_name = MODULES[module_name]["sheet_name"]

        # Push environment variables into the session
        os.environ["EXCEL_PATH"] = str(Path(excel_path).resolve())
        os.environ["SHEET_NAME"] = sheet_name

        total = len(selected_tests)
        passed_count = 0
        failed_count = 0

        self.progress_bar["maximum"] = total
        self.progress_bar["value"] = 0

        start_time = time.time()
        self._log("=" * 70)
        self._log(f"Starting execution of {total} test(s) for Module: {module_name} (Sheet: {sheet_name})")
        self._log(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        self._log(f"Excel Path: {excel_path}")
        self._log("=" * 70 + "\n")

        for idx, (script_name, test_id, desc) in enumerate(selected_tests, start=1):
            if self.stop_requested:
                self._log(f"\n[-] Execution aborted by user. {idx - 1}/{total} tests completed.")
                break

            self.status_lbl.configure(text=f"Running [{idx}/{total}]: {test_id} ({desc})...")
            self._log(f"[{idx}/{total}] RUNNING: {test_id} ({script_name})...")

            script_path = APP_DIR / script_name
            if not script_path.exists():
                self._log(f"   -> FAIL: Script file '{script_name}' not found in directory.")
                failed_count += 1
                self.progress_bar["value"] = idx
                self.summary_lbl.configure(text=f"Total: {total}  |  Passed: {passed_count}  |  Failed: {failed_count}")
                continue

            test_start = time.time()
            success = self._execute_test_process(script_name, sheet_name)
            duration = time.time() - test_start

            if success:
                passed_count += 1
                self._log(f"   -> PASS ({duration:.1f}s)\n")
            else:
                failed_count += 1
                self._log(f"   -> FAIL ({duration:.1f}s)\n")

            self.progress_bar["value"] = idx
            self.summary_lbl.configure(text=f"Total: {total}  |  Passed: {passed_count}  |  Failed: {failed_count}")

        total_elapsed = time.time() - start_time
        self._log("=" * 70)
        self._log(f"COMPLETED in {total_elapsed:.1f}s")
        self._log(f"Summary: Total: {total} | Passed: {passed_count} | Failed: {failed_count}")
        self._log("=" * 70)

        self.status_lbl.configure(text=f"Finished! Passed: {passed_count}, Failed: {failed_count}")
        self.run_btn.configure(state=tk.NORMAL)
        self.stop_btn.configure(state=tk.DISABLED)
        self.module_dropdown.configure(state="readonly")
        self.is_running = False

    def _execute_test_process(self, script_name, sheet_name):
        """
        Executes a test file inside its own isolated process.
        Compatible with both standard python running and compiled PyInstaller .exe!
        """
        env = {**os.environ, "PYTHONIOENCODING": "utf-8", "SHEET_NAME": sheet_name}

        if getattr(sys, "frozen", False):
            # When packaged into an EXE: Call itself with --worker-test flag
            cmd = [sys.executable, "--worker-test", script_name, sheet_name]
        else:
            # When running from standard Python source
            cmd = [sys.executable, str(APP_DIR / script_name)]

        try:
            self.current_process = subprocess.Popen(
                cmd,
                cwd=str(APP_DIR),
                env=env,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                encoding="utf-8",
                errors="replace",
                bufsize=1,
            )

            # Stream stdout line-by-line in real time
            for line in self.current_process.stdout:
                clean_line = line.rstrip()
                if clean_line:
                    self._log(f"   {clean_line}")

            self.current_process.wait()
            return self.current_process.returncode == 0
        except Exception as e:
            self._log(f"   Exception during execution: {e}")
            return False
        finally:
            self.current_process = None


# ==============================================================================
# MAIN ENTRY POINT
# ==============================================================================
if __name__ == "__main__":
    # If launched as an isolated test worker process, bypass GUI and execute test
    run_as_worker()

    # Otherwise launch Desktop Application GUI
    app = AutomationRunnerGUI()
    app.mainloop()