import os

class Tokenisation:
    @classmethod
    def tokenize_xml(cls,input_file,xpath_expression,output_file,processors):
        # vérifier si le fichier d'entrée est un fichier XML
        if not os.path.isfile(input_file) or os.path.splitext(input_file)[1].lower() != '.xml':
            print("Erreur : le fichier d'entrée doit être un fichier XML.")
            return

        # vérifier si le fichier de sortie est un fichier CoNLL_U
        if os.path.splitext(output_file)[1].lower() != '.conllu':
            print("Erreur : le fichier de sortie doit être un fichier CoNLL_U.")
            return

        # importer le module lxml pour traiter le fichier d'entrée
        try:
            from lxml import etree
        except ImportError:
            print("Impossible d'importer le module nécessaire lxml !")
            return

        # ouvrir le fichier XML et créer un objet ElementTree
        tree = etree.parse(input_file)
        # créer un objet XPath pour sélectionner les zones de texte à traiter
        xpath = etree.XPath(xpath_expression)
        # stocker les textes de chaque élément, et chaque élément est séparé par un espace
        text_total = ""
        for element in xpath(tree):
            text_total += element.text.strip() + " "

        try:
            language=processors["language"].lower()
            tool=processors["tokenize"]["tool"].lower()
            model=processors["tokenize"]["model"]
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
                    nlp = stanza.Pipeline(language, processors='tokenize', use_gpu=False)
                else:
                    nlp = stanza.Pipeline(language, processors='tokenize', use_gpu=False, package=model)
            except Exception as err:
                print("Impossible de charger le modèle de stanza que vous avez saisi !")
                return

            # Ouverture du fichier de sortie en mode écriture
            with open(output_file, 'w',encoding="utf-8") as file:
                #initialisation de offset et idToken
                offset = 0
                # Parcours de tous les éléments sélectionnés par l'expression XPath
                for element in xpath(tree):
                    # Obtention du texte de l'élément et suppression des espaces en début et fin de chaîne
                    text = element.text.strip()

                    # Si le texte est vide, passer à l'élément suivant
                    if not text:
                        continue

                    # Tokenisation du texte avec le modèle de langue Stanza
                    doc = nlp(text)

                    # Parcours de tous les tokens
                    for sent in doc.sentences:
                        for i, word in enumerate(sent.words):
                            index_seperation=text_total[offset:].find(word.text)+len(word.text)+offset
                            if offset<len(text_total):
                                if text_total[index_seperation]==" ":
                                    # Création d'une chaîne CoNNL-U pour le token avec les informations SpaceAfter et Offset
                                    connl_token = [
                                        str(word.id),  # ID
                                        word.text,  # FORM
                                        '_',  # LEMMA
                                        '_',  # UPOS
                                        '_',  # XPOS
                                        '_',  # FEATS
                                        '_',  # HEAD
                                        '_',  # DEPREL
                                        '_',  # DEPS
                                        'SpaceAfter=Yes|Offset=' + str(offset), # MISC
                                    ]
                                    offset= offset+len(word.text)+1
                                else:
                                    connl_token = [
                                        str(word.id),  # ID
                                        word.text,  # FORM
                                        '_',  # LEMMA
                                        '_',  # UPOS
                                        '_',  # XPOS
                                        '_',  # FEATS
                                        '_',  # HEAD
                                        '_',  # DEPREL
                                        '_',  # DEPS
                                        'SpaceAfter=No|Offset=' + str(offset), # MISC
                                    ]
                                    offset+=len(word.text)

                            # Écriture de la chaîne CoNNL-U dans le fichier de sortie
                            file.write('\t'.join(connl_token))
                            file.write('\n')
                        file.write('\n')

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

            # Ouverture du fichier de sortie en mode écriture
            with open(output_file, 'w',encoding="utf-8") as file:
                # initialisation de offset et idToken
                offset = 0
                # Parcours de tous les éléments sélectionnés par l'expression XPath
                for element in xpath(tree):
                    # Obtention du texte de l'élément et suppression des espaces en début et fin de chaîne
                    text = element.text.strip()

                    # Si le texte est vide, passer à l'élément suivant
                    if not text:
                        continue

                    # Tokenisation du texte avec le modèle de langue Stanza
                    doc = nlp(text)

                    for sent in doc.sents:
                        # Parcours de tous les tokens
                        for i, token in enumerate(sent):
                            index_seperation = text_total[offset:].find(token.text) + len(token.text) + offset
                            if offset < len(text_total):
                                if text_total[index_seperation] == " ":
                                    # Création d'une chaîne CoNNL-U pour le token avec les informations SpaceAfter et Offset
                                    connl_token = [
                                        str(i+1),  # ID
                                        token.text,  # FORM
                                        '_',  # LEMMA
                                        '_',  # UPOS
                                        '_',  # XPOS
                                        '_',  # FEATS
                                        '_',  # HEAD
                                        '_',  # DEPREL
                                        '_',  # DEPS
                                        'SpaceAfter=Yes|Offset=' + str(offset),  # MISC
                                    ]
                                    offset = offset + len(token.text) + 1
                                else:
                                    connl_token = [
                                        str(i+1),  # ID
                                        token.text,  # FORM
                                        '_',  # LEMMA
                                        '_',  # UPOS
                                        '_',  # XPOS
                                        '_',  # FEATS
                                        '_',  # HEAD
                                        '_',  # DEPREL
                                        '_',  # DEPS
                                        'SpaceAfter=No|Offset=' + str(offset),  # MISC
                                    ]
                                    offset += len(token.text)

                            # Écriture de la chaîne CoNNL-U dans le fichier de sortie
                            file.write(' '.join(connl_token))
                            file.write('\n')
                        file.write('\n')

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

            # Ouverture du fichier de sortie en mode écriture
            with open(output_file, 'w',encoding="utf-8") as file:
                # initialisation de offset et idToken
                offset = 0
                # Parcours de tous les éléments sélectionnés par l'expression XPath
                for element in xpath(tree):
                    # Obtention du texte de l'élément et suppression des espaces en début et fin de chaîne
                    text = element.text.strip()

                    # Si le texte est vide, passer à l'élément suivant
                    if not text:
                        continue

                    # Tokenisation du texte avec le modèle de langue Stanza
                    doc = nlp(text)

                    for sent in doc.sents:
                        # Parcours de tous les tokens
                        for i, token in enumerate(sent):
                            index_seperation = text_total[offset:].find(token.text) + len(token.text) + offset
                            if offset < len(text_total):
                                if text_total[index_seperation] == " ":
                                    # Création d'une chaîne CoNNL-U pour le token avec les informations SpaceAfter et Offset
                                    connl_token = [
                                        str(i+1),  # ID
                                        token.text,  # FORM
                                        '_',  # LEMMA
                                        '_',  # UPOS
                                        '_',  # XPOS
                                        '_',  # FEATS
                                        '_',  # HEAD
                                        '_',  # DEPREL
                                        '_',  # DEPS
                                        'SpaceAfter=Yes|Offset=' + str(offset),  # MISC
                                    ]
                                    offset = offset + len(token.text) + 1
                                else:
                                    connl_token = [
                                        str(i+1),  # ID
                                        token.text,  # FORM
                                        '_',  # LEMMA
                                        '_',  # UPOS
                                        '_',  # XPOS
                                        '_',  # FEATS
                                        '_',  # HEAD
                                        '_',  # DEPREL
                                        '_',  # DEPS
                                        'SpaceAfter=No|Offset=' + str(offset),  # MISC
                                    ]
                                    offset += len(token.text)

                            # Écriture de la chaîne CoNNL-U dans le fichier de sortie
                            file.write('\t'.join(connl_token))
                            file.write('\n')
                        file.write('\n')

        elif tool=="nltk":
            try:
                import nltk
                from nltk.tokenize import word_tokenize
            except ImportError:
                print("Impossible d'importer le module nécessaire nltk !")
                return
            # Charger le modèle de langue
            try:
                nlp = nltk.data.load(model)
            except Exception as err:
                print("Impossible de charger le modèle de nltk que vous avez saisi !")

            # Ouverture du fichier de sortie en mode écriture
            with open(output_file, 'w',encoding="utf-8") as file:
                # initialisation de offset et idToken
                offset = 0
                # Parcours de tous les éléments sélectionnés par l'expression XPath
                for element in xpath(tree):
                    # Obtention du texte de l'élément et suppression des espaces en début et fin de chaîne
                    text = element.text.strip()

                    # Si le texte est vide, passer à l'élément suivant
                    if not text:
                        continue

                    # Tokenisation du texte avec le modèle de langue nltk
                    doc = nlp.tokenize(text)

                    for sent in doc:
                        # Parcours de tous les tokens
                        for i, token in enumerate(word_tokenize(sent)):
                            index_seperation = text_total[offset:].find(token) + len(token) + offset
                            if offset < len(text_total):
                                if text_total[index_seperation] == " ":
                                    # Création d'une chaîne CoNLL-U pour le token avec les informations SpaceAfter et Offset
                                    connl_token = [
                                        str(i+1),  # ID
                                        token,  # FORM
                                        '_',  # LEMMA
                                        '_',  # UPOS
                                        '_',  # XPOS
                                        '_',  # FEATS
                                        '_',  # HEAD
                                        '_',  # DEPREL
                                        '_',  # DEPS
                                        'SpaceAfter=Yes|Offset=' + str(offset),  # MISC
                                    ]
                                    offset = offset + len(token) + 1
                                else:
                                    connl_token = [
                                        str(i+1),  # ID
                                        token,  # FORM
                                        '_',  # LEMMA
                                        '_',  # UPOS
                                        '_',  # XPOS
                                        '_',  # FEATS
                                        '_',  # HEAD
                                        '_',  # DEPREL
                                        '_',  # DEPS
                                        'SpaceAfter=No|Offset=' + str(offset),  # MISC
                                    ]
                                    offset += len(token)

                            # Écriture de la chaîne CoNNL-U dans le fichier de sortie
                            file.write('\t'.join(connl_token))
                            file.write('\n')
                        file.write('\n')

        else:
            print("Veuillez saisir un autre tool, on ne accepte que stanza, spacy, udpipe et nltk !")
            return
