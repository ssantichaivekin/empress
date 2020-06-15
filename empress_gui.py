# empress_gui.py

import tkinter as tk
from tkinter import messagebox
from pathlib import Path
import os
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from matplotlib.backend_bases import MouseEvent, key_press_handler
import empress
import ReconInput

class App:

    def __init__(self, master):
        self.master = master
        # Configures the master frame 
        master.grid_rowconfigure(0, weight=1)
        master.grid_rowconfigure(1, weight=2)
        master.grid_columnconfigure(0, weight=1)
        master.grid_columnconfigure(1, weight=1)

        # Creates a logo frame on top of the master frame 
        self.logo_frame = tk.Frame(master)
        # sticky="nsew" means that self.logo_frame expands in all four directions (north, south, east and west) 
        # to fully occupy the allocated space in the grid system (row 0 column 0&1)
        self.logo_frame.grid(row=0, column=0, columnspan=2, sticky="nsew")
        self.logo_frame.grid_propagate(False)

        # Adds background image
        photo = tk.PhotoImage(file="./assets/jane_logo_thin.gif")
        label = tk.Label(self.logo_frame, image=photo)
        label.place(x=0, y=0)
        label.image = photo

        # Creates an input frame on the left side of the master frame 
        self.func_frame = tk.Frame(master)
        self.func_frame.grid(row=1, column=0, sticky="nsew")
        self.func_frame.grid_rowconfigure(0, weight=1)
        self.func_frame.grid_rowconfigure(1, weight=1)
        self.func_frame.grid_rowconfigure(2, weight=1)
        self.func_frame.grid_rowconfigure(3, weight=1)
        self.func_frame.grid_columnconfigure(0, weight=1)
        self.func_frame.grid_propagate(False)

        # Creates an output frame on the right side of the master frame
        self.output_frame = tk.Frame(master)
        self.output_frame.grid(row=1, column=1, sticky="nsew")
        self.output_frame.grid_rowconfigure(0, weight=1)
        self.output_frame.grid_rowconfigure(1, weight=1)
        self.output_frame.grid_rowconfigure(2, weight=1)
        self.output_frame.grid_columnconfigure(0, weight=1)
        self.output_frame.grid_propagate(False)

        # "Load File" button 
        # Loads in an input .newick file
        # and displays the number of leaves in each tree (DEMO for now) and entry boxes for DTL costs
        # load_file_btn = tk.Button(self.func_frame, text="Load File", background="green", height=2, width=9, command=self.load_file)
        # load_file_btn.grid(row=0, column=0)
        # Creates a Label to overwrite the old file path 
        # self.file_path_label = tk.Label(self.output_frame)

        self.file_to_load = tk.StringVar(self.func_frame) 
        self.file_to_load.set("Load Files")
        self.options = ["Load host tree file", "Load parasite tree file", "Load mapping"]
        self.load_file_list = tk.OptionMenu(self.func_frame, self.file_to_load, *self.options, command=self.load_three_files)
        self.load_file_list.grid(row=0, column=0)
        self.R = ReconInput.ReconInput()
        # Creates Labels to overwrite the old displayed information 
        self.host_tree_info = tk.Label(self.output_frame)
        self.parasite_tree_info = tk.Label(self.output_frame)
        self.mapping_info = tk.Label(self.output_frame)

        # "View Event Cost Regions" button 
        # Pops up a matplotlib graph for the cost regions
        self.view_cost_btn = tk.Button(self.func_frame, text="View Event Cost Regions", command=self.plot_cost_regions, state=tk.DISABLED)
        self.view_cost_btn.grid(row=1, column=0)

        # "Compute Reconciliations" button 
        # Displays reconciliation results(numbers) and three options(checkboxes) for viewing graphical analysis
        self.compute_recon_button = tk.Button(self.func_frame, text="Compute Reconciliations", command=self.recon_analysis, state=tk.DISABLED)
        self.compute_recon_button.grid(row=2, column=0)

    def load_three_files(self, event):
        """
        """ 
        input_info_frame = tk.Frame(self.output_frame)
        input_info_frame.grid(row=0, column=0, sticky="nsew")
        input_info_frame.grid_columnconfigure(0, weight=1)
        input_info_frame.grid_rowconfigure(0, weight=1)
        input_info_frame.grid_rowconfigure(1, weight=1)
        input_info_frame.grid_rowconfigure(2, weight=1)
        input_info_frame.grid_propagate(False)

        # Clicking on "Load host tree file" 
        if self.file_to_load.get() == "Load host tree file":
            # Allows loading a .newick file
            self.host_file_path = None
            # initialdir is set to be the current working directory
            input_file = tk.filedialog.askopenfilename(initialdir=os.getcwd(), title="Select a host file")
            if Path(input_file).suffix == '.nwk':
                print(self.R.read_host(input_file)) 
                if self.R.read_host(input_file) is not None:
                    self.host_file_path = input_file
                    self.host_tree_info.destroy()  # Overwrites the old file path in the grid system
                    # This is only DEMO for now
                    self.host_tree_info = tk.Label(input_info_frame, text="Host:  83 tips (DEMO)")
                    self.host_tree_info.grid(row=0, column=0, sticky="w")
                else: 
                    messagebox.showinfo("Warning", "The input file cannot be read.")          
            else:
                messagebox.showinfo("Warning", "Please load a '.nwk' file.")

        # Clicking on "Load parasite tree file" 
        elif self.file_to_load.get() == "Load parasite tree file":
            # Allows loading a .newick file
            self.host_file_path = None
            # initialdir is set to be the current working directory
            input_file = tk.filedialog.askopenfilename(initialdir=os.getcwd(), title="Select a host file")
            if Path(input_file).suffix == '.nwk': 
                if self.R.read_parasite(input_file) is not None:
                    self.host_file_path = input_file
                    self.host_tree_info.destroy()  # Overwrites the old file path in the grid system
                    # This is only DEMO for now
                    self.parasite_tree_info = tk.Label(input_info_frame, text="Parasite/symbiont:  78 tips (DEMO)")
                    self.parasite_tree_info.grid(row=1, column=0, sticky="w")
                else: 
                    messagebox.showinfo("Warning", "The input file cannot be read.")          
            else:
                messagebox.showinfo("Warning", "Please load a '.nwk' file.")

        # Clicking on "Load mapping" 
        elif self.file_to_load.get() == "Load mapping":
            # Allows loading a .newick file
            self.host_file_path = None
            # initialdir is set to be the current working directory
            input_file = tk.filedialog.askopenfilename(initialdir=os.getcwd(), title="Select a host file")
            if Path(input_file).suffix == '.mapping': 
                if self.R.read_mapping(input_file) is not None:
                    self.host_file_path = input_file
                    self.host_tree_info.destroy()  # Overwrites the old file path in the grid system
                    # This is only DEMO for now
                    self.mapping_info = tk.Label(input_info_frame, text="Mapping:  (DEMO)")
                    self.mapping_info.grid(row=2, column=0, sticky="w")
                else: 
                    messagebox.showinfo("Warning", "The input file cannot be read.")          
            else:
                messagebox.showinfo("Warning", "Please load a '.mapping' file.")

        # Enables the next step, setting DTL costs
        if self.R.complete(): 
            self.view_cost_btn.configure(state=tk.NORMAL)
            self.dtl_cost()

    # def load_file(self):
    #     """Loads in an input file and displays the number of leaves in each tree when "Load File" button is clicked."""
    #     # Creates a frame to display the number of leaves and the file path
    #     input_info_frame = tk.Frame(self.output_frame)
    #     input_info_frame.grid(row=0, column=0, sticky="nsew")
    #     input_info_frame.grid_columnconfigure(0, weight=1)
    #     input_info_frame.grid_rowconfigure(0, weight=1)
    #     input_info_frame.grid_rowconfigure(1, weight=1)
    #     input_info_frame.grid_rowconfigure(2, weight=1)
    #     input_info_frame.grid_propagate(False)

    #     # Allows loading a .newick file
    #     self.file_path = None
    #     # initialdir is set to be the current working directory
    #     input_file = tk.filedialog.askopenfilename(initialdir=os.getcwd(), title="Select a file")
    #     if Path(input_file).suffix == '.newick': 
    #         self.file_path = input_file
    #         self.file_path_label.destroy()  # Overwrites the old file path in the grid system
    #         self.file_path_label = tk.Label(input_info_frame, text=input_file)
    #         self.file_path_label.grid(row=0, column=0, sticky="w")
    #         # This is only DEMO for now
    #         host_tree_info = tk.Label(input_info_frame, text="Host:  83 tips (DEMO)")
    #         host_tree_info.grid(row=1, column=0, sticky="w")
    #         parasite_info = tk.Label(input_info_frame, text="Parasite/symbiont:  78 tips (DEMO)")
    #         parasite_info.grid(row=2, column=0, sticky="w")           
    #     else:
    #         messagebox.showinfo("Warning", "Please load a '.newick' file.")

    #     # Enables the next step, setting DTL costs
    #     if self.file_path is not None: 
    #         self.view_cost_btn.configure(state=tk.NORMAL)
    #         self.dtl_cost()

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

        dup_label = tk.Label(costs_frame, text="Duplication:")
        dup_label.grid(row=0, column=0, sticky="w")
        self.dup_input = tk.DoubleVar()
        dup_entry_box = tk.Entry(costs_frame, width=3, textvariable=self.dup_input)
        self.dup_cost = None
        dup_entry_box.bind('<Key>', self.receive_dup_input)
        dup_entry_box.grid(row=0, column=1, sticky="w")

        trans_label = tk.Label(costs_frame, text="Transfer:")
        trans_label.grid(row=1, column=0, sticky="w")
        self.trans_input = tk.DoubleVar()
        trans_entry_box = tk.Entry(costs_frame, width=3, textvariable=self.trans_input)
        self.trans_cost = None
        trans_entry_box.bind('<Key>', self.receive_trans_input)
        trans_entry_box.grid(row=1, column=1, sticky="w")

        loss_label = tk.Label(costs_frame, text="Loss:")
        loss_label.grid(row=2, column=0, sticky="w")
        self.loss_input = tk.DoubleVar()
        loss_entry_box = tk.Entry(costs_frame, width=3, textvariable=self.loss_input)  
        self.loss_cost = None
        loss_entry_box.bind('<Key>', self.receive_loss_input)
        loss_entry_box.grid(row=2, column=1, sticky="w")

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
        #recon_input = empress.read_input(self.file_path)
        recon_input = empress.read_input(self.R)
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
            self.enable_recon_btn()
        else:
            messagebox.showinfo("Warning", "Please click inside the axes bounds.")

    def receive_dup_input(self, *args):  # *args needed for tkinter callback
        """Check and update the duplication cost when user enters a value in the entry box."""
        try:
            dup_cost = self.dup_input.get()
        except tk.TclError as e:
            messagebox.showinfo("Warning", "Please enter a floating point number:\n" + str(e))
            return
        
        if dup_cost >= 0:
            self.dup_cost = dup_cost
            if self.verify_valid_dtl():
                self.enable_recon_btn()
        else:
            messagebox.showinfo("Warning", "Please enter a non-negative number.")
    
    def receive_trans_input(self, *args):  # *args needed for tkinter callback
        """Check and update the transfer cost when user enters a value in the entry box."""
        try:
            trans_cost = self.trans_input.get()
        except tk.TclError as e:
            messagebox.showinfo("Warning", "Please enter a floating point number:\n" + str(e))
            return
        
        if trans_cost >= 0:
            self.trans_cost = trans_cost
            if self.verify_valid_dtl():
                self.enable_recon_btn()
        else:
            messagebox.showinfo("Warning", "Please enter a non-negative number.")
    
    def receive_loss_input(self, *args):  # *args needed for tkinter callback
        """Check and update the loss cost when user enters a value in the entry box."""
        try:
            trans_cost = self.trans_input.get()
        except tk.TclError as e:
            messagebox.showinfo("Warning", "Please enter a floating point number:\n" + str(e))
            return
        
        if trans_cost >= 0:
            self.trans_cost = trans_cost
            if self.verify_valid_dtl():
                self.enable_recon_btn()
        else:
            messagebox.showinfo("Warning", "Please enter a non-negative number.")
    
    def verify_valid_dtl(self):
        return self.dup_cost and self.trans_cost and self.loss_cost

    def enable_recon_btn(self):
        """Enables the next step, viewing reconciliation results, after DTL costs are set correctly."""
        self.compute_recon_button.configure(state=tk.NORMAL)

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
