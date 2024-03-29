## Semi-automatic generation of relevant articles for the Basque Wikipedia


Enriching Basque wikipedia entries with entities named in daily digital media.

Our system consists of two components:

1. erauzlea.py: data collection (news from online media) and processing (NER, lemmatization).
2. bistaraketa.py: data visualization and publishing the results as Wikipedia template articles.

Each process may work indepedently from the other, this avoids cascading errors and helps to protect the data retrieval process.

### 1. Data Mining module - erauzlea.py

+ Downloading News from online media.
+ Extraction of all the Named Entities from news. 

### 2. Data Visualization module - bistaraketa.py

+ Comparison of the last NE with the previous ones via TF-IDF to choose the most prominent.
+ Weekly publication of the results on Wikipedia, adding media links to the entities.

### Language-dependent Components

Our system has originally been developed for Basque, although it can be adapted by modifying the Data Mining module (erauzlea.py). The following steps are required :  

+ **Media RSS feeds**: Add the RSS addresses of interest.

+ **Name Entity tagger** : A NER model trained with the [Flair system](https://github.com/flairNLP/flair) is required to perform the entity extraction.
+ **Lemmatizer**: We employ a neural-based contextual lemmatizer trained with the [Flair system](https://github.com/flairNLP/flair). This is required if your language of interest includes declension in the named entities. For languages without inflected named entities, this step can be avoided.

### Instalation

+ See [dependencies.md](https://github.com/joseba-fdl/Basque_wikipedia_enrich/edit/main/dependencies.md) for a general description.
+ Python dependencies in the [requirements.txt file](https://github.com/joseba-fdl/Basque_wikipedia_enrich/edit/main/requirements.txt)

### Getting started

+ Run the scripts with the --help parameter for more details about the arguments expected by each of the programs. Without arguments, a specific directory structure is required.
+ **NOTE**: Before running the bistaraketa.py program, the erauzlea.py program should run for a couple of weeks at least. This is to make sure that there is sufficient data for the visualization to work.

python3 erauzlea.py

python3 bistaraketa.py

## Contact

Joseba Fernandez de Landa (joseba.fernandezdelanda@ehu.eus)

Rodrigo Agerri (rodrigo.agerri@ehu.eus)

HiTZ Center - Ixa, University of the Basque Country UPV/EHU
