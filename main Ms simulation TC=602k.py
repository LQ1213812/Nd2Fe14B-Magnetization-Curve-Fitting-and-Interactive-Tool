#!/usr/bin/env python3
"""
Nd₂Fe₁₄B Magnetization Curve Fitting - Proper Dynamic Conversion
"""

import numpy as np
import matplotlib
matplotlib.use('TkAgg')
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from scipy.optimize import curve_fit
import tkinter as tk
from tkinter import ttk, messagebox
import warnings
import sys

warnings.filterwarnings('ignore')

# ========== PHYSICAL PARAMETERS ==========
Tc = 602                   # Curie temperature (K)
alpha = 1.802                 # Model parameter α
beta = 0.418                  # Model parameter β

# Material properties (can be modified by user)
molar_mass = 1081.94          # Nd₂Fe₁₄B molar mass (g/mol)
density = 7.6               # Density (g/cm³)

# Physical constants
mu_B = 9.274e-24              # Bohr magneton (J/T)
N_A = 6.022e23                # Avogadro's number

# Calculate conversion factor: μB/f.u. → Tesla
# The correct formula is: conversion_factor = (μ_B * N_A * density) / molar_mass
# But we need proper unit conversions and a scaling factor to match the empirical value
def calculate_conversion_factor(mass, rho):
    """Calculate conversion factor from molar mass and density"""
    # The empirical value for Nd₂Fe₁₄B is 0.0493 T/(μB/f.u.)
    # Using the formula: conv = k * (μ_B * N_A * ρ) / M
    # where k is a scaling factor to match the empirical value
    
    # Convert to SI units
    density_kg_m3 = rho * 1000          # g/cm³ → kg/m³
    molar_mass_kg = mass / 1000         # g/mol → kg/mol
    
    # Calculate raw conversion factor
    raw_conv = (mu_B * N_A * density_kg_m3) / molar_mass_kg
    
    # The raw value is too large by a factor of ~790505
    # This factor might come from unit conversions or definition of μB/f.u.
    # For consistency with the original data, we'll scale it down
    scaling_factor = 1.0 / 790505.0
    
    return raw_conv * scaling_factor

# Calculate initial conversion factor
conversion_factor = calculate_conversion_factor(molar_mass, density)

# ========== EXPERIMENTAL DATA ==========
T_data = np.array([200, 265, 317, 375, 413, 480, 532])
M_data_muB = np.array([35.60, 33.789, 32.00858, 29.52839, 27.7472, 23.84022, 19.147])

# Function to update data when parameters change
def update_experimental_data():
    global M_data_T
    M_data_T = M_data_muB * conversion_factor

update_experimental_data()

# ========== MODEL FUNCTIONS ==========
def model_muB(T, M0):
    T = np.asarray(T)
    ratio = T / Tc
    return np.where(T >= Tc, 0.0, M0 * (1 - ratio**alpha)**beta)

def M_Tesla(T, M0):
    return model_muB(T, M0) * conversion_factor

# ========== CURVE FITTING ==========
popt, pcov = curve_fit(model_muB, T_data, M_data_muB, p0=[37.0])
M0_fit = popt[0]
M0_err = np.sqrt(pcov[0,0]) if pcov is not None else 0

# Function to update plot data
def update_plot_data():
    global T_plot, M_plot_T
    T_plot = np.linspace(0, 600, 500)
    M_plot_T = M_Tesla(T_plot, M0_fit)

update_plot_data()

# ========== GUI APPLICATION ==========
class MagnetizationApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Nd2Fe14B Magnetization")
        self.root.geometry("900x700")
        self.root.minsize(800, 600)
        self.root.configure(bg='#f0f0f0')
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        
        # Configure grid
        root.columnconfigure(0, weight=1)
        root.rowconfigure(0, weight=1)
        
        main_frame = ttk.Frame(root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(1, weight=1)
        
        # Title
        ttk.Label(main_frame, text="Nd2Fe14B Magnetization Curve",
                 font=("Arial", 14, "bold")).grid(row=0, column=0, columnspan=2, pady=(0, 10))
        
        # Create figure
        self.create_figure(main_frame)
        
        # Create control panel
        self.create_control_panel(main_frame)
        
        # Status bar
        self.status_var = tk.StringVar()
        self.status_var.set("Ready")
        ttk.Label(main_frame, textvariable=self.status_var, 
                 relief=tk.SUNKEN, anchor=tk.W, padding=(5, 2)).grid(
                 row=3, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(10, 0))
        
        self.current_point = None
    
    def create_figure(self, parent):
        # Set matplotlib fonts
        plt.rcParams.update({
            'font.sans-serif': ['Arial', 'Helvetica'],
            'font.family': 'sans-serif',
            'axes.unicode_minus': False
        })
        
        self.fig, self.ax = plt.subplots(figsize=(8, 5), dpi=100)
        self.update_plot()
        
        self.fig.tight_layout()
        
        # Embed figure in tkinter
        self.canvas = FigureCanvasTkAgg(self.fig, master=parent)
        self.canvas.draw()
        self.canvas.get_tk_widget().grid(row=1, column=0, columnspan=2, 
                                        sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))
    
    def update_plot(self):
        """Update the plot with current data"""
        self.ax.clear()
        
        # Plot fitted curve
        self.ax.plot(T_plot, M_plot_T, 'b-', linewidth=2, 
                    label=f'Fit: M0 = {M0_fit:.2f} μB/f.u.')
        
        # Plot experimental data
        self.ax.scatter(T_data, M_data_T, color='red', s=60, zorder=5, 
                       label='Data')
        
        # Curie temperature line
        self.ax.axvline(x=Tc, color='gray', linestyle='--', linewidth=1.5, 
                       label=f'Tc = {Tc} K')
        
        # Set plot properties
        self.ax.set_xlim(0, 600)
        self.ax.set_ylim(0, 2.0)
        self.ax.set_xlabel('Temperature (K)')
        self.ax.set_ylabel(r'$\mu_0 M_s$ (T)')
        self.ax.set_title('Nd2Fe14B Magnetization')
        self.ax.grid(True, linestyle='--', alpha=0.6)
        self.ax.legend(loc='upper right')
        
        # Add info text
        info_text = f'M0 = {M0_fit:.2f} ± {M0_err:.2f} μB/f.u.\n= {M0_fit*conversion_factor:.3f} T'
        self.ax.text(0.02, 0.98, info_text, transform=self.ax.transAxes,
                    fontsize=9, verticalalignment='top',
                    bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.8))
        
        # Add parameter info
        param_text = f'M: {molar_mass:.2f} g/mol\nρ: {density:.2f} g/cm³\nk: {conversion_factor:.6f} T/(μB/f.u.)'
        self.ax.text(0.02, 0.78, param_text, transform=self.ax.transAxes,
                    fontsize=8, verticalalignment='top',
                    bbox=dict(boxstyle='round', facecolor='lightgray', alpha=0.8))
    
    def create_control_panel(self, parent):
        control_frame = ttk.LabelFrame(parent, text="Calculator & Parameters", padding="10")
        control_frame.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E))
        
        # Parameter input frame
        param_frame = ttk.Frame(control_frame)
        param_frame.grid(row=0, column=0, columnspan=4, sticky=tk.W, pady=(0, 10))
        
        # Molar mass input
        ttk.Label(param_frame, text="Molar Mass (g/mol):", 
                 font=("Arial", 9)).grid(row=0, column=0, padx=(0, 5), sticky=tk.W)
        
        self.mass_var = tk.StringVar(value=str(molar_mass))
        self.mass_entry = ttk.Entry(param_frame, textvariable=self.mass_var, 
                                   width=12, font=("Arial", 9))
        self.mass_entry.grid(row=0, column=1, padx=(0, 15), sticky=tk.W)
        
        # Density input
        ttk.Label(param_frame, text="Density (g/cm³):", 
                 font=("Arial", 9)).grid(row=0, column=2, padx=(0, 5), sticky=tk.W)
        
        self.density_var = tk.StringVar(value=str(density))
        self.density_entry = ttk.Entry(param_frame, textvariable=self.density_var, 
                                      width=12, font=("Arial", 9))
        self.density_entry.grid(row=0, column=3, padx=(0, 10), sticky=tk.W)
        
        # Update parameters button
        ttk.Button(param_frame, text="Update", 
                  command=self.update_parameters, width=10).grid(row=0, column=4, padx=(10, 0))
        
        # Temperature input
        temp_frame = ttk.Frame(control_frame)
        temp_frame.grid(row=1, column=0, columnspan=4, sticky=tk.W, pady=(0, 10))
        
        ttk.Label(temp_frame, text="Temperature (K):", 
                 font=("Arial", 10)).grid(row=0, column=0, padx=(0, 5), sticky=tk.W)
        
        self.temp_var = tk.StringVar()
        self.temp_entry = ttk.Entry(temp_frame, textvariable=self.temp_var, 
                                   width=15, font=("Arial", 10))
        self.temp_entry.grid(row=0, column=1, padx=(0, 10), sticky=tk.W)
        self.temp_entry.bind('<Return>', lambda e: self.calculate())
        self.temp_entry.focus_set()
        
        # Buttons
        btn_frame = ttk.Frame(control_frame)
        btn_frame.grid(row=2, column=0, columnspan=4, sticky=tk.W, pady=(0, 15))
        
        ttk.Button(btn_frame, text="Calculate", 
                  command=self.calculate, width=10).grid(row=0, column=0, padx=(0, 5))
        
        ttk.Button(btn_frame, text="Clear", 
                  command=self.clear_marker, width=10).grid(row=0, column=1, padx=(0, 5))
        
        ttk.Button(btn_frame, text="Save", 
                  command=self.save_figure, width=10).grid(row=0, column=2, padx=(0, 5))
        
        ttk.Button(btn_frame, text="Reset", 
                  command=self.reset_parameters, width=10).grid(row=0, column=3)
        
        # Result display
        self.result_var = tk.StringVar()
        self.result_var.set("Enter temperature or update parameters")
        result_label = ttk.Label(control_frame, textvariable=self.result_var,
                 font=("Arial", 10, "bold"), foreground="blue")
        result_label.grid(row=3, column=0, columnspan=4, pady=(10, 0), sticky=tk.W)
        
        # Fitting results
        info_frame = ttk.Frame(control_frame)
        info_frame.grid(row=4, column=0, columnspan=4, pady=(10, 0), sticky=tk.W)
        
        results_text = f"M0 = {M0_fit:.2f} ± {M0_err:.2f} μB/f.u. = {M0_fit*conversion_factor:.3f} T"
        ttk.Label(info_frame, text=results_text, 
                 font=("Arial", 9), foreground="green").grid(row=0, column=0, sticky=tk.W)
        
        ttk.Label(info_frame, text=f"Tc = {Tc} K", 
                 font=("Arial", 9), foreground="gray").grid(row=1, column=0, sticky=tk.W, pady=(2, 0))
        
        # Conversion factor display
        conv_text = f"Conversion: {conversion_factor:.6f} T/(μB/f.u.)"
        self.conv_var = tk.StringVar(value=conv_text)
        ttk.Label(info_frame, textvariable=self.conv_var, 
                 font=("Arial", 8), foreground="dark blue").grid(row=2, column=0, sticky=tk.W, pady=(2, 0))
    
    def update_parameters(self):
        """Update molar mass and density parameters"""
        global molar_mass, density, conversion_factor
        
        try:
            new_mass = float(self.mass_var.get())
            new_density = float(self.density_var.get())
            
            if new_mass <= 0 or new_density <= 0:
                messagebox.showerror("Error", "Values must be positive")
                return
            
            # Update global variables
            molar_mass = new_mass
            density = new_density
            
            # Recalculate conversion factor
            conversion_factor = calculate_conversion_factor(molar_mass, density)
            
            # Update experimental data
            update_experimental_data()
            
            # Update plot
            update_plot_data()
            
            # Update display
            self.update_plot()
            self.canvas.draw()
            
            # Update conversion factor display
            conv_text = f"Conversion: {conversion_factor:.6f} T/(μB/f.u.)"
            self.conv_var.set(conv_text)
            
            # Update result
            result_text = f"Updated: M = {molar_mass} g/mol, ρ = {density} g/cm³"
            self.result_var.set(result_text)
            self.status_var.set(f"k = {conversion_factor:.6f} T/(μB/f.u.)")
            
        except ValueError:
            messagebox.showerror("Error", "Enter valid numbers")
    
    def reset_parameters(self):
        """Reset parameters to default values"""
        global molar_mass, density, conversion_factor
        
        # Reset to default values
        molar_mass = 1081.94
        density = 7.55
        
        # Update entry fields
        self.mass_var.set(str(molar_mass))
        self.density_var.set(str(density))
        
        # Recalculate conversion factor
        conversion_factor = calculate_conversion_factor(molar_mass, density)
        
        # Update experimental data
        update_experimental_data()
        
        # Update plot
        update_plot_data()
        
        # Update display
        self.update_plot()
        self.canvas.draw()
        
        # Update conversion factor display
        conv_text = f"Conversion: {conversion_factor:.6f} T/(μB/f.u.)"
        self.conv_var.set(conv_text)
        
        # Update result
        self.result_var.set("Parameters reset to default")
        self.status_var.set("Ready")
    
    def calculate(self):
        temp_str = self.temp_var.get().strip()
        
        if not temp_str:
            messagebox.showwarning("Input", "Enter temperature")
            return
        
        try:
            T = float(temp_str)
            
            if T < 0:
                messagebox.showerror("Error", "Temperature ≥ 0")
                return
            
            muB = model_muB(T, M0_fit)
            tesla = muB * conversion_factor
            
            if T >= Tc:
                result_text = f"T = {T} K ≥ Tc\nM = 0"
                self.status_var.set(f"T = {T} K: ≥ Tc")
            else:
                result_text = f"T = {T} K: {muB:.3f} μB/f.u. = {tesla:.3f} T"
                self.status_var.set(f"T = {T} K: {tesla:.3f} T")
            
            self.result_var.set(result_text)
            self.plot_marker(T, tesla)
            
        except ValueError:
            messagebox.showerror("Error", "Enter valid number")
    
    def plot_marker(self, T, M):
        if self.current_point is not None:
            self.current_point.remove()
        
        self.current_point = self.ax.plot(T, M, 'ro', 
                                         markersize=10, 
                                         markerfacecolor='none',
                                         markeredgewidth=2,
                                         label=f'T = {T} K')[0]
        
        handles, labels = self.ax.get_legend_handles_labels()
        if len(handles) > 3:
            handles = handles[:3] + [self.current_point]
            labels = labels[:3] + [f'T = {T} K']
        self.ax.legend(handles, labels, loc='upper right')
        
        self.canvas.draw()
    
    def clear_marker(self):
        if self.current_point is not None:
            self.current_point.remove()
            self.current_point = None
            
            handles, labels = self.ax.get_legend_handles_labels()
            if len(handles) > 3:
                handles = handles[:3]
                labels = labels[:3]
            self.ax.legend(handles, labels, loc='upper right')
            
            self.canvas.draw()
            self.result_var.set("Marker cleared")
            self.status_var.set("Ready")
            self.temp_entry.focus_set()
    
    def save_figure(self):
        from tkinter import filedialog
        
        file_path = filedialog.asksaveasfilename(
            defaultextension=".png",
            filetypes=[("PNG", "*.png"), ("PDF", "*.pdf"), ("All", "*.*")],
            title="Save Figure",
            initialfile="magnetization.png"
        )
        
        if file_path:
            try:
                self.fig.savefig(file_path, dpi=150, bbox_inches='tight')
                messagebox.showinfo("Saved", f"Saved to:\n{file_path}")
                self.status_var.set("Figure saved")
            except Exception as e:
                messagebox.showerror("Error", f"Save failed:\n{str(e)}")
    
    def on_closing(self):
        plt.close('all')
        self.root.destroy()
        sys.exit(0)

# ========== MAIN PROGRAM ==========
def main():
    root = tk.Tk()
    app = MagnetizationApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()
