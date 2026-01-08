import re
from re import Pattern

BRANDS: dict[str:str] = {
    "AOTELI": "Aoteli",
    "APLUS": "Aplus",
    "ARIVO": "Arivo",
    "ATTAR": "Attar",
    "BF GOODRICH": "BF Goodrich",
    "BRIDGESTONE": "Bridgestone",
    "CONTINENTAL": "Continental",
    "CORDIANT": "Cordiant",
    "DOUBLESTAR": "DoubleStar",
    "DUNLOP": "Dunlop",
    "DYNAMO": "Dynamo",
    "FIREMAX": "Firemax",
    "GENERAL TIRE": "General Tire",
    "GISLAVED": "Gislaved",
    "HANKOOK": "Hankook",
    "HIFLY": "HiFly",
    "HI-FLY": "HiFly",
    "IKON TYRES": "Ikon",
    "IKON": "Ikon",
    "NORDMAN": "Ikon",
    "КАМА": "КАМА",
    "KAMA": "КАМА",
    "KUMHO": "Kumho",
    "LANVIGATOR": "Lanvigator",
    "LAUFENN": "Laufenn",
    "LEAO": "Leao",
    "LINGLONG": "Linglong",
    "LING LONG": "Linglong",
    "MASSIMO": "Massimo",
    "MAXXIS": "MAXXIS",
    "MAZZINI": "Mazzini",
    "MICHELIN": "Michelin",
    "NEXEN": "Nexen",
    "NITTO": "Nitto",
    "NOKIAN TYRES": "Nokian",
    "NOKIAN": "Nokian",
    "ONYX": "Onyx",
    "PACE": "Pace",
    "PIRELLI": "Pirelli",
    "POWERTRAC": "Powertrac",
    "FORMULA": "Pirelli",
    "ROADCRUZA": "Roadcruza",
    "ROADMARCH": "Roadmarch",
    "ROTALLA": "Rotalla",
    "ROYAL BLACK": "Royal Black",
    "SAILUN": "Sailun",
    "SONIX": "Sonix",
    "SUMAXX": "Sumaxx",
    "TIGAR": "Tigar",
    "TORERO (MATADOR)": "Torero (Matador)",
    "TORERO": "Torero",
    "TOYO": "Toyo",
    "MATADOR": "Matador",  # Должен быть после Torero
    "TRIANGLE": "Triangle",
    "TUNGA": "Tunga",
    "VIATTI": "Viatti",
    "VOLTYRE": "Voltyre",
    "YOKOHAMA": "Yokohama",
    "NKSHZ": "КАМА",
    "НКШЗ": "КАМА",
    "БЕЛШИНА": "БелШина",
    "ВОЛШЗ": "ВолШЗ",
}

MODELS: dict[str:str] = {
    "Aoteli": {
        "ECOSAVER": "Ecosaver",
    },
    "Aplus": {
        "A503": "A503",
        "A703": "A703",
    },
    "Arivo": {
        "ICE CLAW ARW7": "Ice Claw ARW7",
        "ICE CLAW ARW8": "Ice Claw ARW8",
    },
    "Attar": {
        "S01": "S01",
        "W03": "W03",
    },
    "BF Goodrich": {
        "MUD TERRAIN T/A KM3": "Mud Terrain T/A KM3",
        "G-FORCE COMP-2": "G-Force Comp-2",
    },
    "Bridgestone": {
        "BLIZZAK ICE": "Blizzak Ice",
        "BLIZZAK SPIKE-02": "Blizzak Spike-02",
        "SPIKE-02": "Blizzak Spike-02",
        "DM-V2": "DM-V2",
        "DMV-2": "DM-V2",
        "IC7000": "IC7000",
        "REVO-GZ": "Revo GZ",
        "REVO GZ": "Revo GZ",
        "R250": "R250",
    },
    "Continental": {
        "CONTIECO": "Contieco",
        "ICECONTACT 2": "IceContact 2",
        "ICE CONTACT 2": "IceContact 2",
        "ICECONTACT 3": "IceContact 3",
        "ICE CONTACT 3": "IceContact 3",
        "PREMIUM CONTACT 6": "Premium Contact 6",
        "VIKINGCONTACT 7": "VikingContact 7",
        "VIKING CONTACT 7": "VikingContact 7",
    },
    "Cordiant": {
        "ALL TERRAIN": "All-Terrain",
        "ALL-TERRAIN": "All-Terrain",
        "CA-1": "Business CA-1",
        "CA-2": "Business CA-2",
        "CS-2": "Business CS-2",
        "CW-2": "Business CW-2",
        "BUSINESS CW-2": "Business CW-2",
        "COMFORT 2": "Comfort 2",
        "COMFORT-2": "Comfort 2",
        "GRAVITY": "Gravity",
        "OFF ROAD OS-501": "Off Road OS-501",
        "OFF ROAD 2": "Off-Road 2",
        "OFF ROAD  2": "Off-Road 2",
        "PW-404": "Polar SL PW-404",
        "POLAR SL": "Polar SL PW-404",
        "PW-502": "Polar 2 PW-502",
        "POLAR-2": "Polar 2 PW-502",
        "ROAD RUNNER PS-1": "Road Runner PS-1",
        "ROAD RUNNER": "Road Runner PS-1",
        "RUN TOUR": "RUN TOUR",
        "PW-2": "Snow Cross PW-2",
        "SNOW CROSS": "Snow Cross PW-2",
        "PW-4": "Snow Cross 2 PW-4",
        "SNOW CROSS 2": "Snow Cross 2 PW-4",
        "SNOW-CROSS 2": "Snow Cross 2 PW-4",
        "SNOW- CROSS 2": "Snow Cross 2 PW-4",
        "SNO-MAX 7000": "Sno-Max 7000",
        "PS-2": "Sport 3 PS-2",
        "SPORT 3": "Sport 3 PS-2",
        "SPORT-3": "Sport 3 PS-2",
        "WINTER DRIVE 2": "Winter Drive 2",
        "PW-1": "Winter Drive PW-1",
        "WINTER DRIVE": "Winter Drive PW-1",
        "WINTER-DRIVE": "Winter Drive PW-1",
    },
    "DoubleStar": {
        "DS01": "DS01",
        "DW02": "DW02",
    },
    "Dynamo": {
        "MAT01": "Hiscend-H MAT01",
        "MC02": "Hiscend-H MC02",
        "MHT01": "Hiscend-H MHT01",
        "MMT01": "Hiscend-H MMT01",
        "MSU01": "Hiscend-H MSU01",
        "MSU02": "Hiscend-H MSU02",
        "MWH01": "Snow-H MWH01",
        "MWH02": "Snow-H MWH02",
        "MWH03": "Snow-H MWH03",
        "MWS01": "Snow-H MWS01",
        "MH01": "Street-H MH01",
        "MU02": "Street-H MU02",
        "MU71": "Street-H MU71",
    },
    "Dunlop": {
        "GRANDTREK AT5": "Grandtrek AT5",
        "GRANDTREK ICE02": "Grandtrek Ice 02",
        "GRANDTREK ICE 02": "Grandtrek Ice 02",
        "GRANDTREK ICE03": "Grandtrek Ice 03",
        "SP WINTER ICE 02": "SP Winter Ice 02",
        "WINTER MAXX SJ8": "Winter MAXX SJ8",
    },
    "Firemax": {
        "FM601": "FM601",
        "FM810": "FM810",
    },
    "Formula": {
        "ENERGY": "Energy",
        "ICE": "Ice",
    },
    "General Tire": {
        "ALTIMAX ARCTIC 12 CD": "Altimax Arctic 12 CD",
    },
    "Gislaved": {
        "ICECONTROL": "IceControl",
        "ICE CONTROL": "IceControl",
        "NORD FROST 200": "Nord Frost 200",
        "NORD*FROST 200": "Nord Frost 200",
        "NORD FROST VAN 2": "Nord Frost VAN 2",
        "PREMIUMCONTROL": "PremiumControl",
        "PREMIUM CONTROL": "PremiumControl",
        "SOFT FROST 200": "Soft Frost 200",
        "SOFT*FROST 200": "Soft Frost 200",
        "SPIKECONTROL": "SpikeControl",
        "SPIKE CONTROL": "SpikeControl",
        "TERRACONTROL ATR": "TerraControl ATR",
        "TERRA CONTROL ATR": "TerraControl ATR",
        "TERRACONTROL": "TerraControl",
        "TERRA CONTROL": "TerraControl",
        "ULTRACONTROL": "UltraControl",
        "ULTRA CONTROL": "UltraControl",
    },
    "Hankook": {
        "IW01A": "IW01A",
        "IW04A": "iON Nordic i*ce IW04A",
        "RF11": "Dynapro AT2 RF11",
        "RA33": "Dynapro HP2 RA33",
        "RA43": "Dynapro HPX RA43",
        "K125A": "Ventus Prime 3 K125A",
        "K125": "Ventus Prime 3 K125",
        "K127A": "Ventus S1 Evo3 K127A",
        "K127B": "Ventus S1 Evo3 K127B Run Flat",
        "K127": "Ventus S1 Evo3 K127",
        "K135": "Ventus Prime 4 K135",
        "K435": "Kinergy Eco2 K435",
        "RW10": "Winter I*Cept X RW10",
        "RW11": "I*Pike RW11",
        "RW15": "RW15",
        "W330": "Winter I*Cept Evo3 W330",
        "W330A": "Winter I*Cept Evo3 X W330A",
        "W429A": "Winter I*Pike X W429A",
        "W429": "Winter I*Pike RS2 W429",
        "W616": "W616",
        "W636": "Winter I*Cept IZ3 W636",
        "W636A": "Winter I*Cept IZ3 X W636A",
    },
    "HiFly": {
        "HF-261": "HF-261",
    },
    "Ikon": {
        "AUTOGRAPH AQUA 3": "Autograph Aqua 3",
        "AUTOGRAPH ECO C3": "Autograph Eco C3",
        "AUTOGRAPH ECO 3": "Autograph Eco 3",
        "AUTOGRAPH ICE C3": "Autograph Ice C3",
        "AUTOGRAPH ICE 9": "Autograph Ice 9",
        "AUTOGRAPH ICE 10": "Autograph Ice 10",
        "AUTOGRAPH SNOW C3": "Autograph Snow C3",
        "AUTOGRAPH SNOW 3": "Autograph Snow 3",
        "AUTOGRAPH ULTRA 2": "Autograph Ultra 2",
        "CHARACTER AQUA": "Character Aqua",
        "CHARACTER ECO": "Character Eco",
        "CHARACTER ICE 7 SUV (NORDMAN 7 SUV)": "Character Ice 7 SUV (Nordman 7 SUV)",
        "CHARACTER ICE 7 (NORDMAN 7)": "Character Ice 7 (Nordman 7)",
        "CHARACTER ICE 7": "Character Ice 7",
        "CHARACTER ICE 8 SUV (NORDMAN 8 SUV)": "Character Ice 8 SUV (Nordman 8 SUV)",
        "CHARACTER ICE 8 (NORDMAN 8)": "Character Ice 8 (Nordman 8)",
        "CHARACTER ICE 8": "Character Ice 8",
        "CHARACTER SNOW 2 SUV (NORDMAN RS2 SUV)": "Character Snow 2 SUV (Nordman RS2 SUV)",
        "CHARACTER SNOW 2 (NORDMAN RS2)": "Character Snow 2 (Nordman RS2)",
        "CHARACTER SNOW 2": "Character Snow 2",
        "CHARACTER ULTRA": "Character Ultra",
        "NORDMAN C": "Nordman C",
        "NORDMAN RS2": "Nordman RS2",
        "RS2": "Nordman RS2",
        "NORDMAN SC": "Nordman SC",
        "SC": "Nordman SC",
        "NORDMAN SX3": "Nordman SX3",
        "SX3": "Nordman SX3",
        "NORDMAN SZ2": "Nordman SZ2",
        "SZ2": "Nordman SZ2",
        "NORDMAN S2": "Nordman S2",
        "S2": "Nordman S2",
        "NORDMAN 5": "Nordman 5",
        "NORDMAN 7": "Nordman 7",
        "NORDMAN 8": "Nordman 8",
    },
    "КАМА": {
        "ALGA": "Alga",
        "НК-132": "Breeze НК-132",
        "ЕВРО-131 LCV": "Евро-131 LCV",
        "ЕВРО-131": "Евро-131",
        "EURO-518": "Euro-518",
        "ЕВРО 518": "Euro-518",
        "EURO-520": "Euro НК-520",
        "ЕВРО-520": "Euro НК-520",
        "НК-520": "Euro НК-520",
        "LCV-131": "Euro LCV-131 НкШЗ",
        "НК-245": "Flame A/T НК-245 НкШЗ",
        "FLAME M/T LCV": "Flame M/T LCV",
        "FLAME M/T": "Flame M/T",
        "НК-434": "Flame М/T НК-434",
        "V-134": "Strada 2 V-134 НкШЗ",
        "НК-135": "Trace НК-135 НкШЗ",
        "И-502": "И-502 НкШЗ M+S",
        "И-511": "И-511",
        "И-520": "И-520 НкШЗ",
        "КАМА-218": "Кама-218",
        "КАМА-219": "Кама-219 НкШЗ",
        "КАМА-221": "Кама-221",
        "КАМА-503": "Кама-503",
        "KAMA-503": "Кама-503",
        "503": "503",
        "365 HK-241": "365 HK-241 НкШЗ",
        "НК-241": "НК-241",
        "HK-241": "НК-241",
        "HK-242": "НК-242 НкШЗ",
        "242": "НК-242 НкШЗ",
        "НК-243": "НК-243 НкШЗ",
        "НК-534": "НК-534",
    },
    "Kumho": {
        "AT52": "AT52",
        "KC53": "KC53",
        "RS02": "RS02",
    },
    "Lanvigator": {
        "WINTERGRIP VAN": "WinterGrip VAN",
    },
    "Laufenn": {
        "LC01": "LC01",
        "LD01": "LD01",
        "LH01": "LH01",
        "LH71": "LH71",
        "LK01": "LK01",
        "LK03": "LK03",
        "LK41": "LK41",
        "LW51": "LW51",
        "LW71": "LW71",
    },
    "Leao": {
        "WINTER DEFENDER ICE I-15": "Winter Defender Ice I-15",
    },
    "Linglong": {
        "COMFORT MASTER": "Comfort Master",
        "CROSSWIND A/T": "Crosswind A/T",
        "CROSSWIND H/T": "Crosswind H/T",
        "CROSSWIND M/T": "Crosswind M/T",
        "CROSSWIND STORM 01 8PR M+S": "Crosswind Storm 01 8PR M+S",
        "CROSSWIND 4×4 HP": "Crosswind 4×4 HP",
        "GREEN MAX ECOTOURING": "Green-Max EcoTouring",
        "GREEN-MAX ECOTOURING": "Green-Max EcoTouring",
        "GREEN MAX HP010": "Green-Max HP010",
        "GREEN-MAX HP010": "Green-Max HP010",
        "GREEN MAX VAN": "Green-Max VAN",
        "GREEN-MAX VAN": "Green-Max VAN",
        "GREENMAX WINTER GRIP VAN 2": "Green-Max Winter Grip Van 2",
        "GREEN MAX WINTER GRIP VAN 2": "Green-Max Winter Grip Van 2",
        "GREEN-MAX WINTER GRIP 2": "Green-Max Winter Grip 2",
        "GREEN MAX WINTER GRIP": "Green-Max Winter Grip",
        "GREEN-MAX WINTER GRIP": "Green-Max Winter Grip",
        "GREEN-MAX WINTER ICE I-15": "Green-Max Winter Ice I-15",
        "GREEN MAX 4×4 HP": "Green-Max 4×4 HP",
        "GREEN-MAX 4×4 HP": "Green-Max 4×4 HP",
        "GREEN-MAX": "Green-Max",
        "GRIP MASTER C/S": "Grip Master C/S",
        "GRIP MASTER 4S": "Grip Master 4S",
        "R620": "R620",
        "SPORT MASTER": "Sport Master",
    },
    "Massimo": {
        "VITTO": "Vitto",
    },
    "Matador": {
        "SIBIR ICE 2": "Sibir Ice 2 MP-30",
        "MP72": "Izzarda A/T 2 MP-72",
        "MP-72": "Izzarda A/T 2 MP-72",
    },
    "MAXXIS": {
        "AT 771": "Bravo A/T 771",
        "AT-771": "Bravo A/T 771",
        "AT 980E": "Worm-Drive A/T 980E",
        "AT-980E": "Worm-Drive A/T 980E",
        "AT 980": "Worm-Drive A/T 980",
        "AT-980": "Worm-Drive A/T 980",
        "MT 764": "Bighorn M/T 764",
        "MT-764": "Bighorn M/T 764",
        "MP10": "Pragmatra MP10",
        "MP15": "Pragmatra MP15",
        "HP5": "Premitra HP5",
        "MA-SLW": "MA-SLW",
        "MA-Z3": "MA-Z3",
        "MAZ4S": "Victra MA-Z4S",
        "MA Z4S": "Victra MA-Z4S",
        "MA-Z4S": "Victra MA-Z4S",
        "VS5": "Victra Sport VS5",
        "NP-5": "NP-5",
        "NS-5": "NS-5",
        "SP-02": "SP-02",
        "SP3": "SP3",
        "SP5": "SP5",
        "SS-01": "SS-01",
        "UE-168": "Bravo UE-168",
    },
    "Mazzini": {
        "ECO307": "ECO307",
        "ECO605 PLUS": "ECO605 Plus",
        "ECO606": "ECO606",
        "ECO607": "ECO607",
        "ECO809": "ECO809",
        "ECO819": "ECO819",
        "ECOSAVER": "Ecosaver",
        "EFFIVAN": "EffiVan",
        "FALCONER F1": "Falconer F1",
        "GIANTSAVER": "Giantsaver",
        "MUD CONTENDER": "Mud Contender",
        "SHARK A30": "Shark A30",
        "SHARK Z02": "Shark-Z02",
        "SHARK-Z02": "Shark-Z02",
        "SNOWLEOPARD": "Snow Leopard",
        "SNOW LEOPARD": "Snow Leopard",
        "VARENNA S01": "Varenna S01",
        "VARENNA SO1": "Varenna S01",
    },
    "Michelin": {
        "PILOT SPORT 4S": "Pilot Sport 4S",
        "LAT. X-ICE NORTH": "Latitude X-ice North",
        "LATITUDE X-ICE 2": "Latitude X-ice 2",
        "XDE2": "XDE2",
        "X-ICE NORTH 4": "X-ice North 4",
        "X-ICE SNOW MI": "X-ice Snow MI",
    },
    "Nexen": {
        "N'BLUE HD PLUS": "N'Blue Hd Plus",
        "N’BLUE HD PLUS": "N'Blue Hd Plus",
        "NBLUE S": "N'Blue S",
        "N'FERA RU1": "N'Fera RU1",
        "N’FERA RU1": "N'Fera RU1",
        "N'FERA RU5": "N’Fera RU5",
        "N’FERA RU5": "N’Fera RU5",
        "N'FERA SPORT": "N’Fera Sport",
        "N’FERA SPORT": "N’Fera Sport",
        "N'FERA SU1": "N'Fera SU1",
        "N’FERA SU1": "N'Fera SU1",
        "ROADIAN A/T": "Roadian A/T",
        "ROADIAN HP": "Roadian HP",
        "ROADIAN HTX RH5": "Roadian HTX RH5",
        "WILDRANGER AT": "Wildranger A/T",
        "WILDRANGER A/T": "Wildranger A/T",
        "WINGUARD WINSPIKE": "Winguard Winspike",
        "WINGUARD": "Winguard",
    },
    "Nitto": {
        "NTSN3": "NTSN3",
        "NTSPK": "NTSPK",
        "DURA GRAPPLER": "Dura Grappler",
    },
    "Nokian": {
        "HAKKA GREEN 3": "Hakka Green 3",
        "HAKKAPELIITTA R2": "Hakkapeliitta R2",
        "HAKKAPELIITTA R3": "Hakkapeliitta R3",
        "HAKKAPELIITTA R5": "Hakkapeliitta R5",
        "HAKKAPELIITTA 9": "Hakkapeliitta 9",
        "HAKKA BLUE 3": "Hakka Blue 3",
        "NORDMAN C": "Nordman C",
        "NORDMAN RS2": "Nordman RS2",
        "NORDMAN SC": "Nordman SC",
        "NORDMAN SX3": "Nordman SX3",
        "NORDMAN SZ2": "Nordman SZ2",
        "NORDMAN S2": "Nordman S2",
        "NORDMAN 5": "Nordman 5",
        "NORDMAN 7": "Nordman 7",
        "NORDMAN 8": "Nordman 8",
    },
    "Onyx": {
        "NY-W387": "NY-W387",
    },
    "Pace": {
        "ALVENTI RUN FLAT": "Alventi Run Flat",
        "ALVENTI": "Alventi",
        "ANTARCTICA ICE": "Antarctica Ice",
        "ANTARCTICA SPORT": "Antarctica Sport",
        "IMPERO": "Impero",
    },
    "Pirelli": {
        "FORMULA ENERGY": "Formula Energy",
        "ENERGY": "Formula Energy",
        "FORMULA ICE": "Formula Ice",
        "CINTURATO ALL SEASON 2": "Cinturato All Season 2",
        "CINTURATO P1": "Cinturato P1",
        "CINTURATO P7": "Cinturato P7 (P7C2)",
        "POWERGY": "Powergy",
        "P ZERO SPORTS CAR": "P Zero (PZ4) Sports Car",
        "ZERO PNCS": "Zero (PNCS)",
        "SCORPION ALL-SEASON SF2": "Scorpion All Season SF2",
        "SCORPION ALL TERRAIN PLUS": "Scorpion All Terrain Plus",
        "SCORPION ICE ZERO 2": "Scorpion Ice Zero 2",
        "SCORPION VERDE ALL-SEASON": "Scorpion Verde All-Season",
        "SCORPION VERDE": "Scorpion Verde",
        "SCORPION": "Scorpion",
        "ICE ZERO 2": "Ice Zero 2",
        "ICE ZERO FR": "Ice Zero Friction",
        "ICE ZERO": "Ice Zero",
        "WINTER ICE ZERO": "Winter Ice Zero",
    },
    "Powertrac": {
        "ADAMAS H/P": "Adamas H/P",
        "CITYRACING": "CityRacing",
        "CITYROVER": "CityRover",
        "CITYMARCH": "CityMarch",
        "ECOSPORT X77": "EcoSport X77",
        "ICE XPRO": "Ice Xpro",
        "LOADKING": "LoadKing",
        "POWER LANDER A/T": "Power Lander A/T",
        "POWER ROVER M/T": "Power Rover M/T",
        "RACING PRO": "Racing Pro",
        "SNOWPRO STUD 01": "SnowPro Stud 01",
        "SNOWPRO STUD 02": "SnowPro Stud 02",
        "SNOWPRO STUD": "SnowPro Stud",
        "SNOWVAN PRO": "SnowVan Pro",
        "VANTOUR": "VanTour",
        "WILDRANGER AT": "WildRanger A/T",
        "WILDRANGER A/T": "WildRanger A/T",
        "WILDRANGER MT": "WildRanger M/T",
        "WILDRANGER M/T": "WildRanger M/T",
    },
    "Roadcruza": {
        "RA1100": "RA1100",
    },
    "Roadmarch": {
        "SNOWROVER 868": "SnowRover 868",
        "SNOW ROVER 868": "SnowRover 868",
    },
    "Rotalla": {
        "S500": "S500",
    },
    "Royal Black": {
        "ROYAL A/T": "Royal A/T",
        "ROYAL M/T": "Royal M/T",
        "ROYALCOMMERCIAL": "RoyalCommercial",
        "ROYAL COMMERCIAL": "RoyalCommercial",
        "ROYALCOMFORT": "RoyalComfort",
        "ROYAL COMFORT": "RoyalComfort",
        "ROYALEXPLORER EV": "Royal Explorer EV",
        "ROYAL EXPLORER EV": "Royal Explorer EV",
        "ROYALEXPLORER II": "Royal Explorer II",
        "ROYAL EXPLORER II": "Royal Explorer II",
        "ROYALICE": "Royal Ice",
        "ROYALMILE": "Royal Mile",
        "ROYAL MILE": "Royal Mile",
        "ROYALPERFORMANCE": "Royal Performance",
        "ROYAL PERFORMANCE": "Royal Performance",
        "ROYALSPORT": "Royal Sport",
        "ROYAL SPORT": "Royal Sport",
        "ROYALSTUD 2": "RoyalStud II",
        "ROYAL STUD 2": "RoyalStud II",
        "ROYALSTUD II": "RoyalStud II",
        "ROYALSTUD": "RoyalStud",
        "ROYAL STUD": "RoyalStud",
        "ROYALWINTER": "Royal Winter",
        "ROYAL WINTER": "Royal Winter",
    },
    "Sailun": {
        "ATREZZO ELITE 2": "Atrezzo Elite 2",
        "ATREZZO ELITE": "Atrezzo Elite",
        "ATREZZO ZSR": "Atrezzo ZSR",
        "COMMERCIO PRO": "Commercio PRO",
        "ICE BLAZER ARCTIC EVO": "Ice Blazer Arctic Evo",
        "ICE BLAZER ARCTIC RFT": "Ice Blazer Arctic RFT",
        "ICE BLAZER ARCTIC": "Ice Blazer Arctic",
        "WST2": "Ice Blazer WST2",
        "WST3": "Ice Blazer WST3",
        "TERRAMAX A/T": "Terramax A/T",
        "TERRAMAX M/T": "TerraMax M/T",
        "TERRAMAX CVR": "Terramax CVR",
        "SV57": "Turismo SV57",
    },
    "Sonix": {
        "ECOPRO 99": "EcoPro 99",
        "ECO PRO 99": "EcoPro 99",
        "L-ZEAL 56": "L-Zeal 56",
        "PRIMESTAR 66": "Primestar 66",
        "PRIME UHP 08": "Prime UHP 08",
        "SNOWROVER 868": "SnowRover 868",
        "SNOW ROVER 868": "SnowRover 868",
        "SNOWROVER 989": "SnowRover 989",
        "SNOW ROVER 989": "SnowRover 989",
        "WINTER X PRO STUDS 77": "WinterXPro Studs 77",
        "WINTER XPRO STUDS 77": "WinterXPro Studs 77",
        "WINTERXPRO STUDS 77": "WinterXPro Studs 77",
        "WINTER X PRO STUDS 888": "WinterXPro Studs 888",
        "WINTER XPRO STUDS 888": "WinterXPro Studs 888",
        "WINTERXPRO STUDS 888": "WinterXPro Studs 888",
        "WINTERXPRO 888": "WinterXPro Studs 888",
    },
    "Sumaxx": {
        "ALL-TERRAIN A/T": "All-Terrain A/T",
        "MAX DRIFTING X": "Max Drifting X",
        "MAX RACING 86S": "Max Racing 86S",
        "MAX RANGER R/T": "Max Ranger R/T",
        "MAX SPEED R1": "Max Speed R1",
    },
    "Tigar": {
        "CARGO SPEED WINTER ": "Cargo Speed Winter",
        "ICE": "Ice",
        "ROAD-TERRAIN": "Road-Terrain",
        "ROAD TERRAIN": "Road-Terrain",
        "WINTER": "Winter",
    },
    "Torero (Matador)": {
        "MP30 FR": "MP30 FR",
        "MP30": "MP30",
        "MP47": "MP47",
        "MPS330": "MPS330",
        "MPS500": "MPS500",
    },
    "Torero": {
        "MP30 FR": "MP30 FR",
        "MP30": "MP30",
        "MP47": "MP47",
        "MP72": "MP72",
        "MP82": "MP82",
        "MPS125": "MPS125",
        "MPS330": "MPS330",
        "MPS500": "MPS500",
    },
    "Toyo": {
        "ICE-FREEZER": "Ice-Freezer",
        "NANOENERGY 3": "NanoEnergy 3",
        "OBGIZ": "Obgiz",
        "OBGSI6 LS": "OBGSi6 LS",
        "OBGSI6": "OBGSi6",
        "OBSERVE VAN": "Observe Van",
        "PROXES CF2S": "Proxes CF2S",
        "PROXES C1S": "Proxes C1S",
        "PROXES SPORT": "Proxes Sport",
        "PROXES T1S": "Proxes T1S",
    },
    "Triangle": {
        "LL01": "LL01",
        "LS01": "LS01",
        "PL01": "PL01",
        "PL02": "PL02",
        "PS01": "PS01",
        "TC101": "TC101",
        "TE301": "TE301",
        "TH201": "TH201",
        "TE307": "TE307",
        "TH202": "TH202",
        "TI501": "TI501",
        "TR259": "TR259",
        "TR292": "TR292",
        "TR645": "TR645",
        "TR646": "TR646",
        "TR652": "TR652",
        "TR-668A": "TR-668A",
        "TR-690": "TR-690",
        "TR737": "TR737",
        "TR757": "TR757",
        "TR777": "TR777",
        "TRD99": "TRD99",
        "TV701": "TV701",
    },
    "Tunga": {
        "PW-5": "Nordway 2 PW-5",
        "NORDWAY 2": "Nordway 2 PW-5",
        "ZODIAK 2": "Zodiak 2",
        "ZODIAK-2": "Zodiak 2",
        "NORDWAY": "Nordway",
    },
    "Viatti": {
        "V-130": "Strada Asimmetrico V-130",
        "V-237": "Bosco A/T V-237",
        "V-238": "Bosco H/T V-238",
        "V-523": "Bosco Nordico V-523",
        "BOSCO NORDICO": "Bosco Nordico V-523",
        "V-526": "Bosco S/T V-526",
        "BOSCO S/T": "Bosco S/T V-526",
        "V-522": "Brina Nordico V-522",
        "V-521": "Brina V-521",
        "V-528": "Brina Nordico V-528",
        "Strada Asimmetrico": "Strada Asimmetrico V-130",
        "V-134": "Strada 2 V-134",
        "V-524": "Vettore Inverno V-524",
        "V-525": "Vettore Brina V-525",
    },
    "Voltyre": {
        "RF-309": "RF-309",
    },
    "Yokohama": {
        "AE51A": "BluEarth-GT AE51A",
        "AE-51A": "BluEarth-GT AE51A",
        "AE51E": "BluEarth-GT AE51E",
        "AE-51E": "BluEarth-GT AE51E",
        "AE51H": "BluEarth-GT AE51H",
        "AE-51H": "BluEarth-GT AE51H",
        "AE51": "BluEarth-GT AE51",
        "AE-51": "BluEarth-GT AE51",
        "AE61A": "BluEarth-XT AE61A",
        "AE-61A": "BluEarth-XT AE61A",
        "AE61": "BluEarth-XT AE61",
        "AE-61": "BluEarth-XT AE61",
        "E70BZ": "BluEarth E70BZ",
        "E-70BZ": "BluEarth E70BZ",
        "ES32A": "BluEarth-Es ES32A",
        "ES-32A": "BluEarth-Es ES32A",
        "ES32": "BluEarth-Es ES32",
        "ES-32": "BluEarth-Es ES32",
        "G015": "Geolandar A/T G015",
        "G-015": "Geolandar A/T G015",
        "G057B": "Geolandar X-CV G057B",
        "G-057B": "Geolandar X-CV G057B",
        "G057": "Geolandar X-CV G057",
        "G-057": "Geolandar X-CV G057",
        "G058": "Geolandar CV G058",
        "G-058": "Geolandar CV G058",
        "G075": "iceGuard Studless G075",
        "G-075": "iceGuard Studless G075",
        "G-65": "G65",
        "IG50 +": "iceGuard Studless iG50+",
        "IG50+": "iceGuard Studless iG50+",
        "IG-50+": "iceGuard Studless iG50+",
        "IG60A": "iceGuard Studless iG60A",
        "IG-60A": "iceGuard Studless iG60A",
        "IG60": "iceGuard Studless iG60",
        "IG-60": "iceGuard Studless iG60",
        "IG55": "iceGuard Stud iG55",
        "IG-55": "iceGuard Stud iG55",
        "IG65": "iceGuard Stud iG65",
        "IG-65": "iceGuard Stud iG65",
        "IG70A": "iceGuard iG70A",
        "IG-70A": "iceGuard iG70A",
        "IG70": "iceGuard iG70",
        "IG-70": "iceGuard iG70",
        "PA02J": "Parada Spec-X PA02J",
        "PA-02J": "Parada Spec-X PA02J",
        "PA02": "Parada Spec-X PA02",
        "PA-02": "Parada Spec-X PA02",
        "RY61": "BluEarth-Van All Season RY61",
        "RY-61": "BluEarth-Van All Season RY61",
        "V105E N0": "V105E N0",
        "V105W": "V105W",
        "V105 N0": "V105 N0",
        "V107C MO": "V107C MO",
        "V107C": "V107C",
        "V107": "V107",
        "WY01": "W.drive WY01",
        "WY-01": "W.drive WY01",
    },
    "БелШина": {
        "БЕЛ-143": "Бел-143",
        "БЕЛ-147": "Бел-147",
        "БЕЛ-217": "Бел-217",
        "БЕЛ-253": "Бел-253",
        "БЕЛ-254": "Бел-254",
        "БЕЛ-261": "Бел-261",
        "БЕЛ-262": "Бел-262",
        "БЕЛ-267": "Бел-267",
        "БЕЛ-280": "Бел-280",
        "БЕЛ-281": "Бел-281",
        "БЕЛ-282": "Бел-282",
        "БЕЛ-283": "Бел-283",
        "БЕЛ-286": "Бел-286",
        "БЕЛ-287": "Бел-287",
        "БЕЛ-293": "Бел-293",
        "БЕЛ-297": "Бел-297",
        "БЕЛ-303": "Бел-303",
        "БЕЛ-313": "Бел-313",
        "БЕЛ-317": "Бел-317",
        "БЕЛ-329": "Бел-329",
        "БЕЛ-337": "Бел-337",
        "БЕЛ-341": "Бел-341",
        "БЕЛ-347": "Бел-347",
        "БЕЛ-354": "Бел-354",
        "БЕЛ-357": "Бел-357",
        "БЕЛ-367": "Бел-367",
        "БЕЛ-377": "Бел-377",
        "БЕЛ-397": "Бел-397",
        "БЕЛ-402": "Бел-402",
        "БЕЛ-403": "Бел-403",
        "БЕЛ-409": "Бел-409",
        "БЕЛ-494": "Бел-494",
        "БЕЛ-509": "Бел-509",
        "БЕЛ-517": "Бел-517",
        "БИ-522": "БИ-522",
    },
    "ВолШЗ": {
        "VOLTYRE RF-309": "Voltyre RF-309",
        "ВС-22": "ВС-22",
        "ВЛИ-5": "ВЛИ-5",
        "ВЛ-54": "ВЛ-54",
        "С-156": "С-156",
    },
}

test_strings = (
    "Автошина R16 185/75 C Cordiant Business CW-2 104/102 Q TL Ш",
    "автошина 185/65 R15 WESTLAKE Z-506 92T XL Ш",
    "185/60R15 84T Cordiant SNO-MAX 7000  б/к ОШ",
    "215/75R16 C 116/114S Ikon_Tyres Nordman SC",
    "215/75ZR16 C 116/114S Айкон Нордман SC",
    "Автошина R14 185/60 Nexen Winguard ICE PLUS XL 86T",
    "Автошина R14 185/60 Nexen Вингард ICE PLUS XL 86T",
    "175/70/14 Cordiant SNOW CROSS 2 шип 88T 2023г",
    "Автошина R14 185/60 Powertrac SNOWPRO STUD 01 82T шип",
    "Автошина R16 215/65 Gislaved SpikeControl SUV 98T TL",
    "Автошина R14 185 C Triangle TV701 102/100S TL",
    "Автошина R21 275/30 Hankook Ventus s1 evo3 SUV K127B Run Flat XL 98Y",
    "автошина 195/65 R15 DYNAMO SNOW-H_ARCTIC 91T",
    # "Автошина Hankook Ventus s1 evo3 SUV K127B Run Flat XL 98Y",
    "автошина 33x12,5 R15 DYNAMO HISCEND-H_MMT01 108Q",
)


def parse(pattern: Pattern[str], text: str) -> str:
    if m := re.search(pattern, text):
        match = m.groupdict()
        match["full_match"] = m.group()
        match["rest"] = text.replace(match["full_match"], "", 1).strip()
    else:
        match: dict = {"full_match": "", "rest": text}
    return match


def parse_size(text: str) -> dict[str, str]:
    size_pattern = (
        r"(?:"
        # r"(?:(?P<width>\d{2,3})[/xX*]?)?"
        r"(?:(?P<width>\d{1,3}(?:[,.]\d{1,2})?)[/xX*]?)?"
        # r"(?:(?P<height>\d{1,2}(?:[,.]\d{1,2})?))?"
        r"(?:(?P<height>\d{1,2}))?"
        r"\s*(?P<diameter>((?:(?:RZ|Z)?R)|/)\d{2}(?:[,.]\d)?(?:[CС]|LT)?)"
        r") "
    )
    size_pattern2 = (
        r"(?:"
        r"(?P<diameter>(?:(?:RZ|Z)?R)\d{2}(?:[,.]\d)?(?:[CС]|LT)?)"
        r"\s*(?:(?P<width>\d{2,3})[/xX*]?)?"
        # r"(?:(?P<height>\d{1,2}(?:[,.]\d{1,2})?))?"
        r"(?:(?P<height>\d{1,2}))?"
        r") "
    )
    c_pattern = r"(?:(?:^|\s)(?P<comercial>[CС]) )"

    result = parse(size_pattern, text)
    try:
        if result["width"] is None:
            result = parse(size_pattern2, text)
    except KeyError:
        if result["full_match"] == "":
            raise ValueError("Size not found in text")

    if result["width"]:
        width = float(result["width"].replace(",", "."))
        result["width"] = int(width) if width.is_integer() else width

    if result["height"] is None:
        result["height"] = ""

    if "/" in result["diameter"]:
        result["diameter"] = result["diameter"].replace("/", "R")

    result["diam"] = result["diameter"].strip("ZRCСLT")

    _c = parse(c_pattern, result.get("rest", ""))
    result["comercial"] = _c.get("comercial", "")
    result["rest"] = (
        result.get("rest", "").replace(_c.get("full_match", ""), "").strip()
    )

    return result


def parse_model_and_brand(text: str = "", seq: bool = False) -> dict[str, str]:
    result: dict[str, str] = {}
    if seq:
        result = parse_size(text)
    rest = result.get("rest", text).upper().replace("_", " ")

    brand_pattern = re.compile(
        "|".join(
            f"(?P<_{str(e)}>{re.escape(v)})" for e, v in enumerate(list(BRANDS.keys()))
        ),
        re.IGNORECASE,
    )
    brand_match = parse(brand_pattern, rest)
    # if brand_match:
    #     result["rest"] = brand_match["rest"]
    brand = BRANDS.get(brand_match.get("full_match", ""), "?")

    model = "?"
    if m := MODELS.get(brand, None):

        model_pattern = re.compile(
            "|".join(
                f"(?P<_{str(e)}>{re.escape(v)})" for e, v in enumerate(list(m.keys()))
            ),
            re.IGNORECASE,
        )
        model_match = parse(model_pattern, brand_match.get("rest", ""))
        model = m.get(model_match.get("full_match", ""), "?")
        if brand_match:
            result["rest"] = brand_match["rest"]
        result["rest"] = model_match.get("rest", "")

    result["brand"] = brand
    result["model"] = model
    return result


def parse_indexes(text: str = "", seq: bool = False):
    result: dict[str, str] = {}
    if seq:
        result = parse_model_and_brand(text=text, seq=True)
    rest = result.get("rest", text)

    indexes_pattern = r"\b(?:(?P<indexes>\d{2,3}(?:/\d{2,3})?\s?(?:[A-WY-ZТ]|ZR)))\b"

    indexes_match = parse(indexes_pattern, rest)
    result["indexes"] = indexes_match.get("indexes", "?")
    result["rest"] = indexes_match.get("rest", "")
    return result


def parse_suv(text: str = "", seq: bool = False):
    result: dict[str, str] = {}
    if seq:
        result = parse_indexes(text=text, seq=True)
    rest = result.get("rest", text)

    suv_pattern = r"(?P<suv>(?:^|\s)SUV)\b"
    suv_match = parse(suv_pattern, rest)

    result["suv"] = " SUV" if suv_match.get("suv", None) else ""
    result["rest"] = suv_match.get("rest", "")
    return result


def parse_xl(text: str = "", seq: bool = False):
    result: dict[str, str] = {}
    if seq:
        result = parse_suv(text=text, seq=True)
    rest = result.get("rest", text)

    xl_pattern = r"(?P<xl>(?:^|\s)XL)\b"
    xl_match = parse(xl_pattern, rest)

    result["xl"] = " XL" if xl_match.get("xl", None) else ""
    result["rest"] = xl_match.get("rest", "")
    return result


def parse_stud(text: str = "", seq: bool = False):
    result: dict[str, str] = {}
    if seq:
        result = parse_xl(text=text, seq=True)
    rest = result.get("rest", text)

    stud_pattern = r"(?P<stud>(?:^|\s)(ШИПЫ|ШИП|Ш|STUD)\b)"
    stud_match = parse(stud_pattern, rest)

    result["stud"] = True if stud_match.get("stud", None) else False
    result["rest"] = stud_match.get("rest", "")
    return result


def parse_year(text: str = "", seq: bool = False):
    result: dict[str, str] = {}
    if seq:
        result = parse_stud(text=text, seq=True)
    rest = result.get("rest", text)

    year_pattern = r"(?:(?P<year>20\d{2})( ГОД|ГОД|Г|Г\.))\b"
    year_match = parse(year_pattern, rest)
    result["year"] = year_match.get("year", "")
    result["rest"] = year_match.get("rest", "")
    return result


def parse_all(text: str) -> dict[str, str]:
    result: dict[str, str] = parse_year(text=text, seq=True)
    return result


if __name__ == "__main__":
    print(parse_all("автошина 33x12,5 R15 DYNAMO HISCEND-H_MMT01 108Q"))
