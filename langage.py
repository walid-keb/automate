from model import Automate, Etat, Alphabet, Transition
from typing import List, Set
from itertools import product


def simuler_mot(automate: Automate, mot: str) -> bool:
    """Simule un mot sur un automate (supposé déterministe)."""
    etat_courant = next((e for e in automate.listInitiaux), None)
    if not etat_courant:
        raise ValueError("Aucun état initial défini.")

    for symbole in mot:
        transitions = [t for t in automate.listTransition
                       if t.etatSource.idEtat == etat_courant.idEtat
                       and t.alphabet.valAlphabet == symbole]
        if not transitions:
            return False
        etat_courant = transitions[0].etatDestination

    return etat_courant in automate.listFinaux


def generer_mots_acceptes(automate: Automate, longueur_max: int) -> List[str]:
    """Génère les mots acceptés jusqu'à une longueur donnée."""
    symboles = [a.valAlphabet for a in automate.listAlphabets]
    mots_acceptes = []

    for l in range(longueur_max + 1):
        for prod in product(symboles, repeat=l):
            mot = ''.join(prod)
            if simuler_mot(automate, mot):
                mots_acceptes.append(mot)

    return mots_acceptes


def union_automates(a1: Automate, a2: Automate) -> Automate:
    """Construit l’union de deux automates déterministes (produit cartésien)."""
    new_auto = Automate(f"{a1.nom}_union_{a2.nom}")
    alphabet = a1.listAlphabets  # Supposés identiques

    for a in alphabet:
        new_auto.ajouter_alphabet(Alphabet(a.idAlphabet, a.valAlphabet))

    # Création des états du produit
    for e1 in a1.listEtats:
        for e2 in a2.listEtats:
            id_prod = f"{e1.idEtat}_{e2.idEtat}"
            type_prod = "normal"
            if e1 in a1.listInitiaux and e2 in a2.listInitiaux:
                type_prod = "initial"
            if e1 in a1.listFinaux or e2 in a2.listFinaux:
                if type_prod == "initial":
                    type_prod = "initial_final"
                else:
                    type_prod = "final"
            etat_prod = Etat(id_prod, id_prod, type_prod)
            new_auto.ajouter_etat(etat_prod)

    # Transitions du produit
    for t1 in a1.listTransition:
        for t2 in a2.listTransition:
            if t1.alphabet.valAlphabet == t2.alphabet.valAlphabet:
                source_id = f"{t1.etatSource.idEtat}_{t2.etatSource.idEtat}"
                dest_id = f"{t1.etatDestination.idEtat}_{t2.etatDestination.idEtat}"
                source = next(e for e in new_auto.listEtats if e.idEtat == source_id)
                dest = next(e for e in new_auto.listEtats if e.idEtat == dest_id)
                symbole = next(a for a in new_auto.listAlphabets if a.valAlphabet == t1.alphabet.valAlphabet)
                new_auto.ajouter_transition(Transition(f"{source_id}->{dest_id}_{symbole.idAlphabet}", source, dest, symbole))

    return new_auto


def intersection_automates(a1: Automate, a2: Automate) -> Automate:
    """Construit l’intersection de deux automates déterministes."""
    union = union_automates(a1, a2)
    # Redéfinir les états finaux uniquement si les deux composantes sont finales
    union.listFinaux = []
    for e in union.listEtats:
        id1, id2 = e.idEtat.split("_")
        if any(f.idEtat == id1 for f in a1.listFinaux) and any(f.idEtat == id2 for f in a2.listFinaux):
            union.listFinaux.append(e)
    return union


def complement_automate(automate: Automate) -> Automate:
    """Renvoie le complément d’un automate déterministe complet."""
    comp = Automate(automate.nom + "_complement")
    for a in automate.listAlphabets:
        comp.ajouter_alphabet(Alphabet(a.idAlphabet, a.valAlphabet))

    for e in automate.listEtats:
        new_type = "normal"
        if e in automate.listInitiaux:
            new_type = "initial"
        new_e = Etat(e.idEtat, e.labelEtat, new_type)
        comp.ajouter_etat(new_e)

    comp.listFinaux = [e for e in comp.listEtats if all(f.idEtat != e.idEtat for f in automate.listFinaux)]

    for t in automate.listTransition:
        src = next(e for e in comp.listEtats if e.idEtat == t.etatSource.idEtat)
        dst = next(e for e in comp.listEtats if e.idEtat == t.etatDestination.idEtat)
        alpha = next(a for a in comp.listAlphabets if a.idAlphabet == t.alphabet.idAlphabet)
        comp.ajouter_transition(Transition(t.idTransition, src, dst, alpha))

    return comp


def sont_equivalents(a1: Automate, a2: Automate) -> bool:
    """Teste si deux automates déterministes sont équivalents."""
    # A et B sont équivalents ssi leur différence est vide dans les deux sens
    from analyse import minimiser_automate  # si dispo

    comp1 = complement_automate(a1)
    comp2 = complement_automate(a2)

    inter1 = intersection_automates(a1, comp2)
    inter2 = intersection_automates(a2, comp1)

    # S’ils reconnaissent ∅ alors ils n’ont pas d’états finaux accessibles
    mots1 = generer_mots_acceptes(inter1, 5)
    mots2 = generer_mots_acceptes(inter2, 5)
    return not mots1 and not mots2


# --- Interface de test CLI ---
if __name__ == "__main__":
    automate = Automate.charger_json("exemple1")
    mot = "abba"
    print(f"Mot '{mot}' accepté ? {simuler_mot(automate, mot)}")

    mots = generer_mots_acceptes(automate, 3)
    print("Mots acceptés jusqu'à longueur 3 :", mots)
