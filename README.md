# Graf Lab

Graf Lab je modularna Python aplikacija za učitavanje, obradu, pretragu, filtriranje i vizualizaciju grafova.

Projekat se razvija u okviru predmeta **Softverski obrasci i komponente** na Fakultetu tehničkih nauka u Novom Sadu.

## Tehnologije

- Python 3.12+
- Django (web aplikacija, planirano)
- D3.js (vizualizacija, planirano)
- pytest (automatsko testiranje)

## Arhitektura

Projekat je organizovan u nezavisne komponente:

- **API (`graf_lab_api`)** — generički model grafa i interfejsi pluginova.
- **Core (`graf_lab_core`)** — poslovna logika, pretraga, filtriranje i upravljanje pluginovima.
- **Data Source pluginovi** — učitavanje podataka iz JSON i XML dokumenata.
- **Visualizer pluginovi** — Simple i Block prikaz grafa.
- **Web aplikacija** — Django korisnički interfejs.

API i Core su zasebni Python paketi. Pluginovi će se razvijati kao nezavisni instalabilni paketi.

## Postavljanje razvojnog okruženja

### Preduslovi

- Python 3.12 ili noviji
- Git

### 1. Kloniranje repozitorijuma

```cmd
git clone <https://github.com/CodeByNedo/graf-lab.git>
cd graf-lab
```

### 2. Kreiranje virtuelnog okruženja

Windows CMD:

```cmd
python -m venv .venv
.venv\Scripts\activate.bat
```

### 3. Instalacija paketa

```cmd
python -m pip install --upgrade pip
python -m pip install -e ./api
python -m pip install -e ./platform --no-deps
python -m pip install pytest
```

API i Core se instaliraju u editable režimu, tako da se promjene izvornog koda odmah koriste u lokalnom okruženju.

Opcija `--no-deps` koristi se pri lokalnoj instalaciji Core paketa jer je njegova zavisnost `graf-lab-api` prethodno instalirana iz lokalnog direktorijuma.

### 4. Pokretanje testova

```cmd
python -m pytest -v
```

Trenutni početni testovi provjeravaju da li se API i Core paketi mogu uspješno učitati.

## Razvoj

Razvoj funkcionalnosti organizuje se kroz GitHub Issues, zasebne feature grane i Pull Requestove.

Početna verzija projekta sadrži konfiguraciju Python paketa i testnog okruženja. Model grafa, Core servisi, pluginovi i web aplikacija biće implementirani u narednim fazama.