# WBP_MoviaRegler – plan til næste gang (bygges i Unreal EN gang)

Placering: `/Game/MoviaSkaerme/WBP_MoviaRegler` (User Widget, usynlig, 1x1 px)

## Variabel
- `Regler` (String, **Instance Editable**). Python-motoren skriver den.
  En regel pr. linje:  `kilde|operator|vaerdi|handling|maal|til|ellers`
  fx `UMG_TB_NAtron_Time_Icons/TextTimeOffset|>|60|farve|M_E000|#DE3B26|#3FA535`

## Logik (Event Construct: parse én gang -> Timer hver 0,25 s)
1. Split `Regler` på linjeskift, hver linje på `|`.
2. Find ejer-skærmen: Get Parent -> ... -> den UserWidget der ejer os (eller Get Outer).
3. **kilde**: `GetWidgetFromName`. Indeholder kilden `/`: find barnet først, cast til UserWidget, `GetWidgetFromName` igen.
   - TextBlock -> læs teksten. Tal: "+2" = minutter -> *60; "mm:ss" -> sekunder; "-" foran = negativ.
     (Skal tjekkes: hvilket format TextTimeOffset viser i spillet.)
   - Andet widget -> værdien er "ja", hvis det er synligt.
4. **operator**: `>` `<` (som tal), `=` `!=` (tekst), `indeholder` (Contains).
5. **handling** på maal (`GetWidgetFromName`):
   - farve: Border -> SetBrushColor, Image -> SetColorAndOpacity (hex -> LinearColor fra sRGB)
   - tekstfarve: TextBlock SetColorAndOpacity
   - tekst: TextBlock SetText
   - vis / skjul: SetVisibility (Visible / Collapsed)
6. Er reglen falsk og `ellers` er udfyldt -> brug ellers. Linjerne køres i rækkefølge (den sidste sande vinder).

## Python-siden (FÆRDIG)
- movia_motor.saet_regler(): oversætter JSON-regler, sætter widget'en ind som `MoviaRegler`, skriver `Regler`.
- Findes WBP_MoviaRegler ikke, gemmes reglerne i `regler_<skaerm>.txt`.
- Editoren: knappen "⚙ Regler…". AI_GUIDE.md: afsnittet "regler".
