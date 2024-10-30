import numpy as np
import pandas as pd
from random import uniform
import plotly.express as px
import pygfunction as gt
import streamlit as st
import matplotlib.pyplot as plt
from GHEtool import HourlyGeothermalLoad, Borefield, GroundFluxTemperature, GroundLayer


def temperature_plot(df, x_series, y_series, min_value = 0, max_value = 10): #self,
    fig = px.line(df, x=x_series, y=y_series, labels={'Value': y_series, 'Timestamp': 'Tid'}, color_discrete_sequence=[f"rgba(29, 60, 52, 0.75)"])
    fig.update_xaxes(type='category')
    fig.update_xaxes(
        title='',
        type='category',
        gridwidth=0.3,
        tickmode='auto',
        nticks=4,  
        tickangle=30)
    fig.update_yaxes(
        title=f"Temperatur (ºC)",
        tickformat=",",
        ticks="outside",
        gridcolor="lightgrey",
        gridwidth=0.3,
    )
    fig.update_layout(
        #xaxis=dict(showticklabels=False),
        showlegend=False,
        yaxis=dict(range=[min_value, max_value]),
        margin=dict(l=20,r=20,b=20,t=20,pad=0),
        #separators="* .*",
        #yaxis_title=f"Temperatur {series_name.lower()} (ºC)",
        xaxis_title="",
        height = 300,
        )
    st.plotly_chart(fig, use_container_width=True, config = {'displayModeBar': False, 'staticPlot': False})
    avg_temp = round(np.mean(df[y_series]),2)
    max_temp = np.max(df[y_series])
    min_temp = np.min(df[y_series])

    c1,c2,c3 = st.columns(3)
    with c1:
        st.metric('Gjennomsnittstemperatur', f'{avg_temp} C')
    with c2:
        st.metric('Makstemperatur', f'{max_temp} C')
    with c3:
        st.metric('Minimumstemperatur', f'{min_temp} C')
    #fig.write_image("figs/Lufttemp.png")


st.title('GHEtool: Flere lag i grunnen')

bronnlast = pd.read_csv('Timelast_vali_masteroppgave.txt')
bronnlast = bronnlast.iloc[3:,:].reset_index(drop=True)
bronnlast = np.array(bronnlast['1 1'])
bronnlast = bronnlast.astype(float)
bronnlast = -bronnlast/1000
bronnlast = bronnlast*268

bronnlast[2190:6570] = 0
bronnlading = np.zeros(8760)

j = 0
for i in range(2190,6570):
    bronnlading[i] = 1.2*bronnlast[j]
    j = j+1
    if j == 2190:
        j = 6570

#energy_demand = 14700000        #kWh
#power_demand_MW = 5
#days_per_month = [31,59,90,120,151,181,212,243,273,304,334,365]
#bronnlast = np.zeros(8760)
#bronnlading = np.zeros(8760)
#summer_start = days_per_month[3]
#summer_end = days_per_month[9]
#for i in range(0,len(bronnlast)):
#    if i <= summer_start*24 or i >= summer_end*24:
#        bronnlast[i] = energy_demand/(8760-(summer_end*24-summer_start*24))+uniform(-1000, 1000)
#    else:
#        bronnlading[i] = (1.3*energy_demand)/(summer_end*24-summer_start*24)+uniform(-1000, 1000)

#bronnlast = np.array(bronnlast)
#st.write(bronnlast[10])
#st.write(bronnlading[4000])




#---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

# Last
load = HourlyGeothermalLoad(heating_load=bronnlast, cooling_load=bronnlading, simulation_period=25)
borefield = Borefield(load = load)
borefield.set_load(load=load)

# Grunn
#ground_data = GroundFluxTemperature(k_s = 3.8, T_g=8, flux=0, volumetric_heat_capacity=2.16e6)

layer_1 = GroundLayer(k_s=3, volumetric_heat_capacity=2.16e6, thickness=50)
#layer_1 = GroundLayer(k_s=3, volumetric_heat_capacity=2.16e6, thickness=2)
layer_2 = GroundLayer(k_s=3, volumetric_heat_capacity=2.16e6, thickness=50)
layer_3 = GroundLayer(k_s=3, volumetric_heat_capacity=2.16e6, thickness=500)

ground_data = GroundFluxTemperature(T_g=8, flux=0, volumetric_heat_capacity=2.16e6)
ground_data.add_layer_on_bottom([layer_1, layer_2, layer_3])                   # Layer 1 havner i øverste del av brønnen, og layer 3 i nederste
#ground_data.add_layer_on_top([layer_1, layer_2, layer_3])                     # Layer 3 havner i øverste del av brønnen, og layer 1 i nederste. Hvis denne brukes må summen av tykkelser være større enn dybden
                                                                             # De plasseres x antall meter ned i borehullet, og påvirkes ikke av borehole buried depth     

st.write(f'Termisk ledningsevne: {ground_data.k_s(170)} W/mK')               # Regner ut gjennomsnittlig k_s for dybder ned til hit


ks_depths = []
for i in range(0,305,5):
    ks_depths.append(ground_data.k_s(i))

st.write(np.mean(ks_depths))

fig = plt.figure()
plt.plot(np.arange(0,305,5), ks_depths, color='red', linewidth=2)
plt.xlabel('Dybde (m)')
plt.ylabel('Ledningsevne (W/mK)')
plt.grid()
st.pyplot(fig)

borefield.set_ground_parameters(data=ground_data)
borefield.Rb = 0.13   
st.write(borefield.borehole.get_Rb(300,10,0.114/2,3))

# Felt/konfigurasjon
field = gt.boreholes.rectangle_field(
        N_1=25,
        N_2=10,
        B_1=5,
        B_2=5,
        H=300,
        D=10, # borehole buried depth                                               Har ingen betydning for plassering av layers
        r_b=0.1143/2, # borehole radius
        tilt=0 # tilt
        )
borefield.set_borefield(borefield = field)

##st.write(borefield.borefield)

#st.pyplot(gt.boreholes.visualize_field(field))

# Beregning
#borefield.calculation_setup(use_constant_Rb=True)           # Å sette use_constant_Rb til True skal være ekvivalent med å avhuke boksen "Account for internal heat transfer" i EED
st.write(borefield.Rb)
st.write(borefield.ground_data.alpha(100))
borefield.calculate_temperatures(hourly=True)               # Denne funksjonen finnes i GHEtool/GHEtool/Borefield.py, linje 1609->
#st.write(borefield.results)
greie = gt.gfunction.gFunction(borefield.borefield, 1.38e-6, np.array([80000]))#.gFunc          # Denne beregnede g-funksjonen er avhengig av borehole buried depth
st.write(greie.gFunc)

# Resultater
#st.write(borefield.Rb)
#st.write(vars(borefield.results))

borehole_wall_temp = borefield.results._Tb

temp_results = pd.DataFrame(borefield.results._peak_heating)
temp_results = temp_results.reset_index()
temp_results.columns = (['index', 'Temp'])

#temperature_plot(temp_results, 'index', 'Temp', min_value = -10, max_value = 10)


tf_pygfunc = temp_results['Temp'].iloc[:-1]


######### LAG X-VEKTOR ############################################################################
x_vector = np.arange(0,218999)
x_vector = x_vector/8760

######### PLOT TEMP #####################################################################################
mode = 'hourly' # 'const' eller 'hourly' lastprofil
x_min = 0        #12
x_maks = 25       #12.01918                       #First month: 0.08493, First week: 0.01918
linewidth = 1
figwidth = 8
figheight = 4
save = 'no'

st.write('Hit 7')

fig = plt.figure(figsize=(figwidth, figheight))
plt.plot(x_vector, tf_pygfunc, color='red', linewidth=linewidth)
plt.xlim([x_min,x_maks])
plt.ylim([-20,60])
#plt.plot(x_vector, storage_temp_trnsys, color='#0000FF')
#plt.plot(x_vector, out_temp_bh_trnsys, color='#0096FF')
#plt.plot(x_vector, out_temp_load_trnsys, color='#088F8F')
plt.xlabel('Year')
plt.ylabel('Temperature (°C)')
plt.legend(['$T_f$ Pygfunction/GHEtool'])
plt.grid()
if save == 'yes':
    plt.savefig(f'Resultatfigurer/Vali_result_temp_{mode}_{x_min}-{x_maks}.svg', format='svg')
#plt.show()
st.pyplot(fig)

c1, c2 = st.columns(2)
with c1:
    st.metric('Høyeste temperatur siste år', f'{round(np.max(tf_pygfunc[-8760:]),2)} °C')
with c2:
    st.metric('Laveste temperatur siste år', f'{round(np.min(tf_pygfunc[-8760:]),2)} °C')

## Dette har med varmepumpe å gjøre:
#compressor_array, load_array, peak_array = np.zeros(8760), np.zeros(8760), np.zeros(8760)
#YEAR = int(25/2)
#for i in range(0, 2):
#    for j in range(0, 8760):
#        #dhw_COP, dhw_P = _heatpump_technical_sheet(borehole_temperature[(8760*YEAR) + j], dhw_array[j], dhw_flow_temperature[j], heatpump_size=dhw_heatpump)
#        spaceheating_COP, spaceheating_P = _heatpump_technical_sheet(borehole_temperature[(8760*YEAR) + j], spaceheating_array[j], spaceheating_flow_temperature[j], heatpump_size=spaceheating_heatpump)
#        compressor = dhw_P/dhw_COP + spaceheating_P/spaceheating_COP
#        load = (dhw_P - dhw_P/dhw_COP) + (spaceheating_P - spaceheating_P/spaceheating_COP)
#        peak = spaceheating_array[j] + dhw_array[j] - compressor - load
#        compressor_array[j] = compressor
#        load_array[j] = load
#        peak_array[j] = peak
#    borehole_temperature = _borefield_sizing(load_array, borefield)
