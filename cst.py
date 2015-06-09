#!/usr/bin/env python3
# -*- coding: iso-8859-2 -*-
#CST:xjurik08

import sys
import re
import os
from os.path import *
import collections
from collections import deque
import codecs


# Trida parametry stara pouze o zadane parametry
# a take o volani help a pripadne osetreni kombinaci

class Parametry:

	#pole pro parametry, nadefinuju si jednotlive prvky pole
	params = {
		"--help":False,
		"--input":False,
		"--nosubdir":False,
		"--output":False,
		"-k":False,
		"-o":False,
		"-i":False,
		"-w":False,
		"-c":False,
		"-p":False
	}

	# funkce help zkontroluje jake parametry byly nastaveny
	# pokud vse bylo ok tak tiskne help, v opacnem pripade vraci false 
	def printHelp(self):
		# je nastaven parametr help
		if(self.params["--help"] == True):
			isvalid = True
			for prvek in self.params:
				# pokud nektery prvek byl nastaven tak se nejedna o validni parametry
				if(self.params[prvek] != False and prvek != "--help"):
					isvalid = False
			# pokud je vse v poradku tisknu
			if isvalid == True:
				print ("Skript provadi analyzu zdrojovych souboru jayzak C podle  ")
				print ("standardu ISO C99, ktery ve stanovenem formatu vypise     ")
				print ("statistiky komentaru, klicovych slov, operatoru a retezcu.")
				print ("Tento skript bude pracovat s temito parametry:            ")
				print ("        -help              - vypise tuto napovedu         ")
				print ("        --input=fileordir  - kde fileordir je bud soubor  ")
				print ("                             nebo adresar                 ")
				print ("        --nosubdir         - prohledavani je provadeno    ")
				print ("                             pouze ve zdrojovem adresari, ")
				print ("                             v pripade ze je zadan soubor ")
				print ("                             konci chybou                 ")
				print ("        --output=filename  - vysledek je ulozen do souboru")
				print ("                             s nazvem filename            ")
				print ("        -k                 - vypise pocet klicovych slov  ")
				print ("        -o                 - vypise pocet operatoru       ")
				print ("        -i                 - vypise pocet identifikatoru  ")
				print ("        -w=pattern         - vyhleda presny retezec       ")
				print ("                             pattern                      ")
				print ("        -c                 - vypise pocet znaku komentaru ")
				print ("        -p                 - v kombinaci s predchozimi    ")
				print ("                             parametry bude vypisovat     ")
				print ("                             pouze nazvy souboru          ")
				print (" Pozn: parametry -k,-o,-i,-w a -c nelze kombinovat        ")
				print ("       a alespon jeden z techto parametru je povinny      ")
				sys.exit(0)
			# jinak vracim false 
			else:
				return False
		return True
					
	# validate mi kontroluje moznosti zadanych parametru
	def validate(self):
		# pokud help vratil false tak nastala nekde chyba -> koncim
		if(self.printHelp() == False):
			sys.stderr.write ("Error - help musi byt zadan samostatne\n")
			sys.exit(1)
		# nastavim si kolik pomonou promenou pocet_prepinacu
		pocet_prepinacu = 0
		# prochazim sve pole s parametry (jen vyhledavaci prepinace)
		for prvek in [self.params["-k"] , self.params["-o"] ,self.params["-i"] ,self.params["-w"] , self.params["-c"]]:
			# pokud je nektery nastaven tak zvysim pocet
			if(prvek != False):
				pocet_prepinacu +=1

		# jednoducha kontrola pro zjisteni kolik prepinacu bylo zadano
		# pokud je pocet prepinacu vetsi nez 1 tak konci s chybou
		if(pocet_prepinacu > 1):
			sys.stderr.write ("Error - byl zadan vic nez 1 vyhl. parametr\n")
			sys.exit(1)
		# pokud nebyl nastaven zadny parametr podle ktereho by se melo vyhledavat
		# tak koncim s chybou
		elif(pocet_prepinacu == 0):
			sys.stderr.write ("Error - chybi parametr vyhledavani\n")
			sys.exit(1)


	# zpracovani parametru, prochazim argv bez nazvu programu a hledam ktere
	# parametry byly zadany, pritom zaroven kontroluju jestli nahodou uz parametr
	# nebyl pred tim zadan - jednalo by se o zdvojeny parametr -> chyba
	def __init__(self):
		for argument in sys.argv[1:]:
			if (argument[:8] == "--input="):
				if(self.params["--input"] != False):
					sys.stderr.write ("Error - zdvojeny parametr\n")
					sys.exit(1)
				else:	
					param = argument.split("=",2)
					if(self.params["--input"] == False):
						# pokud byl zadan neuplny input tak koncim chybou
						if(param[1] == ''):
							sys.stderr.write ("Error - spatne zadany parametr\n")
							sys.exit(1)
						else:
							self.params["--input"] = os.path.abspath(param[1])
			elif(argument[:9] == "--output="):
				if(self.params["--output"] != False):
					sys.stderr.write ("Error - zdvojeny parametr\n")
					sys.exit(1)
				else:
					param = argument.split("=",2)
					if(self.params["--output"] == False):
						#pokud byl zadan neuplny output tak koncim s chybou
						if(param[1] == ''):
							sys.stderr.write ("Error - spatne zadany parametr\n")
							sys.exit(1)
						else:
							self.params["--output"] = param[1]
			elif(argument[:3] == "-w="):
				if(self.params["-w"] != False):
					sys.stderr.write ("Error - zdvojeny parametr\n")
					sys.exit(1)
				else:
					param = argument.split("=",2)
					if(self.params["-w"] == False):
						if(param[1] == ''):
							sys.stderr.write ("Error - spatne zadany parametr\n")
							sys.exit(1)
						else:
							self.params["-w"] = param[1]	
			elif(argument == "--nosubdir"):
				if(self.params["--nosubdir"] == True):
					sys.stderr.write ("Error - zdvojeny parametr\n")
					sys.exit(1)
				else:
					self.params["--nosubdir"] = True
			elif(argument == "-k"):
				if(self.params["-k"] == True):
					sys.stderr.write ("Error - zdvojeny parametr\n")
					sys.exit(1)
				else:
					self.params["-k"] = True
			elif(argument == "-p"):
				if(self.params["-p"] == True):
					sys.stderr.write ("Error - zdvojeny parametr -p\n")
					sys.exit(1)
				else:
					self.params["-p"] = True
			elif(argument == "-o"):
				if(self.params["-o"] == True):
					sys.stderr.write ("Error - zdvojeny parametr\n")
					sys.exit(1)
				else:
					self.params["-o"] = True
			elif(argument == "-i"):
				if(self.params["-i"] == True):
					sys.stderr.write ("Error - zdvojeny parametr\n")
					sys.exit(1)
				else:
					self.params["-i"] = True
			elif(argument == "-c"):
				if(self.params["-c"] == True):
					sys.stderr.write ("Error - zdvojeny parametr\n")
					sys.exit(1)
				else:
					self.params["-c"] = True
			elif(argument == "--help"):
				if(self.params["--help"] == True):
					sys.stderr.write ("Error - zdvojeny parametr\n")
					sys.exit(1)
				else:
					self.params["--help"] = True
			else:
				sys.stderr.write ("Error - neznam tyto parametry\n")
				sys.exit(1)
		# skoncilo prochazeni parametru, volam funkci validate
		self.validate()

# Trida Soubor obsahuje veskere prostredky pro praci se souborem
# tedy jak ma soubor vypadat pri hledani a pote funkce pro konkretni
# vyhledavani podle zadanych parametru
class Soubor:
	in_file = "" 		# vstupni soubor
	vysledek = 0		# jedna se o vysledek - pocet nalezu
	cesta = ""			# cesta k souboru

	delka_cesty = 0
	delka_vysledku = 0

	nazev_souboru = ""

	# otevreni jednotliveho souboru, ocekava cestu k souboru
	# a parametr True/False zda byl zadan parametr -p ci nikoliv 
	def __init__(self, cesta, cela):
		self.cesta = cesta
		# pokud byl nastaven nebyl nastaven - p -> False
		# tak vracim celou cestu k souboru
		if(cela==False):
			self.delka_cesty = len(cesta)
			self.nazev_souboru = cesta
		# v opacnem pripade pokud je zadan -p -> True
		# tak vracim pouze nazev, coz je filename
		else:
			path, filename = os.path.split(cesta)
			self.delka_cesty = len(filename)
			self.nazev_souboru = filename 

		# v zadani bylo psane ze kodovani souboru musi byt latin2, to jsem take
		# zohlednil pri nacitani souboru
		try:
			self.in_file = codecs.open(self.cesta, 'r', 'iso-8859-2').read()
		# pokud se nepodari otevrit soubor tak chyba
		except IOError:
			sys.stderr.write("Error - nepodarilo se otevrit soubor\n")
			sys.exit(21)

	# pozdeji jsem pro jistotu v celem kodu odstranoval konce radku \r\n
	# ikdyz jsem v nekterych funkcich tuto moznost zohlednoval
	def nahrad_konec(self):
		self.in_file = self.in_file.replace("\r\n", "\n")

#************ POCITANI ************

	# funkce smaze komentare v mojem souboru
	# pro blokove komentare jsem vyuľil regularni vyraz
	# pro jednoradkove se muselo uvazovat o znaku \ proto
	# jsem si napsal funkci pro mazani
	def smaz_koment(self):
		self.in_file = re.sub(re.compile("/\*.*?\*/", re.DOTALL),"", self.in_file)
		self.smaz_jednoradkovy_komentar()
		return self.in_file

	# funkce smaze jednoradkove komentare i s ohledem na \
	def smaz_jednoradkovy_komentar(self):
		i = 0 			# pomocny index
		out_str = "" 	# vystupni string
		# dokud nedojde konec souboru tak po znacich kontroluj
		while(i < len(self.in_file)):
			# pokud se jedna o 2 lomitka 
			if(self.in_file[i] == '/' and self.in_file[i+1] == '/'):
				# zacatek jednoradkoveho komentare
				i = i+2
				while(i < len(self.in_file)-1):
					# pokud prijde konec radku, tak ho smazu
					if(self.in_file[i+1] == '\n' or self.in_file[i+1] == '\r'):
						out_str += " "
						if(self.in_file[i] != '\\'):
							i += 1
							break
					# kdyz za // prijde cokoliv jineho tak to mazu
					else:
						out_str += " "
					i += 1
			out_str += self.in_file[i]
			i += 1
		self.in_file = out_str
		#print(self.in_file)

	# funkce smaze veskere makra v kodu, jedna se o lehkou obmenu 
	# z predesle funkce
	# opet bylo nutne si dat pozor na zalomeni \
	def smaz_makro(self):
		out_str = "" # vystupni string
		i=0			 # pomocny index
		while i < len(self.in_file):
			# pokud prislo #
			if(self.in_file[i] == '#'):
				# zacina makro 
				out_str += " "
				# pokracuji v makru 
				while(i < len(self.in_file)-1):
					# pokud prijde konec radku tak breakni
					if(self.in_file[i+1] == '\n' or self.in_file[i+1] == '\r'):
						#out_str += " "
						if(self.in_file[i] != '\\'):
							i += 1
							break
					# jinak nahrazuj uvnitr se za mezery
					else:
						out_str += " "
					i += 1
			out_str += self.in_file[i]
			i+=1
		self.in_file = out_str
		#print(self.in_file)

	# funkce pro smazani retezce, zde jsem se hlavne uchylil
	# k nahrazovani za mezery z tohoto duvodu:
	#       pripad "ahoj /* toto neni komentar */"
	#		pri pocitani komentaru by se jednalo o chybu
	# 		->nahrazeni stejnym poctem mezer = stejne dlouhy string
	# jedna se o stejny postup jako u predeslych mazani
	def smaz_retezec(self):
		out_str = ""
		i=0
		while i < len(self.in_file):
			# pokud prisla uvozovka
			if(self.in_file[i] == '\"'):
				out_str += "\""
				while(i < len(self.in_file)-1):
					if(self.in_file[i+1] == '\"'):
						#out_str += "1"
						if(self.in_file[i] != '\\'):
							i += 1
							break
					else:
						out_str += " "
					i += 1
			# pokud prisel apostrof
			elif(self.in_file[i] == '\''):
				out_str += "\'"
				while(i < len(self.in_file)-1):
					if(self.in_file[i+1] == '\''):
						#out_str += "1"
						if(self.in_file[i] != '\\'):
							i += 1
							break
					else:
						out_str += " "
					i += 1
			out_str += self.in_file[i]
			i+=1
			
		self.in_file = out_str		
		#print(self.in_file)

	# funkce pro smazani klicovych slov - pouzivam jednoduchy regularni vyraz
	def smaz_klic(self):
		self.in_file = re.sub("(auto|break|case|char|const|continue|default|do|double|else|enum|extern|float|for|goto|if|inline|int|long|register|restrict|return|short|signed|sizeof|static|struct|switch|typedef|union|unsigned|void|volatile|while)", "", self.in_file)

		return self.in_file



	#************ POCITANI ************ 

	# funkce spocita pocet klicovych slov, vyuzivam regularni vyraz,
	# nejprve jsem si vse rozdelil pres cokoliv co neni slovo -nonword character
	# pote jsem v jednotlivych slovech hledal klicove slovo
	def spoc_klic(self):
		pocet_klicu = 0

		for word in re.split("\W+", self.in_file):
			if re.match("(auto|break|case|char|const|continue|default|do|double|else|enum|extern|float|for|goto|if|inline|int|long|register|restrict|return|short|signed|sizeof|static|struct|switch|typedef|union|unsigned|void|volatile|while)", word):
				pocet_klicu += 1

		self.vysledek = pocet_klicu
		# ukladam si delku ve znacich pro pozdejsi vypis
		self.delka_vysledku = len(str(pocet_klicu))
		return pocet_klicu

	# spocitani komentaru je stavovy automat, zohlednuji po pocitani 
	# se zalomenim radku \
	def spoc_koment(self):
		stav = 0
		pocet = 0
		for ch in self.in_file:
			# stav 0, pokud prijde lomitko tak zvysim pocitadlo a jdu do stavu 1
			# pokud prijde cokoliv jineho zustavam ve stavu 0
			if stav == 0:
				if(ch == "/"):
					pocet += 1
					stav = 1
				else:
					stav = 0
			# stav 1, pokud mi prijde dalsi lomitko mam zacatek komentare //
			# zvysim pocitadlo a jdu do stavu 2, pokud mi prijde hvezdicka
			# jedna se o blokovy komentar a jdu do stavu 3
			elif stav == 1:
				if(ch == "/"):
					pocet +=1
					stav = 2
				elif(ch == "*"):
					pocet +=1
					stav = 3
				else:
					pocet -=1	# vracim, nebyl to komentar
					stav = 0
			# stav 2 - mam radkovy komentar
			# pokud prijde \ tak zvysim pocitadlo a jdu do stavu 4
			elif stav == 2:
				if(ch == "\\"):
					pocet +=1
					stav = 4
			# pokud prijde konec radku tak komenar skoncil
				elif(ch == "\n"):
					pocet +=1
					stav = 0
			# cokoliv jineho je uvnitr komentare a zvysuju pocitadlo
				else:
					pocet +=1
					stav = 2
			# stav 3 - mam blokovy komentar, ocekavam hvezdicku
			# pokud prijde jdu do stavu 5
			elif stav == 3:
				if(ch == "*"):
					pocet +=1
					stav = 5
				else:
					pocet +=1
					stav = 3
			# stav 4 - ze stavu 2 vim ze prislo \
			# ocekavam konec radku		
			elif stav == 4:
				if(ch == "\n"):
					pocet += 1
					stav = 2
			# stav 5 - ze stavu 3 vim ze mi prisla *, tak ocekavam
			# lomeno na ukonceni blokoveho komentare
			elif stav == 5:
				if(ch == "/"):
					pocet +=1
					stav = 0
				# pokud prijde dalsi *, zustavam
				elif(ch == "*"):
					pocet +=1
					stav = 5
				# cokoliv jineho, navysuju 
				else:
					pocet +=1
					stav = 2

		self.vysledek = pocet
		# opet si ukladam delku ve znacich
		self.delka_vysledku = len(str(pocet))
		return pocet

	# funkce pro spocitani operatoru, opet vyuzivam regularni vyraz a findall
	def spoc_op(self):
		pocet_op = 0
		pocet_op = re.findall("(((\-|\+|\/|\*|\!|\=|\&|\%|\||\^)?=)|(\&(\&)?)|(\|(\|)?)|(>(>)?(=)?)|(<(<)?(=)?)|\!|\*|\/|\^|\~|(\_|[a-zA-Z0-9])\.\D|\-\>|(\-(\-)?)|(\+(\+)?))", self.in_file)

		# zjistenu poctu
		self.vysledek = len(pocet_op)
		# ulozeni delky poctu ve znacich
		self.delka_vysledku = len(str(self.vysledek))


	# funkce spocita identifikatory pres regularni vyrazy
	# opet si vse rozdelim pres vsechno co neni slovo a hledam
	# mozny identifikator
	def spoc_id(self):
		pocet_id = 0
		for word in re.split("\W+", self.in_file):
			if re.match("([_a-zA-Z][_a-zA-Z0-9]*)", word):
				pocet_id += 1

		self.vysledek = pocet_id
		self.delka_vysledku = len(str(pocet_id))
		return pocet_id

	# funkce spocita pocet patternu v kodu,
	# opet opracuji s regularnim vyrazem
	def spoc_pattern(self):
		posun = 0
		vysl = ""
		pattern = Parametry.params["-w"];
		while(posun < len(pattern)):
			if re.match("(\\|\(|\)|\[|\]|\{|\}|\$|\^|\*|\.|\+|\-|\|\<|\>|\&|\ )", Parametry.params["-w"]):
				pattern = pattern[:posun] + "\\" + pattern[posun:]
				posun += 1
			posun += 1
		#print(pattern)
		Parametry.params["-w"] = pattern

		vysl = re.findall(Parametry.params["-w"] , self.in_file)
		self.vysledek = len(vysl)
		self.delka_vysledku = len(str(self.vysledek))


# ********* PRACE SE SOUBORY **********

# funkce mi najde veskere soubory pokud nebyl zadan parametr input
# vyuzivam os.walk, ktery je na to primo delany
def hledej_soubory(Parametry):
	# vytvorim si frontu do ktere budu postupne davat cesty k souborum
	array = deque()
	for root, dirs, files in os.walk(os.getcwd()):
		# pokud vsak byl zadan parametr nosubdir
		# nesmi prohledavat dal - tedy pokud se tento root neshoduje
		# se slozkou v getcwd tak tyto slozky neprochazim
		if(Parametry.params["--nosubdir"] == True):
			if(root != os.getcwd()):
				continue
		for name in files:
			fileName, fileExtension = os.path.splitext(name)
			# koncovky bere pouze .h a .c
			if(fileExtension == ".h" or fileExtension == ".c"):
				# na konec jej oteviram pres tridu soubor kdy u predevam cestu a parametr -p (True/False)
				array.append(Soubor(os.path.join(root,name), Parametry.params["-p"])) 
	# pokud je retezec prazdny - nenasel nic tak vracim chybu
	if(len(array) == 0):
		sys.stderr.write ("Error - nenasel jsem zadny soubor\n")
		sys.exit(2)
	return array

# funkce pokud byl zadan parametr input
def input_soubor(Parametry):
	# jedna se o jeden soubor nebo o slozku , proto si opet vytvorim frontu
	array = deque()

	# kontroluju jestli je input soubor
	if os.path.isfile(Parametry.params['--input']):
		# pokud se jedna o soubor a byl zadan parametr nosubdir tak koncim s chybou
		if (Parametry.params['--nosubdir'] == True):
			sys.stderr.write ("Error - spatna kombinace parametru, input je soubor\n")
			sys.exit(1)
		# jinak si soubor ulozim do fronty
		else:
			array.append(Soubor(Parametry.params['--input'], Parametry.params["-p"]))
	# pokud se jedna o slozku tak si jednotlive soubory budu ukladat do fronty
	elif os.path.isdir(Parametry.params['--input']):
		for root, dirs, files in os.walk(Parametry.params['--input']):
			# pokud byl zadan parametr nosubdir tak stejne jako u noninput pripadu
			# pokud se root neshoduje s parametrem input tak dalsi slozky neprochazim
			if(Parametry.params["--nosubdir"] == True):
				if(root != Parametry.params["--input"]):
					continue
			for name in files:
				fileName, fileExtension = os.path.splitext(name)
				if(fileExtension == ".h" or fileExtension == ".c"):
					# ukladam si soubory do fronty
					array.append(Soubor(os.path.join(root,name), Parametry.params["-p"]))
	# jinak koncim s chybou
	else:
		sys.stderr.write ("Error - soubor nebo slozka neexistuje\n")
		sys.exit(2)

	return array


#************* ZPRACOVANI *************

# v tomto bloku kodu jen zpracuju jednotlive soubory
# a pote provadim jednotlive vyhledavani podle toho 
# co bylo zadano

# zavolam parametry
a = Parametry()

# kontroluju zda byl nebo nebyl zadan input
if(Parametry.params['--input']) == False:
	files = hledej_soubory(a)
else:
	files = input_soubor(a)


for f in files:
	# predpriprava souboru
	# pokud byl zadan parametr k nebo i nebo o tak si vse nepotrebne smazu
	if(a.params["-k"] == True or a.params["-i"] == True or a.params["-o"] == True):
		f.nahrad_konec()
		f.smaz_koment()
		f.smaz_retezec()
		f.smaz_makro()
	# pokud byl zadan parametr c tak smazu vse nepotrebne
	elif(a.params["-c"] == True):
		f.nahrad_konec()
		f.smaz_retezec()
		f.smaz_makro()


	# kontrola jednotlivych parametru
	if(a.params["-k"] == True):
		# pocitat klicove slova
		f.spoc_klic()
	if(a.params["-c"] == True):
		# pocitam komentare
		f.spoc_koment()
	if(a.params["-o"] == True):
		# pocitam operatory
		f.spoc_op()
	if(a.params["-i"] == True):
		# zde bylo nutne si dat pozor na klice
		# ktere by mohli mit stejny tvar jako identifikator
		# proto je pro jistotu smazu
		f.smaz_klic()
		f.spoc_id()
	if(a.params["-w"] != False):
		# pocitam patterny
		f.spoc_pattern()

	# aby nebyla zaplnena pamet
	f.in_file = ""

#************* FINALNI VYPIS *************

# zde pouzivam jednoduchou matematiku na srovnani delky
# vsech souboru a vysledku a pote doplneni jedne mezery

# nadefinuju si nejdelsi soubor - musim pocitat s CELKEM: (7 znaku)
nejdelsi_soubor = 7
nejdelsi_cislo = 0

celkem_hodnoty = 0

# nejprve hledam nejdelsi soubor a nejdelsi cislo 
for f in files:
	celkem_hodnoty += f.vysledek
	if(nejdelsi_cislo < len(str(celkem_hodnoty))):
		nejdelsi_cislo = len(str(celkem_hodnoty))

	if(nejdelsi_soubor < f.delka_cesty):
		nejdelsi_soubor = f.delka_cesty
		#cislo_souboru = f.delka_cesty
	if(nejdelsi_cislo < f.delka_vysledku):
		nejdelsi_cislo = f.delka_vysledku

# ted budu projizdet vsechny soubory a budu od 
# nejdelsiho soubrou(ve znacich) a od nejdelsiho cisla(ve znacich)
# odcitat jednotlive delky souboru, ktere jsou nadefinovane v tride Soubor

str_celkem = "0"
vystupni_text = ""
for f in files:
	mezery = nejdelsi_soubor - f.delka_cesty
	cislo_mez = nejdelsi_cislo - f.delka_vysledku
	str_vysledek = str(f.vysledek)
	str_celkem = str(celkem_hodnoty)
	# ke kazdemu pak pridavam tolik mezer kolik byl rozdil
	vystupni_text = vystupni_text + f.nazev_souboru + " "*mezery + " " + " "*cislo_mez + str_vysledek + "\n"

#bylo nutne zpracovat jeste CELKEM: kde je stejny postup
celkem_cislo = 0
celkem_mezery = nejdelsi_soubor - 7
celkem_cislo = nejdelsi_cislo - len(str(celkem_hodnoty))
vystupni_text = vystupni_text + "CELKEM:" + " "*celkem_mezery + " " + " "*celkem_cislo + str_celkem + "\n"


# finalni poslani vysledku do souboru nebo na stdout
if(Parametry.params["--output"] == False):
	sys.stdout.write(vystupni_text)
else:
	try:
		vystup = open(Parametry.params["--output"], "w")
		vystup.write(vystupni_text)
		vystup.close()
	except IOError:
		sys.stderr.write ("Error - nepodarilo se zapsat do souboru\n")
		sys.exit(3)



sys.exit(0)
