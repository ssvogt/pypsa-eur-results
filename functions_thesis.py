# this is to import all important stuff for analysis in PyPSA-eur

import plotly.offline as py
from plotly.graph_objs import *

import pypsa
import matplotlib.pyplot as plt
plt.style.use("bmh")
#%matplotlib inline

import pandas as pd

# Functions to use in cost and LCOE calculations
time_varying = ['offwind-dc',
                'offwind-ac',
                'onwind',
                'solar']

# calculate the dispatched energy in MWh (* snapshot_weightings)
def dispatched_energy_tot(tech_name, n):
    return n.generators_t.p.filter(regex=tech_name ,axis=1).multiply(n.snapshot_weightings.generators, axis=0).sum().sum();

# calculate the dispatched energy in MWh per snapshot (* snapshot_weightings)
def dispatched_energy_t(tech_name, n):
    return n.generators_t.p.filter(regex=tech_name ,axis=1).multiply(n.snapshot_weightings.generators, axis=0).sum(axis=1);

# calculate the dispatched energy in MWh per generator (* snapshot_weightings)
def dispatched_energy_gen(tech_name, n):
    return n.generators_t.p.filter(regex=tech_name ,axis=1).multiply(n.snapshot_weightings.generators, axis=0).sum();

# make dataframe of the total dispatched energy for each technology in MWh
def make_tot_energy_df(n):
    carriers = ['biomass', 
               'coal', 
               'geothermal', 
               'lignite', 
               'nuclear', 
               'oil',
               'CCGT',
               'OCGT',
               'offwind-dc', 
               'offwind-ac', 
               'onwind', 
               'ror', 
               'solar']
    rows = []
    for c in carriers:
        rows.append([c, dispatched_energy_tot(c,n)])
    df_energy = pd.DataFrame(rows, columns=["carrier", "dispatched energy [MWh]"])

    return df_energy;  

# make dataframe of the share of dispatched energy for each technology in %
def make_share_energy_df(n):
    carriers = ['biomass', 
               'coal', 
               'geothermal', 
               'lignite', 
               'nuclear', 
               'oil',
               'CCGT',
               'OCGT',
               'offwind-dc', 
               'offwind-ac', 
               'onwind', 
               'ror', 
               'solar']
    total_energy = make_tot_energy_df(n)['dispatched energy [MWh]'].sum()
    rows = []
    for c in carriers:
        rows.append([c, 100*dispatched_energy_tot(c,n)/total_energy])
    df_energy = pd.DataFrame(rows, columns=["carrier", "share dispatched energy [%]"])

    return df_energy;    

# calculate the installed capacity of this technology [MW]
def inst_capacity(tech_name, n):
    inst_capacity = n.generators.p_nom_opt.filter(regex=tech_name ,axis=0).sum()
    return inst_capacity;

# make installed capacity df
def make_capacity_df(n):
    carriers = ['biomass', 
           'coal', 
           'geothermal', 
           'lignite', 
           'nuclear', 
           'oil',
           'CCGT',
           'OCGT',
           'offwind-dc', 
           'offwind-ac', 
           'onwind', 
           'ror', 
           'solar']
    rows = []
    for c in carriers:
        rows.append([c, inst_capacity(c,n)])
    df_capacity = pd.DataFrame(rows, columns=["carrier", "installed capacity [MW]"])

    return df_capacity;

# calculate the maximum theoretically dispatchable energy (maximum utilization) of this technology in the whole year [MWh]
def max_energy(tech_name, n):

    time_varying = ['offwind-dc',
                'offwind-ac',
                'onwind',
                'solar']

    #### ENERGY (max utilization) ####

    # time varying:
    # multiply the capacity factor for each generator in each timeslot (matrix) with the maximal nominal capacity of each generator (vector with generators) --> matrix
    # multiply matrix with snapshot weightings (vector with snapshots) --> matrix
    # sum on both axis
    if(tech_name in time_varying):
        max_energy = (n.generators_t.p_max_pu.filter(regex=tech_name ,axis=1)*n.generators.p_nom_opt.filter(regex=tech_name ,axis=0)).multiply(n.snapshot_weightings.generators, axis=0).sum().sum()
    
    # static: 
    # multiply capacity factor p_max_pu (vector with generators) with nominal power p_nom (vector with generators) [MW]
    # summarize vector to one sum
    # multiply with snapshot weightings (vector with snapshots) [MWh]
    # sum again [MWh]
    else: #if(tech_name not in time_varying):
        max_energy = ((n.generators.p_max_pu.filter(regex=tech_name ,axis=0) * n.generators.p_nom_opt.filter(regex=tech_name ,axis=0)).sum() * n.snapshot_weightings.generators).sum()

    return max_energy;

# make idf of maximal dispatchable energy
def make_max_energy_df(n):
    carriers = ['biomass', 
           'coal', 
           'geothermal', 
           'lignite', 
           'nuclear', 
           'oil',
           'CCGT',
           'OCGT',
           'offwind-dc', 
           'offwind-ac', 
           'onwind', 
           'ror', 
           'solar']
    rows = []
    for c in carriers:
        rows.append([c, max_energy(c,n)])
    df_energy = pd.DataFrame(rows, columns=["carrier", "max. energy [MWh]"])

    return df_energy;



# make dataframe with all important results from the nc file (inst. cap, dispatch, curtailment, max energy, storage capacities, co2 price)
def make_overview(n, description, excel_doc, costs):
    d = {'co2 limit': [n.global_constraints.mu['CO2Limit']], 'objective': [n.objective], 'tot. dispatch': [make_tot_energy_df(n)['dispatched energy [MWh]'].sum()], 'total load': [(n.snapshot_weightings.generators * n.loads_t.p.sum(axis=1)).sum()], 'dispatch and storage dispatch': [(n.snapshot_weightings.generators * n.generators_t.p.sum(axis=1)).sum() + (n.storage_units_t.p_dispatch.multiply(n.snapshot_weightings.generators, axis=0).filter(regex='PHS$' ,axis=1).sum(axis=1) + n.storage_units_t.p_dispatch.multiply(n.snapshot_weightings.generators, axis=0).filter(regex='hydro$' ,axis=1).sum(axis=1)).sum()], 'nom. energy capacity battery':[n.stores.e_nom_opt.filter(regex='battery$' ,axis=0).sum()], 'nom. energy capacity H2':[n.stores.e_nom_opt.filter(regex='H2$' ,axis=0).sum()], 'dispatch battery [MWh]':[n.stores_t.p.multiply(n.snapshot_weightings.generators, axis=0).filter(regex='battery$' ,axis=1).sum(axis=1).sum()], 'dispatch H2 [MWh]':[n.stores_t.p.multiply(n.snapshot_weightings.generators, axis=0).filter(regex='H2$' ,axis=1).sum(axis=1).sum()]}
    df = pd.DataFrame(data=d)

    carriers = ['biomass', 
           'coal', 
           'geothermal', 
           'lignite', 
           'nuclear', 
           'oil',
           'CCGT',
           'OCGT',
           'offwind-dc', 
           'offwind-ac', 
           'onwind', 
           'ror', 
           'solar']

    capacity = make_capacity_df(n)
    rows = []       
    for c in carriers:
        rows.append([n.generators.p_nom.filter(regex=c).sum()])
    capacity['p_nom'] = pd.DataFrame(rows)
    capacity['capacity_addition'] = capacity['installed capacity [MW]'] - capacity['p_nom']


    energy_df = pd.concat([make_tot_energy_df(n)['carrier'], capacity['installed capacity [MW]'], capacity['p_nom'], capacity['capacity_addition'], make_max_energy_df(n)['max. energy [MWh]'], make_tot_energy_df(n)['dispatched energy [MWh]']], axis=1)
    #energy_df.to_excel('2030ext.xlsx', sheet_name=description, index=False)

    #Hydro
    hydro =['hydro']
    #installed capacity
    hydro.append(n.storage_units.p_nom_opt.filter(regex='PHS$' ,axis=0).sum() + n.storage_units.p_nom_opt.filter(regex='hydro$' ,axis=0).sum())
    #p_nom=installed capacity
    hydro.append(n.storage_units.p_nom_opt.filter(regex='PHS$' ,axis=0).sum() + n.storage_units.p_nom_opt.filter(regex='hydro$' ,axis=0).sum())
    # capacity addition
    hydro.append(0)
    # max energy
    hydro.append(((n.storage_units.p_max_pu * n.storage_units.p_nom_opt).sum() * n.snapshot_weightings.generators).sum())
    # dispatch
    hydro.append((n.storage_units_t.p_dispatch.multiply(n.snapshot_weightings.generators, axis=0).filter(regex='PHS$' ,axis=1).sum(axis=1) + n.storage_units_t.p_dispatch.multiply(n.snapshot_weightings.generators, axis=0).filter(regex='hydro$' ,axis=1).sum(axis=1)).sum())

    hydro = pd.DataFrame(hydro).transpose()
    hydro.columns= list(['carrier', 'installed capacity [MW]', 'p_nom', 'capacity_addition','max. energy [MWh]', 'dispatched energy [MWh]'])
    energy_df = energy_df.append(hydro)

    # Curtailment in %
    avail = n.generators_t.p_max_pu.multiply(n.snapshot_weightings.generators, axis=0).multiply(n.generators.p_nom_opt).sum().groupby(n.generators.carrier).sum()
    #used = n.generators_t.p.sum().groupby(n.generators.carrier).sum()
    used = n.generators_t.p.multiply(n.snapshot_weightings.generators, axis=0).sum().groupby(n.generators.carrier).sum()

    curtailment = pd.DataFrame((avail - used), columns=['curtailment'])
    curtailment['carrier'] = curtailment.index
    curtailment.reset_index(drop=True, inplace=True)

    hydrocur = pd.DataFrame(['hydro', '-inf']).transpose()
    hydrocur.columns = list(['carrier','curtailment'])
    curtailment = curtailment.append(hydrocur)

    energy_df = pd.merge(energy_df, curtailment, on='carrier')
    energy_df.curtailment = [0,0,0,0,0,0,0,0,energy_df.curtailment[8], energy_df.curtailment[9], energy_df.curtailment[10], energy_df.curtailment[11], energy_df.curtailment[12], 0]

    energy_df.columns = ['carrier', 'installed_capacity', 'p_nom', 'capacity_addition','max_energy', 'dispatched_energy', 'curtailment']

    coalsum = ['coal (sum)', 
    energy_df.installed_capacity[1]+energy_df.installed_capacity[3], 
    energy_df.p_nom[1]+energy_df.p_nom[3],
    energy_df.capacity_addition[1]+energy_df.capacity_addition[3],
    energy_df.max_energy[1]+energy_df.max_energy[3],
    energy_df.dispatched_energy[1]+energy_df.dispatched_energy[3],
    energy_df.curtailment[1]+energy_df.curtailment[3],
    ]
    coalsum = pd.DataFrame(coalsum).transpose()

    gassum = ['gas (sum)', 
    energy_df.installed_capacity[6]+energy_df.installed_capacity[7], 
    energy_df.p_nom[6]+energy_df.p_nom[7],
    energy_df.capacity_addition[6]+energy_df.capacity_addition[7],
    energy_df.max_energy[6]+energy_df.max_energy[7],
    energy_df.dispatched_energy[6]+energy_df.dispatched_energy[7],
    energy_df.curtailment[6]+energy_df.curtailment[7],
    ]
    gassum = pd.DataFrame(gassum).transpose()

    offwindsum = ['offwind (sum)', 
    energy_df.installed_capacity[8]+energy_df.installed_capacity[9], 
    energy_df.p_nom[8]+energy_df.p_nom[9],
    energy_df.capacity_addition[8]+energy_df.capacity_addition[9],
    energy_df.max_energy[8]+energy_df.max_energy[9],
    energy_df.dispatched_energy[8]+energy_df.dispatched_energy[9],
    energy_df.curtailment[8]+energy_df.curtailment[9],
    ]
    offwindsum = pd.DataFrame(offwindsum).transpose()

    windsum = ['wind (sum)', 
    energy_df.installed_capacity[8]+energy_df.installed_capacity[9]+energy_df.installed_capacity[10], 
    energy_df.p_nom[8]+energy_df.p_nom[9]+energy_df.p_nom[10],
    energy_df.capacity_addition[8]+energy_df.capacity_addition[9]+energy_df.capacity_addition[10],
    energy_df.max_energy[8]+energy_df.max_energy[9]+energy_df.max_energy[10],
    energy_df.dispatched_energy[8]+energy_df.dispatched_energy[9]+energy_df.dispatched_energy[10],
    energy_df.curtailment[8]+energy_df.curtailment[9]+energy_df.curtailment[10],
    ]
    windsum = pd.DataFrame(windsum).transpose()

    #1,2,3,5,6,7
    fossilssum = ['fossils (sum)', 
    energy_df.installed_capacity[1]+energy_df.installed_capacity[2]+energy_df.installed_capacity[3]
    + energy_df.installed_capacity[5]+energy_df.installed_capacity[6]+energy_df.installed_capacity[7], 
    energy_df.p_nom[1]+energy_df.p_nom[2]+energy_df.p_nom[3]
    + energy_df.p_nom[5]+energy_df.p_nom[6]+energy_df.p_nom[7],
    energy_df.capacity_addition[1]+energy_df.capacity_addition[2]+energy_df.capacity_addition[3]
    + energy_df.capacity_addition[5]+energy_df.capacity_addition[6]+energy_df.capacity_addition[7],
    energy_df.max_energy[1]+energy_df.max_energy[2]+energy_df.max_energy[3]
    + energy_df.max_energy[5]+energy_df.max_energy[6]+energy_df.max_energy[7],
    energy_df.dispatched_energy[1]+energy_df.dispatched_energy[2]+energy_df.dispatched_energy[3]
    + energy_df.dispatched_energy[5]+energy_df.dispatched_energy[6]+energy_df.dispatched_energy[7],
    energy_df.curtailment[1]+energy_df.curtailment[2]+energy_df.curtailment[3]
    + energy_df.curtailment[5]+energy_df.curtailment[6]+energy_df.curtailment[7],
    ]
    fossilssum = pd.DataFrame(fossilssum).transpose()

    sum_df = coalsum
    sum_df = sum_df.append(gassum)
    sum_df = sum_df.append(windsum)
    sum_df = sum_df.append(offwindsum)
    sum_df = sum_df.append(fossilssum)
    sum_df.columns = ['carrier', 'installed_capacity', 'p_nom', 'capacity_addition','max_energy', 'dispatched_energy', 'curtailment']
    sum_df = sum_df.reset_index(drop=True)


    energy_df = energy_df.append(sum_df)
    energy_df = energy_df.reset_index(drop=True)

    energy_df.index = [0,2,3,4,5,6,8,9,12,13,14,15,16,17,1,7,10,11,18]
    energy_df = energy_df.sort_index(axis=0)

    energy_df_final = energy_df[['carrier', 'installed_capacity', 'dispatched_energy', 'max_energy','curtailment', 'p_nom', 'capacity_addition']]


    with pd.ExcelWriter(excel_doc, engine="openpyxl", mode='a') as writer:  
        df.to_excel(writer, sheet_name=description+'general')
        energy_df_final.to_excel(writer, sheet_name=description)
    
    return energy_df_final;
