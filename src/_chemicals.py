import biosteam as bst
import thermosteam as tmo

# Chemicals
Oxygen = tmo.Chemical("O2", phase="g")
Nitrogen = tmo.Chemical("N2", phase="g")
Argon = tmo.Chemical("Argon", phase="g")
Carbon = tmo.Chemical("C", phase="s")
Hydrogen = tmo.Chemical("H2", phase="g")
Carbon_Monoxide = tmo.Chemical("CO", phase="g")
Carbon_Dioxide = tmo.Chemical("CO2", phase="g")
Methane = tmo.Chemical("CH4", phase="g")

# Not enough data (Not in Chemicals)
Acetylene = tmo.Chemical("C2H2", phase="g")
Ethylene = tmo.Chemical("Ethylene", phase="g")
Ethane = tmo.Chemical("Ethane", phase="g")
Propane = tmo.Chemical("Propane", phase="g")
Water = tmo.Chemical("Water")
Sulphur = tmo.Chemical("Sulphur")
Carbonyl_Sulfide = tmo.Chemical("Carbonyl Sulfide")
Hydrogen_Sulfide = tmo.Chemical("H2S", phase="g")
Ammonia = tmo.Chemical("Ammonia")
Hydrogen_Chloride = tmo.Chemical("HCl")
Silicon_Dioxide = tmo.Chemical("SiO2", phase="s")
# Calcium_Oxide = tmo.Chemical("CaO", phase="s")
# Calcium_Oxide.copy_models_from(Water, ["Psat"])
Calcium_Oxide = Silicon_Dioxide.copy("CaO")
Benzene = tmo.Chemical("Benzene")
Naphthalene = tmo.Chemical("Naphthalene")

# Not enough data (Not in Chemicals)
Glucose = tmo.Chemical("Glucose", phase="s")
Glucose.Cn.add_model(tmo.functional.rho_to_V(1580, Glucose.MW), top_priority=True)
_cal2joule = 4.184 # auom('cal').conversion_factor('J')
# Hybrid_Poplar = tmo.Chemical(
#     "Hybrid_Pop_NREL",
#     Cp=1.01,
#     rho=1540,
#     HHV=18600*_cal2joule,
#     LHV=17200*_cal2joule,
#     Hf=-23200.01*_cal2joule,
#     default=True,
#     search_db=False,
#     formula="CH1.4O0.8",
#     phase="s"
# )
# Hybrid_Poplar.V.add_model(tmo.functional.rho_to_V(1540, Hybrid_Poplar.MW), top_priority=True)
Hybrid_Poplar = Glucose.copy("Hybrid_Pop_NREL")
Aluminium = tmo.Chemical("Al", phase="s")
Iron = tmo.Chemical("Fe", phase="s")


Sulfer_Dioxide = tmo.Chemical("SO2")
Hydrogen_Cyanide = tmo.Chemical("Hydrogen Cyanide")
Nitric_Oxide = tmo.Chemical("Nitric Oxide")
Methanol = tmo.Chemical("Methanol")
Ethanol = tmo.Chemical("Ethanol")
Isopropanol = tmo.Chemical("Isopropanol")
N_Propanol = tmo.Chemical("N-Propanol")
Isobutanol = tmo.Chemical("Isobutanol")
N_Butanol = tmo.Chemical("N-Butanol")
Pentanol_1 = tmo.Chemical("C5H12O")


C2H4 = tmo.Chemical("C2H4")
C4H8 = tmo.Chemical("C4H8")
C4H10 = tmo.Chemical("C4H10")
C6H12 = tmo.Chemical("C6H12")
C8H16 = tmo.Chemical("C8H16")
C10H20 = tmo.Chemical("C10H20")
C12H24 = tmo.Chemical("C12H24")
C16H32 = tmo.Chemical("C16H32")

C6H14 = tmo.Chemical("C6H14")
C8H18 = tmo.Chemical("C8H18")
C10H22 = tmo.Chemical("C10H22")
C12H26 = tmo.Chemical("C12H26")
C16H34 = tmo.Chemical("C16H34")

Chemicals = [
    Oxygen,
    Nitrogen,
    Argon,
    Carbon,
    Hydrogen,
    Carbon_Monoxide,
    Carbon_Dioxide,
    Methane,
    Acetylene,
    Ethylene,
    Ethane,
    Propane,
    Water,
    Sulphur,
    Carbonyl_Sulfide,
    Hydrogen_Sulfide,
    Ammonia,
    Hydrogen_Chloride,
    Ammonia,
    Hydrogen_Chloride,
    Silicon_Dioxide,
    Calcium_Oxide,
    Benzene,
    Naphthalene,
    Sulfer_Dioxide,
    Hydrogen_Cyanide,
    Nitric_Oxide,
    Methanol,
    Ethanol,
    Isopropanol,
    N_Propanol,
    Isobutanol,
    N_Butanol,
    Pentanol_1,
    Hybrid_Poplar,
    C2H4,
    C4H8,
    C4H10,
    C6H12,
    C8H16,
    C10H20,
    C12H24,
    C16H32,
    C6H14,
    C8H18,
    C10H22,
    C12H26,
    C16H34,
    Aluminium,
    Iron,
]

Water.Cn.l.add_method(Water.Cp("l", 298.15, 101325), Tmin=0, Tmax=373)

Chemical_IDS = []
for i in Chemicals:
    # i.show()
    Chemical_IDS.append(i.ID)


Chemical_IDS
#

bst.preferences.update(
    flow="tonnes/day", T="degC", P="atm", N=100, composition=False
)  # Here you can change units to whichever you
bst.settings.set_thermo(tmo.Chemicals(Chemicals, cache=True))
