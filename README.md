# Resources used

[CS 229 Stanford 2019 Lectures 1-3 Review and Lecture 4 Linear Regression](https://www.youtube.com/watch?v=lNHaZlZJATw&list=PLoROMvodv4rNH7qL6-efu_q2_bPuy0adh&index=4)

# Definiția generală a ipotezei

$$
h_\theta(x) = \theta_0 + \sum_{i=1}^n \theta_i\ \cdot x_i
$$

unde

- $x = (x_1, x_2, \dots, x_n)$ este vectorul de caracteristici,
- $\theta = (\theta_0, \theta_1, \dots, \theta_n)$ sunt parametrii estimați.

# Variabilele selectate

Pentru simplitate, păstrăm doar variabilele:

1. **Etaj**: $x_1$
2. **Număr de băi**: $x_2$
3. **Număr de camere**: $x_3$, cu restricție $x_3 \le 5$
4. **Suprafață utilă**: $x_4$, eliminăm valorile extreme $>300\ \mathrm{m}^2$
5. **Tip imobil** (one-hot):
   - $x_5 = \mathbf{1}_{\{\text{apartament}\}}$
   - $x_6 = \mathbf{1}_{\{\text{casă}\}}$
6. **Confort** (one-hot): $\mathbf{1}_{\{\mathrm{confort}_k\}}$ pentru fiecare nivel $k$
7. **Vechimea clădirii**: $x_7$ (ar fi trebuit transformari cu praguri non-liniare. Nu am contextul unui agent imobiliar sa le cunosc.)
8. **Compartimentare** (one-hot): de ex. `comp_circular`, `comp_decomandat`, `comp_nedecomandat`, `comp_semidecomandat`, `comp_vagon`
9. **Zonă/Sector** (one-hot)

**Suprafata construita** a fost scoasa pentru ca $Corr(construit, util) ~= 0.93$, deci
se rezuma la o combinatie liniara intre doi `theta` din ipoteza, care ar fi putut fi un singur `theta`, mai usor interpretabil.

# Modelul final

$$
h_\theta(x) = \theta_0 + \theta_1\ \cdot x_1 + \theta_2\ \cdot x_2 + \theta_3\ \cdot x_3 + \theta_4\ \cdot x_4 + \sum_{f \in F} \theta_f\ \cdot x_f
$$

unde $F$ este mulțimea tuturor caracteristicilor codificate one‑hot (tip imobil, confort, vechime cu praguri, compartimentare, zonare).

# One-hot encoding pentru locatii

Pentru a ne imagine de ce _functioneaza_ one hot-encoding la zone: E ca si cum in momentul cand un agent imobiliar aude de un anumit sector, isi face o estimatie a pretului.

Pariul nostru este ca exista un `theta_sector_i` care influenteaza corect si se rezuma
la o estimatie asemanatoare cu ce ar face un agent imobiliar.
