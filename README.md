# Basque Wikipedia enrich
Enriching Basque wikipedia entries with entities named in daily digital media.

For that purpose, 

Not only does this system creat written data for a low resourcerd language, but also includes entities related to the culture related with that language. Language is tightly related to culture, so generating culturally accurate data is as important as generating written data. 

As each process could be independent from each other, the decission of spliting the two processes was made due to avoid secuencial errors and protect the data retrieval process.

1- Data Retrieval module - erauzlea.py 

2- Data Mining module - bistaraketa.py




## Language Dependent parts

This system was ensambled with the intention of being a helpful tool to induce written data generation on a low resourcered language scenario. Specyfically, the choosen language was Basque language but, the aim would be to extend the same system to other minority languages. The system modification should take into account the following parts: 

*Media RSS feeds* - The RSS adresses have to be changed to the decided ones, preferably the ones related to media in a specific language.

*Name Entity Recognizer* - The NER system should be adecuated to each language, training specific models or using pretrained ones. This step is critical, because the quality of this task is going to determine the whole result.

*Lemmatizer* - Due to the characteristics of Basque language, we choose to add a lemmatizer to avoid declension on named entities. In Basque language even named entities have inflectional changes, rare chararasteristic that may not happen in other languages. So, the lemmataizer should be can be activated only in languages that declension occurs in named entities. 
