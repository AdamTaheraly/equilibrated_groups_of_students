""""
Author: Adam Taheraly
Aim: Repartition of student among the volunteers.
Input: csv (separator: semicolon; digits: dot) with three column (Nom, Type, Presence).
Output: List of student per volunteer
"""
import pandas as pd
from collections import defaultdict
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
import time
#import sys



# open CSV file
#file_name = sys.argv[1]
data = pd.read_csv("liste_presence.csv", sep = ";")
#data = pd.read_csv("presence.csv")


# Filter present students and volunteers.
eleves_presents = data[(data['présent'] == 1) & (data['niveau'] != 'Bénévole')]
benevoles_presents = data[(data['présent'] == 1) & (data['niveau'] == 'Bénévole')]


# Count the total number of present volunteers.
nb_benevoles = len(benevoles_presents)

# Count the total number of present students.
nb_eleves = len(eleves_presents)

# Count the number of student per volunteer
nb_eleves_par_groupe = nb_eleves // nb_benevoles

# Construct groups per level.
groupes_par_niveau = eleves_presents.groupby('niveau')

# Function to distribute students between groups of similar level.
def repartir_dans_groupes(eleves, nb_eleves_par_groupe):
    groupes = []
    for _, groupe in eleves.groupby('groupe'):
        groupes.append(groupe)
    for eleve in eleves.itertuples():
        groupes.sort(key=lambda x: len(x))
        groupe_plus_petit = groupes[0]
        groupe_plus_petit = pd.concat([groupe_plus_petit, pd.DataFrame([eleve])], ignore_index=True)
        groupes[0] = groupe_plus_petit
    return groupes


# Count the number of needed groups
nb_groupes = nb_benevoles

# Create groups for each level
groupes = []
for niveau, eleves in groupes_par_niveau:
    # Count the number of student per group
    nb_eleves_par_groupe = len(eleves) // nb_groupes
    eleves['groupe'] = [i % nb_eleves for i in range(len(eleves))]
    groupes.extend(repartir_dans_groupes(eleves, nb_eleves_par_groupe))

# Associate each group to a volunteer
for i, groupe in enumerate(groupes):
    groupe['Bénévole'] = benevoles_presents.iloc[i % nb_benevoles]['nom']

benevole = defaultdict(list)
for groupe in groupes:
    benevole[groupe["Bénévole"][0]].append((groupe["nom"][0],groupe["niveau"][0]))

## Recover unique value
valeurs_uniques = sorted(set(val for sublist in benevole.values() for val in sublist))

# Construct a DataFrame with name of rows and columns 
df = pd.DataFrame(index=valeurs_uniques, columns=benevole.keys(), dtype=int)

# Fill the DataFrame with 1 for existing values
for groupe, membres in benevole.items():
    df[groupe] = df.index.isin(membres).astype(int)

# Add column with name of students
names = [name for name, niveau in df.index]  # Recover student names
niveau = [niveau for name, niveau in df.index]
df['Noms'] = names  # Add the name column
df['Niveau'] = niveau  # Add the level column
df.insert(0, 'Niveau', df.pop('Niveau'))
df.insert(0, 'Noms', df.pop('Noms'))

# Construct a figure of A4 page dimension (in inches)
fig_width = 8.27  # Largeur du papier A4 en pouces
fig_height = 11.69  # Hauteur du papier A4 en pouces
fig, ax = plt.subplots(figsize=(fig_width, fig_height))

# Color cell containing 1 in red
colors = [['red' if val == 1 else 'white' for val in row] for row in df.values]
# Suppress labes of axes
ax.axis('tight')
ax.axis('off')

# Adjust the column width
col_widths = [0.2]+ [0.11] * (len(df.columns) - 1)

# Construct the table
table = ax.table(cellText=df.values,
                 colLabels=df.columns.tolist(),  # Inclure les noms des colonnes
                 cellColours=colors,
                 colWidths=col_widths,  # Définir la largeur des colonnes
                 cellLoc='center',  # Aligner le texte au centre des cellules
                 loc='center')

# Adjust the font size
table.auto_set_font_size(False)
table.set_fontsize(8)
table.set

# Save in a pdf file
daystr = time.strftime("%Y%m%d")
filename = "repartition_eleve_" + daystr + ".pdf"
with PdfPages(filename) as pdf:
    pdf.savefig(fig, bbox_inches='tight')

plt.close(fig)
"""for key, value in benevole.items():
    print(key)
    list = []
    for val in value:
        list.append(val[1])
        print(val[0], val[1])
    print(Counter(list))"""
