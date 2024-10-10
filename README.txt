Auteur: Adam Taheraly
Contact: taheraly.adam@gmail.com

Version 2

Aim: The script "distribution_student.py" aim to distribute a list 
     of student of different level between different group of similar 
     level and size. Each group is associated with a volunteer. If needed,
     two waves of student can be defined. A group of autonomous (associated
     with only one volunteer) can also be set up

Prerequisite : module pandas and matplotlib.
	    

Input: file "list_presence.csv" (separator ";") with 3 columns (Name, Level, Presence, Priority,
	Autonomous). 
       The column "Name" contains the name of students and volunteers. The column "Level" 
       contains the level of the student or "Volunteer" for the volunteers. The column "Presence"
       contains 0 for people which are absent and 1 for the present ones. The column "Priority"
       contains 1 for people who have to be in the first wave and 0 when it doesn't matter. The
       column "Autonomous" contains 0 for people who aren't autonomous and 1 for those who are.

Output: "repartition_eleve_AAAAMMJJ.pdf" file containing a table with the list of 
        present student in each row and the present volunteer in each column.
	For each volunteer, associated students are marked with a black cell containing 1. 
	Non-associated	student are marked with a white cell containing a 0. 
	
Steps:
1) If necessary, update the Name, Level, Priority and Autonomous columns
   of students and volunteers in the "list_presence.csv".
2) Replace all 1 by 0 in the Presence column.
3) For each present students and volunteers, replace 0 by 1 in the "Presence" columns.
2) Save file(format "csv UTF8, separator ";")
3) Check if an old version of the output file 
   "repartition_eleve_AAAAMMJJ.pdf" is not open. If open,
   close it.
4) Double click on (or run) the file "distribution_student.py"
5) Open the file "repartition_eleve_AAAAMMJJ.pdf"
