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
            self.root.title("Mixrunner AI - Ableton Live Session Optimizer")
            self.root.geometry("900x950")
        else:
            self.root = root

        # Modern color scheme
        self.colors = {
            'bg_dark': '#1e1e1e',
            'bg_medium': '#2d2d2d',
            'bg_light': '#3c3c3c',
            'accent': '#0d7fc9',
            'accent_hover': '#0a5f96',
            'success': '#4caf50',
            'warning': '#ff9800',
            'error': '#f44336',
            'text': '#ffffff',
            'text_dim': '#b0b0b0',
            'border': '#4a4a4a'
        }

        self.root.configure(bg=self.colors['bg_dark'])

        self.engine = MixrunnerEngine()
        self.is_connected = False
        self.is_analyzing = False

        self._build_ui()

    def _build_ui(self):
        """Build the user interface"""
        # Modern Style Configuration
        style = ttk.Style()
        style.theme_use('clam')

        # Configure modern dark theme
        style.configure('.',
            background=self.colors['bg_dark'],
            foreground=self.colors['text'],
            fieldbackground=self.colors['bg_medium'],
            borderwidth=0
        )

        style.configure('TFrame',
            background=self.colors['bg_dark']
        )

        style.configure('TLabel',
            background=self.colors['bg_dark'],
            foreground=self.colors['text']
        )

        style.configure('TLabelframe',
            background=self.colors['bg_dark'],
            foreground=self.colors['text'],
            borderwidth=1,
            relief='solid'
        )

        style.configure('TLabelframe.Label',
            background=self.colors['bg_dark'],
            foreground=self.colors['accent'],
            font=('Helvetica', 11, 'bold')
        )

        style.configure('TButton',
            background=self.colors['bg_light'],
            foreground=self.colors['text'],
            borderwidth=1,
            relief='flat',
            padding=(15, 8)
        )

        style.map('TButton',
            background=[('active', self.colors['accent'])],
            foreground=[('active', self.colors['text'])]
        )

        style.configure('Accent.TButton',
            background=self.colors['accent'],
            foreground=self.colors['text'],
            font=('Helvetica', 10, 'bold')
        )

        style.map('Accent.TButton',
            background=[('active', self.colors['accent_hover'])]
        )

        style.configure('TCheckbutton',
            background=self.colors['bg_dark'],
            foreground=self.colors['text']
        )

        style.configure('TEntry',
            fieldbackground=self.colors['bg_medium'],
            foreground=self.colors['text'],
            insertcolor=self.colors['text']
        )

        # Main container with padding
        main_frame = tk.Frame(self.root, bg=self.colors['bg_dark'], padx=20, pady=20)
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # Modern Header with gradient effect
        header_frame = tk.Frame(main_frame, bg=self.colors['bg_medium'], height=100)
        header_frame.grid(row=0, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 20))
        header_frame.grid_propagate(False)

        header = tk.Label(
            header_frame,
            text="MIXRUNNER AI",
            font=('Helvetica', 32, 'bold'),
            bg=self.colors['bg_medium'],
            fg=self.colors['accent']
        )
        header.pack(pady=(15, 0))

        subtitle = tk.Label(
            header_frame,
            text="Intelligent Ableton Live Session Optimizer",
            font=('Helvetica', 13),
            bg=self.colors['bg_medium'],
            fg=self.colors['text_dim']
        )
        subtitle.pack(pady=(0, 10))

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
        frame = ttk.LabelFrame(parent, text="  ABLETON LIVE CONNECTION  ", padding="15")
        frame.grid(row=row, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 15))

        self.connect_btn = ttk.Button(
            frame,
            text="⚡ Connect to Ableton Live",
            command=self._connect_to_logic,
            width=25
        )
        self.connect_btn.grid(row=0, column=0, padx=5)

        # Status indicator with colored dot
        status_frame = tk.Frame(frame, bg=self.colors['bg_dark'])
        status_frame.grid(row=0, column=1, padx=20, sticky=tk.W)

        self.status_dot = tk.Label(
            status_frame,
            text="●",
            font=('Helvetica', 16),
            bg=self.colors['bg_dark'],
            fg=self.colors['error']
        )
        self.status_dot.pack(side=tk.LEFT, padx=(0, 8))

        self.connection_status = tk.Label(
            status_frame,
            text="Not Connected",
            font=('Helvetica', 11),
            bg=self.colors['bg_dark'],
            fg=self.colors['error']
        )
        self.connection_status.pack(side=tk.LEFT)

    def _build_config_section(self, parent, row):
        """Build configuration options"""
        frame = ttk.LabelFrame(parent, text="  CONFIGURATION  ", padding="15")
        frame.grid(row=row, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 15))

        # Left column - Checkboxes
        left_frame = tk.Frame(frame, bg=self.colors['bg_dark'])
        left_frame.grid(row=0, column=0, sticky=(tk.W, tk.N), padx=(0, 30))

        self.var_cleanup = tk.BooleanVar(value=True)
        ttk.Checkbutton(
            left_frame,
            text="✓ Remove empty tracks",
            variable=self.var_cleanup
        ).grid(row=0, column=0, sticky=tk.W, pady=5)

        self.var_organize = tk.BooleanVar(value=True)
        ttk.Checkbutton(
            left_frame,
            text="✓ Auto-organize tracks",
            variable=self.var_organize
        ).grid(row=1, column=0, sticky=tk.W, pady=5)

        self.var_color = tk.BooleanVar(value=True)
        ttk.Checkbutton(
            left_frame,
            text="✓ Apply color scheme",
            variable=self.var_color
        ).grid(row=2, column=0, sticky=tk.W, pady=5)

        self.var_normalize = tk.BooleanVar(value=True)
        ttk.Checkbutton(
            left_frame,
            text="✓ Normalize audio levels",
            variable=self.var_normalize
        ).grid(row=3, column=0, sticky=tk.W, pady=5)

        # Right column - Target levels
        right_frame = tk.Frame(frame, bg=self.colors['bg_dark'])
        right_frame.grid(row=0, column=1, sticky=(tk.W, tk.N))

        tk.Label(
            right_frame,
            text="Target LUFS:",
            font=('Helvetica', 10),
            bg=self.colors['bg_dark'],
            fg=self.colors['text_dim']
        ).grid(row=0, column=0, sticky=tk.W, pady=5)

        self.lufs_entry = ttk.Entry(right_frame, width=10, font=('Helvetica', 10))
        self.lufs_entry.insert(0, "-18.0")
        self.lufs_entry.grid(row=0, column=1, padx=(10, 0), pady=5)

        tk.Label(
            right_frame,
            text="Target Peak (dB):",
            font=('Helvetica', 10),
            bg=self.colors['bg_dark'],
            fg=self.colors['text_dim']
        ).grid(row=1, column=0, sticky=tk.W, pady=5)

        self.peak_entry = ttk.Entry(right_frame, width=10, font=('Helvetica', 10))
        self.peak_entry.insert(0, "-6.0")
        self.peak_entry.grid(row=1, column=1, padx=(10, 0), pady=5)

    def _build_actions_section(self, parent, row):
        """Build action buttons"""
        frame = ttk.LabelFrame(parent, text="  ACTIONS  ", padding="15")
        frame.grid(row=row, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 15))

        # Row 1 - Primary actions
        ttk.Button(
            frame,
            text="📊 Analyze Session",
            command=self._analyze_session
        ).grid(row=0, column=0, padx=5, pady=5, sticky=(tk.W, tk.E))

        ttk.Button(
            frame,
            text="🧹 Clean Up",
            command=self._cleanup_session
        ).grid(row=0, column=1, padx=5, pady=5, sticky=(tk.W, tk.E))

        ttk.Button(
            frame,
            text="📁 Organize Tracks",
            command=self._organize_tracks
        ).grid(row=0, column=2, padx=5, pady=5, sticky=(tk.W, tk.E))

        # Row 2 - Secondary actions
        ttk.Button(
            frame,
            text="🎚️ Normalize Audio",
            command=self._normalize_audio
        ).grid(row=1, column=0, padx=5, pady=5, sticky=(tk.W, tk.E))

        ttk.Button(
            frame,
            text="📄 Generate Report",
            command=self._generate_report
        ).grid(row=1, column=1, padx=5, pady=5, sticky=(tk.W, tk.E))

        # Row 3 - Full workflow (prominent)
        ttk.Button(
            frame,
            text="🚀 RUN FULL WORKFLOW",
            command=self._run_full_workflow,
            style="Accent.TButton"
        ).grid(row=2, column=0, columnspan=3, padx=5, pady=(10, 5), sticky=(tk.W, tk.E))

        # Configure column weights
        for i in range(3):
            frame.columnconfigure(i, weight=1)

    def _build_log_section(self, parent, row):
        """Build output log"""
        frame = ttk.LabelFrame(parent, text="  OUTPUT LOG  ", padding="15")
        frame.grid(row=row, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 15))

        self.log_text = scrolledtext.ScrolledText(
            frame,
            wrap=tk.WORD,
            height=20,
            font=('Consolas', 10),
            bg=self.colors['bg_medium'],
            fg=self.colors['text'],
            insertbackground=self.colors['accent'],
            selectbackground=self.colors['accent'],
            selectforeground=self.colors['text'],
            borderwidth=0,
            highlightthickness=1,
            highlightbackground=self.colors['border'],
            highlightcolor=self.colors['accent']
        )
        self.log_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        frame.columnconfigure(0, weight=1)
        frame.rowconfigure(0, weight=1)

    def _build_status_bar(self, parent, row):
        """Build status bar"""
        status_frame = tk.Frame(parent, bg=self.colors['bg_medium'], height=35)
        status_frame.grid(row=row, column=0, columnspan=2, sticky=(tk.W, tk.E))
        status_frame.grid_propagate(False)

        self.status_bar = tk.Label(
            status_frame,
            text="Ready",
            bg=self.colors['bg_medium'],
            fg=self.colors['text_dim'],
            font=('Helvetica', 10),
            anchor=tk.W,
            padx=10
        )
        self.status_bar.pack(fill=tk.BOTH, expand=True, side=tk.LEFT)

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
        """Connect to Ableton Live"""
        self._update_status("Connecting to Ableton Live...")
        self._log("Connecting to Ableton Live...")
        self._log("Make sure Ableton Live is running with the MIDI Remote Script installed...")

        success = self.engine.connect_to_logic()

        if success:
            self.is_connected = True
            self.status_dot.config(fg=self.colors['success'])
            self.connection_status.config(
                text="Connected",
                fg=self.colors['success']
            )
            self._log("✓ Connected to Ableton Live")
            self._update_status("Connected")
        else:
            self.status_dot.config(fg=self.colors['error'])
            self.connection_status.config(
                text="Connection Failed",
                fg=self.colors['error']
            )
            self._log("✗ Failed to connect to Ableton Live")
            self._update_status("Connection failed")
            messagebox.showerror("Connection Error", "Could not connect to Ableton Live. Is it running with the MIDI Remote Script?")

    def _analyze_session(self):
        """Analyze current session"""
        if not self.is_connected:
            messagebox.showwarning("Not Connected", "Please connect to Ableton Live first")
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
            messagebox.showwarning("Not Connected", "Please connect to Ableton Live first")
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
            messagebox.showwarning("Not Connected", "Please connect to Ableton Live first")
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
            messagebox.showwarning("Not Connected", "Please connect to Ableton Live first")
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
            messagebox.showwarning("Not Connected", "Please connect to Ableton Live first")
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
