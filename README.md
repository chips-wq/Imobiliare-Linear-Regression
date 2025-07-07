# Exercițiu EDA

Setul de date a fost extras de pe site-ul https://www.imobiliare.ro/ în anul 2023 și are ca scop determinarea prețului de vânzare a unei case în funcție de diverse caracteristici. 

## Cerințe

- Determinați tipurile de date ale fiecărei coloane
- Identificați dacă există exemple duplicate. Dacă există, eliminați-le.
- Identificați și eliminați coloanele care nu aduc informații relevante (e.g. `url`)
- Unele coloane au valori care au fost extrase eronat (e.g. coloana `Accesinternet` poate avea valoarea **'Ferestre cu 
  geam termopan'**). Identificați aceste valori și eliminați-le
- Există coloane care au ca valori liste de obiecte. De exemplu, coloana `Accesinternet` are valori de forma 
  **['Cablu', 'Fibra optica', 'Wireless', 'Dial-up']**. Determinați un mod prin care să evaluați aceste tipuri de date
- Există coloane care au valori numerice continue, dar sunt de tip obiect (e.g. coloana `Suprafaţăutilă` conține și 
  unitatea de măsură). Convertiți aceste valori în tipul numeric
- Identificați și tratați valorile lipsă
- Identificați care coloane sunt redundante și explicați de ce
- Determinați dacă există anomalii în date (`outliers`). Dacă există, tratați-le
- Determinați distribuția datelor. Coloana atributului țintă este `price`