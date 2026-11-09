// The picture link previews show (Open Graph and X/Twitter): 1200×630, the mark,
// the name and the tagline on the brand cream. It's drawn at build time from
// consts.ts, so a rename updates it too. Text is turned into outlines with the
// app's fonts (OFL, src/assets/fonts), so it looks the same wherever it's built.
import { readFileSync } from 'node:fs';
import { join } from 'node:path';
import type { APIRoute } from 'astro';
import opentype from 'opentype.js';
import sharp from 'sharp';
import { BRAND_NAME, TAGLINE } from '../consts';

const WIDTH = 1200;
const HEIGHT = 630;
const CREAM = '#f4efe9';
const CHARCOAL = '#212121';
const MUTED = '#6b625a';

function loadFont(file: string) {
	const buffer = readFileSync(join(process.cwd(), 'src/assets/fonts', file));
	return opentype.parse(buffer.buffer.slice(buffer.byteOffset, buffer.byteOffset + buffer.byteLength));
}

// Glyph by glyph with kerning. opentype.js can't read some of Hanken Grotesk's
// substitution tables, so its own text layout isn't used.
function textPath(font: opentype.Font, text: string, size: number) {
	const scale = size / font.unitsPerEm;
	const glyphs = Array.from(text, (char) => font.charToGlyph(char));
	const advances = glyphs.map(
		(glyph, i) => (glyph.advanceWidth ?? 0) * scale + (glyphs[i + 1] ? font.getKerningValue(glyph, glyphs[i + 1]) * scale : 0),
	);
	const width = advances.reduce((sum, advance) => sum + advance, 0);
	return {
		width,
		/** The path with its baseline at y and centred on the image. */
		at(y: number) {
			let x = (WIDTH - width) / 2;
			return glyphs
				.map((glyph, i) => {
					const data = glyph.getPath(x, y, size).toPathData(2);
					x += advances[i];
					return data;
				})
				.join('');
		},
	};
}

export const GET: APIRoute = async () => {
	const display = loadFont('Fraunces-Medium.ttf');
	const body = loadFont('HankenGrotesk.ttf');

	// Shrink a long name or tagline to fit the width, rather than clip it.
	const fit = (font: opentype.Font, text: string, size: number, max: number) => {
		const path = textPath(font, text, size);
		return path.width <= max ? path : textPath(font, text, (size * max) / path.width);
	};
	const name = fit(display, BRAND_NAME, 132, 1040);
	const tagline = fit(body, TAGLINE, 46, 1040);

	// src/assets/mark.svg, 87×85 in its own units, scaled to 168 px tall.
	const markHeight = 168;
	const markScale = markHeight / 85;
	const markX = (WIDTH - 87 * markScale) / 2;

	const svg = `<svg xmlns="http://www.w3.org/2000/svg" width="${WIDTH}" height="${HEIGHT}" viewBox="0 0 ${WIDTH} ${HEIGHT}">
	<rect width="100%" height="100%" fill="${CREAM}"/>
	<g transform="translate(${markX} 96) scale(${markScale}) translate(-9 -6)" color="${CHARCOAL}">
		<path d="M19 55C32 64 45 50 53 34C59 22 58 11 50 11C40 11 36 27 36 44C36 62 34 84 22 85C9 86 11 67 29 68C43 69 54 79 71 71" fill="none" stroke="currentColor" stroke-width="6.5" stroke-linecap="round"/>
		<path d="M83 47Q85 56 94 59Q85 62 83 71Q81 62 72 59Q81 56 83 47Z" fill="currentColor"/>
	</g>
	<path d="${name.at(418)}" fill="${CHARCOAL}"/>
	<path d="${tagline.at(500)}" fill="${MUTED}"/>
</svg>`;

	const png = await sharp(Buffer.from(svg)).png().toBuffer();
	return new Response(new Uint8Array(png), { headers: { 'Content-Type': 'image/png' } });
};
