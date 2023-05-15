from meltTempPy import MeltTempPy

system = """
    units      real
    dimension  3
    boundary   p p p
    atom_style full
    """

styles = """
    pair_style lj/cut/coul/long 10.0
    bond_style  harmonic
    angle_style harmonic
    kspace_style pppm 1.0e-5 
    """

potentials = """
    group ox type 2
    group hy type 1

    set group ox charge -0.830
    set group hy charge 0.415

    pair_coeff 1 1*2 0.000 0.000 
    pair_coeff 2 2 0.102 3.188 
    bond_coeff  1 450 0.9572
    angle_coeff 1 55 104.52

    neigh_modify one 10000
    """

thermo = """
    thermo      100
    thermo_style custom step temp pe
    """

mtp = MeltTempPy(system, styles, potentials, thermo, "H2O", 2)
temp, dev = mtp.find_tmelt("Ice-Ic-40A-box.dat", 0.5, 3000, 100, 400, 2, "bond/types 1 angle/types 1 extra/bond/per/atom 1000 extra/angle/per/atom 1000")
print(f"Melting temperature of water is {temp} ± {dev} K")