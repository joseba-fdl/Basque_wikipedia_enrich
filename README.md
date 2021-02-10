# Basque Wikipedia enrich
Enriching Basque wikipedia entries with entities named in daily digital media.

This repository contains a system on two stages. On the one hand the Data Mining module will handle the data collection from digital media and processing stage. On the other hand, the Data Visualization module, in order to visualize and publish the results in a useful way for Wikipedia editors. As each process could be independent from each other, the decission of spliting the two processes was made due to avoid secuencial errors and protect the data retrieval process.

### 1- Data Mining module - erauzlea.py 
-Downloading News from online media.
-Extraction of all the Named Entities from news.

### 2- Data Visualization module - bistaraketa.py 
-Comparison of the last NE with the previous ones via TF-IDF to choose the most prominent.
-Weekly publication of the results on Wikipedia, adding media links to the entities.


## Language Dependent parts

This system was ensambled with the intention of being a helpful tool to induce written data generation on a low resourcered language scenario. Specyfically, the choosen language was Basque language but, the aim would be to extend the same system to other minority languages. The system modification should take into account the following parts, both in the Data Mining module (erauzlea.py): 

*Media RSS feeds* - The RSS adresses have to be changed to the decided ones, preferably the ones related to media in a specific language.

*Name Entity Recognizer* - The NER system should be adecuated to each language, training specific models or using pretrained ones. This step is critical, because the quality of this task is going to determine the whole result.

*Lemmatizer* - Due to the characteristics of Basque language, we choose to add a lemmatizer to avoid declension on named entities. In Basque language even named entities have inflectional changes, rare chararasteristic that may not happen in other languages. So, the lemmataizer should be can be activated only in languages that declension occurs in named entities. 
