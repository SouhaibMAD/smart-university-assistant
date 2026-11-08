## Ce que fait cette PR
<!-- 3 lignes maximum. Pas de roman. -->

## Comment tester
<!-- Commandes exactes, dans l'ordre. Si je ne peux pas reproduire, la PR est refusée. -->

## Checklist (cocher TOUT, sinon la PR n'est pas relue)
- [ ] Je n'ai modifié QUE les fichiers de mon périmètre
- [ ] `ruff check .` passe sans erreur
- [ ] Les tests de ma partie passent (`docker compose exec backend pytest -q`)
- [ ] Aucun secret, aucune clé, aucun `.env` dans le commit
- [ ] Aucune nouvelle dépendance ajoutée sans accord du tech lead
- [ ] Les signatures des fonctions du contrat n'ont pas été modifiées
- [ ] Je peux expliquer chaque ligne de cette PR à l'oral

## Captures / sorties de tests
<!-- Colle ici la sortie de pytest ou une capture d'écran -->
