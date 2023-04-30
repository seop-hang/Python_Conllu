from tokenisation import Tokenisation
from lemmatisation import Lemmatisation
from posparse import Posparse
from featsparse import Featsparse
from depparse import Depparse
from headparse import Headparse

if __name__=="__main__":
    xml_file="./test.xml"
    conllu_file="./test.conllu"
    processors={
        "language":"fr",
        "tokenize" : {
                "tool":"nltk",
                "model":"tokenizers/punkt/french.pickle"
        },
        "pos": {
                "tool":"stanza",
                "model":"partut"
        },
        "feats": {
            "tool": "stanza",
            "model": "partut"
        },
        "lemma": {
                "tool":"spacy",
                "model":"fr_core_news_sm",
        },
        "headparse": {
            "tool": "stanza",
            "model": "standard"
        },
        "depparse": {
                "tool":"spacy",
                "model":"fr_core_news_sm"
        }
    }
    Tokenisation.tokenize_xml(xml_file,"//p",conllu_file,processors)
    Lemmatisation.lemma_wrapper(conllu_file,processors)
    Posparse.pos_wrapper(conllu_file,processors)
    Featsparse.feats_wrapper(conllu_file,processors)
    Headparse.head_wrapper(conllu_file, processors)
    Depparse.deprel_wrapper(conllu_file,processors)
