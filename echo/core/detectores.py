"""F1b — las 10 fichas aprobadas como detectores deterministas (sin LLM).

corregir(texto) -> (texto_corregido, [(ficha_id, original, corregido), ...])

Cada regla dice lo mismo que su ficha (regla_es) y sólo actúa cuando el patrón es inequívoco;
ante la duda no toca nada (lo que no cubra lo corrige el LLM en el brazo e).
Desarrollo SÓLO con la biblioteca y frases trampa propias (PREREGISTRO_F1b.md); nunca con los bancos.
"""
import re

# ------------------------------------------------------------------ léxico verbal: base -> (3sg, pasado)
_IRREG = {
    "be": ("is", "was"), "have": ("has", "had"), "do": ("does", "did"), "go": ("goes", "went"),
    "come": ("comes", "came"), "give": ("gives", "gave"), "make": ("makes", "made"), "take": ("takes", "took"),
    "see": ("sees", "saw"), "eat": ("eats", "ate"), "buy": ("buys", "bought"), "sell": ("sells", "sold"),
    "feed": ("feeds", "fed"), "get": ("gets", "got"), "run": ("runs", "ran"), "bring": ("brings", "brought"),
    "say": ("says", "said"), "tell": ("tells", "told"), "think": ("thinks", "thought"), "write": ("writes", "wrote"),
    "drive": ("drives", "drove"), "grow": ("grows", "grew"), "catch": ("catches", "caught"), "find": ("finds", "found"),
    "leave": ("leaves", "left"), "put": ("puts", "put"), "cut": ("cuts", "cut"), "sleep": ("sleeps", "slept"),
    "fall": ("falls", "fell"), "know": ("knows", "knew"), "begin": ("begins", "began"), "drink": ("drinks", "drank"),
    "ride": ("rides", "rode"), "teach": ("teaches", "taught"), "build": ("builds", "built"), "send": ("sends", "sent"),
    "spend": ("spends", "spent"), "meet": ("meets", "met"), "lose": ("loses", "lost"), "pay": ("pays", "paid"),
    "keep": ("keeps", "kept"), "feel": ("feels", "felt"), "sit": ("sits", "sat"), "stand": ("stands", "stood"),
    "swim": ("swims", "swam"), "sing": ("sings", "sang"), "speak": ("speaks", "spoke"), "wake": ("wakes", "woke"),
    "wear": ("wears", "wore"), "win": ("wins", "won"), "hear": ("hears", "heard"), "hold": ("holds", "held"),
    "read": ("reads", "read"), "understand": ("understands", "understood"), "forget": ("forgets", "forgot"),
    "break": ("breaks", "broke"), "choose": ("chooses", "chose"), "fly": ("flies", "flew"), "hide": ("hides", "hid"),
    "lend": ("lends", "lent"), "light": ("lights", "lit"), "shut": ("shuts", "shut"), "set": ("sets", "set"),
    "hit": ("hits", "hit"), "let": ("lets", "let"), "become": ("becomes", "became"), "blow": ("blows", "blew"),
    "draw": ("draws", "drew"), "freeze": ("freezes", "froze"), "shake": ("shakes", "shook"), "steal": ("steals", "stole"),
    "throw": ("throws", "threw"), "dig": ("digs", "dug"), "feel": ("feels", "felt"), "bite": ("bites", "bit"),
}
_REG = """work live like want need help call clean cook wash plant pick harvest milk visit open close start finish
play watch talk ask answer learn study travel walk arrive stay move carry fix repair check collect prepare
change use love hate wait listen look dance clean paint rain plow water sow vaccinate deliver receive
order serve install connect print save earn improve protect explain practice return visit cross enjoy
attend pass count fill boil fry bake mix pour weigh pack load climb guide show finish hire order""".split()


def _3sg(v):
    if v.endswith(("s", "sh", "ch", "x", "z", "o")):
        return v + "es"
    if v.endswith("y") and v[-2:-1] not in "aeiou":
        return v[:-1] + "ies"
    return v + "s"


def _past(v):
    if v.endswith("e"):
        return v + "d"
    if v.endswith("y") and v[-2:-1] not in "aeiou":
        return v[:-1] + "ied"
    if v in ("plan", "stop", "drop", "shop", "chat", "plug", "jog", "mop", "rob", "hug", "skip"):
        return v + v[-1] + "ed"
    return v + "ed"


VERBOS = dict(_IRREG)
for _v in _REG:
    VERBOS.setdefault(_v, (_3sg(_v), _past(_v)))
TERCERA = {t: b for b, (t, p) in VERBOS.items()}
PASADOS = {p for b, (t, p) in VERBOS.items()}
# verbos que también son sustantivos frecuentes: no se tocan en reglas ambiguas
_AMBIGUOS = {"work", "help", "use", "change", "love", "water", "plant", "milk", "harvest", "order", "rain", "paint",
             "look", "call", "visit", "start", "finish", "study", "play", "walk", "dance", "travel", "pass", "fly",
             "light", "set", "hit", "show", "guide", "load", "pack", "fill", "count", "return", "practice", "drink",
             "cut", "run", "fall", "sleep", "dig", "read", "check", "wait", "answer", "plow", "print", "save"}

# ------------------------------------------------------------------ sujetos
_PRON_3 = r"(?:[Hh]e|[Ss]he|[Ii]t)"
_DET = r"(?:[Mm]y|[Hh]is|[Hh]er|[Oo]ur|[Yy]our|[Tt]heir|[Tt]he|[Tt]his|[Tt]hat|[Ee]very)"
_KIN = (r"(?:father|mother|dad|mom|son|daughter|brother|sister|uncle|aunt|cousin|grandfather|grandmother|grandma|"
        r"grandpa|wife|husband|boss|neighbor|neighbour|friend|teacher|baby|boy|girl|farmer|cook|chef|doctor|nurse|"
        r"driver|guide|engineer|mechanic|instructor|student|partner|family|company|store|shop|farm|cow|dog|cat|"
        r"horse|machine|tractor|truck|bus|car|engine|computer|printer|school|restaurant|hotel|town|village|river)")
_NO_NOMBRE = (r"(?!(?:Last|Yesterday|Today|Tomorrow|Every|Monday|Tuesday|Wednesday|Thursday|Friday|Saturday|Sunday|"
              r"January|February|March|April|May|June|July|August|September|October|November|December|In|On|At|"
              r"The|This|That|These|Those|My|Your|Our|His|Her|Their|And|But|So|Then|Now|Here|There|When|If|"
              r"Because|Please|Sorry|Hello|Hi|Yes|No|Actually|Currently|Boss|Teacher|Sir|Madam)\b)")
_SUJ_3 = rf"(?:{_PRON_3}|{_DET} {_KIN}|{_NO_NOMBRE}[A-Z][a-z]+(?= ))"


def _sub(rx, f, t):
    """Como rx.sub, pero si un candidato no cambia se reintenta desde la palabra siguiente (no se lo come)."""
    i = 0
    while True:
        m = rx.search(t, i)
        if not m:
            return t
        nuevo = f(m)
        if nuevo == m.group(0):
            sp = t.find(" ", m.start() + 1)
            if sp < 0:
                return t
            i = sp + 1
        else:
            t = t[: m.start()] + nuevo + t[m.end():]
            i = m.start() + len(nuevo)
_ADV = r"(?:(?:always|usually|never|often|sometimes|also|still|only|really|normally|generally) )?"
_SUJ_PL = r"(?:[Ww]e|[Yy]ou|[Tt]hey|[Pp]eople)"
_PASADO_MARCA = re.compile(r"\b(yesterday|last (?:night|week|month|year|monday|tuesday|wednesday|thursday|friday|"
                           r"saturday|sunday|weekend|time|harvest|season)|\d+ (?:days?|weeks?|months?|years?) ago|ago|"
                           r"in (?:19|20)\d\d)\b", re.I)
_NUM = (r"(?:\d+|one|two|three|four|five|six|seven|eight|nine|ten|eleven|twelve|thirteen|fourteen|fifteen|sixteen|"
        r"seventeen|eighteen|nineteen|twenty(?:[- ]\w+)?|thirty(?:[- ]\w+)?|forty(?:[- ]\w+)?|fifty(?:[- ]\w+)?|"
        r"sixty(?:[- ]\w+)?|seventy(?:[- ]\w+)?|eighty(?:[- ]\w+)?|ninety(?:[- ]\w+)?|a hundred)")

_ADJ = set("""big small little large tall short long new old young red white black green blue yellow brown gray grey
orange pink purple beautiful ugly cold hot warm fresh clean dirty cheap expensive good bad nice happy sad strong
weak heavy light fast slow high low dark bright sweet sour delicious tired sick fat thin wide narrow deep quiet
noisy rich poor modern traditional organic ripe dry wet soft hard empty full wooden metal plastic electric""".split())


def _be(suj):
    s = suj.lower()
    if s == "i":
        return "am"
    if s in ("you", "we", "they") or s.endswith("s") and not s.endswith(("ss", "us")):
        return "are"
    return "is"


# ------------------------------------------------------------------ reglas (cada una: regex + reemplazo)
def _r_edad(t, out):
    rx = re.compile(rf"\b(?P<suj>I|[Yy]ou|[Ww]e|[Tt]hey|{_SUJ_3}|{_DET} \w+|[Mm]y \w+ \w+) (?P<v>have|has) "
                    rf"(?P<n>{_NUM}) (?P<y>years?)(?P<old> old)?\b(?! (?:of|ago|in|working|studying|here|there)\b)")

    def f(m):
        nuevo = f"{m['suj']} {_be(m['suj'])} {m['n']} {m['y']} old"
        out.append(("edad_have", m.group(0), nuevo))
        return nuevo
    t = _sub(rx, f, t)
    rx2 = re.compile(r"\b[Hh]ow many years (?P<v>have|has|do|does) (?P<suj>you|he|she|it|they|we|your \w+|his \w+|"
                     r"her \w+|my \w+|the \w+|[A-Z][a-z]+)(?: have)?\?")

    def f2(m):
        nuevo = f"How old {_be(m['suj']) if m['suj'].lower() != 'you' else 'are'} {m['suj']}?"
        out.append(("edad_have", m.group(0), nuevo))
        return nuevo
    return _sub(rx2, f2, t)


def _r_people(t, out):
    cambia = {"is": "are", "was": "were", "has": "have", "does": "do", "doesn't": "don't", "isn't": "aren't",
              "wasn't": "weren't"}
    rx = re.compile(r"\b(?P<p>[Pp]eople) " + _ADV + r"(?P<v>is|was|has|does|doesn't|isn't|wasn't|\w+s)\b")

    def f(m):
        v = m["v"]
        if v in cambia:
            nv = cambia[v]
        elif v in TERCERA:
            nv = TERCERA[v]
        else:
            return m.group(0)
        nuevo = m.group(0)[: -len(v)] + nv
        out.append(("people_plural", m.group(0), nuevo))
        return nuevo
    return _sub(rx, f, t)


def _r_negacion(t, out):
    pasado = bool(_PASADO_MARCA.search(t))
    rx = re.compile(rf"\b(?P<suj>I|[Yy]ou|[Ww]e|[Tt]hey|[Pp]eople|{_SUJ_3}|{_DET} \w+ \w+|{_DET} \w+) "
                    rf"(?P<neg>not|no) (?P<v>\w+)\b")

    def f(m):
        v = m["v"].lower()
        if v in TERCERA:
            v = TERCERA[v]
        if v not in VERBOS or v == "be":
            return m.group(0)
        s = m["suj"]
        if pasado:
            aux = "didn't"
        elif re.fullmatch(_SUJ_3, s) or (re.fullmatch(rf"{_DET} [\w ]+", s) and not s.endswith("s")):
            aux = "doesn't"
        else:
            aux = "don't"
        nuevo = f"{s} {aux} {v}"
        out.append(("do_negacion", m.group(0), nuevo))
        return nuevo
    return _sub(rx, f, t)


def _r_pasado(t, out):
    if not _PASADO_MARCA.search(t):
        return t
    # verbo en presente justo después de un sujeto (no tras to / modal / auxiliar)
    rx = re.compile(rf"\b(?P<suj>I|[Yy]ou|[Ww]e|[Tt]hey|[Pp]eople|{_SUJ_3}|{_DET} \w+|{_DET} \w+ \w+) {_ADV}(?P<v>[a-z]+)\b")

    def f(m):
        v = m["v"]
        base = TERCERA.get(v, v)
        if base not in VERBOS or v in PASADOS or base == "be":
            return m.group(0)
        if base in _AMBIGUOS and v == base and re.fullmatch(rf"{_DET} \w+ \w+", m["suj"]):
            return m.group(0)
        nuevo = m.group(0)[: -len(v)] + VERBOS[base][1]
        out.append(("pasado_irregular", m.group(0), nuevo))
        return nuevo
    t = _sub(rx, f, t)
    # coordinado: "... and sell" tras un verbo ya en pasado ("planted corn and sell it")
    rx2 = re.compile(r"\b(?P<y>and|then) (?P<v>[a-z]+)\b")

    def f2(m):
        base = TERCERA.get(m["v"], m["v"])
        if base not in VERBOS or base in _AMBIGUOS or base == "be" or m["v"] in PASADOS:
            return m.group(0)
        prev = t[: m.start()].split()
        if not prev or not any(w.strip(".,").lower() in PASADOS for w in prev[-6:]):
            return m.group(0)
        nuevo = f"{m['y']} {VERBOS[base][1]}"
        out.append(("pasado_irregular", m.group(0), nuevo))
        return nuevo
    return _sub(rx2, f2, t)


def _r_3sg(t, out):
    if _PASADO_MARCA.search(t):
        return t
    rx = re.compile(rf"(?<![Tt]o )(?<!\w)(?P<suj>{_SUJ_3}|{_DET} [a-z]+(?<!s)) {_ADV}(?P<v>[a-z]+)\b(?! (?:to|you)\b)")

    def f(m):
        v = m["v"]
        if v not in VERBOS or v == "be":
            return m.group(0)
        antes = t[: m.start()].rstrip().split()
        if antes and antes[-1].lower().strip(",") in ("and", "or", "&", "of", "with") and \
                not re.fullmatch(_PRON_3, m["suj"]):
            return m.group(0)  # sujeto compuesto ("my mother and my sister cook") o complemento
        if antes and antes[-1].lower() in ("is", "are", "was", "were", "do", "does", "did", "can", "could", "will",
                                           "would", "should", "may", "might", "must", "let", "make", "help", "see",
                                           "watch", "hear", "keep", "have", "had", "has"):
            return m.group(0)  # pregunta invertida ("Is the store open?") o verbo + objeto + base
        if not re.fullmatch(_SUJ_3, m["suj"]):
            # sustantivo libre como sujeto: sólo verbos inequívocos y sólo al inicio de la oración
            # (retenidas 4-nov: "Is the store open", "keep the kitchen clean" eran objeto/adjetivo)
            if v in _AMBIGUOS or v in _ADJ or m["suj"].split()[-1] in _ADJ:
                return m.group(0)
            if antes and not re.search(r"[.!?;,]$", antes[-1]) and antes[-1].lower() not in (
                    "because", "but", "so", "when", "if", "now", "today", "then"):
                return m.group(0)
        if m["suj"][0].isupper() and m.start() == 0 and m["suj"] not in ("He", "She", "It") and \
                not re.fullmatch(rf"{_DET} {_KIN}", m["suj"]):
            return m.group(0)  # palabra inicial con mayúscula que no sabemos si es un nombre
        if v in _AMBIGUOS and not re.fullmatch(_PRON_3, m["suj"]):
            return m.group(0)
        nv = VERBOS[v][0]
        nuevo = m.group(0)[: -len(v)] + nv
        out.append(("concordancia_3sg", m.group(0), nuevo))
        return nuevo
    return _sub(rx, f, t)


def _r_sujeto(t, out):
    rx = re.compile(r"(?P<pre>^|[.!?] |\b(?:because|but|and|so|when|if) |, )(?P<v>[Ii]s|[Ww]as) "
                    r"(?P<sig>very|too|so|really|important|necessary|possible|difficult|easy|hot|cold|warm|sunny|"
                    r"cloudy|raining|windy|late|early|expensive|cheap|beautiful|nice|good|bad|far|near|dangerous|"
                    r"[a-z]+ing\b(?<!thing))")

    def f(m):
        if "?" in t[m.start():].split(".")[0]:
            return m.group(0)
        it = "It" if m["pre"] in ("", ". ", "! ", "? ") else "it"
        nuevo = f"{m['pre']}{it} {m['v'].lower()} {m['sig']}"
        out.append(("sujeto_omitido", m.group(0).strip(), nuevo.strip()))
        return nuevo
    return _sub(rx, f, t)


_A_EXC = {"university", "uniform", "union", "unit", "user", "useful", "usual", "one", "once", "european", "euro",
          "unique", "unicorn", "ewe", "eucalyptus"}
_AN_EXC = {"hour", "hours", "honest", "honor", "honour", "heir", "herb"}


def _r_a_an(t, out):
    rx = re.compile(r"\b(?P<a>[Aa]n?) (?P<w>[A-Za-z][\w'-]*)")

    def f(m):
        a, w = m["a"], m["w"]
        wl = w.lower()
        vocal = (wl[0] in "aeiou" and wl not in _A_EXC and not wl.startswith(("uni", "use", "eu"))) or wl in _AN_EXC
        quiere = "an" if vocal else "a"
        if a.lower() == quiere:
            return m.group(0)
        nuevo = (quiere.capitalize() if a[0].isupper() else quiere) + " " + w
        out.append(("articulo_a_an", m.group(0), nuevo))
        return nuevo
    return _sub(rx, f, t)


_NO_SUST = {"lot", "bit", "little", "few", "very", "really", "so", "too", "more", "most", "is", "are", "was", "and",
            "or", "but", "of", "in", "on", "at", "to", "for", "with"} | _ADJ
_RESULTATIVOS = {"paint", "painted", "paints", "make", "made", "makes", "keep", "kept", "keeps", "get", "got", "gets",
                 "turn", "turned", "turns", "leave", "left", "leaves", "find", "found", "finds", "like", "likes",
                 "want", "wants", "prefer", "prefers", "eat", "eats", "drink", "drinks", "serve", "serves", "sell",
                 "sells", "buy", "buys", "need", "needs"}
_RES_FUERTES = {"paint", "painted", "paints", "make", "made", "makes", "keep", "kept", "keeps", "turn", "turned",
                "turns", "get", "got", "gets"}
_COPULAS = {"is", "are", "was", "were", "be", "been", "seem", "seems", "look", "looks", "feel", "feels"}


def _r_orden(t, out):
    rx = re.compile(r"\b(?P<det>[Aa]n?|[Tt]he|[Mm]y|[Oo]ur|[Hh]is|[Hh]er|[Tt]heir|[Tt]his|[Tt]hat|[Oo]ne|[Tt]wo|[Tt]hree|"
                    r"[Mm]any|[Ss]ome) (?P<n>[a-z]+) (?P<adj>[a-z]+)(?P<fin>\s*(?:[.,!?;]|$| and\b| of\b| for\b| with\b|"
                    r" in\b| on\b| near\b| from\b| to\b| that\b| here\b| there\b))")

    def f(m):
        if m["adj"] not in _ADJ or m["n"] in _NO_SUST or m["n"].endswith("ly"):
            return m.group(0)
        resto = t[m.end():].split()
        if m["fin"].strip() == "and" and resto and resto[0].strip(".,!?") in _ADJ:
            return m.group(0)  # "a cow black and white": dos adjetivos, lo deja al LLM
        prev = t[: m.start()].split()
        excl = _RES_FUERTES if m["det"].lower() in ("a", "an") else _RESULTATIVOS
        if prev and prev[-1].lower().strip(",") in excl | _COPULAS:
            return m.group(0)  # "paint the house red", "keep the room clean", "I like my coffee hot"
        nuevo = f"{m['det']} {m['adj']} {m['n']}{m['fin']}"  # el artículo a/an lo arregla su regla después
        out.append(("orden_adjetivo", m.group(0).rstrip(), nuevo.rstrip()))
        return nuevo
    t = _sub(rx, f, t)
    # plural sin determinante tras un verbo de tener/vender/ver: "have cherries red" -> "have red cherries"
    rx2 = re.compile(r"\b(?P<v>have|has|had|sell|sells|sold|buy|buys|bought|see|sees|saw|grow|grows|grew) "
                     r"(?P<n>[a-z]+s) (?P<adj>[a-z]+)(?P<fin>\s*(?:[.,!?;]|$| and\b| in\b| on\b| for\b| from\b))")

    def f2(m):
        if m["adj"] not in _ADJ or m["n"] in _NO_SUST:
            return m.group(0)
        nuevo = f"{m['v']} {m['adj']} {m['n']}{m['fin']}"
        out.append(("orden_adjetivo", m.group(0).rstrip(), nuevo.rstrip()))
        return nuevo
    return _sub(rx2, f2, t)


def _r_falso(t, out):
    rx = re.compile(r"(?:(?<=^)|(?<=[.!?] ))Actually (?!,)(?=[A-Za-z])")
    if rx.search(t):
        oracion = rx.split(t, maxsplit=1)[1].split(".")[0].lower()
        if not re.search(r"\b(but|not|n't|no|never|think|thought|believe|true|real|really|wrong|right)\b", oracion):
            t = rx.sub("Currently ", t, count=1)
            out.append(("falso_cognado", "Actually", "Currently"))
    for mal, bien in ((r"\b[Aa]ssist(?:s|ed)? to\b", None), (r"\bsensible to\b", "sensitive to")):
        def f(m, bien=bien):
            s = m.group(0)
            if bien is None:
                verbo = s.split()[0]
                b = {"assist": "attend", "Assist": "Attend", "assists": "attends", "assisted": "attended",
                     "Assists": "Attends", "Assisted": "Attended"}[verbo]
            else:
                b = bien
            out.append(("falso_cognado", s, b))
            return b
        t = re.sub(mal, f, t)
    return t


def _r_para(t, out):
    rx = re.compile(r"\b(?P<f>[Ff]or) (?P<v>[a-z]+)\b(?! (?:of|is|are|was)\b)")

    def f(m):
        v = m["v"]
        if v not in VERBOS or v in _AMBIGUOS or v in ("be",):
            return m.group(0)
        nuevo = ("To" if m["f"][0] == "F" else "to") + " " + v
        out.append(("para_infinitivo", m.group(0), nuevo))
        return nuevo
    return _sub(rx, f, t)


# orden: primero lo léxico de frase completa, al final el artículo (puede cambiar tras mover el adjetivo)
REGLAS = [_r_falso, _r_edad, _r_people, _r_negacion, _r_pasado, _r_3sg, _r_sujeto, _r_para, _r_orden, _r_a_an]


def corregir(texto):
    out = []
    t = " ".join(str(texto).split())
    for r in REGLAS:
        t = r(t, out)
    return t, out
