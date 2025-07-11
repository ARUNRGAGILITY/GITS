#!/usr/bin/env python3
"""
Git Python GUI - A comprehensive Git frontend similar to Simple VCS
Usage: python git_python_gui.py [repository_path]
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog, simpledialog
import os
import sys
import subprocess
import threading
from pathlib import Path
import git
from datetime import datetime
import webbrowser
import tempfile
import threading
import platform
import shutil


class GitPythonGUI:
    def __init__(self, root, repo_path=None):
        self.root = root
        self.root.title("Git Python GUI - VCS Style")
        self.root.geometry("1400x900")
        self.root.configure(bg='#f0f0f0')
        
        # Initialize variables
        self.repo = None
        self.repo_path = repo_path or os.getcwd()
        self.current_branch = None
        self.status_operations = []
        self.file_status_cache = {}  # Cache for file status
        self.highlighted_files = set()  # Track highlighted files for auto-clear
        
        # Try to initialize repository
        self.init_repository()
        
        # Create UI components
        self.setup_custom_styles()
        self.create_menu_bar()
        self.create_enhanced_toolbar()
        self.create_main_layout()
        self.create_status_bar()
        
        # Load initial data
        self.refresh_all()
        self.setup_enhanced_refresh_cycle()
        
        # Auto-clear highlights after 5 seconds
        self.schedule_highlight_clear()
    
    def setup_custom_styles(self):
        """Setup custom button styles"""
        style = ttk.Style()
        
        # Configure custom button styles with better visibility
        style.configure('Success.TButton', 
                       foreground='#28a745',  # Bootstrap green
                       font=('TkDefaultFont', 10, 'bold'))
        style.configure('Info.TButton', 
                       foreground='#007bff',  # Bootstrap blue
                       font=('TkDefaultFont', 10, 'bold'))
        style.configure('Warning.TButton', 
                       foreground='#fd7e14',  # Bootstrap orange
                       font=('TkDefaultFont', 10, 'bold'))
        style.configure('Secondary.TButton', 
                       foreground='#6c757d',  # Bootstrap gray
                       font=('TkDefaultFont', 10, 'bold'))
        style.configure('Accent.TButton', 
                       foreground='#6f42c1',  # Bootstrap purple
                       font=('TkDefaultFont', 10, 'bold'))
        style.configure('Operating.TButton', 
                       background='#ffc107',  # Bootstrap warning yellow
                       foreground='#212529',  # Dark text
                       font=('TkDefaultFont', 10, 'bold'))
        
    
    def get_file_icon(self, file_path, file_status='CLEAN'):
        """Get appropriate icon for file type and status"""
        if os.path.isdir(file_path):
            if file_status == 'NEW':
                return '📁🔴'  # New folder - red indicator
            elif file_status == 'MODIFIED':
                return '📁🟠'  # Modified folder - orange indicator
            elif file_status == 'STAGED':
                return '📁🟢'  # Staged folder - green indicator
            else:
                return '📁'  # Clean folder
        
        # Get file extension
        _, ext = os.path.splitext(file_path)
        ext = ext.lower()
        
        # Status indicators
        status_indicator = ''
        if file_status == 'NEW':
            status_indicator = '🔴'
        elif file_status == 'MODIFIED':
            status_indicator = '🟠'
        elif file_status == 'STAGED':
            status_indicator = '🟢'
        elif file_status == 'MODIFIED_STAGED':
            status_indicator = '🔵'
        
        # File type icons
        if ext in ['.py', '.pyx', '.pyi']:
            return f'🐍{status_indicator}'  # Python files
        elif ext in ['.js', '.jsx', '.ts', '.tsx']:
            return f'🟨{status_indicator}'  # JavaScript/TypeScript files
        elif ext in ['.html', '.htm']:
            return f'🌐{status_indicator}'  # HTML files
        elif ext in ['.css', '.scss', '.sass']:
            return f'🎨{status_indicator}'  # CSS files
        elif ext in ['.json', '.yaml', '.yml', '.xml']:
            return f'⚙️{status_indicator}'  # Config files
        elif ext in ['.md', '.txt', '.rst']:
            return f'📝{status_indicator}'  # Text files
        elif ext in ['.jpg', '.jpeg', '.png', '.gif', '.svg', '.bmp']:
            return f'🖼️{status_indicator}'  # Image files
        elif ext in ['.pdf']:
            return f'📄{status_indicator}'  # PDF files
        elif ext in ['.zip', '.rar', '.7z', '.tar', '.gz']:
            return f'🗜️{status_indicator}'  # Archive files
        elif ext in ['.exe', '.dll', '.so', '.dylib']:
            return f'⚙️{status_indicator}'  # Binary files
        elif ext in ['.sh', '.bat', '.cmd']:
            return f'⚡{status_indicator}'  # Script files
        elif ext in ['.sql']:
            return f'🗃️{status_indicator}'  # Database files
        elif ext in ['.log']:
            return f'📋{status_indicator}'  # Log files
        elif ext in ['.csv', '.xlsx', '.xls']:
            return f'📊{status_indicator}'  # Spreadsheet files
        elif ext == '':
            # No extension - check if binary
            try:
                with open(file_path, 'rb') as f:
                    chunk = f.read(1024)
                    if b'\0' in chunk:
                        return f'⚙️{status_indicator}'  # Binary file
                    else:
                        return f'📝{status_indicator}'  # Text file
            except:
                return f'📄{status_indicator}'  # Default file
        else:
            return f'📄{status_indicator}'  # Default file icon
        
    def init_repository(self):
        """Initialize Git repository"""
        try:
            # Check if current path is a git repo or find parent git repo
            current_path = Path(self.repo_path).resolve()
            
            while current_path != current_path.parent:
                if (current_path / '.git').exists():
                    self.repo_path = str(current_path)
                    self.repo = git.Repo(self.repo_path)
                    return
                current_path = current_path.parent
            
            # If no git repo found, ask user to select one
            if not self.repo:
                result = messagebox.askyesno(
                    "No Git Repository", 
                    "No Git repository found. Would you like to select a repository folder?"
                )
                if result:
                    self.select_repository()
                    
        except Exception as e:
            messagebox.showerror("Repository Error", f"Error initializing repository: {str(e)}")
    
    def select_repository(self):
        """Select a repository folder"""
        folder = filedialog.askdirectory(title="Select Git Repository Folder")
        if folder:
            try:
                self.repo_path = folder
                self.repo = git.Repo(folder)
                self.refresh_all()
            except git.exc.InvalidGitRepositoryError:
                messagebox.showerror("Invalid Repository", "Selected folder is not a Git repository")
    
    def create_menu_bar(self):
        """Create menu bar - MODIFIED VERSION"""
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        
        # File menu
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="Open Repository...", command=self.select_repository)
        file_menu.add_command(label="Clone Repository...", command=self.clone_repository)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.root.quit)
        
        # Repository menu
        repo_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Repository", menu=repo_menu)
        repo_menu.add_command(label="Pull", command=self.git_pull)
        repo_menu.add_command(label="Push", command=self.git_push)
        repo_menu.add_command(label="Fetch", command=self.git_fetch)
        repo_menu.add_separator()
        repo_menu.add_command(label="Create Branch...", command=self.create_branch)
        repo_menu.add_command(label="Switch Branch...", command=self.switch_branch)
        repo_menu.add_separator()
        repo_menu.add_command(label="Create Tag...", command=self.create_tag)
        repo_menu.add_command(label="Switch to Tag...", command=self.switch_to_tag_only)
        repo_menu.add_command(label="Manage Tags...", command=self.manage_tags_enhanced)
        repo_menu.add_command(label="Rename Tag...", command=self.show_rename_tag_dialog)  # NEW
        
        # History menu
        history_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="History", menu=history_menu)
        history_menu.add_command(label="Version History (List)", command=self.show_version_history)
        history_menu.add_command(label="Version History (Graph)", command=self.show_version_graph)
        history_menu.add_command(label="Timeline View (Vertical)", command=self.show_vertical_timeline)
        history_menu.add_command(label="Tags & Branches", command=self.show_tags_branches)
        history_menu.add_command(label="Commit Details", command=self.show_commit_details)
        history_menu.add_separator()
        history_menu.add_command(label="Edit Commit Message", command=self.edit_commit_message)  # ENHANCED
        
        # View menu
        view_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="View", menu=view_menu)
        view_menu.add_command(label="Refresh All", command=self.refresh_all)
        view_menu.add_command(label="Show Log", command=self.show_log)
        
        # Help menu
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Help", menu=help_menu)
        help_menu.add_command(label="About", command=self.show_about)
    
     
    def create_main_layout(self):
        """Create main layout with panes"""
        # Main container
        main_container = ttk.Frame(self.root)
        main_container.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Create horizontal paned window
        h_paned = ttk.PanedWindow(main_container, orient=tk.HORIZONTAL)
        h_paned.pack(fill=tk.BOTH, expand=True)
        
        # Left sidebar (repository tree)
        left_frame = ttk.Frame(h_paned, width=300)
        self.create_repository_tree(left_frame)
        h_paned.add(left_frame, weight=1)
        
        # Right side - vertical paned window
        v_paned = ttk.PanedWindow(h_paned, orient=tk.VERTICAL)
        h_paned.add(v_paned, weight=3)
        
        # Top right - file contents and staging area
        top_right = ttk.Frame(v_paned)
        self.create_file_view(top_right)
        v_paned.add(top_right, weight=2)
        
        # Bottom right - modifications and staging
        bottom_right = ttk.Frame(v_paned)
        self.create_changes_view(bottom_right)
        v_paned.add(bottom_right, weight=1)
    
    def create_repository_tree(self, parent):
        """Create repository tree view with action icons"""
        # Repository Tree with action icons
        tree_header_frame = ttk.Frame(parent)
        tree_header_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Label(tree_header_frame, text="Repository Tree", font=('TkDefaultFont', 10, 'bold')).pack(side=tk.LEFT)
        
        # Action icons frame
        icons_frame = ttk.Frame(tree_header_frame)
        icons_frame.pack(side=tk.RIGHT)
        
        # Create/View Branch icons with better styling
        branch_create_btn = ttk.Button(icons_frame, text="🌿+", command=self.create_branch, 
                                      width=5, style='Success.TButton')
        branch_create_btn.pack(side=tk.LEFT, padx=1)
        
        branch_switch_btn = ttk.Button(icons_frame, text="🌿", command=self.switch_branch, 
                                      width=5, style='Info.TButton')
        branch_switch_btn.pack(side=tk.LEFT, padx=1)
        
        # Create/View Tag icons with better styling
        tag_create_btn = ttk.Button(icons_frame, text="🏷️+", command=self.create_tag, 
                                   width=5, style='Warning.TButton')
        tag_create_btn.pack(side=tk.LEFT, padx=1)
        
        tag_manage_btn = ttk.Button(icons_frame, text="🏷️", command=self.manage_tags_enhanced, 
                                   width=5, style='Secondary.TButton')
        tag_manage_btn.pack(side=tk.LEFT, padx=1)
        
        # Refresh icon with better styling
        refresh_btn = ttk.Button(icons_frame, text="🔄", command=self.refresh_all, 
                                width=5, style='Accent.TButton')
        refresh_btn.pack(side=tk.LEFT, padx=1)
        
        # Add tooltips for better UX
        self.create_tooltip(branch_create_btn, "Create new branch")
        self.create_tooltip(branch_switch_btn, "Switch branch")
        self.create_tooltip(tag_create_btn, "Create new tag")
        self.create_tooltip(tag_manage_btn, "View and manage tags")
        self.create_tooltip(refresh_btn, "Refresh repository")
        
        # Tree frame
        tree_frame = ttk.Frame(parent)
        tree_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Treeview with scrollbar
        self.repo_tree = ttk.Treeview(tree_frame, selectmode='browse')
        tree_scrollbar = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL, command=self.repo_tree.yview)
        self.repo_tree.configure(yscrollcommand=tree_scrollbar.set)
        
        self.repo_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        tree_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Bind events
        self.repo_tree.bind('<<TreeviewSelect>>', self.on_tree_select)
    
    def create_file_view(self, parent):
        """Create file view with version information"""
        # Notebook for different views
        notebook = ttk.Notebook(parent)
        notebook.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # File view tab
        file_frame = ttk.Frame(notebook)
        notebook.add(file_frame, text="Files")
        
        # File list with columns
        columns = ('Name', 'Type', 'Size', 'Modified', 'Branch', 'Version', 'Author', 'Commit', 'Commit Date')
        self.file_tree = ttk.Treeview(file_frame, columns=columns, show='tree headings')
        
        # Configure columns
        self.file_tree.heading('#0', text='', anchor=tk.W)
        self.file_tree.column('#0', width=30, minwidth=30)
        
        # Make columns sortable
        for col in columns:
            self.file_tree.heading(col, text=col, anchor=tk.W, command=lambda c=col: self.sort_files_by_column(c))
            self.file_tree.column(col, width=100, minwidth=50)
        
        # Scrollbars for file tree
        file_v_scroll = ttk.Scrollbar(file_frame, orient=tk.VERTICAL, command=self.file_tree.yview)
        file_h_scroll = ttk.Scrollbar(file_frame, orient=tk.HORIZONTAL, command=self.file_tree.xview)
        self.file_tree.configure(yscrollcommand=file_v_scroll.set, xscrollcommand=file_h_scroll.set)
        
        self.file_tree.grid(row=0, column=0, sticky='nsew')
        file_v_scroll.grid(row=0, column=1, sticky='ns')
        file_h_scroll.grid(row=1, column=0, sticky='ew')
        
        file_frame.grid_rowconfigure(0, weight=1)
        file_frame.grid_columnconfigure(0, weight=1)
        
        # Context menu for files
        self.file_context_menu = tk.Menu(self.root, tearoff=0)
        self.file_context_menu.add_command(label="Open in VS Code", command=self.open_in_vscode)
        self.file_context_menu.add_command(label="Add to Git", command=self.add_selected_file)
        self.file_context_menu.add_separator()
        self.file_context_menu.add_command(label="View History", command=self.view_file_history)
        self.file_context_menu.add_command(label="Version Timeline", command=self.view_version_timeline)
        self.file_context_menu.add_command(label="Compare with HEAD", command=self.compare_with_head)
        self.file_context_menu.add_command(label="Blame/Annotate", command=self.show_file_blame)
        self.file_context_menu.add_separator()
        self.file_context_menu.add_command(label="View at Commit", command=self.view_file_at_commit)
        self.file_context_menu.add_command(label="Revert to Version", command=self.revert_file_to_version)
        
        self.file_tree.bind('<Button-3>', self.show_file_context_menu)
        self.file_tree.bind('<Double-1>', self.open_file)
    
    def create_changes_view(self, parent):
        """Create changes view for staging and modifications"""
        notebook = ttk.Notebook(parent)
        notebook.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Modified files tab
        modified_frame = ttk.Frame(notebook)
        notebook.add(modified_frame, text="Modified Files")
        
        self.modified_tree = ttk.Treeview(modified_frame, columns=('Status', 'File'), show='headings')
        self.modified_tree.heading('Status', text='Status')
        self.modified_tree.heading('File', text='File')
        self.modified_tree.column('Status', width=80)
        self.modified_tree.column('File', width=300)
        
        modified_scroll = ttk.Scrollbar(modified_frame, orient=tk.VERTICAL, command=self.modified_tree.yview)
        self.modified_tree.configure(yscrollcommand=modified_scroll.set)
        
        self.modified_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        modified_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Staging area tab
        staging_frame = ttk.Frame(notebook)
        notebook.add(staging_frame, text="Staging Area")
        
        self.staging_tree = ttk.Treeview(staging_frame, columns=('File', 'Status'), show='headings')
        self.staging_tree.heading('File', text='File')
        self.staging_tree.heading('Status', text='Status')
        
        staging_scroll = ttk.Scrollbar(staging_frame, orient=tk.VERTICAL, command=self.staging_tree.yview)
        self.staging_tree.configure(yscrollcommand=staging_scroll.set)
        
        self.staging_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        staging_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Bind events
        self.modified_tree.bind('<Double-1>', self.stage_file)
        self.staging_tree.bind('<Double-1>', self.unstage_file)
    
    def create_status_bar(self):
        """Create status bar"""
        status_frame = ttk.Frame(self.root)
        status_frame.pack(side=tk.BOTTOM, fill=tk.X)
        
        # Status label
        self.status_label = ttk.Label(status_frame, text="Ready", relief=tk.SUNKEN, anchor=tk.W)
        self.status_label.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=2, pady=2)
        
        # Operations in progress
        self.operations_label = ttk.Label(status_frame, text="", relief=tk.SUNKEN, anchor=tk.E)
        self.operations_label.pack(side=tk.RIGHT, padx=2, pady=2)
        
        # Connection status
        self.connection_label = ttk.Label(status_frame, text="", relief=tk.SUNKEN)
        self.connection_label.pack(side=tk.RIGHT, padx=2, pady=2)
    
    def manage_tags_enhanced(self):
        """Enhanced tag management with comprehensive information and details"""
        if not self.repo:
            messagebox.showerror("Error", "No repository loaded")
            return
        
        tags_window = tk.Toplevel(self.root)
        tags_window.title("Tag Management - Comprehensive View")
        tags_window.geometry("1600x900")
        
        # Create main paned window (horizontal)
        main_paned = ttk.PanedWindow(tags_window, orient=tk.HORIZONTAL)
        main_paned.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # LEFT PANE - Tags List
        left_frame = ttk.Frame(main_paned)
        main_paned.add(left_frame, weight=1)
        
        # Tags header with actions
        tags_header = ttk.Frame(left_frame)
        tags_header.pack(fill=tk.X, pady=5)
        
        ttk.Label(tags_header, text="Tags", font=('TkDefaultFont', 12, 'bold')).pack(side=tk.LEFT)
        
        # Quick actions for tags
        actions_frame = ttk.Frame(tags_header)
        actions_frame.pack(side=tk.RIGHT)
        
        ttk.Button(actions_frame, text="Create Tag", command=self.create_tag, 
                  style='Success.TButton').pack(side=tk.LEFT, padx=2)
        ttk.Button(actions_frame, text="Push Tags", command=self.push_all_tags, 
                  style='Info.TButton').pack(side=tk.LEFT, padx=2)
        ttk.Button(actions_frame, text="Refresh", command=lambda: self.refresh_tags_list(tags_tree), 
                  style='Accent.TButton').pack(side=tk.LEFT, padx=2)
        
        # Tags tree with comprehensive columns
        tags_frame = ttk.Frame(left_frame)
        tags_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        
        tags_columns = ('Tag Name', 'Type', 'Commit Hash', 'Date', 'Author', 'Remote Status')
        tags_tree = ttk.Treeview(tags_frame, columns=tags_columns, show='headings', height=20)
        
        # Configure tag columns
        tags_tree.heading('Tag Name', text='Tag Name')
        tags_tree.column('Tag Name', width=150, minwidth=100)
        
        tags_tree.heading('Type', text='Type')
        tags_tree.column('Type', width=80, minwidth=60)
        
        tags_tree.heading('Commit Hash', text='Commit Hash')
        tags_tree.column('Commit Hash', width=100, minwidth=80)
        
        tags_tree.heading('Date', text='Date')
        tags_tree.column('Date', width=120, minwidth=100)
        
        tags_tree.heading('Author', text='Author')
        tags_tree.column('Author', width=120, minwidth=100)
        
        tags_tree.heading('Remote Status', text='Remote Status')
        tags_tree.column('Remote Status', width=100, minwidth=80)
        
        # Scrollbars for tags tree
        tags_v_scroll = ttk.Scrollbar(tags_frame, orient=tk.VERTICAL, command=tags_tree.yview)
        tags_h_scroll = ttk.Scrollbar(tags_frame, orient=tk.HORIZONTAL, command=tags_tree.xview)
        tags_tree.configure(yscrollcommand=tags_v_scroll.set, xscrollcommand=tags_h_scroll.set)
        
        tags_tree.grid(row=0, column=0, sticky='nsew')
        tags_v_scroll.grid(row=0, column=1, sticky='ns')
        tags_h_scroll.grid(row=1, column=0, sticky='ew')
        
        tags_frame.grid_rowconfigure(0, weight=1)
        tags_frame.grid_columnconfigure(0, weight=1)
        
        # RIGHT PANE - Tag Details (vertical split)
        right_paned = ttk.PanedWindow(main_paned, orient=tk.VERTICAL)
        main_paned.add(right_paned, weight=2)
        
        # TOP RIGHT - Tag Information
        info_frame = ttk.LabelFrame(right_paned, text="Tag Information")
        right_paned.add(info_frame, weight=1)
        
        # Tag details text area
        info_text_frame = ttk.Frame(info_frame)
        info_text_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        self.tag_info_text = tk.Text(info_text_frame, height=8, wrap=tk.WORD, font=('Courier', 10))
        info_text_scroll = ttk.Scrollbar(info_text_frame, orient=tk.VERTICAL, command=self.tag_info_text.yview)
        self.tag_info_text.configure(yscrollcommand=info_text_scroll.set)
        
        self.tag_info_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        info_text_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        
        # MIDDLE RIGHT - Commit Details
        commit_frame = ttk.LabelFrame(right_paned, text="Commit Details")
        right_paned.add(commit_frame, weight=1)
        
        commit_text_frame = ttk.Frame(commit_frame)
        commit_text_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        self.commit_details_text = tk.Text(commit_text_frame, height=6, wrap=tk.WORD, font=('Courier', 9))
        commit_text_scroll = ttk.Scrollbar(commit_text_frame, orient=tk.VERTICAL, command=self.commit_details_text.yview)
        self.commit_details_text.configure(yscrollcommand=commit_text_scroll.set)
        
        self.commit_details_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        commit_text_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        
        # BOTTOM RIGHT - Files Changed
        files_frame = ttk.LabelFrame(right_paned, text="Files Changed in Tag")
        right_paned.add(files_frame, weight=2)
        
        files_tree_frame = ttk.Frame(files_frame)
        files_tree_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        files_columns = ('File Path', 'Status', 'Additions', 'Deletions', 'Total Changes')
        self.tag_files_tree = ttk.Treeview(files_tree_frame, columns=files_columns, show='headings')
        
        # Configure files columns
        for col in files_columns:
            self.tag_files_tree.heading(col, text=col)
            if col == 'File Path':
                self.tag_files_tree.column(col, width=300, minwidth=200)
            else:
                self.tag_files_tree.column(col, width=80, minwidth=60)
        
        # Scrollbars for files tree
        files_v_scroll = ttk.Scrollbar(files_tree_frame, orient=tk.VERTICAL, command=self.tag_files_tree.yview)
        files_h_scroll = ttk.Scrollbar(files_tree_frame, orient=tk.HORIZONTAL, command=self.tag_files_tree.xview)
        self.tag_files_tree.configure(yscrollcommand=files_v_scroll.set, xscrollcommand=files_h_scroll.set)
        
        self.tag_files_tree.grid(row=0, column=0, sticky='nsew')
        files_v_scroll.grid(row=0, column=1, sticky='ns')
        files_h_scroll.grid(row=1, column=0, sticky='ew')
        
        files_tree_frame.grid_rowconfigure(0, weight=1)
        files_tree_frame.grid_columnconfigure(0, weight=1)
        
        # BOTTOM ACTIONS BAR
        actions_bar = ttk.Frame(tags_window)
        actions_bar.pack(fill=tk.X, padx=10, pady=5)
        
        # Tag operations
        ttk.Button(actions_bar, text="Switch to Tag", 
                  command=lambda: self.switch_to_selected_tag(tags_tree), 
                  style='Info.TButton').pack(side=tk.LEFT, padx=5)
        
        ttk.Button(actions_bar, text="Delete Tag", 
                  command=lambda: self.delete_selected_tag(tags_tree), 
                  style='Warning.TButton').pack(side=tk.LEFT, padx=5)
        
        ttk.Button(actions_bar, text="Push Tag", 
                  command=lambda: self.push_selected_tag(tags_tree), 
                  style='Success.TButton').pack(side=tk.LEFT, padx=5)
        
        ttk.Button(actions_bar, text="Compare Tags", 
                  command=lambda: self.compare_tags_dialog(tags_tree)).pack(side=tk.LEFT, padx=5)
        
        # File operations
        ttk.Button(actions_bar, text="View File at Tag", 
                  command=lambda: self.view_file_at_selected_tag(tags_tree, self.tag_files_tree)).pack(side=tk.LEFT, padx=10)
        
        ttk.Button(actions_bar, text="Export Tag Info", 
                  command=lambda: self.export_tag_info(tags_tree)).pack(side=tk.LEFT, padx=5)
        
        # Close button
        ttk.Button(actions_bar, text="Close", command=tags_window.destroy).pack(side=tk.RIGHT, padx=5)
        
        # BIND EVENTS
        tags_tree.bind('<<TreeviewSelect>>', lambda e: self.on_tag_select(tags_tree))
        self.tag_files_tree.bind('<Double-1>', lambda e: self.view_file_at_selected_tag(tags_tree, self.tag_files_tree))
        
        # Context menus
        self.create_tag_context_menu(tags_tree)
        self.create_tag_files_context_menu(self.tag_files_tree, tags_tree)
        
        # POPULATE DATA
        self.populate_tags_enhanced(tags_tree)
        
        # Select first tag if available
        if tags_tree.get_children():
            first_tag = tags_tree.get_children()[0]
            tags_tree.selection_set(first_tag)
            tags_tree.see(first_tag)
            self.on_tag_select(tags_tree)
    
    def create_tag_context_menu(self, tags_tree):
        """Create context menu for tags - MODIFIED VERSION"""
        self.tag_context_menu = tk.Menu(self.root, tearoff=0)
        self.tag_context_menu.add_command(label="Switch to Tag", 
                                        command=lambda: self.switch_to_selected_tag(tags_tree))
        self.tag_context_menu.add_command(label="Create Branch from Tag", 
                                        command=lambda: self.create_branch_from_tag(tags_tree))
        self.tag_context_menu.add_separator()
        self.tag_context_menu.add_command(label="Rename Tag",                    # NEW
                                        command=lambda: self.rename_tag_from_context(tags_tree))
        self.tag_context_menu.add_command(label="Push Tag to Remote", 
                                        command=lambda: self.push_selected_tag(tags_tree))
        self.tag_context_menu.add_command(label="Delete Tag", 
                                        command=lambda: self.delete_selected_tag(tags_tree))
        self.tag_context_menu.add_separator()
        self.tag_context_menu.add_command(label="View Tag at GitHub", 
                                        command=lambda: self.view_tag_at_github(tags_tree))
        self.tag_context_menu.add_command(label="Copy Tag Name", 
                                        command=lambda: self.copy_tag_name(tags_tree))
        
        tags_tree.bind('<Button-3>', lambda e: self.show_tag_context_menu(e, tags_tree))
    
    def create_tag_files_context_menu(self, files_tree, tags_tree):
        """Create context menu for tag files"""
        self.tag_files_context_menu = tk.Menu(self.root, tearoff=0)
        self.tag_files_context_menu.add_command(label="View File at Tag", 
                                               command=lambda: self.view_file_at_selected_tag(tags_tree, files_tree))
        self.tag_files_context_menu.add_command(label="Compare with Current", 
                                               command=lambda: self.compare_file_with_current_from_tag(tags_tree, files_tree))
        self.tag_files_context_menu.add_command(label="View File History", 
                                               command=lambda: self.view_file_history_from_tag(tags_tree, files_tree))
        self.tag_files_context_menu.add_separator()
        self.tag_files_context_menu.add_command(label="Copy File Path", 
                                               command=lambda: self.copy_file_path(files_tree))
        
        files_tree.bind('<Button-3>', lambda e: self.show_tag_files_context_menu(e, files_tree))
    
    def populate_tags_enhanced(self, tags_tree):
        """Populate tags with comprehensive information"""
        try:
            # Clear existing items
            for item in tags_tree.get_children():
                tags_tree.delete(item)
            
            # Get remote tags for comparison
            remote_tags = set()
            try:
                if self.repo.remotes:
                    remote_refs = self.repo.remotes.origin.refs
                    for ref in remote_refs:
                        if ref.name.startswith('origin/refs/tags/'):
                            tag_name = ref.name.replace('origin/refs/tags/', '')
                            remote_tags.add(tag_name)
            except:
                pass
            
            # Sort tags by date (newest first)
            sorted_tags = sorted(self.repo.tags, key=lambda t: t.commit.committed_datetime, reverse=True)
            
            for tag in sorted_tags:
                try:
                    commit = tag.commit
                    
                    # Determine tag type
                    tag_type = "Lightweight"
                    if hasattr(tag, 'tag') and tag.tag:
                        tag_type = "Annotated"
                    
                    # Remote status
                    remote_status = "✓ Remote" if tag.name in remote_tags else "✗ Local only"
                    
                    # Color coding based on status
                    if tag.name in remote_tags:
                        tags = ('remote_tag',)
                    else:
                        tags = ('local_tag',)
                    
                    tags_tree.insert('', 'end', values=(
                        tag.name,
                        tag_type,
                        commit.hexsha[:12],
                        commit.committed_datetime.strftime('%Y-%m-%d %H:%M:%S'),
                        commit.author.name,
                        remote_status
                    ), tags=tags)
                    
                except Exception as e:
                    # If there's an error with a specific tag, add it with limited info
                    tags_tree.insert('', 'end', values=(
                        tag.name,
                        "Error",
                        "N/A",
                        "N/A",
                        "N/A",
                        "N/A"
                    ), tags=('error_tag',))
            
            # Configure tag colors
            tags_tree.tag_configure('remote_tag', background='#e8f5e8', foreground='#2d5a2d')  # Light green
            tags_tree.tag_configure('local_tag', background='#fff3cd', foreground='#856404')   # Light yellow
            tags_tree.tag_configure('error_tag', background='#f8d7da', foreground='#721c24')   # Light red
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to populate tags: {str(e)}")
    
    def on_tag_select(self, tags_tree):
        """Handle tag selection and update details panes"""
        selection = tags_tree.selection()
        if not selection:
            return
        
        try:
            selected_values = tags_tree.item(selection[0])['values']
            tag_name = selected_values[0]
            
            # Find the tag object
            selected_tag = None
            for tag in self.repo.tags:
                if tag.name == tag_name:
                    selected_tag = tag
                    break
            
            if not selected_tag:
                return
            
            # Update tag information pane
            self.update_tag_info_pane(selected_tag)
            
            # Update commit details pane
            self.update_commit_details_pane(selected_tag.commit)
            
            # Update files changed pane
            self.update_tag_files_pane(selected_tag)
            
        except Exception as e:
            self.tag_info_text.delete('1.0', tk.END)
            self.tag_info_text.insert('1.0', f"Error loading tag details: {str(e)}")
    
    def update_tag_info_pane(self, tag):
        """Update the tag information pane"""
        try:
            self.tag_info_text.delete('1.0', tk.END)
            
            info = f"🏷️  TAG INFORMATION\n"
            info += f"{'='*50}\n\n"
            
            info += f"Name: {tag.name}\n"
            info += f"Type: {'Annotated' if hasattr(tag, 'tag') and tag.tag else 'Lightweight'}\n"
            info += f"Object: {tag.commit.hexsha}\n"
            info += f"Created: {tag.commit.committed_datetime.strftime('%Y-%m-%d %H:%M:%S %Z')}\n"
            
            # Tag message (for annotated tags)
            if hasattr(tag, 'tag') and tag.tag:
                if tag.tag.message:
                    info += f"\nTag Message:\n{'-'*20}\n{tag.tag.message.strip()}\n"
                if tag.tag.tagger:
                    info += f"\nTagger: {tag.tag.tagger.name} <{tag.tag.tagger.email}>\n"
                    info += f"Tagged: {tag.tag.tagged_date}\n"
            
            # Remote status
            try:
                remote_refs = [ref.name for ref in self.repo.remotes.origin.refs if 'tags' in ref.name]
                is_remote = any(tag.name in ref for ref in remote_refs)
                info += f"\nRemote Status: {'✓ Pushed to remote' if is_remote else '✗ Local only'}\n"
            except:
                info += f"\nRemote Status: Unknown\n"
            
            # Branch information
            branches_containing = []
            for branch in self.repo.branches:
                try:
                    if tag.commit in list(self.repo.iter_commits(branch.name)):
                        branches_containing.append(branch.name)
                except:
                    continue
            
            if branches_containing:
                info += f"\nBranches containing this tag:\n{', '.join(branches_containing[:5])}"
                if len(branches_containing) > 5:
                    info += f" (+{len(branches_containing) - 5} more)"
            
            self.tag_info_text.insert('1.0', info)
            
        except Exception as e:
            self.tag_info_text.delete('1.0', tk.END)
            self.tag_info_text.insert('1.0', f"Error updating tag info: {str(e)}")
    
    def update_commit_details_pane(self, commit):
        """Update the commit details pane"""
        try:
            self.commit_details_text.delete('1.0', tk.END)
            
            details = f"📝  COMMIT DETAILS\n"
            details += f"{'='*50}\n\n"
            
            details += f"Hash: {commit.hexsha}\n"
            details += f"Short Hash: {commit.hexsha[:12]}\n"
            details += f"Author: {commit.author.name} <{commit.author.email}>\n"
            details += f"Authored: {commit.authored_datetime.strftime('%Y-%m-%d %H:%M:%S %Z')}\n"
            details += f"Committer: {commit.committer.name} <{commit.committer.email}>\n"
            details += f"Committed: {commit.committed_datetime.strftime('%Y-%m-%d %H:%M:%S %Z')}\n"
            
            # Parent information
            if commit.parents:
                details += f"\nParents: {', '.join([p.hexsha[:8] for p in commit.parents])}\n"
            else:
                details += f"\nParents: None (root commit)\n"
            
            # Commit message
            details += f"\nCommit Message:\n{'-'*20}\n{commit.message.strip()}\n"
            
            # Statistics
            if commit.parents:
                try:
                    # Get diff statistics
                    diff = commit.parents[0].diff(commit)
                    files_changed = len(diff)
                    insertions = sum(d.diff.decode('utf-8').count('\n+') for d in diff if d.diff)
                    deletions = sum(d.diff.decode('utf-8').count('\n-') for d in diff if d.diff)
                    
                    details += f"\nStatistics:\n{'-'*20}\n"
                    details += f"Files changed: {files_changed}\n"
                    details += f"Insertions: +{insertions}\n"
                    details += f"Deletions: -{deletions}\n"
                    details += f"Net change: {insertions - deletions:+d}\n"
                except:
                    details += f"\nStatistics: Unable to calculate\n"
            
            self.commit_details_text.insert('1.0', details)
            
        except Exception as e:
            self.commit_details_text.delete('1.0', tk.END)
            self.commit_details_text.insert('1.0', f"Error updating commit details: {str(e)}")
    
    def update_tag_files_pane(self, tag):
        """Update the files changed pane"""
        try:
            # Clear existing items
            for item in self.tag_files_tree.get_children():
                self.tag_files_tree.delete(item)
            
            commit = tag.commit
            
            if commit.parents:
                # Compare with parent commit
                parent_commit = commit.parents[0]
                diffs = parent_commit.diff(commit)
                
                total_files = 0
                total_additions = 0
                total_deletions = 0
                
                for diff in diffs:
                    status = 'Modified'
                    if diff.new_file:
                        status = 'Added'
                    elif diff.deleted_file:
                        status = 'Deleted'
                    elif diff.renamed_file:
                        status = 'Renamed'
                    elif diff.copied_file:
                        status = 'Copied'
                    
                    file_path = diff.b_path or diff.a_path
                    
                    # Calculate line changes
                    additions = deletions = 0
                    try:
                        if diff.diff:
                            diff_text = diff.diff.decode('utf-8')
                            additions = diff_text.count('\n+') - diff_text.count('\n+++')
                            deletions = diff_text.count('\n-') - diff_text.count('\n---')
                    except:
                        pass
                    
                    total_changes = additions + deletions
                    total_files += 1
                    total_additions += additions
                    total_deletions += deletions
                    
                    # Color coding based on change type
                    if status == 'Added':
                        tags = ('added_file',)
                    elif status == 'Deleted':
                        tags = ('deleted_file',)
                    elif status == 'Modified':
                        tags = ('modified_file',)
                    else:
                        tags = ('renamed_file',)
                    
                    self.tag_files_tree.insert('', 'end', values=(
                        file_path,
                        status,
                        f"+{additions}",
                        f"-{deletions}",
                        str(total_changes)
                    ), tags=tags)
                
                # Add summary row
                if total_files > 0:
                    self.tag_files_tree.insert('', 'end', values=(
                        f"📊 SUMMARY ({total_files} files)",
                        "Total",
                        f"+{total_additions}",
                        f"-{total_deletions}",
                        str(total_additions + total_deletions)
                    ), tags=('summary_row',))
                
            else:
                # Root commit - all files are new
                for item in commit.tree.traverse():
                    if item.type == 'blob':
                        self.tag_files_tree.insert('', 'end', values=(
                            item.path,
                            'Added',
                            'New',
                            '0',
                            'New'
                        ), tags=('added_file',))
            
            # Configure file colors
            self.tag_files_tree.tag_configure('added_file', background='#d4edda', foreground='#155724')
            self.tag_files_tree.tag_configure('deleted_file', background='#f8d7da', foreground='#721c24')
            self.tag_files_tree.tag_configure('modified_file', background='#fff3cd', foreground='#856404')
            self.tag_files_tree.tag_configure('renamed_file', background='#cce5ff', foreground='#004085')
            self.tag_files_tree.tag_configure('summary_row', background='#e9ecef', foreground='#495057', font=('TkDefaultFont', 10, 'bold'))
            
        except Exception as e:
            self.tag_files_tree.insert('', 'end', values=(
                f"Error: {str(e)}",
                "Error",
                "N/A",
                "N/A",
                "N/A"
            ))
    
    def refresh_tags_list(self, tags_tree):
        """Refresh the tags list"""
        self.populate_tags_enhanced(tags_tree)
    
    def switch_to_selected_tag(self, tags_tree):
        """Switch to the selected tag"""
        selection = tags_tree.selection()
        if not selection:
            messagebox.showwarning("No Selection", "Please select a tag to switch to")
            return
        
        tag_name = tags_tree.item(selection[0])['values'][0]
        
        if messagebox.askyesno("Confirm Switch", 
                              f"Switch to tag '{tag_name}'?\n\n" +
                              "This will detach HEAD from the current branch."):
            try:
                self.repo.git.checkout(tag_name)
                self.refresh_all()
                self.status_label.config(text=f"✓ Switched to tag: {tag_name} (HEAD detached)")
                messagebox.showinfo("Success", f"Successfully switched to tag '{tag_name}'")
            except Exception as e:
                messagebox.showerror("Switch Error", f"Failed to switch to tag: {str(e)}")
    
    def delete_selected_tag(self, tags_tree):
        """Delete the selected tag"""
        selection = tags_tree.selection()
        if not selection:
            messagebox.showwarning("No Selection", "Please select a tag to delete")
            return
        
        tag_name = tags_tree.item(selection[0])['values'][0]
        
        if messagebox.askyesno("Confirm Delete", 
                              f"Delete tag '{tag_name}'?\n\n" +
                              "This action cannot be undone."):
            try:
                self.repo.delete_tag(tag_name)
                self.refresh_tags_list(tags_tree)
                self.status_label.config(text=f"✓ Tag '{tag_name}' deleted")
                messagebox.showinfo("Success", f"Tag '{tag_name}' deleted successfully")
            except Exception as e:
                messagebox.showerror("Delete Error", f"Failed to delete tag: {str(e)}")
    
    def push_selected_tag(self, tags_tree):
        """Push the selected tag to remote"""
        selection = tags_tree.selection()
        if not selection:
            messagebox.showwarning("No Selection", "Please select a tag to push")
            return
        
        tag_name = tags_tree.item(selection[0])['values'][0]
        
        if messagebox.askyesno("Confirm Push", f"Push tag '{tag_name}' to remote?"):
            def push_tag():
                try:
                    self.status_label.config(text=f"Pushing tag '{tag_name}'...")
                    self.repo.git.push('origin', tag_name)
                    self.root.after(0, lambda: self.status_label.config(text=f"✓ Tag '{tag_name}' pushed to remote"))
                    self.root.after(0, lambda: self.refresh_tags_list(tags_tree))
                    self.root.after(0, lambda: messagebox.showinfo("Success", f"Tag '{tag_name}' pushed successfully"))
                except Exception as e:
                    self.root.after(0, lambda: messagebox.showerror("Push Error", f"Failed to push tag: {str(e)}"))
            
            threading.Thread(target=push_tag, daemon=True).start()
    
    def push_all_tags(self):
        """Push all tags to remote"""
        if messagebox.askyesno("Confirm Push All", "Push all tags to remote?"):
            def push_all():
                try:
                    self.status_label.config(text="Pushing all tags...")
                    self.repo.git.push('origin', '--tags')
                    self.root.after(0, lambda: self.status_label.config(text="✓ All tags pushed to remote"))
                    self.root.after(0, lambda: messagebox.showinfo("Success", "All tags pushed successfully"))
                except Exception as e:
                    self.root.after(0, lambda: messagebox.showerror("Push Error", f"Failed to push tags: {str(e)}"))
            
            threading.Thread(target=push_all, daemon=True).start()
    
    def view_file_at_selected_tag(self, tags_tree, files_tree):
        """View file at the selected tag"""
        tag_selection = tags_tree.selection()
        file_selection = files_tree.selection()
        
        if not tag_selection or not file_selection:
            messagebox.showwarning("No Selection", "Please select both a tag and a file")
            return
        
        tag_name = tags_tree.item(tag_selection[0])['values'][0]
        file_path = files_tree.item(file_selection[0])['values'][0]
        
        # Skip summary row
        if file_path.startswith('📊 SUMMARY'):
            return
        
        try:
            tag = self.repo.tags[tag_name]
            self.show_file_at_commit(file_path, tag.commit.hexsha)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to view file: {str(e)}")
    
    def compare_tags_dialog(self, tags_tree):
        """Compare two tags"""
        messagebox.showinfo("Feature Coming Soon", "Tag comparison feature will be implemented in a future version")
    
    def export_tag_info(self, tags_tree):
        """Export tag information to file"""
        selection = tags_tree.selection()
        if not selection:
            messagebox.showwarning("No Selection", "Please select a tag to export")
            return
        
        tag_name = tags_tree.item(selection[0])['values'][0]
        
        file_path = filedialog.asksaveasfilename(
            title="Export Tag Information",
            defaultextension=".txt",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
        )
        
        if file_path:
            try:
                tag = self.repo.tags[tag_name]
                with open(file_path, 'w') as f:
                    f.write(f"Tag Information Export\n")
                    f.write(f"{'='*50}\n\n")
                    f.write(f"Tag Name: {tag_name}\n")
                    f.write(f"Commit: {tag.commit.hexsha}\n")
                    f.write(f"Author: {tag.commit.author.name}\n")
                    f.write(f"Date: {tag.commit.committed_datetime}\n")
                    f.write(f"Message: {tag.commit.message.strip()}\n")
                    
                messagebox.showinfo("Success", f"Tag information exported to {file_path}")
            except Exception as e:
                messagebox.showerror("Export Error", f"Failed to export tag info: {str(e)}")
    
    def show_tag_context_menu(self, event, tags_tree):
        """Show context menu for tags"""
        try:
            self.tag_context_menu.tk_popup(event.x_root, event.y_root)
        finally:
            self.tag_context_menu.grab_release()
    
    def show_tag_files_context_menu(self, event, files_tree):
        """Show context menu for tag files"""
        try:
            self.tag_files_context_menu.tk_popup(event.x_root, event.y_root)
        finally:
            self.tag_files_context_menu.grab_release()
    
    def create_branch_from_tag(self, tags_tree):
        """Create a branch from the selected tag"""
        selection = tags_tree.selection()
        if not selection:
            messagebox.showwarning("No Selection", "Please select a tag")
            return
        
        tag_name = tags_tree.item(selection[0])['values'][0]
        branch_name = simpledialog.askstring("Create Branch", f"Enter branch name for tag '{tag_name}':")
        
        if branch_name:
            try:
                tag = self.repo.tags[tag_name]
                new_branch = self.repo.create_head(branch_name, tag.commit)
                
                if messagebox.askyesno("Switch Branch", f"Switch to new branch '{branch_name}'?"):
                    new_branch.checkout()
                    self.refresh_all()
                
                messagebox.showinfo("Success", f"Branch '{branch_name}' created from tag '{tag_name}'")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to create branch: {str(e)}")
    
    def view_tag_at_github(self, tags_tree):
        """View tag at GitHub"""
        selection = tags_tree.selection()
        if not selection:
            return
        
        tag_name = tags_tree.item(selection[0])['values'][0]
        
        try:
            remote_url = self.repo.remotes.origin.url
            if 'github.com' in remote_url:
                # Convert SSH URL to HTTPS if needed
                if remote_url.startswith('git@github.com:'):
                    remote_url = remote_url.replace('git@github.com:', 'https://github.com/')
                if remote_url.endswith('.git'):
                    remote_url = remote_url[:-4]
                
                github_url = f"{remote_url}/releases/tag/{tag_name}"
                webbrowser.open(github_url)
            else:
                messagebox.showinfo("Info", "This feature is only available for GitHub repositories")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to open GitHub: {str(e)}")
    
    def copy_tag_name(self, tags_tree):
        """Copy tag name to clipboard"""
        selection = tags_tree.selection()
        if not selection:
            return
        
        tag_name = tags_tree.item(selection[0])['values'][0]
        self.root.clipboard_clear()
        self.root.clipboard_append(tag_name)
        self.status_label.config(text=f"Tag name '{tag_name}' copied to clipboard")
    
    def copy_file_path(self, files_tree):
        """Copy file path to clipboard"""
        selection = files_tree.selection()
        if not selection:
            return
        
        file_path = files_tree.item(selection[0])['values'][0]
        if not file_path.startswith('📊 SUMMARY'):
            self.root.clipboard_clear()
            self.root.clipboard_append(file_path)
            self.status_label.config(text=f"File path '{file_path}' copied to clipboard")
    
    def compare_file_with_current_from_tag(self, tags_tree, files_tree):
        """Compare file in tag with current version"""
        tag_selection = tags_tree.selection()
        file_selection = files_tree.selection()
        
        if not tag_selection or not file_selection:
            messagebox.showwarning("No Selection", "Please select both a tag and a file")
            return
        
        tag_name = tags_tree.item(tag_selection[0])['values'][0]
        file_path = files_tree.item(file_selection[0])['values'][0]
        
        if file_path.startswith('📊 SUMMARY'):
            return
        
        try:
            tag = self.repo.tags[tag_name]
            self.compare_file_with_current(files_tree, tag.commit)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to compare file: {str(e)}")
    
    def view_file_history_from_tag(self, tags_tree, files_tree):
        """View file history from tag"""
        file_selection = files_tree.selection()
        if not file_selection:
            messagebox.showwarning("No Selection", "Please select a file")
            return
        
        file_path = files_tree.item(file_selection[0])['values'][0]
        
        if file_path.startswith('📊 SUMMARY'):
            return
        
        try:
            self.show_file_history_dialog(file_path)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to view file history: {str(e)}")
    
    def show_file_history_dialog(self, file_path):
        """Show file history in a dialog"""
        history_window = tk.Toplevel(self.root)
        history_window.title(f"File History: {file_path}")
        history_window.geometry("800x600")
        
        columns = ('Commit', 'Date', 'Author', 'Message')
        history_tree = ttk.Treeview(history_window, columns=columns, show='headings')
        
        for col in columns:
            history_tree.heading(col, text=col)
            history_tree.column(col, width=150)
        
        try:
            commits = list(self.repo.iter_commits(paths=file_path))
            for commit in commits:
                history_tree.insert('', 'end', values=(
                    commit.hexsha[:8],
                    commit.committed_datetime.strftime('%Y-%m-%d %H:%M'),
                    commit.author.name,
                    commit.message.strip()[:50]
                ))
        except Exception as e:
            messagebox.showerror("Error", f"Could not get file history: {str(e)}")
        
        history_tree.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        ttk.Button(history_window, text="Close", command=history_window.destroy).pack(pady=10)
    
    # Continue with the rest of the original methods...
    
    def populate_repository_tree(self):
        """Populate repository tree with folders and status indicators"""
        if not self.repo:
            return
        
        # Clear existing items
        for item in self.repo_tree.get_children():
            self.repo_tree.delete(item)
        
        # Update file status cache
        self.update_file_status_cache_enhanced()
        
        # Add repository root
        repo_name = os.path.basename(self.repo_path)
        root_status = self.get_folder_status(self.repo_path)
        root_item = self.repo_tree.insert('', 'end', text=f"{root_status} {repo_name}", values=(self.repo_path,), open=True)
        
        # Add folders recursively
        self.add_tree_nodes(root_item, self.repo_path)
    
        
    def get_folder_status(self, folder_path):
        """Get status indicator for folder"""
        has_new = False
        has_modified = False
        has_staged = False
        
        for file_path, status in self.file_status_cache.items():
            if file_path.startswith(folder_path):
                if status == 'NEW':
                    has_new = True
                elif status == 'MODIFIED':
                    has_modified = True
                elif status in ['STAGED', 'MODIFIED_STAGED']:
                    has_staged = True
        
        if has_staged:
            return "📁🟢"  # Green for staged
        elif has_modified:
            return "📁🟠"  # Orange for modified
        elif has_new:
            return "📁🔴"  # Red for new/untracked
        else:
            return "📁"  # Regular folder
    
    def add_tree_nodes(self, parent, path):
        """Add tree nodes recursively with status indicators"""
        try:
            for item in sorted(os.listdir(path)):
                if item.startswith('.'):
                    continue
                
                item_path = os.path.join(path, item)
                if os.path.isdir(item_path):
                    status_indicator = self.get_folder_status(item_path)
                    folder_item = self.repo_tree.insert(parent, 'end', text=f"{status_indicator} {item}", values=(item_path,))
                    # Add subdirectories
                    if any(os.path.isdir(os.path.join(item_path, f)) for f in os.listdir(item_path) if not f.startswith('.')):
                        self.add_tree_nodes(folder_item, item_path)
        except PermissionError:
            pass
    
    def on_tree_select(self, event):
        """Handle tree selection"""
        selection = self.repo_tree.selection()
        if selection:
            item = selection[0]
            values = self.repo_tree.item(item)['values']
            if values:  # Make sure values exist
                path = values[0]
                self.populate_file_list_enhanced(path)
            else:
                # If no values, try to reconstruct path
                self.refresh_all()
    
        
    def schedule_highlight_clear(self):
        """Schedule clearing of file highlights after 5 seconds"""
        if hasattr(self, 'highlight_timer'):
            self.root.after_cancel(self.highlight_timer)
        
        self.highlight_timer = self.root.after(5000, self.clear_file_highlights)
    
    def clear_file_highlights(self):
        """Clear file highlights and reset to normal colors"""
        try:
            if hasattr(self, 'file_tree'):
                # Reset all highlighted files to clean state
                for child in self.file_tree.get_children():
                    current_tags = self.file_tree.item(child, 'tags')
                    if current_tags and current_tags[0] in ['new_file', 'modified_file', 'staged_file', 'modified_staged_file']:
                        # Get the file path
                        file_name = self.file_tree.item(child, 'values')[0]
                        tree_selection = self.repo_tree.selection()
                        if tree_selection:
                            tree_item = self.repo_tree.item(tree_selection[0])
                            values = tree_item['values']
                            if values:
                                folder_path = values[0]
                                file_path = os.path.join(folder_path, file_name)
                                
                                # Check if file is still modified
                                current_status = self.file_status_cache.get(file_path, 'CLEAN')
                                if current_status == 'CLEAN':
                                    # Reset to clean styling
                                    self.file_tree.item(child, tags=('clean_file',))
                                    icon = self.get_file_icon(file_path, 'CLEAN')
                                    self.file_tree.item(child, text=icon)
                
                # Clear highlighted files set
                self.highlighted_files.clear()
                
        except Exception as e:
            pass  # Silently handle any errors during cleanup
    
    def create_tooltip(self, widget, text):
        """Create a tooltip for a widget"""
        def on_enter(event):
            tooltip = tk.Toplevel()
            tooltip.wm_overrideredirect(True)
            tooltip.wm_geometry(f"+{event.x_root+10}+{event.y_root+10}")
            label = tk.Label(tooltip, text=text, background="lightyellow", 
                           relief="solid", borderwidth=1, font=('TkDefaultFont', 8))
            label.pack()
            widget.tooltip = tooltip
        
        def on_leave(event):
            if hasattr(widget, 'tooltip'):
                widget.tooltip.destroy()
                del widget.tooltip
        
        widget.bind("<Enter>", on_enter)
        widget.bind("<Leave>", on_leave)
    
    def get_git_file_info(self, file_path):
        """Get Git information for a file"""
        if not self.repo:
            return "", "", "", "", ""
        
        try:
            # Get relative path from repo root
            rel_path = os.path.relpath(file_path, self.repo_path)
            
            # Get latest commit for this file
            commits = list(self.repo.iter_commits(paths=rel_path, max_count=10))
            
            if commits:
                latest_commit = commits[0]
                branch_info = self.current_branch or "main"
                commit_info = latest_commit.hexsha[:8]
                version_info = str(len(commits))
                author_info = latest_commit.author.name
                commit_date = latest_commit.committed_datetime.strftime('%Y-%m-%d')
                
                return branch_info, commit_info, version_info, author_info, commit_date
            else:
                return self.current_branch or "main", "New", "0", "", ""
                
        except Exception:
            return "", "", "", "", ""
    
    def populate_changes(self):
        """Populate modified and staged files"""
        if not self.repo:
            return
        
        # Clear existing items
        for item in self.modified_tree.get_children():
            self.modified_tree.delete(item)
        for item in self.staging_tree.get_children():
            self.staging_tree.delete(item)
        
        try:
            # Get repository status
            status = self.repo.git.status('--porcelain').split('\n')
            
            for line in status:
                if not line.strip():
                    continue
                
                status_code = line[:2]
                file_path = line[3:]
                
                # Parse status codes
                if status_code[0] in ['M', 'A', 'D', 'R', 'C']:
                    # Staged changes
                    status_text = self.get_status_text(status_code[0])
                    self.staging_tree.insert('', 'end', values=(file_path, status_text))
                
                if status_code[1] in ['M', 'D', '?', '!']:
                    # Unstaged changes
                    status_text = self.get_status_text(status_code[1])
                    self.modified_tree.insert('', 'end', values=(status_text, file_path))
                    
        except Exception as e:
            self.status_label.config(text=f"Error reading status: {str(e)}")
    
    def get_status_text(self, code):
        """Convert status code to readable text"""
        status_map = {
            'M': 'Modified',
            'A': 'Added',
            'D': 'Deleted',
            'R': 'Renamed',
            'C': 'Copied',
            '?': 'Untracked',
            '!': 'Ignored'
        }
        return status_map.get(code, 'Unknown')
    
    def format_file_size(self, size):
        """Format file size in human readable format"""
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size < 1024.0:
                return f"{size:.1f} {unit}"
            size /= 1024.0
        return f"{size:.1f} TB"
    
    def refresh_all(self):
        """Refresh all data"""
        if self.repo:
            try:
                # Check if HEAD is detached and pointing to a tag
                try:
                    current_ref = self.repo.head.ref
                    self.current_branch = current_ref.name
                    self.branch_label.config(text=f"Branch: {self.current_branch}", 
                                           foreground='#007bff')  # Blue for branch
                except:
                    # HEAD is detached, check if it's pointing to a tag
                    head_commit = self.repo.head.commit
                    current_tag = None
                    
                    for tag in self.repo.tags:
                        if tag.commit == head_commit:
                            current_tag = tag.name
                            break
                    
                    if current_tag:
                        self.current_branch = None
                        self.branch_label.config(text=f"Tag: {current_tag}", 
                                               foreground='#fd7e14')  # Orange for tag
                    else:
                        self.current_branch = None
                        self.branch_label.config(text=f"HEAD: {head_commit.hexsha[:8]}", 
                                               foreground='#dc3545')  # Red for detached HEAD
                
                # Update remote URL and user info
                try:
                    remote_url = self.repo.remotes.origin.url
                    self.remote_label.config(text=f"Remote: {remote_url}")
                except:
                    self.remote_label.config(text="No remote configured")
                
                # Update user info with better detection
                try:
                    # Try multiple methods to get user config
                    user_name = ""
                    user_email = ""
                    
                    # Method 1: Try local repo config
                    try:
                        config = self.repo.config_reader()
                        user_name = config.get_value("user", "name", fallback="")
                        user_email = config.get_value("user", "email", fallback="")
                    except:
                        pass
                    
                    # Method 2: Try git config command directly
                    if not user_name:
                        try:
                            user_name = self.repo.git.config('user.name').strip()
                            user_email = self.repo.git.config('user.email').strip()
                        except:
                            pass
                    
                    # Method 3: Try global config command
                    if not user_name:
                        try:
                            user_name = self.repo.git.config('--global', 'user.name').strip()
                            user_email = self.repo.git.config('--global', 'user.email').strip()
                        except:
                            pass
                    
                    # Method 4: Parse .gitconfig file directly
                    if not user_name:
                        try:
                            import configparser
                            config_file = os.path.expanduser('~/.gitconfig')
                            if os.path.exists(config_file):
                                config_parser = configparser.ConfigParser()
                                config_parser.read(config_file)
                                if 'user' in config_parser:
                                    user_name = config_parser['user'].get('name', '')
                                    user_email = config_parser['user'].get('email', '')
                        except:
                            pass
                    
                    # Update label based on results
                    if user_name and user_email:
                        self.user_label.config(text=f"User: {user_name} <{user_email}>")
                    elif user_name:
                        self.user_label.config(text=f"User: {user_name}")
                    else:
                        self.user_label.config(text="User: Not configured")
                        
                except Exception as e:
                    self.user_label.config(text="User: Error reading config")
                
                self.populate_repository_tree()
                self.populate_changes()
                self.status_label.config(text="Repository refreshed")
                
                # Schedule highlight clearing
                self.schedule_highlight_clear()
                
            except Exception as e:
                self.status_label.config(text=f"Error refreshing: {str(e)}")
        else:
            self.status_label.config(text="No repository loaded")
    
    def git_pull(self):
        """Execute git pull"""
        if not self.repo:
            messagebox.showerror("Error", "No repository loaded")
            return
        
        def pull_worker():
            try:
                self.status_label.config(text="Pulling changes...")
                self.repo.remotes.origin.pull()
                self.root.after(0, lambda: self.status_label.config(text="Pull completed"))
                self.root.after(0, self.refresh_all)
            except Exception as e:
                self.root.after(0, lambda: messagebox.showerror("Pull Error", str(e)))
        
        threading.Thread(target=pull_worker, daemon=True).start()
    
    def git_push(self):
        """Execute git push"""
        if not self.repo:
            messagebox.showerror("Error", "No repository loaded")
            return
        
        def push_worker():
            try:
                self.status_label.config(text="Pushing changes...")
                self.repo.remotes.origin.push()
                self.root.after(0, lambda: self.status_label.config(text="Push completed"))
            except Exception as e:
                self.root.after(0, lambda: messagebox.showerror("Push Error", str(e)))
        
        threading.Thread(target=push_worker, daemon=True).start()
    
    def git_fetch(self):
        """Execute git fetch"""
        if not self.repo:
            messagebox.showerror("Error", "No repository loaded")
            return
        
        def fetch_worker():
            try:
                self.status_label.config(text="Fetching changes...")
                self.repo.remotes.origin.fetch()
                self.root.after(0, lambda: self.status_label.config(text="Fetch completed"))
            except Exception as e:
                self.root.after(0, lambda: messagebox.showerror("Fetch Error", str(e)))
        
        threading.Thread(target=fetch_worker, daemon=True).start()
    
    def git_commit(self):
        """Execute git commit"""
        if not self.repo:
            messagebox.showerror("Error", "No repository loaded")
            return
        
        # Check if there are staged changes
        try:
            staged_files = self.repo.index.diff("HEAD")
            if not staged_files:
                messagebox.showwarning("No Changes", "No staged changes to commit")
                return
        except:
            # If there's no HEAD (first commit), check if index has files
            try:
                if not self.repo.index.entries:
                    messagebox.showwarning("No Changes", "No staged changes to commit")
                    return
            except:
                messagebox.showwarning("No Changes", "No staged changes to commit")
                return
        
        # Get commit message
        message = simpledialog.askstring("Commit Message", "Enter commit message:")
        if message:
            try:
                self.repo.index.commit(message)
                self.status_label.config(text="Commit completed")
                self.refresh_all()
            except Exception as e:
                messagebox.showerror("Commit Error", str(e))
    
    def git_add_all(self):
        """Add all changes to staging area"""
        if not self.repo:
            messagebox.showerror("Error", "No repository loaded")
            return
        
        try:
            # Add all files including untracked
            self.repo.git.add('-A')
            self.status_label.config(text="All changes added to staging area")
            self.refresh_all()
        except Exception as e:
            messagebox.showerror("Add Error", str(e))
    
    def add_selected_file(self):
        """Add selected file to Git"""
        selection = self.file_tree.selection()
        if selection and self.repo:
            item = selection[0]
            file_name = self.file_tree.item(item)['values'][0]
            
            tree_selection = self.repo_tree.selection()
            if tree_selection:
                folder_path = self.repo_tree.item(tree_selection[0])['values'][0]
                file_path = os.path.join(folder_path, file_name)
                rel_path = os.path.relpath(file_path, self.repo_path)
                
                try:
                    self.repo.index.add([rel_path])
                    self.status_label.config(text=f"Added {file_name} to Git")
                    self.refresh_all()
                except Exception as e:
                    messagebox.showerror("Add Error", str(e))
    
    def stage_file(self, event):
        """Stage selected file"""
        selection = self.modified_tree.selection()
        if selection:
            item = selection[0]
            file_path = self.modified_tree.item(item)['values'][1]
            try:
                self.repo.index.add([file_path])
                self.populate_changes()
                self.status_label.config(text=f"Staged {file_path}")
            except Exception as e:
                messagebox.showerror("Stage Error", str(e))
    
    def unstage_file(self, event):
        """Unstage selected file"""
        selection = self.staging_tree.selection()
        if selection:
            item = selection[0]
            file_path = self.staging_tree.item(item)['values'][0]
            try:
                self.repo.index.reset([file_path])
                self.populate_changes()
                self.status_label.config(text=f"Unstaged {file_path}")
            except Exception as e:
                messagebox.showerror("Unstage Error", str(e))
    
    def open_in_vscode(self):
        """Open selected file in VS Code"""
        selection = self.file_tree.selection()
        if selection:
            item = selection[0]
            file_name = self.file_tree.item(item)['values'][0]
            
            # Get current folder path
            tree_selection = self.repo_tree.selection()
            if tree_selection:
                tree_item = self.repo_tree.item(tree_selection[0])
                values = tree_item['values']
                if values:
                    folder_path = values[0]
                else:
                    folder_path = self.repo_path
            else:
                folder_path = self.repo_path
            
            file_path = os.path.join(folder_path, file_name)
            
            # Make sure the file exists
            if os.path.exists(file_path):
                try:
                    # Try different VS Code commands
                    commands_to_try = ['code', 'code.cmd', 'code.exe']
                    
                    for cmd in commands_to_try:
                        try:
                            subprocess.run([cmd, file_path], check=True)
                            self.status_label.config(text=f"Opened {file_name} in VS Code")
                            return
                        except (subprocess.CalledProcessError, FileNotFoundError):
                            continue
                    
                    # If VS Code not found, try opening with system default
                    import webbrowser
                    webbrowser.open(file_path)
                    self.status_label.config(text=f"Opened {file_name} with default application")
                    
                except Exception as e:
                    messagebox.showerror("Error", f"Could not open file: {str(e)}")
            else:
                messagebox.showerror("Error", f"File not found: {file_path}")
    
    def show_file_context_menu(self, event):
        """Show context menu for file operations"""
        try:
            self.file_context_menu.tk_popup(event.x_root, event.y_root)
        finally:
            self.file_context_menu.grab_release()
    
    def open_file(self, event):
        """Open file with default application"""
        selection = self.file_tree.selection()
        if selection:
            item = selection[0]
            file_name = self.file_tree.item(item)['values'][0]
            
            tree_selection = self.repo_tree.selection()
            if tree_selection:
                tree_item = self.repo_tree.item(tree_selection[0])
                values = tree_item['values']
                if values:
                    folder_path = values[0]
                else:
                    folder_path = self.repo_path
            else:
                folder_path = self.repo_path
            
            file_path = os.path.join(folder_path, file_name)
            
            if os.path.isfile(file_path):
                try:
                    # Try VS Code first, then system default
                    commands_to_try = ['code', 'code.cmd', 'code.exe']
                    
                    for cmd in commands_to_try:
                        try:
                            subprocess.run([cmd, file_path], check=True)
                            self.status_label.config(text=f"Opened {file_name} in VS Code")
                            return
                        except (subprocess.CalledProcessError, FileNotFoundError):
                            continue
                    
                    # Fallback to system default
                    if sys.platform.startswith('darwin'):
                        subprocess.run(['open', file_path])
                    elif sys.platform.startswith('win'):
                        os.startfile(file_path)
                    else:
                        subprocess.run(['xdg-open', file_path])
                        
                    self.status_label.config(text=f"Opened {file_name}")
                    
                except Exception as e:
                    messagebox.showerror("Error", f"Could not open file: {str(e)}")
            else:
                messagebox.showerror("Error", f"File not found: {file_path}")
    
    def view_file_history(self):
        """View file history"""
        selection = self.file_tree.selection()
        if selection and self.repo:
            item = selection[0]
            file_name = self.file_tree.item(item)['values'][0]
            
            tree_selection = self.repo_tree.selection()
            if tree_selection:
                folder_path = self.repo_tree.item(tree_selection[0])['values'][0]
                file_path = os.path.join(folder_path, file_name)
                rel_path = os.path.relpath(file_path, self.repo_path)
                
                # Create history window
                history_window = tk.Toplevel(self.root)
                history_window.title(f"History: {file_name}")
                history_window.geometry("800x600")
                
                # History listbox
                history_frame = ttk.Frame(history_window)
                history_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
                
                columns = ('Commit', 'Date', 'Author', 'Message')
                history_tree = ttk.Treeview(history_frame, columns=columns, show='headings')
                
                for col in columns:
                    history_tree.heading(col, text=col)
                    history_tree.column(col, width=150)
                
                # Get file history
                try:
                    commits = list(self.repo.iter_commits(paths=rel_path))
                    for commit in commits:
                        history_tree.insert('', 'end', values=(
                            commit.hexsha[:8],
                            commit.committed_datetime.strftime('%Y-%m-%d %H:%M'),
                            commit.author.name,
                            commit.message.strip()
                        ))
                except Exception as e:
                    messagebox.showerror("Error", f"Could not get file history: {str(e)}")
                
                history_tree.pack(fill=tk.BOTH, expand=True)
    

    # Enhanced compare with head functionality
    def compare_with_head(self):
        """Compare file with HEAD - IMPLEMENTED"""
        selection = self.file_tree.selection()
        if not selection or not self.repo:
            messagebox.showwarning("No Selection", "Please select a file to compare")
            return
        
        item = selection[0]
        file_name = self.file_tree.item(item)['values'][0]
        
        tree_selection = self.repo_tree.selection()
        if not tree_selection:
            messagebox.showwarning("No Selection", "Please select a folder first")
            return
        
        folder_path = self.repo_tree.item(tree_selection[0])['values'][0]
        file_path = os.path.join(folder_path, file_name)
        
        if not os.path.isfile(file_path):
            messagebox.showwarning("Not a File", "Please select a file, not a directory")
            return
        
        rel_path = os.path.relpath(file_path, self.repo_path)
        
        # Create comparison window
        compare_window = tk.Toplevel(self.root)
        compare_window.title(f"Compare with HEAD: {file_name}")
        compare_window.geometry("1400x800")
        
        # Create paned window
        paned = ttk.PanedWindow(compare_window, orient=tk.HORIZONTAL)
        paned.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Left side - HEAD version
        left_frame = ttk.LabelFrame(paned, text="HEAD Version")
        paned.add(left_frame, weight=1)
        
        left_text = tk.Text(left_frame, font=('Courier', 9), wrap=tk.NONE)
        left_v_scroll = ttk.Scrollbar(left_frame, orient=tk.VERTICAL, command=left_text.yview)
        left_h_scroll = ttk.Scrollbar(left_frame, orient=tk.HORIZONTAL, command=left_text.xview)
        left_text.configure(yscrollcommand=left_v_scroll.set, xscrollcommand=left_h_scroll.set)
        
        left_text.grid(row=0, column=0, sticky='nsew')
        left_v_scroll.grid(row=0, column=1, sticky='ns')
        left_h_scroll.grid(row=1, column=0, sticky='ew')
        
        left_frame.grid_rowconfigure(0, weight=1)
        left_frame.grid_columnconfigure(0, weight=1)
        
        # Right side - working directory version
        right_frame = ttk.LabelFrame(paned, text="Working Directory")
        paned.add(right_frame, weight=1)
        
        right_text = tk.Text(right_frame, font=('Courier', 9), wrap=tk.NONE)
        right_v_scroll = ttk.Scrollbar(right_frame, orient=tk.VERTICAL, command=right_text.yview)
        right_h_scroll = ttk.Scrollbar(right_frame, orient=tk.HORIZONTAL, command=right_text.xview)
        right_text.configure(yscrollcommand=right_v_scroll.set, xscrollcommand=right_h_scroll.set)
        
        right_text.grid(row=0, column=0, sticky='nsew')
        right_v_scroll.grid(row=0, column=1, sticky='ns')
        right_h_scroll.grid(row=1, column=0, sticky='ew')
        
        right_frame.grid_rowconfigure(0, weight=1)
        right_frame.grid_columnconfigure(0, weight=1)
        
        try:
            # Get HEAD version
            try:
                head_commit = self.repo.head.commit
                head_content = head_commit.tree[rel_path].data_stream.read().decode('utf-8', errors='replace')
                left_text.insert('1.0', head_content)
            except:
                left_text.insert('1.0', "File not found in HEAD or binary file")
            
            # Get working directory version
            if os.path.exists(file_path):
                with open(file_path, 'r', encoding='utf-8', errors='replace') as f:
                    working_content = f.read()
                    right_text.insert('1.0', working_content)
            else:
                right_text.insert('1.0', "File not found in working directory")
            
            left_text.config(state=tk.DISABLED)
            right_text.config(state=tk.DISABLED)
            
            # Add diff statistics
            try:
                head_lines = left_text.get('1.0', tk.END).split('\n')
                working_lines = right_text.get('1.0', tk.END).split('\n')
                
                stats_frame = ttk.Frame(compare_window)
                stats_frame.pack(fill=tk.X, padx=10, pady=5)
                
                stats_text = f"HEAD: {len(head_lines)} lines | Working: {len(working_lines)} lines"
                ttk.Label(stats_frame, text=stats_text, font=('TkDefaultFont', 9)).pack()
            except:
                pass
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to compare files: {str(e)}")

    
    def create_branch(self):
        """Create new branch"""
        if not self.repo:
            messagebox.showerror("Error", "No repository loaded")
            return
        
        branch_name = simpledialog.askstring("New Branch", "Enter branch name:")
        if branch_name:
            try:
                new_branch = self.repo.create_head(branch_name)
                new_branch.checkout()
                self.refresh_all()
                self.status_label.config(text=f"Created and switched to branch: {branch_name}")
            except Exception as e:
                messagebox.showerror("Branch Error", str(e))
    
    def switch_branch(self):
        """Switch to different branch or tag with improved interface"""
        if not self.repo:
            messagebox.showerror("Error", "No repository loaded")
            return
        
        try:
            # Get list of branches
            local_branches = [str(branch.name) for branch in self.repo.branches]
            remote_branches = []
            
            # Get remote branches
            try:
                for ref in self.repo.refs:
                    if ref.name.startswith('origin/') and not ref.name.endswith('/HEAD'):
                        branch_name = ref.name.replace('origin/', '')
                        if branch_name not in local_branches:
                            remote_branches.append(f"origin/{branch_name}")
            except:
                pass
            
            # Get tags
            tags = [tag.name for tag in self.repo.tags]
            
            # Create branch/tag selection window
            switch_window = tk.Toplevel(self.root)
            switch_window.title("Switch Branch or Tag")
            switch_window.geometry("700x500")
            
            ttk.Label(switch_window, text="Select branch or tag to switch to:", font=('TkDefaultFont', 10, 'bold')).pack(pady=10)
            
            # Current branch info
            try:
                current = self.repo.active_branch.name
                ttk.Label(switch_window, text=f"Current branch: {current}", 
                         font=('TkDefaultFont', 9)).pack(pady=5)
            except:
                ttk.Label(switch_window, text="Current: HEAD detached", 
                         font=('TkDefaultFont', 9)).pack(pady=5)
            
            # Create notebook for branches and tags
            notebook = ttk.Notebook(switch_window)
            notebook.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
            
            # Branches tab
            branch_frame = ttk.Frame(notebook)
            notebook.add(branch_frame, text="Branches")
            
            # Branch treeview
            branch_columns = ('Name', 'Type', 'Commit', 'Date', 'Author')
            branch_tree = ttk.Treeview(branch_frame, columns=branch_columns, show='headings', height=15)
            
            for col in branch_columns:
                branch_tree.heading(col, text=col)
                if col == 'Name':
                    branch_tree.column(col, width=200)
                elif col == 'Type':
                    branch_tree.column(col, width=100)
                else:
                    branch_tree.column(col, width=120)
            
            branch_scrollbar = ttk.Scrollbar(branch_frame, orient=tk.VERTICAL, command=branch_tree.yview)
            branch_tree.configure(yscrollcommand=branch_scrollbar.set)
            
            # Populate branches
            for branch_name in local_branches:
                try:
                    branch = self.repo.heads[branch_name]
                    commit = branch.commit
                    is_current = "✓ Current" if branch == self.repo.active_branch else ""
                    branch_tree.insert('', 'end', values=(
                        branch_name,
                        f"Local {is_current}",
                        commit.hexsha[:8],
                        commit.committed_datetime.strftime('%Y-%m-%d'),
                        commit.author.name
                    ))
                except:
                    branch_tree.insert('', 'end', values=(branch_name, "Local", "", "", ""))
            
            for branch_name in remote_branches:
                try:
                    ref = self.repo.refs[branch_name]
                    commit = ref.commit
                    branch_tree.insert('', 'end', values=(
                        branch_name,
                        "Remote",
                        commit.hexsha[:8],
                        commit.committed_datetime.strftime('%Y-%m-%d'),
                        commit.author.name
                    ))
                except:
                    branch_tree.insert('', 'end', values=(branch_name, "Remote", "", "", ""))
            
            branch_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
            branch_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
            
            # Tags tab
            tag_frame = ttk.Frame(notebook)
            notebook.add(tag_frame, text="Tags")
            
            # Tag treeview
            tag_columns = ('Tag Name', 'Commit', 'Date', 'Author', 'Message')
            tag_tree = ttk.Treeview(tag_frame, columns=tag_columns, show='headings', height=15)
            
            for col in tag_columns:
                tag_tree.heading(col, text=col)
                if col == 'Tag Name':
                    tag_tree.column(col, width=150)
                elif col == 'Message':
                    tag_tree.column(col, width=200)
                else:
                    tag_tree.column(col, width=120)
            
            tag_scrollbar = ttk.Scrollbar(tag_frame, orient=tk.VERTICAL, command=tag_tree.yview)
            tag_tree.configure(yscrollcommand=tag_scrollbar.set)
            
            # Populate tags
            for tag in self.repo.tags:
                commit = tag.commit
                message = ""
                try:
                    if hasattr(tag, 'tag') and tag.tag and tag.tag.message:
                        message = tag.tag.message.strip()[:50]
                    else:
                        message = commit.message.strip()[:50]
                except:
                    message = "No message"
                
                tag_tree.insert('', 'end', values=(
                    tag.name,
                    commit.hexsha[:8],
                    commit.committed_datetime.strftime('%Y-%m-%d'),
                    commit.author.name,
                    message
                ))
            
            tag_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
            tag_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
            
            def switch_to_selected():
                current_tab = notebook.select()
                tab_text = notebook.tab(current_tab, "text")
                
                if tab_text == "Branches":
                    selection = branch_tree.selection()
                    if selection:
                        selected_data = branch_tree.item(selection[0])['values']
                        branch_name = selected_data[0]
                        branch_type = selected_data[1]
                        
                        try:
                            if "Remote" in branch_type:
                                # Create local branch from remote
                                local_name = branch_name.replace('origin/', '')
                                if messagebox.askyesno("Create Local Branch", 
                                                     f"Create local branch '{local_name}' from '{branch_name}'?"):
                                    self.repo.git.checkout('-b', local_name, branch_name)
                                    self.refresh_all()
                                    self.status_label.config(text=f"Created and switched to branch: {local_name}")
                                    switch_window.destroy()
                            else:
                                # Switch to existing local branch
                                clean_branch_name = branch_name.replace(" ✓ Current", "")
                                self.repo.git.checkout(clean_branch_name)
                                self.refresh_all()
                                self.status_label.config(text=f"Switched to branch: {clean_branch_name}")
                                switch_window.destroy()
                                
                        except Exception as e:
                            messagebox.showerror("Switch Error", f"Failed to switch branch: {str(e)}")
                    else:
                        messagebox.showwarning("No Selection", "Please select a branch")
                
                elif tab_text == "Tags":
                    selection = tag_tree.selection()
                    if selection:
                        tag_name = tag_tree.item(selection[0])['values'][0]
                        
                        if messagebox.askyesno("Confirm", f"Switch to tag '{tag_name}'?\nThis will detach HEAD."):
                            try:
                                self.repo.git.checkout(tag_name)
                                self.refresh_all()
                                self.status_label.config(text=f"Switched to tag: {tag_name} (HEAD detached)")
                                switch_window.destroy()
                                
                                # Update branch label to show tag
                                self.branch_label.config(text=f"Tag: {tag_name}", 
                                                       foreground='#fd7e14')  # Orange for tag
                                
                                # Refresh graph if open
                                if hasattr(self, 'graph_canvas'):
                                    self.draw_commit_graph(self.graph_canvas)
                                    
                            except Exception as e:
                                messagebox.showerror("Switch Error", f"Failed to switch to tag: {str(e)}")
                    else:
                        messagebox.showwarning("No Selection", "Please select a tag")
            
            # Buttons
            button_frame = ttk.Frame(switch_window)
            button_frame.pack(fill=tk.X, padx=20, pady=10)
            
            ttk.Button(button_frame, text="Switch", command=switch_to_selected).pack(side=tk.LEFT, padx=5)
            ttk.Button(button_frame, text="Cancel", command=switch_window.destroy).pack(side=tk.RIGHT, padx=5)
            
            # Double-click to switch
            branch_tree.bind('<Double-1>', lambda e: switch_to_selected())
            tag_tree.bind('<Double-1>', lambda e: switch_to_selected())
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load branches/tags: {str(e)}")
    
    def clone_repository(self):
        """Clone a repository"""
        url = simpledialog.askstring("Clone Repository", "Enter repository URL:")
        if url:
            folder = filedialog.askdirectory(title="Select destination folder")
            if folder:
                def clone_worker():
                    try:
                        self.status_label.config(text="Cloning repository...")
                        cloned_repo = git.Repo.clone_from(url, folder)
                        self.repo = cloned_repo
                        self.repo_path = folder
                        self.root.after(0, self.refresh_all)
                        self.root.after(0, lambda: self.status_label.config(text="Repository cloned successfully"))
                    except Exception as e:
                        self.root.after(0, lambda: messagebox.showerror("Clone Error", str(e)))
                
                threading.Thread(target=clone_worker, daemon=True).start()
    
    def show_log(self):
        """Show commit log"""
        if not self.repo:
            messagebox.showerror("Error", "No repository loaded")
            return
        
        # Create log window
        log_window = tk.Toplevel(self.root)
        log_window.title("Commit Log")
        log_window.geometry("1000x600")
        
        # Log treeview
        log_frame = ttk.Frame(log_window)
        log_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        columns = ('Commit', 'Date', 'Author', 'Message')
        log_tree = ttk.Treeview(log_frame, columns=columns, show='headings')
        
        for col in columns:
            log_tree.heading(col, text=col)
        
        log_tree.column('Commit', width=100)
        log_tree.column('Date', width=150)
        log_tree.column('Author', width=150)
        log_tree.column('Message', width=500)
        
        # Populate log
        try:
            commits = list(self.repo.iter_commits(max_count=100))
            for commit in commits:
                log_tree.insert('', 'end', values=(
                    commit.hexsha[:8],
                    commit.committed_datetime.strftime('%Y-%m-%d %H:%M:%S'),
                    commit.author.name,
                    commit.message.strip()
                ))
        except Exception as e:
            messagebox.showerror("Error", f"Could not get commit log: {str(e)}")
        
        log_tree.pack(fill=tk.BOTH, expand=True)
    
    def show_about(self):
        """Show about dialog"""
        about_text = """Git Python GUI - VCS Style
        
A comprehensive Git frontend built with Python and tkinter.
Features:
- Repository tree view
- File management with version information
- Staging and commit operations
- Branch management
- Remote operations (pull, push, fetch)
- Enhanced tag management with comprehensive details
- VS Code integration

Inspired by Simple VCS version control system.
        """
        messagebox.showinfo("About", about_text)
    
    def show_config(self):
        """Show Git configuration"""
        if not self.repo:
            messagebox.showerror("Error", "No repository loaded")
            return
        
        config_window = tk.Toplevel(self.root)
        config_window.title("Git Configuration")
        config_window.geometry("600x400")
        
        # Create notebook for different config scopes
        notebook = ttk.Notebook(config_window)
        notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Local config
        local_frame = ttk.Frame(notebook)
        notebook.add(local_frame, text="Local")
        
        local_tree = ttk.Treeview(local_frame, columns=('Value',), show='tree headings')
        local_tree.heading('#0', text='Setting')
        local_tree.heading('Value', text='Value')
        local_tree.column('#0', width=250)
        local_tree.column('Value', width=300)
        
        try:
            config = self.repo.config_reader()
            for section_name in config.sections():
                section_item = local_tree.insert('', 'end', text=section_name, values=('',))
                for (name, value) in config.items(section_name):
                    local_tree.insert(section_item, 'end', text=f"  {name}", values=(value,))
        except Exception as e:
            local_tree.insert('', 'end', text="Error", values=(str(e),))
        
        local_tree.pack(fill=tk.BOTH, expand=True)
        
        # Global config
        global_frame = ttk.Frame(notebook)
        notebook.add(global_frame, text="Global")
        
        global_tree = ttk.Treeview(global_frame, columns=('Value',), show='tree headings')
        global_tree.heading('#0', text='Setting')
        global_tree.heading('Value', text='Value')
        global_tree.column('#0', width=250)
        global_tree.column('Value', width=300)
        
        try:
            from git import GitConfigParser
            global_config = GitConfigParser([os.path.expanduser('~/.gitconfig')], read_only=True)
            for section_name in global_config.sections():
                section_item = global_tree.insert('', 'end', text=section_name, values=('',))
                for (name, value) in global_config.items(section_name):
                    global_tree.insert(section_item, 'end', text=f"  {name}", values=(value,))
        except Exception as e:
            global_tree.insert('', 'end', text="Error", values=(str(e),))
        
        global_tree.pack(fill=tk.BOTH, expand=True)
        
        # Buttons frame
        button_frame = ttk.Frame(config_window)
        button_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Button(button_frame, text="Edit Config", command=self.edit_config).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Close", command=config_window.destroy).pack(side=tk.RIGHT, padx=5)
    
    def edit_config(self):
        """Edit Git configuration"""
        config_window = tk.Toplevel(self.root)
        config_window.title("Edit Git Configuration")
        config_window.geometry("500x300")
        
        # User info frame
        user_frame = ttk.LabelFrame(config_window, text="User Information")
        user_frame.pack(fill=tk.X, padx=10, pady=10)
        
        ttk.Label(user_frame, text="Name:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        name_var = tk.StringVar()
        name_entry = ttk.Entry(user_frame, textvariable=name_var, width=40)
        name_entry.grid(row=0, column=1, padx=5, pady=5)
        
        ttk.Label(user_frame, text="Email:").grid(row=1, column=0, sticky=tk.W, padx=5, pady=5)
        email_var = tk.StringVar()
        email_entry = ttk.Entry(user_frame, textvariable=email_var, width=40)
        email_entry.grid(row=1, column=1, padx=5, pady=5)
        
        # Load current values
        try:
            config = self.repo.config_reader()
            name_var.set(config.get_value("user", "name", fallback=""))
            email_var.set(config.get_value("user", "email", fallback=""))
        except:
            pass
        
        def save_config():
            try:
                with self.repo.config_writer() as config:
                    config.set_value("user", "name", name_var.get())
                    config.set_value("user", "email", email_var.get())
                self.refresh_all()
                messagebox.showinfo("Success", "Configuration saved successfully")
                config_window.destroy()
            except Exception as e:
                messagebox.showerror("Error", f"Failed to save configuration: {str(e)}")
        
        # Buttons
        button_frame = ttk.Frame(config_window)
        button_frame.pack(fill=tk.X, padx=10, pady=10)
        
        ttk.Button(button_frame, text="Save", command=save_config).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Cancel", command=config_window.destroy).pack(side=tk.RIGHT, padx=5)
    
    def create_tag(self):
        """Create a new tag with push option"""
        if not self.repo:
            messagebox.showerror("Error", "No repository loaded")
            return
        
        tag_window = tk.Toplevel(self.root)
        tag_window.title("Create Tag")
        tag_window.geometry("800x450")
        tag_window.resizable(False, False)
        
        # Center the window
        tag_window.transient(self.root)
        tag_window.grab_set()
        
        ttk.Label(tag_window, text="Create New Tag", font=('TkDefaultFont', 12, 'bold')).pack(pady=10)
        
        # Tag info frame
        info_frame = ttk.LabelFrame(tag_window, text="Tag Information")
        info_frame.pack(fill=tk.X, padx=20, pady=10)
        
        # Tag name
        ttk.Label(info_frame, text="Tag Name:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        tag_name_var = tk.StringVar()
        tag_name_entry = ttk.Entry(info_frame, textvariable=tag_name_var, width=30)
        tag_name_entry.grid(row=0, column=1, padx=5, pady=5)
        tag_name_entry.focus()
        
        # Tag message
        ttk.Label(info_frame, text="Tag Message:").grid(row=1, column=0, sticky=tk.W, padx=5, pady=5)
        message_var = tk.StringVar()
        message_entry = ttk.Entry(info_frame, textvariable=message_var, width=30)
        message_entry.grid(row=1, column=1, padx=5, pady=5)
        
        # Description
        ttk.Label(info_frame, text="Description:").grid(row=2, column=0, sticky=tk.NW, padx=5, pady=5)
        description_text = tk.Text(info_frame, height=4, width=30)
        description_text.grid(row=2, column=1, padx=5, pady=5)
        
        # Options frame
        options_frame = ttk.LabelFrame(tag_window, text="Options")
        options_frame.pack(fill=tk.X, padx=20, pady=10)
        
        push_after_create = tk.BooleanVar(value=True)
        ttk.Checkbutton(options_frame, text="Push tag to GitHub after creation", 
                       variable=push_after_create).pack(anchor=tk.W, padx=10, pady=5)
        
        # Info
        info_text = "💡 Tip: Check 'Push tag to GitHub' to make the tag visible on GitHub immediately"
        ttk.Label(options_frame, text=info_text, font=('TkDefaultFont', 9), 
                 foreground='#6c757d').pack(padx=10, pady=5)
        
        # Current commit info
        try:
            current_commit = self.repo.head.commit
            commit_info = f"Tag will be created at: {current_commit.hexsha[:8]} - {current_commit.message.strip()[:50]}"
            ttk.Label(tag_window, text=commit_info, font=('TkDefaultFont', 8), 
                     foreground='#6c757d').pack(padx=20, pady=5)
        except:
            pass
        
        def create_tag_action():
            tag_name = tag_name_var.get().strip()
            message = message_var.get().strip()
            description = description_text.get('1.0', tk.END).strip()
            
            if not tag_name:
                messagebox.showerror("Error", "Tag name is required")
                tag_name_entry.focus()
                return
            
            # Validate tag name
            if not tag_name.replace('.', '').replace('-', '').replace('_', '').isalnum():
                messagebox.showerror("Error", "Tag name should contain only letters, numbers, dots, hyphens, and underscores")
                tag_name_entry.focus()
                return
            
            try:
                # Create full tag message
                full_message = message
                if description:
                    full_message += f"\n\n{description}"
                
                if full_message:
                    self.repo.create_tag(tag_name, message=full_message)
                else:
                    self.repo.create_tag(tag_name)
                
                tag_window.destroy()
                
                success_msg = f"✓ Tag '{tag_name}' created successfully"
                self.status_label.config(text=success_msg)
                
                # Push tag if requested
                if push_after_create.get():
                    def push_tag():
                        try:
                            self.status_label.config(text=f"Pushing tag '{tag_name}' to GitHub...")
                            self.repo.git.push('origin', tag_name)
                            final_msg = f"✓ Tag '{tag_name}' created and pushed to GitHub"
                            self.status_label.config(text=final_msg)
                            messagebox.showinfo("Success", f"Tag '{tag_name}' created and pushed to GitHub!\n\nThe tag is now visible on GitHub.")
                        except Exception as e:
                            error_msg = f"Tag created but push failed: {str(e)}"
                            self.status_label.config(text=error_msg)
                            messagebox.showerror("Push Error", f"Tag '{tag_name}' was created locally but failed to push to GitHub:\n\n{str(e)}\n\nUse 'Push Branch + Tags' to push it later.")
                    
                    # Push in background
                    threading.Thread(target=push_tag, daemon=True).start()
                else:
                    messagebox.showinfo("Tag Created", f"Tag '{tag_name}' created successfully!\n\nNote: The tag is only local. Use 'Push Branch + Tags' to make it visible on GitHub.")
                
                self.refresh_all()
                
            except Exception as e:
                messagebox.showerror("Error", f"Failed to create tag: {str(e)}")
        
        # Buttons
        button_frame = ttk.Frame(tag_window)
        button_frame.pack(fill=tk.X, padx=20, pady=20)
        
        ttk.Button(button_frame, text="Create Tag", command=create_tag_action, 
                  style='Success.TButton').pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Cancel", command=tag_window.destroy).pack(side=tk.RIGHT, padx=5)
        
        # Enter key binding
        tag_window.bind('<Return>', lambda e: create_tag_action())
    
    def switch_to_tag_only(self):
        """Switch to a specific tag - focused tag interface"""
        if not self.repo:
            messagebox.showerror("Error", "No repository loaded")
            return
        
        try:
            tags = list(self.repo.tags)
            if not tags:
                messagebox.showwarning("No Tags", "No tags found in repository")
                return
            
            # Create tag selection window
            tag_window = tk.Toplevel(self.root)
            tag_window.title("Switch to Tag")
            tag_window.geometry("800x500")
            
            ttk.Label(tag_window, text="Select tag to switch to:", font=('TkDefaultFont', 12, 'bold')).pack(pady=10)
            
            # Current status
            try:
                current = self.repo.active_branch.name
                ttk.Label(tag_window, text=f"Current branch: {current}", 
                         font=('TkDefaultFont', 9), foreground='blue').pack(pady=5)
            except:
                ttk.Label(tag_window, text="Current: HEAD detached", 
                         font=('TkDefaultFont', 9), foreground='red').pack(pady=5)
            
            # Tag selection frame
            selection_frame = ttk.Frame(tag_window)
            selection_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
            
            # Tag treeview with detailed columns
            tag_columns = ('Tag Name', 'Commit Hash', 'Commit Date', 'Author', 'Tag Message')
            tag_tree = ttk.Treeview(selection_frame, columns=tag_columns, show='headings', height=18)
            
            # Configure columns with proper widths
            tag_tree.heading('Tag Name', text='Tag Name')
            tag_tree.column('Tag Name', width=120, minwidth=100)
            
            tag_tree.heading('Commit Hash', text='Commit Hash')
            tag_tree.column('Commit Hash', width=100, minwidth=80)
            
            tag_tree.heading('Commit Date', text='Commit Date')
            tag_tree.column('Commit Date', width=120, minwidth=100)
            
            tag_tree.heading('Author', text='Author')
            tag_tree.column('Author', width=120, minwidth=100)
            
            tag_tree.heading('Tag Message', text='Tag Message')
            tag_tree.column('Tag Message', width=250, minwidth=200)
            
            # Scrollbar
            tag_scrollbar = ttk.Scrollbar(selection_frame, orient=tk.VERTICAL, command=tag_tree.yview)
            tag_tree.configure(yscrollcommand=tag_scrollbar.set)
            
            # Populate tags (sorted by date, newest first)
            sorted_tags = sorted(tags, key=lambda t: t.commit.committed_datetime, reverse=True)
            
            for tag in sorted_tags:
                commit = tag.commit
                
                # Get tag message
                tag_message = ""
                try:
                    if hasattr(tag, 'tag') and tag.tag and tag.tag.message:
                        tag_message = tag.tag.message.strip()
                        if len(tag_message) > 40:
                            tag_message = tag_message[:40] + "..."
                    else:
                        commit_msg = commit.message.strip()
                        if len(commit_msg) > 40:
                            commit_msg = commit_msg[:40] + "..."
                        tag_message = f"(commit: {commit_msg})"
                except:
                    tag_message = "No message"
                
                tag_tree.insert('', 'end', values=(
                    tag.name,
                    commit.hexsha[:8],
                    commit.committed_datetime.strftime('%Y-%m-%d %H:%M'),
                    commit.author.name,
                    tag_message
                ))
            
            tag_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
            tag_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
            
            # Info panel
            info_frame = ttk.LabelFrame(tag_window, text="Tag Information")
            info_frame.pack(fill=tk.X, padx=20, pady=5)
            
            self.tag_info_label = ttk.Label(info_frame, text="Select a tag to see details", 
                                           font=('TkDefaultFont', 9))
            self.tag_info_label.pack(pady=10)
            
            def on_tag_select(event):
                selection = tag_tree.selection()
                if selection:
                    selected_values = tag_tree.item(selection[0])['values']
                    tag_name = selected_values[0]
                    
                    # Find the tag object
                    selected_tag = None
                    for tag in tags:
                        if tag.name == tag_name:
                            selected_tag = tag
                            break
                    
                    if selected_tag:
                        commit = selected_tag.commit
                        info_text = f"Tag: {tag_name} | Commit: {commit.hexsha[:12]} | "
                        info_text += f"Date: {commit.committed_datetime.strftime('%Y-%m-%d %H:%M:%S')} | "
                        info_text += f"Author: {commit.author.name}"
                        
                        # Add files changed count
                        try:
                            if commit.parents:
                                files_changed = len(commit.parents[0].diff(commit))
                                info_text += f" | Files changed: {files_changed}"
                        except:
                            pass
                        
                        self.tag_info_label.config(text=info_text)
            
            tag_tree.bind('<<TreeviewSelect>>', on_tag_select)
            
            def switch_to_selected_tag():
                selection = tag_tree.selection()
                if selection:
                    tag_name = tag_tree.item(selection[0])['values'][0]
                    
                    if messagebox.askyesno("Confirm Switch", 
                                         f"Switch to tag '{tag_name}'?\n\n" +
                                         "This will detach HEAD from the current branch.\n" +
                                         "You can return to a branch later using 'Switch Branch'."):
                        try:
                            self.repo.git.checkout(tag_name)
                            self.refresh_all()
                            self.status_label.config(text=f"✓ Switched to tag: {tag_name} (HEAD detached)")
                            tag_window.destroy()
                            
                            # Update the branch label to show tag
                            self.branch_label.config(text=f"Tag: {tag_name}", 
                                                   foreground='#fd7e14')  # Orange for tag
                            
                            # Refresh graph if open
                            if hasattr(self, 'graph_canvas'):
                                self.draw_commit_graph(self.graph_canvas)
                            
                            # Show success message
                            messagebox.showinfo("Success", f"Successfully switched to tag '{tag_name}'")
                                
                        except Exception as e:
                            messagebox.showerror("Switch Error", f"Failed to switch to tag: {str(e)}")
                else:
                    messagebox.showwarning("No Selection", "Please select a tag to switch to")
            
            # Buttons
            button_frame = ttk.Frame(tag_window)
            button_frame.pack(fill=tk.X, padx=20, pady=10)
            
            ttk.Button(button_frame, text="Switch to Tag", 
                      command=switch_to_selected_tag, 
                      style='Accent.TButton').pack(side=tk.LEFT, padx=5)
            
            ttk.Button(button_frame, text="View Tag Details", 
                      command=lambda: self.show_selected_tag_details(tag_tree)).pack(side=tk.LEFT, padx=5)
            
            ttk.Button(button_frame, text="Cancel", 
                      command=tag_window.destroy).pack(side=tk.RIGHT, padx=5)
            
            # Double-click to switch
            tag_tree.bind('<Double-1>', lambda e: switch_to_selected_tag())
            
            # Select first tag by default
            if tag_tree.get_children():
                first_item = tag_tree.get_children()[0]
                tag_tree.selection_set(first_item)
                tag_tree.see(first_item)
                on_tag_select(None)
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load tags: {str(e)}")
    
    def show_selected_tag_details(self, tag_tree):
        """Show detailed information about selected tag"""
        selection = tag_tree.selection()
        if selection:
            tag_name = tag_tree.item(selection[0])['values'][0]
            
            # Find the tag
            for tag in self.repo.tags:
                if tag.name == tag_name:
                    self.show_tag_files_enhanced(tag_name)
                    break
        else:
            messagebox.showwarning("No Selection", "Please select a tag to view details")
    
    def show_tag_files_enhanced(self, tag_name):
        """Enhanced view of files changed in a specific tag"""
        tag_files_window = tk.Toplevel(self.root)
        tag_files_window.title(f"Files in Tag: {tag_name}")
        tag_files_window.geometry("1000x700")
        
        # Create paned window
        paned = ttk.PanedWindow(tag_files_window, orient=tk.VERTICAL)
        paned.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Top - tag info
        info_frame = ttk.LabelFrame(paned, text="Tag Information")
        paned.add(info_frame, weight=1)
        
        try:
            tag = self.repo.tags[tag_name]
            commit = tag.commit
            
            ttk.Label(info_frame, text=f"Tag: {tag_name}").pack(anchor=tk.W, padx=5, pady=2)
            ttk.Label(info_frame, text=f"Commit: {commit.hexsha}").pack(anchor=tk.W, padx=5, pady=2)
            ttk.Label(info_frame, text=f"Author: {commit.author.name}").pack(anchor=tk.W, padx=5, pady=2)
            ttk.Label(info_frame, text=f"Date: {commit.committed_datetime}").pack(anchor=tk.W, padx=5, pady=2)
            ttk.Label(info_frame, text=f"Message: {commit.message.strip()}").pack(anchor=tk.W, padx=5, pady=2)
        except Exception as e:
            ttk.Label(info_frame, text=f"Error: {str(e)}").pack(anchor=tk.W, padx=5, pady=2)
        
        # Bottom - files
        files_frame = ttk.LabelFrame(paned, text="Files Changed")
        paned.add(files_frame, weight=3)
        
        columns = ('File', 'Status', 'Additions', 'Deletions')
        files_tree = ttk.Treeview(files_frame, columns=columns, show='headings')
        
        for col in columns:
            files_tree.heading(col, text=col)
            files_tree.column(col, width=200)
        
        # Context menu for tag files
        tag_file_menu = tk.Menu(self.root, tearoff=0)
        tag_file_menu.add_command(label="View File at Tag", 
                                 command=lambda: self.view_file_at_tag(files_tree, tag_name))
        
        def show_tag_file_menu(event):
            try:
                tag_file_menu.tk_popup(event.x_root, event.y_root)
            finally:
                tag_file_menu.grab_release()
        
        files_tree.bind('<Button-3>', show_tag_file_menu)
        files_tree.bind('<Double-1>', lambda e: self.view_file_at_tag(files_tree, tag_name))
        
        try:
            tag = self.repo.tags[tag_name]
            commit = tag.commit
            
            if commit.parents:
                diffs = commit.parents[0].diff(commit)
                for diff in diffs:
                    status = 'Modified'
                    if diff.new_file:
                        status = 'Added'
                    elif diff.deleted_file:
                        status = 'Deleted'
                    elif diff.renamed_file:
                        status = 'Renamed'
                    
                    file_path = diff.b_path or diff.a_path
                    
                    try:
                        if diff.diff:
                            additions = diff.diff.decode('utf-8').count('\n+')
                            deletions = diff.diff.decode('utf-8').count('\n-')
                        else:
                            additions = deletions = 0
                    except:
                        additions = deletions = 0
                    
                    files_tree.insert('', 'end', values=(file_path, status, additions, deletions))
            else:
                for item in commit.tree.traverse():
                    if item.type == 'blob':
                        files_tree.insert('', 'end', values=(item.path, 'Added', 0, 0))
        except Exception as e:
            messagebox.showerror("Error", f"Failed to get tag files: {str(e)}")
        
        files_tree.pack(fill=tk.BOTH, expand=True)
    
    def view_file_at_tag(self, tree, tag_name):
        """View file at specific tag"""
        selection = tree.selection()
        if selection:
            file_path = tree.item(selection[0])['values'][0]
            try:
                tag = self.repo.tags[tag_name]
                self.show_file_at_commit(file_path, tag.commit.hexsha)
            except Exception as e:
                messagebox.showerror("Error", f"Failed to view file at tag: {str(e)}")
    
    def show_file_at_commit(self, file_path, commit_hash):
        """Show file content at specific commit"""
        try:
            commit = self.repo.commit(commit_hash)
            
            file_window = tk.Toplevel(self.root)
            file_window.title(f"File: {file_path} @ {commit_hash[:8]}")
            file_window.geometry("1000x700")
            
            # Create text widget with scrollbar
            text_frame = ttk.Frame(file_window)
            text_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
            
            text_widget = tk.Text(text_frame, font=('Courier', 10), wrap=tk.NONE)
            v_scrollbar = ttk.Scrollbar(text_frame, orient=tk.VERTICAL, command=text_widget.yview)
            h_scrollbar = ttk.Scrollbar(text_frame, orient=tk.HORIZONTAL, command=text_widget.xview)
            text_widget.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)
            
            text_widget.grid(row=0, column=0, sticky='nsew')
            v_scrollbar.grid(row=0, column=1, sticky='ns')
            h_scrollbar.grid(row=1, column=0, sticky='ew')
            
            text_frame.grid_rowconfigure(0, weight=1)
            text_frame.grid_columnconfigure(0, weight=1)
            
            # Get file content
            try:
                file_content = commit.tree[file_path].data_stream.read().decode('utf-8')
                text_widget.insert('1.0', file_content)
            except:
                text_widget.insert('1.0', f"Could not read file content (binary file or not found)")
            
            text_widget.config(state=tk.DISABLED)
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to show file at commit: {str(e)}")
    
    # Additional methods for comprehensive functionality
    def sort_files_by_column(self, column):
        """Sort files by column"""
        items = [(self.file_tree.set(item, column), item) for item in self.file_tree.get_children('')]
        
        # Sort items
        try:
            # Try numeric sort first
            items.sort(key=lambda x: float(x[0]) if x[0].replace('.', '').isdigit() else x[0].lower())
        except:
            # Fall back to string sort
            items.sort(key=lambda x: x[0].lower())
        
        # Rearrange items
        for index, (val, item) in enumerate(items):
            self.file_tree.move(item, '', index)
    
    def show_version_history(self):
        """Show comprehensive version history"""
        if not self.repo:
            messagebox.showerror("Error", "No repository loaded")
            return
        
        history_window = tk.Toplevel(self.root)
        history_window.title("Version History")
        history_window.geometry("1200x700")
        
        # Create paned window
        paned = ttk.PanedWindow(history_window, orient=tk.HORIZONTAL)
        paned.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Left side - commits
        left_frame = ttk.Frame(paned)
        paned.add(left_frame, weight=1)
        
        ttk.Label(left_frame, text="Commit History", font=('TkDefaultFont', 10, 'bold')).pack(anchor=tk.W)
        
        commits_columns = ('Commit', 'Date', 'Author', 'Message')
        commits_tree = ttk.Treeview(left_frame, columns=commits_columns, show='headings', height=15)
        
        for col in commits_columns:
            commits_tree.heading(col, text=col)
        
        commits_tree.column('Commit', width=80)
        commits_tree.column('Date', width=150)
        commits_tree.column('Author', width=120)
        commits_tree.column('Message', width=300)
        
        # Right side - files changed
        right_frame = ttk.Frame(paned)
        paned.add(right_frame, weight=1)
        
        ttk.Label(right_frame, text="Files Changed", font=('TkDefaultFont', 10, 'bold')).pack(anchor=tk.W)
        
        files_columns = ('File', 'Status', 'Changes')
        files_tree = ttk.Treeview(right_frame, columns=files_columns, show='headings', height=15)
        
        for col in files_columns:
            files_tree.heading(col, text=col)
            files_tree.column(col, width=200)
        
        # Populate commits
        try:
            commits = list(self.repo.iter_commits(max_count=100))
            for commit in commits:
                commits_tree.insert('', 'end', values=(
                    commit.hexsha[:8],
                    commit.committed_datetime.strftime('%Y-%m-%d %H:%M:%S'),
                    commit.author.name,
                    commit.message.strip()
                ))
        except Exception as e:
            messagebox.showerror("Error", f"Failed to get commit history: {str(e)}")
        
        def on_commit_select(event):
            selection = commits_tree.selection()
            if selection:
                # Clear files tree
                for item in files_tree.get_children():
                    files_tree.delete(item)
                
                commit_hash = commits_tree.item(selection[0])['values'][0]
                
                try:
                    commit = self.repo.commit(commit_hash)
                    
                    if commit.parents:
                        diffs = commit.parents[0].diff(commit)
                        for diff in diffs:
                            status = 'Modified'
                            if diff.new_file:
                                status = 'Added'
                            elif diff.deleted_file:
                                status = 'Deleted'
                            elif diff.renamed_file:
                                status = 'Renamed'
                            
                            file_path = diff.b_path or diff.a_path
                            
                            try:
                                changes = f"+{diff.diff.decode('utf-8').count(chr(10) + '+')} -{diff.diff.decode('utf-8').count(chr(10) + '-')}" if diff.diff else "0"
                            except:
                                changes = "0"
                            
                            files_tree.insert('', 'end', values=(file_path, status, changes))
                    else:
                        # First commit
                        for item in commit.tree.traverse():
                            if item.type == 'blob':
                                files_tree.insert('', 'end', values=(item.path, 'Added', 'New'))
                except Exception as e:
                    self.status_label.config(text=f"Error loading commit details: {str(e)}")
        
        commits_tree.bind('<<TreeviewSelect>>', on_commit_select)
        
        commits_tree.pack(fill=tk.BOTH, expand=True)
        files_tree.pack(fill=tk.BOTH, expand=True)
    
    def show_version_graph(self):
        """Show graphical version history with branches and navigation"""
        if not self.repo:
            messagebox.showerror("Error", "No repository loaded")
            return
        
        graph_window = tk.Toplevel(self.root)
        graph_window.title("Version History - Graph View")
        graph_window.geometry("1400x800")
        
        # Create toolbar for graph operations
        toolbar_frame = ttk.Frame(graph_window)
        toolbar_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Label(toolbar_frame, text="Graph Operations:", font=('TkDefaultFont', 10, 'bold')).pack(side=tk.LEFT)
        ttk.Button(toolbar_frame, text="Go to HEAD", command=lambda: self.checkout_commit('HEAD')).pack(side=tk.LEFT, padx=5)
        ttk.Button(toolbar_frame, text="Refresh Graph", command=lambda: self.refresh_graph(canvas, graph_window)).pack(side=tk.LEFT, padx=5)
        
        # Create main frame
        main_frame = ttk.Frame(graph_window)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Create canvas with scrollbars
        canvas_frame = ttk.Frame(main_frame)
        canvas_frame.pack(fill=tk.BOTH, expand=True)
        
        canvas = tk.Canvas(canvas_frame, bg='white', scrollregion=(0, 0, 3000, 600))
        h_scroll = ttk.Scrollbar(canvas_frame, orient=tk.HORIZONTAL, command=canvas.xview)
        v_scroll = ttk.Scrollbar(canvas_frame, orient=tk.VERTICAL, command=canvas.yview)
        
        canvas.configure(xscrollcommand=h_scroll.set, yscrollcommand=v_scroll.set)
        
        # Grid layout for canvas and scrollbars
        canvas.grid(row=0, column=0, sticky='nsew')
        v_scroll.grid(row=0, column=1, sticky='ns')
        h_scroll.grid(row=1, column=0, sticky='ew')
        
        canvas_frame.grid_rowconfigure(0, weight=1)
        canvas_frame.grid_columnconfigure(0, weight=1)
        
        # Store canvas reference for refresh
        self.graph_canvas = canvas
        self.graph_window = graph_window
        
        # Draw the graph
        self.draw_commit_graph(canvas)
    
    def draw_commit_graph(self, canvas):
        """Draw commit graph with branches"""
        try:
            # Clear canvas
            canvas.delete("all")
            
            # Get commits from all branches
            all_commits = {}
            branch_commits = {}
            
            # Get commits from each branch
            for branch in self.repo.branches:
                try:
                    commits = list(self.repo.iter_commits(branch.name, max_count=30))
                    branch_commits[branch.name] = commits
                    for commit in commits:
                        if commit.hexsha not in all_commits:
                            all_commits[commit.hexsha] = {
                                'commit': commit,
                                'branches': [branch.name],
                                'x': 0, 'y': 0
                            }
                        else:
                            all_commits[commit.hexsha]['branches'].append(branch.name)
                except:
                    continue
            
            if not all_commits:
                canvas.create_text(200, 100, text="No commits found", font=('Arial', 16), fill='red')
                return
            
            # Sort commits by date
            sorted_commits = sorted(all_commits.values(), 
                                   key=lambda x: x['commit'].committed_datetime, reverse=True)
            
            # Calculate layout
            commit_width = 200
            commit_height = 120
            margin_x = 30
            margin_y = 50
            branch_y_offset = 150
            
            # Assign colors to branches
            branch_colors = {}
            colors = ['lightblue', 'lightgreen', 'lightcoral', 'lightyellow', 'lightpink', 'lightgray']
            for i, branch_name in enumerate(branch_commits.keys()):
                branch_colors[branch_name] = colors[i % len(colors)]
            
            # Draw commits
            for i, commit_data in enumerate(sorted_commits):
                commit = commit_data['commit']
                branches = commit_data['branches']
                
                # Calculate position
                x = i * (commit_width + margin_x) + margin_x
                y = margin_y
                
                # Use primary branch color
                primary_branch = branches[0] if branches else 'main'
                fill_color = branch_colors.get(primary_branch, 'lightblue')
                
                # Draw commit rectangle
                rect = canvas.create_rectangle(x, y, x + commit_width, y + commit_height, 
                                             fill=fill_color, outline='blue', width=2)
                
                # Add commit info
                version_num = len(sorted_commits) - i
                canvas.create_text(x + commit_width//2, y + 15, 
                                 text=f"Version {version_num}", 
                                 font=('Arial', 10, 'bold'), anchor='center')
                
                canvas.create_text(x + commit_width//2, y + 35, 
                                 text=f"Hash: {commit.hexsha[:8]}", 
                                 font=('Arial', 8), anchor='center')
                
                canvas.create_text(x + commit_width//2, y + 50, 
                                 text=f"Author: {commit.author.name[:20]}", 
                                 font=('Arial', 8), anchor='center')
                
                canvas.create_text(x + commit_width//2, y + 65, 
                                 text=commit.committed_datetime.strftime('%Y-%m-%d %H:%M'), 
                                 font=('Arial', 7), anchor='center')
                
                # Branch info
                branch_text = ", ".join(branches[:2])
                if len(branches) > 2:
                    branch_text += f" (+{len(branches)-2})"
                canvas.create_text(x + commit_width//2, y + 80, 
                                 text=f"Branches: {branch_text}", 
                                 font=('Arial', 7), anchor='center')
                
                # Message (truncated)
                message = commit.message.strip()[:25] + "..." if len(commit.message.strip()) > 25 else commit.message.strip()
                canvas.create_text(x + commit_width//2, y + 95, 
                                 text=message, 
                                 font=('Arial', 7), anchor='center')
                
                # Current HEAD indicator
                try:
                    if commit == self.repo.head.commit:
                        canvas.create_text(x + commit_width//2, y + 110, 
                                         text="← HEAD", 
                                         font=('Arial', 8, 'bold'), fill='red', anchor='center')
                except:
                    pass
                
                # Draw connection line to next commit
                if i < len(sorted_commits) - 1:
                    canvas.create_line(x + commit_width, y + commit_height//2,
                                     x + commit_width + margin_x, y + commit_height//2,
                                     fill='green', width=3, arrow=tk.LAST)
                
                # Make clickable with commit operations
                canvas.tag_bind(rect, "<Button-1>", 
                               lambda e, c=commit: self.show_commit_operations(c))
                canvas.tag_bind(rect, "<Double-1>", 
                               lambda e, c=commit: self.checkout_commit(c.hexsha))
                
                # Store position for branch lines
                commit_data['x'] = x + commit_width//2
                commit_data['y'] = y + commit_height//2
            
            # Draw branch lines
            self.draw_branch_lines(canvas, branch_commits, sorted_commits, branch_colors, 
                                 commit_width, margin_x, branch_y_offset)
            
            # Update scroll region
            total_width = len(sorted_commits) * (commit_width + margin_x) + margin_x
            canvas.configure(scrollregion=(0, 0, total_width, commit_height + branch_y_offset + 100))
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to create version graph: {str(e)}")
            canvas.create_text(200, 100, text=f"Error: {str(e)}", font=('Arial', 12), fill='red')
    
    def draw_branch_lines(self, canvas, branch_commits, sorted_commits, branch_colors, 
                         commit_width, margin_x, branch_y_offset):
        """Draw branch lines below commits"""
        y_start = 200  # Below commits
        
        for i, (branch_name, commits) in enumerate(branch_commits.items()):
            y_pos = y_start + i * 30
            color = branch_colors.get(branch_name, 'blue')
            
            # Draw branch name
            canvas.create_text(10, y_pos, text=branch_name, 
                             font=('Arial', 9, 'bold'), fill=color, anchor='w')
            
            # Draw branch line
            branch_commits_sorted = sorted(commits, key=lambda x: x.committed_datetime, reverse=True)
            
            prev_x = None
            for commit in branch_commits_sorted:
                # Find commit position in sorted list
                for j, commit_data in enumerate(sorted_commits):
                    if commit_data['commit'] == commit:
                        x = j * (commit_width + margin_x) + margin_x + commit_width//2
                        
                        # Draw dot on branch line
                        canvas.create_oval(x-3, y_pos-3, x+3, y_pos+3, 
                                         fill=color, outline=color)
                        
                        # Connect to previous commit on this branch
                        if prev_x is not None:
                            canvas.create_line(prev_x, y_pos, x, y_pos, 
                                             fill=color, width=2)
                        
                        prev_x = x
                        break
    
    def show_commit_operations(self, commit):
        """Show operations menu for a commit"""
        ops_window = tk.Toplevel(self.root)
        ops_window.title(f"Commit Operations: {commit.hexsha[:8]}")
        ops_window.geometry("400x300")
        
        # Commit info
        info_frame = ttk.LabelFrame(ops_window, text="Commit Information")
        info_frame.pack(fill=tk.X, padx=10, pady=10)
        
        ttk.Label(info_frame, text=f"Hash: {commit.hexsha[:8]}").pack(anchor=tk.W, padx=5, pady=2)
        ttk.Label(info_frame, text=f"Author: {commit.author.name}").pack(anchor=tk.W, padx=5, pady=2)
        ttk.Label(info_frame, text=f"Date: {commit.committed_datetime}").pack(anchor=tk.W, padx=5, pady=2)
        ttk.Label(info_frame, text=f"Message: {commit.message.strip()}").pack(anchor=tk.W, padx=5, pady=2)
        
        # Operations
        ops_frame = ttk.LabelFrame(ops_window, text="Operations")
        ops_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        ttk.Button(ops_frame, text="Checkout this Commit", 
                  command=lambda: self.checkout_commit_and_close(commit.hexsha, ops_window)).pack(fill=tk.X, padx=5, pady=2)
        
        ttk.Button(ops_frame, text="Edit Commit Message", 
                  command=lambda: self.edit_commit_message_advanced(commit, ops_window)).pack(fill=tk.X, padx=5, pady=2)
        
        ttk.Button(ops_frame, text="View Files Changed", 
                  command=lambda: self.open_commit_details(commit)).pack(fill=tk.X, padx=5, pady=2)
        
        ttk.Button(ops_frame, text="Create Branch from Here", 
                  command=lambda: self.create_branch_from_commit(commit, ops_window)).pack(fill=tk.X, padx=5, pady=2)
        
        ttk.Button(ops_window, text="Close", command=ops_window.destroy).pack(pady=10)
    
    def checkout_commit(self, commit_hash):
        """Checkout to specific commit"""
        if messagebox.askyesno("Checkout Commit", 
                              f"Checkout to commit {commit_hash[:8]}?\nThis will detach HEAD."):
            try:
                self.repo.git.checkout(commit_hash)
                self.refresh_all()
                self.status_label.config(text=f"Checked out to commit {commit_hash[:8]} (HEAD detached)")
                
                # Refresh graph if open
                if hasattr(self, 'graph_canvas'):
                    self.draw_commit_graph(self.graph_canvas)
                    
            except Exception as e:
                messagebox.showerror("Checkout Error", str(e))
    
    def checkout_commit_and_close(self, commit_hash, window):
        """Checkout commit and close window"""
        self.checkout_commit(commit_hash)
        window.destroy()
    
    def refresh_graph(self, canvas, window):
        """Refresh the commit graph"""
        self.draw_commit_graph(canvas)
    
    def open_commit_details(self, commit):
        """Open detailed view for a specific commit"""
        details_window = tk.Toplevel(self.root)
        details_window.title(f"Commit Details: {commit.hexsha[:8]}")
        details_window.geometry("1000x700")
        
        # Create paned window
        paned = ttk.PanedWindow(details_window, orient=tk.HORIZONTAL)
        paned.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Left side - commit info and actions
        left_frame = ttk.Frame(paned)
        paned.add(left_frame, weight=1)
        
        # Commit info
        info_frame = ttk.LabelFrame(left_frame, text="Commit Information")
        info_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Label(info_frame, text=f"Hash: {commit.hexsha}").pack(anchor=tk.W, padx=5, pady=2)
        ttk.Label(info_frame, text=f"Author: {commit.author.name} <{commit.author.email}>").pack(anchor=tk.W, padx=5, pady=2)
        ttk.Label(info_frame, text=f"Date: {commit.committed_datetime}").pack(anchor=tk.W, padx=5, pady=2)
        
        # Message frame (editable)
        msg_frame = ttk.LabelFrame(info_frame, text="Message")
        msg_frame.pack(fill=tk.X, padx=5, pady=5)
        
        self.commit_message_text = tk.Text(msg_frame, height=3, wrap=tk.WORD)
        self.commit_message_text.pack(fill=tk.X, padx=5, pady=5)
        self.commit_message_text.insert('1.0', commit.message.strip())
        
        # Action buttons
        action_frame = ttk.Frame(left_frame)
        action_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Button(action_frame, text="Edit Message", 
                  command=lambda: self.edit_commit_message_inline(commit)).pack(side=tk.LEFT, padx=2)
        ttk.Button(action_frame, text="Revert Commit", 
                  command=lambda: self.revert_commit(commit)).pack(side=tk.LEFT, padx=2)
        ttk.Button(action_frame, text="Cherry Pick", 
                  command=lambda: self.cherry_pick_commit(commit)).pack(side=tk.LEFT, padx=2)
        
        # Right side - files changed
        right_frame = ttk.Frame(paned)
        paned.add(right_frame, weight=2)
        
        ttk.Label(right_frame, text="Files Changed", font=('TkDefaultFont', 10, 'bold')).pack(anchor=tk.W, padx=5)
        
        files_columns = ('File', 'Status', 'Changes')
        files_tree = ttk.Treeview(right_frame, columns=files_columns, show='headings')
        
        for col in files_columns:
            files_tree.heading(col, text=col)
            files_tree.column(col, width=200)
        
        # Context menu for files in commit
        file_commit_menu = tk.Menu(self.root, tearoff=0)
        file_commit_menu.add_command(label="View File at This Commit", 
                                    command=lambda: self.view_file_at_commit_from_tree(files_tree, commit))
        file_commit_menu.add_command(label="Compare with Current", 
                                    command=lambda: self.compare_file_with_current(files_tree, commit))
        
        def show_file_commit_menu(event):
            try:
                file_commit_menu.tk_popup(event.x_root, event.y_root)
            finally:
                file_commit_menu.grab_release()
        
        files_tree.bind('<Button-3>', show_file_commit_menu)
        files_tree.bind('<Double-1>', lambda e: self.view_file_at_commit_from_tree(files_tree, commit))
        
        # Populate files
        try:
            if commit.parents:
                diffs = commit.parents[0].diff(commit)
                for diff in diffs:
                    status = 'Modified'
                    if diff.new_file:
                        status = 'Added'
                    elif diff.deleted_file:
                        status = 'Deleted'
                    elif diff.renamed_file:
                        status = 'Renamed'
                    
                    file_path = diff.b_path or diff.a_path
                    
                    try:
                        if diff.diff:
                            additions = diff.diff.decode('utf-8').count('\n+')
                            deletions = diff.diff.decode('utf-8').count('\n-')
                            changes = f"+{additions} -{deletions}"
                        else:
                            changes = "Binary"
                    except:
                        changes = "Modified"
                    
                    files_tree.insert('', 'end', values=(file_path, status, changes))
            else:
                # First commit
                for item in commit.tree.traverse():
                    if item.type == 'blob':
                        files_tree.insert('', 'end', values=(item.path, 'Added', 'New'))
        except Exception as e:
            messagebox.showerror("Error", f"Failed to get commit files: {str(e)}")
        
        files_tree.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
    
    
    def edit_commit_message(self):
        """Fixed commit message editing with proper window sizing and error handling"""
        if not self.repo:
            messagebox.showerror("Error", "No repository loaded")
            return
        
        # Check if there are any uncommitted changes
        try:
            if self.repo.is_dirty():
                if not messagebox.askyesno("Uncommitted Changes", 
                                        "You have uncommitted changes. Editing commit messages requires a clean working directory.\n\n" +
                                        "Do you want to continue anyway? (Changes will be stashed temporarily)"):
                    return
        except:
            pass
        
        # Create commit selection window with proper sizing
        edit_window = tk.Toplevel(self.root)
        edit_window.title("Edit Commit Message")
        edit_window.geometry("1200x700")  # Increased height
        edit_window.minsize(1000, 600)   # Minimum size
        
        # Make window resizable
        edit_window.resizable(True, True)
        
        # Header frame
        header_frame = ttk.Frame(edit_window)
        header_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Label(header_frame, text="Edit Commit Message", 
                font=('TkDefaultFont', 14, 'bold')).pack(side=tk.LEFT)
        
        # Warning frame - more prominent
        warning_frame = ttk.LabelFrame(edit_window, text="⚠️ Important Warning")
        warning_frame.pack(fill=tk.X, padx=10, pady=5)
        
        warning_text = tk.Text(warning_frame, height=3, wrap=tk.WORD, 
                            font=('TkDefaultFont', 9), fg='red', bg='#fff3cd')
        warning_text.pack(fill=tk.X, padx=5, pady=5)
        
        warning_msg = """⚠️ CAUTION: Editing commit messages rewrites Git history!
    • Only edit messages if you haven't pushed to a shared repository
    • This will change commit hashes and may affect other developers
    • Consider the impact before proceeding with historical commits"""
        
        warning_text.insert('1.0', warning_msg)
        warning_text.config(state=tk.DISABLED)
        
        # Main content frame
        main_frame = ttk.Frame(edit_window)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # Commits selection frame
        commits_frame = ttk.LabelFrame(main_frame, text="Select Commit to Edit")
        commits_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        
        # Treeview for commits
        columns = ('Position', 'Hash', 'Date', 'Author', 'Current Message')
        commits_tree = ttk.Treeview(commits_frame, columns=columns, show='headings', height=12)
        
        # Configure columns with proper widths
        commits_tree.heading('Position', text='Position')
        commits_tree.column('Position', width=100, minwidth=80)
        
        commits_tree.heading('Hash', text='Hash')
        commits_tree.column('Hash', width=120, minwidth=100)
        
        commits_tree.heading('Date', text='Date')
        commits_tree.column('Date', width=180, minwidth=150)
        
        commits_tree.heading('Author', text='Author')
        commits_tree.column('Author', width=150, minwidth=120)
        
        commits_tree.heading('Current Message', text='Current Message')
        commits_tree.column('Current Message', width=400, minwidth=300)
        
        # Scrollbar for commits
        commits_scroll = ttk.Scrollbar(commits_frame, orient=tk.VERTICAL, command=commits_tree.yview)
        commits_tree.configure(yscrollcommand=commits_scroll.set)
        
        # Pack commits tree
        commits_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)
        commits_scroll.pack(side=tk.RIGHT, fill=tk.Y, pady=5)
        
        # Message editing frame
        message_frame = ttk.LabelFrame(main_frame, text="Edit Message")
        message_frame.pack(fill=tk.X, pady=5)
        
        # Current message display
        current_frame = ttk.Frame(message_frame)
        current_frame.pack(fill=tk.X, padx=5, pady=2)
        
        ttk.Label(current_frame, text="Current Message:", font=('TkDefaultFont', 9, 'bold')).pack(anchor=tk.W)
        current_msg_text = tk.Text(current_frame, height=3, wrap=tk.WORD, state=tk.DISABLED, 
                                font=('TkDefaultFont', 9), bg='#f8f9fa')
        current_msg_text.pack(fill=tk.X, pady=2)
        
        # New message input
        new_frame = ttk.Frame(message_frame)
        new_frame.pack(fill=tk.X, padx=5, pady=2)
        
        ttk.Label(new_frame, text="New Message:", font=('TkDefaultFont', 9, 'bold')).pack(anchor=tk.W)
        new_msg_text = tk.Text(new_frame, height=3, wrap=tk.WORD, font=('TkDefaultFont', 9))
        new_msg_text.pack(fill=tk.X, pady=2)
        
        # Buttons frame - Fixed positioning
        button_frame = ttk.Frame(edit_window)
        button_frame.pack(fill=tk.X, padx=10, pady=10, side=tk.BOTTOM)
        
        # Populate commits (last 15 commits)
        try:
            commits = list(self.repo.iter_commits(max_count=15))
            for i, commit in enumerate(commits):
                position = "HEAD" if i == 0 else f"HEAD~{i}"
                message = commit.message.strip().replace('\n', ' ')
                if len(message) > 60:
                    message = message[:60] + "..."
                
                # Color code based on position
                tags = ('head_commit',) if i == 0 else ('normal_commit',)
                
                commits_tree.insert('', 'end', values=(
                    position,
                    commit.hexsha[:12],
                    commit.committed_datetime.strftime('%Y-%m-%d %H:%M:%S'),
                    commit.author.name,
                    message
                ), tags=tags)
            
            # Configure row colors
            commits_tree.tag_configure('head_commit', background='#e8f5e8')
            commits_tree.tag_configure('normal_commit', background='white')
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load commits: {str(e)}")
            edit_window.destroy()
            return
        
        # Selection handler
        def on_commit_select(event):
            selection = commits_tree.selection()
            if selection:
                values = commits_tree.item(selection[0])['values']
                commit_hash = values[1]
                
                # Find the commit and update text areas
                for commit in commits:
                    if commit.hexsha.startswith(commit_hash):
                        # Update current message
                        current_msg_text.config(state=tk.NORMAL)
                        current_msg_text.delete('1.0', tk.END)
                        current_msg_text.insert('1.0', commit.message.strip())
                        current_msg_text.config(state=tk.DISABLED)
                        
                        # Update new message
                        new_msg_text.delete('1.0', tk.END)
                        new_msg_text.insert('1.0', commit.message.strip())
                        new_msg_text.focus_set()
                        break
        
        commits_tree.bind('<<TreeviewSelect>>', on_commit_select)
        
        # Button functions
        def edit_selected_commit():
            selection = commits_tree.selection()
            if not selection:
                messagebox.showwarning("No Selection", "Please select a commit to edit")
                return
            
            values = commits_tree.item(selection[0])['values']
            position = values[0]
            commit_hash = values[1]
            new_message = new_msg_text.get('1.0', tk.END).strip()
            
            if not new_message:
                messagebox.showerror("Error", "Please enter a new commit message")
                new_msg_text.focus_set()
                return
            
            # Find the commit
            selected_commit = None
            for commit in commits:
                if commit.hexsha.startswith(commit_hash):
                    selected_commit = commit
                    break
            
            if not selected_commit:
                messagebox.showerror("Error", "Could not find selected commit")
                return
            
            # Check if message is different
            if new_message == selected_commit.message.strip():
                messagebox.showinfo("No Change", "The message is unchanged")
                return
            
            # Show final confirmation with risk assessment
            if position == "HEAD":
                risk_level = "LOW"
                risk_msg = "This will amend the last commit (HEAD). This is relatively safe if you haven't pushed yet."
            else:
                risk_level = "HIGH"
                risk_msg = f"This will rewrite Git history from {position} onward. This is risky if you've already pushed these commits."
            
            confirm_msg = f"""Edit commit message for {position}?

    Risk Level: {risk_level}
    {risk_msg}

    New message: {new_message[:100]}{'...' if len(new_message) > 100 else ''}

    Are you sure you want to proceed?"""
            
            if not messagebox.askyesno("Final Confirmation", confirm_msg):
                return
            
            # Disable window during operation
            edit_window.config(cursor="wait")
            for child in edit_window.winfo_children():
                child.config(state=tk.DISABLED)
            
            # Edit the commit message
            def edit_commit():
                try:
                    if position == "HEAD":
                        # Simple amend for HEAD
                        self.repo.git.commit('--amend', '-m', new_message)
                        self.root.after(0, lambda: show_success("HEAD commit message updated successfully!"))
                    else:
                        # Interactive rebase for older commits
                        self.edit_commit_message_python_only(selected_commit, new_message)
                    
                except Exception as e:
                    self.root.after(0, lambda: show_error(f"Failed to edit commit message: {str(e)}"))
            
            def show_success(msg):
                edit_window.destroy()
                messagebox.showinfo("Success", msg)
                self.refresh_all()
                if hasattr(self, 'graph_canvas'):
                    self.draw_commit_graph(self.graph_canvas)
            
            def show_error(msg):
                edit_window.config(cursor="")
                for child in edit_window.winfo_children():
                    child.config(state=tk.NORMAL)
                messagebox.showerror("Error", msg)
            
            # Run in background thread
            threading.Thread(target=edit_commit, daemon=True).start()
        
        def cancel_edit():
            edit_window.destroy()
        
        # Create buttons with proper spacing
        ttk.Button(button_frame, text="Edit Message", command=edit_selected_commit, 
                style='Success.TButton', width=15).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(button_frame, text="Cancel", command=cancel_edit, 
                width=15).pack(side=tk.RIGHT, padx=5)
        
        # Help button
        def show_help():
            help_text = """Commit Message Editing Help:

    HEAD Commit (Safe):
    • Changes only the last commit message
    • Safe if you haven't pushed yet
    • Uses 'git commit --amend'

    Historical Commits (Risky):
    • Rewrites Git history from that point
    • Changes all subsequent commit hashes
    • Only do this if you haven't pushed or shared the commits
    • Uses interactive rebase

    Best Practices:
    • Only edit unpushed commits
    • Communicate with team before editing shared history
    • Always backup important work
    • Test on a copy of the repository first"""
            
            messagebox.showinfo("Help", help_text)
        
        ttk.Button(button_frame, text="Help", command=show_help, 
                width=10).pack(side=tk.LEFT, padx=20)
        
        # Select HEAD by default
        if commits_tree.get_children():
            first_item = commits_tree.get_children()[0]
            commits_tree.selection_set(first_item)
            commits_tree.see(first_item)
            on_commit_select(None)
        
        # Focus on new message text
        new_msg_text.focus_set()


    
    def show_commit_edit_safety_dialog(self):
        """Show dialog about commit editing safety"""
        safe, message = self.is_commit_editing_safe()
        
        if safe is None:
            messagebox.showwarning("Safety Check Failed", message)
            return True
        elif safe:
            messagebox.showinfo("Safe to Edit", f"✅ {message}")
            return True
        else:
            return messagebox.askyesno("Risky Operation", 
                f"⚠️ {message}\n\nEditing commit messages will rewrite Git history and may cause issues for other developers.\n\nDo you want to proceed anyway?")


    # Enhanced version with safety checks
    def edit_commit_message_with_safety(self):
        """Edit commit message with safety checks"""
        if not self.repo:
            messagebox.showerror("Error", "No repository loaded")
            return
        
        # Check safety first
        if not self.show_commit_edit_safety_dialog():
            return
        
        # Proceed with editing
        self.edit_commit_message()


    # Simple alternative for just HEAD commit
    def edit_head_commit_message(self):
        """Simple dialog to edit just the HEAD commit message"""
        if not self.repo:
            messagebox.showerror("Error", "No repository loaded")
            return
        
        try:
            head_commit = self.repo.head.commit
            current_message = head_commit.message.strip()
            
            # Simple input dialog
            new_message = simpledialog.askstring(
                "Edit HEAD Commit Message",
                "Enter new commit message:",
                initialvalue=current_message
            )
            
            if new_message and new_message.strip() != current_message:
                if messagebox.askyesno("Confirm", "Amend the last commit with new message?"):
                    self.repo.git.commit('--amend', '-m', new_message.strip())
                    messagebox.showinfo("Success", "HEAD commit message updated!")
                    self.refresh_all()
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to edit commit message: {str(e)}")


    def edit_commit_message_interactive(self, commit, new_message):
        """Edit commit message using interactive rebase"""
        try:
            # Create a temporary script for the rebase
            import tempfile
            
            # Get the commit before the one we want to edit
            parent_commit = commit.parents[0] if commit.parents else None
            
            if not parent_commit:
                # This is the root commit, use --root
                rebase_cmd = ['git', 'rebase', '--root', '-i']
            else:
                rebase_cmd = ['git', 'rebase', '-i', parent_commit.hexsha]
            
            # Create environment for the rebase
            env = os.environ.copy()
            
            # Create a custom editor script
            with tempfile.NamedTemporaryFile(mode='w', suffix='.sh', delete=False) as script_file:
                script_content = f'''#!/bin/bash
    # Custom rebase script
    if [ "$1" = "git-rebase-todo" ]; then
        # Replace 'pick' with 'reword' for our target commit
        sed -i 's/pick {commit.hexsha[:7]}/reword {commit.hexsha[:7]}/' "$2"
    elif [ "$1" = "COMMIT_EDITMSG" ]; then
        # Replace the commit message
        echo "{new_message}" > "$2"
    fi
    '''
                script_file.write(script_content)
                script_path = script_file.name
            
            # Make script executable
            os.chmod(script_path, 0o755)
            
            # Set custom editor
            env['GIT_EDITOR'] = script_path
            
            # Run the rebase
            subprocess.run(rebase_cmd, cwd=self.repo_path, env=env, check=True)
            
            # Clean up
            os.unlink(script_path)
            
            messagebox.showinfo("Success", f"Commit message updated successfully!\n\nNote: Git history has been rewritten.")
            
        except subprocess.CalledProcessError as e:
            messagebox.showerror("Rebase Error", f"Failed to edit commit message: {str(e)}")
        except Exception as e:
            messagebox.showerror("Error", f"Unexpected error: {str(e)}")


    def create_branch_from_commit(self, commit, parent_window):
        """Create branch from specific commit"""
        branch_name = simpledialog.askstring("Create Branch", "Enter new branch name:")
        if branch_name:
            try:
                new_branch = self.repo.create_head(branch_name, commit)
                if messagebox.askyesno("Switch Branch", f"Switch to new branch '{branch_name}'?"):
                    new_branch.checkout()
                    self.refresh_all()
                
                messagebox.showinfo("Success", f"Branch '{branch_name}' created from {commit.hexsha[:8]}")
                parent_window.destroy()
            except Exception as e:
                messagebox.showerror("Error", f"Failed to create branch: {str(e)}")
    
    def edit_commit_message_inline(self, commit):
        """Edit commit message inline"""
        new_message = self.commit_message_text.get('1.0', tk.END).strip()
        
        if new_message == commit.message.strip():
            messagebox.showinfo("No Change", "Message is unchanged")
            return
        
        if messagebox.askyesno("Confirm", "This will rewrite Git history. Continue?"):
            try:
                # Use git commit --amend for the last commit
                if commit == self.repo.head.commit:
                    self.repo.git.commit('--amend', '-m', new_message)
                    messagebox.showinfo("Success", "Commit message updated")
                else:
                    messagebox.showwarning("Warning", "Can only edit the last commit message safely")
                
                self.refresh_all()
            except Exception as e:
                messagebox.showerror("Error", f"Failed to edit commit message: {str(e)}")
    
    def revert_commit(self, commit):
        """Revert a specific commit"""
        if messagebox.askyesno("Confirm Revert", f"Revert commit {commit.hexsha[:8]}?"):
            try:
                self.repo.git.revert(commit.hexsha, '--no-edit')
                messagebox.showinfo("Success", "Commit reverted")
                self.refresh_all()
            except Exception as e:
                messagebox.showerror("Error", f"Failed to revert commit: {str(e)}")
    
    def cherry_pick_commit(self, commit):
        """Cherry pick a specific commit"""
        if messagebox.askyesno("Confirm Cherry Pick", f"Cherry pick commit {commit.hexsha[:8]}?"):
            try:
                self.repo.git.cherry_pick(commit.hexsha)
                messagebox.showinfo("Success", "Commit cherry picked")
                self.refresh_all()
            except Exception as e:
                messagebox.showerror("Error", f"Failed to cherry pick commit: {str(e)}")
    
    def view_file_at_commit_from_tree(self, tree, commit):
        """View file at commit from tree selection"""
        selection = tree.selection()
        if selection:
            file_path = tree.item(selection[0])['values'][0]
            self.show_file_at_commit(file_path, commit.hexsha)
    
    def compare_file_with_current(self, tree, commit):
        """Compare file in commit with current version"""
        selection = tree.selection()
        if selection:
            file_path = tree.item(selection[0])['values'][0]
            
            compare_window = tk.Toplevel(self.root)
            compare_window.title(f"Compare: {file_path}")
            compare_window.geometry("1400x800")
            
            # Create side-by-side comparison
            main_frame = ttk.Frame(compare_window)
            main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
            
            # Left side - commit version
            left_frame = ttk.LabelFrame(main_frame, text=f"Commit {commit.hexsha[:8]}")
            left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5)
            
            left_text = tk.Text(left_frame, font=('Courier', 9), wrap=tk.NONE)
            left_text.pack(fill=tk.BOTH, expand=True)
            
            # Right side - current version
            right_frame = ttk.LabelFrame(main_frame, text="Current Version")
            right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=5)
            
            right_text = tk.Text(right_frame, font=('Courier', 9), wrap=tk.NONE)
            right_text.pack(fill=tk.BOTH, expand=True)
            
            try:
                # Get commit version
                try:
                    commit_content = commit.tree[file_path].data_stream.read().decode('utf-8')
                    left_text.insert('1.0', commit_content)
                except:
                    left_text.insert('1.0', "File not found in commit or binary file")
                
                # Get current version
                current_path = os.path.join(self.repo_path, file_path)
                if os.path.exists(current_path):
                    with open(current_path, 'r', encoding='utf-8') as f:
                        current_content = f.read()
                        right_text.insert('1.0', current_content)
                else:
                    right_text.insert('1.0', "File not found in current working directory")
                
                left_text.config(state=tk.DISABLED)
                right_text.config(state=tk.DISABLED)
                
            except Exception as e:
                messagebox.showerror("Error", f"Failed to compare files: {str(e)}")
    
    # Additional stub methods for menu functionality
    def show_vertical_timeline(self):
        """Show vertical timeline view from oldest to newest"""
        if not self.repo:
            messagebox.showerror("Error", "No repository loaded")
            return
        
        timeline_window = tk.Toplevel(self.root)
        timeline_window.title("Timeline View - Vertical")
        timeline_window.geometry("1200x800")
        
        # Create main frame with scrollable area
        main_frame = ttk.Frame(timeline_window)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Create paned window
        paned = ttk.PanedWindow(main_frame, orient=tk.HORIZONTAL)
        paned.pack(fill=tk.BOTH, expand=True)
        
        # Left side - timeline
        left_frame = ttk.Frame(paned)
        paned.add(left_frame, weight=1)
        
        ttk.Label(left_frame, text="Commit Timeline", font=('TkDefaultFont', 12, 'bold')).pack(pady=5)
        
        # Timeline with scrollbar
        timeline_frame = ttk.Frame(left_frame)
        timeline_frame.pack(fill=tk.BOTH, expand=True)
        
        # Create canvas for timeline
        timeline_canvas = tk.Canvas(timeline_frame, bg='white', width=600)
        timeline_scroll = ttk.Scrollbar(timeline_frame, orient=tk.VERTICAL, command=timeline_canvas.yview)
        timeline_canvas.configure(yscrollcommand=timeline_scroll.set)
        
        timeline_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        timeline_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Enable mouse wheel scrolling
        def on_mousewheel(event):
            timeline_canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        
        timeline_canvas.bind("<MouseWheel>", on_mousewheel)
        timeline_canvas.bind("<Button-4>", lambda e: timeline_canvas.yview_scroll(-1, "units"))
        timeline_canvas.bind("<Button-5>", lambda e: timeline_canvas.yview_scroll(1, "units"))
        
        # Right side - details
        right_frame = ttk.Frame(paned)
        paned.add(right_frame, weight=1)
        
        ttk.Label(right_frame, text="Commit Details", font=('TkDefaultFont', 12, 'bold')).pack(pady=5)
        
        # Details text area
        details_frame = ttk.Frame(right_frame)
        details_frame.pack(fill=tk.BOTH, expand=True)
        
        self.timeline_details_text = tk.Text(details_frame, wrap=tk.WORD, height=10)
        details_scroll = ttk.Scrollbar(details_frame, orient=tk.VERTICAL, command=self.timeline_details_text.yview)
        self.timeline_details_text.configure(yscrollcommand=details_scroll.set)
        
        self.timeline_details_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        details_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Files changed area
        files_frame = ttk.LabelFrame(right_frame, text="Files Changed")
        files_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        
        files_columns = ('File', 'Status', 'Changes')
        self.timeline_files_tree = ttk.Treeview(files_frame, columns=files_columns, show='headings', height=8)
        
        for col in files_columns:
            self.timeline_files_tree.heading(col, text=col)
            self.timeline_files_tree.column(col, width=150)
        
        files_tree_scroll = ttk.Scrollbar(files_frame, orient=tk.VERTICAL, command=self.timeline_files_tree.yview)
        self.timeline_files_tree.configure(yscrollcommand=files_tree_scroll.set)
        
        self.timeline_files_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        files_tree_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Draw timeline
        self.draw_vertical_timeline(timeline_canvas)
        
        # Store references
        self.timeline_canvas = timeline_canvas
        self.timeline_window = timeline_window
    
    def draw_vertical_timeline(self, canvas):
        """Draw vertical timeline from oldest to newest"""
        try:
            # Get all commits (reversed to show oldest first)
            commits = list(reversed(list(self.repo.iter_commits(max_count=100))))
            
            if not commits:
                canvas.create_text(300, 100, text="No commits found", font=('Arial', 16), fill='red')
                return
            
            # Calculate dimensions
            item_height = 120
            item_width = 550
            margin = 30
            
            total_height = len(commits) * item_height + 2 * margin
            canvas.configure(scrollregion=(0, 0, 600, total_height))
            
            # Get branch and tag info
            branch_info = {}
            tag_info = {}
            
            # Map commits to branches
            for branch in self.repo.branches:
                try:
                    for commit in self.repo.iter_commits(branch.name):
                        if commit.hexsha not in branch_info:
                            branch_info[commit.hexsha] = []
                        branch_info[commit.hexsha].append(branch.name)
                except:
                    continue
            
            # Map commits to tags
            for tag in self.repo.tags:
                if tag.commit.hexsha not in tag_info:
                    tag_info[tag.commit.hexsha] = []
                tag_info[tag.commit.hexsha].append(tag.name)
            
            # Draw timeline line
            canvas.create_line(50, margin, 50, total_height - margin, fill='blue', width=4)
            
            # Draw commits
            for i, commit in enumerate(commits):
                y = margin + i * item_height
                
                # Draw commit circle
                canvas.create_oval(45, y + 55, 55, y + 65, fill='red', outline='darkred', width=2)
                
                # Draw commit box
                is_head = False
                try:
                    is_head = (commit == self.repo.head.commit)
                except:
                    pass
                
                box_color = 'lightgreen' if is_head else 'lightblue'
                rect = canvas.create_rectangle(80, y + 10, 80 + item_width, y + 100, 
                                             fill=box_color, outline='blue', width=2)
                
                # Version number
                version_num = i + 1
                canvas.create_text(90, y + 25, text=f"Version {version_num}", 
                                 font=('Arial', 10, 'bold'), anchor='w')
                
                # Hash
                canvas.create_text(90, y + 40, text=f"Hash: {commit.hexsha[:12]}", 
                                 font=('Arial', 9), anchor='w')
                
                # Author and date
                canvas.create_text(90, y + 55, text=f"Author: {commit.author.name}", 
                                 font=('Arial', 9), anchor='w')
                canvas.create_text(90, y + 70, text=f"Date: {commit.committed_datetime.strftime('%Y-%m-%d %H:%M:%S')}", 
                                 font=('Arial', 9), anchor='w')
                
                # Branches and tags
                branch_text = ""
                if commit.hexsha in branch_info:
                    branches = branch_info[commit.hexsha][:3]  # Show max 3 branches
                    branch_text = f"Branches: {', '.join(branches)}"
                    if len(branch_info[commit.hexsha]) > 3:
                        branch_text += f" (+{len(branch_info[commit.hexsha]) - 3})"
                
                if commit.hexsha in tag_info:
                    tags = tag_info[commit.hexsha][:2]  # Show max 2 tags
                    tag_text = f"Tags: {', '.join(tags)}"
                    if len(tag_info[commit.hexsha]) > 2:
                        tag_text += f" (+{len(tag_info[commit.hexsha]) - 2})"
                    branch_text += f" | {tag_text}" if branch_text else tag_text
                
                if branch_text:
                    canvas.create_text(90, y + 85, text=branch_text, 
                                     font=('Arial', 8), anchor='w', fill='darkgreen')
                
                # HEAD indicator
                if is_head:
                    canvas.create_text(550, y + 25, text="← HEAD", 
                                     font=('Arial', 10, 'bold'), fill='red', anchor='w')
                
                # Message (on hover or click)
                canvas.tag_bind(rect, "<Button-1>", 
                               lambda e, c=commit: self.show_timeline_commit_details(c))
                
                # Store commit reference
                canvas.create_text(90, y + 5, text="", tags=f"commit_{commit.hexsha}")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to draw timeline: {str(e)}")
            canvas.create_text(300, 100, text=f"Error: {str(e)}", font=('Arial', 12), fill='red')

    def show_timeline_commit_details(self, commit):
        """Show commit details in timeline right pane"""
        try:
            # Update details text
            self.timeline_details_text.delete('1.0', tk.END)
            
            details = f"Commit: {commit.hexsha}\n"
            details += f"Author: {commit.author.name} <{commit.author.email}>\n"
            details += f"Date: {commit.committed_datetime}\n"
            details += f"Message:\n{commit.message.strip()}\n\n"
            
            # Add parent info
            if commit.parents:
                details += f"Parents: {', '.join([p.hexsha[:8] for p in commit.parents])}\n"
            else:
                details += "Parents: None (initial commit)\n"
            
            # Add branch/tag info
            branch_info = []
            for branch in self.repo.branches:
                try:
                    if commit in list(self.repo.iter_commits(branch.name)):
                        branch_info.append(branch.name)
                except:
                    continue
            
            if branch_info:
                details += f"Branches: {', '.join(branch_info)}\n"
            
            tag_info = []
            for tag in self.repo.tags:
                if tag.commit == commit:
                    tag_info.append(tag.name)
            
            if tag_info:
                details += f"Tags: {', '.join(tag_info)}\n"
            
            self.timeline_details_text.insert('1.0', details)
            
            # Update files tree
            for item in self.timeline_files_tree.get_children():
                self.timeline_files_tree.delete(item)
            
            if commit.parents:
                diffs = commit.parents[0].diff(commit)
                for diff in diffs:
                    status = 'Modified'
                    if diff.new_file:
                        status = 'Added'
                    elif diff.deleted_file:
                        status = 'Deleted'
                    elif diff.renamed_file:
                        status = 'Renamed'
                    
                    file_path = diff.b_path or diff.a_path
                    
                    try:
                        if diff.diff:
                            additions = diff.diff.decode('utf-8').count('\n+')
                            deletions = diff.diff.decode('utf-8').count('\n-')
                            changes = f"+{additions} -{deletions}"
                        else:
                            changes = "Binary"
                    except:
                        changes = "Modified"
                    
                    self.timeline_files_tree.insert('', 'end', values=(file_path, status, changes))
            else:
                # Initial commit
                for item in commit.tree.traverse():
                    if item.type == 'blob':
                        self.timeline_files_tree.insert('', 'end', values=(item.path, 'Added', 'New'))
                        
        except Exception as e:
            self.timeline_details_text.delete('1.0', tk.END)
            self.timeline_details_text.insert('1.0', f"Error loading commit details: {str(e)}")


        
    def show_tags_branches(self):
        """Show tags and branches overview - IMPLEMENTED"""
        if not self.repo:
            messagebox.showerror("Error", "No repository loaded")
            return
        
        overview_window = tk.Toplevel(self.root)
        overview_window.title("Tags & Branches Overview")
        overview_window.geometry("1000x700")
        
        # Create notebook for tabs
        notebook = ttk.Notebook(overview_window)
        notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Branches tab
        branches_frame = ttk.Frame(notebook)
        notebook.add(branches_frame, text="Branches")
        
        # Local branches
        local_frame = ttk.LabelFrame(branches_frame, text="Local Branches")
        local_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        local_columns = ('Branch', 'Current', 'Last Commit', 'Author', 'Date')
        local_tree = ttk.Treeview(local_frame, columns=local_columns, show='headings')
        
        for col in local_columns:
            local_tree.heading(col, text=col)
            local_tree.column(col, width=150)
        
        local_tree.pack(fill=tk.BOTH, expand=True)
        
        # Remote branches
        remote_frame = ttk.LabelFrame(branches_frame, text="Remote Branches")
        remote_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        remote_columns = ('Branch', 'Remote', 'Last Commit', 'Author', 'Date')
        remote_tree = ttk.Treeview(remote_frame, columns=remote_columns, show='headings')
        
        for col in remote_columns:
            remote_tree.heading(col, text=col)
            remote_tree.column(col, width=150)
        
        remote_tree.pack(fill=tk.BOTH, expand=True)
        
        # Tags tab
        tags_frame = ttk.Frame(notebook)
        notebook.add(tags_frame, text="Tags")
        
        tags_overview_frame = ttk.LabelFrame(tags_frame, text="All Tags")
        tags_overview_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        tags_columns = ('Tag', 'Type', 'Commit', 'Date', 'Author', 'Message')
        tags_overview_tree = ttk.Treeview(tags_overview_frame, columns=tags_columns, show='headings')
        
        for col in tags_columns:
            tags_overview_tree.heading(col, text=col)
            if col == 'Message':
                tags_overview_tree.column(col, width=200)
            else:
                tags_overview_tree.column(col, width=120)
        
        tags_overview_tree.pack(fill=tk.BOTH, expand=True)
        
        # Populate data
        try:
            # Local branches
            current_branch = None
            try:
                current_branch = self.repo.active_branch.name
            except:
                pass
            
            for branch in self.repo.branches:
                is_current = "✓" if branch.name == current_branch else ""
                commit = branch.commit
                local_tree.insert('', 'end', values=(
                    branch.name,
                    is_current,
                    commit.hexsha[:8],
                    commit.author.name,
                    commit.committed_datetime.strftime('%Y-%m-%d %H:%M')
                ))
            
            # Remote branches
            try:
                for ref in self.repo.refs:
                    if ref.name.startswith('origin/') and not ref.name.endswith('/HEAD'):
                        branch_name = ref.name.replace('origin/', '')
                        commit = ref.commit
                        remote_tree.insert('', 'end', values=(
                            branch_name,
                            "origin",
                            commit.hexsha[:8],
                            commit.author.name,
                            commit.committed_datetime.strftime('%Y-%m-%d %H:%M')
                        ))
            except:
                pass
            
            # Tags
            for tag in self.repo.tags:
                commit = tag.commit
                tag_type = "Annotated" if hasattr(tag, 'tag') and tag.tag else "Lightweight"
                message = ""
                try:
                    if hasattr(tag, 'tag') and tag.tag and tag.tag.message:
                        message = tag.tag.message.strip()[:50]
                    else:
                        message = commit.message.strip()[:50]
                except:
                    message = "No message"
                
                tags_overview_tree.insert('', 'end', values=(
                    tag.name,
                    tag_type,
                    commit.hexsha[:8],
                    commit.committed_datetime.strftime('%Y-%m-%d %H:%M'),
                    commit.author.name,
                    message
                ))
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load branches/tags: {str(e)}")
    
    def show_commit_details(self):
        """Show detailed commit information - IMPLEMENTED"""
        if not self.repo:
            messagebox.showerror("Error", "No repository loaded")
            return
        
        # Get commit selection
        commits = list(self.repo.iter_commits(max_count=50))
        if not commits:
            messagebox.showinfo("No Commits", "No commits found in repository")
            return
        
        # Create commit selection dialog
        selection_window = tk.Toplevel(self.root)
        selection_window.title("Select Commit for Details")
        selection_window.geometry("800x500")
        
        ttk.Label(selection_window, text="Select commit to view details:", 
                font=('TkDefaultFont', 10, 'bold')).pack(pady=10)
        
        # Commits list
        commits_frame = ttk.Frame(selection_window)
        commits_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        commits_columns = ('Hash', 'Date', 'Author', 'Message')
        commits_tree = ttk.Treeview(commits_frame, columns=commits_columns, show='headings')
        
        for col in commits_columns:
            commits_tree.heading(col, text=col)
            if col == 'Message':
                commits_tree.column(col, width=300)
            else:
                commits_tree.column(col, width=120)
        
        commits_scroll = ttk.Scrollbar(commits_frame, orient=tk.VERTICAL, command=commits_tree.yview)
        commits_tree.configure(yscrollcommand=commits_scroll.set)
        
        commits_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        commits_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Populate commits
        for commit in commits:
            message = commit.message.strip()[:50]
            if len(commit.message.strip()) > 50:
                message += "..."
            
            commits_tree.insert('', 'end', values=(
                commit.hexsha[:8],
                commit.committed_datetime.strftime('%Y-%m-%d %H:%M'),
                commit.author.name,
                message
            ))
        
        def show_selected_commit():
            selection = commits_tree.selection()
            if selection:
                commit_hash = commits_tree.item(selection[0])['values'][0]
                for commit in commits:
                    if commit.hexsha.startswith(commit_hash):
                        selection_window.destroy()
                        self.open_commit_details(commit)
                        break
            else:
                messagebox.showwarning("No Selection", "Please select a commit")
        
        # Buttons
        button_frame = ttk.Frame(selection_window)
        button_frame.pack(fill=tk.X, padx=20, pady=10)
        
        ttk.Button(button_frame, text="Show Details", command=show_selected_commit).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Cancel", command=selection_window.destroy).pack(side=tk.RIGHT, padx=5)
        
        # Double-click to show details
        commits_tree.bind('<Double-1>', lambda e: show_selected_commit())
        
        # Select first commit
        if commits_tree.get_children():
            first_item = commits_tree.get_children()[0]
            commits_tree.selection_set(first_item)
            commits_tree.see(first_item)

    def view_file_at_commit(self):
        """View selected file at a specific commit - IMPLEMENTED"""
        selection = self.file_tree.selection()
        if not selection or not self.repo:
            messagebox.showwarning("No Selection", "Please select a file to view at commit")
            return
        
        item = selection[0]
        file_name = self.file_tree.item(item)['values'][0]
        
        tree_selection = self.repo_tree.selection()
        if not tree_selection:
            messagebox.showwarning("No Selection", "Please select a folder first")
            return
        
        folder_path = self.repo_tree.item(tree_selection[0])['values'][0]
        file_path = os.path.join(folder_path, file_name)
        
        if not os.path.isfile(file_path):
            messagebox.showwarning("Not a File", "Please select a file, not a directory")
            return
        
        rel_path = os.path.relpath(file_path, self.repo_path)
        
        # Get commits that contain this file
        try:
            commits = list(self.repo.iter_commits(paths=rel_path, max_count=20))
            if not commits:
                messagebox.showinfo("No History", f"No commit history found for {file_name}")
                return
        except Exception as e:
            messagebox.showerror("Error", f"Failed to get file history: {str(e)}")
            return
        
        # Create commit selection dialog
        selection_window = tk.Toplevel(self.root)
        selection_window.title(f"View {file_name} at Commit")
        selection_window.geometry("800x500")
        
        ttk.Label(selection_window, text=f"Select commit to view {file_name}:", 
                font=('TkDefaultFont', 10, 'bold')).pack(pady=10)
        
        # Commits list
        commits_frame = ttk.Frame(selection_window)
        commits_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        commits_columns = ('Hash', 'Date', 'Author', 'Message')
        commits_tree = ttk.Treeview(commits_frame, columns=commits_columns, show='headings')
        
        for col in commits_columns:
            commits_tree.heading(col, text=col)
            if col == 'Message':
                commits_tree.column(col, width=300)
            else:
                commits_tree.column(col, width=120)
        
        commits_scroll = ttk.Scrollbar(commits_frame, orient=tk.VERTICAL, command=commits_tree.yview)
        commits_tree.configure(yscrollcommand=commits_scroll.set)
        
        commits_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        commits_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Populate commits
        for commit in commits:
            message = commit.message.strip()[:50]
            if len(commit.message.strip()) > 50:
                message += "..."
            
            commits_tree.insert('', 'end', values=(
                commit.hexsha[:8],
                commit.committed_datetime.strftime('%Y-%m-%d %H:%M'),
                commit.author.name,
                message
            ))
        
        def view_selected_commit():
            selection = commits_tree.selection()
            if selection:
                commit_hash = commits_tree.item(selection[0])['values'][0]
                for commit in commits:
                    if commit.hexsha.startswith(commit_hash):
                        selection_window.destroy()
                        self.show_file_at_commit(rel_path, commit.hexsha)
                        break
            else:
                messagebox.showwarning("No Selection", "Please select a commit")
        
        # Buttons
        button_frame = ttk.Frame(selection_window)
        button_frame.pack(fill=tk.X, padx=20, pady=10)
        
        ttk.Button(button_frame, text="View File", command=view_selected_commit).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Cancel", command=selection_window.destroy).pack(side=tk.RIGHT, padx=5)
        
        # Double-click to view
        commits_tree.bind('<Double-1>', lambda e: view_selected_commit())
        
        # Select first commit
        if commits_tree.get_children():
            first_item = commits_tree.get_children()[0]
            commits_tree.selection_set(first_item)
            commits_tree.see(first_item)


    def revert_file_to_version(self):
        """Revert selected file to a specific version - IMPLEMENTED"""
        selection = self.file_tree.selection()
        if not selection or not self.repo:
            messagebox.showwarning("No Selection", "Please select a file to revert")
            return
        
        item = selection[0]
        file_name = self.file_tree.item(item)['values'][0]
        
        tree_selection = self.repo_tree.selection()
        if not tree_selection:
            messagebox.showwarning("No Selection", "Please select a folder first")
            return
        
        folder_path = self.repo_tree.item(tree_selection[0])['values'][0]
        file_path = os.path.join(folder_path, file_name)
        
        if not os.path.isfile(file_path):
            messagebox.showwarning("Not a File", "Please select a file, not a directory")
            return
        
        rel_path = os.path.relpath(file_path, self.repo_path)
        
        # Get commits that contain this file
        try:
            commits = list(self.repo.iter_commits(paths=rel_path, max_count=20))
            if not commits:
                messagebox.showinfo("No History", f"No commit history found for {file_name}")
                return
        except Exception as e:
            messagebox.showerror("Error", f"Failed to get file history: {str(e)}")
            return
        
        # Create revert dialog
        revert_window = tk.Toplevel(self.root)
        revert_window.title(f"Revert {file_name} to Version")
        revert_window.geometry("800x500")
        
        # Warning
        warning_frame = ttk.Frame(revert_window)
        warning_frame.pack(fill=tk.X, padx=20, pady=10)
        
        warning_text = f"⚠️ Warning: This will overwrite the current content of {file_name}"
        ttk.Label(warning_frame, text=warning_text, foreground='red', 
                font=('TkDefaultFont', 10, 'bold')).pack()
        
        ttk.Label(revert_window, text=f"Select version to revert {file_name} to:", 
                font=('TkDefaultFont', 10, 'bold')).pack(pady=10)
        
        # Commits list
        commits_frame = ttk.Frame(revert_window)
        commits_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        commits_columns = ('Version', 'Hash', 'Date', 'Author', 'Message')
        commits_tree = ttk.Treeview(commits_frame, columns=commits_columns, show='headings')
        
        commits_tree.heading('Version', text='Version')
        commits_tree.column('Version', width=80)
        
        for col in commits_columns[1:]:
            commits_tree.heading(col, text=col)
            if col == 'Message':
                commits_tree.column(col, width=300)
            else:
                commits_tree.column(col, width=120)
        
        commits_scroll = ttk.Scrollbar(commits_frame, orient=tk.VERTICAL, command=commits_tree.yview)
        commits_tree.configure(yscrollcommand=commits_scroll.set)
        
        commits_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        commits_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Populate commits
        for i, commit in enumerate(commits):
            version_num = len(commits) - i
            message = commit.message.strip()[:50]
            if len(commit.message.strip()) > 50:
                message += "..."
            
            commits_tree.insert('', 'end', values=(
                version_num,
                commit.hexsha[:8],
                commit.committed_datetime.strftime('%Y-%m-%d %H:%M'),
                commit.author.name,
                message
            ))
        
        def revert_to_selected():
            selection = commits_tree.selection()
            if selection:
                values = commits_tree.item(selection[0])['values']
                version_num = values[0]
                commit_hash = values[1]
                
                if messagebox.askyesno("Confirm Revert", 
                                    f"Revert {file_name} to version {version_num}?\n\n" +
                                    f"Commit: {commit_hash}\n" +
                                    "This will overwrite the current file content."):
                    try:
                        for commit in commits:
                            if commit.hexsha.startswith(commit_hash):
                                # Get file content at this commit
                                file_content = commit.tree[rel_path].data_stream.read()
                                
                                # Write to working directory
                                with open(file_path, 'wb') as f:
                                    f.write(file_content)
                                
                                messagebox.showinfo("Success", 
                                                f"{file_name} reverted to version {version_num}")
                                revert_window.destroy()
                                self.refresh_all()
                                break
                    except Exception as e:
                        messagebox.showerror("Error", f"Failed to revert file: {str(e)}")
            else:
                messagebox.showwarning("No Selection", "Please select a version to revert to")
        
        # Buttons
        button_frame = ttk.Frame(revert_window)
        button_frame.pack(fill=tk.X, padx=20, pady=10)
        
        ttk.Button(button_frame, text="Revert to Selected", command=revert_to_selected,
                style='Warning.TButton').pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Cancel", command=revert_window.destroy).pack(side=tk.RIGHT, padx=5)
        
        # Double-click to revert
        commits_tree.bind('<Double-1>', lambda e: revert_to_selected())
        
        # Select first commit (most recent)
        if commits_tree.get_children():
            first_item = commits_tree.get_children()[0]
            commits_tree.selection_set(first_item)
            commits_tree.see(first_item)

    def show_file_blame(self):
        """Show file blame/annotation"""
        selection = self.file_tree.selection()
        if not selection or not self.repo:
            messagebox.showwarning("No Selection", "Please select a file to view blame")
            return
        
        item = selection[0]
        file_name = self.file_tree.item(item)['values'][0]
        
        tree_selection = self.repo_tree.selection()
        if not tree_selection:
            messagebox.showwarning("No Selection", "Please select a folder first")
            return
        
        folder_path = self.repo_tree.item(tree_selection[0])['values'][0]
        file_path = os.path.join(folder_path, file_name)
        
        if not os.path.isfile(file_path):
            messagebox.showwarning("Not a File", "Please select a file, not a directory")
            return
        
        rel_path = os.path.relpath(file_path, self.repo_path)
        
        # Create blame window
        blame_window = tk.Toplevel(self.root)
        blame_window.title(f"Blame: {file_name}")
        blame_window.geometry("1200x800")
        
        # Create paned window
        paned = ttk.PanedWindow(blame_window, orient=tk.HORIZONTAL)
        paned.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Left side - blame info
        left_frame = ttk.Frame(paned)
        paned.add(left_frame, weight=1)
        
        ttk.Label(left_frame, text="Blame Information", font=('TkDefaultFont', 10, 'bold')).pack(pady=5)
        
        # Blame tree
        blame_columns = ('Line', 'Commit', 'Author', 'Date', 'Code')
        blame_tree = ttk.Treeview(left_frame, columns=blame_columns, show='headings')
        
        # Configure columns
        blame_tree.heading('Line', text='Line')
        blame_tree.column('Line', width=50)
        
        blame_tree.heading('Commit', text='Commit')
        blame_tree.column('Commit', width=80)
        
        blame_tree.heading('Author', text='Author')
        blame_tree.column('Author', width=100)
        
        blame_tree.heading('Date', text='Date')
        blame_tree.column('Date', width=100)
        
        blame_tree.heading('Code', text='Code')
        blame_tree.column('Code', width=400)
        
        # Scrollbars
        blame_v_scroll = ttk.Scrollbar(left_frame, orient=tk.VERTICAL, command=blame_tree.yview)
        blame_h_scroll = ttk.Scrollbar(left_frame, orient=tk.HORIZONTAL, command=blame_tree.xview)
        blame_tree.configure(yscrollcommand=blame_v_scroll.set, xscrollcommand=blame_h_scroll.set)
        
        blame_tree.grid(row=0, column=0, sticky='nsew')
        blame_v_scroll.grid(row=0, column=1, sticky='ns')
        blame_h_scroll.grid(row=1, column=0, sticky='ew')
        
        left_frame.grid_rowconfigure(0, weight=1)
        left_frame.grid_columnconfigure(0, weight=1)
        
        # Right side - commit details
        right_frame = ttk.Frame(paned)
        paned.add(right_frame, weight=1)
        
        ttk.Label(right_frame, text="Commit Details", font=('TkDefaultFont', 10, 'bold')).pack(pady=5)
        
        # Details text
        details_text = tk.Text(right_frame, wrap=tk.WORD, height=20)
        details_scroll = ttk.Scrollbar(right_frame, orient=tk.VERTICAL, command=details_text.yview)
        details_text.configure(yscrollcommand=details_scroll.set)
        
        details_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        details_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Get blame information
        try:
            blame_info = self.repo.blame('HEAD', rel_path)
            
            line_number = 1
            for commit, lines in blame_info:
                for line in lines:
                    # Clean up line content
                    line_content = line.rstrip('\n\r')
                    if len(line_content) > 60:
                        line_content = line_content[:60] + "..."
                    
                    blame_tree.insert('', 'end', values=(
                        line_number,
                        commit.hexsha[:8],
                        commit.author.name,
                        commit.committed_datetime.strftime('%Y-%m-%d'),
                        line_content
                    ))
                    line_number += 1
            
            # Selection handler
            def on_blame_select(event):
                selection = blame_tree.selection()
                if selection:
                    values = blame_tree.item(selection[0])['values']
                    commit_hash = values[1]
                    
                    # Find the commit
                    for commit, lines in blame_info:
                        if commit.hexsha.startswith(commit_hash):
                            details_text.delete('1.0', tk.END)
                            
                            details = f"Commit: {commit.hexsha}\n"
                            details += f"Author: {commit.author.name} <{commit.author.email}>\n"
                            details += f"Date: {commit.committed_datetime}\n"
                            details += f"Message:\n{commit.message.strip()}\n\n"
                            
                            # Show changes in this commit
                            if commit.parents:
                                try:
                                    diffs = commit.parents[0].diff(commit, paths=rel_path)
                                    if diffs:
                                        details += "Changes in this file:\n"
                                        details += "-" * 30 + "\n"
                                        for diff in diffs:
                                            if diff.diff:
                                                details += diff.diff.decode('utf-8', errors='replace')
                                except:
                                    details += "Could not show diff\n"
                            
                            details_text.insert('1.0', details)
                            break
            
            blame_tree.bind('<<TreeviewSelect>>', on_blame_select)
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to get blame information: {str(e)}")
            blame_tree.insert('', 'end', values=('Error', '', '', '', str(e)))

    def view_version_timeline(self):
        """View version timeline for selected file"""
        selection = self.file_tree.selection()
        if not selection or not self.repo:
            messagebox.showwarning("No Selection", "Please select a file to view timeline")
            return
        
        item = selection[0]
        file_name = self.file_tree.item(item)['values'][0]
        
        tree_selection = self.repo_tree.selection()
        if not tree_selection:
            messagebox.showwarning("No Selection", "Please select a folder first")
            return
        
        folder_path = self.repo_tree.item(tree_selection[0])['values'][0]
        file_path = os.path.join(folder_path, file_name)
        
        if not os.path.isfile(file_path):
            messagebox.showwarning("Not a File", "Please select a file, not a directory")
            return
        
        rel_path = os.path.relpath(file_path, self.repo_path)
        
        # Create timeline window
        timeline_window = tk.Toplevel(self.root)
        timeline_window.title(f"Version Timeline: {file_name}")
        timeline_window.geometry("1400x800")
        
        # Create paned window
        paned = ttk.PanedWindow(timeline_window, orient=tk.HORIZONTAL)
        paned.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Left side - timeline
        left_frame = ttk.Frame(paned)
        paned.add(left_frame, weight=1)
        
        ttk.Label(left_frame, text=f"Timeline for: {file_name}", font=('TkDefaultFont', 10, 'bold')).pack(pady=5)
        
        # Timeline tree
        timeline_columns = ('Version', 'Commit', 'Date', 'Author', 'Message', 'Changes')
        timeline_tree = ttk.Treeview(left_frame, columns=timeline_columns, show='headings')
        
        # Configure columns
        for col in timeline_columns:
            timeline_tree.heading(col, text=col)
            if col == 'Version':
                timeline_tree.column(col, width=70)
            elif col == 'Commit':
                timeline_tree.column(col, width=80)
            elif col == 'Changes':
                timeline_tree.column(col, width=80)
            else:
                timeline_tree.column(col, width=120)
        
        # Scrollbars
        timeline_v_scroll = ttk.Scrollbar(left_frame, orient=tk.VERTICAL, command=timeline_tree.yview)
        timeline_h_scroll = ttk.Scrollbar(left_frame, orient=tk.HORIZONTAL, command=timeline_tree.xview)
        timeline_tree.configure(yscrollcommand=timeline_v_scroll.set, xscrollcommand=timeline_h_scroll.set)
        
        timeline_tree.grid(row=0, column=0, sticky='nsew')
        timeline_v_scroll.grid(row=0, column=1, sticky='ns')
        timeline_h_scroll.grid(row=1, column=0, sticky='ew')
        
        left_frame.grid_rowconfigure(0, weight=1)
        left_frame.grid_columnconfigure(0, weight=1)
        
        # Right side - file content
        right_frame = ttk.Frame(paned)
        paned.add(right_frame, weight=2)
        
        ttk.Label(right_frame, text="File Content at Selected Version", font=('TkDefaultFont', 10, 'bold')).pack(pady=5)
        
        # File content text
        content_text = tk.Text(right_frame, wrap=tk.NONE, font=('Courier', 10))
        content_v_scroll = ttk.Scrollbar(right_frame, orient=tk.VERTICAL, command=content_text.yview)
        content_h_scroll = ttk.Scrollbar(right_frame, orient=tk.HORIZONTAL, command=content_text.xview)
        content_text.configure(yscrollcommand=content_v_scroll.set, xscrollcommand=content_h_scroll.set)
        
        content_text.grid(row=0, column=0, sticky='nsew')
        content_v_scroll.grid(row=0, column=1, sticky='ns')
        content_h_scroll.grid(row=1, column=0, sticky='ew')
        
        right_frame.grid_rowconfigure(0, weight=1)
        right_frame.grid_columnconfigure(0, weight=1)
        
        # Get file history
        try:
            commits = list(self.repo.iter_commits(paths=rel_path))
            
            if not commits:
                messagebox.showinfo("No History", f"No version history found for {file_name}")
                timeline_window.destroy()
                return
            
            # Populate timeline
            for i, commit in enumerate(commits):
                version_num = len(commits) - i
                
                # Get changes info
                changes_info = "Initial"
                if commit.parents:
                    try:
                        diffs = commit.parents[0].diff(commit, paths=rel_path)
                        if diffs and diffs[0].diff:
                            diff_text = diffs[0].diff.decode('utf-8', errors='replace')
                            additions = diff_text.count('\n+')
                            deletions = diff_text.count('\n-')
                            changes_info = f"+{additions} -{deletions}"
                    except:
                        changes_info = "Modified"
                
                timeline_tree.insert('', 'end', values=(
                    version_num,
                    commit.hexsha[:8],
                    commit.committed_datetime.strftime('%Y-%m-%d %H:%M'),
                    commit.author.name,
                    commit.message.strip()[:40] + ("..." if len(commit.message.strip()) > 40 else ""),
                    changes_info
                ))
            
            # Selection handler
            def on_timeline_select(event):
                selection = timeline_tree.selection()
                if selection:
                    values = timeline_tree.item(selection[0])['values']
                    commit_hash = values[1]
                    
                    # Find the commit
                    for commit in commits:
                        if commit.hexsha.startswith(commit_hash):
                            content_text.delete('1.0', tk.END)
                            
                            try:
                                # Get file content at this commit
                                file_content = commit.tree[rel_path].data_stream.read().decode('utf-8', errors='replace')
                                content_text.insert('1.0', file_content)
                            except:
                                content_text.insert('1.0', "Could not read file content (binary file or file not found)")
                            break
            
            timeline_tree.bind('<<TreeviewSelect>>', on_timeline_select)
            
            # Context menu for timeline
            timeline_menu = tk.Menu(timeline_window, tearoff=0)
            timeline_menu.add_command(label="View Full Commit", 
                                    command=lambda: self.view_full_commit_from_timeline(timeline_tree, commits))
            timeline_menu.add_command(label="Compare with Current", 
                                    command=lambda: self.compare_timeline_with_current(timeline_tree, commits, rel_path))
            timeline_menu.add_command(label="Revert to This Version", 
                                    command=lambda: self.revert_to_timeline_version(timeline_tree, commits, rel_path))
            
            def show_timeline_menu(event):
                try:
                    timeline_menu.tk_popup(event.x_root, event.y_root)
                finally:
                    timeline_menu.grab_release()
            
            timeline_tree.bind('<Button-3>', show_timeline_menu)
            
            # Select latest version
            if timeline_tree.get_children():
                first_item = timeline_tree.get_children()[0]
                timeline_tree.selection_set(first_item)
                timeline_tree.see(first_item)
                on_timeline_select(None)
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to get file timeline: {str(e)}")

    def show_rename_tag_dialog(self):
        """Show dialog to rename tags"""
        if not self.repo:
            messagebox.showerror("Error", "No repository loaded")
            return
        
        tags = list(self.repo.tags)
        if not tags:
            messagebox.showwarning("No Tags", "No tags found in repository")
            return
        
        # Create rename dialog
        rename_window = tk.Toplevel(self.root)
        rename_window.title("Rename Tags")
        rename_window.geometry("600x400")
        
        ttk.Label(rename_window, text="Select tag to rename:", font=('TkDefaultFont', 10, 'bold')).pack(pady=10)
        
        # Tags list
        tags_frame = ttk.Frame(rename_window)
        tags_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        tags_listbox = tk.Listbox(tags_frame, font=('TkDefaultFont', 10))
        tags_scroll = ttk.Scrollbar(tags_frame, orient=tk.VERTICAL, command=tags_listbox.yview)
        tags_listbox.configure(yscrollcommand=tags_scroll.set)
        
        # Populate tags
        for tag in sorted(tags, key=lambda t: t.name):
            tags_listbox.insert(tk.END, tag.name)
        
        tags_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        tags_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Rename input
        input_frame = ttk.Frame(rename_window)
        input_frame.pack(fill=tk.X, padx=20, pady=10)
        
        ttk.Label(input_frame, text="New tag name:").pack(anchor=tk.W)
        new_name_var = tk.StringVar()
        new_name_entry = ttk.Entry(input_frame, textvariable=new_name_var, width=40)
        new_name_entry.pack(fill=tk.X, pady=5)
        
        # Update entry when selection changes
        def on_tag_select(event):
            selection = tags_listbox.curselection()
            if selection:
                selected_tag = tags_listbox.get(selection[0])
                new_name_var.set(selected_tag)
        
        tags_listbox.bind('<<ListboxSelect>>', on_tag_select)
        
        def rename_selected_tag():
            selection = tags_listbox.curselection()
            if not selection:
                messagebox.showwarning("No Selection", "Please select a tag to rename")
                return
            
            old_name = tags_listbox.get(selection[0])
            new_name = new_name_var.get().strip()
            
            if self.rename_tag(old_name, new_name):
                rename_window.destroy()
                self.refresh_all()
        
        # Buttons
        button_frame = ttk.Frame(rename_window)
        button_frame.pack(fill=tk.X, padx=20, pady=10)
        
        ttk.Button(button_frame, text="Rename", command=rename_selected_tag, 
                style='Warning.TButton').pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Cancel", command=rename_window.destroy).pack(side=tk.RIGHT, padx=5)
        
        # Select first tag
        if tags_listbox.size() > 0:
            tags_listbox.selection_set(0)
            on_tag_select(None)
        
        new_name_entry.focus()

    
    
    def rename_tag(self, old_tag_name, new_tag_name=None):
        """Rename a tag"""
        if not self.repo:
            messagebox.showerror("Error", "No repository loaded")
            return False
        
        # Get new tag name if not provided
        if not new_tag_name:
            new_tag_name = simpledialog.askstring("Rename Tag", 
                                                f"Enter new name for tag '{old_tag_name}':",
                                                initialvalue=old_tag_name)
        
        if not new_tag_name or new_tag_name == old_tag_name:
            return False
        
        # Validate new tag name
        if not new_tag_name.replace('.', '').replace('-', '').replace('_', '').isalnum():
            messagebox.showerror("Error", "Tag name should contain only letters, numbers, dots, hyphens, and underscores")
            return False
        
        # Check if new tag name already exists
        if new_tag_name in [tag.name for tag in self.repo.tags]:
            messagebox.showerror("Error", f"Tag '{new_tag_name}' already exists")
            return False
        
        try:
            # Get the old tag
            old_tag = self.repo.tags[old_tag_name]
            
            # Create new tag at the same commit
            if hasattr(old_tag, 'tag') and old_tag.tag:
                # Annotated tag
                message = old_tag.tag.message if old_tag.tag.message else f"Renamed from {old_tag_name}"
                self.repo.create_tag(new_tag_name, ref=old_tag.commit, message=message)
            else:
                # Lightweight tag
                self.repo.create_tag(new_tag_name, ref=old_tag.commit)
            
            # Delete old tag
            self.repo.delete_tag(old_tag_name)
            
            # Ask about remote operations
            if messagebox.askyesno("Remote Operations", 
                                f"Tag renamed locally. Do you want to update the remote?\n\n" +
                                f"This will:\n" +
                                f"1. Delete '{old_tag_name}' from remote\n" +
                                f"2. Push '{new_tag_name}' to remote"):
                try:
                    # Delete old tag from remote
                    self.repo.git.push('origin', f':refs/tags/{old_tag_name}')
                    # Push new tag to remote
                    self.repo.git.push('origin', new_tag_name)
                    messagebox.showinfo("Success", f"Tag renamed from '{old_tag_name}' to '{new_tag_name}' and updated on remote")
                except Exception as e:
                    messagebox.showwarning("Remote Update Failed", 
                                        f"Tag renamed locally but failed to update remote: {str(e)}")
            else:
                messagebox.showinfo("Success", f"Tag renamed from '{old_tag_name}' to '{new_tag_name}'")
            
            return True
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to rename tag: {str(e)}")
            return False


    # Additional helper method for tag context menu
    def rename_tag_from_context(self, tags_tree):
        """Rename tag from context menu"""
        selection = tags_tree.selection()
        if selection:
            tag_name = tags_tree.item(selection[0])['values'][0]
            if self.rename_tag(tag_name):
                self.refresh_tags_list(tags_tree)



    def view_full_commit_from_timeline(self, tree, commits):
        """View full commit details from timeline"""
        selection = tree.selection()
        if selection:
            values = tree.item(selection[0])['values']
            commit_hash = values[1]
            
            for commit in commits:
                if commit.hexsha.startswith(commit_hash):
                    self.open_commit_details(commit)
                break


    def compare_timeline_with_current(self, tree, commits, rel_path):
        """Compare timeline version with current"""
        selection = tree.selection()
        if selection:
            values = tree.item(selection[0])['values']
            commit_hash = values[1]
            
            for commit in commits:
                if commit.hexsha.startswith(commit_hash):
                    self.compare_file_with_current_detailed(rel_path, commit)
                    break


    def revert_to_timeline_version(self, tree, commits, rel_path):
        """Revert file to timeline version"""
        selection = tree.selection()
        if selection:
            values = tree.item(selection[0])['values']
            commit_hash = values[1]
            version_num = values[0]
            
            if messagebox.askyesno("Confirm Revert", 
                                f"Revert file to version {version_num} ({commit_hash})?\n\n" +
                                "This will overwrite the current file content."):
                try:
                    for commit in commits:
                        if commit.hexsha.startswith(commit_hash):
                            # Get file content at this commit
                            file_content = commit.tree[rel_path].data_stream.read()
                            
                            # Write to working directory
                            full_path = os.path.join(self.repo_path, rel_path)
                            with open(full_path, 'wb') as f:
                                f.write(file_content)
                            
                            messagebox.showinfo("Success", f"File reverted to version {version_num}")
                            self.refresh_all()
                            break
                except Exception as e:
                    messagebox.showerror("Error", f"Failed to revert file: {str(e)}")


    def compare_file_with_current_detailed(self, rel_path, commit):
        """Detailed comparison between commit version and current"""
        compare_window = tk.Toplevel(self.root)
        compare_window.title(f"Compare: {os.path.basename(rel_path)}")
        compare_window.geometry("1400x800")
        
        # Create paned window
        paned = ttk.PanedWindow(compare_window, orient=tk.HORIZONTAL)
        paned.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Left side - commit version
        left_frame = ttk.LabelFrame(paned, text=f"Version at {commit.hexsha[:8]}")
        paned.add(left_frame, weight=1)
        
        left_text = tk.Text(left_frame, font=('Courier', 9), wrap=tk.NONE)
        left_v_scroll = ttk.Scrollbar(left_frame, orient=tk.VERTICAL, command=left_text.yview)
        left_h_scroll = ttk.Scrollbar(left_frame, orient=tk.HORIZONTAL, command=left_text.xview)
        left_text.configure(yscrollcommand=left_v_scroll.set, xscrollcommand=left_h_scroll.set)
        
        left_text.grid(row=0, column=0, sticky='nsew')
        left_v_scroll.grid(row=0, column=1, sticky='ns')
        left_h_scroll.grid(row=1, column=0, sticky='ew')
        
        left_frame.grid_rowconfigure(0, weight=1)
        left_frame.grid_columnconfigure(0, weight=1)
        
        # Right side - current version
        right_frame = ttk.LabelFrame(paned, text="Current Version")
        paned.add(right_frame, weight=1)
        
        right_text = tk.Text(right_frame, font=('Courier', 9), wrap=tk.NONE)
        right_v_scroll = ttk.Scrollbar(right_frame, orient=tk.VERTICAL, command=right_text.yview)
        right_h_scroll = ttk.Scrollbar(right_frame, orient=tk.HORIZONTAL, command=right_text.xview)
        right_text.configure(yscrollcommand=right_v_scroll.set, xscrollcommand=right_h_scroll.set)
        
        right_text.grid(row=0, column=0, sticky='nsew')
        right_v_scroll.grid(row=0, column=1, sticky='ns')
        right_h_scroll.grid(row=1, column=0, sticky='ew')
        
        right_frame.grid_rowconfigure(0, weight=1)
        right_frame.grid_columnconfigure(0, weight=1)
        
        try:
            # Get commit version
            try:
                commit_content = commit.tree[rel_path].data_stream.read().decode('utf-8', errors='replace')
                left_text.insert('1.0', commit_content)
            except:
                left_text.insert('1.0', "Could not read file content (binary file or file not found)")
            
            # Get current version
            current_path = os.path.join(self.repo_path, rel_path)
            if os.path.exists(current_path):
                with open(current_path, 'r', encoding='utf-8', errors='replace') as f:
                    current_content = f.read()
                    right_text.insert('1.0', current_content)
            else:
                right_text.insert('1.0', "File not found in current working directory")
            
            left_text.config(state=tk.DISABLED)
            right_text.config(state=tk.DISABLED)
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to compare files: {str(e)}")








##
    
    def edit_commit_message_safe_fixed(self, commit, new_message):
        """Fixed interactive rebase for editing commit messages - much more robust"""
        try:
            # Method 1: Try the simple git command approach first
            try:
                # For commits that are 1-2 positions back, try simpler approach
                commits_from_head = list(self.repo.iter_commits(max_count=10))
                commit_position = None
                
                for i, c in enumerate(commits_from_head):
                    if c.hexsha == commit.hexsha:
                        commit_position = i
                        break
                
                if commit_position is not None and commit_position <= 2:
                    # Try the simpler approach for recent commits
                    result = self.try_simple_reword(commit, new_message, commit_position)
                    if result:
                        return
                
            except Exception as e:
                print(f"Simple reword failed: {e}")
            
            # Method 2: Use git filter-branch (more reliable)
            try:
                result = self.try_filter_branch_reword(commit, new_message)
                if result:
                    return
            except Exception as e:
                print(f"Filter-branch failed: {e}")
            
            # Method 3: Manual interactive rebase with better script
            self.try_interactive_rebase_fixed(commit, new_message)
            
        except Exception as e:
            self.root.after(0, lambda: messagebox.showerror("Error", f"All rebase methods failed: {str(e)}"))


    def try_simple_reword(self, commit, new_message, position):
        """Try simple reword for recent commits"""
        try:
            if position == 0:
                # HEAD commit - use amend
                self.repo.git.commit('--amend', '-m', new_message)
                self.root.after(0, lambda: messagebox.showinfo("Success", "HEAD commit message updated!"))
                self.root.after(0, self.refresh_all)
                return True
                
            elif position == 1:
                # Second commit - use reset and recommit
                if messagebox.askyesno("Confirm Method", 
                                    "This will use git reset method. Your working directory must be clean. Continue?"):
                    
                    # Get the current HEAD
                    original_head = self.repo.head.commit.hexsha
                    
                    try:
                        # Reset to the commit before the one we want to edit
                        target_commit = commit.parents[0] if commit.parents else None
                        if target_commit:
                            self.repo.git.reset('--soft', target_commit.hexsha)
                            
                            # Recommit with new message
                            self.repo.git.commit('-m', new_message)
                            
                            # Cherry-pick the HEAD commit
                            self.repo.git.cherry_pick(original_head)
                            
                            self.root.after(0, lambda: messagebox.showinfo("Success", "Commit message updated using reset method!"))
                            self.root.after(0, self.refresh_all)
                            return True
                        
                    except Exception as e:
                        # Restore original state
                        try:
                            self.repo.git.reset('--hard', original_head)
                        except:
                            pass
                        raise e
            
            return False
            
        except Exception as e:
            print(f"Simple reword failed: {e}")
            return False


    def try_filter_branch_reword(self, commit, new_message):
        """Try using git filter-branch to rewrite commit message"""
        try:
            # Create a backup branch first
            backup_branch = f"backup-{commit.hexsha[:8]}"
            self.repo.create_head(backup_branch)
            
            # Create message filter script
            script_content = f'''#!/bin/bash
if [ "$GIT_COMMIT" = "{commit.hexsha}" ]; then
    echo '{new_message}'
else
    cat
fi
'''

            
            # Create temporary script file
            temp_dir = tempfile.mkdtemp()
            script_path = os.path.join(temp_dir, 'msg_filter.sh')
            
            with open(script_path, 'w') as f:
                f.write(script_content)
            
            # Make executable
            os.chmod(script_path, 0o755)
            
            # Run filter-branch
            env = os.environ.copy()
            cmd = ['git', 'filter-branch', '-f', '--msg-filter', script_path, '--', '--all']
            
            result = subprocess.run(cmd, cwd=self.repo_path, env=env, 
                                capture_output=True, text=True, timeout=60)
            
            # Clean up
            try:
                shutil.rmtree(temp_dir)
            except:
                pass
            
            if result.returncode == 0:
                # Delete backup branch
                self.repo.delete_head(backup_branch)
                
                self.root.after(0, lambda: messagebox.showinfo("Success", 
                    "Commit message updated using filter-branch!"))
                self.root.after(0, self.refresh_all)
                return True
            else:
                # Keep backup branch for safety
                error_msg = result.stderr or "Filter-branch failed"
                self.root.after(0, lambda: messagebox.showerror("Filter-branch Failed", 
                    f"Error: {error_msg}\n\nBackup branch '{backup_branch}' created for safety."))
                return False
                
        except Exception as e:
            print(f"Filter-branch method failed: {e}")
            return False


    def try_interactive_rebase_fixed(self, commit, new_message):
        """Fixed interactive rebase with better error handling"""
        try:
            # Create a more robust rebase script
            temp_dir = tempfile.mkdtemp()
            
            # Create the editor script based on platform
            if platform.system() == "Windows":
                script_path = os.path.join(temp_dir, 'git_editor.bat')
                script_content = f'''@echo off
    set "FILE=%~1"
    set "BASENAME=%~nx1"

    if "%BASENAME%"=="git-rebase-todo" (
        powershell -Command "(Get-Content '%FILE%') | ForEach-Object {{ $_ -replace '^pick {commit.hexsha[:7]}', 'reword {commit.hexsha[:7]}' }} | Set-Content '%FILE%'"
        exit /b 0
    )

    if "%BASENAME%"=="COMMIT_EDITMSG" (
        echo {new_message.replace('"', '""')} > "%FILE%"
        exit /b 0
    )

    exit /b 0
    '''
            else:
                script_path = os.path.join(temp_dir, 'git_editor.sh')
                script_content = f'''#!/bin/bash
    FILE="$1"
    BASENAME=$(basename "$FILE")

    if [ "$BASENAME" = "git-rebase-todo" ]; then
        sed -i.bak 's/^pick {commit.hexsha[:7]}/reword {commit.hexsha[:7]}/' "$FILE"
        exit 0
    fi

    if [ "$BASENAME" = "COMMIT_EDITMSG" ]; then
        echo '{new_message}' > "$FILE"
        exit 0
    fi

    exit 0
    '''
            
            # Write script
            with open(script_path, 'w', newline='\n') as f:
                f.write(script_content)
            
            # Make executable (Unix-like systems)
            if platform.system() != "Windows":
                os.chmod(script_path, 0o755)
            
            # Set up environment
            env = os.environ.copy()
            env['GIT_EDITOR'] = script_path
            env['GIT_SEQUENCE_EDITOR'] = script_path
            
            # Determine rebase command
            if commit.parents:
                parent_commit = commit.parents[0]
                cmd = ['git', 'rebase', '-i', parent_commit.hexsha]
            else:
                cmd = ['git', 'rebase', '-i', '--root']
            
            # Show progress dialog
            progress_window = tk.Toplevel(self.root)
            progress_window.title("Rebasing...")
            progress_window.geometry("400x150")
            progress_window.transient(self.root)
            progress_window.grab_set()
            
            ttk.Label(progress_window, text="Performing interactive rebase...", 
                    font=('TkDefaultFont', 10)).pack(pady=20)
            
            progress_bar = ttk.Progressbar(progress_window, mode='indeterminate')
            progress_bar.pack(pady=10, padx=20, fill=tk.X)
            progress_bar.start()
            
            status_var = tk.StringVar(value="Starting rebase...")
            ttk.Label(progress_window, textvariable=status_var).pack(pady=5)
            
            def run_rebase():
                try:
                    status_var.set("Running git rebase...")
                    
                    # Run the rebase
                    result = subprocess.run(cmd, cwd=self.repo_path, env=env,
                                        capture_output=True, text=True, timeout=120)
                    
                    # Clean up temp files
                    try:
                        shutil.rmtree(temp_dir)
                    except:
                        pass
                    
                    if result.returncode == 0:
                        self.root.after(0, lambda: show_rebase_success())
                    else:
                        error_output = result.stderr or result.stdout or "Unknown rebase error"
                        self.root.after(0, lambda: show_rebase_error(error_output))
                        
                except subprocess.TimeoutExpired:
                    self.root.after(0, lambda: show_rebase_error("Rebase timed out"))
                except Exception as e:
                    self.root.after(0, lambda: show_rebase_error(str(e)))
            
            def show_rebase_success():
                progress_window.destroy()
                messagebox.showinfo("Success", 
                    "Commit message updated successfully!\n\nGit history has been rewritten.")
                self.refresh_all()
                if hasattr(self, 'graph_canvas'):
                    self.draw_commit_graph(self.graph_canvas)
            
            def show_rebase_error(error_msg):
                progress_window.destroy()
                
                # Check if we're in a rebase state
                rebase_dir = os.path.join(self.repo_path, '.git', 'rebase-merge')
                rebase_apply_dir = os.path.join(self.repo_path, '.git', 'rebase-apply')
                
                in_rebase = os.path.exists(rebase_dir) or os.path.exists(rebase_apply_dir)
                
                if in_rebase:
                    self.show_rebase_recovery_dialog(error_msg)
                else:
                    messagebox.showerror("Rebase Failed", 
                        f"Interactive rebase failed:\n\n{error_msg}\n\n" +
                        "The repository should be in its original state.")
            
            # Start rebase in background
            threading.Thread(target=run_rebase, daemon=True).start()
            
        except Exception as e:
            self.root.after(0, lambda: messagebox.showerror("Error", f"Failed to setup rebase: {str(e)}"))


    def show_rebase_recovery_dialog(self, error_msg):
        """Show dialog to help user recover from failed rebase"""
        recovery_window = tk.Toplevel(self.root)
        recovery_window.title("Rebase Recovery")
        recovery_window.geometry("600x400")
        recovery_window.transient(self.root)
        recovery_window.grab_set()
        
        # Header
        header_frame = ttk.Frame(recovery_window)
        header_frame.pack(fill=tk.X, padx=10, pady=10)
        
        ttk.Label(header_frame, text="⚠️ Rebase Needs Attention", 
                font=('TkDefaultFont', 12, 'bold'), foreground='red').pack()
        
        # Error info
        info_frame = ttk.LabelFrame(recovery_window, text="Error Details")
        info_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        error_text = tk.Text(info_frame, height=8, wrap=tk.WORD, font=('Courier', 9))
        error_scroll = ttk.Scrollbar(info_frame, orient=tk.VERTICAL, command=error_text.yview)
        error_text.configure(yscrollcommand=error_scroll.set)
        
        error_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)
        error_scroll.pack(side=tk.RIGHT, fill=tk.Y, pady=5)
        
        error_text.insert('1.0', f"Rebase Error:\n{error_msg}\n\n")
        error_text.insert(tk.END, "The repository is currently in a rebase state.\n")
        error_text.insert(tk.END, "You need to either continue or abort the rebase.")
        error_text.config(state=tk.DISABLED)
        
        # Instructions
        inst_frame = ttk.LabelFrame(recovery_window, text="Recovery Options")
        inst_frame.pack(fill=tk.X, padx=10, pady=5)
        
        instructions = """Choose one of the following options:

    1. ABORT REBASE: Cancel the rebase and return to original state (SAFE)
    2. CONTINUE REBASE: Try to continue if you've resolved conflicts
    3. MANUAL RECOVERY: Open terminal/command prompt to handle manually

    Recommendation: Choose "Abort Rebase" to safely return to the original state."""
        
        ttk.Label(inst_frame, text=instructions, font=('TkDefaultFont', 9)).pack(padx=10, pady=10, anchor=tk.W)
        
        # Buttons
        button_frame = ttk.Frame(recovery_window)
        button_frame.pack(fill=tk.X, padx=10, pady=10)
        
        def abort_rebase():
            try:
                result = subprocess.run(['git', 'rebase', '--abort'], 
                                    cwd=self.repo_path, capture_output=True, text=True)
                
                if result.returncode == 0:
                    recovery_window.destroy()
                    messagebox.showinfo("Rebase Aborted", 
                        "Rebase has been aborted. Repository is back to original state.")
                    self.refresh_all()
                else:
                    messagebox.showerror("Abort Failed", f"Failed to abort rebase: {result.stderr}")
                    
            except Exception as e:
                messagebox.showerror("Error", f"Error aborting rebase: {str(e)}")
        
        def continue_rebase():
            try:
                result = subprocess.run(['git', 'rebase', '--continue'], 
                                    cwd=self.repo_path, capture_output=True, text=True)
                
                if result.returncode == 0:
                    recovery_window.destroy()
                    messagebox.showinfo("Rebase Continued", 
                        "Rebase completed successfully!")
                    self.refresh_all()
                else:
                    messagebox.showerror("Continue Failed", 
                        f"Failed to continue rebase: {result.stderr}\n\n" +
                        "You may need to resolve conflicts first.")
                    
            except Exception as e:
                messagebox.showerror("Error", f"Error continuing rebase: {str(e)}")
        
        def open_terminal():
            """Open terminal in repository directory"""
            try:
                system = platform.system()
                if system == "Windows":
                    subprocess.Popen(['cmd', '/c', 'start', 'cmd', '/k', f'cd /d "{self.repo_path}"'])
                elif system == "Darwin":  # macOS
                    subprocess.Popen(['open', '-a', 'Terminal', self.repo_path])
                else:  # Linux
                    subprocess.Popen(['gnome-terminal', '--working-directory', self.repo_path])
                
                messagebox.showinfo("Terminal Opened", 
                    f"Terminal opened in {self.repo_path}\n\n" +
                    "Use these commands:\n" +
                    "- git rebase --abort (to cancel)\n" +
                    "- git rebase --continue (to proceed)\n" +
                    "- git status (to check state)")
                    
            except Exception as e:
                messagebox.showerror("Error", f"Could not open terminal: {str(e)}")
        
        # Create buttons
        ttk.Button(button_frame, text="❌ Abort Rebase (Safe)", command=abort_rebase, 
                style='Warning.TButton').pack(side=tk.LEFT, padx=5)
        
        ttk.Button(button_frame, text="✅ Continue Rebase", command=continue_rebase, 
                style='Success.TButton').pack(side=tk.LEFT, padx=5)
        
        ttk.Button(button_frame, text="🖥️ Open Terminal", command=open_terminal).pack(side=tk.LEFT, padx=15)
        
        ttk.Button(button_frame, text="Close", command=recovery_window.destroy).pack(side=tk.RIGHT, padx=5)


    def check_rebase_state(self):
        """Check if repository is in a rebase state"""
        try:
            rebase_dir = os.path.join(self.repo_path, '.git', 'rebase-merge')
            rebase_apply_dir = os.path.join(self.repo_path, '.git', 'rebase-apply')
            
            if os.path.exists(rebase_dir) or os.path.exists(rebase_apply_dir):
                return True, "Repository is in rebase state"
            
            return False, "Repository is clean"
            
        except Exception as e:
            return None, f"Error checking rebase state: {str(e)}"


    def edit_commit_message_enhanced(self):
        """Enhanced commit message editing with better pre-checks"""
        if not self.repo:
            messagebox.showerror("Error", "No repository loaded")
            return
        
        # Check if already in rebase state
        in_rebase, rebase_msg = self.check_rebase_state()
        
        if in_rebase:
            if messagebox.askyesno("Rebase In Progress", 
                                f"{rebase_msg}\n\nDo you want to handle the existing rebase first?"):
                self.show_rebase_recovery_dialog("Existing rebase detected")
            return
        
        # Check for uncommitted changes
        try:
            if self.repo.is_dirty():
                if not messagebox.askyesno("Uncommitted Changes", 
                                        "You have uncommitted changes. These should be committed or stashed first.\n\n" +
                                        "Continue anyway? (Not recommended)"):
                    return
        except:
            pass
        
        # Proceed with the enhanced edit dialog
        self.edit_commit_message()


    # Simple fallback method for editing only HEAD
    def edit_head_commit_simple(self):
        """Simple and reliable method to edit only HEAD commit"""
        if not self.repo:
            messagebox.showerror("Error", "No repository loaded")
            return
        
        try:
            head_commit = self.repo.head.commit
            current_message = head_commit.message.strip()
            
            # Create simple dialog
            edit_dialog = tk.Toplevel(self.root)
            edit_dialog.title("Edit HEAD Commit Message")
            edit_dialog.geometry("600x300")
            edit_dialog.transient(self.root)
            edit_dialog.grab_set()
            
            # Header
            ttk.Label(edit_dialog, text="Edit Last Commit Message", 
                    font=('TkDefaultFont', 12, 'bold')).pack(pady=10)
            
            # Current message
            ttk.Label(edit_dialog, text="Current message:").pack(anchor=tk.W, padx=20)
            current_text = tk.Text(edit_dialog, height=3, wrap=tk.WORD, state=tk.DISABLED, bg='#f0f0f0')
            current_text.pack(fill=tk.X, padx=20, pady=5)
            current_text.config(state=tk.NORMAL)
            current_text.insert('1.0', current_message)
            current_text.config(state=tk.DISABLED)
            
            # New message
            ttk.Label(edit_dialog, text="New message:").pack(anchor=tk.W, padx=20)
            new_text = tk.Text(edit_dialog, height=3, wrap=tk.WORD)
            new_text.pack(fill=tk.X, padx=20, pady=5)
            new_text.insert('1.0', current_message)
            new_text.focus_set()
            
            # Buttons
            button_frame = ttk.Frame(edit_dialog)
            button_frame.pack(fill=tk.X, padx=20, pady=20)
            
            def save_message():
                new_message = new_text.get('1.0', tk.END).strip()
                if new_message and new_message != current_message:
                    try:
                        self.repo.git.commit('--amend', '-m', new_message)
                        edit_dialog.destroy()
                        messagebox.showinfo("Success", "HEAD commit message updated!")
                        self.refresh_all()
                    except Exception as e:
                        messagebox.showerror("Error", f"Failed to update message: {str(e)}")
                else:
                    edit_dialog.destroy()
            
            ttk.Button(button_frame, text="Save", command=save_message, 
                    style='Success.TButton').pack(side=tk.LEFT, padx=5)
            ttk.Button(button_frame, text="Cancel", command=edit_dialog.destroy).pack(side=tk.RIGHT, padx=5)
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to edit HEAD commit: {str(e)}")





##


###
    
    def populate_file_list_enhanced(self, folder_path):
        """Enhanced file list with better row highlighting"""
        # Clear existing items
        for item in self.file_tree.get_children():
            self.file_tree.delete(item)
        
        if not os.path.exists(folder_path):
            return
        
        try:
            for item in sorted(os.listdir(folder_path)):
                if item.startswith('.'):
                    continue
                
                item_path = os.path.join(folder_path, item)
                
                # Get file status
                file_status = self.file_status_cache.get(item_path, 'CLEAN')
                
                # Get file info
                if os.path.isfile(item_path):
                    size = os.path.getsize(item_path)
                    size_str = self.format_file_size(size)
                    modified = datetime.fromtimestamp(os.path.getmtime(item_path)).strftime('%Y-%m-%d %H:%M')
                    
                    # Get Git info
                    branch_info, commit_info, version_info, author_info, commit_date = self.get_git_file_info(item_path)
                    
                    # Choose icon based on file type and status
                    icon = self.get_file_icon(item_path, file_status)
                    
                    # Enhanced row highlighting based on file status
                    if file_status == 'NEW':
                        tags = ('new_file',)
                        self.highlighted_files.add(item_path)
                    elif file_status == 'MODIFIED':
                        tags = ('modified_file',)
                        self.highlighted_files.add(item_path)
                    elif file_status == 'STAGED':
                        tags = ('staged_file',)
                        self.highlighted_files.add(item_path)
                    elif file_status == 'MODIFIED_STAGED':
                        tags = ('modified_staged_file',)
                        self.highlighted_files.add(item_path)
                    elif file_status == 'DELETED':
                        tags = ('deleted_file',)
                        self.highlighted_files.add(item_path)
                    elif file_status == 'RENAMED':
                        tags = ('renamed_file',)
                        self.highlighted_files.add(item_path)
                    elif file_status == 'COPIED':
                        tags = ('copied_file',)
                        self.highlighted_files.add(item_path)
                    elif file_status == 'CONFLICTED':
                        tags = ('conflicted_file',)
                        self.highlighted_files.add(item_path)
                    else:
                        tags = ('clean_file',)
                    
                    file_item = self.file_tree.insert('', 'end', text=icon, 
                                        values=(item, 'File', size_str, modified, branch_info, version_info, author_info, commit_info, commit_date),
                                        tags=tags)
                    
                elif os.path.isdir(item_path):
                    folder_icon = self.get_folder_status(item_path)
                    folder_status = self.get_folder_git_status(item_path)
                    
                    if folder_status == 'MODIFIED':
                        tags = ('modified_folder',)
                    elif folder_status == 'NEW':
                        tags = ('new_folder',)
                    elif folder_status == 'STAGED':
                        tags = ('staged_folder',)
                    else:
                        tags = ('clean_folder',)
                    
                    self.file_tree.insert('', 'end', text=folder_icon, 
                                        values=(item, 'Folder', '', '', '', '', '', '', ''),
                                        tags=tags)
            
            # Configure enhanced tag colors with better contrast
            self.configure_file_tree_colors()
            
        except PermissionError:
            self.status_label.config(text="Permission denied accessing folder")


    def configure_file_tree_colors(self):
        """Configure enhanced color scheme for file tree"""
        # File status colors with better visibility
        self.file_tree.tag_configure('new_file', 
                                    background='#ffebee', foreground='#c62828',
                                    font=('TkDefaultFont', 9, 'bold'))  # Light red with dark red text
        
        self.file_tree.tag_configure('modified_file', 
                                    background='#fff8e1', foreground='#f57f17',
                                    font=('TkDefaultFont', 9, 'bold'))  # Light amber with dark amber text
        
        self.file_tree.tag_configure('staged_file', 
                                    background='#e8f5e8', foreground='#2e7d32',
                                    font=('TkDefaultFont', 9, 'bold'))  # Light green with dark green text
        
        self.file_tree.tag_configure('modified_staged_file', 
                                    background='#e3f2fd', foreground='#1565c0',
                                    font=('TkDefaultFont', 9, 'bold'))  # Light blue with dark blue text
        
        self.file_tree.tag_configure('deleted_file', 
                                    background='#fce4ec', foreground='#ad1457',
                                    font=('TkDefaultFont', 9, 'italic'))  # Light pink with dark pink text
        
        self.file_tree.tag_configure('renamed_file', 
                                    background='#f3e5f5', foreground='#7b1fa2',
                                    font=('TkDefaultFont', 9))  # Light purple with dark purple text
        
        self.file_tree.tag_configure('copied_file', 
                                    background='#e0f2f1', foreground='#00695c',
                                    font=('TkDefaultFont', 9))  # Light teal with dark teal text
        
        self.file_tree.tag_configure('conflicted_file', 
                                    background='#ffcdd2', foreground='#d32f2f',
                                    font=('TkDefaultFont', 9, 'bold'))  # Light red with dark red text - conflicts
        
        self.file_tree.tag_configure('clean_file', 
                                    background='white', foreground='black',
                                    font=('TkDefaultFont', 9))
        
        # Folder colors
        self.file_tree.tag_configure('modified_folder', 
                                    background='#fff3e0', foreground='#e65100')
        self.file_tree.tag_configure('new_folder', 
                                    background='#ffebee', foreground='#c62828')
        self.file_tree.tag_configure('staged_folder', 
                                    background='#e8f5e8', foreground='#2e7d32')
        self.file_tree.tag_configure('clean_folder', 
                                    background='white', foreground='black')


    def get_folder_git_status(self, folder_path):
        """Get Git status for folder"""
        has_new = False
        has_modified = False
        has_staged = False
        
        for file_path, status in self.file_status_cache.items():
            if file_path.startswith(folder_path):
                if status == 'NEW':
                    has_new = True
                elif status == 'MODIFIED':
                    has_modified = True
                elif status in ['STAGED', 'MODIFIED_STAGED']:
                    has_staged = True
        
        if has_staged:
            return 'STAGED'
        elif has_modified:
            return 'MODIFIED'
        elif has_new:
            return 'NEW'
        else:
            return 'CLEAN'


    def update_file_status_cache_enhanced(self):
        """Enhanced file status cache with conflict detection"""
        if not self.repo:
            return
        
        self.file_status_cache = {}
        
        try:
            # Get repository status
            status_output = self.repo.git.status('--porcelain')
            
            for line in status_output.split('\n'):
                if not line.strip():
                    continue
                
                status_code = line[:2]
                file_path = line[3:]
                full_path = os.path.join(self.repo_path, file_path)
                
                # Enhanced status detection
                if status_code == 'UU':  # Both modified (merge conflict)
                    self.file_status_cache[full_path] = 'CONFLICTED'
                elif status_code == 'AA':  # Both added (merge conflict)
                    self.file_status_cache[full_path] = 'CONFLICTED'
                elif status_code == 'DD':  # Both deleted (merge conflict)
                    self.file_status_cache[full_path] = 'CONFLICTED'
                elif status_code[0] in ['M', 'A', 'D', 'R', 'C']:
                    if status_code[1] in ['M', 'D']:
                        self.file_status_cache[full_path] = 'MODIFIED_STAGED'
                    else:
                        self.file_status_cache[full_path] = 'STAGED'
                elif status_code[1] in ['M', 'D']:
                    self.file_status_cache[full_path] = 'MODIFIED'
                elif status_code[1] == '?':
                    self.file_status_cache[full_path] = 'NEW'
                elif status_code[0] == 'R':
                    self.file_status_cache[full_path] = 'RENAMED'
                elif status_code[0] == 'C':
                    self.file_status_cache[full_path] = 'COPIED'
                elif status_code[0] == 'D' or status_code[1] == 'D':
                    self.file_status_cache[full_path] = 'DELETED'
                        
        except Exception as e:
            self.status_label.config(text=f"Error updating status: {str(e)}")

    
    def edit_commit_message_python_only(self, commit, new_message):
        """Edit commit message using pure Python approach - no bash files"""
        try:
            # Method 1: For HEAD commit, use simple amend
            if commit == self.repo.head.commit:
                self.repo.git.commit('--amend', '-m', new_message)
                self.root.after(0, lambda: messagebox.showinfo("Success", "HEAD commit message updated!"))
                self.root.after(0, self.refresh_all)
                return True
            
            # Method 2: For other commits, use Python-based rebase
            return self.python_interactive_rebase(commit, new_message)
            
        except Exception as e:
            self.root.after(0, lambda: messagebox.showerror("Error", f"Failed to edit commit: {str(e)}"))
            return False


    def python_interactive_rebase(self, commit, new_message):
        """Python-only interactive rebase implementation"""
        try:
            # Create a backup branch
            backup_branch = f"backup-edit-{int(time.time())}"
            self.repo.create_head(backup_branch)
            
            # Get commit list from target to HEAD
            commits_to_rebase = []
            current = self.repo.head.commit
            
            while current and current != commit.parents[0] if commit.parents else None:
                commits_to_rebase.append(current)
                if not current.parents:
                    break
                current = current.parents[0]
            
            commits_to_rebase.reverse()  # Oldest first
            
            # Reset to the parent of our target commit
            if commit.parents:
                self.repo.git.reset('--hard', commit.parents[0].hexsha)
            else:
                # Root commit - create orphan branch
                self.repo.git.checkout('--orphan', 'temp-rebase')
            
            # Apply commits one by one
            for i, c in enumerate(commits_to_rebase):
                if c == commit:
                    # This is our target commit - use new message
                    try:
                        # Cherry-pick with new message
                        self.repo.git.cherry_pick('--no-commit', c.hexsha)
                        self.repo.git.commit('-m', new_message)
                    except:
                        # If cherry-pick fails, try manual commit
                        self.repo.index.commit(new_message, author=c.author, 
                                            author_date=c.authored_datetime,
                                            committer=c.committer,
                                            commit_date=c.committed_datetime)
                else:
                    # Regular cherry-pick
                    try:
                        self.repo.git.cherry_pick(c.hexsha)
                    except subprocess.CalledProcessError:
                        # Handle conflicts
                        return self.handle_rebase_conflict(backup_branch)
            
            # Delete backup branch
            self.repo.delete_head(backup_branch)
            
            self.root.after(0, lambda: messagebox.showinfo("Success", 
                "Commit message updated successfully using Python rebase!"))
            self.root.after(0, self.refresh_all)
            return True
            
        except Exception as e:
            # Restore from backup
            try:
                self.repo.git.reset('--hard', backup_branch)
                self.repo.delete_head(backup_branch)
            except:
                pass
            
            self.root.after(0, lambda: messagebox.showerror("Python Rebase Failed", 
                f"Failed to edit commit message: {str(e)}\n\nRepository restored from backup."))
            return False


    def handle_rebase_conflict(self, backup_branch):
        """Handle conflicts during Python rebase"""
        def show_conflict_dialog():
            conflict_window = tk.Toplevel(self.root)
            conflict_window.title("Rebase Conflict")
            conflict_window.geometry("500x300")
            
            ttk.Label(conflict_window, text="⚠️ Rebase Conflict Detected", 
                    font=('TkDefaultFont', 12, 'bold'), foreground='red').pack(pady=10)
            
            ttk.Label(conflict_window, text="There are conflicts that need to be resolved manually.\n" +
                    "Please resolve conflicts and try again, or abort the operation.").pack(pady=10)
            
            button_frame = ttk.Frame(conflict_window)
            button_frame.pack(pady=20)
            
            def abort_rebase():
                try:
                    self.repo.git.reset('--hard', backup_branch)
                    self.repo.delete_head(backup_branch)
                    conflict_window.destroy()
                    messagebox.showinfo("Aborted", "Rebase aborted, repository restored.")
                    self.refresh_all()
                except Exception as e:
                    messagebox.showerror("Error", f"Failed to abort: {str(e)}")
            
            ttk.Button(button_frame, text="Abort Rebase", command=abort_rebase, 
                    style='Warning.TButton').pack(side=tk.LEFT, padx=10)
            ttk.Button(button_frame, text="Close", command=conflict_window.destroy).pack(side=tk.RIGHT, padx=10)
        
        self.root.after(0, show_conflict_dialog)
        return False


    # merge
    
    def check_merge_status(self):
        """Check for merge conflicts and pending merges"""
        if not self.repo:
            return False, []
        
        try:
            # Check if we're in a merge state
            merge_head_file = os.path.join(self.repo_path, '.git', 'MERGE_HEAD')
            in_merge = os.path.exists(merge_head_file)
            
            # Get conflicted files
            conflicted_files = []
            status_output = self.repo.git.status('--porcelain')
            
            for line in status_output.split('\n'):
                if not line.strip():
                    continue
                
                status_code = line[:2]
                file_path = line[3:]
                
                # Check for conflict markers
                if status_code in ['UU', 'AA', 'DD', 'AU', 'UA', 'DU', 'UD']:
                    conflicted_files.append(file_path)
            
            return in_merge, conflicted_files
            
        except Exception as e:
            print(f"Error checking merge status: {e}")
            return False, []


    def update_merge_navbar_status(self):
        """Update navbar with merge status indicators"""
        in_merge, conflicted_files = self.check_merge_status()
        
        if in_merge or conflicted_files:
            # Show merge indicator
            self.show_merge_indicator(len(conflicted_files))
        else:
            # Hide merge indicator
            self.hide_merge_indicator()


    def show_merge_indicator(self, conflict_count):
        """Show merge conflict indicator in toolbar"""
        if not hasattr(self, 'merge_indicator_frame'):
            # Create merge indicator frame
            self.merge_indicator_frame = ttk.Frame(self.root)
            self.merge_indicator_frame.pack(side=tk.TOP, fill=tk.X, after=self.repo_label.master)
            
            # Warning background
            self.merge_indicator_frame.configure(style='Warning.TFrame')
        
        # Clear existing widgets
        for widget in self.merge_indicator_frame.winfo_children():
            widget.destroy()
        
        # Create warning bar
        warning_frame = ttk.Frame(self.merge_indicator_frame)
        warning_frame.configure(style='Warning.TFrame')
        warning_frame.pack(fill=tk.X, padx=5, pady=2)
        
        # Warning icon and text
        if conflict_count > 0:
            warning_text = f"⚠️ MERGE CONFLICTS: {conflict_count} files need resolution"
            style = 'Conflict.TLabel'
        else:
            warning_text = "🔄 MERGE IN PROGRESS: Commit when ready"
            style = 'Merge.TLabel'
        
        warning_label = ttk.Label(warning_frame, text=warning_text, style=style)
        warning_label.pack(side=tk.LEFT, padx=10)
        
        # Action buttons
        ttk.Button(warning_frame, text="View Conflicts", 
                command=self.show_merge_conflicts_dialog,
                style='Warning.TButton').pack(side=tk.LEFT, padx=5)
        
        if conflict_count == 0:
            ttk.Button(warning_frame, text="Complete Merge", 
                    command=self.complete_merge,
                    style='Success.TButton').pack(side=tk.LEFT, padx=5)
        
        ttk.Button(warning_frame, text="Abort Merge", 
                command=self.abort_merge,
                style='Secondary.TButton').pack(side=tk.LEFT, padx=5)
        
        # Configure warning styles
        self.configure_warning_styles()


    def hide_merge_indicator(self):
        """Hide merge conflict indicator"""
        if hasattr(self, 'merge_indicator_frame'):
            self.merge_indicator_frame.destroy()
            delattr(self, 'merge_indicator_frame')


    def configure_warning_styles(self):
        """Configure warning and merge indicator styles"""
        style = ttk.Style()
        
        # Warning frame style
        style.configure('Warning.TFrame', background='#fff3cd', relief='solid', borderwidth=1)
        
        # Conflict label style
        style.configure('Conflict.TLabel', 
                    background='#fff3cd', foreground='#856404',
                    font=('TkDefaultFont', 10, 'bold'))
        
        # Merge label style
        style.configure('Merge.TLabel', 
                    background='#d1ecf1', foreground='#0c5460',
                    font=('TkDefaultFont', 10, 'bold'))


    def show_merge_conflicts_dialog(self):
        """Show dialog with merge conflicts"""
        in_merge, conflicted_files = self.check_merge_status()
        
        if not conflicted_files:
            messagebox.showinfo("No Conflicts", "No merge conflicts found.")
            return
        
        # Create conflicts dialog
        conflicts_window = tk.Toplevel(self.root)
        conflicts_window.title("Merge Conflicts")
        conflicts_window.geometry("800x600")
        
        # Header
        ttk.Label(conflicts_window, text="Files with Merge Conflicts", 
                font=('TkDefaultFont', 12, 'bold')).pack(pady=10)
        
        # Conflicts list
        conflicts_frame = ttk.Frame(conflicts_window)
        conflicts_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        conflicts_tree = ttk.Treeview(conflicts_frame, columns=('File', 'Status'), show='headings')
        conflicts_tree.heading('File', text='File Path')
        conflicts_tree.heading('Status', text='Conflict Type')
        
        conflicts_scroll = ttk.Scrollbar(conflicts_frame, orient=tk.VERTICAL, command=conflicts_tree.yview)
        conflicts_tree.configure(yscrollcommand=conflicts_scroll.set)
        
        # Populate conflicts
        for file_path in conflicted_files:
            status = self.get_conflict_status(file_path)
            conflicts_tree.insert('', 'end', values=(file_path, status))
        
        conflicts_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        conflicts_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Action buttons
        button_frame = ttk.Frame(conflicts_window)
        button_frame.pack(fill=tk.X, padx=20, pady=10)
        
        def open_conflict_file():
            selection = conflicts_tree.selection()
            if selection:
                file_path = conflicts_tree.item(selection[0])['values'][0]
                full_path = os.path.join(self.repo_path, file_path)
                try:
                    subprocess.run(['code', full_path], check=True)
                except:
                    messagebox.showerror("Error", "Could not open VS Code")
        
        ttk.Button(button_frame, text="Open in VS Code", command=open_conflict_file).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Refresh", command=lambda: self.refresh_conflicts_list(conflicts_tree)).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Close", command=conflicts_window.destroy).pack(side=tk.RIGHT, padx=5)


    def get_conflict_status(self, file_path):
        """Get human-readable conflict status"""
        try:
            status_output = self.repo.git.status('--porcelain')
            for line in status_output.split('\n'):
                if file_path in line:
                    status_code = line[:2]
                    if status_code == 'UU':
                        return 'Both Modified'
                    elif status_code == 'AA':
                        return 'Both Added'
                    elif status_code == 'DD':
                        return 'Both Deleted'
                    elif status_code == 'AU':
                        return 'Added by Us'
                    elif status_code == 'UA':
                        return 'Added by Them'
                    elif status_code == 'DU':
                        return 'Deleted by Us'
                    elif status_code == 'UD':
                        return 'Deleted by Them'
            return 'Unknown Conflict'
        except:
            return 'Unknown'


    def complete_merge(self):
        """Complete the merge process"""
        try:
            # Check if there are still conflicts
            in_merge, conflicted_files = self.check_merge_status()
            
            if conflicted_files:
                messagebox.showerror("Conflicts Remain", 
                    f"Cannot complete merge. {len(conflicted_files)} files still have conflicts.")
                return
            
            # Get merge commit message
            merge_msg = simpledialog.askstring("Merge Commit", "Enter merge commit message:", 
                                            initialvalue="Merge branch")
            
            if merge_msg:
                self.repo.git.commit('-m', merge_msg)
                messagebox.showinfo("Merge Complete", "Merge completed successfully!")
                self.refresh_all()
                self.update_merge_navbar_status()
        
        except Exception as e:
            messagebox.showerror("Merge Error", f"Failed to complete merge: {str(e)}")


    def abort_merge(self):
        """Abort the merge process"""
        if messagebox.askyesno("Abort Merge", "Are you sure you want to abort the merge?"):
            try:
                self.repo.git.merge('--abort')
                messagebox.showinfo("Merge Aborted", "Merge has been aborted.")
                self.refresh_all()
                self.update_merge_navbar_status()
            except Exception as e:
                messagebox.showerror("Abort Error", f"Failed to abort merge: {str(e)}")

    
    def create_enhanced_toolbar(self):
        """Enhanced toolbar with operation-aware buttons"""
        toolbar = ttk.Frame(self.root)
        toolbar.pack(side=tk.TOP, fill=tk.X, padx=5, pady=2)
        
        # Repository info (same as before)
        ttk.Label(toolbar, text="Repository:").pack(side=tk.LEFT, padx=5)
        self.repo_label = ttk.Label(toolbar, text=self.repo_path, font=('TkDefaultFont', 9, 'bold'))
        self.repo_label.pack(side=tk.LEFT, padx=5)
        
        ttk.Separator(toolbar, orient=tk.VERTICAL).pack(side=tk.LEFT, fill=tk.Y, padx=10)
        
        # Branch info
        branch_frame = ttk.Frame(toolbar)
        branch_frame.pack(side=tk.LEFT, padx=10)
        
        ttk.Label(branch_frame, text="Current:", font=('TkDefaultFont', 9)).pack(side=tk.LEFT)
        self.branch_label = ttk.Label(branch_frame, text="", font=('TkDefaultFont', 10, 'bold'), 
                                    foreground='#007bff')
        self.branch_label.pack(side=tk.LEFT, padx=(5,0))
        
        ttk.Separator(toolbar, orient=tk.VERTICAL).pack(side=tk.LEFT, fill=tk.Y, padx=10)
        
        # Enhanced action buttons with operation states
        self.pull_button = ttk.Button(toolbar, text="Pull", command=self.enhanced_git_pull)
        self.pull_button.pack(side=tk.LEFT, padx=2)
        
        self.push_button = ttk.Button(toolbar, text="Push", command=self.enhanced_git_push)
        self.push_button.pack(side=tk.LEFT, padx=2)
        
        self.commit_button = ttk.Button(toolbar, text="Commit", command=self.enhanced_git_commit)
        self.commit_button.pack(side=tk.LEFT, padx=2)
        
        self.add_all_button = ttk.Button(toolbar, text="Add All", command=self.enhanced_git_add_all)
        self.add_all_button.pack(side=tk.LEFT, padx=2)
        
        self.refresh_button = ttk.Button(toolbar, text="Refresh", command=self.enhanced_refresh_all)
        self.refresh_button.pack(side=tk.LEFT, padx=2)
        
        # Right side info (same as before)
        right_info_frame = ttk.Frame(toolbar)
        right_info_frame.pack(side=tk.RIGHT, padx=5)
        
        self.remote_label = ttk.Label(right_info_frame, text="", font=('TkDefaultFont', 8))
        self.remote_label.pack(anchor=tk.E)
        
        user_frame = ttk.Frame(right_info_frame)
        user_frame.pack(anchor=tk.E)
        
        self.user_label = ttk.Label(user_frame, text="", font=('TkDefaultFont', 8))
        self.user_label.pack(side=tk.LEFT)
        
        ttk.Button(user_frame, text="Config", command=self.show_config, width=8).pack(side=tk.LEFT, padx=(5,0))


    def set_button_operating_state(self, button, operation_name):
        """Set button to operating state"""
        button.configure(text=f"{operation_name}...", style='Operating.TButton', state=tk.DISABLED)


    def reset_button_state(self, button, original_text):
        """Reset button to normal state"""
        button.configure(text=original_text, style='TButton', state=tk.NORMAL)


    def enhanced_git_pull(self):
        """Enhanced git pull with visual feedback"""
        self.set_button_operating_state(self.pull_button, "Pulling")
        
        def pull_worker():
            try:
                self.repo.remotes.origin.pull()
                self.root.after(0, lambda: self.complete_operation(self.pull_button, "Pull", "Pull completed successfully"))
            except Exception as e:
                self.root.after(0, lambda: self.handle_operation_error(self.pull_button, "Pull", str(e)))
        
        threading.Thread(target=pull_worker, daemon=True).start()


    def enhanced_git_push(self):
        """Enhanced git push with visual feedback"""
        self.set_button_operating_state(self.push_button, "Pushing")
        
        def push_worker():
            try:
                self.repo.remotes.origin.push()
                self.root.after(0, lambda: self.complete_operation(self.push_button, "Push", "Push completed successfully"))
            except Exception as e:
                self.root.after(0, lambda: self.handle_operation_error(self.push_button, "Push", str(e)))
        
        threading.Thread(target=push_worker, daemon=True).start()


    def enhanced_git_commit(self):
        """Enhanced git commit with visual feedback"""
        self.set_button_operating_state(self.commit_button, "Committing")
        
        # Get commit message first
        message = simpledialog.askstring("Commit Message", "Enter commit message:")
        if not message:
            self.reset_button_state(self.commit_button, "Commit")
            return
        
        def commit_worker():
            try:
                self.repo.index.commit(message)
                self.root.after(0, lambda: self.complete_operation(self.commit_button, "Commit", "Commit completed successfully"))
            except Exception as e:
                self.root.after(0, lambda: self.handle_operation_error(self.commit_button, "Commit", str(e)))
        
        threading.Thread(target=commit_worker, daemon=True).start()


    def enhanced_git_add_all(self):
        """Enhanced git add all with visual feedback"""
        self.set_button_operating_state(self.add_all_button, "Adding")
        
        def add_worker():
            try:
                self.repo.git.add('-A')
                self.root.after(0, lambda: self.complete_operation(self.add_all_button, "Add All", "All changes added to staging"))
            except Exception as e:
                self.root.after(0, lambda: self.handle_operation_error(self.add_all_button, "Add All", str(e)))
        
        threading.Thread(target=add_worker, daemon=True).start()


    def enhanced_refresh_all(self):
        """Enhanced refresh with visual feedback"""
        self.set_button_operating_state(self.refresh_button, "Refreshing")
        
        def refresh_worker():
            try:
                time.sleep(0.5)  # Brief delay to show the state change
                self.root.after(0, self.refresh_all_data)
                self.root.after(0, lambda: self.complete_operation(self.refresh_button, "Refresh", "Repository refreshed"))
            except Exception as e:
                self.root.after(0, lambda: self.handle_operation_error(self.refresh_button, "Refresh", str(e)))
        
        threading.Thread(target=refresh_worker, daemon=True).start()


    def complete_operation(self, button, operation_name, success_message):
        """Complete operation with success feedback"""
        self.reset_button_state(button, operation_name)
        self.status_label.config(text=f"✓ {success_message}")
        self.update_merge_navbar_status()  # Check for merge status after operations


    def handle_operation_error(self, button, operation_name, error_message):
        """Handle operation error with feedback"""
        self.reset_button_state(button, operation_name)
        self.status_label.config(text=f"✗ {operation_name} failed: {error_message}")
        messagebox.showerror(f"{operation_name} Error", error_message)


    def refresh_all_data(self):
        """Refresh all data components"""
        self.update_file_status_cache_enhanced()
        self.populate_repository_tree()
        self.populate_changes()
        
        # Refresh current file list if a folder is selected
        tree_selection = self.repo_tree.selection()
        if tree_selection:
            tree_item = self.repo_tree.item(tree_selection[0])
            values = tree_item['values']
            if values:
                folder_path = values[0]
                self.populate_file_list_enhanced(folder_path)


    # ==========================================
    # 5. INTEGRATION METHODS
    # ==========================================

    def setup_enhanced_refresh_cycle(self):
        """Setup enhanced refresh cycle with merge detection"""
        def refresh_cycle():
            if self.repo:
                self.update_file_status_cache_enhanced()
                self.update_merge_navbar_status()
            
            # Schedule next refresh
            self.root.after(5000, refresh_cycle)  # Every 5 seconds
        
        # Start the cycle
        refresh_cycle()
###



def main():
    """Main function"""
    root = tk.Tk()
    
    # Get repository path from command line argument
    repo_path = sys.argv[1] if len(sys.argv) > 1 else None
    
    # Create and run application
    app = GitPythonGUI(root, repo_path)
    root.mainloop()

if __name__ == "__main__":
    main()