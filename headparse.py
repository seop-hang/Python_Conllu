import os
import conllu

class Headparse:
    @classmethod
    def head_wrapper(cls,conllu_filename,processors):
        # vérifier si le fichier d'entrée est un fichier CoNLLU
        if not os.path.isfile(conllu_filename) or os.path.splitext(conllu_filename)[1].lower() != '.conllu':
            print("Erreur : le fichier d'entrée doit être un fichier conllu.")
            return

        try:
            language=processors["language"].lower()
            tool=processors["headparse"]["tool"].lower()
            model=processors["headparse"]["model"]
        except Exception as err:
            print("Veuillez vérifier la structure de processors !")

        if tool=="stanza":
            try:
                import stanza
            except ImportError:
                print("Impossible d'importer le module nécessaire stanza !")
                return

            # Charger le modèle de langue
            try:
                model=model.lower()
                if model=="standard":
                    nlp = stanza.Pipeline(language, processors='tokenize,mwt,pos,lemma,depparse', use_gpu=False)
                else:
                    nlp = stanza.Pipeline(language, processors='tokenize,mwt,pos,lemma,depparse', use_gpu=False, package=model)
            except Exception as err:
                print("Impossible de charger le modèle de stanza que vous avez saisi !")
                return

            # Lecture du fichier
            with open(conllu_filename, "r", encoding="utf-8") as file:
                # Lire le contenu du fichier avec la bibliothèque conllu
                data = file.read()
                fields_parser = lambda field, x: field[x]
                sentences = conllu.parse(data,field_parsers={"id":fields_parser,"form":fields_parser,"lemma":fields_parser,
                            "upos":fields_parser,"xpos":fields_parser,"feats":fields_parser,"head":fields_parser,
                            "deprel": fields_parser,"deps":fields_parser,"misc":fields_parser})
            # Parcourir chaque token dans chaque phrase
            for sentence in sentences:
                # reconstruire la phrase et l'analyser
                text = " ".join([token["form"] for token in sentence])
                doc=nlp(text)
                for i,token in enumerate(sentence):
                    token["head"] = doc.sentences[0].words[i].head

            # Réécrire les données modifiées dans le fichier CoNLL-U
            with open(conllu_filename, "w", encoding="utf-8") as file:
                for sentence in sentences:
                    # Parcourir les tokens de chaque phrase et les écrire dans le fichier
                    for token in sentence:
                        line = "\t".join([str(token[field]) for field in token.keys()])
                        file.write(line + "\n")
                    file.write("\n")

        elif tool=="spacy":
            try:
                import spacy
            except ImportError:
                print("Impossible d'importer le module nécessaire spacy !")
                return
            # Charger le modèle de langue
            try:
                nlp = spacy.load(model)
            except Exception as err:
                print("Impossible de charger le modèle de spacy que vous avez saisi !")
                return

            # Lecture du fichier
            with open(conllu_filename, "r", encoding="utf-8") as file:
                # Lire le contenu du fichier avec la bibliothèque conllu
                data = file.read()
                fields_parser = lambda field, x: field[x]
                sentences = conllu.parse(data,field_parsers={"id":fields_parser,"form":fields_parser,"lemma":fields_parser,
                            "upos":fields_parser,"xpos":fields_parser,"feats":fields_parser,"head":fields_parser,
                            "deprel": fields_parser,"deps":fields_parser,"misc":fields_parser})
            # Parcourir chaque token dans chaque phrase
            for sentence in sentences:
                # reconstruire la phrase et l'analyser
                text = " ".join([token["form"] for token in sentence])
                doc = nlp(text)
                for i, token in enumerate(sentence):
                    token["head"] = str(doc[i].head.i + 1)  # ajouter 1 car le comptage commence à partir de 0 dans spaCy et de 1 dans CoNLL-U

            # Réécrire les données modifiées dans le fichier CoNLL-U
            with open(conllu_filename, "w", encoding="utf-8") as file:
                for sentence in sentences:
                    # Parcourir les tokens de chaque phrase et les écrire dans le fichier
                    for token in sentence:
                        line = "\t".join([str(token[field]) for field in token.keys()])
                        file.write(line + "\n")
                    file.write("\n")

        elif tool=="udpipe":
            try:
                import spacy_udpipe
            except ImportError:
                print("Impossible d'importer le module nécessaire UDPipe !")
                return
            # Charger le modèle de langue
            try:
                spacy_udpipe.download(model)
                nlp = spacy_udpipe.load(model)
            except Exception as err:
                print("Impossible de charger le modèle de UDPipe que vous avez saisi !")

            # Lecture du fichier
            with open(conllu_filename, "r", encoding="utf-8") as file:
                # Lire le contenu du fichier avec la bibliothèque conllu
                data = file.read()
                fields_parser = lambda field, x: field[x]
                sentences = conllu.parse(data,field_parsers={"id":fields_parser,"form":fields_parser,"lemma":fields_parser,
                            "upos":fields_parser,"xpos":fields_parser,"feats":fields_parser,"head":fields_parser,
                            "deprel": fields_parser,"deps":fields_parser,"misc":fields_parser})
            # Parcourir chaque token dans chaque phrase
            for sentence in sentences:
                # reconstruire la phrase et l'analyser
                text = " ".join([token["form"] for token in sentence])
                doc = nlp(text)
                for i, token in enumerate(sentence):
                    token["head"] = doc[i].head.i + 1

            # Réécrire les données modifiées dans le fichier CoNLL-U
            with open(conllu_filename, "w", encoding="utf-8") as file:
                for sentence in sentences:
                    # Parcourir les tokens de chaque phrase et les écrire dans le fichier
                    for token in sentence:
                        line = "\t".join([str(token[field]) for field in token.keys()])
                        file.write(line + "\n")
                    file.write("\n")

        else:
            print("Veuillez saisir un autre tool, on ne accepte que stanza, spacy, udpipe et nltk !")
            return