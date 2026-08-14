# Language support

Namche Shadow Sans and Namche Shadow Mono are designed for Latin text and ship
the inherited Geist Cyrillic character set. Their OpenType metadata therefore
declares `dlng=Latn` and `slng=Latn,Cyrl`. Namche Shadow Pixel currently
declares Latin only.

The supported shaping contract for Sans and Mono includes:

- combining acute, grave, and circumflex marks used with Russian, Ukrainian,
  Belarusian, Bulgarian, and Serbian Cyrillic;
- removal of the soft upper dot before top marks on Cyrillic `і` and `ј`,
  Latin `į`, and Vietnamese `ị`;
- the existing Latin, Latin Extended, Vietnamese, Cyrillic, and Cyrillic
  Extended codepoints present in the release fonts.

Namche does not claim every character that Google Fonts classifies as an
*auxiliary* orthography codepoint. The current deliberate omissions are:

- `Ǿ ǿ`;
- `Ĕ ĕ Ĭ ĭ Ŀ ŀ Ŏ ŏ`;
- `Ĳ ĳ`;
- `Ȟ ȟ Ʒ ʒ Ǯ ǯ`;
- `Ǔ ǔ ſ ʻ`.

Those omissions do not remove the primary orthography of the languages named
by Fontspector, but they mean the project does not promise exhaustive
historical, transliteration, or auxiliary coverage. Adding any of these
characters requires a separate design review rather than copying outlines from
another font solely to silence a distributor profile.

The upright Namche Shadow Sans variable font additionally parks `ѫ` until its
rounded masters are interpolation-compatible. This exception does not apply to
the Sans statics, which must continue to include the character in every weight.

Run the focused `soft_dotted` and
`googlefonts/glyphsets/shape_languages` Fontspector checks after any source or
OpenType-layout change. The retained language-shaping warning should contain
only the auxiliary omissions above; an attachment failure or a mandatory
soft-dot failure is a regression.
