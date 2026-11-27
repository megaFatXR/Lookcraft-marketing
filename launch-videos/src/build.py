#!/usr/bin/env python3
"""Renders the launch wipe videos: two 15 s reels (him, her) in EN and ES, plus 6 s single wipes as B-roll.
Still layers come from layer.html through headless Chrome; ffmpeg does the wipes, fades and encoding."""
import json, os, subprocess, sys, urllib.parse

HERE = os.path.dirname(os.path.abspath(__file__))
LAYERS = os.path.join(HERE, 'layers')
OUT = os.path.dirname(HERE)  # launch-videos/
CHROME = '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome'
FPS = 30
os.makedirs(LAYERS, exist_ok=True)
os.makedirs(OUT, exist_ok=True)


def layer(name, spec, w, h, transparent=False):
	path = os.path.join(LAYERS, name + '.png')
	if os.path.exists(path) and '--fresh' not in sys.argv:
		return path
	url = 'file://' + os.path.join(HERE, 'layer.html') + '#' + urllib.parse.quote(json.dumps(spec))
	args = [CHROME, '--headless=new', '--disable-gpu', '--hide-scrollbars', '--force-device-scale-factor=1',
		'--allow-file-access-from-files', '--virtual-time-budget=3000', f'--window-size={w},{h}', f'--screenshot={path}']
	if transparent:
		args.append('--default-background-color=00000000')
	subprocess.run(args + [url], check=True, stderr=subprocess.DEVNULL, stdout=subprocess.DEVNULL)
	return path


# Title change: fade out to the cream band colour, then the new title in (gbrp planes: G, B, R of #f4efe9).
DIP = "st(2,if(eq(PLANE,0),239,if(eq(PLANE,1),233,244)));if(gt(P,0.5),A+(ld(2)-A)*(1-P)*2,B+(ld(2)-B)*P*2)"

# Left-to-right wipe with eased progress and a white line at the edge (planes are RGB, so 255 is white).
WIPE = "st(0,1-P);st(1,ld(0)*ld(0)*(3-2*ld(0))*W);if(lt(abs(X-ld(1)),3),255,if(gt(X,ld(1)),A,B))"


def chain(inputs, starts, kind, dur, label):
	"""xfade a list of input labels; starts[i] is when transition i (into clip i+1) begins."""
	parts, cur = [], inputs[0]
	for i, nxt in enumerate(inputs[1:]):
		out = f'{label}{i}'
		k = kind[i] if isinstance(kind, list) else kind
		d = dur[i] if isinstance(dur, list) else dur
		kind_, dur_ = kind, dur
		kind, dur = k, d
		if kind == 'wipe':
			parts.append(f'[{cur}][{nxt}]xfade=transition=custom:expr=\'{WIPE}\':duration={dur}:offset={starts[i]:.3f}[{out}]')
		elif kind == 'dip':
			parts.append(f'[{cur}][{nxt}]xfade=transition=custom:expr=\'{DIP}\':duration={dur}:offset={starts[i]:.3f}[{out}]')
		else:
			parts.append(f'[{cur}][{nxt}]xfade=transition=fade:duration={dur}:offset={starts[i]:.3f}[{out}]')
		kind, dur = kind_, dur_
		cur = out
	return parts, cur


def lengths(starts, dur, end):
	"""Clip lengths so clip 0 runs until the first transition ends, clip i from transition i-1 to transition i's end."""
	ls, prev = [], 0.0
	for i, s in enumerate(starts):
		ls.append(s + (dur[i] if isinstance(dur, list) else dur) - prev)
		prev = s
	ls.append(end - prev)
	return ls


def encode(name, inputs, graph, final):
	cmd = ['ffmpeg', '-v', 'error', '-y']
	for path, length in inputs:
		cmd += ['-loop', '1', '-framerate', str(FPS), '-t', f'{length:.3f}', '-i', path]
	cmd += ['-filter_complex', ';'.join(graph), '-map', f'[{final}]', '-r', str(FPS), '-c:v', 'libx264', '-preset', 'slow',
		'-crf', '17', '-pix_fmt', 'yuv420p', '-movflags', '+faststart', os.path.join(OUT, name + '.mp4')]
	subprocess.run(cmd, check=True)
	print('out/' + name + '.mp4')


TEXT = {
	'en': {'photo': 'Your photo', 'ai': 'Try-on', 'shops': '{s} shops', 'free': '<em>3 free</em> try-ons to start',
		'look': 'Look {i} of 4', 'before': 'Before', 'total': 'total',
		'question': 'Which one would you pick?', 'comment': 'Tell us in the comments: <strong>1, 2, 3 or 4</strong>',
		'him': {'hook1': 'He looks ok-ish, right?', 'hook2': 'But his stylist can do better.', 'now': 'How he looks now'},
		'her': {'hook1': 'She looks ok-ish, right?', 'hook2': 'But her stylist can do better.', 'now': 'How she looks now'}},
	'es': {'photo': 'Tu foto', 'ai': 'Try-on', 'shops': '{s} tiendas', 'free': '<em>3 try-ons gratis</em> para empezar',
		'look': 'Look {i} de 4', 'before': 'Antes', 'total': 'en total',
		'question': '¿Cuál elegirías tú?', 'comment': 'Dínoslo en comentarios: <strong>1, 2, 3 o 4</strong>',
		'him': {'hook1': 'No está mal, ¿verdad?', 'hook2': 'Pero su estilista puede hacerlo mejor.', 'now': 'Así va ahora'},
		'her': {'hook1': 'No está mal, ¿verdad?', 'hook2': 'Pero su estilista puede hacerlo mejor.', 'now': 'Así va ahora'}},
}

REELS = {
	'him': {
		'base': 'him-base',
		'styles': [('him-old-money', 'Old Money Tailored', '€ 410'), ('him-grunge', 'Urban Grunge Layering', '€ 506'),
			('him-charcoal-coat', 'Urban Charcoal Coat', '€ 506'), ('him-navy-city', 'Navy City', '€ 296')],
		'pieces': (5, 5),
		'cards': [
			('right', 520, 'scene-1/coat', 'Printemps', 'Camel overcoat', '210,00 €'),
			('left', 640, 'scene-1/shirt', 'Springfield', 'Slim-fit shirt', '55,96 €'),
			('right', 770, 'scene-1/shoes', 'Clarks', 'Leather brogues', '82,50 €'),
			('left', 900, 'scene-1/sweater', 'Zara', 'Navy sweater', '29,99 €'),
			('left', 1160, 'scene-1/chinos', 'Vestirlaboral', 'Beige chinos', '31,49 €'),
		],
	},
	'her': {
		'base': 'her-base',
		'styles': [('her-boho', 'Boho Chic Autumn', '€ 394'), ('her-old-money', 'Effortless Old Money', '€ 265'),
			('her-preppy-v2', 'Classic Preppy Park', '€ 344'), ('her-western', 'Western Fringe', '€ 340')],
		'pieces': (6, 5),
		'cards': [
			('right', 520, 'scene-2/blazer', 'Zara', 'Linen blazer', '59,95 €'),
			('left', 600, 'scene-2/top', 'Mango', 'Knit V-neck top', '22,99 €'),
			('right', 770, 'scene-2/skirt', 'Zara', 'Paisley ruffle skirt', '39,95 €'),
			('left', 850, 'scene-2/belt', 'Pull&amp;Bear', 'Buckle belt', '15,99 €'),
			('left', 1100, 'scene-2/bag', 'Bimba y Lola', 'Fringe suede bag', '135,00 €'),
			('left', 1350, 'scene-2/boots', 'Camper', 'Suede ankle boots', '119,99 €'),
		],
	},
}

PH = 1380  # photo region under the 540 px text band


def reel(who, lang):
	r, t = REELS[who], TEXT[lang]
	h = t[who]
	hook = lambda second: f'<div class="hook1">{h["hook1"]}</div><div class="hook2{"" if second else " hidden"}">{h["hook2"]}</div>'
	photos = [layer(f'p-{r["base"]}-now-{lang}', {'kind': 'photo', 'src': r['base'], 'h': PH, 'sticker': h['now']}, 1080, PH)]
	bands = [layer(f'b-{who}-hook1-{lang}', {'kind': 'band', 'html': hook(False)}, 1080, 540),
		layer(f'b-{who}-hook2-{lang}', {'kind': 'band', 'html': hook(True)}, 1080, 540)]
	pieces = json.load(open(os.path.join(HERE, 'pieces', 'pieces.json')))
	for src, title, _ in r['styles']:
		look = pieces[src]
		shops = len({p['merchant'] for p in look['pieces']})
		strip = ''.join(f'<span><img src="{os.path.join(HERE, p["img"])}"></span>' for p in look['pieces'])
		photos.append(layer(f'p-{src}-{lang}', {'kind': 'photo', 'src': src, 'h': PH, 'pill': t['ai']}, 1080, PH))
		bands.append(layer(f'b-{src}-{lang}', {'kind': 'band', 'html': f'<h2>{title}</h2><p><strong>€ {round(look["total"])}</strong> · {t["shops"].format(s=shops)}</p><div class="strip">{strip}</div>'}, 1080, 540))
	inset = layer(f'inset-{who}-{lang}', {'kind': 'inset', 'src': r['base'], 'label': t['before']}, 1080, 1920, True)
	logo = layer('logo', {'kind': 'logo'}, 1080, 1920, True)
	grid = layer(f'grid-{who}-{lang}', {'kind': 'grid', 'band': f'<h2>{t["question"]}</h2><p>{t["comment"]}</p>',
		'cells': [{'src': src, 'title': title} for src, title, _ in r['styles']]}, 1080, 1920)
	end = layer(f'end-{lang}', {'kind': 'end', 'free': t['free']}, 1080, 1920)

	wipes, W = [2.6, 4.6, 6.6, 8.6], 0.6
	band_at = [1.2] + [x + 0.1 for x in wipes]
	band_kind = ['fade'] + ['dip'] * len(wipes)
	band_dur = [0.35] + [0.4] * len(wipes)
	grid_at, end_at, total_len = 10.8, 13.2, 14.8
	main_end = grid_at + 0.4
	inputs, graph = [], []
	for p, length in zip(photos, lengths(wipes, W, main_end)):
		inputs.append((p, length))
	for b, length in zip(bands, lengths(band_at, band_dur, main_end)):
		inputs.append((b, length))
	np, nb = len(photos), len(bands)
	for i in range(np):
		graph.append(f'[{i}:v]format=gbrp,setsar=1[p{i}]')
	for i in range(nb):
		graph.append(f'[{np + i}:v]format=gbrp,setsar=1[b{i}]')
	g, ptrack = chain([f'p{i}' for i in range(np)], wipes, 'wipe', W, 'pw')
	graph += g
	g, btrack = chain([f'b{i}' for i in range(nb)], band_at, band_kind, band_dur, 'bf')
	graph += g
	graph.append(f'[{btrack}][{ptrack}]vstack,format=yuva444p[s0]')
	k = np + nb
	inputs.append((inset, main_end))
	graph.append(f'[{k}:v]format=rgba,fade=in:st=3.0:d=0.35:alpha=1,fade=out:st=10.5:d=0.3:alpha=1[inset]')
	graph.append(f"[s0][inset]overlay=x='-50*max(0\\,1-(t-3.0)/0.45)^2':y=0:eval=frame[si]")
	cur = 'si'
	k = len(inputs)
	inputs.append((grid, end_at + 0.5 - grid_at))
	graph.append(f'[{cur}]format=yuv444p[main]')
	graph.append(f'[{k}:v]format=yuv444p,setsar=1[grid]')
	graph.append(f'[main][grid]xfade=transition=fade:duration=0.4:offset={grid_at}[mg]')
	k = len(inputs)
	inputs.append((logo, end_at + 0.5))
	graph.append(f'[{k}:v]format=rgba[logo]')
	graph.append('[mg][logo]overlay=0:0,format=yuv444p[ml]')
	k = len(inputs)
	inputs.append((end, total_len - end_at))
	graph.append(f'[{k}:v]format=yuv444p,setsar=1[end]')
	graph.append(f'[ml][end]xfade=transition=fade:duration=0.5:offset={end_at}[v]')
	encode(f'reel-{who}-{lang}', inputs, graph, 'v')


SHOPS = {'Uniqlo Spain': 'Uniqlo', 'ZARA España': 'Zara', 'MANGO': 'Mango', 'Printemps.com ES': 'Printemps', 'Dr. Martens - ES': 'Dr. Martens',
	'bimbaylola.com': 'Bimba y Lola', 'Sarenza.com España': 'Sarenza', 'vestirlaboral.com': 'Vestirlaboral', 'aboutyou.es': 'About You',
	'Zalando.es': 'Zalando', 'Querol.net': 'Querol', 'nencinisport.es': 'Nencini Sport', 'Wordans.es': 'Wordans', 'Amazon.es': 'Amazon',
	'ovsfashion.com': 'OVS', 'Lisas Boutique': "Lisa's Boutique"}
ORDER = ['outerwear', 'top', 'one-piece', 'bottom', 'shoes', 'accessory']
BRIEFS = {
	'him-old-money': ('An old money look', 'Un look old money', 500),
	'him-grunge': ('A rock and grunge look for the weekend', 'Un look rock y grunge para el finde', 700),
	'him-charcoal-coat': ('A streetwear look for every day', 'Un look streetwear para el día a día', 700),
	'him-navy-city': ('A look like my street-style photo', 'Un look como mi foto de street style', 400),
	'her-boho': ('A boho look', 'Un look boho', 500),
	'her-old-money': ('An old money look', 'Un look old money', 500),
	'her-preppy-v2': ('A preppy look', 'Un look preppy', 500),
	'her-western': ('A western-inspired look', 'Un look de inspiración western', 500),
}
LOOK = {
	'en': {'asked': {'him': 'He asked his stylist:', 'her': 'She asked her stylist:'}, 'upto': 'up to € {b}',
		'question': 'Would you wear it?', 'budget': {'him': '<strong>€ {t}</strong> of his € {b} budget', 'her': '<strong>€ {t}</strong> of her € {b} budget'}},
	'es': {'asked': {'him': 'Le pidió a su estilista:', 'her': 'Le pidió a su estilista:'}, 'upto': 'hasta {b} €',
		'question': '¿Te lo pondrías?', 'budget': {'him': '<strong>{t} €</strong> de un presupuesto de {b} €', 'her': '<strong>{t} €</strong> de un presupuesto de {b} €'}},
}


def look_video(src, lang):
	"""~13 s: the brief over the plain photo, the wipe to the try-on, each piece sliding in with its shop and price, then a question."""
	who = src.split('-')[0]
	r, t, lt = REELS[who], TEXT[lang], LOOK[lang]
	title = next(x[1] for x in r['styles'] if x[0] == src)
	look = json.load(open(os.path.join(HERE, 'pieces', 'pieces.json')))[src]
	items = sorted(look['pieces'], key=lambda p: ORDER.index(p['category']) if p['category'] in ORDER else 9)
	shops = len({p['merchant'] for p in items})
	total = round(look['total'])
	en, es, budget = BRIEFS[src]
	brief = en if lang == 'en' else es
	photos = [layer(f'p-{r["base"]}-now-{lang}', {'kind': 'photo', 'src': r['base'], 'h': PH, 'sticker': t[who]['now']}, 1080, PH),
		layer(f'p-{src}-{lang}', {'kind': 'photo', 'src': src, 'h': PH, 'pill': t['ai']}, 1080, PH)]
	bands = [layer(f'b-{src}-brief-{lang}', {'kind': 'band', 'html': f'<div class="ask">{lt["asked"][who]}</div><div class="bubble"><q>{brief}</q><small>{lt["upto"].format(b=budget)}</small></div>'}, 1080, 540),
		layer(f'b-{src}-name-{lang}', {'kind': 'band', 'html': f'<h2>{title}</h2><p><strong>€ {total}</strong> · {t["shops"].format(s=shops)}</p>'}, 1080, 540),
		layer(f'b-{src}-question-{lang}', {'kind': 'band', 'html': f'<h2>{lt["question"]}</h2><p>{lt["budget"][who].format(t=total, b=budget)}</p>'}, 1080, 540)]
	gap = 142
	top0 = 1110 - (len(items) * gap) // 2
	cards = []
	for i, p in enumerate(items):
		price = p['priceText'] or f"{p['price']:.2f} €".replace('.', ',')
		cards.append(layer(f'pc-{src}-{i}', {'kind': 'pcard', 'img': os.path.join(HERE, p['img']), 'shop': SHOPS.get(p['merchant'], p['merchant']),
			'price': price, 'top': top0 + i * gap}, 1080, 1920, True))
	logo = layer('logo', {'kind': 'logo'}, 1080, 1920, True)
	end = layer(f'end-{lang}', {'kind': 'end', 'free': t['free']}, 1080, 1920)

	wipe_at, W = 2.6, 0.7
	card0, step = 3.7, 0.45
	question_at = max(9.2, card0 + step * len(items) + 1.6)
	end_at = question_at + 2.6
	total_len = end_at + 1.6
	main_end = end_at + 0.5
	inputs = [(photos[0], wipe_at + W), (photos[1], main_end - wipe_at)]
	band_at = [wipe_at + 0.15, question_at]
	inputs += list(zip(bands, lengths(band_at, 0.4, main_end)))
	graph = [f'[{i}:v]format=gbrp,setsar=1[x{i}]' for i in range(5)]
	graph.append(f"[x0][x1]xfade=transition=custom:expr='{WIPE}':duration={W}:offset={wipe_at}[ph]")
	g, band = chain(['x2', 'x3', 'x4'], band_at, 'dip', 0.4, 'bd')
	graph += g
	graph.append(f'[{band}][ph]vstack,format=yuva444p[s0]')
	cur = 's0'
	for i, card in enumerate(cards):
		k = len(inputs)
		inputs.append((card, main_end))
		st = card0 + i * step
		graph.append(f'[{k}:v]format=rgba,fade=in:st={st:.2f}:d=0.3:alpha=1[c{i}]')
		graph.append(f"[{cur}][c{i}]overlay=x='-60*max(0\\,1-(t-{st:.2f})/0.4)^2':y=0:eval=frame[s{i + 1}]")
		cur = f's{i + 1}'
	k = len(inputs)
	inputs.append((logo, main_end))
	graph.append(f'[{k}:v]format=rgba[logo]')
	graph.append(f'[{cur}][logo]overlay=0:0,format=yuv444p[main]')
	k = len(inputs)
	inputs.append((end, total_len - end_at))
	graph.append(f'[{k}:v]format=yuv444p,setsar=1[end]')
	graph.append(f'[main][end]xfade=transition=fade:duration=0.5:offset={end_at:.2f}[v]')
	encode(f'look-{src.replace("-v2", "")}-{lang}', inputs, graph, 'v')


def single(base, after, lang):
	"""6 s full-screen wipe from the plain photo to one try-on, with no text beyond the label: B-roll for the episodes."""
	t = TEXT[lang]
	a = layer(f'f-{base}-{lang}', {'kind': 'photo', 'src': base, 'h': 1920, 'pill': t['photo'], 'pillTop': 260}, 1080, 1920)
	b = layer(f'f-{after}-{lang}', {'kind': 'photo', 'src': after, 'h': 1920, 'pill': t['ai'], 'pillTop': 260}, 1080, 1920)
	inputs = [(a, 2.3), (b, 4.5)]
	graph = ['[0:v]format=gbrp,setsar=1[a]', '[1:v]format=gbrp,setsar=1[b]',
		f"[a][b]xfade=transition=custom:expr='{WIPE}':duration=0.8:offset=1.5[v]"]
	encode(f'wipe-{after.replace("-v2", "")}-{lang}', inputs, graph, 'v')


if __name__ == '__main__':
	for lang in ('en', 'es'):
		for who in ('him', 'her'):
			reel(who, lang)
	for after in ('him-old-money', 'him-grunge', 'him-charcoal-coat', 'him-navy-city'):
		for lang in ('en', 'es'):
			single('him-base', after, lang)
	for after in ('her-boho', 'her-old-money', 'her-preppy-v2', 'her-western'):
		for lang in ('en', 'es'):
			single('her-base', after, lang)
