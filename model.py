import json, os
from typing import List, Dict, Optional, Set

class Etat:
    """Classe représentant un état dans un automate."""
    
    def __init__(self, idEtat: str, labelEtat: str, typeEtat: str = "normal"):
        """
        Constructeur de la classe Etat.
        
        Args:
            idEtat (str): Identifiant unique de l'état.
            labelEtat (str): Nom ou étiquette de l'état.
            typeEtat (str): Type de l'état ("initial", "final", ou "normal").
        """
        self.idEtat = idEtat
        self.labelEtat = labelEtat
        self.typeEtat = typeEtat.lower()  # Uniformisation en minuscules

    # Getters
    def get_idEtat(self) -> str:
        return self.idEtat

    def get_labelEtat(self) -> str:
        return self.labelEtat

    def get_typeEtat(self) -> str:
        return self.typeEtat

    # Setters
    def set_labelEtat(self, new_label: str) -> None:
        self.labelEtat = new_label

    def set_typeEtat(self, new_type: str) -> None:
        if new_type.lower() in {"initial", "final", "normal"}:
            self.typeEtat = new_type.lower()
        else:
            raise ValueError("Type d'état invalide. Choisir parmi 'initial', 'final', ou 'normal'.")

    def __repr__(self) -> str:
        return f"Etat(id={self.idEtat}, label={self.labelEtat}, type={self.typeEtat})"

class Alphabet:
    """Classe représentant un symbole dans l'alphabet d'un automate."""
    
    def __init__(self, idAlphabet: str, valAlphabet: str):
        """
        Constructeur de la classe Alphabet.
        
        Args:
            idAlphabet (str): Identifiant unique du symbole.
            valAlphabet (str): Valeur du symbole (ex: 'a', '0').
        """
        self.idAlphabet = idAlphabet
        self.valAlphabet = valAlphabet

    # Getters
    def get_idAlphabet(self) -> str:
        return self.idAlphabet

    def get_valAlphabet(self) -> str:
        return self.valAlphabet

    # Setters
    def set_valAlphabet(self, new_val: str) -> None:
        self.valAlphabet = new_val

    def __repr__(self) -> str:
        return f"Alphabet(id={self.idAlphabet}, val={self.valAlphabet})"

class Transition:
    """Classe représentant une transition entre deux états dans un automate."""
    
    def __init__(self, idTransition: str, etatSource: Etat, etatDestination: Etat, alphabet: Alphabet):
        """
        Constructeur de la classe Transition.
        
        Args:
            idTransition (str): Identifiant unique de la transition.
            etatSource (Etat): Etat de départ.
            etatDestination (Etat): Etat d'arrivée.
            alphabet (Alphabet): Symbole déclenchant la transition.
        """
        self.idTransition = idTransition
        self.etatSource = etatSource
        self.etatDestination = etatDestination
        self.alphabet = alphabet

    # Getters
    def get_idTransition(self) -> str:
        return self.idTransition

    def get_etatSource(self) -> Etat:
        return self.etatSource

    def get_etatDestination(self) -> Etat:
        return self.etatDestination

    def get_alphabet(self) -> Alphabet:
        return self.alphabet

    # Setters
    def set_etatSource(self, new_source: Etat) -> None:
        self.etatSource = new_source

    def set_etatDestination(self, new_dest: Etat) -> None:
        self.etatDestination = new_dest

    def set_alphabet(self, new_alphabet: Alphabet) -> None:
        self.alphabet = new_alphabet

    def __repr__(self) -> str:
        return f"Transition(id={self.idTransition}, source={self.etatSource.idEtat}, dest={self.etatDestination.idEtat}, symbole={self.alphabet.valAlphabet})"

class Automate:
    """Classe principale représentant un automate fini (AFD ou AFN)."""
    
    def __init__(self, nom: str):
        """
        Constructeur de la classe Automate.
        
        Args:
            nom (str): Nom unique de l'automate.
        """
        self.nom = nom
        self.listAlphabets: List[Alphabet] = []
        self.listEtats: List[Etat] = []
        self.listInitiaux: List[Etat] = []
        self.listFinaux: List[Etat] = []
        self.listTransition: List[Transition] = []

    # --- Méthodes pour gérer les états ---
    def ajouter_etat(self, etat: Etat) -> None:
        """Ajoute un état à l'automate."""
        if etat.idEtat in {e.idEtat for e in self.listEtats}:
            raise ValueError(f"Etat avec l'id {etat.idEtat} existe déjà.")
        self.listEtats.append(etat)
        if etat.typeEtat == "initial":
            self.listInitiaux.append(etat)
        elif etat.typeEtat == "final":
            self.listFinaux.append(etat)

    def supprimer_etat(self, idEtat: str) -> None:
        """Supprime un état et ses transitions associées."""
        etat = next((e for e in self.listEtats if e.idEtat == idEtat), None)
        if not etat:
            raise ValueError(f"Etat avec l'id {idEtat} introuvable.")
        
        # Supprimer les transitions liées à cet état
        self.listTransition = [t for t in self.listTransition 
                             if t.etatSource.idEtat != idEtat and t.etatDestination.idEtat != idEtat]
        
        # Supprimer des listes d'états initiaux/finaux si nécessaire
        if etat in self.listInitiaux:
            self.listInitiaux.remove(etat)
        if etat in self.listFinaux:
            self.listFinaux.remove(etat)
        
        self.listEtats.remove(etat)

    # --- Méthodes pour gérer l'alphabet ---
    def ajouter_alphabet(self, alphabet: Alphabet) -> None:
        """Ajoute un symbole à l'alphabet de l'automate."""
        if alphabet.idAlphabet in {a.idAlphabet for a in self.listAlphabets}:
            raise ValueError(f"Symbole avec l'id {alphabet.idAlphabet} existe déjà.")
        self.listAlphabets.append(alphabet)

    def supprimer_alphabet(self, idAlphabet: str) -> None:
        """Supprime un symbole et ses transitions associées."""
        alphabet = next((a for a in self.listAlphabets if a.idAlphabet == idAlphabet), None)
        if not alphabet:
            raise ValueError(f"Symbole avec l'id {idAlphabet} introuvable.")
        
        # Supprimer les transitions utilisant ce symbole
        self.listTransition = [t for t in self.listTransition if t.alphabet.idAlphabet != idAlphabet]
        self.listAlphabets.remove(alphabet)

    # --- Méthodes pour gérer les transitions ---
    def ajouter_transition(self, transition: Transition) -> None:
        """Ajoute une transition à l'automate."""
        # Vérifier que les états et le symbole existent
        if not any(e.idEtat == transition.etatSource.idEtat for e in self.listEtats):
            raise ValueError(f"Etat source {transition.etatSource.idEtat} introuvable.")
        if not any(e.idEtat == transition.etatDestination.idEtat for e in self.listEtats):
            raise ValueError(f"Etat destination {transition.etatDestination.idEtat} introuvable.")
        if not any(a.idAlphabet == transition.alphabet.idAlphabet for a in self.listAlphabets):
            raise ValueError(f"Symbole {transition.alphabet.idAlphabet} introuvable dans l'alphabet.")
        
        self.listTransition.append(transition)

    def supprimer_transition(self, idTransition: str) -> None:
        """Supprime une transition."""
        transition = next((t for t in self.listTransition if t.idTransition == idTransition), None)
        if not transition:
            raise ValueError(f"Transition avec l'id {idTransition} introuvable.")
        self.listTransition.remove(transition)

    # --- Méthodes pour la persistance (sauvegarde/chargement) ---
    def sauvegarder_json(self, dossier: str = "Automates") -> None:
        """Sauvegarde l'automate dans un fichier JSON."""
        data = {
            "nom": self.nom,
            "alphabet": [{"id": a.idAlphabet, "val": a.valAlphabet} for a in self.listAlphabets],
            "etats": [{"id": e.idEtat, "label": e.labelEtat, "type": e.typeEtat} for e in self.listEtats],
            "transitions": [{
                "id": t.idTransition,
                "source": t.etatSource.idEtat,
                "dest": t.etatDestination.idEtat,
                "symbole": t.alphabet.idAlphabet
            } for t in self.listTransition]
        }
        
        os.makedirs(dossier, exist_ok=True)
        chemin = f"{dossier}/{self.nom}.json"
        with open(chemin, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=4)

    @classmethod
    def charger_json(cls, nom: str, dossier: str = "Automates") -> 'Automate':
        """Charge un automate à partir d'un fichier JSON."""
        chemin = f"{dossier}/{nom}.json"
        with open(chemin, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        automate = cls(data["nom"])
        
        # Charger l'alphabet
        for symbole in data["alphabet"]:
            automate.ajouter_alphabet(Alphabet(symbole["id"], symbole["val"]))
        
        # Charger les états
        for etat_data in data["etats"]:
            etat = Etat(etat_data["id"], etat_data["label"], etat_data["type"])
            automate.ajouter_etat(etat)
        
        # Charger les transitions
        for transition_data in data["transitions"]:
            source = next(e for e in automate.listEtats if e.idEtat == transition_data["source"])
            dest = next(e for e in automate.listEtats if e.idEtat == transition_data["dest"])
            symbole = next(a for a in automate.listAlphabets if a.idAlphabet == transition_data["symbole"])
            automate.ajouter_transition(Transition(
                transition_data["id"], source, dest, symbole
            ))
        
        return automate

    def __repr__(self) -> str:
        return f"Automate(nom={self.nom}, états={len(self.listEtats)}, transitions={len(self.listTransition)})"
