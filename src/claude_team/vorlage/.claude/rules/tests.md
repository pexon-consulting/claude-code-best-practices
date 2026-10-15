---
paths:
  - "tests/**/*"
  - "**/*.test.{ts,tsx,js}"
  - "**/test_*.py"
---

# Regeln für Tests

- Ein Test prüft ein Verhalten. Name sagt, was erwartet wird: `test_leere_liste_ergibt_null`.
- Keine echten Personendaten. Muster-IBAN `DE89 3704 0044 0532 0130 00`, Mails an `@example.com`.
- Kein Netzwerk in Unit-Tests. Externe Dienste mocken.
- Einen fehlschlagenden Test nie löschen oder auf skip setzen, um grün zu werden. Ursache melden.
