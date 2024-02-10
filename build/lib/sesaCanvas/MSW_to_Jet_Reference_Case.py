# %%
# Imports
from matplotlib import pyplot as plt
import biosteam as bst
import thermosteam as tmo
import numpy as np
import pandas as pd
# from steamdrawio import draw 
# from _diagramDrawio import draw_io
np.bool = bool
np.int = int

bst.units.Flash._design = lambda self: None
bst.units.Flash.no_vessel_needed = True

# %%
from _chemicals import *
#%%
# for c in Chemicals:
#     print(c.ID)
#     print(c.get_missing_properties())
# Hybrid_Poplar.Psat.Tmax

#%%
# add natural gas utility
lp_steam = bst.UtilityAgent("low_pressure_steam", Water=1, T=114 + 273.15, P=4 * 101325, 
    T_limit=368.15 + 273.15, 
    heat_transfer_price=2.843e-6, # $3/mmbtu
    heat_transfer_efficiency=0.95
    )
mp_steam = bst.UtilityAgent("medium_pressure_steam", Water=1, T=250 + 273.15, P=12 * 101325, 
    T_limit=368.15 + 273.15,
    heat_transfer_price=2.843e-6, # $3/mmbtu
    heat_transfer_efficiency=0.95)
hp_steam = bst.UtilityAgent("high_pressure_steam", Water=1, T=400 + 273.15, P=45 * 101325,  
    T_limit=368.15 + 273.15,
    heat_transfer_price=2.843e-6, # $3/mmbtu
    heat_transfer_efficiency=0.95)
natural_gas = bst.UtilityAgent("natural_gas", CO2=1, T=1200+273, P=101325, 
    T_limit=1400 + 273.15,
    heat_transfer_price=2.843e-6, # $3/mmbtu
    heat_transfer_efficiency=0.95)

# gas.Hvap = Water.Hvap
bst.settings.heating_agents.clear()
bst.settings.heating_agents.extend([lp_steam, mp_steam, hp_steam, natural_gas])
#%%

"""
Warning: Temperature and Pressure units are in 
F and Psia, but code runs in K and Pascal
"""

"""
HX = Heat Exchanger
C = Compressor
S = Stream
T = Tank
CO = Connector (Circle)
U = Unknown Unit
Spl = Splitter
X = Unit with square with X
Tri = Triangle that has multiple connections and 1 output
Tur = Turbine
Div = Diverger (Opposite of Tri/1 input with multiple outputs)

"""
bst.main_flowsheet.clear()
# 200 Biomass preparation and 300 Gasification
with bst.System("Pretreatment") as pretreatment:
#
    # In: Air (S_100)
    S_100 = bst.Stream(
        "S_100",
        O2=97654.13,
        N2=318713.3,
        Argon=5435.613,
        CO2=212.2069,
        Water=8397.746,
        units="lb/hr",
        T=(90 - 32) * 5 / 9 + 273.15,
        P=14.696 * 6894.76,
    )

    #
    # Air: Units
    C_100 = bst.units.compressor.IsentropicCompressor("C_100", outs=["S_110"], P=22 * 6894.76)
    S_100 - 0 - C_100
    # C_100

    #
    # Biomass
    # Error with Hybrid_Pop_NREL


    # Waste

    #
    # BFW
    S_1931 = bst.Stream(
        "S_1931",
        Water=10675.5,
        units="lb/hr",
        T=(237 - 32) * 5 / 9 + 273.15,
        P=860 * 6894.76,
    )
    # S_1931.show()

    #
    # BFW: Units
    HX_251 = bst.units.heat_exchange.HXprocess("HX_251", outs=["S_361", "S_1932"])
    S_1931 - HX_251 - 0
    # HX_251

    # Outs: S_791 (TO STM DRUM)
    CO_790 = bst.units.MixTank("CO_790", outs=["S_791"], tau=1.5/60)
    (HX_251 - 1) - CO_790

    # Not sure what unit to use
    # Outs: S_210 (VENT)
    T_200 = bst.units.Mixer("T_200", outs=["S_210i"])

    # Hybrid_Pop_NREL = 183718.6,
    Waste = bst.Stream(
        "Waste", 
        Hybrid_Pop_NREL=2000,
        Al=0.088*2000*0.5,
        Fe=0.088*2000*0.5,
        Water=2000*0.25, units="tonnes/day", T=(60 - 32) * 5 / 9 + 273.15, P=25 * 6894.76
    )

    MECHSEP = bst.units.MixTank("MECHSEP", outs=["Wastei"], tau=2.5)
    Waste - 0- MECHSEP 

    MECHSP = bst.units.Splitter("MECHSP", outs=["Wastei2", "Wastei3"], split={
        "Al": 1,
        "Fe": 1,
        "Hybrid_Pop_NREL": 0.05,
        })
    MECHSEP - MECHSP

    AlSP = bst.units.Splitter("AlSP", outs=["oAluminium", "oIron"], split={
        "Al": 1,
        "Fe": 0,
    })
    MECHSP - 0 - 0- AlSP


    (MECHSP-1, HX_251 - 0) - T_200
    T_210 = bst.units.Flash(
        "T_210", outs=["S_210", "S_220"], T=(304 - 32) * 5 / 9 + 273.15, P=101325
    )
    T_200 - 0 - T_210

    # T_200

with bst.System("Gasification") as gasification:
    #
    # Steam
    S_1910 = bst.Stream(
        "S_1910",
        Water=73119.59,
        units="lb/hr",
        T=(260 - 32) * 5 / 9 + 273.15,
        P=25 * 6894.76,
    )

    X_300 = bst.units.MixTank("X_300", outs="S_300", tau=1.5/60)

    S_1910 - X_300 - 0

    # X_300


    #
    # BCL Gasifier
    M_301 = bst.units.MixTank("M_301", outs="S_302", tau=1.5/60)

    #
    # Gasifier
    # Unit 305
    Gasifier = bst.units.MixTank("Gasifier", outs="S_303", tau=5/60)
    (M_301) - Gasifier

    def spec_gasification():
        Gasifier._run()
        yields = {"O2":0.028,
            "N2":0,
            "Argon":0,
            "C":0.150,
            "H2":0.030,
            "CO":0.425,
            "CO2":0.202,
            "CH4":0.089,
            "C2H2":0.004,
            "Ethylene":0.044,
            "Ethane":0.003,
            "Propane":0,
            "Water":0,
            "Sulphur":0,
            "Carbonyl Sulfide":0,
            "H2S":0.001,
            "Ammonia":0.002,
            "HCl":0,
            "SiO2":0,
            "Benzene":0.003,
            "Naphthalene":0.010}
        for i in yields:
            if type(Gasifier.outs[0]) == tmo.Stream:
                Gasifier.outs[0].imass[i] += yields[i] * Gasifier.ins[0].get_flow("kg/hr", "Hybrid_Pop_NREL")
                Gasifier.outs[0].imass[ "Hybrid_Pop_NREL"] = (1-sum(yields.values())) * Gasifier.ins[0].get_flow("kg/hr", "Hybrid_Pop_NREL")
            else:
                Gasifier.outs[0].imass["g", i] += yields[i] * Gasifier.ins[0].get_flow("kg/hr", "Hybrid_Pop_NREL")
                Gasifier.outs[0].imass["l", "Hybrid_Pop_NREL"] = (1-sum(yields.values())) * Gasifier.ins[0].get_flow("kg/hr", "Hybrid_Pop_NREL")
    Gasifier.add_specification(spec_gasification)

    Spl_310 = bst.units.Flash("Spl_310", outs=["S_320", "S_312"], T=(1598-32) * 5 / 9 + 273.15, P=22/14.7*101325)
    (Gasifier) - Spl_310
    # Spl_310

    #
    M_316 = bst.units.Mixer("M_316", outs="S_318")
    (C_100 - 0, Spl_310 - 1) - M_316
    # M_316

    # Unit 317
    Combustor = bst.units.MixTank("Combustor", outs="S_319", tau=1.5/60)
    M_316 - Combustor
    # Combustor
    def spec_combustor():
        Combustor._run()
        rxn = tmo.reaction.Reaction(
            "C + O2 -> CO2",
            reactant = "C",
            X = 0.95,
            basis="wt"
        )
        rxn(Combustor.outs[0])
        Combustor.outs[0].T = 950+273.15
    Combustor.add_specification(spec_combustor)

    Spl_315 = bst.units.Splitter("Spl_315", outs=["S_316", "S_350"], split={
        "SiO2": 1.0,
        "CaO": 1.0,
        })
    Combustor - Spl_315
    # Spl_315-0-M_301
    (T_210 - 1, X_300 - 0, Spl_315 - 0) - M_301
    # Spl_315
    # M_301

with bst.System("Syngas_Cleanup") as syngas_cleanup:
    #
    # Quench Water
    S_353 = bst.Stream(
        "S_353", Water=750.0001, T=(60 - 32) * 5 / 9 + 273.15, P=14.7 * 6894.76
    )

    # CWS
    S_1834 = bst.Stream(
        "S_1834", Water=28811.37, T=(90 - 32) * 5 / 9 + 273.15, P=65 * 6894.76
    )

    #
    Spl_350 = bst.units.Splitter("Spl_350", outs=["S_360", "S_351"], split={
        "SiO2": 0.0,
        "CaO": 0.0,
        "C": 0.0,
        "O2": 1.0,
        "N2": 1.0,
        "Argon": 1.0,
        "CO2": 1.0,
        "Water": 1.0,
        })
    (Spl_315 - 1) - Spl_350
    # Spl_350

    #

    # Outs: S_1835
    U_352 = bst.units.heat_exchange.HXprocess("U_352", outs=["S_1835", "S_352"])
    (S_1834, Spl_350 - 1) - U_352
    # U_352

    #
    # Outs: S_354 (WET ASH)
    M_353 = bst.units.MixTank("M_353", outs="S_354")
    (U_352 - 1, S_353) - M_353
    # M_353

    HX_251.ins[1] = Spl_350.outs[0]

    #
    # Tar Reformer
    # Unit 321
    Tar_Reformer = bst.units.MixTank("Tar_Reformer", outs="S_329", tau=1.5/60)

    def spec_tar_reformer():
        # ToDo: see Spath, et al., (2005) for more details
        Tar_Reformer._run()
        yields = {"H2":2.004061938,
            "CO":1.261356013,
            "CO2":1.000000269,
            "CH4":0.800000123,
            "C2H2":0.500000071,
            "Ethylene":0.499999938,
            "Ethane":0.100000086,
            "Propane":1,
            "Water":0.8596849,
            "Sulphur":1,
            "Carbonyl Sulfide":1,
            "H2S":1,
            "Ammonia":0.300000141,
            "HCl":1,
            "SiO2":1,
            "CaO":1,
            "Benzene":0.300000063,
            "Naphthalene":0.050000026}
        
        for i in yields:
            Tar_Reformer.outs[0].imass[i] = yields[i] * Tar_Reformer.ins[0].imass[i]
    Tar_Reformer.add_specification(spec_tar_reformer)
        

    (Spl_310 - 0) - Tar_Reformer

    # Tar_Reformer

    HX_330 = bst.units.heat_exchange.HXprocess("HX_330", outs=["S_324", "S_1938"])
    (Tar_Reformer) - HX_330
    # HX_330

    # Outs: S_792 (To STM DRUM)
    CO_792 = bst.units.MixTank("CO_792", outs="S_792", tau=1.5/60)
    # (HX_330-1)-CO_792


    HX_335 = bst.units.heat_exchange.HXprocess("HX_335", outs=["S_325", "S_1936"])

    # BFW
    S_1935 = bst.Stream(
        "S_1935",
        Water=130000,
        units="lb/hr",
        T=(237 - 32) * 5 / 9 + 273.15,
        P=860 * 6894.76,
    )

    (HX_330 - 0, S_1935) - HX_335
    HX_330.ins[1] = HX_335.outs[1]

    # HX_335

    #
    # Scrubber

    # Unit 340
    sm1 = bst.Stream("sm1")
    sm2 = bst.Stream("sm2")
    Scrubber_mixer = bst.units.Mixer("Scrubber_mixer", ins=(sm1, sm2), outs="S_341")
    Scrubber = bst.units.Flash("Scrubber", outs=["S_345", "S_1701"], T=(118.3 - 32) * 5 / 9 + 273.15, P=15/14.7*101325)
    (HX_335 - 0) - 0 - Scrubber_mixer
    Scrubber_mixer - Scrubber
    # Scrubber

with bst.System("Sulfur_Cleanup") as sulfur_cleanup:

    # Outs: S_1702 (TO WWT)
    Spl_16 = bst.units.Splitter("Spl_16", outs=["S_1702", "S_1703"], split=0.01)
    (Scrubber - 1) - Spl_16
    # Spl_16

    # CWS
    S_1830 = bst.Stream(
        "S_1830", Water=3819701, units="lb/hr", T=(90 - 32) * 5 / 9 + 273.15, P=60 * 6894.76
    )

    # Outs: S_1831
    HX_341 = bst.units.heat_exchange.HXprocess("HX_341", outs=["S_341", "S_1831"])
    (Spl_16 - 1, S_1830) - HX_341
    # HX_341

    # From V4
    S_343 = bst.Stream(
        "S_343",
        Water=37319.66,
        units="lb/hr",
        T=(110 - 32) * 5 / 9 + 273.15,
        P=415 * 6894.76,
    )

    M_342 = bst.units.MixTank("M_342", outs="S_344", tau=1.5/60)
    (HX_341 - 0, S_343) - M_342
    # M_342

    Scrubber_mixer.ins[1] = M_342.outs[0]

with bst.System("Syngas_compression") as syngas_compression:
    #
    """400 Syngas Compression and Purification"""

    # RAW SYNGAS COMPRESSION
    # Compressors are Mixtanks
    C_410 = bst.units.Splitter("C_410", outs=["S_1741", "S_412"], split={
        "Water": 0.0
        })
    HX_411 = bst.units.heat_exchange.HXutility(
        "HX_411", outs="S_413", T=(140 - 32) * 5 / 9 + 273.15
    )
    C_412 = bst.units.Splitter("C_412", outs=["S_1742", "S_416"], split={
        "Water": 0.0
        })
    HX_413 = bst.units.heat_exchange.HXutility(
        "HX_413", outs="S_417", T=(140 - 32) * 5 / 9 + 273.15
    )
    M_1740 = bst.units.MixTank("M_1740", outs="S_1743", tau=1.5/60)
    C_414 = bst.units.Splitter("C_414", outs=["S_1744", "S_420"], split={
        "Water": 0.2
        })
    HX_415 = bst.units.heat_exchange.HXutility(
        "HX_415", outs="S_421", T=(140 - 32) * 5 / 9 + 273.15
    )
    C_416 = bst.units.Splitter("C_416", outs=["S_1746", "S_422"], split={
        "Water": 0.4
        })
    HX_417 = bst.units.heat_exchange.HXutility(
        "HX_417", outs="S_423", T=(140 - 32) * 5 / 9 + 273.15
    )
    M_1741 = bst.units.MixTank("M_1741", outs="S_1745", tau=1.5/60)
    M_1742 = bst.units.MixTank("M_1742", outs="S_1747", tau=1.5/60)
    C_418 = bst.units.Splitter("C_418", outs=["S_1748", "S_424"], split={
        "Water": 0.3
        })
    HX_419 = bst.units.heat_exchange.HXutility(
        "HX_419", outs="S_425", T=(140 - 32) * 5 / 9 + 273.15
    )
    M_1743 = bst.units.MixTank("M_1743", outs="S_1749", tau=1.5/60)

    # Connections
    (Scrubber - 0) - (C_410)
    (C_410 - 0) - (M_1740)
    HX_411 - C_412
    (C_412 - 1) - HX_413
    (C_410 - 1, C_412 - 0) - HX_411
    HX_413 - C_414
    (C_414 - 1) - (HX_415)
    HX_415 - C_416
    (C_416 - 1) - HX_417
    (M_1740 - 0, C_414 - 0) - M_1741
    (M_1741 - 0, C_416 - 0) - M_1742
    HX_417 - C_418
    (C_418 - 1) - HX_419
    (M_1742 - 0, C_418 - 0) - M_1743


    #
    # In: CWS (S_1840)
    S_1840 = bst.Stream(
        "S_1840",
        Water=138253.4,
        units="lb/hr",
        T=(90 - 32) * 5 / 9 + 273.15,
        P=65 * 6894.76,
    )

    HX_420 = bst.units.heat_exchange.HXprocess("HX_420", outs=["S_426", "S_1841"])
    (HX_419 - 0, S_1840) - HX_420
    # HX_420

    # Unit 429
    KO_POT = bst.units.Splitter("KO_POT", outs=["S_428", "S_429"], split=0.5)
    M_1744 = bst.units.MixTank("M_1744", outs="S_1750", tau=1.5/60)
    (HX_420 - 0) - KO_POT
    (KO_POT - 0, M_1743 - 0) - M_1744

    # In: Steam (S_1945)
    S_1945 = bst.Stream(
        "S_1945",
        Water=663.7736,
        units="lb/hr",
        T=(366.3939 - 32) * 5 / 9 + 273.15,
        P=35 * 6894.76,
    )

    HX_431 = bst.units.heat_exchange.HXprocess("HX_431", outs=["S_430", "S_1946"])
    (KO_POT - 1, S_1945) - HX_431

    X_6 = bst.units.MixTank("X_6", outs="S_9946", tau=1.5/60)
    (HX_431 - 1) - X_6

    # Unit 430
    LO_CAT = bst.units.Splitter("LO_CAT", outs=["S_431", "S_432"], split=0.0)
    CO_7 = bst.units.MixTank("CO_7", outs="S_4432", tau=1.5/60)
    (HX_431 - 0) - LO_CAT
    (LO_CAT - 1) - CO_7

    # HX_9496 = bst.units.heat_exchange.HXutility('HX_9496', outs = 'S_433', T = (707-32)*5/9+273.15)
    HX_9496 = bst.units.MixTank(
        "HX_9496", outs="S_433", tau=1.5/60
    )  # ToDo: Switch back to heat exchange later
    HX_9496.outs[0].T = (707 - 32) * 5 / 9 + 273.15
    (CO_7 - 0) - HX_9496

    # Unit 435
    ZnO_BED = bst.units.Splitter("ZnO_BED", outs=["S_434", "S_435"], split={
        "H2S": 0.0,
        })

    (HX_9496 - 0) - ZnO_BED

    # In: Steam (S_1940)
    S_1940 = bst.Stream(
        "S_1940",
        Water=135112.5,
        units="lb/hr",
        T=(715.0002 - 32) * 5 / 9 + 273.15,
        P=450 * 6894.76,
    )

    # In: CO2
    S_454 = bst.Stream(
        "S_454", CO2=158436, units="lb/hr", T=(60 - 32) * 5 / 9 + 273.15, P=22 * 6894.76
    )

    Tur_452 = bst.units.MixTank("Tur_452", outs="S_455", tau=1.5/60)
    HX_9452 = bst.units.heat_exchange.HXutility(
        "HX_9452", outs="S_456", T=(150 - 32) * 5 / 9 + 273.15
    )
    Tur_9463 = bst.units.MixTank("Tur_9463", outs="S_457", tau=1.5/60)
    HX_9454 = bst.units.heat_exchange.HXutility(
        "HX_9454", outs="S_458", T=(150 - 32) * 5 / 9 + 273.15
    )
    Tur_9455 = bst.units.MixTank("Tur_9455", outs="S_459", tau=1.5/60)

    S_454 - Tur_452 - HX_9452 - Tur_9463 - HX_9454 - Tur_9455

    # Temporary Stream made to rbe replaced by S_552
    S_temp = bst.Stream("S_temp")

    # Triangle located in 400 Syngas Compression and Purification
    Tri_400 = bst.units.MixTank("Tri_400", outs="S_440", tau=1.5/60)
    # Need connection from S_552 which is in 500 Mixed Alcohol Synthesis
    (ZnO_BED - 1, Tur_9455 - 0, S_1940, S_temp) - Tri_400


    HX_494 = bst.units.heat_exchange.HXprocess("HX_494", outs=["S_441", "S_496"])
    (Tri_400 - 0) - HX_494


    # Toward Flue Gas
    HX_495 = bst.units.heat_exchange.HXprocess("HX_495", outs=["S_1942", "S_4495"])

    # In: Stream (S_1941)
    S_1941 = bst.Stream(
        "S_1941",
        Water=126493.8,
        units="lb/hr",
        T=(525.2153 - 32) * 5 / 9 + 273.15,
        P=850 * 6894.76,
    )

    (HX_494 - 1, S_1941) - HX_495


    HX_496 = bst.units.heat_exchange.HXprocess("HX_496", outs=["S_497", "S_9433"])

    # In: ZnO Preheat (S_9432)
    S_9432 = bst.Stream("S_9432")

    (HX_495 - 1, S_9432) - HX_496


    HX_498 = bst.units.heat_exchange.HXprocess("HX_498", outs=["S_498", "S_1971"])

    # In: Stream (S_1941)
    S_1970 = bst.Stream("S_1970")

    (HX_496 - 1, S_1970) - HX_498

    C_497 = bst.units.compressor.Compressor("C_497", outs="S_499", P=15 * 6894.76)

    (HX_498 - 0) - C_497

    # Outs: Turbine (S_toTurbine)
    CO_2 = bst.units.MixTank("CO_2", outs="S_toTurbine", tau=1.5/60)

    # Outs: Deareator (S_769)
    CO_8 = bst.units.MixTank("CO_8", outs="S_769", tau=1.5/60)

    (HX_495 - 0) - CO_2
    (HX_498 - 1) - CO_8

    # Reformer

    # Unit 440
    Reformer = bst.units.MixTank("Reformer", outs=("S_442"), tau=1.5/60)
    (HX_494 - 0) - 0 - Reformer
    def spec_reformer():
        Reformer._run()
        # Steam Methane reforming
        # CH4 + H2O -> CO + 3H2
        rxn = tmo.reaction.Reaction(
            'CH4 + H2O -> CO + 3H2',
            reactant = 'CH4',
            X = 14917/27172
        )
        rxn.basis = "wt"
        if type(Reformer.outs[0]) == tmo.Stream:
            rxn(Reformer.outs[0])
        else:
            rxn(Reformer.outs[0]['g'])
        Reformer.outs[0].T=(930-32)*5/9+273.15
        Reformer.outs[0].P=430/14.7*6894.76
    Reformer.add_specification(spec_reformer)

    # In: SAT'D STM (S_1943)
    S_1943 = bst.Stream(
        "S_1943",
        Water=435348,
        units="lb/hr",
        T=(525.2153 - 32) * 5 / 9 + 273.15,
        P=850 * 6894.76,
    )

    HX_442 = bst.units.heat_exchange.HXprocess("HX_442", outs=["S_445", "S_1944"])
    (Reformer - 0, S_1943) - HX_442

    # Outs: Turbine (S_794)
    CO_794 = bst.units.MixTank("CO_794", outs="S_794", tau=1.5/60)
    (HX_442 - 1) - CO_794

    # In: BFW (S_1950)
    S_1950 = bst.Stream(
        "S_1950",
        Water=268328.3,
        units="lb/hr",
        T=(237 - 32) * 5 / 9 + 273.15,
        P=860 * 6894.76,
    )

    HX_444 = bst.units.heat_exchange.HXprocess("HX_444", outs=["S_447", "S_1951"])
    (HX_442 - 0, S_1950) - HX_444


    U_445 = bst.units.MixTank("U_445", outs="S_448", tau=1.5/60)
    (HX_444 - 0) - U_445

    # In: CWS (S_1842)
    S_1842 = bst.Stream(
        "S_1842", Water=738555, units="lb/hr", T=(90 - 32) * 5 / 9 + 273.15, P=65 * 6894.76
    )

    HX_447 = bst.units.heat_exchange.HXprocess("HX_447", outs=["S_449", "S_1843"])
    (U_445 - 0, S_1842) - HX_447

    # Out: Scrubber (S_1751)
    T_449 = bst.units.Flash("T_449", outs=["S_450", "S_1751"], 
                            # T=(110-32)*5/9+273.15, 
                            Q=0,
                            P=427.5/14.7*101325)
    (HX_447 - 0) - T_449

    # Unit 450
    AMINE_UNIT = bst.units.Splitter("AMINE_UNIT", outs=["S_452", "S_451"], split={
        "CO2": 0.1,
        "Water": 0
        })
    (T_449 - 0) - AMINE_UNIT

    #

    # Out: CO2 (S_453)
    V_451 = bst.units.heat_exchange.HXutility(
        "V_451", outs="S_453", T=(150 - 32) * 5 / 9 + 273.15
    )
    (AMINE_UNIT - 0) - V_451

    #
    # CLEAN SYNGAS COMPRESSION
    Tur_470 = bst.units.MixTank("Tur_470", outs="S_471", tau=1.5/60)
    HX_471 = bst.units.heat_exchange.HXutility(
        "HX_471", outs="S_472", T=(150 - 32) * 5 / 9 + 273.15
    )
    Tur_472 = bst.units.MixTank("Tur_472", outs="S_473", tau=1.5/60)
    HX_473 = bst.units.heat_exchange.HXutility(
        "HX_473", outs="S_474", T=(150 - 32) * 5 / 9 + 273.15
    )
    Tur_474 = bst.units.MixTank("Tur_474", outs="S_477", tau=1.5/60)

    (AMINE_UNIT - 1) - Tur_470 - HX_471 - Tur_472 - HX_473 - Tur_474


    #
    # In: AIR (S_490)
    S_490 = bst.Stream("S_490")

    Tur_490 = bst.units.MixTank("Tur_490", outs="S_491", tau=1.5/60)
    S_490 - Tur_490

    Tri_491 = bst.units.MixTank("Tri_491", outs="S_493", tau=1.5/60)

    # Temporary Stream for Tri_491 to be replaced by S_1602
    S_temp2 = bst.Stream("S_temp2")

    (Tur_490 - 0, S_temp2) - Tri_491

    # Unit 492
    Burners = bst.units.MixTank("Burners", outs="S_494", tau=1.5/60)

    X_493 = bst.units.MixTank("X_493", outs="S_495", tau=1.5/60)
    Tri_491 - Burners - X_493
    HX_494.ins[1] = X_493.outs[0]

with bst.System("Mixed_Alcohol_Synthesis") as mixed_alcohol_synthesis:
    #
    """ 500 Mixed Alcohol Synthesis and
        600 Mixed Alcohol Separations     """

    # In BFW (S_1952)
    S_1952 = bst.Stream(
        "S_1952",
        Water=164146,
        units="lb/hr",
        T=(237 - 32) * 5 / 9 + 273.15,
        P=860 * 6894.76,
    )

    HX_501 = bst.units.heat_exchange.HXutility(
        "HX_501", outs="S_1953", T=(526.5776 - 32) * 5 / 9 + 273.15
    )
    HX_501._design = lambda: None  # ToDo: Fix this later
    X_502 = bst.units.MixTank("X_502", outs="S_1954", tau=1.5/60)

    # Out: To 1945 (S_737)
    CO_737 = bst.units.MixTank("CO_737", outs="S_737", tau=1.5/60)

    S_1952 - HX_501 - X_502 - CO_737

    #
    # Mixed Alcohol Synthesis Reactor
    M_562 = bst.units.MixTank("M_562", outs="S_512", tau=1.5/60) 
    T_500 = bst.units.MixTank("T_500", outs="S_516", tau=1.5/60) # Mixed Alcohol Reactor

    """
    2 CO + 4 H2 → C2 H6 + H2O 0.5%
    CO + H2 → Methanol 4.1%
    2 CO + 4 H2 → Ethanol + H2 O 11.4%
    3 CO + 6 H2 → Propanol + 2 H 2 O 3%
    4 CO + 8 H2 → n-Butanol + 3 H 2 O 1%
    5 CO + 10 H2 → n-Pentanol + 4H2 O 0.5%
    Methanol Recycle Reactions Mole % Recycled Methanol Conversion
    Methanol + CO + 2 H2 → Ethanol + H2 O 58%
    Methanol + 2 CO + 4H2 → Propanol + 2 H2 O 7%
    Methanol + 3 CO + 6 H2 → n-Butanol + 3 H 2 O 4.5%
    Methanol + 4 CO + 8 H2 → n-Pentanol + 4H2 O 2%
    """


    def spec_alcohol_synthesis():
        T_500._run()
        rxns = tmo.ParallelReaction([
            tmo.Reaction("CO+H2O -> CO2 + H2", reactant="CO", X=0.13),
            tmo.Reaction("CO+3H2 -> CH4 + H2O", reactant="CO", X=0.045),
            tmo.Reaction("2CO + 4H2 -> C2H6 + H2O", reactant="CO", X=0.005),
            tmo.Reaction("CO + H2 -> Methanol", reactant="CO", X=0.041),
            tmo.Reaction("2CO + 4H2 -> Ethanol + H2O", reactant="CO", X=0.114),
            tmo.Reaction("3CO + 6H2 -> N-Propanol + 2H2O", reactant="CO", X=0.03),
            tmo.Reaction("4CO + 8H2 -> N-Butanol + 3H2O", reactant="CO", X=0.01),
            tmo.Reaction("5CO + 10H2 -> C5H12O + 4H2O", reactant="CO", X=0.005),
            tmo.Reaction("Methanol + CO + 2H2 -> Ethanol + H2O", reactant="Methanol", X=0.58),
            tmo.Reaction("Methanol + 2CO + 4H2 -> N-Propanol + 2H2O", reactant="Methanol", X=0.07),
            tmo.Reaction("Methanol + 3CO + 6H2 -> N-Butanol + 3H2O", reactant="Methanol", X=0.045),
            tmo.Reaction("Methanol + 4CO + 8H2 -> C5H12O + 4H2O", reactant="Methanol", X=0.02),
            ])
        rxns(T_500.outs[0])
    T_500.add_specification(spec_alcohol_synthesis)

    X_503 = bst.units.MixTank("X_503", outs="S_517", tau=1.5/60)
    M_562 - T_500 - X_503

    HX_505 = bst.units.heat_exchange.HXprocess("HX_505", outs=["S_510", "S_518"])
    def spec_hx_505():
        try:
            HX_505._run()
        except:
            pass
    HX_505.add_specification(spec_hx_505)

    (Tur_474 - 0, X_503 - 0) - HX_505
    M_562.ins[0] = HX_505.outs[0]

    U_506 = bst.units.MixTank("U_506", outs="S_519", tau=1.5/60)
    (HX_505 - 1) - U_506

    # In: CWS (S_1850)
    S_1850 = bst.Stream(
        "S_1850", Water=364879, units="lb/hr", T=(90 - 32) * 5 / 9 + 273.15, P=65 * 6894.76
    )

    # Outs: S_1851
    HX_508 = bst.units.heat_exchange.HXprocess("HX_508", outs=["S_520", "S_1851"])
    (U_506 - 0, S_1850) - HX_508

    # Spl_511 = bst.units.Flash("Spl_511", outs=["S_523", "S_524"], T=(110 - 32) * 5 / 9 + 273.15, P=1975/14.7*101325)
    Spl_511 = bst.units.Splitter("Spl_511", outs=["S_523", "S_524"], split={
        "O2": 1,
        "N2": 1,
        "CO": 1,
        "CO2": 1,
        "H2": 1,
        "CH4": 1,
        "C2H2": 1,
        "Ethylene": 1,
        "Ethane": 1,
        "Water": 0.05,
        "Methanol": 0.05,
        "Ethanol": 0.05,
        "N-Propanol": 0.05,
        "N-Butanol": 0.01,
        "C5H12O": 0.01,
        })
    Spl_549 = bst.units.Splitter("Spl_549", outs=["S_551", "S_552"],  split=0.4)
    (HX_508 - 0) - Spl_511
    (Spl_511 - 0) - Spl_549

    Tri_400.ins[3] = Spl_549.outs[1]

    Spl_513 = bst.units.Splitter("Spl_513", outs=["S_528", "S_530"], split=1)

    # Unit 601
    Lights = bst.units.distillation.BinaryDistillation("Lights", outs=["S_601", "S_605"], 
                                    LHK=("CO2", "Ethanol"),
                                    k=2,
                                    y_top=0.95,
                                    x_bot=0.05,)
    Lights._summary = lambda: None

    def spec_lights():
        Lights.design_results["Reflux"] = 2
        if Lights.ins[0].F_mass < 1:
            return
        try:
            Lights._run()
        except:
            pass
    Lights.add_specification(spec_lights)

    (Spl_511 - 1) - Spl_513
    (Spl_513 - 0) - Lights

    #
    # Mol Sieve
    HX_621 = bst.units.heat_exchange.HXprocess("HX_621", outs="S_621")
    X_1 = bst.units.MixTank("X_1", outs="S_9621", tau=1.5/60)
    (Lights - 1) - HX_621
    (HX_621 - 0) - X_1

    # Outs: WWT (S_625)
    Spl_620 = bst.units.Splitter("Spl_620", outs=["S_625", "S_622"], split={
        "Water": 1,
        }) # molecular sieve
    (X_1 - 0) - 0-Spl_620

    # In: S_1861
    S_1861 = bst.Stream(
        "S_1861", Water=173765, units="lb/hr", T=(90 - 32) * 5 / 9 + 273.15, P=60 * 6894.76
    )

    # Out: S_1862
    HX_622 = bst.units.heat_exchange.HXprocess("HX_622", outs=["S_623", "S_1862"])
    (Spl_620 - 1, S_1861) - HX_622

    # Unit 610
    MeOH_COLUMN = bst.units.ShortcutColumn("MeOH_COLUMN", outs=["S_610", "S_620"], 
                                        LHK=("Methanol", "Ethanol"),
                                            k=1.5,
                                            Lr=0.90,
                                            Hr=0.90,)
    def spec_meoh_column():
        try:
            MeOH_COLUMN._run()
        except:
            pass
    MeOH_COLUMN.add_specification(spec_meoh_column)

    (HX_622 - 0) - MeOH_COLUMN

    Spl_611 = bst.units.Splitter("Spl_611", outs=["S_611", "S_612"], split=0.1)
    (MeOH_COLUMN - 0) - Spl_611

    # No Unit Number
    Fuel_GAS = bst.units.MixTank("Fuel_Gas", outs="S_1602", tau=1.5/60)
    (Spl_549 - 0, Spl_513 - 1, Lights - 0, Spl_611 - 0) - Fuel_GAS

    Tri_491.ins[1] = Fuel_GAS.outs[0]

    # Unit 630
    # Outs: EtOH (S_631) and PrOH+ (S_636)
    EtOH_COLUMN = bst.units.ShortcutColumn("EtOH_COLUMN", outs=["S_631", "oPropanol"], 
                                        LHK=("Ethanol", "N-Propanol"),
                                            k=1.5,
                                            Lr=0.90,
                                            Hr=0.90,)

    out_propanol = EtOH_COLUMN.outs[1]
    def spec_etoh_column():
        try:
            EtOH_COLUMN._run()
        except:
            pass
    EtOH_COLUMN.add_specification(spec_etoh_column)

    (MeOH_COLUMN - 1) - EtOH_COLUMN

    # No Unit Number (in 600 Mixed Alcohol Separations)
    HX_600 = bst.units.heat_exchange.HXutility(
        "HX_600", outs="S_615", T=(152 - 32) * 5 / 9 + 273.15
    )
    (Spl_611 - 1) - HX_600

    #
    # Unit 615
    MeOH_RECYCLE = bst.units.Pump("MeOH_RECYCLE", outs="S_560")
    HX_600 - MeOH_RECYCLE

    # In: HP STM
    S_1955 = bst.Stream(
        "S_1955", Water=435348, T=(1000 - 32) * 5 / 9 + 273.15, P=850 * 6894.76
    )  # ToDo: Change to steam later

    # Unit 559
    # Out: S_1956
    VAPORIZER = bst.units.heat_exchange.HXprocess("VAPORIZER", outs=["S_561", "S_1956"])
    (MeOH_RECYCLE - 0, S_1955) - VAPORIZER

    M_562.ins[1] = VAPORIZER.outs[0]


    """ 700 STEAM SYSTEM """

    # In: FLUEGAS
    S_701 = bst.Stream(
        "S_701",
        Water=10675.7,
        units="lb/hr",
        T=(526.5776 - 32) * 5 / 9 + 273.15,
        P=860 * 6894.76,
    )

    # In: TAR REF
    S_702 = bst.Stream(
        "S_702",
        Water=130000,
        units="lb/hr",
        T=(526.5776 - 32) * 5 / 9 + 273.15,
        P=860 * 6894.76,
    )

    # In: SYNTH
    S_703 = bst.Stream(
        "S_703",
        Water=164146,
        units="lb/hr",
        T=(526.5776 - 32) * 5 / 9 + 273.15,
        P=860 * 6894.76,
    )

    # No Unit Number (in 700 STEAM SYSTEM)
    Tri_700 = bst.units.MixTank("Tri_700", outs="S_704", tau=1.5/60)
    (S_701, S_702, S_703, HX_444 - 1) - Tri_700

    # Unit 700
    STEAM_DRUM = bst.units.Splitter("STEAM_DRUM", outs=["S_706", "S_711"], split=0.5)
    Tri_700 - STEAM_DRUM

    #
    # No Unit Number (in 700 STEAM SYSTEM)
    # Should changed to unit later
    # Out: STM REF (S_707), SR RECUP (S_708)
    Div_700 = bst.units.Duplicator("Div_700", outs=["S_707", "S_708", "S_709"])
    (STEAM_DRUM - 0) - Div_700


    # In: STM REF
    S_720 = bst.Stream(
        "S_720",
        Water=435348,
        units="lb/hr",
        T=(1000 - 32) * 5 / 9 + 273.15,
        P=850 * 6894.76,
    )

    # In: SR REC
    S_721 = bst.Stream(
        "S_721",
        Water=126493.8,
        units="lb/hr",
        T=(1000 - 32) * 5 / 9 + 273.15,
        P=850 * 6894.76,
    )

    Tri_720 = bst.units.MixTank("Tri_720", outs="S_725", tau=1.5/60)
    (S_720, S_721) - Tri_720

    Tur_730 = bst.units.Turbine("Tur_730", outs="S_731", P=1 * 6894.76)

    # Out: STM REF (S_732)
    Div_731 = bst.units.Duplicator("Div_731", outs=["S_732", "S_736"])
    Tri_720 - Tur_730 - Div_731

    Tur_740 = bst.units.Turbine("Tur_740", outs="S_741", P=1 * 6894.76)

    # Out: Gasifier (S_742)
    Div_745 = bst.units.Duplicator(
        "Div_745", outs=["S_742", "S_743", "S_744", "S_745", "S_746", "S_747"]
    )
    (Div_731 - 1) - Tur_740 - Div_745

    # Unit 660
    REBOIL_COND = bst.units.heat_exchange.HXutility("REBOIL_COND", outs="S_773")
    (Div_745 - 4) - REBOIL_COND
    # Unit 661
    MOL_SIEVE = bst.units.heat_exchange.HXutility("MOL_SIEVE", outs="S_772")
    (Div_745 - 3) - MOL_SIEVE
    # Unit 432
    LO_CAT_HTR = bst.units.heat_exchange.HXutility("LO_CAT_HTR", outs="S_774")
    (Div_745 - 5) - LO_CAT_HTR
    Tur_750 = bst.units.Turbine("Tur_750", outs="S_751", P=1 * 6894.76)
    (Div_745 - 2) - Tur_750

    # Unit 650
    # MeOH_VAPORIZ = bst.units.heat_exchange.HXutility('MeOH_VAPORIZ', outs = 'S_710', T = (526.5776-32)*5/9+273.15, rigorous=False)
    MeOH_VAPORIZ = bst.units.MixTank("MeOH_VAPORIZ", outs="S_710", tau=1.5/60)
    MeOH_VAPORIZ.outs[0].T = (
        526.5776 - 32
    ) * 5 / 9 + 273.15  # ToDo: Switch back to heat exchange later
    (Div_700 - 2) - MeOH_VAPORIZ

    # In: MU from E498 (S_770)
    S_770 = bst.Stream(
        "S_770",
        Water=213884,
        units="lb/hr",
        T=(178.7597 - 32) * 5 / 9 + 273.15,
        P=60 * 6894.76,
    )

    Tri_765 = bst.units.MixTank("Tri_765", outs="S_777", tau=1.5/60)
    (MeOH_VAPORIZ - 0, S_770, MOL_SIEVE - 0, REBOIL_COND - 0, LO_CAT_HTR - 0) - Tri_765

    # In S_1871
    S_1871 = bst.Stream(
        "S_1871", Water=9232755, units="lb/hr", T=(90 - 32) * 5 / 9 + 273.15, P=65 * 6894.76
    )

    HX_760 = bst.units.heat_exchange.HXprocess("HX_760", outs=["S_761", "S_1872"])
    (Tur_750 - 0, S_1871) - HX_760

    # Unit 761
    COND_PUMP = bst.units.Pump("COND_PUMP", outs="S_762")
    (HX_760 - 0) - COND_PUMP

    # Unit 703
    BLOWDOWN = bst.units.Splitter("BLOWDOWN", outs=["S_712", "S_718"], split=0.5)
    (STEAM_DRUM - 1) - BLOWDOWN

    # Out: WWT (S_719)
    HX_770 = bst.units.heat_exchange.HXprocess("HX_770", outs="S_719")
    (BLOWDOWN - 1) - HX_770


    # Unit 705
    # Out: VENT (S_715)
    DEAERATOR = bst.units.Splitter("DEAERATOR", outs=["S_715", "S_779"], split=0.0)
    (BLOWDOWN - 0, Div_745 - 1, COND_PUMP - 0, Tri_765 - 0) - DEAERATOR

    # Unit 780
    # Out: S_781
    BFW_PUMP = bst.units.Pump("BFW_PUMP", outs="S_781")
    (DEAERATOR - 1) - BFW_PUMP

with bst.System("Jet_fuel_synthesis") as jet_fuel_synthesis:
    # Jet Fuel Synthesis Sytem
    # Area 800
    DEHYDRATION = bst.units.MixTank("DEHYDRATION", outs="S_801", tau=1.5/60)
    EtOH_COLUMN-0-0-DEHYDRATION
    def spec_dehydration():
        DEHYDRATION._run()
        rxn = tmo.reaction.Reaction(
            "Ethanol -> Ethylene + Water", 
            reactant="Ethanol",
            X=0.90
        )
        rxn(DEHYDRATION.outs[0])
    DEHYDRATION.add_specification(spec_dehydration)

    SEPARATION_800 = bst.units.Flash("SEPARATION_800", outs=["S_802", "S_803"], T=90 + 273.15, P=101325)
    DEHYDRATION-0-0-SEPARATION_800

    OLIGOMERIZATION = bst.units.MixTank("OLIGOMERIZATION", outs="S_804", tau=1.5/60)
    SEPARATION_800-0-0-OLIGOMERIZATION
    def spec_oligomerization():
        OLIGOMERIZATION._run()
        rxn = tmo.reaction.ParallelReaction([
            tmo.reaction.Reaction(
            "2Ethylene -> C4H8", 
            reactant="Ethylene",
            X=0.1
            ),
            tmo.reaction.Reaction(
            "3Ethylene -> C6H12", 
            reactant="Ethylene",
            X=0.1
            ),
            
            tmo.reaction.Reaction(
            "4Ethylene -> C8H16", 
            reactant="Ethylene",
            X=0.2
            ),
            
            tmo.reaction.Reaction(
            "5Ethylene -> C10H20", 
            reactant="Ethylene",
            X=0.4
            ),
            
            tmo.reaction.Reaction(
            "6Ethylene -> C12H24", 
            reactant="Ethylene",
            X=0.1
            ),
            
            tmo.reaction.Reaction(
            "8Ethylene -> C16H34", 
            reactant="Ethylene",
            X=0.1
            )
        ]
        )
        rxn(OLIGOMERIZATION.outs[0])
    OLIGOMERIZATION.add_specification(spec_oligomerization)

    DISTILLATION_800 = bst.units.distillation.ShortcutColumn("DISTILLATION_800", outs=["S_805", "S_806"],
                                                                    LHK=("C4H8", "C12H24"),
                                                                    k=1.5,
                                                                    product_specification_format='Recovery',
                                                                    Lr=0.9,
                                                                    Hr=0.99,)
    DISTILLATION_800.check_LHK = False
    DISTILLATION_800.design_results["Reflux"] = 2
    DISTILLATION_800.design_results["Theoretical stages"] = 2
    DISTILLATION_800.design_results["Theoretical feed stage"] = 1

    OLIGOMERIZATION-0-0-DISTILLATION_800
    HYDROGENATION_800 = bst.units.MixTank("HYDROGENATION_800", outs="S_807", tau=1.5/60)
    HYDROGEN = bst.Stream("HYDROGEN", H2=2000*0.1*0.05, units="tonnes/day")
    def spec_hydrogenation():
        
        HYDROGENATION_800._run()
        rxn = tmo.reaction.ParallelReaction([
            tmo.reaction.Reaction(
                "C4H8 + H2 -> C4H10", 
                reactant="C4H8",
                X=0.99
            ),
            tmo.reaction.Reaction(
                "C6H12 + H2 -> C6H14", 
                reactant="C6H12",
                X=0.99
            ),
            tmo.reaction.Reaction(
                "C8H16 + H2 -> C8H18", 
                reactant="C8H16",
                X=0.99
            ),
            tmo.reaction.Reaction(
                "C10H20 + H2 -> C10H22", 
                reactant="C10H20",
                X=0.99
            ),
            tmo.reaction.Reaction(
                "C12H24 + H2 -> C12H26", 
                reactant="C12H24",
                X=0.99
            ),
            tmo.reaction.Reaction(
                "C16H32 + H2 -> C16H34", 
                reactant="C16H32",
                X=0.99
            ),
        ]
        )
        rxn.force_reaction(HYDROGENATION_800.outs[0])
    HYDROGENATION_800.add_specification(spec_hydrogenation)
    DISTILLATION_800-1-0-HYDROGENATION_800
    DISTILLATION_800-0-1-OLIGOMERIZATION

    JET_FUEL_FLASH = bst.units.Splitter("JETFUELFLASH", outs=["S_808", "S_809"], split={
        "C4H10":0.95,
        "C6H14":0.95,
        "C8H18":0.99,
        "C10H22":0.99,
        "C12H26":0.99,
        "C16H34":0.99
        })
    out_jet_fuel = JET_FUEL_FLASH.outs[0]
    HYDROGENATION_800-0-0-JET_FUEL_FLASH

    HYDROGEN_MIXER = bst.units.Mixer("HYDROGEN_MIXER", outs="S_810")
    HYDROGEN_MIXER.ins[0] = HYDROGEN
    # HYDROGEN_MIXER.ins[1] = JET_FUEL_FLASH.outs[1]
    HYDROGEN_MIXER-0-1-HYDROGENATION_800



# %%
# Diagram
sys = bst.main_flowsheet.create_system("sys")
# sys.diagram(format="png")
# draw_io(sys)
# %%
#
try:
    sys.simulate()
except:
    try:
        sys.simulate()
    except:
        pass 
