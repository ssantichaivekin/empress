# eMPRess_GUI_iteration5

import tkinter as tk
from tkinter import messagebox
from pathlib import Path
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from matplotlib.backend_bases import MouseEvent, key_press_handler
import empress

class App:

    def __init__(self, master):
        self.master = master
        ### configures the master frame ###
        master.grid_rowconfigure(0, weight=1)
        master.grid_rowconfigure(1, weight=2)
        master.grid_columnconfigure(0, weight=1)
        master.grid_columnconfigure(1, weight=1)

        ### creates a logo frame on top of the master frame ###
        self.logo_frame = tk.Frame(master)
        self.logo_frame.grid(row=0, column=0, columnspan=2, sticky="nsew")
        self.logo_frame.grid_propagate(False)

        # adds background image
        photo = tk.PhotoImage(file="JaneTransLogo-thin.png")
        label = tk.Label(self.logo_frame, image=photo)
        label.place(x=0, y=0)
        label.image = photo

        ### creates an input frame on the left side of the master frame ###
        self.func_frame = tk.Frame(master)
        self.func_frame.grid(row=1, column=0, sticky="nsew")
        self.func_frame.grid_rowconfigure(0, weight=1)
        self.func_frame.grid_rowconfigure(1, weight=1)
        self.func_frame.grid_rowconfigure(2, weight=1)
        self.func_frame.grid_rowconfigure(3, weight=1)
        self.func_frame.grid_columnconfigure(0, weight=1)
        self.func_frame.grid_propagate(False)

        ### creates an output frame on the right side of the master frame ###
        self.output_frame = tk.Frame(master)
        self.output_frame.grid(row=1, column=1, sticky="nsew")
        self.output_frame.grid_rowconfigure(0, weight=1)
        self.output_frame.grid_rowconfigure(1, weight=1)
        self.output_frame.grid_rowconfigure(2, weight=1)
        self.output_frame.grid_columnconfigure(0, weight=1)
        self.output_frame.grid_propagate(False)

        ### "Load File" button ###
        # loads in an input .newick file
        # and displays the number of leaves in each tree (DEMO for now) and entry boxes for DTL costs
        load_file_btn = tk.Button(self.func_frame, text="Load File", background="green", height=2, width=9, command=self.load_file)
        load_file_btn.grid(row=0, column=0)
        # creates a Label to overwrite the old file path 
        self.file_path_label = tk.Label(self.output_frame)

        ### "View Event Cost Landscape" button ###
        # pops up a matplotlib graph for the cost landscape
        self.view_cost_btn = tk.Button(self.func_frame, text="View Event Cost Landscape", command=self.plot_cost_landscape, state=tk.DISABLED)
        self.view_cost_btn.grid(row=1, column=0)

        ### "Compute Reconciliations" button ###
        # displays reconciliation results(numbers) and three options(checkboxes) for viewing graphical analysis
        self.compute_recon_button = tk.Button(self.func_frame, text="Compute Reconciliations", command=self.recon_analysis, state=tk.DISABLED)
        self.compute_recon_button.grid(row=2, column=0)

    def load_file(self):
        """Loads in an input file and displays the number of leaves in each tree when "Load File" button is clicked."""
        # creates a frame to display the number of leaves and the file path
        recon_input_info_frame = tk.Frame(self.output_frame)
        recon_input_info_frame.grid(row=0, column=0, sticky="nsew")
        recon_input_info_frame.grid_columnconfigure(0, weight=1)
        recon_input_info_frame.grid_rowconfigure(0, weight=1)
        recon_input_info_frame.grid_rowconfigure(1, weight=1)
        recon_input_info_frame.grid_rowconfigure(2, weight=1)
        recon_input_info_frame.grid_propagate(False)

        # allows loading a .newick file
        self.file_path = ""
        input_file = tk.filedialog.askopenfilename(initialdir="/desktop", title="Select a file")
        if Path(input_file).suffix == '.newick': 
            self.file_path = input_file
            self.file_path_label.destroy()  # overwrites the old file path in the grid system
            self.file_path_label = tk.Label(recon_input_info_frame, text=input_file)
            self.file_path_label.grid(row=0, column=0, sticky="w")
            # this is only DEMO for now
            host_tree_info = tk.Label(recon_input_info_frame, text="Host:  83 tips (DEMO)")
            host_tree_info.grid(row=1, column=0, sticky="w")
            parasite_info = tk.Label(recon_input_info_frame, text="Parasite/symbiont:  78 tips (DEMO)")
            parasite_info.grid(row=2, column=0, sticky="w")           
        else:
            messagebox.showinfo("Warning", "Please load a '.newick' file.")

        # enables the next step, setting DTL costs
        if self.file_path != "": 
            self.view_cost_btn.configure(state=tk.NORMAL)
            self.DTL_cost()

    def DTL_cost(self):
        """Sets DTL costs by clicking on the matplotlib graph or by entering manually."""
        # creates a frame for setting DTL costs
        costs_frame = tk.Frame(self.output_frame)
        costs_frame.grid(row=1, column=0, sticky="nsew")
        costs_frame.grid_columnconfigure(0, weight=1)
        costs_frame.grid_columnconfigure(1, weight=3)
        costs_frame.grid_rowconfigure(0, weight=1)
        costs_frame.grid_rowconfigure(1, weight=1)
        costs_frame.grid_rowconfigure(2, weight=1)
        costs_frame.grid_propagate(False)

        dup_label = tk.Label(costs_frame, text="Duplication:")
        trans_label = tk.Label(costs_frame, text="Transfer:")
        loss_label = tk.Label(costs_frame, text="Loss:")
        dup_label.grid(row=0, column=0, sticky="w")
        trans_label.grid(row=1, column=0, sticky="w")
        loss_label.grid(row=2, column=0, sticky="w")
        self.dup_cost = tk.StringVar()
        self.trans_cost = tk.StringVar()
        self.loss_cost = tk.StringVar()
        dup_entry = tk.Entry(costs_frame, width=3, textvariable=self.dup_cost)
        trans_entry = tk.Entry(costs_frame, width=3, textvariable=self.trans_cost)
        loss_entry = tk.Entry(costs_frame, width=3, textvariable=self.loss_cost)
        dup_entry.bind('<Return>', self.check_dup_input)
        trans_entry.bind('<Return>', self.check_trans_input)
        loss_entry.bind('<Return>', self.check_loss_input)
        #dup_entry.bind('<FocusOut>', self.check_dup_input)  # (bug) this will make the invalid input warning appear twice
        #trans_entry.bind('<FocusOut>', self.check_trans_input)  # same as above 
        #loss_entry.bind('<FocusOut>', self.check_loss_input)  # same as above 
        dup_entry.grid(row=0, column=1, sticky="w")
        trans_entry.grid(row=1, column=1, sticky="w")
        loss_entry.grid(row=2, column=1, sticky="w")

    def plot_cost_landscape(self):
        """Plots the cost landscape using matplotlib and embeds the graph in a tkinter window."""    
        # creates a new tkinter window 
        plt_window = tk.Toplevel(self.master)
        plt_window.geometry("550x550")
        plt_window.title("Matplotlib Graph DEMO")
        # creates a new frame
        plt_frame = tk.Frame(plt_window)
        plt_frame.pack(fill=tk.BOTH, expand=1)
        plt_frame.pack_propagate(False)
        # use empress wrapper
        recon_input = empress.read_input(self.file_path)
        cost_regions = empress.compute_cost_regions(recon_input, 0.5, 10, 0.5, 10)  
        #cost_regions.draw_to_file('./examples/cost_poly.png')  # draw and save to a file
        fig = cost_regions.draw()  # draw to figure (creates matplotlib figure)
        canvas = FigureCanvasTkAgg(fig, plt_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=True)
        toolbar = NavigationToolbar2Tk(canvas, plt_frame)
        toolbar.update()
        canvas.get_tk_widget().pack(side=tk.TOP)
        # updates the DTL costs using the x,y coordinates clicked by the user inside the graph 
        # otherwise pops up a warning message window
        fig.canvas.callbacks.connect('button_press_event', self.get_xy_coordinates)

    def get_xy_coordinates(self, event):
        """Updates the DTL costs when user clicks on the matplotlib graph, otherwise pops up a warning message window."""
        if event.inaxes is not None:
            self.dup_cost.set("1")
            self.trans_cost.set(str(round(event.ydata, 2)))
            self.loss_cost.set(str(round(event.xdata, 2)))
            # enables the next step, viewing reconciliation result
            self.has_dup_cost = True
            self.has_trans_cost = True
            self.has_loss_cost = True
            self.enable_recon_btn()
        else:
            messagebox.showinfo("Warning", "Please click inside the axes bounds.")

    def enable_recon_btn(self):
        """Enables the next step, viewing reconciliation results, after DTL costs are set correctly."""
        if self.has_dup_cost == True and self.has_trans_cost == True and self.has_loss_cost == True:
            self.compute_recon_button.configure(state=tk.NORMAL)

    def check_dup_input(self, *args):
        """Checks and updates the duplication cost when user enters a value in the entry box."""
        dupValue_without_decimal_point = self.dup_cost.get().replace(".", "")
        if str.isdigit(dupValue_without_decimal_point) and ("-" not in dupValue_without_decimal_point):
                self.dup_cost.set(str(round(float(self.dup_cost.get()), 2)))
                self.has_dup_cost = True
                self.enable_recon_btn()
        else:
            messagebox.showinfo("Warning", "Please enter a non-negative number.")
            self.dup_cost.set("")
            self.has_dup_cost = False

    def check_trans_input(self, *args):
        """Checks and updates the transfer cost when user enters a value in the entry box."""
        transValue_without_decimal_point = self.trans_cost.get().replace(".", "")
        if str.isdigit(transValue_without_decimal_point) and ("-" not in transValue_without_decimal_point):
                self.trans_cost.set(str(round(float(self.trans_cost.get()), 2)))
                self.has_trans_cost = True
                self.enable_recon_btn()
        else:
            messagebox.showinfo("Warning", "Please enter a non-negative number.")
            self.trans_cost.set("")
            self.has_trans_cost = False
    
    def check_loss_input(self, *args):
        """Checks and updates the loss cost when user enters a value in the entry box."""
        lossValue_without_decimal_point = self.loss_cost.get().replace(".", "")
        if str.isdigit(lossValue_without_decimal_point) and ("-" not in lossValue_without_decimal_point):
                self.loss_cost.set(str(round(float(self.loss_cost.get()), 2)))
                self.has_loss_cost = True
                self.enable_recon_btn()
        else:
            messagebox.showinfo("Warning", "Please enter a non-negative number.")
            self.loss_cost.set("")
            self.has_loss_cost = False

    def recon_analysis(self):
        """Displays reconciliation results in numbers and further viewing options for graphical analysis."""
        # creates a frame for the three checkbuttons
        recon_checkbox_frame = tk.Frame(self.func_frame)
        recon_checkbox_frame.grid(row=3, column=0, sticky="nsew")
        recon_checkbox_frame.pack_propagate(False)
        self.recon_space_btn_var = tk.IntVar()
        self.recons_btn_var = tk.IntVar()
        self.histogram_btn_var = tk.IntVar()
        recon_space_btn = tk.Checkbutton(recon_checkbox_frame, text="View solution space", padx=10, variable=self.recon_space_btn_var, command=self.open_and_close_window_recon_space)
        recons_btn = tk.Checkbutton(recon_checkbox_frame, text="View reconciliations", padx=10, variable=self.recons_btn_var, command=self.open_and_close_window_recons)
        histogram_btn = tk.Checkbutton(recon_checkbox_frame, text="Stats mode", padx=36, variable=self.histogram_btn_var, command=self.open_and_close_window_histogram)
        recon_space_btn.pack()
        recons_btn.pack()
        histogram_btn.pack()

        # shows reconciliation results as numbers
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
        if self.recon_space_btn_var.get() == 1:
            self.recon_space_window = tk.Toplevel(self.master)
            self.recon_space_window.geometry("400x400")
            self.recon_space_window.title("View reconciliation space")
            Recon_space_window(self.recon_space_window)
        if self.recon_space_btn_var.get() == 0:
            if self.recon_space_window.winfo_exists() == 1:
                self.recon_space_window.destroy()

    def open_and_close_window_recons(self):
        """
        Opens a new window titled "View reconciliations" when the checkbox is checked,
        and closes the window when the checkbox is unchecked.
        """
        if self.recons_btn_var.get() == 1:
            self.recons_window = tk.Toplevel(self.master)
            self.recons_window.geometry("400x400")
            self.recons_window.title("View reconciliations")
            Recon_window(self.recons_window)
        if self.recons_btn_var.get() == 0:
            if self.recons_window.winfo_exists() == 1:
                self.recons_window.destroy()

    def open_and_close_window_histogram(self):
        """
        Opens a new window titled "View p-value histogram" when the checkbox is checked,
        and closes the window when the checkbox is unchecked.
        """
        if self.histogram_btn_var.get() == 1:
            self.histogram_window = tk.Toplevel(self.master)
            self.histogram_window.geometry("400x400")
            self.histogram_window.title("View p-value histogram")
            Histogram_window(self.histogram_window)
        if self.histogram_btn_var.get() == 0:
            if self.histogram_window.winfo_exists() == 1:
                self.histogram_window.destroy()

### View reconciliation space ###
class Recon_space_window:
    def __init__(self, master):
        self.master = master        
        self.frame = tk.Frame(master)
        self.frame.pack(fill=tk.BOTH, expand=1)
        self.frame.pack_propagate(False)

### View reconciliations ###
class Recon_window:
    def __init__(self, master):
        self.master = master        
        self.frame = tk.Frame(master)
        self.frame.pack(fill=tk.BOTH, expand=1)
        self.frame.pack_propagate(False)

### View p-value histogram ###
class Histogram_window:
    def __init__(self, master):
        self.master = master        
        self.frame = tk.Frame(master)
        self.frame.pack(fill=tk.BOTH, expand=1)
        self.frame.pack_propagate(False)

def on_closing():
   plt.close("all")
   root.destroy()


root = tk.Tk()
root.geometry("600x600")
root.title("eMPRess GUI Version 1")
App(root)
root.protocol("WM_DELETE_WINDOW", on_closing)
root.mainloop()
root.quit()






























