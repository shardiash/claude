# MOVIA KOMMANDO – guide til AI

Du (AI'en) skal skrive EN JSON-fil, der hedder `kommando.json`. Brugeren
lægger den i `C:\Users\tacci\Documents\The Bus\MoviaTools\` og kører
`movia_kommando.py` i The Bus Modding Editor (Tools > Execute Python Script).
Den bygger/ændrer en skærm i busspillet "The Bus". Svar KUN med gyldig JSON.

## Format

```json
{
  "skaerm": "Passager",
  "layout": { ... },          // valgfri: byg hele skærmen forfra
  "aendringer": [ ... ]       // valgfri: små ændringer i eksisterende elementer
}
```

Brug enten `layout`, `aendringer` eller begge.

Skal flere skærme laves på én gang (fx `Main` OG `Header`), så skriv en
liste: `[ {"skaerm": "Main", ...}, {"skaerm": "Header", ...} ]`.

## Skærme

| skaerm | Størrelse (px) | Hvad |
|---|---|---|
| `Passager` | 1600 × 430 | Passagerskærmen i loftet |
| `Main` | 1200 × 764 | Chaufførens bordcomputer, når bussen holder stille |
| `Driving` | 1200 × 764 | Chaufførens bordcomputer, når bussen kører |
| `Header` | 900 × 100 | Bordcomputerens topbjælke (ur, forsinkelse, linje). Den er FÆLLES for alle bordcomputer-skærme |
| `StopRaekke` | – | Én række i passagerskærmens stopliste (kun `aendringer`) |
| `Startup` | 1200 × 764 | Bordcomputerens opstartsskærm (kun `aendringer`) |

Alle skærme undtagen StopRaekke og Startup kan bygges med `layout`.

## layout

```json
"layout": {
  "w": 1600, "h": 430, "bg": "#FFFFFF",
  "items": [ element, element, ... ]
}
```

Elementer tegnes i rækkefølge: første = bagerst, sidste = forrest.
x/y er øverste venstre hjørne i pixels. Farver er hex: `"#RRGGBB"`.

### Element-typer

**Fast tekst**
```json
{"type": "text", "name": "Overskrift", "x": 806, "y": 22, "text": "Næste stop",
 "size": 18, "color": "#333333", "bold": false}
```

**Datafelt** (tekst som spillet selv opdaterer – brug ALTID dette til rigtige data)
```json
{"type": "text", "name": "Næste stop", "x": 942, "y": 18, "data": "NaesteStop",
 "size": 40, "color": "#1D1D1D", "bold": true}
```
Tilladte `data` afhænger af skærmen:

| skaerm | Tekst-datafelter (`"type": "text"`) | Område-datafelter (`"type": "box"`) |
|---|---|---|
| `Passager` | `NaesteStop`, `SidsteStop`, `Linje`, `Ur` | `StopListe` |
| `Header` | `Ur`, `Forsinkelse`, `Dato`, `LinjeDestination` | – |
| `Main` | – | `Header`, `StopListe` |
| `Driving` | – | `Header` |

- `Forsinkelse` = spillets forsinkelse/før tid, fx "-0:01:35" (spillet farver den selv)
- `LinjeDestination` = linje og endestation i én tekst, fx "498 - S OSTBAHNHOF"
- `Header` (på Main/Driving) = hele topbjælken som én blok. Dens indhold
  designes separat med `"skaerm": "Header"`.
- `StopListe` = spillets egen stopliste, som opdaterer sig selv.

**Boks**
```json
{"type": "box", "name": "Topfelt", "x": 790, "y": 0, "w": 810, "h": 92, "color": "#F3F4F5"}
```

**Boks der skifter farve ved en tilstand**
```json
{"type": "box", "name": "STOP-felt", "x": 790, "y": 93, "w": 152, "h": 136,
 "color": "#111111", "color_on": "#E2231A", "state": "StopOenske"}
```
Tilladte `state`: `StopOenske` (en passager har trykket stop). Brug højst én
boks med `StopOenske` pr. skærm.

**Dataområde** (et område spillet fylder ud)
```json
{"type": "box", "name": "Stopliste", "x": 960, "y": 100, "w": 620, "h": 320,
 "color": "#FFFFFF", "data": "StopListe"}
```
Tilladte `data` for bokse: `StopListe` – spillets liste over kommende stop.

**Billede**
```json
{"type": "box", "name": "Reklame", "x": 0, "y": 0, "w": 790, "h": 430,
 "color": "#FFFFFF", "image": "T_Reklame_Aeblefest"}
```
`image` kan være et billednavn der allerede er i modden
(`T_Reklame_Aeblefest`, `T_Reklame_Boennebaren`, `T_Movia_Kort`, `ikon_bus`,
`ikon_metro`, `ikon_stoppested`, `ikon_bus_position`) eller en fuld sti til en
PNG på brugerens computer, fx `"C:\\Users\\tacci\\Pictures\\logo.png"` –
den importeres automatisk.

**Spil-element** (et hvilket som helst eksisterende element fra spillet)
```json
{"type": "box", "name": "Knapper", "x": 0, "y": 680, "w": 1200, "h": 84, "spil": "ElementNavn"}
```
Flytter spillets eget element hen på pladsen (fx bordcomputerens knapper).
`ElementNavn` skal være det præcise navn fra Hierarchy – kør
`{"funktion": "vis_elementer"}` for at få listen. Brug kun navne du kender.

Valgfrit på alle elementer: `"hidden": true` (skjult i spillet).

### Hvad sker der med spillets gamle layout?
Alt, du ikke har koblet eller nævnt, bliver skjult. Skal noget af det gamle
blive stående (fx knapperne nederst på bordcomputeren), så skriv navnene i
`"behold": ["ElementNavn", ...]` inde i `layout`. VIGTIGT på `Main` og
`Driving`: bordcomputerens knapper skal flyttes med et spil-element eller
beholdes, ellers kan chaufføren ikke betjene den.

## aendringer

Små ændringer i spillets eksisterende elementer. `element` er navnet fra
Hierarchy i editoren (spørg brugeren, eller kør `vis_elementer` først).

```json
"aendringer": [
  {"funktion": "vis_elementer"},
  {"funktion": "tekst",          "element": "TextBlock_98", "vaerdi": "Næste stop"},
  {"funktion": "tekstfarve",     "element": "TextBlock_98", "vaerdi": "#333333"},
  {"funktion": "skrift",         "element": "TextBlock_98", "vaegt": "Bold", "stoerrelse": 30},
  {"funktion": "farve",          "element": "Image_0",      "vaerdi": "#F3F4F5"},
  {"funktion": "billede",        "element": "Image_Reklame", "vaerdi": "/Game/MoviaSkaerme/T_Reklame_Boennebaren"},
  {"funktion": "skjul",          "element": "Image_2"},
  {"funktion": "vis",            "element": "Image_2"},
  {"funktion": "gennemsigtighed","element": "Image_2", "vaerdi": 0.5}
]
```
`vaegt`: `Regular`, `Medium`, `SemiBold`, `Bold`, `ExtraBold`.
Hver ændring kan have sin egen `"skaerm"`, ellers bruges den øverste.

Kendte elementnavne på `Passager`: `Text_NextBusStop`, `Text_Busline`,
`Text_Destination`, `Text_Time`, `Image_Reklame`, `Image_0` (topfeltets baggrund),
`Image_3` (STOP-feltets farve), `Border_1` (STOP-feltets sorte baggrund),
`TextBlock_0` (teksten "STOP"), `Vertical_NextNextObjects` (stoplisten).

## regler (ting der ændrer sig mens man kører)

Læg `"regler"` (liste) inde i `"layout"`. Hver regel tjekkes hele tiden i spillet.
`element` = `name` på et element i samme layout (giv elementerne unikke navne!).

### hvis – rigtige udtryk
Skriv betingelsen som tekst:
```
"hvis": "Forsinkelse > 60"
"hvis": "Forsinkelse > 60 og Linje = '5C'"
"hvis": "Forsinkelse < -60 eller Forsinkelse > 120"
"hvis": "NaesteStop indeholder 'St.'"
"hvis": "Forsinkelse / 60 >= 2"
"hvis": "(Tid % 20) < 10"
```
- Sammenlign: `>  <  >=  <=  =  !=`, og tekst med `indeholder`
- Kombinér: `og`, `eller`, `ikke`, parenteser
- Regning: `+ - * /` og `%` (rest – sæt den til sidst). Kun ét datafelt pr. sammenligning.
- Tekst i 'enkelte anførselstegn'.
- Udelad `hvis` = gælder altid.

### Datafelter i regler
| navn | skærm | hvad |
|---|---|---|
| tekst-datafelterne (`NaesteStop`, `Linje`, `SidsteStop`, `Ur` …) | den skærm de hører til | spillets egen tekst (tal i teksten kan regnes med) |
| `Forsinkelse` | **Header**, **Driving** | sekunder, positiv = forsinket, negativ = for tidlig |
| `NaesteTid` | **Driving** | planlagt ankomst ved næste stop, sekunder efter midnat (format `hh:mm:ss`) |
| `SidsteTidSek` | **Driving** | planlagt ankomst ved sidste stop (endestation), sekunder efter midnat |
| `SidsteStopNavn` | **Driving** | navnet på sidste stop (tekst) |
| `NaesteStopNavn` | **Driving** | navnet på næste stop – bliver ved det stop bussen holder ved, indtil den kører igen (tekst) |
| `NaesteAfgang` | **Driving** | planlagt AFGANG fra næste stop, sekunder efter midnat (format `hh:mm:ss`) |
| `HolderVedStop` | **Driving** | 1 når bussen holder stille (under 3 km/t) ved et stop ifølge spillet, ellers 0 (bruges til at vise/skjule "Tag afgang"-boksen) |
| `AktuelAfgang` | **Driving** | planlagt afgang fra det stop bussen holder ved, sekunder efter midnat (format `hh:mm:ss`), 0 hvis ikke ved et stop |
| `LinjeNr` | **Driving** | linjenummer (tekst, fx 5C) |
| `Minutter1`, `Minutter2`, `Minutter3` | **Passager** | minutter til 1., 2. og 3. stop ifølge køreplanen |
| `Forventet1`, `Forventet2`, `Forventet3` | **Passager** | forventede minutter: køreplan rettet efter hvor langt bussen er fra næste stop (forsinkelse lægges til / trækkes fra) |
| `Afstand` | **Passager** | meter (i luftlinje) fra bussen til næste stop |
| `Linje1_1` … `Linje3_5` | **Passager** | andre buslinjer ved stop 1–3 (op til 5 pr. stop, din egen linje er fjernet). Tom tekst = ingen. Fx `Linje2_1` = første andre linje ved 2. stop |
| `AfgLinje1` … `AfgLinje8` | **Passager** | afgangstavle: linjenummer for de næste busser ved det stop bussen er ved/kommer til (tekst) |
| `AfgTil1` … `AfgTil8` | **Passager** | afgangstavle: destination (tekst) |
| `AfgMin1` … `AfgMin8` | **Passager** | afgangstavle: minutter til afgang |
| `VedStop` | **Passager** | 1 når bussen holder stille (under 3 km/t) ved et stop (spillet siger "ved stop"), ellers 0. Som tekst: fart + * ved stop (fejlsøgning) |
| `Klokken` | alle | spillets ur i minutter efter midnat (brug format `hh:mm`) |
| `KlokkeSek` | alle | spillets ur i sekunder efter midnat (brug format `hh:mm:ss`) |
| `Tid` | alle | sekunder siden spillet startede (til blink/sider) |

`Forsinkelse` findes IKKE på `Main` – lav forsinkelses-regler på skærmen `Header` eller `Driving`.
Kommer senere (virker IKKE i regler endnu): `Hastighed`, `Doere`, `Blinklys`, `Passagerer`, `StopOenske`.
(`StopOenske` virker allerede som `"state"` på en boks – se layout.)

### saet – hvad der sker
| saet | til / ellers |
|---|---|
| `farve` | #RRGGBB (boks) |
| `tekstfarve` | #RRGGBB |
| `tekst` | tekst, må have ÉN `{udtryk:format}` – se nedenfor |
| `vis` / `skjul` | (ingen) – gør det modsatte når hvis er falsk |
| `opacity` | 0 til 1 |
| `billede` | billednavn (fx `T_Reklame_Aeblefest`) |
| `blink` | blinker mens hvis er sand. `"periode": 1` (sek), `"min": 0` |
| `flytx` / `flyty` | forskyd elementet vandret/lodret i pixels (fx `"til": 0, "ellers": -120`). Med `glid` glider det |

`"ellers"`: værdi når hvis er falsk. `"glid": 0.5`: blød overgang i sekunder – på `vis`/`skjul`/`opacity` en fade, på `farve` (bokse) en blød farvetoning, på `flytx`/`flyty` en glidende bevægelse.

Eksempel – boks der glider ind fra venstre og toner frem, når bussen holder ved et stop:
```json
{"hvis": "HolderVedStop = 1", "saet": "vis", "element": "AfgangBoks", "glid": 0.25},
{"hvis": "HolderVedStop = 1", "saet": "flytx", "element": "AfgangBoks", "til": 0, "ellers": -120, "glid": 0.25}
```

### tekstformatering
```
"til": "{Forsinkelse / 60 : fortegn} min"   ->  "+2 min"
"til": "{Forsinkelse : mm:ss}"              ->  "01:30"
"til": "{Forsinkelse : m:ss}"               ->  "+0:16" / "-2:48" (med fortegn)
"til": "{KlokkeSek : hh:mm:ss}"            ->  "07:31:05"
"til": "Kl. {Ur}"                           ->  rå tekst
```
Formater: `raa`, `heltal`, `1dec`, `fortegn`, `mm:ss`, `hh:mm`, `m:ss` (med fortegn), `hh:mm:ss`.

### sider (skift mellem visninger)
```json
"sider": {"skift_hver": 10, "glid": 0.5, "sider": [["Stopliste", "Tidslinje"], ["Reklame2"]]}
```
Læg `"sider"` i `"layout"`. Hver side er en liste af elementnavne.

### z (lagdeling)
Alle elementer kan have `"z": 10`. Højere tal ligger øverst. Uden z = rækkefølgen i listen.

### Eksempel
```json
"regler": [
  {"hvis": "Forsinkelse > 60 eller Forsinkelse < -60", "saet": "farve",
   "element": "StatusBoks", "til": "#DE3B26", "ellers": "#3FA535", "glid": 0.3},
  {"saet": "tekst", "element": "ForsinkelseTekst", "til": "{Forsinkelse / 60 : fortegn} min"},
  {"hvis": "Forsinkelse > 120", "saet": "blink", "element": "Advarsel", "periode": 0.8}
]
```
(Eksemplet ovenfor hører til skærmen `Header`, fordi det bruger Forsinkelse.)

### Eksempel: rigtige minutter i passagerskærmens stopliste
Lav tre tekst-elementer ("Minutter 1-3") ud for stoplistens prikker og giv dem en regel:
```json
"regler": [
  {"saet": "tekst", "element": "Minutter 1", "til": "{Minutter1:heltal} min"},
  {"saet": "tekst", "element": "Minutter 2", "til": "{Minutter2:heltal} min"},
  {"saet": "tekst", "element": "Minutter 3", "til": "{Minutter3:heltal} min"}
]
```
Mere realistisk – forventet tid og "Nu" når bussen er tæt på (sidste regel vinder):
```json
"regler": [
  {"saet": "tekst", "element": "Minutter 1", "til": "{Forventet1:heltal} min"},
  {"saet": "tekst", "element": "Minutter 2", "til": "{Forventet2:heltal} min"},
  {"saet": "tekst", "element": "Minutter 3", "til": "{Forventet3:heltal} min"},
  {"hvis": "Afstand < 150 eller Forventet1 < 0.5", "saet": "tekst", "element": "Minutter 1", "til": "Nu"}
]
```

### Eksempel: ur og skift mellem stopliste og reklame
```json
"regler": [{"saet": "tekst", "element": "Ur", "til": "{Klokken:hh:mm}"}],
"sider": {"skift_hver": 10, "glid": 0.5, "sider": [["Stopliste", "Tidslinje"], ["Reklame2"]]}
```

Regel-motoren (WBP_MoviaMotor) sættes automatisk ind på skærmen, når kommandoen køres.
Programmet gemmes også i `program_<skaerm>.txt`, så man kan se hvad der blev lavet.

## aendringer – ekstra funktioner
Ud over dem ovenfor: `hoejde` (Spacer/SizeBox, vaerdi = tal), `klip` (klip indhold),
`juster` (vaerdi: top/midt/bund/fyld), `egenskab` (vaerdi: {"navn": ..., "vaerdi": ...}).

### Stoplistens rækker (skaerm `StopRaekke`)
En stoprække består af: `SizeBox_0` (prik + navn), `Image_2` (prikken), `TextBlock_4` (stopnavnet),
`HorizontalBox_5` + `Spacer_2` (skiftemuligheder – giver hul, hold dem skjult/0) og
`Spacer_4` (luft under rækken = afstanden mellem stop).
```json
{"skaerm": "StopRaekke", "aendringer": [
  {"funktion": "skjul",  "element": "HorizontalBox_5"},
  {"funktion": "hoejde", "element": "Spacer_2", "vaerdi": 0},
  {"funktion": "hoejde", "element": "SizeBox_0", "vaerdi": 56},
  {"funktion": "klip",   "element": "SizeBox_0"},
  {"funktion": "juster", "element": "TextBlock_4", "vaerdi": "top"},
  {"funktion": "hoejde", "element": "Spacer_4", "vaerdi": 147}
]}
```
Større `Spacer_4` = mere luft mellem stoppene. Spillet viser altid 3 stop.

## Movia-farver

Movia-gul `#FFC20E`, STOP-rød `#E2231A`, sort `#111111`, mørk tekst `#1D1D1D`,
grå tekst `#333333`, lysegrå tekst `#8A8F94`, lysegrå baggrund `#F3F4F5`,
grøn `#3FA535`, rød `#DE3B26`, mørkeblå `#233257`.
Skrifttype er altid Inter (vælges automatisk).

## Det kan IKKE lade sig gøre (lov det ikke)

- Andre datafelter end dem der står ovenfor (fx vejr, rigtigt GPS-kort, fart – fart kommer senere)
- Flere end 3 stop i passagerskærmens stopliste
- Live data fra internettet (vejr, nyheder) – spillet kan ikke hente web-data

## Eksempel: bordcomputer (Main) i Movia-stil

```json
{
  "skaerm": "Main",
  "layout": {
    "w": 1200, "h": 764, "bg": "#233257",
    "items": [
      {"type": "box", "name": "Kort", "x": 0, "y": 0, "w": 1200, "h": 764, "color": "#FFFFFF", "image": "T_Movia_Kort"},
      {"type": "box", "name": "Topbjælke", "x": 0, "y": 0, "w": 1200, "h": 100, "color": "#0A0A0A", "data": "Header"},
      {"type": "box", "name": "Stopliste", "x": 20, "y": 120, "w": 460, "h": 540, "color": "#DE3B26", "data": "StopListe"}
    ]
  }
}
```

## Eksempel: topbjælken (Header)

```json
{
  "skaerm": "Header",
  "layout": {
    "w": 900, "h": 100, "bg": "#0A0A0A",
    "items": [
      {"type": "box", "name": "Baggrund", "x": 0, "y": 0, "w": 900, "h": 100, "color": "#0A0A0A"},
      {"type": "text", "name": "Linje og destination", "x": 20, "y": 30, "data": "LinjeDestination", "size": 30, "color": "#FFFFFF", "bold": true},
      {"type": "text", "name": "Ur", "x": 660, "y": 8, "data": "Ur", "size": 44, "color": "#FFFFFF"},
      {"type": "text", "name": "Forsinkelse", "x": 700, "y": 62, "data": "Forsinkelse", "size": 24, "color": "#FFFFFF"}
    ]
  }
}
```

## Komplet eksempel (Movia-passagerskærm)

```json
{
  "skaerm": "Passager",
  "layout": {
    "w": 1600, "h": 430, "bg": "#FFFFFF",
    "items": [
      {"type": "box", "name": "Reklame", "x": 0, "y": 0, "w": 790, "h": 430, "color": "#FFFFFF", "image": "T_Reklame_Aeblefest"},
      {"type": "box", "name": "Topfelt", "x": 790, "y": 0, "w": 810, "h": 92, "color": "#F3F4F5"},
      {"type": "text", "name": "Label DK", "x": 806, "y": 22, "text": "Næste stop", "size": 18, "color": "#333333"},
      {"type": "text", "name": "Label EN", "x": 806, "y": 46, "text": "Next stop", "size": 18, "color": "#8A8F94"},
      {"type": "text", "name": "Næste stop", "x": 942, "y": 18, "data": "NaesteStop", "size": 40, "color": "#1D1D1D", "bold": true},
      {"type": "box", "name": "Venstre kolonne", "x": 790, "y": 92, "w": 152, "h": 338, "color": "#F3F4F5"},
      {"type": "box", "name": "STOP-felt", "x": 790, "y": 93, "w": 152, "h": 136, "color": "#111111", "color_on": "#E2231A", "state": "StopOenske"},
      {"type": "text", "name": "STOP", "x": 815, "y": 136, "text": "STOP", "size": 36, "color": "#FFFFFF", "bold": true},
      {"type": "text", "name": "Linje-label", "x": 806, "y": 250, "text": "Linje:", "size": 20, "color": "#333333"},
      {"type": "text", "name": "Linje", "x": 870, "y": 250, "data": "Linje", "size": 20, "color": "#8A8F94"},
      {"type": "text", "name": "Zone", "x": 806, "y": 285, "text": "Zone: 2", "size": 20, "color": "#333333"},
      {"type": "text", "name": "Tid", "x": 806, "y": 320, "data": "Ur", "size": 20, "color": "#333333"},
      {"type": "box", "name": "Stopliste", "x": 960, "y": 100, "w": 620, "h": 320, "color": "#FFFFFF", "data": "StopListe"}
    ]
  }
}
```

Layout-delen kan også åbnes og rettes i Movia Editor (Åbn… → vælg filen,
hvis den kun indeholder `layout`-delen).


## Eksempel: chaufførens kørselsskærm (Driving)
Skærmen `Driving` er bygget som den rigtige Movia-tablet: blå statuslinje, sort top med linje-boks,
destination og stort ur, sidebar med 3 knapper, rød/grøn "Næste stop"-boks med forsinkelse,
"Sidste stop"-boks, kort og blå bundbjælke. Spillets egne knapper i bunden er skjult med `aendringer` (skjul).
Farveregel: rød når `Forsinkelse > 0` (forsinket), ellers grøn.
```json
{"hvis": "Forsinkelse > 0", "saet": "farve", "element": "NaesteBoks", "til": "#DE3B26", "ellers": "#3FA535"},
{"saet": "tekst", "element": "Forsinkelse", "til": "{Forsinkelse:m:ss}"},
{"saet": "tekst", "element": "Naeste tid", "til": "{NaesteTid:hh:mm:ss}"},
{"saet": "tekst", "element": "Ur", "til": "{KlokkeSek:hh:mm:ss}"}
```
Ikoner til knapperne ligger i `MoviaTools\Ikoner\` (knap_logud, knap_menu, knap_stop, knap_telefon, knap_besked, trekant, nav_*).

## Tekst: justering og klip
Tekst-elementer kan have `"align": "midt"` eller `"align": "hoejre"` (kræver `w`), og `"klip": true`
(lang tekst afsluttes med "…" i stedet for at løbe ind i andre ting – kræver `w`).
```json
{"type": "text", "name": "Naeste tid", "x": 310, "y": 122, "w": 160, "text": "07:31:00", "size": 22, "align": "hoejre"}
{"type": "text", "name": "Naeste stop", "x": 64, "y": 130, "w": 262, "text": "-", "size": 22, "bold": true, "klip": true}
```
VIGTIGT: Brug IKKE `"data"` på Driving-skærmen til stopnavne – spillet farver de felter sort. Lav i stedet en
almindelig tekst og en regel: `{"saet": "tekst", "element": "Naeste stop", "til": "{NaesteStopNavn}"}`.

## GPS-kort (type "gps")
Et rigtigt, kørende GPS-kort (spillets eget navigationskort) i 3D. Kun ét pr. skærm.
```json
{"type": "gps", "name": "Kort", "x": 54, "y": 98, "w": 1146, "h": 602, "z": -20,
 "pitch": -35, "afstand": 4000, "vinkel": 35,
 "baggrund": "C:\\Users\\tacci\\Documents\\The Bus\\MoviaTools\\Ikoner\\kort_bg.png"}
```
- `pitch` = hvor skråt kortet ses (-20 fladt … -60 meget skråt), `afstand` = kamera-afstand, `vinkel` = kamera-drejning.
- `baggrund` = billede der farver kortets baggrund (spillet gør det mørkere, så vælg en lys farve).
- 3D-ring om næste busstop: et billede-element med `"ring": true` – motoren flytter det hen over næste stop på kortet
  og skjuler det, når stoppet er uden for kortet:
```json
{"type": "box", "name": "Stopring", "x": 0, "y": 0, "w": 140, "h": 70, "image": "...\\Ikoner\\stop_ring.png", "ring": true, "z": -12}
```


## Eksempel: linje-mærker og afgangstavle (Passager)
Mærke under 1. stop (gul, blå hvis S-bus), vises kun hvis der er en linje:
```json
{"hvis": "Linje1_1 != ''", "saet": "vis", "element": "Maerke1_1"},
{"hvis": "Linje1_1 indeholder 'S'", "saet": "farve", "element": "Maerke1_1", "til": "#1E5FD6", "ellers": "#F5B800"},
{"saet": "tekst", "element": "MaerkeTxt1_1", "til": "{Linje1_1}"}
```
Afgangstavle der kun vises ved stoppet (lag med højt `z`, så den dækker stoplisten):
```json
{"hvis": "VedStop = 1", "saet": "vis", "element": "Tavle bund"},
{"hvis": "VedStop = 1 og AfgLinje1 != ''", "saet": "vis", "element": "Tavle rk1 til"},
{"saet": "tekst", "element": "Tavle rk1 til", "til": "{AfgTil1}"},
{"saet": "tekst", "element": "Tavle rk1 min", "til": "{AfgMin1:heltal}"},
{"hvis": "AfgMin1 < 1", "saet": "tekst", "element": "Tavle rk1 min", "til": "Nu"}
```
Data hentes fra spillets egne afgangstavler ca. hvert 2,5 sekund.


## Reklamer: skift mellem flere + video
Flere reklamer på samme plads der skifter (med blød overgang) – læg dem oven i hinanden og brug `sider` i layoutet:
```json
"sider": {"skift_hver": 12, "glid": 0.8, "sider": [["Reklame"], ["Reklame 2"], ["Reklame 3"]]}
```
Video-reklamer: læg videoen (.mp4/.mov/.webm/.gif) i `MoviaTools\Reklamer` og dobbeltklik `video_til_flipbook.bat`
(kræver én gang: `pip install opencv-python pillow`). Det laver `Reklamer\<navn>_flipbook.png` + `.json`.
Brug den så som et billede-element med `"video"` i stedet for `"image"`:
```json
{"type": "box", "name": "Reklame 3", "x": 0, "y": 0, "w": 790, "h": 430, "color": "#000000",
 "video": "C:\\Users\\tacci\\Documents\\The Bus\\MoviaTools\\Reklamer\\pizza_flipbook.png"}
```
Videoer skal være korte (højst ca. 64 billeder = 8 sek ved 8 fps), uden lyd. Længere videoer bliver klippet.

## Trykknapper (type "knap") og stoplisten
Et lag af typen `"knap"` er en usynlig trykflade. Den tegner ikke noget selv – læg den oven på en boks/et ikon.
- `"skifter": "Liste"` – hvert tryk skifter variablen `Liste` mellem 0 og 1.
- `"trin": "Rul", "vaerdi": 1, "min": 0, "max": 30` – hvert tryk lægger `vaerdi` til variablen `Rul` (holdt mellem min og max).
Variablerne (fx `Liste`, `Rul`) kan bruges i regler som alle andre: `"hvis": "Liste = 1"`.
En knap kan kun trykkes, når den er synlig – skjul den med en `vis`-regel, når den ikke skal virke.

Stoplisten (**Driving/Main**): `Stop1Navn` … `Stop8Navn`, `Stop1Tid` (planlagt ankomst, sek – format `hh:mm:ss`),
`Stop1Afgang`, `Stop1Findes` (1/0). Stop1 er det stop der står som "Næste stop"; en knap-gruppe der hedder `Rul` ruller listen.

`AfgangTekst` (**Driving**): planlagt afgang fra stoppet bussen holder ved, fx `08:19:00`, og hvis man er for sent på den `08:19:00 (08:21:00)`.
