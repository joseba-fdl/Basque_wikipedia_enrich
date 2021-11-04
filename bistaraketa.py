#https://eu.wikipedia.org/wiki/Wikiproiektu:Euskarazko_albisteetako_Izen_Entitateak

import pandas as pd
import datetime
from collections import Counter
import re
import os
import time
import scattertext as st
import spacy
from pprint import pprint
import pywikibot
import requests


WIKIPEDIA_KONTUA=''
WIKIPEDIA_PASAHITZA=''

def sortu_wp_zirriborroa (nor):

    query = """
    SELECT ?a ?aLabel ?propLabel ?b ?bLabel
    WHERE
    {
      ?item rdfs:label """
    query = query + '"' + nor +'"' + """@es.
      ?item ?a ?b.

      SERVICE wikibase:label { bd:serviceParam wikibase:language "eu". } 
      ?prop wikibase:directClaim ?a .
    }
    """
    r = requests.get('https://query.wikidata.org/sparql', params = {'format': 'json', 'query': query})
    data = r.json()


    propietateak = {}
    for item in data['results']['bindings']:
        propietateak[item['propLabel']['value']] = item['bLabel']['value']

    jaiolekua = propietateak['jaiolekua'] if 'jaiolekua' in propietateak else "AAAa"
    jaiodata = propietateak['jaiotza data'] if 'jaiotza data' in propietateak else "2050"
    jarduera = propietateak['jarduera'] if 'jarduera' in propietateak else "CCCc"
    herritartasuna = propietateak['herritartasuneko herrialdea']  if 'herritartasuneko herrialdea' in propietateak else "ZZZz"

    izenburu = "\n=" + nor + "=\n"
    zirri = "{{zirriborroa}} \n"
    bio = "{{biografia infotaula automatikoa}}\n"
    lerroburu = "'''" + nor + "''' ([[" +jaiolekua + "]], [[" + jaiodata[:4] + "]]) [[" + herritartasuna + "]]-eko [[" + jarduera + "]]-a da."

    #############
    corpusa_albisteak="data/termino_corpusa.tsv" # [egunkari/data/lang/albiste_url/per/org/loc]
    df_albisteak=pd.read_csv(corpusa_albisteak, sep='\t', parse_dates=[1]) # datak datetimera pasatzeko 1 zutabea
    url_albiste=[]
    egunkaria_albiste=[]
    for index, row in df_albisteak.tail(40000).iterrows(): #.tail(2000)
        if len(row[4])>2:
            found_albisteak=re.findall('('+nor+')',str(row[4]))
            if len(found_albisteak) > 0:
                url_albiste.append(row[3])
                egunkaria_albiste.append(row[0])
                
    albiste_egunkari_dict={}
    for url_albiste_bakoitza, egunkaria_albiste_bakoitza in zip(url_albiste, egunkaria_albiste):
        if egunkaria_albiste_bakoitza not in albiste_egunkari_dict:
            albiste_egunkari_dict.update({egunkaria_albiste_bakoitza: []})
        albiste_egunkari_dict[egunkaria_albiste_bakoitza].append(url_albiste_bakoitza)
            
    albisteak=''
    #for url_albiste_bakoitza, egunkaria_albiste_bakoitza in zip(url_albiste, egunkaria_albiste):
    for egunkaria_albiste_bakoitza in albiste_egunkari_dict:
        albisteak += '\n\nAstean zehar '+egunkaria_albiste_bakoitza+'-n azaldu diren albisteak.'
        for item in albiste_egunkari_dict[egunkaria_albiste_bakoitza]:
            #albisteak += "<ref>{{Erreferentzia| izenburua="+url_albiste_bakoitza+"|hizkuntza=eu|url="+url_albiste_bakoitza+"}}</ref>"
            albisteak += "<ref>{{Erreferentzia| izenburua="+item+"|hizkuntza=eu|url="+item+"}}</ref>"

    erref = "\n== Erreferentziak ==\n{{Erreferentzia zerrenda}}\n\n== Kanpo estekak ==\n"
    berrian = "* [https://www.berria.eus/bilatzailea/?q="+ nor.replace(" ","+") +  " " +nor +"] berria egunkarian\n"
    argian = "* [https://www.argia.eus/bilaketa?q="+ nor.replace(" ","+") +  " " +nor +"] argia aldizkarian\n" 
    eitben = "* [https://www.google.com/search?q=site:www.eitb.eus/eu/%20"+ nor.replace(" ","%20") +  " " +nor + "] Euskal Telebistan\n" 
    mediatan = berrian + argian + eitben

    nor_21 = nor.split(' ')
    if len(nor_21) == 2:
       nor_21 = nor_21[1] + ", " + nor_21[0]
    else:
       nor_21 = nor
       
    bizialdia = "{{bizialdia|" + jaiodata[:4] + "eko||"+ nor_21 +"}}\n"
    
    kategoriak = "\n[[Kategoria:" +jaiolekua +"]]"
    kategoriak = kategoriak + "\n[[Kategoria:" + jarduera + "]]"

    artikulua = izenburu + zirri + bio + lerroburu + albisteak + erref + mediatan + bizialdia + kategoriak
    site = mwclient.Site('eu.wikipedia.org')
    site.login(WIKIPEDIA_KONTUA,WIKIPEDIA_PASAHITZA)
    page_zirriborro = site.Pages['Wikiproiektu:ieproba/'+'_'.join(nor.split())]
    page_zirriborro.save(artikulua)
    return artikulua

def filtratu_solteak(zerrenda1):
    zerrenda2=[]
    for item in zerrenda1:
        if len(item.split()) > 1:
            zerrenda2.append(item)
    return zerrenda2


def asteko_entitate_zerrenda_eguneratua():        
    corpusa="data/termino_corpusa.tsv" ## CORPUS ##[egunkari/data/lang/albiste_url/per/org/loc]
    df=pd.read_csv(corpusa, sep='\t', parse_dates=[1]) # datak datetimera pasatzeko 1 zutabea
    data_orain=datetime.datetime.now().date() #### DATE 
    data_astebete_atzera=data_orain-datetime.timedelta(days=7)
    TRESHOLD=0
    for item in df['data'].tolist():
        if item.date() >= data_astebete_atzera:
            break
        TRESHOLD+=1

    hitz_hutsalak=[', ',''] ## Add stopwords

    collected={'index':[],'entities':[]}
    collected_batera=[]
    collected_batera1=[]
    collected_batera2=[]

    zutabea=4 # pertsonak:4 erakundeak:5 tokiak:6
    for index, row in df.iterrows():
        if row[zutabea]!='[]': # per zutabea
            kk=row[zutabea].split('[')[1].split(']')[0].split('\'')
            for j in hitz_hutsalak: kk=list(filter(lambda x: x!=j, kk)) # zarata kendu
            kk=list(filter(lambda x: not re.search('[,|/»!\"]',x), kk)) # koma badauka bota
            if len(kk)>0:
                kk=list(set(kk)) # errepikatuak kendu
                kk=filtratu_solteak(kk) ######## filtratu_solteak() LERRO BAT GEHITUTA
                collected['index'].append(index)
                collected['entities'].append(kk)#" , ".join(kk))
                collected_batera.extend(kk)
                if index < TRESHOLD: collected_batera1.extend(kk) #### TRESHOLD!!
                else: collected_batera2.extend(kk)


    # TF-IDF
    bagOfWordsA = collected_batera1
    bagOfWordsB = collected_batera2

    numOfWordsA = dict.fromkeys(set(collected_batera), 0)
    for word in bagOfWordsA:
        numOfWordsA[word] += 1

    numOfWordsB = dict.fromkeys(set(collected_batera), 0)
    for word in bagOfWordsB:
        numOfWordsB[word] += 1

    def computeTF(wordDict, bagOfWords):
        tfDict = {}
        bagOfWordsCount = len(bagOfWords)
        for word, count in wordDict.items():
            tfDict[word] = count / float(bagOfWordsCount)
        return tfDict

    tfA = computeTF(numOfWordsA, bagOfWordsA)
    tfB = computeTF(numOfWordsB, bagOfWordsB)


    def computeIDF(documents):
        import math
        N = len(documents)
    
        idfDict = dict.fromkeys(documents[0].keys(), 0)
        for document in documents:
            for word, val in document.items():
                if val > 0:
                    idfDict[word] += 1
    
        for word, val in idfDict.items():
            idfDict[word] = math.log(N / float(val))
        return idfDict

    idfs = computeIDF([numOfWordsA, numOfWordsB])

    def computeTFIDF(tfBagOfWords, idfs):
        tfidf = {}
        for word, val in tfBagOfWords.items():
            tfidf[word] = val * idfs[word]
        return tfidf

    tfidfA = computeTFIDF(tfA, idfs)
    tfidfB = computeTFIDF(tfB, idfs)

    df_terms = pd.DataFrame([tfidfA, tfidfB])
    df_terms_T = df_terms.T
    df_terms2 = df_terms_T
    df_terms2.reset_index(inplace=True)

    zaharrak_ordenatuta=df_terms2.sort_values(0, ascending=False)['index'].values.tolist()
    berriak_ordenatuta=df_terms2.sort_values(1, ascending=False)['index'].values.tolist()

    ohikoenak=pd.DataFrame(Counter(collected_batera).most_common())[0].values.tolist()

    berriak_ordenatuta_sample=berriak_ordenatuta[:100]

    kont=0
    ie_zerrenda_bueltatu=[]
    for item in ohikoenak:
        for item2 in berriak_ordenatuta_sample:
            if item==item2 and kont<10:
                ie_zerrenda_bueltatu.append(item)
                kont+=1

    #### Gorde csv-an ####                   
    lerroa_csvrako=[str(data_orain)]+ie_zerrenda_bueltatu # data eta 10 IErekin lerro bat sortu
    df_ie = pd.DataFrame([lerroa_csvrako,lerroa_csvrako],index=None, columns=None, dtype=None, copy=False) # lerroarekin df bat sortu
    df_ie = df_ie[:1]
    df_ie.to_csv('data/ie_denak.csv', header=None, index=False, mode='a') # lerroa gehitu csv-ra




def wp_n1 (nor):
    ##Ea nor pertsona Wikipedian dagoen (begiratu hizkuntza hauetan:'en', 'ca', 'es', 'fr'
    ## Sortu string bat estekekin pipe karaktereekin banatuta
    eleak = ['en', 'ca', 'es', 'fr']  
    l1 =""
    for ele1 in eleak:
        site = pywikibot.Site(ele1, 'wikipedia')
        page = pywikibot.Page(site, nor)
        if page.exists() :
            l1= l1 + " \n|" + str(page)
        else:
            l1= l1 + " \n|" + "   "
    return l1


def wikipedian_bilatu_eu_en_es (nor):
    langs =["eu","en","es", "ca","fr"]
    lang1 =langs[0]
    lang2 =langs[1]
    lang3 =langs[2]
    lang4 =langs[3]
    lang5 =langs[4]
    site = pywikibot.Site(lang1, "wikipedia")
    page = pywikibot.Page(site, nor)
    errorea = False
    try:
        item = pywikibot.ItemPage.fromPage(page)
    except:
        site = pywikibot.Site(lang2, "wikipedia")
        try:
            page = pywikibot.Page(site, nor)
            item = pywikibot.ItemPage.fromPage(page)
        except:
            site = pywikibot.Site(lang3, "wikipedia")
            try:
                page = pywikibot.Page(site, nor)
                item = pywikibot.ItemPage.fromPage(page)
            except:
                site = pywikibot.Site(lang4, "wikipedia")
                try:
                    page = pywikibot.Page(site, nor)
                    item = pywikibot.ItemPage.fromPage(page)
                except:
                    site = pywikibot.Site(lang5, "wikipedia")
                    try:
                        page = pywikibot.Page(site, nor)
                        item = pywikibot.ItemPage.fromPage(page)
                    except:
                        errorea = True
                        item = "kk"
                        page = "kk"

    return page, item, errorea


def taulak_ieekin(ie_asteko_zer):
    print(ie_asteko_zer)
    taula_hasiera = """{| style="margin: 0.5em 0.5em 0.5em 1em; padding: 0.5em; background: #f9f9f9; border: 1px #aaa solid; border-collapse: collapse; font-size: 95%;" cellspacing="0" cellpadding="4" {{taulapolita}}
        | bgcolor="#EFEFEF" |'''Izena'''
        | bgcolor="#EFEFEF" |'''Wikidata'''
        | bgcolor="#EFEFEF" |'''en wiki'''
        | bgcolor="#EFEFEF" |'''ca wiki'''
        | bgcolor="#EFEFEF" |'''es wiki'''
        | bgcolor="#EFEFEF" |'''fr wiki'''
        | bgcolor="#EFEFEF" |'''ZIRRIBORROA'''
        |-"""
    taula_amaiera = "\n|}"
    taula = taula_hasiera

    artikulugaiak = ""
    
    for nor in ie_asteko_zer :
            lerroa = ""
            print (nor)
            page, item, errorea = wikipedian_bilatu_eu_en_es (nor)
            if errorea == False :
                # ez da aurkitu wikipedian 
                item.get()
                print('\t',item)
                print('\t',page)
                wp_n1(nor)
                taula = taula + "\n|" + "[[" + nor +"]]"
                taula = taula + "\n|" + str(item) 
                taula = taula + wp_n1(nor)
                zirriborroa = "[[Wikiproiektu:ieproba/"+'_'.join(nor.split()) +"|Zirriborroa]]"
                artikulugaiak += sortu_wp_zirriborroa(nor) ##### SORTU ZIRRIBORROA
                taula = taula + "\n| " +zirriborroa
                taula = taula + " \n|-"

            else:
                print("\t Ez dago")
                taula = taula + "\n|" + "[[" + nor +"]]"
                taula = taula + "\n|" + "     "  #+ str(item) 
                taula = taula + "\n|   \n|   \n|   \n|   " #wiki esteka hutsak
                taula = taula + "\n|   "  #zirriborrorik ez"
                taula = taula + " \n|-"

    taula = taula + taula_amaiera
    taula = taula.replace("[[wikipedia:", "[[:")
    taula = taula.replace("[[wikidata:", "[[d:")
    print (taula, "\n\n\n")
    return taula



def taulak_ieekin_desplegable(ie_asteko_zer):
    taula_hasiera = """| bgcolor="#EFEFEF" |'''Izena'''
        | bgcolor="#EFEFEF" |'''Wikidata'''
        | bgcolor="#EFEFEF" |'''en wiki'''
        | bgcolor="#EFEFEF" |'''ca wiki'''
        | bgcolor="#EFEFEF" |'''es wiki'''
        | bgcolor="#EFEFEF" |'''fr wiki'''
        | bgcolor="#EFEFEF" |'''ZIRRIBORROA'''
        |-"""
    taula_amaiera = "\n|}"
    taula = taula_hasiera

    artikulugaiak = ""
    
    for nor in ie_asteko_zer :
            lerroa = ""
            print (nor)
            page, item, errorea = wikipedian_bilatu_eu_en_es (nor)
            if errorea == False :
                # ez da aurkitu wikipedian 
                item.get()
                print('\t',item)
                print('\t',page)
                wp_n1(nor)
                taula = taula + "\n|" + "[[" + nor +"]]"
                taula = taula + "\n|" + str(item) 
                taula = taula + wp_n1(nor)
                zirriborroa = "[[Lankide:" +'_'.join(nor.split()) +"|Zirriborroa]]"
                artikulugaiak += sortu_wp_zirriborroa(nor) ##### SORTU ZIRRIBORROA
                taula = taula + "\n| " +zirriborroa
                taula = taula + " \n|-"
            else:
                print("\t Ez dago")
                taula = taula + "\n|" + "[[" + nor +"]]"
                taula = taula + "\n|" + "     "  #+ str(item) 
                taula = taula + "\n|   \n|   \n|   \n|   " #wiki esteka hutsak
                taula = taula + "\n|   "  #zirriborrorik ez"
                taula = taula + " \n|-"

    taula = taula + taula_amaiera
    taula = taula.replace("[[wikipedia:", "[[:")
    taula = taula.replace("[[wikidata:", "[[d:")
    print (taula, "\n\n\n")
    return taula


def taulak_ieekin_desplegable_2(ie_asteko_zer):
    print(ie_asteko_zer)
    taula_hasiera = '|\n{| class="wikitable mw-collapsible mw-collapsed"\n|- style="vertical-align: top;"\n|+ class="nowrap" style="white-space: nowrap;" |'+ ie_asteko_zer[0]+'ko astea\n'
    taula=taula_hasiera+'! Izena \n! Wikidata \n! en wiki \n! ca wiki \n! es wiki \n! fr wiki \n! ZIRRIBORROA\n|-'

    artikulugaiak = ""
    
    for nor in ie_asteko_zer[1:11]:
            lerroa = ""
            print (nor)
            page, item, errorea = wikipedian_bilatu_eu_en_es (nor)
            if errorea == False :
                # ez da aurkitu wikipedian 
                item.get()
                print('\t',item)
                print('\t',page)
                wp_n1(nor)
                taula = taula + "\n|" + "[[" + nor +"]]"
                taula = taula + "\n|" + str(item) 
                taula = taula + wp_n1(nor)
                zirriborroa = "[[Wikiproiektu:ieproba/"+'_'.join(nor.split()) +"|Zirriborroa]]"
                artikulugaiak += sortu_wp_zirriborroa(nor) ##### SORTU ZIRRIBORROA
                taula = taula + "\n| " +zirriborroa
                taula = taula + " \n|-"

            else:
                print("\t Ez dago")
                taula = taula + "\n|" + "[[" + nor +"]]"
                taula = taula + "\n|" + "     "  #+ str(item) 
                taula = taula + "\n|   \n|   \n|   \n|   " #wiki esteka hutsak
                taula = taula + "\n|   "  #zirriborrorik ez"
                taula = taula + " \n|-"

    taula = taula + "\n|}\n|-\n" # amaiera
    taula = taula.replace("[[wikipedia:", "[[:")
    taula = taula.replace("[[wikidata:", "[[d:")
    print (taula, "\n\n\n")
    return taula




def scattertext():
    corpusa="data/termino_corpusa.tsv"
    df=pd.read_csv(corpusa, sep='\t', parse_dates=[1]) # datak datetimera pasatzeko 1 zutabea
    df=df[-3000:] #azkeneko 3.000 elementuak aukeratu(1.000 ±= aste bat)
    ### 7 egunetatik gaur arte ###
    t1=datetime.datetime.today() - datetime.timedelta(days=7) # egun atzera
    t=str(t1).split()[0].split('-')

    ### eguna automatiko edo manual ###
    urtea_=int(t[0]) #2020
    hilabetea_=int(t[1]) #3 # aurretik zeroa jarri gabe
    eguna_=int(t[2]) #1 # aurretik zeroa jarri gabe
    data_batera=str(urtea_)+'-'+str(hilabetea_)+'-'+str(eguna_)

    ## Data ordez indizea erabiliko dugu tresholda aukeratzeko, artikulu batzuen data gaizki dagoelako
    indizetik_gora=0
    for index, row in df.iterrows():
        if row[1].date()==t1.date():
            indizetik_gora=index
            break

    ## indizearen arabera prestatu lehen-orain (treshold)
    df['data2']=(df.index >= indizetik_gora).astype(int) # oraingoak=1; lehengoak=0
    df['data2'].replace([0,1],["lehengoak","oraingoak"],inplace=True)
    df['data']=[str(i).partition(' ')[0] for i in df.data] # data bakarrik, ordua kenduta
        
    # Turn it into a Scattertext Corpus 
    corpus = st.CorpusFromPandas(df,
                                category_col='data2',
                                text_col='per',
                                nlp=spacy.load('en_core_web_sm')).build()

    #Here are the NE that are most associated with ORAINGOAK:
    term_freq_df = corpus.get_term_freq_df()
    term_freq_df['New Score'] = corpus.get_scaled_f_scores('oraingoak')

    #And LEHENGOAK:
    term_freq_df['Old Score'] = corpus.get_scaled_f_scores('lehengoak')

    #Visualizing term associations
    html = st.produce_scattertext_explorer(corpus,
                                            category='oraingoak',
                                            category_name='Albiste berriak, '+data_batera+'-tik aurrera',
                                            not_category_name='Albiste zaharrak, '+data_batera+' baino lehen',
                                            width_in_pixels=1000,
                                            metadata=df[['data','egunkari','albiste_url']])
    # SAVE MODEL #    
    open("data/nortzuetaz.html", 'wb').write(html.encode('utf-8'))
    


##### MAIN LOOP #####

####  asteko IE zerrenda eguneratu, 'ie_denak.csv' fitxategira lerro bat gehituz. Astean behin deitu, astelehen goizean goiz.  ####
asteko_entitate_zerrenda_eguneratua() # deskonektatu daiteke           

import itertools            
import mwclient 
site = mwclient.Site('eu.wikipedia.org')
site.login(WIKIPEDIA_KONTUA,WIKIPEDIA_PASAHITZA)
page = site.Pages['Wikiproiektu:Euskarazko albisteetako Izen Entitateak'] # Orria kargatu
text=page.text() 

sarrera="\n==  Sarrera  ==\
        \nHemen topatuko duzun edukia, euskaraz argitaratzen duten hainbat hedabide digitaletatik erauzia dago. Euskarazko albiste bakoitzaren pertsonen izen entitateak automatikoki jaso dira, asteko pertsonaia aipatuenak zentzuk diren erakusteko aukera emanez. Astelehenero, pasa den asteko 10 entitate nabarmenenak automatikoki publikatuko dira. Horretarako, azkeneko asteko izen entitateak bestelako izen entitate guztiekin konparatzen dira, berrienak direnak aukeratuz. Azkeneko lau asteetako pertsonaiak etengabe eguneratzen joango dira eta zaharragoak direnak bukaerako menu zabalgarrian gordeta geratuko dira. Horrez gain, bistaraketa interaktibo bat sortu da, pertsonaia berri zein ohikoen arteko erlazioak erakusten dituena.\
        \n===  Metodologia  === \
        \nLan honen sorkuntzan erabilitako metodologiak hainbat pausu ditu: hedabide digitalen identifikazioa, hedabideen entzuketa bitartez albisteak jasotzea, albisteetatik izen entitateak erauztea eta azkeneko astean nabarmenak izan diren entitateen aukeraketa.\
        \n\n* '''Euskarazko hedabideen eskuzko identifikazioa''': Euskal Herrian euskaraz aritzen diren 8 komunikabide digital identifikatu dira.\
        \n\n* '''Hedabideen entzuketa''': MSM crawlerra erabili da hedabideen [[RSS|RSS]] loturak jasotzeko. Hedabide ezberdinetatik berri jarioa jaso, garbitu eta gorde da corpus batean. Jasotako albiste bakoitzetik egunkaria, data, hizkuntza, titularra, edukia eta lotura gorde dira.\
        \n\n* '''Izen entitateen erauzketa''': Lehenik eta behin, entzuketan euskarazko, gaztelerazko eta frantsesezko albisteak lortzen direnez, soilik euskarazko albisteak aukeratuko dira, beste guztiak alboratuz. Euskarazko albiste bakoitzaren edukia tokenizatu, lematizatu eta izen entitateen detektoreaz aztertu da. Hiru fase hauetatik eratorritako entitate izendunak jaso ostean, albiste bakoitzaren izen entitateak gorde dira.\
        \n\n* '''Izen entitateen aukeraketa''': Euskarazko albiste guztietatik, izen entitate berrienak eta nabarmenenak aukeratzeko [[Tf–idf|tf-idf]] banaketan oinarritu gara. Banaketa horri esker, azkeneko asteko izen entitateak beste guztiekin konparatzen dira, ohikoak diren izen entitateak alboratu eta azkeneko astean nabarmenak direnak jasotzeko asmoz.\
        \n===  Esteka interaktiboa  === \
        \n\nAstero adierazgarrienak diren Izen Entitateak aurkitzeaz gain, interesgarria iruditu zaigu bistaraketa berezi bat proposatzea izen entitateen maiztasuna eta berritasuna haintzat hartzen dituena. Scattertext teknikari esker, izen entitate berrienak nabarmendu ahalko ditugu zaharrenetatik. Horrez gain izen entitate aipatuenak eta gutxi aipatuenen arteko ezberdintasuna ikusi ahal izango da aldi berean. Adierazpen grafiko hau egunero berrituko da, iragandako 7 egunetako datuak eta azkeneko hilabeteko datuak konparatuta, izen entitateak sailkatu eta agerpenen iturria ikusteko aukera emanez.\
        \n\nBistaraketaren adierazpen grafikoan izen entitateen banaketa topatu dezakegu, denboraren eta agerpen kopuruaren arabera. Era honetan, bi dimentsioetako grafikoaren goiko erdian estitate berri eta ohikoenak topatu ditzakegu. Aldi berean, grafikoaren eskubi aldean estitate zahar ohikoenak topatuko dira. Halaber, entitate berri aipatuenak grafikako goiko eskubiko koadrantean aurkitu ahal izango ditugu, azkeneko astean aipatuenak izan diren entitateak izango dira hauek. Bestalde, ezkerreko goiko koadrantean beti aipatuak diren entitateak kokatuko dira, hau da, ohikoenak. Eskubiko beheko koadrantean, ostera, albiste zaharretan ohikoak izan diren eta albiste berrietan agerpen txikia daukatenak azaltzen dira.\
        \n\nBistaratze sistema honek izen entitateen bilatzaile bat dauka ere, entitatea grafikoan kokatzeaz gain, bere agerpen guztiak emango dizkigu. Agerpenetan egunkaria, eguna, albistera lotura eta albistean agertzen diren bestelako entitateak edukiko ditugu. Era honetan, entitate bakoitzaren informazio ahalik eta osatuena lortuko dugu, bere agerpenen testuingurua erakutsiko duen bistaratze bat eskainiz.\
        \n\n [http://ESTEKA MAPA INTERAKTIBORA ESTEKA]"

#csv-a irakurri
df_ie_guztiak=pd.read_csv('data/ie_denak.csv', header=None)
print(df_ie_guztiak)
# 4 aste berrienak aukeratu bistan jartzeko. 
lauaste=df_ie_guztiak[-4:].iloc[::-1] # reverse = .iloc[::-1]
asteak_bistan=""
for index,item in lauaste.iterrows():
    asteak_bistan+="\n==  "+item[0]+"ko asteko izen entitateak  =="
    asteak_bistan+="\n\n"+taulak_ieekin(item[1:11]) ##### TAULAK #####    
                    
### BESTELAKO ASTEAK DESPLEGABLEAN ###
if len(df_ie_guztiak)>4:
    besteaste=df_ie_guztiak[:-4].iloc[::-1] # reverse = .iloc[::-1]
    desplegablea='\n==  Bestelakoak  ==\n{| class="wikitable mw-collapsible mw-collapsed"\n|- style="white-space: nowrap;"\n! Aurreko asteetako izen entitateak\n|-\n'
    # ieak gehitu lista desplegablera #
    for index,item in besteaste.iterrows():                
        desplegablea+="\n\n"+taulak_ieekin_desplegable_2(item) ##### TAULA DESPLEGABLEAK #####
    desplegablea+="|}"
                
page.save(sarrera+"\n"+asteak_bistan+desplegablea) # Textua eguneratu
asteguna=1

scattertext() ## SORTU SCATTERTEXT BISUALIZAZIOA ##

time.sleep(5*60)
        



