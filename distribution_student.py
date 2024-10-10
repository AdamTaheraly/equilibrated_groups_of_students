"""
Author: Adam Taheraly
Aim: Repartition of student among the volunteers (by wave)
Input: csv (separator: semicolon; digits: dot) with four column (Name, Level, Presence, Priority, Autonomous).
Output: List of student per volunteer (per wave)
"""

import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
import numpy as np
import pandas as pd
import time


def filter_present(csv):
    """
    Filter out students and volunteers who are present from the list of people. Discriminate between the one associated
    with the autonomous group if necessary.
    """
    # Filter present students and volunteers.
    present_students = csv[(csv['Presence'] == 1) & (csv['Level'] != 'Volunteer')]
    present_volunteers = csv[(csv['Presence'] == 1) & (csv['Level'] == 'Volunteer')]

    # Discriminate the autonomous ones with the ones who are not.
    present_students_autonomous = present_students[present_students["Autonomous"] == 1]
    if not present_students_autonomous.empty:
        present_students = pd.merge(present_students, present_students_autonomous, how='outer',
                                    indicator=True).query("_merge != 'both'").drop('_merge',
                                                                                   axis=1).reset_index(drop=True)

        present_volunteer_autonomous = present_volunteers.sample(n=1, replace=False)
        present_volunteers = pd.merge(present_volunteers, present_volunteer_autonomous, how='outer',
                                      indicator=True).query("_merge != 'both'").drop('_merge',
                                                                                     axis=1).reset_index(drop=True)
    else:
        present_students_autonomous = pd.DataFrame()
        present_volunteer_autonomous = pd.DataFrame()

    return present_students, present_students_autonomous, present_volunteers, present_volunteer_autonomous


class GroupingStudentsByVolunteers:

    def __init__(self, students, volunteers):
        self.students = students
        self.volunteers = volunteers
        self.nb_students = len(self.students)
        self.nb_volunteers = len(self.volunteers)

    def generate_groups(self):
        """
        Generate a DataFrame indicating the repartition of students among volunteers
        """

        def _distribute_students(students):
            """
            Function to distribute students between groups of similar level.
            """
            groups = []
            for _, group in students.groupby('Group'):
                groups.append(group)
            for student in students.itertuples():
                groups.sort(key=lambda x: len(x))

                smallest_group = groups[0]
                smallest_group = pd.concat([smallest_group, pd.DataFrame([student])], ignore_index=True)
                groups[0] = smallest_group
            return groups

        # Group students by level
        students_by_level = self.students.groupby('Level')
        # Create groups for each level
        groups = []
        students_copy = self.students.copy(deep=True)
        students_copy['Group'] = [i % self.nb_students for i in range(self.nb_students)]
        for _, _ in students_by_level:
            groups.extend(_distribute_students(students_copy))

        # Associate each group to a volunteer
        groups = [group.dropna() for group in groups]
        groups = pd.concat(groups).drop_duplicates(keep="first")
        assigned_volunteers = []
        for row in groups.itertuples(index=True, name='Pandas'):
            i = getattr(row, "Group")
            assigned_volunteers.append(self.volunteers.iloc[i % self.nb_volunteers]['Name'])
        groups["Volunteer"] = assigned_volunteers

        # Construct a DataFrame with name of rows and columns
        df_groups = pd.DataFrame(index=groups["Name"], columns=groups.Volunteer.sort_values().unique(), dtype=int)
        df_groups.insert(0, "Level", list(groups.Level))

        # Fill the DataFrame with 1 for existing values
        for Name, Volunteer in zip(groups.Name, groups.Volunteer):
            df_groups.at[Name, Volunteer] = 1

        # Formatting of the DataFrame
        df_groups = df_groups.replace(np.nan, '', regex=True)
        df_groups = df_groups.reset_index()

        return df_groups


class PdfOutput:
    """
    Construct a pdf file containing tables 
    """
    def __init__(self):
        pass

    def dimension(self, width=8.27, height=11.69):
        """
        Construct a figure of defined dimension (in inches)
        """
        fig, ax = plt.subplots(figsize=(width, height))
        return fig, ax

    def table(self, dataframe, title, color="black", ):
        """
        Convert DataFrame in formatted table for export
        """
        # Color cell containing 1 in red
        colors = [[color if val == 1 else 'white' for val in row] for row in dataframe.values]

        # Suppress labels of axes
        ax.axis('tight')
        ax.axis('off')

        # Adjust the column width
        col_widths = [0.2] + [0.11] * (len(dataframe.columns) - 1)

        # Construct the table
        table = ax.table(cellText=dataframe.values,  # df.values
                         colLabels=dataframe.columns.tolist(),  # Include column names (df.columns.tolist())
                         cellColours=colors,
                         colWidths=col_widths,  # Define columns width
                         cellLoc='center',  # Center text in cells
                         loc='center')
        # Adjust the font size
        table.auto_set_font_size(False)
        table.set_fontsize(8)
        plt.title(title)
        plt.close()

    def output(self, figs):
        """
        Create pdf file with one figure per page
        """
        # Save in a pdf file
        daystr = time.strftime("%Y%m%d")
        filename = "repartition_student_" + daystr + ".pdf"
        with PdfPages(filename) as pdf:
            for fig in figs:
                pdf.savefig(fig, bbox_inches='tight')


# open CSV file
data = pd.read_csv("list_presence.csv", sep=";")

# Initialize PDF export
figs, ax = [], []
output = PdfOutput()

# Filter present peoples and autonomous ones
students, students_autonomous, volunteers, volunteer_autonomous = filter_present(data)

# Construct tables with 2 waves if needed else only one
if any(data["Priority"]):
    # Identify the number of students by wave
    nb_students_by_wave = len(students) // 2

    # get students of the first wave
    students_with_priority = students[(students['Priority'] == 1)]
    if len(students_with_priority) < nb_students_by_wave:
        # Get priority student and complete wave with other remaining student
        nb_slots_remaining = nb_students_by_wave - len(students_with_priority)
        remaining_students = pd.merge(students_with_priority, students, how='outer',
                                      indicator=True).query("_merge != 'both'").drop('_merge',
                                                                                     axis=1).reset_index(drop=True)
        selected_supplementary_students = remaining_students.sample(n=nb_slots_remaining, replace=False)
        students_first_wave = pd.concat([students_with_priority, selected_supplementary_students])
    else:
        # Get priority student
        students_first_wave = students_with_priority

    # create group for student wave 1
    first_wave = GroupingStudentsByVolunteers(students_first_wave, volunteers)
    df_first_wave = first_wave.generate_groups()

    # get students of the second wave
    students_second_wave = pd.merge(students, students_first_wave, how='outer',
                                    indicator=True).query("_merge != 'both'").drop('_merge',
                                                                                   axis=1).reset_index(drop=True)

    # create group for student wave 2
    second_wave = GroupingStudentsByVolunteers(students_second_wave, volunteers)
    df_second_wave = second_wave.generate_groups()

    # generate output with table of wave 1 and 2
    fig, ax = output.dimension()
    output.table(df_first_wave, "Grouping for the first wave")
    figs.append(fig)

    fig, ax = output.dimension()
    output.table(df_second_wave, "Grouping for the second wave")
    figs.append(fig)

else:
    # create group of student
    general_grouping = GroupingStudentsByVolunteers(students, volunteers)
    df_general_grouping = general_grouping.generate_groups()

    # generate output with table
    fig, ax = output.dimension()
    output.table(df_general_grouping, "Grouping without priority students")
    figs.append(fig)

# Construct a table for the autonomous group if needed
if not students_autonomous.empty:
    df = pd.DataFrame(index=students_autonomous.Name, columns=volunteer_autonomous.Name, dtype=int)
    df[volunteer_autonomous.Name] = 1
    df = df.reset_index()

    fig, ax = output.dimension()
    output.table(df, 'Autonomous student')
    figs.append(fig)

# Generate PDF export
output.output(figs)
