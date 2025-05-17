from model import Automate
from typing import Dict, Set

class AnalyseAutomate:
    """
    Classe utilitaire pour l'analyse et la transformation des automates finis (AFD/AFN).
    Contient des méthodes statiques pour vérifier, compléter, déterminiser et minimiser les automates.
    """

    @staticmethod
    def est_deterministe(automate: Automate) -> bool:
        """
        Détermine si un automate fini est déterministe (AFD).
        Un automate est déterministe s'il possède exactement un état initial,
        aucune transition ε (vide), et pour chaque état et chaque symbole de l'alphabet,
        il y a au plus une transition sortante.
        Retourne True si l'automate est déterministe, sinon False.
        """
        # Vérifier qu'il y a exactement un état initial
        if len(automate.listInitiaux) != 1:
            return False
        # Vérifier l'absence de transitions ε (optionnel)
        for t in automate.listTransition:
            if t.alphabet.valAlphabet == '' or t.alphabet.valAlphabet == 'ε':
                return False
        # Pour chaque état et chaque symbole, vérifier qu'il y a au plus une transition sortante
        transitions_dict: Dict[str, Dict[str, Set[str]]] = {}
        for t in automate.listTransition:
            src = t.etatSource.idEtat
            symb = t.alphabet.valAlphabet
            if src not in transitions_dict:
                transitions_dict[src] = {}
            if symb not in transitions_dict[src]:
                transitions_dict[src][symb] = set()
            transitions_dict[src][symb].add(t.etatDestination.idEtat)
        for etat in automate.listEtats:
            src = etat.idEtat
            if src in transitions_dict:
                for symb, dests in transitions_dict[src].items():
                    if len(dests) > 1:
                        return False
        return True

    @staticmethod
    def est_complet(automate: Automate) -> bool:
        """
        Vérifie si un automate est complet :
        Pour chaque état q et chaque symbole a de l'alphabet,
        il existe au moins une transition (q, a, p).
        """
        for etat in automate.listEtats:
            for symbole in automate.listAlphabets:
                found = False
                for t in automate.listTransition:
                    if t.etatSource.idEtat == etat.idEtat and t.alphabet.valAlphabet == symbole.valAlphabet:
                        found = True
                        break
                if not found:
                    return False
        return True

    @staticmethod
    def completer(automate: Automate) -> Automate:
        """
        Complète l'automate en ajoutant un état puits et toutes les transitions manquantes
        pour chaque couple (état, symbole) de l'alphabet. L'état puits s'auto-boucle sur chaque symbole.
        Retourne l'automate complété (modifie en place).
        """
        # Générer un nom unique pour l'état puits
        noms_etats = {e.idEtat for e in automate.listEtats}
        nom_puits = "PUITS"
        i = 1
        while nom_puits in noms_etats:
            nom_puits = f"PUITS{i}"
            i += 1
        # Créer l'état puits
        from model import Etat, Transition
        etat_puits = Etat(nom_puits, "Etat puits", "normal")
        automate.ajouter_etat(etat_puits)
        # Pour chaque état et chaque symbole, ajouter la transition manquante vers le puits
        for etat in automate.listEtats:
            for symbole in automate.listAlphabets:
                existe = False
                for t in automate.listTransition:
                    if t.etatSource.idEtat == etat.idEtat and t.alphabet.valAlphabet == symbole.valAlphabet:
                        existe = True
                        break
                if not existe:
                    automate.ajouter_transition(Transition(
                        f"trans_{len(automate.listTransition)}",
                        etat,
                        etat_puits,
                        symbole
                    ))
        # Boucler l'état puits sur lui-même pour chaque symbole
        for symbole in automate.listAlphabets:
            automate.ajouter_transition(Transition(
                f"trans_{len(automate.listTransition)}",
                etat_puits,
                etat_puits,
                symbole
            ))
        return automate

    @staticmethod
    def determiniser(afn: Automate) -> Automate:
        """
        Transforme un AFN en AFD équivalent par la méthode des sous-ensembles (construction de puissance).
        Prend explicitement en compte l'état ∅ (ensemble vide) comme état poubelle.
        Retourne un nouvel automate déterministe.
        """
        from model import Automate, Etat, Alphabet, Transition
        # 1. Préparer l'alphabet
        alphabet = afn.listAlphabets
        # 2. Macro-états : chaque état = ensemble d'états AFN (utiliser frozenset pour hash)
        etats_afn = {e.idEtat: e for e in afn.listEtats}
        finaux_afn = {e.idEtat for e in afn.listFinaux}
        # 3. Initialisation
        init_set = frozenset(e.idEtat for e in afn.listInitiaux)
        file = [init_set]
        etats_dfa = {init_set: Etat(str(sorted(init_set)), str(sorted(init_set)), "initial")}
        transitions_dfa = []
        finaux_dfa = set()
        # 4. Déterminisation
        deja_vus = set()
        while file:
            courant = file.pop(0)
            if courant in deja_vus:
                continue
            deja_vus.add(courant)
            # Marquer comme final si au moins un état final AFN est présent
            if any(e in finaux_afn for e in courant):
                finaux_dfa.add(courant)
            for symbole in alphabet:
                cible = set()
                for id_etat in courant:
                    for t in afn.listTransition:
                        if t.etatSource.idEtat == id_etat and t.alphabet.valAlphabet == symbole.valAlphabet:
                            cible.add(t.etatDestination.idEtat)
                if not cible:
                    # Ajouter un état représentant l'ensemble vide (∅)
                    cible_fs = frozenset()
                    if cible_fs not in etats_dfa:
                        etats_dfa[cible_fs] = Etat("∅", "∅", "normal")
                        # Ne pas ajouter ∅ à la file, il est déjà terminal
                    transitions_dfa.append(Transition(
                        f"trans_{len(transitions_dfa)}",
                        etats_dfa[courant],
                        etats_dfa[cible_fs],
                        symbole
                    ))
                    continue
                cible_fs = frozenset(cible)
                if cible_fs not in etats_dfa:
                    etats_dfa[cible_fs] = Etat(str(sorted(cible_fs)), str(sorted(cible_fs)), "normal")
                    file.append(cible_fs)
                transitions_dfa.append(Transition(
                    f"trans_{len(transitions_dfa)}",
                    etats_dfa[courant],
                    etats_dfa[cible_fs],
                    symbole
                ))
        # Ajouter les transitions ∅ -> ∅ pour tous les symboles si ∅ existe
        if frozenset() in etats_dfa:
            etat_vide = etats_dfa[frozenset()]
            for symbole in alphabet:
                transitions_dfa.append(Transition(
                    f"trans_{len(transitions_dfa)}",
                    etat_vide,
                    etat_vide,
                    symbole
                ))
        # 5. Construire l'automate AFD
        afd = Automate(afn.nom + "_AFD")
        for symbole in alphabet:
            afd.ajouter_alphabet(symbole)
        for etat in etats_dfa.values():
            if etat.typeEtat == "initial":
                afd.ajouter_etat(Etat(etat.idEtat, etat.labelEtat, "initial"))
            else:
                afd.ajouter_etat(Etat(etat.idEtat, etat.labelEtat, "normal"))
        for macro in finaux_dfa:
            if macro == frozenset():
                continue  # ∅ n'est jamais final
            etat_final = next(e for e in afd.listEtats if e.idEtat == str(sorted(macro)))
            etat_final.set_typeEtat("final")
            afd.listFinaux.append(etat_final)
        for t in transitions_dfa:
            src = next(e for e in afd.listEtats if e.idEtat == t.etatSource.idEtat)
            dest = next(e for e in afd.listEtats if e.idEtat == t.etatDestination.idEtat)
            afd.ajouter_transition(Transition(
                t.idTransition,
                src,
                dest,
                t.alphabet
            ))
        return afd

    @staticmethod
    def minimiser(afd: Automate) -> Automate:
        """
        Minimise un AFD en supprimant les états inaccessibles et en fusionnant les états équivalents (algorithme de partition).
        Retourne un nouvel automate minimal équivalent.
        """
        from model import Automate, Etat, Alphabet, Transition
        # 1. Supprimer les états inaccessibles
        accessibles = set()
        file = [e for e in afd.listInitiaux]
        while file:
            courant = file.pop()
            if courant.idEtat in accessibles:
                continue
            accessibles.add(courant.idEtat)
            for t in afd.listTransition:
                if t.etatSource.idEtat == courant.idEtat and t.etatDestination.idEtat not in accessibles:
                    file.append(t.etatDestination)
        # 2. Partition initiale : finaux vs non-finaux
        finaux = {e.idEtat for e in afd.listFinaux if e.idEtat in accessibles}
        non_finaux = {e.idEtat for e in afd.listEtats if e.idEtat in accessibles and e.idEtat not in finaux}
        partitions = [finaux, non_finaux]
        # 3. Raffinement des partitions
        alphabet = [a.valAlphabet for a in afd.listAlphabets]
        transitions = {(t.etatSource.idEtat, t.alphabet.valAlphabet): t.etatDestination.idEtat for t in afd.listTransition}
        stable = False
        while not stable:
            stable = True
            new_partitions = []
            for bloc in partitions:
                sous_blocs = {}
                for etat in bloc:
                    signature = []
                    for a in alphabet:
                        dest = transitions.get((etat, a), None)
                        for i, part in enumerate(partitions):
                            if dest in part:
                                signature.append(i)
                                break
                        else:
                            signature.append(-1)
                    signature = tuple(signature)
                    if signature not in sous_blocs:
                        sous_blocs[signature] = set()
                    sous_blocs[signature].add(etat)
                if len(sous_blocs) > 1:
                    stable = False
                new_partitions.extend(sous_blocs.values())
            partitions = new_partitions
        # 4. Construire l'automate minimal
        etat_map = {}
        min_afd = Automate(afd.nom + "_min")
        for i, bloc in enumerate(partitions):
            id_bloc = f"B{i}"
            label_bloc = str(sorted(bloc))
            type_bloc = "normal"
            if any(e.idEtat in bloc for e in afd.listInitiaux):
                type_bloc = "initial"
            if any(e.idEtat in bloc for e in afd.listFinaux):
                type_bloc = "final"
            etat = Etat(id_bloc, label_bloc, type_bloc)
            min_afd.ajouter_etat(etat)
            etat_map[frozenset(bloc)] = etat
        for a in afd.listAlphabets:
            min_afd.ajouter_alphabet(a)
        # Transitions
        for i, bloc in enumerate(partitions):
            src = etat_map[frozenset(bloc)]
            representant = next(iter(bloc))
            for a in alphabet:
                dest = transitions.get((representant, a), None)
                if dest is not None:
                    for j, bloc2 in enumerate(partitions):
                        if dest in bloc2:
                            dst = etat_map[frozenset(bloc2)]
                            min_afd.ajouter_transition(Transition(
                                f"trans_{len(min_afd.listTransition)}",
                                src,
                                dst,
                                next(al for al in min_afd.listAlphabets if al.valAlphabet == a)
                            ))
                            break
        return min_afd

    @staticmethod
    def est_minimal(afd: Automate) -> bool:
        """
        Vérifie si un AFD est minimal en comparant le nombre d'états avec son minimisé.
        Retourne True si l'automate est déjà minimal, sinon False.
        """
        min_afd = AnalyseAutomate.minimiser(afd)
        return len(min_afd.listEtats) == len(afd.listEtats)

