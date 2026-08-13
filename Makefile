SOURCES=$(shell python3 scripts/read-config.py --sources )
FAMILY=$(shell python3 scripts/read-config.py --family )

help:
	@echo "###"
	@echo "# Build targets for $(FAMILY)"
	@echo "###"
	@echo
	@echo "  make build:  Builds the fonts and places them in the fonts/ directory"
	@echo "  make finalize-sans-statics GLYPHS_SANS_EXPORT=/path: merge native Glyphs OTF/TTF exports into the release files"
	@echo "  make test:   Tests the fonts with fontspector"
	@echo "  make proof:  Creates HTML proof documents in the proof/ directory"
	@echo "  make images: Creates PNG specimen images in the documentation/ directory"
	@echo

build: build.stamp

venv: venv/touchfile

venv-pixel: venv-pixel/touchfile

customize: venv
	. venv/bin/activate; python3 scripts/customize.py

build.stamp: venv venv-pixel sources/config-NamcheShadowSans.yaml $(SOURCES)
	$(MAKE) check-source-copies
	rm -rf fonts namche-shadow-font namche-shadow-font.zip
	# Namche Shadow Sans statics are native Glyphs exports: gftools does not run
	# the seven RoundCorner instance filters. Skip that config so a Linux build
	# cannot silently replace the approved outlines. Namche Shadow Pixel uses a
	# virtual master, which the released gftools in
	# requirements.txt can't build (it fails with "No final targets"). Build it
	# with the dev gftools in venv-pixel that has the virtual-master fix;
	# Mono uses venv.
	@for config in sources/config*.yaml; do \
		if [ "$$config" = "sources/config-NamcheShadowSans.yaml" ]; then \
			echo "Using committed native Glyphs exports for Namche Shadow Sans"; \
		elif [ "$$config" = "sources/config-NamcheShadowPixel.yaml" ]; then \
			( . venv-pixel/bin/activate && gftools builder "$$config" ); \
		else \
			( . venv/bin/activate && gftools builder "$$config" ); \
		fi; \
	done
	# Sans statics and Pixel statics/webfonts are native Glyphs exports committed
	# to the repository. Restore them after the clean build so release and npm
	# artifacts use the approved outlines.
	git checkout -- fonts/NamcheShadowSans/otf fonts/NamcheShadowSans/ttf fonts/NamcheShadowSans/webfonts
	git checkout -- fonts/NamcheShadowPixel/otf fonts/NamcheShadowPixel/ttf fonts/NamcheShadowPixel/webfonts
	# Sans metadata was finalized with the native exports; leave those committed
	# files byte-for-byte intact. Normalize only families generated in this run.
	. venv/bin/activate; python3 scripts/rename_font_metadata.py fonts/NamcheShadowMono
	. venv/bin/activate; python3 scripts/rename_font_metadata.py fonts/NamcheShadowPixel
	. venv/bin/activate; python3 scripts/rename_font_metadata.py --check fonts
	$(MAKE) copy-npm-fonts
	$(MAKE) create-release-zip
	touch build.stamp

check-source-copies:
	# Mono and Pixel are deliberately outline-identical Geist derivatives. Only
	# fontinfo.plist may differ because it contains family names and attribution.
	diff -qr --exclude=fontinfo.plist originals/geist/sources/GeistMono.glyphspackage sources/NamcheShadowMono.glyphspackage
	diff -qr --exclude=fontinfo.plist originals/geist/sources/GeistMono-Italic.glyphspackage sources/NamcheShadowMono-Italic.glyphspackage
	diff -qr --exclude=fontinfo.plist originals/geist/sources/GeistPixel.glyphspackage sources/NamcheShadowPixel.glyphspackage

finalize-sans-statics: venv
	test -n "$(GLYPHS_SANS_EXPORT)" || (echo "Set GLYPHS_SANS_EXPORT to a directory containing otf/ and ttf/." && exit 1)
	. venv/bin/activate; python3 scripts/finalize_glyphs_statics.py --gftools fonts/NamcheShadowSans --glyphs "$(GLYPHS_SANS_EXPORT)" --output fonts/NamcheShadowSans
	. venv/bin/activate; python3 scripts/rename_font_metadata.py --check fonts/NamcheShadowSans
	$(MAKE) copy-npm-fonts

copy-npm-fonts:
	# Clear any pre-existing build artifacts
	rm -rf packages/next/dist/fonts
	# Copy over the relevant font files
	mkdir -p packages/next/dist/fonts/namche-shadow-sans packages/next/dist/fonts/namche-shadow-mono packages/next/dist/fonts/namche-shadow-pixel
	cp fonts/NamcheShadowSans/ttf/*.ttf packages/next/dist/fonts/namche-shadow-sans/
	cp fonts/NamcheShadowSans/webfonts/*.woff2 packages/next/dist/fonts/namche-shadow-sans/
	cp fonts/NamcheShadowMono/ttf/*.ttf packages/next/dist/fonts/namche-shadow-mono/
	cp fonts/NamcheShadowMono/webfonts/*.woff2 packages/next/dist/fonts/namche-shadow-mono/
	cp fonts/NamcheShadowMono/variable/*.ttf packages/next/dist/fonts/namche-shadow-mono/
	cp fonts/NamcheShadowPixel/webfonts/*.woff2 packages/next/dist/fonts/namche-shadow-pixel/
	# Apparently there is a naming mismatch between the font files for npm distribution and the actual font files,
	# so we need to rename them to the correct names.
	cd packages/next/dist/fonts/namche-shadow-sans && \
		mv NamcheShadowSans-ExtraLight.ttf NamcheShadowSans-UltraLight.ttf && \
		mv NamcheShadowSans-ExtraLight.woff2 NamcheShadowSans-UltraLight.woff2 && \
		mv NamcheShadowSans-ExtraLightItalic.ttf NamcheShadowSans-UltraLightItalic.ttf && \
		mv NamcheShadowSans-ExtraLightItalic.woff2 NamcheShadowSans-UltraLightItalic.woff2 && \
		mv NamcheShadowSans-Black.ttf NamcheShadowSans-UltraBlack.ttf && \
		mv NamcheShadowSans-Black.woff2 NamcheShadowSans-UltraBlack.woff2 && \
		mv NamcheShadowSans-ExtraBold.ttf NamcheShadowSans-Black.ttf && \
		mv NamcheShadowSans-ExtraBold.woff2 NamcheShadowSans-Black.woff2 && \
		mv NamcheShadowSans-BlackItalic.ttf NamcheShadowSans-UltraBlackItalic.ttf && \
		mv NamcheShadowSans-BlackItalic.woff2 NamcheShadowSans-UltraBlackItalic.woff2 && \
		mv NamcheShadowSans-ExtraBoldItalic.ttf NamcheShadowSans-BlackItalic.ttf && \
		mv NamcheShadowSans-ExtraBoldItalic.woff2 NamcheShadowSans-BlackItalic.woff2
	cd packages/next/dist/fonts/namche-shadow-mono && \
		mv NamcheShadowMono-ExtraLight.ttf NamcheShadowMono-UltraLight.ttf && \
		mv NamcheShadowMono-ExtraLight.woff2 NamcheShadowMono-UltraLight.woff2 && \
		mv NamcheShadowMono-ExtraBold.ttf NamcheShadowMono-UltraBlack.ttf && \
		mv NamcheShadowMono-ExtraBold.woff2 NamcheShadowMono-UltraBlack.woff2 && \
		mv 'NamcheShadowMono[wght].ttf' NamcheShadowMono-Variable.ttf && \
		mv 'NamcheShadowMono[wght].woff2' NamcheShadowMono-Variable.woff2

create-release-zip:
	mkdir -p namche-shadow-font
	cp -r fonts/* namche-shadow-font/
	cp documentation/DESCRIPTION.en_us.html namche-shadow-font/ || true
	cp documentation/article/ARTICLE.en_us.html namche-shadow-font/ || true
	cp OFL.txt namche-shadow-font/
	zip -r namche-shadow-font.zip namche-shadow-font
	rm -rf namche-shadow-font

venv/touchfile: requirements.txt
	test -d venv || python3 -m venv venv
	. venv/bin/activate; pip install -Ur requirements.txt
	touch venv/touchfile

# Namche Shadow Pixel's virtual-master support only exists in an unreleased gftools dev
# build (Simon Cozens' fix). Pin the exact commit for reproducibility; revisit
# once it ships in an official gftools release and we can fold it into venv.
GFTOOLS_PIXEL_REF = 47ec3706b

venv-pixel/touchfile: Makefile
	test -d venv-pixel || python3 -m venv venv-pixel
	. venv-pixel/bin/activate; pip install "gftools @ git+https://github.com/googlefonts/gftools@$(GFTOOLS_PIXEL_REF)"
	touch venv-pixel/touchfile

test: build.stamp
	which fontspector || (echo "fontspector not found. Please install it with 'cargo install fontspector'." && exit 1)
	TOCHECK=$$(find fonts/NamcheShadowSans/ttf -type f 2>/dev/null); mkdir -p out/ out/fontspector; fontspector --profile googlefonts -l warn --full-lists --succinct --json out/fontspector/NamcheShadowSans-fontspector-report.json --badges out/badges $$TOCHECK  || echo '::warning file=sources/config-NamcheShadowSans.yaml,title=fontspector failures::The fontspector QA check reported errors in your font. Please check the generated report.'
	TOCHECK=$$(find fonts/NamcheShadowMono/variable -type f 2>/dev/null); mkdir -p out/ out/fontspector; fontspector --profile googlefonts -l warn --full-lists --succinct --json out/fontspector/NamcheShadowMonoVF-fontspector-report.json --badges out/badges $$TOCHECK  || echo '::warning file=sources/config-NamcheShadowMono.yaml,title=fontspector failures::The fontspector QA check reported errors in your font. Please check the generated report.'
	TOCHECK=$$(find fonts/NamcheShadowMono/ttf -type f 2>/dev/null); mkdir -p out/ out/fontspector; fontspector --profile googlefonts -l warn --full-lists --succinct --json out/fontspector/NamcheShadowMono-fontspector-report.json --badges out/badges $$TOCHECK  || echo '::warning file=sources/config-NamcheShadowMono.yaml,title=fontspector failures::The fontspector QA check reported errors in your font. Please check the generated report.'
	TOCHECK=$$(find fonts/NamcheShadowPixel/ttf -type f 2>/dev/null); mkdir -p out/ out/fontspector; fontspector --profile googlefonts -l warn --full-lists --succinct --json out/fontspector/NamcheShadowPixel-fontspector-report.json --badges out/badges $$TOCHECK  || echo '::warning file=sources/config-NamcheShadowPixel.yaml,title=fontspector failures::The fontspector QA check reported errors in your font. Please check the generated report.'

proof: venv build.stamp
	TOCHECK=$$(find fonts/NamcheShadowSans/variable -type f 2>/dev/null); if [ -z "$$TOCHECK" ]; then TOCHECK=$$(find fonts/NamcheShadowSans/ttf -type f 2>/dev/null); fi ; . venv/bin/activate; mkdir -p out/ out/proof; diffenator2 proof $$TOCHECK -o out/proof

images: venv $(DRAWBOT_OUTPUT)

%.png: %.py build.stamp
	. venv/bin/activate; python3 $< --output $@

clean:
	rm -rf venv venv-pixel
	find . -name "*.pyc" -delete

update-project-template:
	npx update-template https://github.com/googlefonts/googlefonts-project-template/

update: venv
	venv/bin/pip install --upgrade pip-tools
	# See https://pip-tools.readthedocs.io/en/latest/#a-note-on-resolvers for
	# the `--resolver` flag below.
	venv/bin/pip-compile --upgrade --verbose --resolver=backtracking requirements.in
	venv/bin/pip-sync requirements.txt

	git commit -m "Update requirements" requirements.txt
	git push
