import numpy as np
import pandas as pd
import streamlit as st
import plotly.express as px
from datetime import datetime
import os
import io

st.set_page_config(page_title="Data fra Nyhavna", page_icon="🔥")

with open("styles/main.css") as f:
    st.markdown("<style>{}</style>".format(f.read()), unsafe_allow_html=True)

st.title('Temperaturdata fra Nyhavna')
valgt_bronn = st.selectbox('Velg brønn',options=['B3_CH1','B3_CH2','B4','B5','B6'])

mappenavn = f'{valgt_bronn}_datafiler'

dir_list = os.listdir(mappenavn)

filnummer = st.slider('Filnummer',min_value=0,max_value=len(dir_list)-1,step=1)

filnavn = dir_list[filnummer]


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



#relevant_length = []
#relevant_temp = []
#for i in range(0,len(df)-3):
    #if df['Lengde'].iloc[i+1] - df['Lengde'].iloc[i] < 2:
    #    relevant_length.append(df['Lengde'].iloc[i])
    #    relevant_temp.append(df['Temp'].iloc[i])
#    if abs(df['Temp'].iloc[i+1] - df['Temp'].iloc[i]) < 1 and abs(df['Temp'].iloc[i+2] - df['Temp'].iloc[i]) < 1 and abs(df['Temp'].iloc[i+3] - df['Temp'].iloc[i]) < 1:
    
        #if abs(df['Temp'].iloc[i+1] - df['Temp'].iloc[i]) < 0.25: 
#        relevant_length.append(df['Lengde'].iloc[i])
#        relevant_temp.append(df['Temp'].iloc[i])

#df_ferdig = pd.DataFrame({'Lengde':relevant_length, 'Temp':relevant_temp})

df_ferdig = df


#for i in range(0,len(df_ferdig)-1):
#    if df_ferdig['Lengde'].iloc[i+1] - df_ferdig['Lengde'].iloc[i] > 10:
#        del1 = df_ferdig.iloc[:i]
#        del2 = df_ferdig.iloc[i+1:]
        
#        if len(del1)>2:
#            if abs(del1['Lengde'].iloc[-1]-del1['Lengde'].iloc[0]) > 70:
#                df_slutt = del1

#            elif abs(del2['Lengde'].iloc[-1]-del2['Lengde'].iloc[0]) > 70:
#                df_slutt = del2
#            break
#        elif abs(del2['Lengde'].iloc[-1]-del2['Lengde'].iloc[0]) > 70:
#                df_slutt = del2
#    else:
#        df_slutt = pd.DataFrame(columns=['Lengde','Temp'])
        #df_slutt = df_ferdig
        
#df_slutt = df_slutt.reset_index(drop=True)
df_slutt = df_ferdig

st.markdown('---')
st.subheader('Temperaturplot uten valgte aksegrenser:')

fig = px.line(df_ferdig, x='Temp', y='Lengde', title=f'Temperatur i brønn {valgt_bronn} den {formatted_datetime}', color_discrete_sequence=['#367A2F', '#FFC358'])
fig.update_layout(xaxis_title='Temperatur (\u2103)', yaxis_title='Dybde (m)',legend_title=None)
fig.update_layout(height=800)
fig.update_yaxes(autorange="reversed")
st.plotly_chart(fig)

st.markdown('---')
st.subheader('Temperaturplot med valgte aksegrenser og korrigert for brønndybde:')
c1, c2 = st.columns(2)
with c1:
    min_x = st.number_input('Minste verdi x-akse basert på figuren over:',value=-3.0,min_value=-20.0,max_value=20.0,step=0.1)
with c2:
    maks_x = st.number_input('Største verdi x-akse basert på figuren over:',value=3.0,min_value=-20.0,max_value=20.0,step=0.1)

c1, c2 = st.columns(2)
with c1:
    min_y = st.number_input('Minste verdi y-akse basert på figuren over:',value=-500,min_value=-1000,max_value=1000,step=1)
with c2:
    maks_y = st.number_input('Største verdi y-akse basert på figuren over:',value=500,min_value=-1000,max_value=1000,step=1)

til_figurtittel = st.text_input("Tillegg til figurtittel")


df_slutt = df_slutt[df_slutt['Lengde'] >= min_y] 
df_slutt = df_slutt[df_slutt['Lengde'] <= maks_y] 
df_slutt = df_slutt.reset_index(drop=True)

dybde = df_slutt['Lengde']-df_slutt['Lengde'].iloc[0]
df_slutt['Dybde'] = dybde

st.markdown('')
st.markdown(f'**Temperatur i brønn {valgt_bronn} den {formatted_datetime}:**')

fig = px.line(df_slutt, x='Temp', y='Dybde',title=f'Temperatur i testbrønn den {formatted_datetime} ({til_figurtittel})', color_discrete_sequence=['#367A2F', '#FFC358'])
fig.update_layout(xaxis_title='Temperatur (\u2103)', yaxis_title='Dybde (m)',legend_title=None)
fig.update_layout(height=600)
fig.update_yaxes(autorange="reversed")
fig.update_xaxes(range=[min_x, maks_x])

yticks_interval = 10
yticks_values = list(range(int(df_slutt['Dybde'].min()), int(df_slutt['Dybde'].max())+1, yticks_interval))
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
#fig.update_yaxes(range=[min_y-df_slutt['Lengde'].iloc[0], maks_y-df_slutt['Lengde'].iloc[0]])
st.plotly_chart(fig)



# Create an in-memory buffer
buffer = io.BytesIO()

# Save the figure as a pdf to the buffer
fig.write_image(file=buffer, format="png")

# Download the pdf from the buffer
st.download_button(
    label="Last ned figuren over som PNG",
    data=buffer,
    file_name=f"Temp_{valgt_bronn}_{formatted_datetime}.png",
    mime="application/png",
)



