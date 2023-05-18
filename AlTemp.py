from meltTempPy import MeltTempPy

system = """
    units      real
    dimension  3
    boundary   p p p
    atom_style atomic
    """

styles = """
    pair_style eam/alloy
    """

potentials = """
    pair_coeff * * Al99.eam.alloy Al
    """

thermo = """
    thermo      100
    thermo_style custom step temp pe
    """

settings = ""

mtp = MeltTempPy(system, styles, potentials, thermo, "Al", 1)
temp, dev = mtp.find_tmelt("Al_cube.lmp", 0.5, 3000, 500, 2000, 2, settings)
print(f"Melting temperature of water is {temp} ± {dev} K")
print(f"Total time: {mtp.time}")