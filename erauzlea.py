import os
import sys
import re
from bs4 import BeautifulSoup
from langdetect import detect
import pandas as pd
import datetime
import collections
import xml.etree.ElementTree as ET

import argparse
parser = argparse.ArgumentParser(description="Indicate locations")
parser.add_argument('-ner_tagger','--nermodeldir',  default="./models/best-model.pt", type=str,help='specify NER tagger model directory and file')
parser.add_argument('-lemmatizer','--lemmamodeldir',default="./models/eu-lemma-sigmorphon2019.pt", type=str,help='specify lemmatizer model directory and file')
parser.add_argument('-msm',       '--msmdir',       default="../MSM/", type=str,help='specify MSM directory')
parser.add_argument('-rss',       '--rssurldir',    default="./rss_urls.txt", type=str,help='specify RSS url list directory and file')
parsed_arguments = parser.parse_args()


#pytotch version: 1.3.1 
import flair
from syntok.tokenizer import Tokenizer
import syntok.segmenter as segmenter
# 3 fitxategi hauek MODELS karpetatik hartu:
from models.get_ses_affixes import _apply_lemma_rule
nerTagger = flair.models.SequenceTagger.load(parsed_arguments.nermodeldir)
lemmatizer = flair.models.SequenceTagger.load(parsed_arguments.lemmamodeldir)


def garbiketa(text1): # CLEANING
    textart=re.sub("\t"," ",text1)
    textart=re.sub("\n",". ",textart)
    textart=re.sub("\.{2,}",".",textart) # 2 puntu edo gehio > espazio bakarra
    textart=re.sub("\s{2,}"," ",textart) # 2 espazio edo gehio > espazio bakarra    
    return textart

def egunkari_mota(url): # PUBLISHER
    eg_mota=url
    if re.search('naiz.eus', url): eg_mota="naiz"
    elif re.search('mediabask.eus', url): eg_mota="naiz"
    elif re.search('kazeta.eus', url): eg_mota="naiz"
    elif re.search('zuzeu.eus', url): eg_mota="zuzeu"
    elif re.search('berria.eus', url): eg_mota="berria"
    elif re.search('feedproxy.google.com/~r/sustatu', url): eg_mota="sustatu"
    elif re.search('argia.eus', url): eg_mota="argia"
    elif re.search('eitb.eus', url): eg_mota="eitb"
    elif re.search('noticiasdealava.eus', url): eg_mota="gnoticias"    
    elif re.search('noticiasdegipuzkoa.eus', url): eg_mota="gnoticias" 
    elif re.search('deia.eus', url): eg_mota="gnoticias"               
    elif re.search('noticiasdenavarra.com', url): eg_mota="gnoticias"  
    elif re.search('elcorreo.com', url): eg_mota="correo"          
    return eg_mota

def NER_eus(input_testua):
    sents_tokens = segmenter.analyze(input_testua)
    tok_sents = []
    for paragraph in sents_tokens:
        for sent in paragraph:
            tokens = []
            for token in sent:
                tokens.append(token.value)
            tok_sents.append(flair.data.Sentence(" ".join(tokens)))

    # predict NER and LEMMA with loaded models    
    nerTagger.predict(tok_sents)
    lemmatizer.predict(tok_sents)

    per=[]
    org=[]
    loc=[]
    for processed_sent in tok_sents:
        entitatea=""
        for token in processed_sent:
            ner_type=token.get_tag('ner').value
            if ner_type != 'O':
                ner_mota=ner_type.split('-')[1] # IE mota
                decoded_lemma = _apply_lemma_rule(token.text, token.get_tag('lemma').value) # IE lema
                #print(f"{token.text}\t{decoded_lemma}\t{ner_type}")
                ner_type_posizioa,ner_type_mota=ner_type.split('-')
                # IE konposatuak (B+(I)+E)
                if ner_type_posizioa=='B': 
                    entitatea+=decoded_lemma+" "
                elif ner_type_posizioa=='I':
                    entitatea+=decoded_lemma+" "
                elif ner_type_posizioa=='E':
                    entitatea+=decoded_lemma
                    if ner_mota=='PER':per.append(entitatea)
                    elif ner_mota=='ORG':org.append(entitatea)
                    elif ner_mota=='LOC':loc.append(entitatea)
                    entitatea=""
                # IE bakunak
                elif ner_type_posizioa=='S':
                    if ner_mota=='PER':per.append(decoded_lemma)
                    elif ner_mota=='ORG':org.append(decoded_lemma)
                    elif ner_mota=='LOC':loc.append(decoded_lemma)
                    
    return per, org, loc



### MAIN LOOP ###
while True:
    ##### NOTIZIAK ERAUZI ETA GORDE -> komunikabide_corpusa.tsv #####
    t=datetime.datetime.now().time()
    if (t.hour==10 or t.hour==14 or t.hour==18 or t.hour==22)and(t.minute==0):
        print(">>> ERAUZKETA >>> "+str(t.hour)+":"+str(t.minute))

        #### ERAUZLEA ####
        bidea_erauzle =parsed_arguments.msmdir # "../MSM/" # MSM Crawler folder
        fitxategia1="zaborra/out_msm.xml"

        ## Choosen media RSS feeds ##
        with open(parsed_arguments.rssurldir) as rss_urls_fitx:
            RSSURLS = [line.rstrip('\n') for line in rss_urls_fitx]

        ## MSM CALL ##
        os.system("java -jar "+bidea_erauzle+"target/MSM-1.3.8.jar feed -c "+bidea_erauzle+"config.cfg -u '"+','.join(RSSURLS)+"' -s stout > "+fitxategia1)
        print(">>> ERAUZKETA >>> "+str(t.hour)+":"+str(t.minute))

        # Xml atxigarri bat sortzeko, bestela ezin da irakurri
        with open(fitxategia1,"r+") as fp:
            lines = fp.readlines() # read old content
            fp.seek(0) # go back to the beginning of the file
            fp.write("<docs>\n") # write new content at the TOP
            for line in lines: # write old content after new
                line=re.sub("<{2,}"," ",line)
                line=re.sub(">{2,}"," ",line)
                fp.write(line)
            fp.write("</docs>") # write new content at the END

        #### GARBIKETA ETA BILTOKIRATZEA ####
        corpusa="data/komunikabide_corpusa.tsv"   #### CORPUSA ####
        corpusa_exists = os.path.isfile(corpusa)
        if not corpusa_exists:
            with open(corpusa,'w') as csvfile: csvfile.writelines("egunkari\tdata\tlang\ttitularra\ttestua\talbiste_url")
        
        with open(fitxategia1) as fp:    
            soup = BeautifulSoup(fp, 'xml')    
            datu_guztiak=[]
            df_zaharra=pd.read_csv(corpusa, sep='\t')
            url_daudenak=df_zaharra.iloc[:,5].values
    
            for item in soup.find_all('doc'):
                ### artikulu bakoitza .tsv formatuan gorde: [egunkari/data/lang/titularra/testua/albiste_url] ###
                ## url ## konprobatu ea badagoen datubasean ##
                errepikatu_gabe=True
                albiste_url=item.find_all('url')[0].text
                for url_zahar in url_daudenak:
                    if albiste_url==url_zahar:
                        errepikatu_gabe=False
                        break
            
                if errepikatu_gabe:
                    ## testua ##
                    testua=garbiketa(item.find_all('text')[0].text)
                    ## egunkari mota ##
                    egunkari=egunkari_mota(albiste_url)
                    ## titularra ##
                    titularra=item.find_all('title')[0].text
                    ## data ##
                    data=item.find_all('date')[0].text

                    # Testurik ez badago albistea deskartatu #
                    if testua:               
                        ## hizkunzta ##
                        # Naizen > artikuluen hizkuntza atera | Besteak euskaraz daude denak
                        if egunkari=='naiz':
                            if detect(testua) == "es": lang="es"
                            elif detect(testua) == "fr": lang="fr"
                            else: lang="eu"
                        else: lang=item.find_all('lang')[0].text
                        ## GORDE ##
                        datu_guztiak.append([egunkari,data,lang,titularra,testua,albiste_url])

            print("Berri:"+str(len(datu_guztiak))+"  Zeudenak:"+str(len(url_daudenak)))
            ### Data Framea sortu ###
            df = pd.DataFrame(datu_guztiak)
            ### GORDE HEMEN >> komunikabide_corpusa.tsv ###
            df.to_csv(corpusa, mode='a', sep='\t', header=False, index=False)  



        ##### komunikabide_corpusa.tsv tik-> IZEN ENTITATEAK ERAUZI ETA GORDE -> termino_corpusa.tsv #####

        #### CORPUSA IRAKURRI ####
        corpusa="data/komunikabide_corpusa.tsv" #### CORPUSA ####
        #irakurtzeko [egunkari/data/lang/titularra/testua/albiste_url]
        df_1=pd.read_csv(corpusa, sep='\t')

        ## termino corpusa ##
        corpusa_ter="data/termino_corpusa.tsv" #### termino CORPUSA ####
        #irakurtzeko [egunkari/data/lang/albiste_url/per/org/loc]
        corpusa_ter_exists = os.path.isfile(corpusa_ter) # ez balego, sortu
        if not corpusa_ter_exists:
            with open(corpusa_ter,'w') as csvfile: csvfile.writelines("egunkari\tdata\tlang\talbiste_url\tper\torg\tloc")
            
        
        dft=pd.read_csv(corpusa_ter, sep='\t')
        url_aztertuak=list(dft['albiste_url'])

        ## Corpusetik atera interesatzen zaigun testua (euskaraz,...)##
        # euskarazko artikuluen testua ##
        euskarazko_artikuluak=df_1.loc[df_1['lang'] == 'eu']
        for item in euskarazko_artikuluak.values:
            #[egunkari/data/lang/titularra/testua/albiste_url]
            albiste_url=item[5]
            if albiste_url not in url_aztertuak:
                egunkari=item[0]
                data=item[1]
                lang=item[2]    
                terminoak=NER_eus(item[4])
                ## GORDE ## [egunkari/data/lang/albiste_url/per/org/loc]
                df_berri = pd.DataFrame([[egunkari,data,lang,albiste_url,per,org,loc]]]) # lerroka gorde
                df_berri.to_csv(corpusa_ter, mode='a', sep='\t', header=False, index=False)
                print(albiste_url)

        print("####  ENTZUKETA EGINA! ITXOITEN  ####")




        


        
