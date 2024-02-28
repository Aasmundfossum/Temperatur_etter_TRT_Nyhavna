import pandas as pd 
from mpl_toolkits.mplot3d import Axes3D
import numpy as np
import matplotlib.pyplot as plt

# Create an empty DataFrame to store the combined data
df_combined = pd.DataFrame(columns=["Station", "East", "North"])

# Create a list of sheet names to read data from
sheet_names = ["B3", "B4", "B5", "B6"]  # Adjust sheet names accordingly

# Read data from each sheet and append to the combined DataFrame
df_list = []

for sheet_name in sheet_names:
    df = pd.read_excel("Borehullsavvikmålinger.xlsx", sheet_name=sheet_name, skiprows=3)
    df = df.iloc[1:, :]
    df['East'] = df['East'].abs()
    df['North'] = df['North'].abs()
    df = df[["Station", "East", "North"]]  # Select relevant columns
    df_combined = pd.concat([df_combined, df], ignore_index=True)
    df_list.append(df)

fig = plt.figure()
ax = fig.add_subplot(111, projection='3d')

z_max = max(df_combined["Station"])

ax.set_xlim(0, 100)  # Set limits for x-axis
ax.set_ylim(0, 100)  # Set limits for y-axis
ax.set_zlim(0, 200)  # Set limits for z-axis
ax.set_xlabel('Vest (m)')
ax.set_ylabel('Sør (m)')
ax.set_zlabel('Dybde (m)')

ax.xaxis.set_ticks(np.linspace(ax.get_xlim()[0], ax.get_xlim()[1], 5))
ax.yaxis.set_ticks(np.linspace(ax.get_ylim()[0], ax.get_ylim()[1], 5)) # Sett 5 akse-labels på x- og y-aksen

ax.set_zlim(z_max, 0)  # Setting z-axis limits in reverse order
colors = ['#FFC358', '#b7dc8f', '#48a23f', '#1d3c34']  # Hexadecimal color

for i in range(0,len(df_list)):
    z = df_list[i]["Station"]
    x = df_list[i]["East"]
    y = df_list[i]["North"]
    ax.scatter(x, y, z, c=colors[i])  # Use 'c' parameter to specify colors
    ax.plot(df_list[i]['East'], df_list[i]['North'], df_list[i]['Station'], color=colors[i], label=f'B{i+3}')

#for sheet_name in sheet_names:
#    df_sheet = df_combined[df_combined['Station'] == sheet_name]
#    ax.scatter(df_sheet['East'], df_sheet['North'], df_sheet['Station'], label=sheet_name)
#    ax.plot(df_sheet['East'], df_sheet['North'], df_sheet['Station'], label='_nolegend_')  # No legend for lines

ax.set_title('Borehullsavvik fra B3, B4, B5, and B6')
ax.set_box_aspect([0.5,0.5,1])  # Bestem relativ størrelse i hver retning til plottet
ax.legend()
plt.show()
