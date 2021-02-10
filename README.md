# Basque Wikipedia enrich
Enriching Basque wikipedia entries with entities named in daily media.

For that purpose, 

Not only does this system creat written data for a low resourcerd language, but also includes entities related to the culture related with that language. Language is tightly related to culture, so generating culturally accurate data is as important as generating written data. 

As each process could be independent from each other, the decission of spliting the two processes was made due to avoid secuencial errors and protect the data retrieval process.

1- Data Retrieval module - erauzlea.py 

2- Data Mining module - bistaraketa.py




Language Dependant parts

This system was ensambled with the intention of being a helpful tool to induce written data generation on a low resourcered language scenario. Specyfically, the choosen language was Basque language but, the aim would be to extend  

Name Entity Recognizer
Lemmatizer - Due to the characteristics of Basque language, we choose to add a lemmatizer, because name entities are declinated 
