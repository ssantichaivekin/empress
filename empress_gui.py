# empress_gui.py

import tkinter as tk
from tkinter import messagebox
from pathlib import Path
import os
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from matplotlib.backend_bases import MouseEvent, key_press_handler
import empress
import ReconInput
from empress.topo_sort.tree_format_converter import dict_to_tree
from empress.topo_sort import Tree

class App(tk.Frame):

    def __init__(self, master):
        tk.Frame.__init__(self, master)
        self.master = master
        # Configure the master frame 
        master.grid_rowconfigure(0, weight=1)
        master.grid_rowconfigure(1, weight=2)
        master.grid_columnconfigure(0, weight=1)
        master.grid_columnconfigure(1, weight=1)

        # Create a logo frame on top of the master frame 
        self.logo_frame = tk.Frame(master)
        # sticky="nsew" means that self.logo_frame expands in all four directions (north, south, east and west) 
        # to fully occupy the allocated space in the grid system (row 0 column 0&1)
        self.logo_frame.grid(row=0, column=0, columnspan=2, sticky="nsew")
        self.logo_frame.grid_propagate(False)

        # Add logo image
        photo = tk.PhotoImage(file="./assets/jane_logo_thin.gif")
        label = tk.Label(self.logo_frame, image=photo)
        label.place(x=0, y=0)
        label.image = photo

        # Create an input frame on the left side of the master frame 
        self.input_frame = tk.Frame(master)
        self.input_frame.grid(row=1, column=0, sticky="nsew")
        self.input_frame.grid_rowconfigure(0, weight=3)
        self.input_frame.grid_rowconfigure(1, weight=3)
        self.input_frame.grid_rowconfigure(2, weight=5)
        self.input_frame.grid_columnconfigure(0, weight=1)
        self.input_frame.grid_propagate(False)

        # Create an output frame on the right side of the master frame
        self.output_frame = tk.Frame(master)
        self.output_frame.grid(row=1, column=1, sticky="nsew")
        self.output_frame.grid_rowconfigure(0, weight=2)
        self.output_frame.grid_rowconfigure(1, weight=3)
        self.output_frame.grid_rowconfigure(2, weight=3)
        self.output_frame.grid_columnconfigure(0, weight=1)
        self.output_frame.grid_propagate(False)

        # "Load Files" button 
        # Load in three input files (two .nwk and one .mapping)
        # and display the number of leaves in each tree and the entry boxes for setting DTL costs (next step)
        self.file_to_load = tk.StringVar(self.input_frame) 
        self.file_to_load.set("Load Files")
        self.options = ["Load host tree file", "Load parasite tree file", "Load mapping file"]
        self.load_file_list = tk.OptionMenu(self.input_frame, self.file_to_load, *self.options, command=self.load_input_files)
        self.load_file_list.grid(row=0, column=0)
        # Force a sequence of loading host tree file first, and then parasite tree file, and then mapping file
        self.load_file_list['menu'].entryconfigure("Load parasite tree file", state = "disabled")
        self.load_file_list['menu'].entryconfigure("Load mapping file", state = "disabled")

        # "View Event Cost Regions" button 
        # Pop up a matplotlib graph for the cost regions
        self.view_cost_btn = tk.Button(self.input_frame, text="View Event Cost Regions", command=self.plot_cost_regions, state=tk.DISABLED)
        self.view_cost_btn.grid(row=1, column=0)

        # Create a frame for "Compute Reconciliations" button and its checkbuttons in self.input_frame
        self.compute_recon_frame = tk.Frame(self.input_frame)
        self.compute_recon_frame.grid(row=2, column=0, sticky="nsew")
        self.compute_recon_frame.grid_rowconfigure(0, weight=1)
        self.compute_recon_frame.grid_rowconfigure(1, weight=4)
        self.compute_recon_frame.grid_columnconfigure(0, weight=1)
        self.compute_recon_frame.grid_propagate(False)
        # "Compute Reconciliations" button 
        # Display reconciliation results(numbers) and three options(checkboxes) for viewing graphical analysis
        self.compute_recon_button = tk.Button(self.compute_recon_frame, text="Compute Reconciliations", command=self.recon_analysis, state=tk.DISABLED)
        self.compute_recon_button.grid(row=0, column=0)

        # Creates a frame for the "Compute Reconciliations" button's checkbuttons in self.compute_recon_frame
        self.recon_checkbox_frame = tk.Frame(self.compute_recon_frame)
        self.recon_checkbox_frame.grid(row=1, column=0, sticky="nsew")
        self.recon_checkbox_frame.grid_rowconfigure(0, weight=3)
        self.recon_checkbox_frame.grid_rowconfigure(1, weight=1)
        self.recon_checkbox_frame.grid_rowconfigure(2, weight=1)
        self.recon_checkbox_frame.grid_columnconfigure(0, weight=1)
        self.recon_checkbox_frame.grid_propagate(False)

        # Creates a frame for setting the number of clusters in self.recon_checkbox_frame
        self.num_cluster_frame = tk.Frame(self.recon_checkbox_frame)
        self.num_cluster_frame.grid(row=0, column=0, sticky="nsew")
        self.num_cluster_frame.grid_rowconfigure(0, weight=1)
        self.num_cluster_frame.grid_columnconfigure(0, weight=1)
        self.num_cluster_frame.grid_columnconfigure(1, weight=1)
        self.num_cluster_frame.grid_columnconfigure(2, weight=1)
        self.num_cluster_frame.grid_propagate(False)

        # Create an input information frame in self.output_frame
        # to display the numbers of tips for host and parasite trees
        self.input_info_frame = tk.Frame(self.output_frame)
        self.input_info_frame.grid(row=0, column=0, sticky="nsew")
        self.input_info_frame.grid_rowconfigure(0, weight=1)
        self.input_info_frame.grid_rowconfigure(1, weight=1)
        self.input_info_frame.grid_rowconfigure(2, weight=1)
        self.input_info_frame.grid_columnconfigure(0, weight=1)
        self.input_info_frame.grid_propagate(False)

        # Creates a frame for setting DTL costs in self.output_frame
        self.costs_frame = tk.Frame(self.output_frame)
        self.costs_frame.grid(row=1, column=0, sticky="nsew")
        self.costs_frame.grid_columnconfigure(0, weight=1)
        self.costs_frame.grid_columnconfigure(1, weight=1)
        self.costs_frame.grid_columnconfigure(2, weight=10)
        self.costs_frame.grid_rowconfigure(0, weight=1)
        self.costs_frame.grid_rowconfigure(1, weight=1)
        self.costs_frame.grid_rowconfigure(2, weight=1)
        self.costs_frame.grid_propagate(False) 

        # Creates a frame for showing reconciliation results as numbers in self.output_frame
        self.recon_nums_frame = tk.Frame(self.output_frame)
        self.recon_nums_frame.grid(row=2, column=0, sticky="nsew")
        self.recon_nums_frame.grid_rowconfigure(0, weight=1)
        self.recon_nums_frame.grid_rowconfigure(1, weight=1)
        self.recon_nums_frame.grid_rowconfigure(2, weight=1)
        self.recon_nums_frame.grid_rowconfigure(3, weight=1)
        self.recon_nums_frame.grid_rowconfigure(4, weight=1)
        self.recon_nums_frame.grid_columnconfigure(0, weight=1)
        self.recon_nums_frame.grid_propagate(False)

        # To overwrite everything when user loads in new input files 
        # (always starting from the host tree file)
        self.host_tree_info = tk.Label(self.input_info_frame)
        self.parasite_tree_info = tk.Label(self.input_info_frame)
        self.mapping_info = tk.Label(self.input_info_frame)

        self.dup_label = tk.Label(self.costs_frame)
        self.dup_error = tk.Label(self.costs_frame)
        self.dup_entry_box = tk.Entry(self.costs_frame)
        self.trans_label = tk.Label(self.costs_frame)
        self.trans_error = tk.Label(self.costs_frame)
        self.trans_entry_box = tk.Entry(self.costs_frame)
        self.loss_label = tk.Label(self.costs_frame)
        self.loss_error = tk.Label(self.costs_frame)
        self.loss_entry_box = tk.Entry(self.costs_frame)
        self.dup_input = tk.DoubleVar()
        self.trans_input = tk.DoubleVar()
        self.loss_input = tk.DoubleVar()

        self.recon_MPRs_label = tk.Label(self.recon_nums_frame)
        self.recon_cospeci_label = tk.Label(self.recon_nums_frame)
        self.recon_dup_label = tk.Label(self.recon_nums_frame)
        self.recon_trans_label = tk.Label(self.recon_nums_frame)
        self.recon_loss_label = tk.Label(self.recon_nums_frame)

        self.num_cluster_label = tk.Label(self.num_cluster_frame)
        self.num_cluster_error = tk.Label(self.num_cluster_frame)
        self.num_cluster_entry_box = tk.Entry(self.num_cluster_frame)
        self.num_cluster_input = tk.IntVar()
        self.recon_space_btn = tk.Checkbutton(self.recon_checkbox_frame)
        self.recon_space_btn_var = tk.BooleanVar()
        self.recons_btn = tk.Checkbutton(self.recon_checkbox_frame)
        self.recons_btn_var = tk.BooleanVar()

        self.recon_input = ReconInput.ReconInput()
        App.recon_graph = None
        App.clusters_list = []
        App.median_reconciliation = None

    def reset_everything(self):
        """Reset everything when user loads in new input files (always starting from the host tree file)."""
        self.load_file_list['menu'].entryconfigure("Load parasite tree file", state = "normal")
        self.load_file_list['menu'].entryconfigure("Load host tree file", state = "disabled")

        # Reset self.recon_input so self.view_cost_btn can be disabled
        self.recon_input = ReconInput.ReconInput()
        self.view_cost_btn.configure(state=tk.DISABLED)

        # Reset dtl costs so self.compute_recon_button can be disabled
        self.dup_cost = None
        self.trans_cost = None
        self.loss_cost = None
        self.compute_recon_button.configure(state=tk.DISABLED)
        
        self.num_cluster_label.destroy()
        self.num_cluster_error.destroy()
        self.num_cluster_entry_box.destroy()
        self.num_cluster_input.set(1)
        self.recon_space_btn.destroy()
        self.recon_space_btn_var.set(tk.FALSE)
        self.recons_btn.destroy()
        self.recons_btn_var.set(tk.FALSE)
        
        self.host_tree_info.destroy() 
        self.parasite_tree_info.destroy()
        self.mapping_info.destroy()

        self.dup_label.destroy()
        self.dup_error.destroy()
        self.dup_entry_box.destroy()
        self.trans_label.destroy()
        self.trans_error.destroy()
        self.trans_entry_box.destroy()
        self.loss_label.destroy()
        self.loss_error.destroy()
        self.loss_entry_box.destroy()

        self.recon_MPRs_label.destroy()
        self.recon_cospeci_label.destroy()
        self.recon_dup_label.destroy()
        self.recon_trans_label.destroy()
        self.recon_loss_label.destroy()

        App.recon_graph = None 
        App.clusters_list = []
        App.median_reconciliation = None

    def load_input_files(self, event):
        """
        Load in two .nwk files for the host tree and parasite tree, and one .mapping file. Display the number of tips for 
        the trees and a message to indicate the successful reading of the tips mapping.
        """ 
        # Clicking on "Load host tree file" 
        if self.file_to_load.get() == "Load host tree file":
            # Allows loading a .newick file
            self.host_file_path = None
            # initialdir is set to be the current working directory
            input_file = tk.filedialog.askopenfilename(initialdir=os.getcwd(), title="Select a host file")
            if Path(input_file).suffix == '.nwk':
                # Read in host tree file
                self.recon_input.read_host(input_file)
                if self.recon_input.host_tree is not None:
                    # Reset everything every time user successfully loads in a new host tree file
                    self.reset_everything()
                    # Read in host tree file
                    self.recon_input.read_host(input_file)
                    self.host_file_path = input_file
                    host_tree_tips_number = self.compute_tree_tips("host tree")
                    self.host_tree_info = tk.Label(self.input_info_frame, text="Host: " + str(host_tree_tips_number) + " tips")
                    self.host_tree_info.grid(row=0, column=0, sticky="w")
                else: 
                    messagebox.showinfo("Warning", "The input file cannot be read.")          
            else:
                messagebox.showinfo("Warning", "Please load a '.nwk' file.")

        # Clicking on "Load parasite tree file" 
        elif self.file_to_load.get() == "Load parasite tree file":
            # Allows loading a .newick file
            self.parasite_file_path = None
            # initialdir is set to be the current working directory
            input_file = tk.filedialog.askopenfilename(initialdir=os.getcwd(), title="Select a parasite file")
            if Path(input_file).suffix == '.nwk': 
                self.recon_input.read_parasite(input_file)
                if self.recon_input.parasite_tree is not None:
                    self.parasite_file_path = input_file
                    parasite_tree_tips_number = self.compute_tree_tips("parasite tree")
                    self.parasite_tree_info = tk.Label(self.input_info_frame, text="Parasite/symbiont: " + str(parasite_tree_tips_number) + " tips")
                    self.parasite_tree_info.grid(row=1, column=0, sticky="w")
                    self.load_file_list['menu'].entryconfigure("Load mapping file", state = "normal")
                    self.load_file_list['menu'].entryconfigure("Load parasite tree file", state = "disabled")
                else: 
                    messagebox.showinfo("Warning", "The input file cannot be read.")          
            else:
                messagebox.showinfo("Warning", "Please load a '.nwk' file.")

        # Clicking on "Load mapping" 
        elif self.file_to_load.get() == "Load mapping file":
            # Allows loading a .newick file
            self.mapping_file_path = None
            # initialdir is set to be the current working directory
            input_file = tk.filedialog.askopenfilename(initialdir=os.getcwd(), title="Select a mapping file")
            if Path(input_file).suffix == '.mapping': 
                self.recon_input.read_mapping(input_file)
                if self.recon_input.phi is not None:
                    self.mapping_file_path = input_file
                    self.mapping_info = tk.Label(self.input_info_frame, text="Tip mapping has been read successfully.")
                    self.mapping_info.grid(row=2, column=0, sticky="w")
                    self.load_file_list['menu'].entryconfigure("Load host tree file", state = "normal")
                    self.load_file_list['menu'].entryconfigure("Load mapping file", state = "disabled")

                    # Enables the next step, setting DTL costs
                    if self.recon_input.complete(): 
                        self.view_cost_btn.configure(state=tk.NORMAL)
                        self.dtl_cost()
                        # Compute App.recon_graph
                        App.recon_graph = empress.reconcile(self.recon_input, 1, 1, 1)
                else: 
                    messagebox.showinfo("Warning", "The input file cannot be read.")          
            else:
                messagebox.showinfo("Warning", "Please load a '.mapping' file.")

    def compute_tree_tips(self, tree_type):
        """Compute the number of tips for the input host tree and parasite tree."""
        if tree_type == "host tree":
            host_tree_object = dict_to_tree(self.recon_input.host_tree, Tree.TreeType.HOST)
            return len(host_tree_object.leaf_list())
        elif tree_type == "parasite tree":
            parasite_tree_object = dict_to_tree(self.recon_input.parasite_tree, Tree.TreeType.PARASITE)
            return len(parasite_tree_object.leaf_list())

    def dtl_cost(self):
        """Set DTL costs by clicking on the matplotlib graph or by entering manually."""  
        self.dup_label = tk.Label(self.costs_frame, text="Duplication:")
        self.dup_error = tk.Label(self.costs_frame, text="")
        # %P = value of the entry if the edit is allowed
        # see https://stackoverflow.com/questions/4140437/interactively-validating-entry-widget-content-in-tkinter
        dup_vcmd = (self.register(self.validate_dup_input), '%P')
        # self.dup_input is tk.DoubleVar()
        self.dup_entry_box = tk.Entry(self.costs_frame, width=3, validate="all", textvariable=self.dup_input, validatecommand=dup_vcmd)
        
        self.dup_label.grid(row=0, column=0, sticky="w")
        self.dup_entry_box.grid(row=0, column=1, sticky="w")
        self.dup_error.grid(row=0, column=2, sticky="w")

        self.trans_label = tk.Label(self.costs_frame, text="Transfer:")
        self.trans_error = tk.Label(self.costs_frame, text="")
        # %P = value of the entry if the edit is allowed
        # see https://stackoverflow.com/questions/4140437/interactively-validating-entry-widget-content-in-tkinter
        trans_vcmd = (self.register(self.validate_trans_input), '%P')
        # self.trans_input is tk.DoubleVar()
        self.trans_entry_box = tk.Entry(self.costs_frame, width=3, textvariable=self.trans_input, validate="all", validatecommand=trans_vcmd)
        self.trans_label.grid(row=1, column=0, sticky="w")
        self.trans_entry_box.grid(row=1, column=1, sticky="w")
        self.trans_error.grid(row=1, column=2, sticky="w")

        self.loss_label = tk.Label(self.costs_frame, text="Loss:")
        self.loss_label.grid(row=2, column=0, sticky="w")
        self.loss_error = tk.Label(self.costs_frame, text="")
        # %P = value of the entry if the edit is allowed
        # see https://stackoverflow.com/questions/4140437/interactively-validating-entry-widget-content-in-tkinter
        loss_vcmd = (self.register(self.validate_loss_input), '%P')
        # self.loss_input is tk.DoubleVar()
        self.loss_entry_box = tk.Entry(self.costs_frame, width=3, validate="all", textvariable=self.loss_input, validatecommand=loss_vcmd)
        self.loss_label.grid(row=2, column=0, sticky="w")
        self.loss_entry_box.grid(row=2, column=1, sticky="w")
        self.loss_error.grid(row=2, column=2, sticky="w")
    
    def validate_dup_input(self, input_after_change: str):
        try:
            val = float(input_after_change)
            if val >= 0:
                self.dup_cost = val
            else:
                self.dup_cost = None   
                self.dup_error.config(text="should be non-negative", fg="red")    
        except ValueError:
            self.dup_cost = None
            self.dup_error.config(text="should be a number", fg="red")
        
        if self.dup_cost is not None:
            self.dup_error.config(text="valid", fg="green")
        self.update_recon_btn()
        return True # return True means allowing the change to happen

    def validate_trans_input(self, input_after_change: str):
        try:
            val = float(input_after_change)
            if val >= 0:
                self.trans_cost = val
            else:
                self.trans_cost = None   
                self.trans_error.config(text="should be non-negative", fg="red")    
        except ValueError:
            self.trans_cost = None
            self.trans_error.config(text="should be a number", fg="red")
        
        if self.trans_cost is not None:
            self.trans_error.config(text="valid", fg="green")
        self.update_recon_btn()
        return True # return True means allowing the change to happen
    
    def validate_loss_input(self, input_after_change: str):
        try:
            val = float(input_after_change)
            if val >= 0:
                self.loss_cost = val
            else:
                self.loss_cost = None   
                self.loss_error.config(text="should be non-negative", fg="red")    
        except ValueError:
            self.loss_cost = None
            self.loss_error.config(text="should be a number", fg="red")
        
        if self.loss_cost is not None:
            self.loss_error.config(text="valid", fg="green")
        self.update_recon_btn()
        return True # return True means allowing the change to happen

    def plot_cost_regions(self):
        """Plot the cost regions using matplotlib and embed the graph in a tkinter window."""    
        # Creates a new tkinter window 
        plt_window = tk.Toplevel(self.master)
        plt_window.geometry("550x550")
        plt_window.title("Matplotlib Graph - Cost regions")
        # Creates a new frame
        plt_frame = tk.Frame(plt_window)
        plt_frame.pack(fill=tk.BOTH, expand=1)
        plt_frame.pack_propagate(False)
        cost_regions = empress.compute_cost_regions(self.recon_input, 0.5, 10, 0.5, 10)  
        #cost_regions.draw_to_file('./examples/cost_poly.png')  # draw and save to a file
        fig = cost_regions.draw()  # draw to figure (creates matplotlib figure)
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
            self.dup_input.set("1.00")
            self.trans_input.set(round(event.ydata, 2))
            self.loss_input.set(round(event.xdata, 2))
            # Enables the next step, viewing reconciliation result
            self.dup_cost = 1.00
            self.trans_cost = event.ydata
            self.loss_cost = event.xdata
            self.update_recon_btn()
        else:
            messagebox.showinfo("Warning", "Please click inside the axes bounds.")

    def update_recon_btn(self):
        if self.dup_cost is not None and self.trans_cost is not None and self.loss_cost is not None:
            self.compute_recon_button.configure(state=tk.NORMAL)
        else:
            self.compute_recon_button.configure(state=tk.DISABLED)

    def recon_analysis(self):
        """Display reconciliation results in numbers and further viewing options for graphical analysis."""
        self.num_cluster_label = tk.Label(self.num_cluster_frame, text="Number of clusters:")
        self.num_cluster_error = tk.Label(self.num_cluster_frame, text="")
        num_cluster_vcmd = (self.register(self.validate_num_cluster_input), '%P')
        # self.num_cluster_input is tk.IntVar(), initialized to be 1
        self.num_cluster_entry_box = tk.Entry(self.num_cluster_frame, width=2, textvariable=self.num_cluster_input, validate="all", validatecommand=num_cluster_vcmd)
        self.num_cluster_label.grid(row=0, column=0, sticky="e")
        self.num_cluster_entry_box.grid(row=0, column=1)
        self.num_cluster_error.grid(row=0, column=2, sticky="w")

        # self.recon_space_btn_var is tk.BooleanVar(), initialized to be FALSE
        self.recon_space_btn = tk.Checkbutton(self.recon_checkbox_frame, text="View solution space", 
            padx=10, variable=self.recon_space_btn_var, 
            command=self.open_and_close_window_recon_space)
        self.recon_space_btn.grid(row=1, column=0)

        # self.recons_btn_var is tk.BooleanVar(), initialized to be FALSE
        self.recons_btn = tk.Checkbutton(self.recon_checkbox_frame, text="View reconciliations", 
            padx=10, variable=self.recons_btn_var, 
            command=self.open_and_close_window_recons)
        self.recons_btn.grid(row=2, column=0)

        # Shows reconciliation results as numbers
        num_MPRs = App.recon_graph.n_recon
        self.recon_MPRs_label = tk.Label(self.recon_nums_frame, text="Number of MPRs: " + str(num_MPRs))
        self.recon_cospeci_label = tk.Label(self.recon_nums_frame, text="# Cospeciations:")
        self.recon_dup_label = tk.Label(self.recon_nums_frame, text="# Duplications:")
        self.recon_trans_label = tk.Label(self.recon_nums_frame, text="# Transfers:")
        self.recon_loss_label = tk.Label(self.recon_nums_frame, text="# Losses:")
        self.recon_MPRs_label.grid(row=0, column=0, sticky="w")
        self.recon_cospeci_label.grid(row=1, column=0, sticky="w")
        self.recon_dup_label.grid(row=2, column=0, sticky="w")
        self.recon_trans_label.grid(row=3, column=0, sticky="w")
        self.recon_loss_label.grid(row=4, column=0, sticky="w")

    def validate_num_cluster_input(self, input_after_change: str):
        try:
            val = int(input_after_change)
            if val >= 1:
                self.num_cluster = val
            else:
                self.num_cluster = None   
                self.num_cluster_error.config(text=">= 1", fg="red")    
        except ValueError:
            self.num_cluster = None
            self.num_cluster_error.config(text="number", fg="red")
        
        if self.num_cluster is not None:
            self.num_cluster_error.config(text="valid", fg="green")
            self.compute_recon_solutions()
        return True # return True means allowing the change to happen

    def compute_recon_solutions(self):
        """Compute cluster histograms and median reconciliations and store them in variables for drawing later."""
        # Compute all clusters from 1 to self.num_cluster
        # and store them in a list called App.clusters_list
        # App.clusters_list[0] contains App.recon_graph.cluster(1) and so on
        # Each App.clusters_list[num] is a list of ReconGraph
        App.clusters_list = []
        for num in range(self.num_cluster):
            App.clusters_list.append(App.recon_graph.cluster(num+1))
        
        # Find median
        App.median_reconciliation = App.recon_graph.median()

    def open_and_close_window_recon_space(self):
        """
        Open a new window titled "View reconciliation space" when the checkbox is checked,
        and close the window when the checkbox is unchecked.
        """
        if self.recon_space_btn_var.get() == True:
            self.recon_space_window = tk.Toplevel(self.master)
            self.recon_space_window.geometry("900x900")
            self.recon_space_window.title("View reconciliation space")
            ReconSpaceWindow(self.recon_space_window)
        if self.recon_space_btn_var.get() == False:
            if self.recon_space_window.winfo_exists() == 1:
                self.recon_space_window.destroy()

    def open_and_close_window_recons(self):
        """
        Open a new window titled "View reconciliations" when the checkbox is checked,
        and close the window when the checkbox is unchecked.
        """
        if self.recons_btn_var.get() == True:
            self.recons_window = tk.Toplevel(self.master)
            self.recons_window.geometry("500x500")
            self.recons_window.title("View reconciliations")
            ReconsWindow(self.recons_window)
        if self.recons_btn_var.get() == False:
            if self.recons_window.winfo_exists() == 1:
                self.recons_window.destroy()

# View reconciliation space 
class ReconSpaceWindow(tk.Frame):
    def __init__(self, master):
        super().__init__(master)
        self.master = master        
        self.frame = tk.Frame(master)
        self.frame.pack(fill=tk.BOTH, expand=1)
        self.frame.pack_propagate(False)
        self.draw_clusters()
    
    def draw_clusters(self):
        """
        """
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

# View reconciliations 
class ReconsWindow(tk.Frame):
    def __init__(self, master):
        super().__init__(master)
        self.master = master        
        self.frame = tk.Frame(master)
        self.frame.pack(fill=tk.BOTH, expand=1)
        self.frame.pack_propagate(False)
        self.draw_median_recons()
    
    def draw_median_recons(self):
        """
        """
        fig = App.median_reconciliation.draw()
        canvas = FigureCanvasTkAgg(fig, self.frame)
        canvas.draw()
        canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=True)
        # The toolbar allows the user to zoom in/out, drag the graph and save the graph
        toolbar = NavigationToolbar2Tk(canvas, self.frame)
        toolbar.update()
        canvas.get_tk_widget().pack(side=tk.TOP)

def on_closing():
    """Kills the matplotlib program and all other tkinter programs when the master window is closed."""
    plt.close("all")
    root.destroy()

root = tk.Tk()
root.geometry("600x600")
root.title("eMPRess GUI Version 1")
App(root)
root.protocol("WM_DELETE_WINDOW", on_closing)
root.mainloop()
root.quit()
