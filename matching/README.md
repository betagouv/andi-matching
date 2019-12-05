## Matching ANDi

Librarie matching et interface en ligne de commande

- Sur base de critères définis, génère une liste de correspondances

Critères supportés:
- adresse d'origine
- code rome du métier recherché
- distance
- taille d'entreprise
- qualité du contact
- qualité de l'accueil

### Correspondance rome => naf

Une première version de l'outil employait des fiches "manuelles", dans le répertoire **rome\_defs**. La qualité était suffisante
mais difficile à mettre en oeuvre pour l'ensemble des codes.

Une seconde version utilise un tableau de correspondance (voir [andi-data](https://github.com/betagouv/andi-data/) ) sur l'ensemble
des codes nafs, qui permet également une pondération plus fine.

## Utilisation
```shell
# Aide
./match.py --help
# Requête de base
./match.py --debug --config_file config.yaml run-csv --lat '49.0465' --lon '2.0655' --max-distance 10 --rome K2112
```


## Résultats
Quelques exemples de résultats obtenus
```shell
Matching started, lat/lon 49.0465/2.0655, max 10 km, ROME: K2112
Parsed sizes: tpe: False, pme: False, eti: False, ge: False
Connecting to database ...
Obtained database cursor
Obtained results preview (score is naf / size / geo / welcome / contact):
8559A  INSTITUT DE FORMATION ET DE CO  	Formation continue d'adultes       	2 km	(5-1-3-2-2 => 43)	34003
8413Z  AGIR POUR LA VALORISATION POUR  	Administration publique (tutelle) des	2 km	(5-1-3-2-2 => 43)	27991
9411Z  CHAMBRE DE METIERS ET DE L'ART  	Activités des organisations patronale	1 km	(5-1-3-2-2 => 43)	26738
8559A  BUSINESS CLASS LANGUAGE SOLUTI  	Formation continue d'adultes       	1 km	(5-1-3-2-2 => 43)	51197
8559A  CENTRE DE FORMATION ET CONSEIL  	Formation continue d'adultes       	6 km	(5-1-2-2-2 => 42)	50920
8559A  OBJECTIF EMPLOI OUEST           	Formation continue d'adultes       	13 km	(5-1-1-2-2 => 41)	543824
8413Z  MISSION LOCALE DE SARTROUVILLE  	Administration publique (tutelle) des	14 km	(5-1-1-2-2 => 41)	530583
8810C  UNIRH 95                        	Aide par le travail                	2 km	(4-1-3-2-2 => 38)	38731
8559B  ASSOCIATION INCITE              	Autres enseignements               	3 km	(4-1-3-2-2 => 38)	42805
7830Z  TILT SERVICES                   	Autre mise à disposition de ressource	1 km	(4-1-3-2-2 => 38)	31466
8559A  SARL EDU'CAB                    	Formation continue d'adultes       	1 km	(5-1-3-1-1 => 37)	95372
8559A  ENVOL IDF                       	Formation continue d'adultes       	3 km	(5-1-3-1-1 => 37)	66540
8559A  LENA                            	Formation continue d'adultes       	2 km	(5-1-3-1-1 => 37)	91563
8560Z  ESPACES & LUMIERES              	Activités de soutien à l'enseignement	2 km	(5-1-3-1-1 => 37)	65189
8559A  JADA FORMATION                  	Formation continue d'adultes       	1 km	(5-1-3-1-1 => 37)	89635
8559A  SMART EVOLUTION CONSULTING      	Formation continue d'adultes       	1 km	(5-1-3-1-1 => 37)	90809
8559A  HEURTAUX  FORMATION CONSEIL     	Formation continue d'adultes       	3 km	(5-1-3-1-1 => 37)	95574
8559A  QUARTZ ACTIVE                   	Formation continue d'adultes       	2 km	(5-1-3-1-1 => 37)	89048
8559A  TREE OF SCIENCE                 	Formation continue d'adultes       	3 km	(5-1-3-1-1 => 37)	83629
8559A  AGIR SUR LES COMPETENCES        	Formation continue d'adultes       	5 km	(5-1-3-1-1 => 37)	68280
```
