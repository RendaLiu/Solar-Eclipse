AU = 1.495979e+8
YEAR = 365.2422 * 24
# 质量取为GM的值
PLANET_MASS = {
    "Sun": 132712440041.279419,
    "Mercury": 22031.868551,
    "Venus": 324858.592000,
    "Earth": 398600.435507,
    "Mars": 42828.375816,
    "Jupiter": 126712764.100000,
    "Saturn": 37940584.841800,
    "Uranus": 5794556.400000,
    "Neptune": 6836527.100580,
    "Moon": 4902.800118,
}
for cb in PLANET_MASS.keys():
    PLANET_MASS[cb] *= (3600**2) / (AU**3)
PLANET_RADII = {
    "Sun": 6.957e5,
    "Mercury": 2.439e3,
    "Venus": 6.052e3,
    "Earth": 6.378e3,
    "Mars": 3.390e3,
    "Jupiter": 7.149e4,
    "Saturn": 6.027e4,
    "Uranus": 2.556e4,
    "Neptune": 2.476e4,
    "Moon": 1.737e3,
}
PLANET_TAG = {
    "Sun": 'sun',
    "Venus": 'venus',
    "Earth": 'earth',
    "Jupiter": 'jupiter barycenter',
    "Moon": 'moon',
}
