
import os, json, re
from model import Alphabet, Automate, Etat, Transition
from typing import List, Dict, Optional

# --- Gestion des automates (Nouveau code) ---
class GestionAutomates:
    def __init__(self):
        self.automates: Dict[str, Automate] = {}  # Dictionnaire pour stocker les automates en mémoire
        self.dossier_automates = "Automates"

    def creer_automate(self) -> None:
        """Crée un nouvel automate interactivement."""
        print("\n--- Création d'un nouvel automate ---")
        nom = input("Nom de l'automate (doit être unique) : ").strip()
        
        if nom in self.automates:
            print(f"Erreur : Un automate avec le nom '{nom}' existe déjà.")
            return
        
        automate = Automate(nom)
        
        # Ajout des symboles à l'alphabet
        print("\nAjout des symboles à l'alphabet (tapez 'fin' pour terminer) :")
        while True:
            symbole = input("Symbole (ex: 'a', '0') : ").strip()
            if symbole.lower() == 'fin':
                break
            automate.ajouter_alphabet(Alphabet(f"sym_{len(automate.listAlphabets)}", symbole))
        
        # Ajout des états
        print("\nAjout des états (tapez 'fin' pour terminer) :")
        while True:
            id_etat = input("ID de l'état (ex: 'q0') : ").strip()
            if id_etat.lower() == 'fin':
                break
            if not re.match(r'^[a-zA-Z0-9]+$', id_etat):  # Simple alphanumeric check, you might need more complex validation
                print("ID d'état invalide. Il doit contenir uniquement des lettres et des chiffres.")
                continue
            label = input("Label de l'état : ").strip()
            type_etat = input("Type (initial/final/normal) : ").strip().lower()
            if type_etat not in ["initial", "final", "normal"]:
                print("Type d'état invalide. Veuillez choisir parmi 'initial', 'final' ou 'normal'.")
                continue
            automate.ajouter_etat(Etat(id_etat, label, type_etat))
        
        # Ajout des transitions
        print("\nAjout des transitions (tapez 'fin' pour terminer) :")
        while True:
            print("\nListe des états disponibles :")
            for etat in automate.listEtats:
                print(f"- {etat.idEtat} ({etat.labelEtat})")
            
            source = input("ID état source : ").strip()
            if source.lower() == 'fin':
                break
            
            dest = input("ID état destination : ").strip()
            print("Symboles disponibles :", [a.valAlphabet for a in automate.listAlphabets])
            symbole = input("Symbole de la transition : ").strip()
            
            try:
                etat_source = next(e for e in automate.listEtats if e.idEtat == source)
                etat_dest = next(e for e in automate.listEtats if e.idEtat == dest)
                alphabet = next(a for a in automate.listAlphabets if a.valAlphabet == symbole)
                
                automate.ajouter_transition(Transition(
                    f"trans_{len(automate.listTransition)}",
                    etat_source,
                    etat_dest,
                    alphabet
                ))
                print("Transition ajoutée avec succès !")
            except StopIteration:
                print("Erreur : Etat ou symbole introuvable.")
        
        # Sauvegarde et ajout à la collection
        automate.sauvegarder_json(self.dossier_automates)
        self.automates[nom] = automate
        print(f"\nAutomate '{nom}' créé et sauvegardé avec succès !")

    def modifier_automate(self) -> None:
        """Modifie un automate existant."""
        print("\n--- Modification d'un automate ---")
        nom = input("Nom de l'automate à modifier : ").strip()
        
        if nom not in self.automates:
            print(f"Erreur : Automate '{nom}' introuvable.")
            return
        
        automate = self.automates[nom]
        
        while True:
            print("\nQue voulez-vous modifier ?")
            print("1. Ajouter un symbole à l'alphabet")
            print("2. Supprimer un symbole")
            print("3. Ajouter un état")
            print("4. Modifier/supprimer un état")
            print("5. Ajouter une transition")
            print("6. Supprimer une transition")
            print("7. Terminer les modifications")
            
            choix = input("Votre choix (1-7) : ").strip()
            
            if choix == '1':
                symbole = input("Nouveau symbole : ").strip()
                automate.ajouter_alphabet(Alphabet(f"sym_{len(automate.listAlphabets)}", symbole))
                print("Symbole ajouté !")
            
            elif choix == '2':
                print("Symboles disponibles :", [a.valAlphabet for a in automate.listAlphabets])
                symbole = input("Symbole à supprimer : ").strip()
                try:
                    alphabet = next(a for a in automate.listAlphabets if a.valAlphabet == symbole)
                    automate.supprimer_alphabet(alphabet.idAlphabet)
                    print("Symbole supprimé !")
                except StopIteration:
                    print("Symbole introuvable.")
            
            elif choix == '3':
                id_etat = input("ID du nouvel état : ").strip()
                label = input("Label : ").strip()
                type_etat = input("Type (initial/final/normal) : ").strip().lower()
                automate.ajouter_etat(Etat(id_etat, label, type_etat))
                print("Etat ajouté !")
            
            elif choix == '4':
                print("\nEtats disponibles :")
                for etat in automate.listEtats:
                    print(f"- {etat.idEtat} ({etat.labelEtat}, {etat.typeEtat})")
                
                action = input("Voulez-vous (m)odifier ou (s)upprimer un état ? ").strip().lower()
                id_etat = input("ID de l'état : ").strip()
                
                try:
                    etat = next(e for e in automate.listEtats if e.idEtat == id_etat)
                    
                    if action == 'm':
                        new_label = input(f"Nouveau label (actuel: {etat.labelEtat}) : ").strip()
                        new_type = input(f"Nouveau type (actuel: {etat.typeEtat}) : ").strip().lower()
                        etat.labelEtat = new_label if new_label else etat.labelEtat
                        etat.typeEtat = new_type if new_type else etat.typeEtat
                        print("Etat modifié !")
                    elif action == 's':
                        automate.supprimer_etat(id_etat)
                        print("Etat supprimé !")
                except StopIteration:
                    print("Etat introuvable.")
            
            elif choix == '5':
                print("\nAjout d'une transition :")
                print("Etats disponibles :", [e.idEtat for e in automate.listEtats])
                source = input("ID état source : ").strip()
                dest = input("ID état destination : ").strip()
                print("Symboles disponibles :", [a.valAlphabet for a in automate.listAlphabets])
                symbole = input("Symbole : ").strip()
                
                try:
                    etat_source = next(e for e in automate.listEtats if e.idEtat == source)
                    etat_dest = next(e for e in automate.listEtats if e.idEtat == dest)
                    alphabet = next(a for a in automate.listAlphabets if a.valAlphabet == symbole)
                    
                    automate.ajouter_transition(Transition(
                        f"trans_{len(automate.listTransition)}",
                        etat_source,
                        etat_dest,
                        alphabet
                    ))
                    print("Transition ajoutée !")
                except StopIteration:
                    print("Erreur : Etat ou symbole introuvable.")
            
            elif choix == '6':
                print("\nTransitions disponibles :")
                for i, trans in enumerate(automate.listTransition):
                    print(f"{i+1}. {trans.etatSource.idEtat} --{trans.alphabet.valAlphabet}--> {trans.etatDestination.idEtat}")
                
                try:
                    idx = int(input("Numéro de la transition à supprimer : ")) - 1
                    if 0 <= idx < len(automate.listTransition):
                        automate.supprimer_transition(automate.listTransition[idx].idTransition)
                        print("Transition supprimée !")
                    else:
                        print("Numéro invalide.")
                except ValueError:
                    print("Veuillez entrer un nombre.")
            
            elif choix == '7':
                automate.sauvegarder_json(self.dossier_automates)
                print("Modifications sauvegardées !")
                break
            
            else:
                print("Choix invalide.")

    def supprimer_automate(self) -> None:
        """Supprime complètement un automate."""
        print("\n--- Suppression d'un automate ---")
        nom = input("Nom de l'automate à supprimer : ").strip()
        
        if nom not in self.automates:
            print(f"Erreur : Automate '{nom}' introuvable.")
            return
        
        # Suppression du fichier
        chemin = f"{self.dossier_automates}/{nom}.json"
        if os.path.exists(chemin):
            os.remove(chemin)
        
        # Suppression de la mémoire
        del self.automates[nom]
        print(f"Automate '{nom}' supprimé avec succès !")

    def charger_automates_existants(self) -> None:
        """Charge tous les automates existants depuis le dossier."""
        if not os.path.exists(self.dossier_automates):
            os.makedirs(self.dossier_automates)
            return
        
        for fichier in os.listdir(self.dossier_automates):
            if fichier.endswith(".json"):
                nom = fichier[:-5]  # Retire l'extension .json
                try:
                    automate = Automate.charger_json(nom, self.dossier_automates)
                    self.automates[nom] = automate
                except Exception as e:
                    print(f"Erreur lors du chargement de {nom} : {str(e)}")

# --- Interface CLI ---
def main():
    gestion = GestionAutomates()
    gestion.charger_automates_existants()
    
    while True:
        print("\n=== Gestion des Automates ===")
        print("1. Créer un nouvel automate")
        print("2. Modifier un automate existant")
        print("3. Supprimer un automate")
        print("4. Lister les automates disponibles")
        print("5. Quitter")
        
        choix = input("Votre choix (1-5) : ").strip()
        
        if choix == '1':
            gestion.creer_automate()
        elif choix == '2':
            gestion.modifier_automate()
        elif choix == '3':
            gestion.supprimer_automate()
        elif choix == '4':
            print("\nAutomates disponibles :")
            for nom in gestion.automates:
                print(f"- {nom} ({len(gestion.automates[nom].listEtats)} états, {len(gestion.automates[nom].listTransition)} transitions)")
        elif choix == '5':
            print("Au revoir !")
            break
        else:
            print("Choix invalide. Veuillez réessayer.")

if __name__ == "__main__":
    main()