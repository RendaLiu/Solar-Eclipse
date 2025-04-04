AU = 1.496e+11
G = 6.67430e-11 * (3600**2) / (1.496e11)**3
YEAR = 365 * 24
PLANET_MASS = {
    "Sun": 1.9885e30,
    "Mercury": 3.301e23,
    "Venus": 4.867e24,
    "Earth": 5.97237e24,
    "Mars": 6.417e23,
    "Jupiter": 1.899e27,
    "Saturn": 5.683e26,
    "Uranus": 8.681e25,
    "Neptune": 1.024e26,
    "Moon": 7.3477e22,
}
PLANET_RADII = {
    "Sun": 6.957e8,
    "Mercury": 2.439e6,
    "Venus": 6.052e6,
    "Earth": 6.378e6,
    "Mars": 3.390e6,
    "Jupiter": 7.149e7,
    "Saturn": 6.027e7,
    "Uranus": 2.556e7,
    "Neptune": 2.476e7,
    "Moon": 1.737e6,
}
PLANET_TAG = {
    "Sun": 'sun',
    "Venus": 'venus',
    "Earth": 'earth',
    "Jupiter": 'jupiter barycenter',
    "Moon": 'moon',
}
