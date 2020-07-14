# empress_gui.py

import tkinter as tk
from tkinter import messagebox
import os
import sys
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk

import empress
from empress import input_reader
from empress.recon_vis.utils import dict_to_tree
from empress.recon_vis import tree

def resource_path(relative_path):
    # The path can be different under pyinstaller
    # see https://stackoverflow.com/questions/57132421/relative-path-setting-fail-via-pyinstaller
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath("."), relative_path)

class App(tk.Frame):

    def __init__(self, master):
        tk.Frame.__init__(self, master)
        self.init_frames(master)
        self.init_load_files()
        self.init_view_tanglegram()
        self.init_view_cost_space()
        self.init_compute_reconciliations()
        self.init_view_solution_space()
        self.init_view_reconciliations()
        self.init_view_pvalue_histogram()
        self.init_windows()

    def init_frames(self, master):
        self.master = master
        self.master.grid_rowconfigure(0, weight=2)
        self.master.grid_rowconfigure(1, weight=1)
        self.master.grid_rowconfigure(2, weight=1)
        self.master.grid_rowconfigure(3, weight=1)
        self.master.grid_rowconfigure(4, weight=1)
        self.master.grid_columnconfigure(0, weight=1)
        self.master.grid_columnconfigure(1, weight=1)
        # To display the dividing lines among different frames
        self.master.configure(background="grey")

        # Create a logo frame on top of the self.master frame
        self.logo_frame = tk.Frame(self.master)
        # sticky="nsew" means that self.logo_frame expands in all four directions (north, south, east and west) 
        # to fully occupy the allocated space in the grid system (row 0 column 0-1)
        self.logo_frame.grid(row=0, column=0, columnspan=2, sticky="nsew")
        self.logo_frame.grid_propagate(False)
        # Add logo image in self.logo_frame
        photo = tk.PhotoImage(file=resource_path("assets/jane_logo_thin.gif"))
        label = tk.Label(self.logo_frame, image=photo)
        label.place(x=0, y=0)
        label.image = photo

        # Create an input frame on the left side of the self.master frame
        self.input_frame = tk.Frame(self.master)
        self.input_frame.grid(row=1, column=0, rowspan=4, sticky="nsew", padx=(0, 1), pady=(1, 0))
        self.input_frame.grid_rowconfigure(0, weight=1)
        self.input_frame.grid_rowconfigure(1, weight=1)
        self.input_frame.grid_rowconfigure(2, weight=1)
        self.input_frame.grid_rowconfigure(3, weight=1)
        self.input_frame.grid_rowconfigure(4, weight=1)
        self.input_frame.grid_rowconfigure(5, weight=1)
        self.input_frame.grid_rowconfigure(6, weight=1)
        self.input_frame.grid_columnconfigure(0, weight=1)
        self.input_frame.grid_propagate(False)

        # Create an input information frame
        # to display the numbers of tips for host and parasite trees
        self.input_info_frame = tk.Frame(self.master)
        self.input_info_frame.grid(row=1, column=1, sticky="nsew", pady=(1,1))
        self.input_info_frame.grid_rowconfigure(0, weight=1)
        self.input_info_frame.grid_rowconfigure(1, weight=1)
        self.input_info_frame.grid_rowconfigure(2, weight=1)
        self.input_info_frame.grid_columnconfigure(0, weight=1)
        self.input_info_frame.grid_propagate(False)

        # Creates a frame for setting DTL costs
        self.costs_frame = tk.Frame(self.master)
        self.costs_frame.grid(row=2, column=1, sticky="nsew", pady=(0,1))
        self.costs_frame.grid_rowconfigure(0, weight=1)
        self.costs_frame.grid_rowconfigure(1, weight=4)
        self.costs_frame.grid_columnconfigure(0, weight=1)
        self.costs_frame.grid_columnconfigure(1, weight=1)
        self.costs_frame.grid_propagate(False)

        # Creates a frame for showing reconciliation results as numbers
        self.recon_nums_frame = tk.Frame(self.master)
        self.recon_nums_frame.grid(row=3, column=1, sticky="nsew", pady=(0,1))
        self.recon_nums_frame.grid_rowconfigure(0, weight=1)
        self.recon_nums_frame.grid_rowconfigure(1, weight=1)
        self.recon_nums_frame.grid_rowconfigure(2, weight=1)
        self.recon_nums_frame.grid_rowconfigure(3, weight=1)
        self.recon_nums_frame.grid_rowconfigure(4, weight=1)
        self.recon_nums_frame.grid_columnconfigure(0, weight=1)
        self.recon_nums_frame.grid_columnconfigure(1, weight=7)
        self.recon_nums_frame.grid_propagate(False)

        # To occupy empty space so the grey background in self.master is not shown
        self.empty_frame = tk.Frame(self.master)
        self.empty_frame.grid(row=4, column=1, sticky="nsew")

    def init_load_files(self):
        # "Load files" dropdown
        # Load in three input files and display the number of leaves in each tree 
        # and the entry boxes for setting DTL costs
        self.load_files_var = tk.StringVar(self.input_frame)
        self.load_files_var.set("Load files")
        self.load_files_options = ["Load host tree file", "Load parasite tree file", "Load mapping file"]
        self.load_files_dropdown = tk.OptionMenu(self.input_frame, self.load_files_var, *self.load_files_options, command=self.load_input_files)
        self.load_files_dropdown.configure(width=15)
        self.load_files_dropdown.grid(row=0, column=0)
        # Force a sequence of loading host tree file first, and then parasite tree file, and then mapping file
        self.load_files_dropdown['menu'].entryconfigure("Load parasite tree file", state = "disabled")
        self.load_files_dropdown['menu'].entryconfigure("Load mapping file", state = "disabled")

        self.host_tree_info = tk.Label(self.input_info_frame)
        self.parasite_tree_info = tk.Label(self.input_info_frame)
        self.mapping_info = tk.Label(self.input_info_frame)
        self.recon_input = empress.ReconInputWrapper()
        self.first_time_loading_files = True
        self.need_to_reset = True

    def init_view_tanglegram(self):
        # "View tanglegram" button
        self.view_tanglegram_btn = tk.Button(self.input_frame, text="View tanglegram", command=self.display_tanglegram, state=tk.DISABLED, width=18)
        self.view_tanglegram_btn.grid(row=1, column=0)

    def init_view_cost_space(self):
        # "View cost space" button
        self.view_cost_space_btn = tk.Button(self.input_frame, text="View cost space", command=self.plot_cost_regions, state=tk.DISABLED, width=18)
        self.view_cost_space_btn.grid(row=2, column=0)

        self.dup_label = tk.Label(self.costs_frame)
        self.dup_entry_box = CustomEntry(self.costs_frame)
        self.trans_label = tk.Label(self.costs_frame)
        self.trans_entry_box = tk.Entry(self.costs_frame)
        self.loss_label = tk.Label(self.costs_frame)
        self.loss_entry_box = tk.Entry(self.costs_frame)
        self.dup_input = tk.DoubleVar()
        self.dup_input.set(1.00)
        self.trans_input = tk.DoubleVar()
        self.trans_input.set(1.00)
        self.loss_input = tk.DoubleVar()
        self.loss_input.set(1.00)
        self.dup_cost = None
        self.trans_cost = None
        self.loss_cost = None

    def init_compute_reconciliations(self):
        # "Compute reconciliations" button
        self.compute_reconciliations_btn = tk.Button(self.input_frame, text="Compute reconciliations", command=self.display_recon_information, state=tk.DISABLED, width=18)
        self.compute_reconciliations_btn.grid(row=3, column=0)

        self.recon_MPRs_label = tk.Label(self.recon_nums_frame)
        self.recon_count_label = tk.Label(self.recon_nums_frame)
        self.recon_cospeci_label = tk.Label(self.recon_nums_frame)
        self.cospec_count_label = tk.Label(self.recon_nums_frame)
        self.recon_dup_label = tk.Label(self.recon_nums_frame)
        self.dup_count_label = tk.Label(self.recon_nums_frame)
        self.recon_trans_label = tk.Label(self.recon_nums_frame)
        self.trans_count_label = tk.Label(self.recon_nums_frame)
        self.recon_loss_label = tk.Label(self.recon_nums_frame)
        self.loss_count_label = tk.Label(self.recon_nums_frame)
        self.recon_info_displayed = False
        App.recon_graph = None

    def init_view_solution_space(self):
        # "View solution space" dropdown
        self.view_solution_space_var = tk.StringVar(self.input_frame)
        self.view_solution_space_var.set("View solution space")
        self.view_solution_space_options = ["Entire space", "Clusters"]
        self.view_solution_space_dropdown = tk.OptionMenu(self.input_frame, self.view_solution_space_var, *self.view_solution_space_options, command=self.select_from_view_solution_space_dropdown)
        self.view_solution_space_dropdown.configure(width=15)
        self.view_solution_space_dropdown.configure(state=tk.DISABLED)
        self.view_solution_space_dropdown.grid(row=4, column=0)

        self.num_cluster_input = tk.IntVar()
        self.num_cluster_input.set(1)
        self.num_cluster = None
        App.clusters_list = []
        App.medians = None

    def init_view_reconciliations(self):
        # "View reconciliations" dropdown
        self.view_reconciliations_var = tk.StringVar(self.input_frame)
        self.view_reconciliations_var.set("View reconciliations")
        self.view_reconciliations_options = ["One MPR", "One per cluster"]
        self.view_reconciliations_dropdown = tk.OptionMenu(self.input_frame, self.view_reconciliations_var, *self.view_reconciliations_options, command=self.select_from_view_reconciliations_dropdown)
        self.view_reconciliations_dropdown.configure(width=15)
        self.view_reconciliations_dropdown.configure(state=tk.DISABLED)
        self.view_reconciliations_dropdown['menu'].entryconfigure("One per cluster", state = "disabled")
        self.view_reconciliations_dropdown.grid(row=5, column=0)

    def init_view_pvalue_histogram(self):
        # "View p-value histogram" button
        self.view_pvalue_histogram_btn = tk.Button(self.input_frame, text="View p-value histogram", command=self.open_window_pvalue_histogram, state=tk.DISABLED, width=18)
        self.view_pvalue_histogram_btn.grid(row=6, column=0)

    def init_windows(self):
        self.tanglegram_window = None
        self.cost_space_window = None
        self.entire_space_window = None
        self.set_num_cluster_window = None
        self.one_MPR_window = None
        self.view_solution_space_window = None
        self.view_reconciliations_window = None
        self.view_pvalue_histogram_window = None
    
    def refresh_when_reload_host(self):
        if self.first_time_loading_files:
            self.recon_input.read_host(self.host_file_path)
            self.host_tree_info.destroy()
        else:
            if self.need_to_reset:
                self.reset()
            self.recon_input.read_host(self.host_file_path)
            self.host_tree_info.destroy()
            self.parasite_tree_info.destroy()
            self.mapping_info.destroy()
    
    def refresh_when_reload_parasite(self):
        if self.first_time_loading_files:
            self.recon_input.read_parasite(self.parasite_file_path)
            self.parasite_tree_info.destroy()
        else:
            if self.need_to_reset:
                self.reset()
            self.recon_input.read_host(self.host_file_path)
            self.recon_input.read_parasite(self.parasite_file_path)
            self.parasite_tree_info.destroy()
            self.mapping_info.destroy()
    
    def refresh_when_reload_mapping(self):
        if self.first_time_loading_files:
            self.recon_input.read_mapping(self.mapping_file_path)
            self.mapping_info.destroy()
            self.first_time_loading_files = False
        else:
            if self.need_to_reset:
                self.reset()
            self.recon_input.read_host(self.host_file_path)
            self.recon_input.read_parasite(self.parasite_file_path)
            self.recon_input.read_mapping(self.mapping_file_path)
            self.mapping_info.destroy()  
            self.need_to_reset = True  

    def reset(self):
        App.recon_graph = None
        App.clusters_list = []
        App.medians = None
        self.recon_input = empress.ReconInputWrapper()
        self.view_cost_space_btn.configure(state=tk.DISABLED)
        self.view_tanglegram_btn.configure(state=tk.DISABLED)

        # Reset dtl costs so self.compute_reconciliations_btn can be disabled
        self.dup_cost = None
        self.trans_cost = None
        self.loss_cost = None
        self.dup_input.set(1.00)
        self.trans_input.set(1.00)
        self.loss_input.set(1.00)
        self.compute_reconciliations_btn.configure(state=tk.DISABLED)
        self.disable_unaccessable_widgets()

        # Reset the rest
        self.dup_label.destroy()
        self.dup_entry_box.destroy()
        self.trans_label.destroy()
        self.trans_entry_box.destroy()
        self.loss_label.destroy()
        self.loss_entry_box.destroy()

        self.recon_MPRs_label.destroy()
        self.recon_count_label.destroy()
        self.recon_cospeci_label.destroy()
        self.cospec_count_label.destroy()
        self.recon_dup_label.destroy()
        self.dup_count_label.destroy()
        self.recon_trans_label.destroy()
        self.trans_count_label.destroy()
        self.recon_loss_label.destroy()
        self.loss_count_label.destroy()

        self.num_cluster_input = tk.IntVar()
        self.num_cluster_input.set(1)
        self.num_cluster = None

        self.recon_info_displayed = False
        if self.tanglegram_window is not None and self.tanglegram_window.winfo_exists():
            self.tanglegram_window.destroy()
        if self.cost_space_window is not None and self.cost_space_window.winfo_exists():
            self.cost_space_window.destroy()
        self.close_unnecessary_windows_if_opened()
        self.view_reconciliations_dropdown['menu'].entryconfigure("One per cluster", state = "disabled")
        self.need_to_reset = False

    def close_unnecessary_windows_if_opened(self):
        if self.entire_space_window is not None and self.entire_space_window.winfo_exists():
            self.entire_space_window.destroy()

        if self.set_num_cluster_window is not None and self.set_num_cluster_window.winfo_exists():
            self.set_num_cluster_window.destroy()

        if self.view_solution_space_window is not None and self.view_solution_space_window.winfo_exists():
            self.view_solution_space_window.destroy()

        if self.one_MPR_window is not None and self.one_MPR_window.winfo_exists():
            self.one_MPR_window.destroy()

        if self.view_reconciliations_window is not None and self.view_reconciliations_window.winfo_exists():
            self.view_reconciliations_window.destroy()

        if self.view_pvalue_histogram_window is not None and self.view_pvalue_histogram_window.winfo_exists():
            self.view_pvalue_histogram_window.destroy()

    def disable_unaccessable_widgets(self):
        self.view_solution_space_dropdown.configure(state=tk.DISABLED)
        self.view_reconciliations_dropdown.configure(state=tk.DISABLED)
        self.view_pvalue_histogram_btn.configure(state=tk.DISABLED)

    def load_input_files(self, event):
        """Load in two .nwk files for the host tree and parasite tree, and one .mapping file. Display the number of tips for
        the trees and a message to indicate the successful reading of the tips mapping."""
        # Clicking on "Load host tree file"
        if self.load_files_var.get() == "Load host tree file":
            self.load_files_var.set("Load files")
            # initialdir is set to be the current working directory
            input_file = tk.filedialog.askopenfilename(initialdir=os.getcwd(), title="Select a host file",
                                                       filetypes=[("Newick Trees", "*.nwk *.newick *.tree")])
            if input_file != "":
                try:
                    self.recon_input.read_host(input_file)
                except Exception as e:
                    messagebox.showinfo("Warning", "Error: " + str(e))
                self.host_file_path = input_file
                # Force a sequence of loading host tree file first, and then parasite tree file, and then mapping file
                self.load_files_dropdown['menu'].entryconfigure("Load parasite tree file", state = "disabled")
                self.load_files_dropdown['menu'].entryconfigure("Load mapping file", state = "disabled")
                self.refresh_when_reload_host()
                self.update_host_info()
                self.load_files_dropdown['menu'].entryconfigure("Load parasite tree file", state = "normal")

        # Clicking on "Load parasite tree file"
        elif self.load_files_var.get() == "Load parasite tree file":
            self.load_files_var.set("Load files")
            # initialdir is set to be the current working directory
            input_file = tk.filedialog.askopenfilename(initialdir=os.getcwd(), title="Select a parasite file",
                                                       filetypes=[("Newick Trees", "*.nwk *.newick *.tree")])
            if input_file != "":
                try:
                    self.recon_input.read_parasite(input_file)
                except Exception as e:
                    messagebox.showinfo("Warning", "Error: " + str(e))
                self.parasite_file_path = input_file
                self.refresh_when_reload_parasite()
                self.update_parasite_info()
                self.load_files_dropdown['menu'].entryconfigure("Load mapping file", state = "normal")

        # Clicking on "Load mapping file"
        elif self.load_files_var.get() == "Load mapping file":
            self.load_files_var.set("Load files")
            # initialdir is set to be the current working directory
            input_file = tk.filedialog.askopenfilename(initialdir=os.getcwd(), title="Select a mapping file",
                                                       filetypes=[("Tip mapping", "*.mapping")])
            if input_file != "":
                try:
                    self.recon_input.read_mapping(input_file)
                except Exception as e:
                    messagebox.showinfo("Warning", "Error: " + str(e))
                self.mapping_file_path = input_file
                self.refresh_when_reload_mapping()
                self.update_mapping_info()
                if self.recon_input.is_complete():
                    self.view_tanglegram_btn.configure(state=tk.NORMAL)
                    self.view_cost_space_btn.configure(state=tk.NORMAL)
                    self.compute_reconciliations_btn.configure(state=tk.NORMAL)
                    self.create_dtl_costs_boxes()
                    self.first_time_loading_files = False

    def compute_tree_tips(self, tree_type):
        """Compute the number of tips for the host tree and parasite tree inputs."""
        if tree_type == "host tree":
            host_tree_object = dict_to_tree(self.recon_input.host_dict, tree.TreeType.HOST)
            return len(host_tree_object.leaf_list())
        elif tree_type == "parasite tree":
            parasite_tree_object = dict_to_tree(self.recon_input.parasite_dict, tree.TreeType.PARASITE)
            return len(parasite_tree_object.leaf_list())

    def update_host_info(self):
        host_tree_tips_number = self.compute_tree_tips("host tree")
        self.host_tree_info = tk.Label(self.input_info_frame, text="Host: "+os.path.basename(self.host_file_path)+": "+str(host_tree_tips_number)+" tips")
        self.host_tree_info.grid(row=0, column=0, sticky="w")

    def update_parasite_info(self):
        parasite_tree_tips_number = self.compute_tree_tips("parasite tree")
        self.parasite_tree_info = tk.Label(self.input_info_frame, text="Parasite/symbiont: "+os.path.basename(self.parasite_file_path)+": "+str(parasite_tree_tips_number)+" tips")
        self.parasite_tree_info.grid(row=1, column=0, sticky="w")

    def update_mapping_info(self):
        self.mapping_info = tk.Label(self.input_info_frame, text="Mapping: "+os.path.basename(self.mapping_file_path))
        self.mapping_info.grid(row=2, column=0, sticky="w")

    def display_tanglegram(self):
        """Display a tanglegram in a new tkinter window."""
        # Creates a new tkinter window
        self.tanglegram_window = tk.Toplevel(self.master)
        self.tanglegram_window.geometry("600x600")
        self.tanglegram_window.title("Tanglegram")
        # Creates a new frame
        tanglegram_frame = tk.Frame(self.tanglegram_window)
        tanglegram_frame.pack(fill=tk.BOTH, expand=1)
        tanglegram_frame.pack_propagate(False)
        fig = self.recon_input.draw()
        canvas = FigureCanvasTkAgg(fig, tanglegram_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=True)
        # The toolbar allows the user to zoom in/out, drag the graph and save the graph
        toolbar = NavigationToolbar2Tk(canvas, tanglegram_frame)
        toolbar.update()
        canvas.get_tk_widget().pack(side=tk.TOP)

    def plot_cost_regions(self):
        """Plot the cost regions using matplotlib and embed the graph in a tkinter window."""
        self.disable_unaccessable_widgets()
        # Creates a new tkinter window
        self.cost_space_window = tk.Toplevel(self.master)
        self.cost_space_window.geometry("550x550")
        self.cost_space_window.title("Matplotlib Graph - Cost regions")
        # Creates a new frame
        plt_frame = tk.Frame(self.cost_space_window)
        plt_frame.pack(fill=tk.BOTH, expand=1)
        plt_frame.pack_propagate(False)
        cost_regions = self.recon_input.compute_cost_regions(0.5, 10, 0.5, 10)
        fig = cost_regions.draw()  # creates matplotlib figure
        canvas = FigureCanvasTkAgg(fig, plt_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=True)
        # The toolbar allows the user to zoom in/out, drag the graph and save the graph
        toolbar = NavigationToolbar2Tk(canvas, plt_frame)
        toolbar.update()
        canvas.get_tk_widget().pack(side=tk.TOP)
        # Updates the DTL costs using the x,y coordinates clicked by the user inside the graph
        # Otherwise pops up a warning message window
        fig.canvas.callbacks.connect('button_press_event', self.get_xy_coordinates)

    def get_xy_coordinates(self, event):
        """Update the DTL costs when user clicks on the matplotlib graph, otherwise pop up a warning message window."""
        if event.inaxes is not None:
            self.dup_input.set(round(event.xdata, 2))
            self.trans_input.set(round(event.ydata, 2))
            self.loss_input.set("1.00")
            # Enables the next step, viewing reconciliation result
            self.dup_cost = event.xdata
            self.trans_cost = event.ydata
            self.loss_cost = 1.00
            self.update_compute_reconciliations_btn()
        else:
            messagebox.showinfo("Warning", "Please click inside the axes bounds.")

    def create_dtl_costs_boxes(self):
        """Set DTL costs by clicking on the matplotlib graph or by entering manually."""
        self.dup_label = tk.Label(self.costs_frame, text="Duplication cost:")
        self.dup_label.grid(row=0, column=0, sticky="w")
        # %P = value of the entry if the edit is allowed
        # see https://stackoverflow.com/questions/4140437/interactively-validating-entry-widget-content-in-tkinter
        dup_vcmd = (self.register(self.validate_dup_input), '%P')
        # self.dup_input is tk.DoubleVar(), initialized to be 1.00
        self.dup_entry_box = CustomEntry(self.costs_frame, width=4, textvariable=self.dup_input)
        self.dup_entry_box.set_border_color("green")
        self.dup_entry_box.validate(validate="key", validatecommand=dup_vcmd)
        self.dup_entry_box.grid(row=0, column=1, sticky="w")
        self.validate_dup_input(str(self.dup_entry_box.get()))  # validate for the initialization of self.dup_input to be 1.00

        self.trans_label = tk.Label(self.costs_frame, text="Transfer cost:")
        self.trans_label.grid(row=1, column=0, sticky="w")
        # %P = value of the entry if the edit is allowed
        # see https://stackoverflow.com/questions/4140437/interactively-validating-entry-widget-content-in-tkinter
        trans_vcmd = (self.register(self.validate_trans_input), '%P')
        # self.trans_input is tk.DoubleVar(), initialized to be 1.00
        self.trans_entry_box = CustomEntry(self.costs_frame, width=4, textvariable=self.trans_input)
        self.trans_entry_box.set_border_color("green")
        self.trans_entry_box.validate(validate="all", validatecommand=trans_vcmd)
        self.trans_entry_box.grid(row=1, column=1, sticky="w")
        self.validate_trans_input(str(self.trans_entry_box.get()))  # validate for the initialization of self.trans_input to be 1.0

        self.loss_label = tk.Label(self.costs_frame, text="Loss cost:")
        self.loss_label.grid(row=2, column=0, sticky="w")
        # %P = value of the entry if the edit is allowed
        # see https://stackoverflow.com/questions/4140437/interactively-validating-entry-widget-content-in-tkinter
        loss_vcmd = (self.register(self.validate_loss_input), '%P')
        # self.loss_input is tk.DoubleVar(), initialized to be 1.00
        self.loss_entry_box = CustomEntry(self.costs_frame, width=4, textvariable=self.loss_input)
        self.loss_entry_box.set_border_color("green")
        self.loss_entry_box.validate(validate="all", validatecommand=loss_vcmd)
        self.loss_entry_box.grid(row=2, column=1, sticky="w")
        self.validate_loss_input(str(self.loss_entry_box.get()))  # validate for the initialization of self.loss_input to be 1.00
    
    def validate_dup_input(self, input_after_change: str):
        """Duplication cost is only allowed to be a float that is >= 0."""
        try:
            val = float(input_after_change)
            if val >= 0:
                self.dup_cost = val
                self.dup_entry_box.set_border_color("green")
            else:
                self.dup_cost = None   
                self.dup_entry_box.set_border_color("red")
        except ValueError:
            self.dup_cost = None
            self.dup_entry_box.set_border_color("red")
        
        self.update_compute_reconciliations_btn()
        return True  # return True means allowing the change to happen

    def validate_trans_input(self, input_after_change: str):
        """Transfer cost is only allowed to be a float that is >= 0."""
        try:
            val = float(input_after_change)
            if val >= 0:
                self.trans_cost = val
                self.trans_entry_box.set_border_color("green")
            else:
                self.trans_cost = None   
                self.trans_entry_box.set_border_color("red")
        except ValueError:
            self.trans_cost = None
            self.trans_entry_box.set_border_color("red")
        
        self.update_compute_reconciliations_btn()
        return True  # return True means allowing the change to happen
    
    def validate_loss_input(self, input_after_change: str):
        """Loss cost is only allowed to be a float that is >= 0."""
        try:
            val = float(input_after_change)
            if val >= 0:
                self.loss_cost = val
                self.loss_entry_box.set_border_color("green")
            else:
                self.loss_cost = None   
                self.loss_entry_box.set_border_color("red")
        except ValueError:
            self.loss_cost = None
            self.loss_entry_box.set_border_color("red")

        self.update_compute_reconciliations_btn()
        return True  # return True means allowing the change to happen

    def update_compute_reconciliations_btn(self):
        """When the dtl costs inputs are all valid, enable the next button and close unnecessary windows."""
        if self.dup_cost is not None and self.trans_cost is not None and self.loss_cost is not None:
            # Enable the next button
            self.compute_reconciliations_btn.configure(state=tk.NORMAL)
            self.disable_unaccessable_widgets()
            self.close_unnecessary_windows_if_opened()
        else:
            self.compute_reconciliations_btn.configure(state=tk.DISABLED)

    def display_recon_information(self):
        """Display numeric reconciliation results and close unnecessary windows."""
        App.recon_graph = self.recon_input.reconcile(self.dup_cost, self.trans_cost, self.loss_cost)
        self.recon_count = App.recon_graph.n_recon
        self.cospec_count, self.dup_count, self.trans_count, self.loss_count = App.recon_graph.median().count_events()
        if not self.recon_info_displayed:
            # Display numeric reconciliation results
            self.recon_MPRs_label = tk.Label(self.recon_nums_frame, text="Number of MPRs: ")
            self.recon_MPRs_label.grid(row=0, column=0, sticky="w")
            self.recon_count_label = tk.Label(self.recon_nums_frame, text=self.recon_count)
            self.recon_count_label.grid(row=0, column=1, sticky="w")
            self.recon_cospeci_label = tk.Label(self.recon_nums_frame, text="# Cospeciations:")
            self.recon_cospeci_label.grid(row=1, column=0, sticky="w")
            self.cospec_count_label = tk.Label(self.recon_nums_frame, text=self.cospec_count)
            self.cospec_count_label.grid(row=1, column=1, sticky="w")
            self.recon_dup_label = tk.Label(self.recon_nums_frame, text="# Duplications:")
            self.recon_dup_label.grid(row=2, column=0, sticky="w")
            self.dup_count_label = tk.Label(self.recon_nums_frame, text=self.dup_count)
            self.dup_count_label.grid(row=2, column=1, sticky="w")
            self.recon_trans_label = tk.Label(self.recon_nums_frame, text="# Transfers:")
            self.recon_trans_label.grid(row=3, column=0, sticky="w")
            self.trans_count_label = tk.Label(self.recon_nums_frame, text=self.trans_count)
            self.trans_count_label.grid(row=3, column=1, sticky="w")
            self.recon_loss_label = tk.Label(self.recon_nums_frame, text="# Losses:")
            self.recon_loss_label.grid(row=4, column=0, sticky="w")
            self.loss_count_label = tk.Label(self.recon_nums_frame, text=self.loss_count)
            self.loss_count_label.grid(row=4, column=1, sticky="w")
            self.recon_info_displayed = True
        else:
            self.recon_count_label.destroy()
            self.recon_count_label = tk.Label(self.recon_nums_frame, text=self.recon_count)
            self.recon_count_label.grid(row=0, column=1, sticky="w")
            self.cospec_count_label.destroy()
            self.cospec_count_label = tk.Label(self.recon_nums_frame, text=self.cospec_count)
            self.cospec_count_label.grid(row=1, column=1, sticky="w")
            self.dup_count_label.destroy()
            self.dup_count_label = tk.Label(self.recon_nums_frame, text=self.dup_count)
            self.dup_count_label.grid(row=2, column=1, sticky="w")
            self.trans_count_label.destroy()
            self.trans_count_label = tk.Label(self.recon_nums_frame, text=self.trans_count)
            self.trans_count_label.grid(row=3, column=1, sticky="w")
            self.loss_count_label.destroy()
            self.loss_count_label = tk.Label(self.recon_nums_frame, text=self.loss_count)
            self.loss_count_label.grid(row=4, column=1, sticky="w")

        self.close_unnecessary_windows_if_opened()
        self.view_solution_space_dropdown.configure(state=tk.NORMAL)
        self.view_reconciliations_dropdown.configure(state=tk.NORMAL)
        self.view_pvalue_histogram_btn.configure(state=tk.NORMAL)

    def select_from_view_solution_space_dropdown(self, event):
        """When "View solution space" dropdown is clicked."""
        if self.view_solution_space_var.get() == "Entire space":
            self.view_solution_space_var.set("View solution space")
            # Creates a new tkinter window
            self.entire_space_window = tk.Toplevel(self.master)
            self.entire_space_window.geometry("600x600")
            self.entire_space_window.title("Entire space")
            # Creates a new frame
            plt_frame = tk.Frame(self.entire_space_window)
            plt_frame.pack(fill=tk.BOTH, expand=1)
            plt_frame.pack_propagate(False)
            fig = App.recon_graph.draw()
            canvas = FigureCanvasTkAgg(fig, plt_frame)
            canvas.draw()
            canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=True)
            # The toolbar allows the user to zoom in/out, drag the graph and save the graph
            toolbar = NavigationToolbar2Tk(canvas, plt_frame)
            toolbar.update()
            canvas.get_tk_widget().pack(side=tk.TOP)

        elif self.view_solution_space_var.get() == "Clusters":
            self.view_solution_space_var.set("View solution space")
            self.set_num_clusters()

    def set_num_clusters(self):
        """Pop up a new tkinter window for setting the number of clusters."""
        # Creates a new tkinter window
        self.set_num_cluster_window = tk.Toplevel(self.master)
        self.set_num_cluster_window.geometry("300x200")
        self.set_num_cluster_window.title("Set the number of clusters")
        # Creates a new frame
        self.set_num_cluster_frame = tk.Frame(self.set_num_cluster_window)
        self.set_num_cluster_frame.pack(fill=tk.BOTH, expand=tk.YES)
        self.set_num_cluster_frame.pack_propagate(False)

        self.enter_num_clusters_btn = tk.Button(self.set_num_cluster_frame, text="Enter", command=self.click_on_enter_num_clusters_btn, state=tk.NORMAL)
        self.enter_num_clusters_btn.grid(row=1, column=0)

        self.num_cluster_label = tk.Label(self.set_num_cluster_frame, text="Number of clusters:")
        self.num_cluster_error = tk.Label(self.set_num_cluster_frame, text="")
        num_cluster_vcmd = (self.register(self.validate_num_cluster_input), '%P')
        # self.num_cluster_input is tk.IntVar(), initialized to be 1
        self.num_cluster_entry_box = CustomEntry(self.set_num_cluster_frame, width=3, textvariable=self.num_cluster_input)
        self.num_cluster_entry_box.set_border_color("green")
        self.num_cluster_entry_box.validate(validate="key", validatecommand=num_cluster_vcmd)
        self.validate_num_cluster_input(1)
        self.num_cluster_label.grid(row=0, column=0, sticky="e")
        self.num_cluster_entry_box.grid(row=0, column=1, sticky="w")
        self.num_cluster_error.grid(row=0, column=2)

    def validate_num_cluster_input(self, input_after_change: str):
        """The number of clusters is only allowed to be an integer that >= 1 and <= the number of MPRs."""
        try:
            val = int(input_after_change)
            if val >= 1 and val <= self.recon_count:
                self.num_cluster = val
                self.num_cluster_entry_box.set_border_color("green")
                self.enter_num_clusters_btn.configure(state=tk.NORMAL)
            else:
                self.num_cluster = None
                self.num_cluster_entry_box.set_border_color("red")
                self.enter_num_clusters_btn.configure(state=tk.DISABLED)
        except ValueError:
            self.num_cluster = None
            self.num_cluster_entry_box.set_border_color("red")
            self.enter_num_clusters_btn.configure(state=tk.DISABLED)

        if self.num_cluster is not None:
            self.num_cluster_entry_box.set_border_color("green")
            self.enter_num_clusters_btn.configure(state=tk.NORMAL)
            self.view_reconciliations_dropdown.configure(state=tk.NORMAL)
            self.view_reconciliations_dropdown['menu'].entryconfigure("One per cluster", state=tk.NORMAL)
        return True # return True means allowing the change to happen

    def click_on_enter_num_clusters_btn(self):
        """Compute cluster histograms and median reconciliations, and open a new tkinter window to show the solution space."""
        self.compute_recon_solutions()
        self.open_window_solution_space()

    def compute_recon_solutions(self):
        """Compute cluster histograms and median reconciliations and store them in variables to draw later."""
        # Compute all clusters from 1 to self.num_cluster
        # and store them in a list called App.clusters_list
        # App.clusters_list[0] contains App.recon_graph.cluster(1) and so on
        # Each App.clusters_list[num] is a list of ReconGraph
        App.clusters_list = []
        for num in range(self.num_cluster):
            App.clusters_list.append(App.recon_graph.cluster(num+1))

        # Compute medians for a specific self.num_cluster
        App.medians = []
        if self.num_cluster == 1:
            App.medians.append(App.recon_graph.median())
        else:
            clusters = App.recon_graph.cluster(self.num_cluster)
            for i in range(len(clusters)):
                App.medians.append(clusters[i].median())

        if self.view_solution_space_window is not None and self.view_solution_space_window.winfo_exists():
            self.view_solution_space_window.destroy()
        if self.view_reconciliations_window is not None and self.view_reconciliations_window.winfo_exists():
            self.view_reconciliations_window.destroy()
        if self.view_pvalue_histogram_window is not None and self.view_pvalue_histogram_window.winfo_exists():
            self.view_pvalue_histogram_window.destroy()

    def select_from_view_reconciliations_dropdown(self, event):
        """When "View reconciliations" dropdown is clicked."""
        if self.view_reconciliations_var.get() == "One MPR":
            self.view_reconciliations_var.set("View reconciliations")
            # Creates a new tkinter window
            self.one_MPR_window = tk.Toplevel(self.master)
            self.one_MPR_window.geometry("600x600")
            self.one_MPR_window.title("One MPR")
            ReconciliationsOneMPRWindow(self.one_MPR_window)

        elif self.view_reconciliations_var.get() == "One per cluster":
            self.view_reconciliations_var.set("View reconciliations")
            self.open_window_reconciliations()

    def open_window_solution_space(self):
        """Pop up a new tkinter window to display the solution space."""
        if self.num_cluster is not None:
            self.view_solution_space_window = tk.Toplevel(self.master)
            self.view_solution_space_window.geometry("900x900")
            self.view_solution_space_window.title("View reconciliation space")
            SolutionSpaceWindow(self.view_solution_space_window)

    def open_window_reconciliations(self):
        """Pop up a new tkinter window to display the reconciliations."""
        if self.num_cluster is not None:
            self.view_reconciliations_window = tk.Toplevel(self.master)
            self.view_reconciliations_window.geometry("900x900")
            self.view_reconciliations_window.title("View reconciliations")
            ReconciliationsOnePerClusterWindow(self.view_reconciliations_window)

    def open_window_pvalue_histogram(self):
        """Pop up a new tkinter window to display the p-value histogram."""
        App.p_value_histogram = App.recon_graph.draw_stats()
        self.view_pvalue_histogram_window = tk.Toplevel(self.master)
        self.view_pvalue_histogram_window.geometry("700x700")
        self.view_pvalue_histogram_window.title("p-value Histogram")
        PValueHistogramWindow(self.view_pvalue_histogram_window)

# View reconciliation space - Clusters
class SolutionSpaceWindow(tk.Frame):
    def __init__(self, master):
        super().__init__(master)
        self.master = master
        self.frame = tk.Frame(self.master)
        self.frame.pack(fill=tk.BOTH, expand=1)
        self.frame.pack_propagate(False)
        self.draw_clusters()

    def draw_clusters(self):
        if len(App.clusters_list) == 1:
            fig = App.recon_graph.draw()
        else:
            fig, axs = plt.subplots(len(App.clusters_list), len(App.clusters_list))
            for i in range(len(App.clusters_list)):
                for j in range(len(App.clusters_list[i])):
                    App.clusters_list[i][j].draw_on(axs[i,j])

        canvas = FigureCanvasTkAgg(fig, self.frame)
        canvas.draw()
        canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=True)
        # The toolbar allows the user to zoom in/out, drag the graph and save the graph
        toolbar = NavigationToolbar2Tk(canvas, self.frame)
        toolbar.update()
        canvas.get_tk_widget().pack(side=tk.TOP)

# View reconciliations - One MPR
class ReconciliationsOneMPRWindow(tk.Frame):
    def __init__(self, master):
        super().__init__(master)
        self.master = master
        self.master.grid_rowconfigure(0, weight=5)
        self.master.grid_rowconfigure(1, weight=1)
        self.master.grid_columnconfigure(0, weight=1)
        self.frame = tk.Frame(self.master)
        self.frame.grid(row=0, column=0, sticky="nsew")
        self.frame.grid_propagate(False)
        self.checkboxes_frame = tk.Frame(self.master)
        self.checkboxes_frame.grid(row=1, column=0)
        self.checkboxes_frame.grid_propagate(False)
        self.create_checkboxes()
        self.draw_one_MPR()

    def draw_one_MPR(self):
        self.fig = App.recon_graph.median().draw(show_internal_labels=self.show_internal_node_names_boolean, show_freq=self.show_event_frequencies_boolean)
        self.canvas = FigureCanvasTkAgg(self.fig, self.frame)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=True)
        # The toolbar allows the user to zoom in/out, drag the graph and save the graph
        toolbar = NavigationToolbar2Tk(self.canvas, self.frame)
        toolbar.update()
        self.canvas.get_tk_widget().pack(side=tk.TOP)

    def create_checkboxes(self):
        self.show_internal_node_names_boolean = tk.BooleanVar()
        self.show_internal_node_names_boolean.set(tk.TRUE)
        show_internal_node_names_checkbutton = tk.Checkbutton(self.checkboxes_frame, text="Display internal node names", variable=self.show_internal_node_names_boolean, command=self.update_one_mpr)
        show_internal_node_names_checkbutton.pack(side=tk.LEFT)

        self.show_event_frequencies_boolean = tk.BooleanVar()
        self.show_event_frequencies_boolean.set(tk.TRUE)
        show_event_frequencies_checkbutton = tk.Checkbutton(self.checkboxes_frame, text="Display frequencies", variable=self.show_event_frequencies_boolean, command=self.update_one_mpr)
        show_event_frequencies_checkbutton.pack(side=tk.LEFT)

    def update_one_mpr(self):
        self.canvas.get_tk_widget().destroy()
        self.fig = App.recon_graph.median().draw(
            show_internal_labels=self.show_internal_node_names_boolean.get(),
            show_freq=self.show_event_frequencies_boolean.get()
        )
        self.canvas = FigureCanvasTkAgg(self.fig, self.frame)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=True)

# View reconciliations - One per cluster
class ReconciliationsOnePerClusterWindow(tk.Frame):
    def __init__(self, master):
        super().__init__(master)
        self.master = master
        self.frame = tk.Frame(self.master)
        self.frame.pack(fill=tk.BOTH, expand=1)
        self.frame.pack_propagate(False)
        self.draw_median_recons()
    def draw_median_recons(self):
        if len(App.medians) == 1:
            fig = App.medians[0].draw()
        else:
            fig, axs = plt.subplots(1, len(App.medians))
            for i in range(len(App.medians)):
                App.medians[i].draw_on(axs[i])
        canvas = FigureCanvasTkAgg(fig, self.frame)
        canvas.draw()
        canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=True)
        # The toolbar allows the user to zoom in/out, drag the graph and save the graph
        toolbar = NavigationToolbar2Tk(canvas, self.frame)
        toolbar.update()
        canvas.get_tk_widget().pack(side=tk.TOP)

# p-value Histogram
class PValueHistogramWindow(tk.Frame):
    def __init__(self, master):
        super().__init__(master)
        self.master = master
        self.frame = tk.Frame(self.master)
        self.frame.pack(fill=tk.BOTH, expand=1)
        self.frame.pack_propagate(False)
        self.draw_p_value_histogram()
    def draw_p_value_histogram(self):
        canvas = FigureCanvasTkAgg(App.p_value_histogram, self.frame)
        canvas.draw()
        canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=True)
        # The toolbar allows the user to zoom in/out, drag the graph and save the graph
        toolbar = NavigationToolbar2Tk(canvas, self.frame)
        toolbar.update()
        canvas.get_tk_widget().pack(side=tk.TOP)

class CustomEntry(tk.Frame):
    def __init__(self, parent, *args, **kwargs):
        tk.Frame.__init__(self, parent)
        self.entry = tk.Entry(self, *args, **kwargs)
        self.entry.pack(fill="both", expand=tk.TRUE, padx=1, pady=1)

        self.get = self.entry.get
        self.insert = self.entry.insert

    def set_border_color(self, color):
        self.configure(background=color)
    def validate(self, validate, validatecommand):
        self.entry.configure(validate=validate, validatecommand=validatecommand)

def on_closing():
    """Kills the matplotlib program and all other tkinter programs when the self.master window is closed."""
    plt.close("all")
    root.destroy()

root = tk.Tk()
root.geometry("700x600")
root.title("eMPRess GUI Version 1")
App(root)
root.protocol("WM_DELETE_WINDOW", on_closing)
root.mainloop()
root.quit()
