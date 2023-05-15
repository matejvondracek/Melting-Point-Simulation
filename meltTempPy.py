from lammps import lammps
import time

class MeltTempPy:
    system = "" 
    styles = ""
    potentials = ""
    thermo = ""
    name = ""
    compute = """
            compute pe all pe
            compute temp all temp
            """
    timestep = 0.0
    run = 0
    t = 0
    n_atom_types = 0


    def __init__(self, system, styles, potentials, thermo, name, n_atom_types):
        self.system = system
        self.styles = styles
        self.potentials = potentials
        self.thermo = thermo
        self.name += name
        self.n_atom_types = n_atom_types


    def _run_sim_init(self, source, t_min, t_max, create_box_settings):
        # melting for liquid
        lmp = lammps()
        lmp.commands_string(self.system + self.styles)
        lmp.command(f"read_data {source}")
        lmp.commands_string(self.potentials + self.thermo + self.compute) 
        s = f"""
            velocity all create {t_max} 123456 dist gaussian
            fix f1 all nvt temp {t_max} {t_max} 10.0
            dump d all atom 10 {self.name}_init_melt.dump
            
            timestep {self.timestep}
            run {self.run}

            write_data temp.lmp pair ij 
            """
        lmp.commands_string(s)

        boxlo, boxhi, xy, yz, zx, per, type = lmp.extract_box()

        # combining liquid and solid
        lmp = lammps()
        lmp.commands_string(self.system + self.styles)
        lmp.command(f"region sim_box block 0 {2 * (boxhi[0] - boxlo[0]) + 4} 0 {boxhi[1] - boxlo[1] + 1} 0 {boxhi[2] - boxlo[2] + 1}")
        lmp.command(f"create_box {self.n_atom_types} sim_box {create_box_settings}")
        
        lmp.command(f"read_data temp.lmp add append group liquid shift {-boxlo[0]} {-boxlo[1]} {-boxlo[2]}")
        lmp.command(f"read_data {source} add append group solid shift {boxhi[0] - 2 * boxlo[0] + 2} {-boxlo[1]} {-boxlo[2]}")
        
        lmp.commands_string(self.potentials)
        lmp.commands_string(self.thermo + self.compute)
        s = f"""   
            write_data test pair ij
            velocity all create 1 123456 dist gaussian
            fix f all nvt temp 1 {t_max} 1000.0
            dump d all atom 1 {self.name}_init_equi.dump

            run 100
            
            write_data {self.name}_init.lmp pair ij
            """
        lmp.commands_string(s)
        return lmp.extract_compute("pe", 0, 0)
    
    
    def _run_sim_nvt(self, temp):
        lmp = lammps()
        lmp.commands_string(self.system + self.styles)
        lmp.command(f"read_data {self.name}_init.lmp")
        lmp.commands_string(self.potentials + self.thermo + self.compute)
        s = f"""
            velocity all create 1 123456 dist gaussian
            fix f1 all nvt temp 1 {temp} 50.0
            dump d all atom 10 {self.name}_nvt_{int(temp)}.dump

            timestep {self.timestep}
            run {self.run}   
            """
        lmp.commands_string(s)
        return lmp.extract_compute("pe", 0, 0)
    
    
    def find_tmelt(self, source, time_step, steps, t_min, t_max, max_dev, create_box_settings):
        start_time = time.time()
        self.timestep = time_step
        self.run = steps

        pe_init = self._run_sim_init(source, t_min, t_max, create_box_settings)

        while (t_max - t_min > 2 * max_dev):
            t_mid = (t_max + t_min) / 2
            print(t_mid)
            pe_res = self._run_sim_nvt(t_mid)
            if pe_res is not None:       
                if (pe_init > pe_res):
                    t_min = t_mid
                else:
                    t_max = t_mid 
            else:
                Exception()
            
        t_mid = (t_max + t_min) / 2
        dev = (t_max - t_min) / 2
        self.t = round((time.time() - start_time) / 60)
        return t_mid, dev