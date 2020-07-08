# empress_gui.py

import tkinter as tk
from tkinter import messagebox
from pathlib import Path
import os
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk

import empress
from empress import input_reader
from empress.recon_vis.utils import dict_to_tree
from empress.recon_vis import tree

class App(tk.Frame):

    def __init__(self, master):
        tk.Frame.__init__(self, master)
        self.master = master
        # Configure the self.master frame
        self.master.grid_rowconfigure(0, weight=2)
        self.master.grid_rowconfigure(1, weight=1)
        self.master.grid_rowconfigure(2, weight=1)
        self.master.grid_rowconfigure(3, weight=1)
        self.master.grid_rowconfigure(4, weight=1)
        self.master.grid_columnconfigure(0, weight=1)
        self.master.grid_columnconfigure(1, weight=1)
        # To display the dividing lines among different frames by adding paddings
        self.master.configure(background="grey")

        # Create a logo frame on top of the self.master frame
        self.logo_frame = tk.Frame(self.master)
        # sticky="nsew" means that self.logo_frame expands in all four directions (north, south, east and west)
        # to fully occupy the allocated space in the grid system (row 0 column 0-1)
        self.logo_frame.grid(row=0, column=0, columnspan=2, sticky="nsew")
        self.logo_frame.grid_propagate(False)

        # Add logo image in self.logo_frame
        photo = tk.PhotoImage(file="./assets/jane_logo_thin.gif")
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

        # "Load files" dropdown
        # Load in three input files (two .nwk and one .mapping)
        # and display the number of leaves in each tree and the entry boxes for setting DTL costs
        self.load_files_var = tk.StringVar(self.input_frame)
        self.load_files_var.set("Load files")
        self.load_files_options = ["Load host tree file", "Load parasite tree file", "Load mapping file"]
        self.load_files_dropdown = tk.OptionMenu(self.input_frame, self.load_files_var, *self.load_files_options,
                                                 command=self.load_input_files)
        self.load_files_dropdown.configure(width=15)
        self.load_files_dropdown.grid(row=0, column=0)
        # Force a sequence of loading host tree file first, and then parasite tree file, and then mapping file
        self.load_files_dropdown['menu'].entryconfigure("Load parasite tree file", state="disabled")
        self.load_files_dropdown['menu'].entryconfigure("Load mapping file", state="disabled")

        # recon_input variables
        self.recon_info_displayed = False
        self.recon_input = input_reader._ReconInput()
        App.recon_graph = None
        App.clusters_list = []
        App.medians = None

        # Create an input information frame
        # to display the numbers of tips for host and parasite trees
        self.input_info_frame = tk.Frame(self.master)
        self.input_info_frame.grid(row=1, column=1, sticky="nsew", pady=(1, 1))
        self.input_info_frame.grid_rowconfigure(0, weight=1)
        self.input_info_frame.grid_rowconfigure(1, weight=1)
        self.input_info_frame.grid_rowconfigure(2, weight=1)
        self.input_info_frame.grid_columnconfigure(0, weight=1)
        self.input_info_frame.grid_propagate(False)

        # To overwrite everything when user loads in new input files
        # (always starting from the host tree file)
        self.host_tree_info = tk.Label(self.input_info_frame)
        self.parasite_tree_info = tk.Label(self.input_info_frame)
        self.mapping_info = tk.Label(self.input_info_frame)

    def refresh_when_new_input_files_loaded(self, event):
        """Reset when user loads in a new input file (can be either of the three options)."""
        App.recon_graph = None
        App.clusters_list = []
        App.medians = None
        # Reset self.recon_input so self.view_cost_space_btn can be disabled
        self.recon_input = input_reader._ReconInput()

        if event == "Load host tree file":
            self.load_files_dropdown['menu'].entryconfigure("Load parasite tree file", state="normal")
            # Read in host tree file after reseting everything
            self.recon_input.read_host(self.host_file_path)
            self.host_tree_info.destroy()
            self.parasite_tree_info.destroy()
            self.mapping_info.destroy()

        elif event == "Load parasite tree file":
            self.load_files_dropdown['menu'].entryconfigure("Load mapping file", state="normal")
            # Read in host and parasite tree files after reseting everything
            self.recon_input.read_host(self.host_file_path)
            self.recon_input.read_parasite(self.parasite_file_path)
            self.parasite_tree_info.destroy()
            self.mapping_info.destroy()

        elif event == "Load mapping file":
            # Read in host and parasite trees and mapping files after reseting everything
            self.recon_input.read_host(self.host_file_path)
            self.recon_input.read_parasite(self.parasite_file_path)
            self.recon_input.read_mapping(self.mapping_file_path)
            self.mapping_info.destroy()

    def load_input_files(self, event):
        """Load in two .nwk files for the host tree and parasite tree, and one .mapping file. Display the number of tips for
        the trees and a message to indicate the successful reading of the tips mapping."""
        # Clicking on "Load host tree file"
        if self.load_files_var.get() == "Load host tree file":
            self.load_files_var.set("Load files")
            # initialdir is set to be the current working directory
            input_file = tk.filedialog.askopenfilename(initialdir=os.getcwd(), title="Select a host file")
            if input_file != "":
                try:
                    self.recon_input.read_host(input_file)
                except Exception as e:
                    messagebox.showinfo("Warning", "Error: " + str(e))
                self.host_file_path = input_file
                # Force a sequence of loading host tree file first, and then parasite tree file, and then mapping file
                self.load_files_dropdown['menu'].entryconfigure("Load parasite tree file", state="disabled")
                self.load_files_dropdown['menu'].entryconfigure("Load mapping file", state="disabled")
                self.refresh_when_new_input_files_loaded("Load host tree file")
                self.update_input_files_info("host")

                # Clicking on "Load parasite tree file"
        elif self.load_files_var.get() == "Load parasite tree file":
            self.load_files_var.set("Load files")
            # initialdir is set to be the current working directory
            input_file = tk.filedialog.askopenfilename(initialdir=os.getcwd(), title="Select a parasite file")
            if input_file != "":
                try:
                    self.recon_input.read_parasite(input_file)
                except Exception as e:
                    messagebox.showinfo("Warning", "Error: " + str(e))
                self.parasite_file_path = input_file
                self.refresh_when_new_input_files_loaded("Load parasite tree file")
                self.update_input_files_info("parasite")

        # Clicking on "Load mapping file"
        elif self.load_files_var.get() == "Load mapping file":
            self.load_files_var.set("Load files")
            # initialdir is set to be the current working directory
            input_file = tk.filedialog.askopenfilename(initialdir=os.getcwd(), title="Select a mapping file")
            if input_file != "":
                try:
                    self.recon_input.read_mapping(input_file)
                except Exception as e:
                    messagebox.showinfo("Warning", "Error: " + str(e))
                self.mapping_file_path = input_file
                self.refresh_when_new_input_files_loaded("Load mapping file")
                self.update_input_files_info("mapping")

    def compute_tree_tips(self, tree_type):
        """Compute the number of tips for the host tree and parasite tree inputs."""
        if tree_type == "host tree":
            host_tree_object = dict_to_tree(self.recon_input.host_dict, tree.TreeType.HOST)
            return len(host_tree_object.leaf_list())
        elif tree_type == "parasite tree":
            parasite_tree_object = dict_to_tree(self.recon_input.parasite_dict, tree.TreeType.PARASITE)
            return len(parasite_tree_object.leaf_list())

    def update_input_files_info(self, fileType):
        if fileType == "host":
            host_tree_tips_number = self.compute_tree_tips("host tree")
            self.host_tree_info = tk.Label(self.input_info_frame,
                                           text="Host: " + os.path.basename(self.host_file_path) + ": " + str(
                                               host_tree_tips_number) + " tips")
            self.host_tree_info.grid(row=0, column=0, sticky="w")
        elif fileType == "parasite":
            parasite_tree_tips_number = self.compute_tree_tips("parasite tree")
            self.parasite_tree_info = tk.Label(self.input_info_frame, text="Parasite/symbiont: " + os.path.basename(
                self.parasite_file_path) + ": " + str(parasite_tree_tips_number) + " tips")
            self.parasite_tree_info.grid(row=1, column=0, sticky="w")
        elif fileType == "mapping":
            self.mapping_info = tk.Label(self.input_info_frame,
                                         text="Mapping: " + os.path.basename(self.mapping_file_path))
            self.mapping_info.grid(row=2, column=0, sticky="w")

    def dtl_cost(self):
        """Sets DTL costs by clicking on the matplotlib graph or by entering manually."""
        # Creates a frame for setting DTL costs
        costs_frame = tk.Frame(self.output_frame)
        costs_frame.grid(row=1, column=0, sticky="nsew")
        costs_frame.grid_columnconfigure(0, weight=1)
        costs_frame.grid_columnconfigure(1, weight=3)
        costs_frame.grid_rowconfigure(0, weight=1)
        costs_frame.grid_rowconfigure(1, weight=1)
        costs_frame.grid_rowconfigure(2, weight=1)
        costs_frame.grid_propagate(False)

        self.dup_cost = None
        self.trans_cost = None
        self.loss_cost = None

        dup_label = tk.Label(costs_frame, text="Duplication:")
        self.dup_error = tk.Label(costs_frame, text="")
        # %P = value of the entry if the edit is allowed
        # see https://stackoverflow.com/questions/4140437/interactively-validating-entry-widget-content-in-tkinter
        dup_vcmd = (self.register(self.validate_dup_input), '%P')
        self.dup_input = tk.DoubleVar()
        self.dup_entry_box = tk.Entry(costs_frame, width=3, validate="all", textvariable=self.dup_input, validatecommand=dup_vcmd)
        
        dup_label.grid(row=0, column=0, sticky="w")
        self.dup_entry_box.grid(row=0, column=1, sticky="w")
        self.dup_error.grid(row=0, column=2, sticky="w")

        trans_label = tk.Label(costs_frame, text="Transfer:")
        self.trans_error = tk.Label(costs_frame, text="")
        # %P = value of the entry if the edit is allowed
        # see https://stackoverflow.com/questions/4140437/interactively-validating-entry-widget-content-in-tkinter
        trans_vcmd = (self.register(self.validate_trans_input), '%P')
        self.trans_input = tk.DoubleVar()
        self.trans_entry_box = tk.Entry(costs_frame, width=3, textvariable=self.trans_input, validate="all", validatecommand=trans_vcmd)
        trans_label.grid(row=1, column=0, sticky="w")
        self.trans_entry_box.grid(row=1, column=1, sticky="w")
        self.trans_error.grid(row=1, column=2, sticky="w")

        loss_label = tk.Label(costs_frame, text="Loss:")
        loss_label.grid(row=2, column=0, sticky="w")
        self.loss_error = tk.Label(costs_frame, text="")
        # %P = value of the entry if the edit is allowed
        # see https://stackoverflow.com/questions/4140437/interactively-validating-entry-widget-content-in-tkinter
        loss_vcmd = (self.register(self.validate_loss_input), '%P')
        self.loss_input = tk.DoubleVar()
        self.loss_entry_box = tk.Entry(costs_frame, width=3, validate="all", textvariable=self.loss_input, validatecommand=loss_vcmd)
        loss_label.grid(row=2, column=0, sticky="w")
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
        """Plots the cost regions using matplotlib and embeds the graph in a tkinter window."""    
        # Creates a new tkinter window 
        plt_window = tk.Toplevel(self.master)
        plt_window.geometry("550x550")
        plt_window.title("Matplotlib Graph DEMO")
        # Creates a new frame
        plt_frame = tk.Frame(plt_window)
        plt_frame.pack(fill=tk.BOTH, expand=1)
        plt_frame.pack_propagate(False)
        recon_input = empress.read_input(self.file_path)
        cost_regions = empress.compute_cost_regions(recon_input, 0.5, 10, 0.5, 10)  
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
        """Updates the DTL costs when user clicks on the matplotlib graph, otherwise pops up a warning message window."""
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
        """Displays reconciliation results in numbers and further viewing options for graphical analysis."""
        # Creates a frame for the three checkbuttons
        recon_checkbox_frame = tk.Frame(self.func_frame)
        recon_checkbox_frame.grid(row=3, column=0, sticky="nsew")
        recon_checkbox_frame.pack_propagate(False)
        self.recon_space_btn_var = tk.BooleanVar()
        self.recons_btn_var = tk.BooleanVar()
        self.histogram_btn_var = tk.BooleanVar()
        recon_space_btn = tk.Checkbutton(recon_checkbox_frame, text="View solution space", 
            padx=10, variable=self.recon_space_btn_var, 
            command=self.open_and_close_window_recon_space)
        recons_btn = tk.Checkbutton(recon_checkbox_frame, text="View reconciliations", 
            padx=10, variable=self.recons_btn_var, 
            command=self.open_and_close_window_recons)
        histogram_btn = tk.Checkbutton(recon_checkbox_frame, text="Stats mode", 
            padx=36, variable=self.histogram_btn_var, 
            command=self.open_and_close_window_histogram)
        recon_space_btn.pack()
        recons_btn.pack()
        histogram_btn.pack()

        # Shows reconciliation results as numbers
        recon_nums_frame = tk.Frame(self.output_frame)
        recon_nums_frame.grid(row=2, column=0, sticky="nsew")
        recon_nums_frame.grid_propagate(False)
        recon_MPRs_label = tk.Label(recon_nums_frame, text="Number of MPRs:")
        recon_cospeci_label = tk.Label(recon_nums_frame, text="# Cospeciations:")
        recon_dup_label = tk.Label(recon_nums_frame, text="# Duplications:")
        recon_trans_label = tk.Label(recon_nums_frame, text="# Transfers:")
        recon_loss_label = tk.Label(recon_nums_frame, text="# Losses:")
        recon_MPRs_label.grid(row=0, column=0, sticky="w")
        recon_cospeci_label.grid(row=1, column=0, sticky="w")
        recon_dup_label.grid(row=2, column=0, sticky="w")
        recon_trans_label.grid(row=3, column=0, sticky="w")
        recon_loss_label.grid(row=4, column=0, sticky="w")

    def open_and_close_window_recon_space(self):
        """
        Opens a new window titled "View reconciliation space" when the checkbox is checked,
        and closes the window when the checkbox is unchecked.
        """
        if self.recon_space_btn_var.get() == True:
            self.recon_space_window = tk.Toplevel(self.master)
            self.recon_space_window.geometry("400x400")
            self.recon_space_window.title("View reconciliation space")
            ReconSpaceWindow(self.recon_space_window)
        if self.recon_space_btn_var.get() == False:
            if self.recon_space_window.winfo_exists() == 1:
                self.recon_space_window.destroy()

    def open_and_close_window_recons(self):
        """
        Opens a new window titled "View reconciliations" when the checkbox is checked,
        and closes the window when the checkbox is unchecked.
        """
        if self.recons_btn_var.get() == True:
            self.recons_window = tk.Toplevel(self.master)
            self.recons_window.geometry("400x400")
            self.recons_window.title("View reconciliations")
            ReconsWindow(self.recons_window)
        if self.recons_btn_var.get() == False:
            if self.recons_window.winfo_exists() == 1:
                self.recons_window.destroy()

    def open_and_close_window_histogram(self):
        """
        Opens a new window titled "View p-value histogram" when the checkbox is checked,
        and closes the window when the checkbox is unchecked.
        """
        if self.histogram_btn_var.get() == True:
            self.histogram_window = tk.Toplevel(self.master)
            self.histogram_window.geometry("400x400")
            self.histogram_window.title("View p-value histogram")
            HistogramWindow(self.histogram_window)
        if self.histogram_btn_var.get() == False:
            if self.histogram_window.winfo_exists() == 1:
                self.histogram_window.destroy()

# View reconciliation space 
class ReconSpaceWindow:
    def __init__(self, master):
        self.master = master        
        self.frame = tk.Frame(master)
        self.frame.pack(fill=tk.BOTH, expand=1)
        self.frame.pack_propagate(False)

# View reconciliations 
class ReconsWindow:
    def __init__(self, master):
        self.master = master        
        self.frame = tk.Frame(master)
        self.frame.pack(fill=tk.BOTH, expand=1)
        self.frame.pack_propagate(False)

# View p-value histogram 
class HistogramWindow:
    def __init__(self, master):
        self.master = master        
        self.frame = tk.Frame(master)
        self.frame.pack(fill=tk.BOTH, expand=1)
        self.frame.pack_propagate(False)

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
