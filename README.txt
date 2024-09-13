Auteur: Adam Taheraly
Contact: taheraly.adam@gmail.com

Aim: The script "distribution_student.py" aim to distribute a list 
     of student of different level between different group of similar 
     level and size. Each group is associated with a volunteer.

Prerequisite : module pandas and matplotlib.
	    

Input: file "liste_presence.csv" (separator ";") with 3 columns (noms, niveau, présent). 
       The column "noms" include the name of students and volunteers. The column "niveau" 
       include the level of the student or "bénévole" for the volunteers. The column "présent" 
       include 0 for people which are absent and 1 for the present ones.

Output: "repartition_eleve_AAAAMMJJ.pdf" file containing a table with the list of 
        present student in each row and the present volunteer in each column.
	For each volunteer, associated students are marked with a red cell containing 1. 
	Non-associated	student are marked with a white cell containing a 0. 
	
Steps:
1) If necessary, update the name of students and volunteers in the "liste_presence.csv".
2) Replace all 1 by 0.
3) For each present students and volunteers, replace 0 by 1 in the "présent" column.
2) Save file(format "csv UTF8, separator ";")
3) Check if an old version of the output file 
   "repartition_eleve_AAAAMMJJ.pdf" is not open. If open,
   close it.
4) Double click on (or run) the file "distribution_student.py"
5) Open the file "repartition_eleve_AAAAMMJJ.pdf"
