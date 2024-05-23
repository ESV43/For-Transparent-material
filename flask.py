from flask import Flask, request, jsonify
import numpy as np
import pandas as pd
from scipy.optimize import minimize
import matplotlib.pyplot as plt
from io import BytesIO
import base64

app = Flask(__name__)

# Load reflectance data from CSV file
def load_reflectance_data(file):
    data = pd.read_csv(file)
    wavelengths = data['Wavelength (nm)'].values  # in nm
    reflectance = data['Reflectance'].values  # in %
    return wavelengths, reflectance  # Convert percentage to fraction

# Cauchy's model to calculate refractive index
def cauchy_refractive_index(wavelength, A, B):
    return A + B / (wavelength ** 2)

# Fresnel equations to calculate reflectance for a thin film
def fresnel_reflectance(wavelength, n_0, n_f, n_s, d):
    r_01 = (n_0 - n_f) / (n_0 + n_f)
    r_12 = (n_f - n_s) / (n_f + n_s)
    delta = (4 * np.pi * n_f * d) / wavelength
    r_eff = r_01 + r_12 * np.exp(-1j * delta)
    R = np.abs(r_eff) ** 2
    return R

# Objective function to minimize (difference between experimental and theoretical reflectance)
def objective_function(params, wavelengths, experimental_reflectance, n_0, n_s):
    A, B, d = params
    theoretical_reflectance = []
    for wavelength in wavelengths:
        n_f = cauchy_refractive_index(wavelength, A, B)
        R = fresnel
def fresnel_reflectance(wavelength, n_0, n_f, n_s, d):
    r_01 = (n_0 - n_f) / (n_0 + n_f)
    r_12 = (n_f - n_s) / (n_f + n_s)
    delta = (4 * np.pi * n_f * d) / wavelength
    r_eff = r_01 + r_12 * np.exp(-1j * delta)
    R = np.abs(r_eff) ** 2
    return R

# Objective function to minimize (difference between experimental and theoretical reflectance)
def objective_function(params, wavelengths, experimental_reflectance, n_0, n_s):
    A, B, d = params
    theoretical_reflectance = []
    for wavelength in wavelengths:
        n_f = cauchy_refractive_index(wavelength, A, B)
        R = fresnel_reflectance(wavelength, n_0, n_f, n_s, d)
        theoretical_reflectance.append(R)
    theoretical_reflectance = np.array(theoretical_reflectance)
    return np.sum((theoretical_reflectance - experimental_reflectance) ** 2)

# Endpoint to handle the analysis
@app.route('/analyze', methods=['POST'])
def analyze():
    file = request.files['file']
    n_0 = 1  # Refractive index of air
    n_s = float(request.form['n_s'])
    A_init = float(request.form['A_init'])
    B_init = 0.1  # A reasonable starting guess for B
    d_init = 200  # Initial guess for thickness in nm

    # Load the reflectance data
    wavelengths, experimental_reflectance = load_reflectance_data(file)

    # Optimize to find the best parameters
    result = minimize(objective_function, [A_init, B_init, d_init],
                      args=(wavelengths, experimental_reflectance, n_0, n_s),
                      bounds=[(1, 3), (0, 1), (0, 1000)])  # Example bounds

    A, B, d = result.x

    # Calculate theoretical reflectance with the optimized parameters
    theoretical_reflectance = []
    for wavelength in wavelengths:
        n_f = cauchy_refractive_index(wavelength, A, B)
        R = fresnel_reflectance(wavelength, n_0, n_f, n_s, d)
        theoretical_reflectance.append(R)
    theoretical_reflectance = np.array(theoretical_reflectance)

    return jsonify({
        'A': A,
        'B': B,
        'd': d,
        'wavelengths': wavelengths.tolist(),
        'experimental_reflectance': experimental_reflectance.tolist(),
        'theoretical_reflectance': theoretical_reflectance.tolist()
    })

if __name__ == '__main__':
    app.run(debug=True)
