#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import gam

# create the simulation
sim = gam.Simulation()

# main options
ui = sim.user_info
ui.g4_verbose = False
ui.visu = False
ui.number_of_threads = 1
gam.log.setLevel(gam.RUN)  # FIXME to put in ui ?
print(ui)

# add a material database
sim.add_material_database('data/GateMaterials.db')

# units
m = gam.g4_units('m')
mm = gam.g4_units('mm')
cm = gam.g4_units('cm')
keV = gam.g4_units('keV')
Bq = gam.g4_units('Bq')
kBq = 1000 * Bq

#  change world size
world = sim.world
world.size = [1 * m, 1 * m, 1 * m]

# CT image
patient = sim.add_volume('Image', 'patient')
patient.image = 'data/449_CT_4mm.mhd'
patient.material = 'G4_AIR'  # material used by default
patient.voxel_materials = [[-900, 'G4_AIR'],
                           [-100, 'Lung'],
                           [0, 'G4_ADIPOSE_TISSUE_ICRP'],
                           [300, 'G4_TISSUE_SOFT_ICRP'],
                           [800, 'G4_B-100_BONE'],
                           [6000, 'G4_BONE_COMPACT_ICRU']]
patient.dump_label_image = 'data/449_CT_label.mhd'
patient.translation = [0, 0, 0]

# source from spect
source = sim.add_source('Voxels', 'spect')
source.particle = 'e-'
source.activity = 50000 * Bq / ui.number_of_threads
source.image = 'data/five_pixels_norm.mha'
source.direction.type = 'iso'
source.position.translation = [0 * mm, 0 * mm, 0 * mm]
source.energy.mono = 1 * keV
source.mother = 'patient'
source.img_coord_system = True

# cuts
p = sim.get_physics_info()
p.physics_list_name = 'G4EmStandardPhysics_option1'
p.enable_decay = False
c = p.production_cuts
c.world.gamma = 1 * mm
c.world.positron = 1 * mm
c.world.electron = 1 * mm
c.world.proton = 1 * m

# add dose actor
dose = sim.add_actor('DoseActor', 'dose')
dose.save = 'output/test21-edep.mhd'
dose.mother = 'patient'
dose.dimension = [125, 125, 101]
dose.spacing = [4 * mm, 4 * mm, 4 * mm]
dose.img_coord_system = True

# add stat actor
stats = sim.add_actor('SimulationStatisticsActor', 'Stats')
stats.track_types_flag = True

# create G4 objects
sim.initialize()

# verbose
sim.apply_g4_command('/tracking/verbose 0')

# start simulation
sim.start()

# print results at the end
stat = sim.get_actor('Stats')
# stat.write('output/stat021.txt')
d = sim.get_actor('dose')

# tests
stats_ref = gam.read_stat_file('./output/stat021.txt')
stats_ref.counts.run_count = ui.number_of_threads
is_ok = gam.assert_stats(stat, stats_ref, 0.1)
is_ok = is_ok and gam.assert_images('output/test21-edep.mhd',
                                    'output/test21-ref-edep.mhd',
                                    stat, tolerance=0.01)
gam.test_ok(is_ok)