"""
Control Panel - GUI for Mixrunner Tool
"""

import tkinter as tk
from tkinter import ttk, scrolledtext, filedialog, messagebox
from pathlib import Path
from typing import Optional
import threading

from ..mixrunner_engine import MixrunnerEngine


class MixreadyControlPanel:
    """
    GUI Control Panel for Mixrunner Engine
    """

    def __init__(self, root: Optional[tk.Tk] = None):
        if root is None:
            self.root = tk.Tk()
            self.root.title("Mixrunner AI - Logic Pro Session Optimizer")
            self.root.geometry("800x900")
        else:
            self.root = root

        self.engine = MixrunnerEngine()
        self.is_connected = False
        self.is_analyzing = False

        self._build_ui()

    def _build_ui(self):
        """Build the user interface"""
        # Style
        style = ttk.Style()
        style.theme_use('clam')

        # Main container
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # Header
        header = ttk.Label(
            main_frame,
            text="Mixrunner AI",
            font=('Helvetica', 24, 'bold')
        )
        header.grid(row=0, column=0, columnspan=2, pady=(0, 10))

        subtitle = ttk.Label(
            main_frame,
            text="Intelligent Logic Pro Session Preparation",
            font=('Helvetica', 12)
        )
        subtitle.grid(row=1, column=0, columnspan=2, pady=(0, 20))

        # Connection Section
        self._build_connection_section(main_frame, row=2)

        # Configuration Section
        self._build_config_section(main_frame, row=3)

        # Actions Section
        self._build_actions_section(main_frame, row=4)

        # Output Log
        self._build_log_section(main_frame, row=5)

        # Status Bar
        self._build_status_bar(main_frame, row=6)

        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(5, weight=1)

    def _build_connection_section(self, parent, row):
        """Build connection controls"""
        frame = ttk.LabelFrame(parent, text="Logic Pro Connection", padding="10")
        frame.grid(row=row, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))

        self.connect_btn = ttk.Button(
            frame,
            text="Connect to Logic Pro",
            command=self._connect_to_logic
        )
        self.connect_btn.grid(row=0, column=0, padx=5)

        self.connection_status = ttk.Label(frame, text="Not Connected", foreground="red")
        self.connection_status.grid(row=0, column=1, padx=10)

    def _build_config_section(self, parent, row):
        """Build configuration options"""
        frame = ttk.LabelFrame(parent, text="Configuration", padding="10")
        frame.grid(row=row, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))

        # Checkboxes for options
        self.var_cleanup = tk.BooleanVar(value=True)
        ttk.Checkbutton(
            frame,
            text="Remove empty tracks",
            variable=self.var_cleanup
        ).grid(row=0, column=0, sticky=tk.W, pady=2)

        self.var_organize = tk.BooleanVar(value=True)
        ttk.Checkbutton(
            frame,
            text="Auto-organize tracks",
            variable=self.var_organize
        ).grid(row=1, column=0, sticky=tk.W, pady=2)

        self.var_color = tk.BooleanVar(value=True)
        ttk.Checkbutton(
            frame,
            text="Apply color scheme",
            variable=self.var_color
        ).grid(row=2, column=0, sticky=tk.W, pady=2)

        self.var_normalize = tk.BooleanVar(value=True)
        ttk.Checkbutton(
            frame,
            text="Normalize audio levels",
            variable=self.var_normalize
        ).grid(row=3, column=0, sticky=tk.W, pady=2)

        # Target levels
        ttk.Label(frame, text="Target LUFS:").grid(row=0, column=1, padx=(20, 5))
        self.lufs_entry = ttk.Entry(frame, width=8)
        self.lufs_entry.insert(0, "-18.0")
        self.lufs_entry.grid(row=0, column=2)

        ttk.Label(frame, text="Target Peak (dB):").grid(row=1, column=1, padx=(20, 5))
        self.peak_entry = ttk.Entry(frame, width=8)
        self.peak_entry.insert(0, "-6.0")
        self.peak_entry.grid(row=1, column=2)

    def _build_actions_section(self, parent, row):
        """Build action buttons"""
        frame = ttk.LabelFrame(parent, text="Actions", padding="10")
        frame.grid(row=row, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))

        # Row 1
        ttk.Button(
            frame,
            text="Analyze Session",
            command=self._analyze_session
        ).grid(row=0, column=0, padx=5, pady=5, sticky=(tk.W, tk.E))

        ttk.Button(
            frame,
            text="Clean Up",
            command=self._cleanup_session
        ).grid(row=0, column=1, padx=5, pady=5, sticky=(tk.W, tk.E))

        ttk.Button(
            frame,
            text="Organize Tracks",
            command=self._organize_tracks
        ).grid(row=0, column=2, padx=5, pady=5, sticky=(tk.W, tk.E))

        # Row 2
        ttk.Button(
            frame,
            text="Normalize Audio",
            command=self._normalize_audio
        ).grid(row=1, column=0, padx=5, pady=5, sticky=(tk.W, tk.E))

        ttk.Button(
            frame,
            text="Full Workflow",
            command=self._run_full_workflow,
            style="Accent.TButton"
        ).grid(row=1, column=1, padx=5, pady=5, sticky=(tk.W, tk.E))

        ttk.Button(
            frame,
            text="Generate Report",
            command=self._generate_report
        ).grid(row=1, column=2, padx=5, pady=5, sticky=(tk.W, tk.E))

        # Configure column weights
        for i in range(3):
            frame.columnconfigure(i, weight=1)

    def _build_log_section(self, parent, row):
        """Build output log"""
        frame = ttk.LabelFrame(parent, text="Output Log", padding="10")
        frame.grid(row=row, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))

        self.log_text = scrolledtext.ScrolledText(
            frame,
            wrap=tk.WORD,
            height=20,
            font=('Courier', 9)
        )
        self.log_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        frame.columnconfigure(0, weight=1)
        frame.rowconfigure(0, weight=1)

    def _build_status_bar(self, parent, row):
        """Build status bar"""
        self.status_bar = ttk.Label(
            parent,
            text="Ready",
            relief=tk.SUNKEN,
            anchor=tk.W
        )
        self.status_bar.grid(row=row, column=0, columnspan=2, sticky=(tk.W, tk.E))

    def _log(self, message: str):
        """Add message to log"""
        self.log_text.insert(tk.END, message + "\n")
        self.log_text.see(tk.END)
        self.root.update_idletasks()

    def _update_status(self, message: str):
        """Update status bar"""
        self.status_bar.config(text=message)
        self.root.update_idletasks()

    def _connect_to_logic(self):
        """Connect to Logic Pro"""
        self._update_status("Connecting to Logic Pro...")
        self._log("Connecting to Logic Pro...")

        success = self.engine.connect_to_logic()

        if success:
            self.is_connected = True
            self.connection_status.config(text="Connected", foreground="green")
            self._log("✓ Connected to Logic Pro")
            self._update_status("Connected")
        else:
            self.connection_status.config(text="Failed", foreground="red")
            self._log("✗ Failed to connect to Logic Pro")
            self._update_status("Connection failed")
            messagebox.showerror("Connection Error", "Could not connect to Logic Pro. Is it running?")

    def _analyze_session(self):
        """Analyze current session"""
        if not self.is_connected:
            messagebox.showwarning("Not Connected", "Please connect to Logic Pro first")
            return

        def analyze():
            self._update_status("Analyzing session...")
            self._log("\n" + "=" * 60)
            self._log("Starting session analysis...")

            self._update_config()
            results = self.engine.analyze_session()

            if results:
                self._log("✓ Analysis complete")
                report = self.engine.generate_report()
                self._log("\n" + report)
            else:
                self._log("✗ Analysis failed")

            self._update_status("Ready")

        threading.Thread(target=analyze, daemon=True).start()

    def _cleanup_session(self):
        """Clean up session"""
        if not self.is_connected:
            messagebox.showwarning("Not Connected", "Please connect to Logic Pro first")
            return

        def cleanup():
            self._update_status("Cleaning up session...")
            self._log("\nCleaning up session...")

            success = self.engine.apply_cleanup()

            if success:
                self._log("✓ Cleanup complete")
            else:
                self._log("✗ Cleanup failed")

            self._update_status("Ready")

        threading.Thread(target=cleanup, daemon=True).start()

    def _organize_tracks(self):
        """Organize tracks"""
        if not self.is_connected:
            messagebox.showwarning("Not Connected", "Please connect to Logic Pro first")
            return

        def organize():
            self._update_status("Organizing tracks...")
            self._log("\nOrganizing tracks...")

            success = self.engine.organize_tracks()

            if success:
                self._log("✓ Track organization complete")
            else:
                self._log("✗ Track organization failed")

            self._update_status("Ready")

        threading.Thread(target=organize, daemon=True).start()

    def _normalize_audio(self):
        """Normalize audio"""
        if not self.is_connected:
            messagebox.showwarning("Not Connected", "Please connect to Logic Pro first")
            return

        def normalize():
            self._update_status("Normalizing audio...")
            self._log("\nNormalizing audio...")

            success = self.engine.normalize_technical()

            if success:
                self._log("✓ Normalization complete")
            else:
                self._log("✗ Normalization failed")

            self._update_status("Ready")

        threading.Thread(target=normalize, daemon=True).start()

    def _run_full_workflow(self):
        """Run complete workflow"""
        if not self.is_connected:
            messagebox.showwarning("Not Connected", "Please connect to Logic Pro first")
            return

        response = messagebox.askyesno(
            "Run Full Workflow",
            "This will analyze and optimize your session. Continue?"
        )

        if not response:
            return

        def workflow():
            self._update_status("Running full workflow...")
            self._log("\n" + "=" * 60)
            self._log("STARTING FULL WORKFLOW")
            self._log("=" * 60)

            self._update_config()
            success = self.engine.run_full_workflow()

            if success:
                self._log("\n" + "=" * 60)
                self._log("✓ WORKFLOW COMPLETE!")
                self._log("=" * 60)
                messagebox.showinfo("Success", "Mix preparation complete!")
            else:
                self._log("✗ Workflow failed")
                messagebox.showerror("Error", "Workflow failed. Check log for details.")

            self._update_status("Ready")

        threading.Thread(target=workflow, daemon=True).start()

    def _generate_report(self):
        """Generate and display report"""
        report = self.engine.generate_report()
        self._log("\n" + report)

    def _update_config(self):
        """Update engine configuration from UI"""
        self.engine.config.update({
            'remove_empty_tracks': self.var_cleanup.get(),
            'auto_organize': self.var_organize.get(),
            'auto_color_tracks': self.var_color.get(),
            'normalize_audio': self.var_normalize.get(),
            'target_lufs': float(self.lufs_entry.get()),
            'target_peak': float(self.peak_entry.get()),
        })

    def run(self):
        """Start the GUI"""
        self.root.mainloop()


def main():
    """Entry point for GUI"""
    app = MixReadinessControlPanel()
    app.run()


if __name__ == '__main__':
    main()
