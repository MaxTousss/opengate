#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Context: See test079_mean_energy_per_ion_pairs.py

zxc
"""

from test079_mean_energy_per_ion_pairs_helpers import *
import opengate.tests.utility as tu
import matplotlib.pyplot as plt


#########################################################################################
# Simulations configuration that may be relevant to change
#########################################################################################
# Mean energy of Ion Pair to use. 5.0 eV should produce the expected 0.5 deg FWHM in PET
# imaging
mean_energy = 5.0 * eV


def set_ionisation(simulation_engine, param):
    volume = param["volume"]
    mean_energy = param["mean_energy"]
    sim = simulation_engine.simulation
    mat = sim.volume_manager.find_or_build_material(volume.material)
    ionisation = mat.GetIonisation()
    if mean_energy is not None:
        ionisation.SetMeanEnergyPerIonPair(mean_energy)
    print(
        f"material {volume.material} mean excitation energy is {ionisation.GetMeanExcitationEnergy() / eV} eV"
    )
    print(
        f"material {volume.material} mean energy per ion pair is {ionisation.GetMeanEnergyPerIonPair() / eV} eV"
    )


#########################################################################################
# Main : We use this to launch the test
#########################################################################################
if __name__ == "__main__":
    paths = tu.get_default_test_paths(__file__, output_folder="test079")

    # Define core of the simulation, including physics
    sim = setup_simulation_engine(paths)

    # add a waterbox
    wb = sim.add_volume("Box", "waterbox")
    wb.size = [50 * cm, 50 * cm, 50 * cm]
    ###################################
    # zxc start

    # Even when defined in add_material_nb_atoms, need to add to GateMaterial.db
    elems = ["C", "H", "O"]
    nbAtoms = [5, 8, 2]
    sim.volume_manager.material_database.add_material_nb_atoms(
        "IEC_PLASTIC", elems, nbAtoms, 1.18 * gcm3
    )

    # IEC_PLASTIC:   d=1.18 g/cm3; n=3; stat=Solid
    #         +el: name=Carbon ; n=5
    #         +el: name=Hydrogen ; n=8
    #         +el: name=Oxygen ; n=2

    #
    # # Material in GateMaterial.db but still need add_material_nb_atoms
    #
    # elems = ["H", "O"]
    # faction = [14, 111]
    # gcm3 = gate.g4_units.g_cm3
    # sim.volume_manager.material_database.add_material_nb_atoms(
    #     "Body", elems, faction, 1.00 * gcm3
    # )
    # wb.material = "Body"

    # zxc end
    ###################################
    # wb.material = "G4_WATER"
    wb.material = "IEC_PLASTIC"

    # test mat properties
    """mat = sim.volume_manager.find_or_build_material(wb.material)
    ionisation = mat.GetIonisation()
    print(
        f"material {wb.material} mean excitation energy is {ionisation.GetMeanExcitationEnergy() / eV} eV"
    )
    print(
        f"material {wb.material} mean energy per ion pair is {ionisation.GetMeanEnergyPerIonPair() / eV} eV"
    )"""

    # set the source
    source = sim.add_source("GenericSource", "f18")
    source.particle = "ion 9 18"
    source.energy.mono = 0
    source.activity = 10000 * Bq
    source.direction.type = "iso"

    # add phase actor
    phsp = setup_actor(sim, "phsp", wb.name)
    phsp.output_filename = paths.output / "annihilation_photons.root"

    # set the hook to print the mean energy
    sim.user_hook_after_init = set_ionisation
    sim.user_hook_after_init_arg = {"volume": wb, "mean_energy": None}

    # go
    sim.run(start_new_process=True)

    # redo test changing the MeanEnergyPerIonPair
    root_filename = phsp.output_filename
    phsp.output_filename = paths.output / "annihilation_photons_with_mepip.root"

    # ionisation.SetMeanEnergyPerIonPair(5.0 * eV)
    # print(f"set MeanEnergyPerIonPair to {ionisation.GetMeanEnergyPerIonPair() / eV} eV")
    # set the hook to print the mean energy
    sim.user_hook_after_init = set_ionisation
    sim.user_hook_after_init_arg = {"volume": wb, "mean_energy": mean_energy}

    # go
    sim.run()

    # test: no mean energy, should be mostly colinear
    gamma_pairs = read_gamma_pairs(root_filename)
    acollinearity_angles = compute_acollinearity_angles(gamma_pairs)

    colin_median = plot_colin_case(acollinearity_angles)

    # test: with mean energy, acolinearity amplitude should have a Rayleigh distribution
    gamma_pairs = read_gamma_pairs(phsp.output_filename)
    acollinearity_angles = compute_acollinearity_angles(gamma_pairs)

    acolin_scale = plot_acolin_case(mean_energy, acollinearity_angles)

    f = paths.output / "acollinearity_angles_p2.png"
    plt.savefig(f)
    print(f"Plot was saved in {f}")

    # final
    # No acolin
    is_ok_p1 = colin_median < 0.01
    # Basic acolin
    is_ok_p2 = np.isclose(acolin_scale * 2.355, 0.5, atol=0.2)

    tu.test_ok(is_ok_p1 and is_ok_p2)
