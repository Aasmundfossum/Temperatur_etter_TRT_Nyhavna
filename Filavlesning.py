import numpy as np
import pandas as pd
import streamlit as st
import plotly.express as px
from datetime import datetime
import os
import io

st.set_page_config(page_title="Temperaturdata", page_icon="🔥")

with open("styles/main.css") as f:
    st.markdown("<style>{}</style>".format(f.read()), unsafe_allow_html=True)

st.title('Verktøy for plotting av temperaturmålinger før og etter termisk responstest')
valgt_bronn = st.selectbox('Velg brønn',options=['B3_CH1','B3_CH2','B4','B5','B6'])

mappenavn = f'{valgt_bronn}_datafiler'

dir_list = os.listdir(mappenavn)

sammenstilling = st.checkbox('Sammenstilling av flere tidspunkter i samme figur')

filnummer_sjekk = st.slider('Filnummer',min_value=0,max_value=len(dir_list)-1,step=1)
filnavn = dir_list[filnummer_sjekk]
filsti = f'{mappenavn}/{filnavn}'

f = open(filsti, "r")
filstring = f.read()
f.close()

filstring = filstring.replace(',', '.')

rader = filstring.split('\n')

dato = rader[9].replace('date\t','')
tid = rader[10].replace('time\t','')

datetime_str = f"{dato} {tid}"
datetime_obj = datetime.strptime(datetime_str, '%Y/%m/%d %H:%M:%S')
formatted_datetime = datetime_obj.strftime('%d.%m.%Y kl. %H:%M:%S')
st.write(f'Dato for valgt filnummer slider: {formatted_datetime}')

if sammenstilling == True:
    c1,c2,c3,c4 = st.columns(4)
    with c1:
        nr_1 = st.number_input('Filnummer 1', min_value=0, max_value=len(dir_list)-1, step=1)
    with c2:
        nr_2 = st.number_input('Filnummer 2', min_value=0, max_value=len(dir_list)-1, step=1)
    with c3:
        nr_3 = st.number_input('Filnummer 3', min_value=0, max_value=len(dir_list)-1, step=1)
    with c4:
        nr_4 = st.number_input('Filnummer 4', min_value=0, max_value=len(dir_list)-1, step=1)
    filnummer = [nr_1, nr_2, nr_3, nr_4]

elif sammenstilling == False:
    filnummer = filnummer_sjekk
    filnummer = [filnummer]

#########################################################################
df_liste = []
formatted_datetime_list = []
for j in range(0,len(filnummer)):
    filnavn = dir_list[filnummer[j]]
    filsti = f'{mappenavn}/{filnavn}'

    f = open(filsti, "r")
    filstring = f.read()
    f.close()

    filstring = filstring.replace(',', '.')

    rader = filstring.split('\n')

    dato = rader[9].replace('date\t','')
    tid = rader[10].replace('time\t','')

    datetime_str = f"{dato} {tid}"
    datetime_obj = datetime.strptime(datetime_str, '%Y/%m/%d %H:%M:%S')
    formatted_datetime = datetime_obj.strftime('%d.%m.%Y kl. %H:%M:%S')
    formatted_datetime_list.append(formatted_datetime)

    rader_data = rader[26:]

    length = np.zeros(len(rader_data))
    temp = np.zeros(len(rader_data))
    stokes = np.zeros(len(rader_data))
    anti_stokes = np.zeros(len(rader_data))

    for i in range(0,len(rader_data)-1):
        kolonner = rader_data[i].split('\t')
        length[i] = kolonner[0]
        temp[i] = kolonner[1]

        df = pd.DataFrame({'Lengde':length, 'Temp':temp})
        df = df[df['Temp'] <= 25]
        df = df[df['Temp'] >=-10]  
        df = df[df['Temp'] != 0.0] 
        df = df.reset_index(drop=True)

        df_slutt = df
    df_liste.append(df_slutt)

#######################################################
st.markdown('---')
st.subheader('Temperaturplot uten valgte aksegrenser:')
empty_df = pd.DataFrame(columns=['Temp', 'Lengde'])
colors = ['#1d3c34', '#48a23f', '#b7dc8f','#FFC358']

if len(formatted_datetime_list) > 1:
    tittel = f'Temperatur i brønn {valgt_bronn} mellom ({formatted_datetime_list[0]}) og ({formatted_datetime_list[-1]})'
else:
    tittel = f'Temperatur i brønn {valgt_bronn} den {formatted_datetime_list[0]}'

fig = px.line(empty_df, x='Temp', y='Lengde', title=tittel, color_discrete_sequence=['#367A2F', '#FFC358'])
for k in range(0,len(df_liste)):
    fig.add_trace(px.line(df_liste[k], x='Temp', y='Lengde', color_discrete_sequence=[colors[k]]).data[0])
fig.update_layout(xaxis_title='Temperatur (\u2103)', yaxis_title='Dybde (m)',legend_title=None)
fig.update_layout(height=800)
fig.update_yaxes(autorange="reversed")
st.plotly_chart(fig)

st.markdown('---')
st.subheader('Temperaturplot med valgte aksegrenser og korrigert for brønndybde:')
c1, c2 = st.columns(2)
with c1:
    min_x = st.number_input('Min x:',value=-3.0,min_value=-20.0,max_value=20.0,step=0.1)
with c2:
    maks_x = st.number_input('Maks x:',value=3.0,min_value=-20.0,max_value=20.0,step=0.1)

c1, c2 = st.columns(2)
with c1:
    min_y = st.number_input('Min y:',value=-500,min_value=-1000,max_value=1000,step=1)
with c2:
    maks_y = st.number_input('Maks y:',value=500,min_value=-1000,max_value=1000,step=1)

skjul = st.number_input('Skjul øverste X datapunkter, hvor X er:', value=0, min_value=0, step=1)

til_figurtittel = st.text_input('Tillegg til figurtittel, f.eks. "2 timer etter test"')
st.markdown('---')

if sammenstilling == False:
    sammenlikn = st.checkbox('Sammenlikn med grovere måling av uforstyrret temperatur (i ustand)')

if sammenlikn == True:
    sammenlikn_fil = st.file_uploader('Excel-fil med TRT-data og beregninger', type='xlsm')
    kalibrering = st.number_input('Korreksjon av temperaturmålinger (antall grader som plusses på)', value=0.0, step=0.1)
    if sammenlikn_fil:
        grov_temp = pd.read_excel(sammenlikn_fil, sheet_name='Uforstyrret temperatur', usecols='A,B')
        grov_temp=grov_temp.loc[5:]
        grov_temp=grov_temp.reset_index(drop=True)
        grov_temp.columns = ['Temp', 'Dybde']
else:
    kalibrering = 0

df_liste_slutt = []
for j in range(0,len(filnummer)):
    df_slutt = df_liste[j]
    df_slutt = df_slutt[df_slutt['Lengde'] >= min_y] 
    df_slutt = df_slutt[df_slutt['Lengde'] <= maks_y] 
    df_slutt = df_slutt.reset_index(drop=True)

    dybde = df_slutt['Lengde']-df_slutt['Lengde'].iloc[0]
    df_slutt['Dybde'] = dybde
    df_slutt['Temp'] = df_slutt['Temp'] + kalibrering

    df_slutt.iloc[:skjul, 1] = np.nan
    df_liste_slutt.append(df_slutt)

st.markdown('')

if valgt_bronn == 'B3_CH1' or valgt_bronn == 'B3_CH2':
    bronnummer = 3
elif valgt_bronn == 'B4':
    bronnummer = 4
elif valgt_bronn == 'B5':
    bronnummer = 5
elif valgt_bronn == 'B6':
    bronnummer = 6


st.markdown('---')


if len(formatted_datetime_list) > 1:
    nettsidetittel = f'Temperatur i testbrønn {bronnummer} mellom {formatted_datetime_list[0]} og {formatted_datetime_list[-1]} ({til_figurtittel})'
    tittel_2 = f'Temperatur i testbrønn {bronnummer} ({til_figurtittel})'
else:
    tittel_2 = f'Temperatur i testbrønn {bronnummer} den {formatted_datetime_list[0]} ({til_figurtittel})'
    nettsidetittel = f'Temperatur i testbrønn {bronnummer} den {formatted_datetime_list[0]}'

st.markdown(f'**{nettsidetittel}:**')


## PLOTTTT
fig = px.line(empty_df, x='Temp', y='Lengde',title=tittel_2, color_discrete_sequence=['#367A2F', '#FFC358'])
for k in range(0,len(df_liste_slutt)):
    fig.add_trace(px.line(df_liste_slutt[k], x='Temp', y='Dybde', color_discrete_sequence=[colors[k]]).data[0])

#if sammenlikn and sammenlikn_fil:
#    fig.add_trace(px.line(grov_temp, x='Temp', y='Dybde', color_discrete_sequence=['#FFC358']).data[0])

fig.update_layout(xaxis_title='Temperaturmåling (\u2103)', yaxis_title='Dybde (m)',legend_title=None)
fig.update_layout(height=600)
fig.update_yaxes(autorange="reversed")
fig.update_xaxes(range=[min_x, maks_x])

fig.update_layout(xaxis_title='Temperaturmåling (°C)', yaxis_title='Dybde (m)', height=600)

yticks_interval = 10
yticks_values = list(range(int(df_slutt['Dybde'].min()), int(df_slutt['Dybde'].max())+10, yticks_interval))
fig.update_yaxes(tickvals=yticks_values, ticktext=yticks_values)

xticks_interval = 1
xticks_values = list(range(int(min_x), int(maks_x)+1, xticks_interval))
fig.update_xaxes(tickvals=xticks_values, ticktext=xticks_values)

fig.update_layout(
    title_font=dict(color='black'),
    xaxis=dict(title_font=dict(color='black'), tickfont=dict(color='black')),
    yaxis=dict(title_font=dict(color='black'), tickfont=dict(color='black')),
    paper_bgcolor='white',  # Set the background color of the plot
    plot_bgcolor='white',   # Set the background color of the plot area
)

st.plotly_chart(fig)


# Create an in-memory buffer
buffer = io.BytesIO()

# Save the figure as a pdf to the buffer
fig.write_image(file=buffer, format="png")

# Download the pdf from the buffer
if sammenstilling == True:
    st.download_button(
        label="Last ned figuren over som PNG",
        data=buffer,
        file_name=f"Temp_{valgt_bronn}_flere_kurver.png",
        mime="application/png",
    )
else:
        st.download_button(
        label="Last ned figuren over som PNG",
        data=buffer,
        file_name=f"Temp_{valgt_bronn}_{formatted_datetime_list[0]}.png",
        mime="application/png",
    )



