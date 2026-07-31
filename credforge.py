#!/usr/bin/env python3
"""
CredForge — Realistic synthetic credential generator for red team operations.
Generates combolist-grade data (email:password, username:password, PII) that
matches the statistical patterns of real breaches:

  * Frequency-weighted passwords (top real-world passwords dominate the tail)
  * Per-country email domains, weighted like real registrations
  * Age-weighted birth years (1975-1995 heavy)
  * Dedup, min-length filter, reproducible seeding

100% synthetic — no data from actual breaches. For authorized testing only.

Usage (CLI):
    python3 credforge.py -n 5000 -f 1 -c br -o brazil_creds.txt
    python3 credforge.py -n 100000 -f 6 -o wordlist.txt --unique --min-length 8
    python3 credforge.py --count 100 --format 4 --country us --output pii.txt --seed 42

Usage (interactive):
    python3 credforge.py
"""

import argparse
import os
import random
import string
import sys
from datetime import datetime

VERSION = "3.0.0"

R = '\033[0m'
B = '\033[1m'
D = '\033[2m'
G = '\033[38;5;83m'
Y = '\033[38;5;214m'
Rc = '\033[38;5;196m'
C = '\033[38;5;51m'
A = '\033[38;5;198m'
K = '\033[38;5;220m'

BANNER = f"""
 {C}╔═══════════════════════════════════════════════╗{R}
 {C}║{R}                                             {C}║{R}
 {C}║{R}    {K}  ____           _   __                 {C}║{R}
 {C}║{R}    {K} / ___|_ __ __ _| | / _| ___  _ __      {C}║{R}
 {C}║{R}    {K}| |   | '__/ _` | | | |_ / _ \\| '__|    {C}║{R}
 {C}║{R}    {K}| |___| | | (_| | | |  _| (_) | |       {C}║{R}
 {C}║{R}    {K}\\____|_|  \\__,_|_| |_|  \\___/|_|       {C}║{R}
 {C}║{R}      {D}Realistic Cred Generator v3.0{R}          {C}║{R}
 {C}║{R}      {D}breach-weighted · zero deps{R}            {C}║{R}
 {C}║{R}            {D}by Adam-ZS{R}                      {C}║{R}
 {C}║{R}                                             {C}║{R}
 {C}╚═══════════════════════════════════════════════╝{R}
"""

# ─────────────────────────────────────────────────────────────────────────────
# Name databases (uniform within country; realistic top-name coverage)
# ─────────────────────────────────────────────────────────────────────────────
FIRST_NAMES = {
    'us': ['James','Robert','John','Michael','David','William','Richard','Joseph','Thomas','Christopher','Mary','Patricia','Jennifer','Linda','Barbara','Elizabeth','Susan','Jessica','Sarah','Karen','Charles','Daniel','Matthew','Anthony','Mark','Steven','Andrew','Kenneth','George','Edward','Lisa','Nancy','Betty','Margaret','Sandra','Ashley','Dorothy','Kimberly','Emily','Donna','Brian','Kevin','Jason','Jeffrey','Timothy','Ryan','Jacob','Gary','Nicholas','Eric','Michelle','Carol','Amanda','Melissa','Deborah','Stephanie','Rebecca','Sharon','Laura','Cynthia','Tyler','Brandon','Austin','Jordan','Dylan','Cody','Hunter','Cameron','Evan','Logan','Kathleen','Amy','Angela','Shirley','Anna','Brenda','Pamela','Emma','Nicole','Helen','Jose','Luis','Carlos','Juan','Miguel','Angel','Pedro','Ramon','Pablo','Diego','Maria','Carmen','Ana','Sofia','Isabella','Valentina','Gabriela','Elena','Rosa','Marta'],
    'uk': ['Oliver','George','Harry','Jack','Jacob','Charlie','Thomas','Oscar','William','James','Amelia','Olivia','Emily','Lily','Ella','Ava','Sophie','Chloe','Isla','Grace','Noah','Leo','Archie','Henry','Freddie','Theo','Arthur','Ethan','Mason','Harrison','Rose','Alice','Florence','Poppy','Daisy','Freya','Ruby','Evie','Molly','Ivy'],
    'fr': ['Antoine','Pierre','Jean','Michel','Andre','Philippe','Nicolas','Christophe','Francois','Laurent','Marie','Nathalie','Isabelle','Catherine','Francoise','Monique','Sylvie','Christine','Veronique','Brigitte','Lucas','Gabriel','Raphael','Louis','Arthur','Jules','Adam','Alexandre','Hugo','Maxime','Lea','Emma','Chloe','Manon','Jade','Camille','Sarah','Laura','Lola','Ines'],
    'de': ['Lukas','Leon','Felix','Maximilian','Jonas','Tim','Niklas','Philipp','Fabian','Johannes','Julia','Lisa','Laura','Anna','Sarah','Leonie','Lena','Marie','Sophie','Hannah','Finn','Elias','Luis','Henry','Moritz','Julian','Tom','Benedikt','David','Jonas','Emilia','Mia','Emma','Nele','Leni','Frieda','Marlene','Ida','Paula','Clara'],
    'ru': ['Aleksandr','Sergey','Dmitriy','Andrey','Aleksey','Mikhail','Vladimir','Ivan','Nikolay','Pavel','Olga','Elena','Natalya','Irina','Anna','Tatiana','Marina','Yulia','Svetlana','Ekaterina','Artem','Maxim','Egor','Daniil','Nikita','Timofey','Matvey','Roman','Yaroslav','Ilya','Anastasia','Daria','Polina','Viktoria','Ksenia','Alina','Alexandra','Valeria','Elizaveta','Ulyana'],
    'ar': ['Mohammed','Ahmed','Ali','Hassan','Hussein','Omar','Khaled','Mahmoud','Abdullah','Youssef','Fatima','Aisha','Mariam','Layla','Zainab','Noor','Huda','Amira','Sarah','Yasmin','Adam','Ibrahim','Ismail','Musa','Yusuf','Yahya','Nuh','Harun','Sulayman','Dawood','Nadia','Samira','Leila','Rania','Dana','Mona','Hala','Rasha','Maha','Nour'],
    'jp': ['Hiroshi','Takeshi','Kenji','Satoshi','Taro','Ichiro','Shinji','Ryota','Yuki','Kazuki','Yuko','Akiko','Yoko','Hanako','Sakura','Yumi','Keiko','Miyuki','Tomoko','Rie','Haruto','Yuma','Sota','Riku','Kaito','Ryo','Haruki','Sho','Ren','Hinata','Misaki','Aoi','Rin','Mei','Yua','Himari','Ichika','Koharu','Sara','Miyu'],
    'br': ['Lucas','Gabriel','Matheus','Joao','Pedro','Felipe','Rafael','Gustavo','Vinicius','Guilherme','Julia','Ana','Maria','Larissa','Beatriz','Camila','Gabriela','Isabela','Amanda','Marina','Enzo','Miguel','Davi','Arthur','Bernardo','Caio','Thiago','Leonardo','Vitor','Eduardo','Fernanda','Bruna','Jessica','Tatiane','Aline','Priscila','Carolina','Vanessa','Leticia','Juliana'],
    'in': ['Aarav','Vihaan','Vivaan','Arjun','Reyansh','Ishaan','Shaurya','Dhruv','Rohan','Aryan','Aanya','Aadhya','Sara','Ira','Ananya','Myra','Diya','Aarohi','Anaya','Navya','Raj','Vikram','Sanjay','Ravi','Amit','Suresh','Deepak','Manoj','Vijay','Rahul','Priya','Neha','Shweta','Pooja','Anita','Sunita','Deepika','Rekha','Kavita','Swati'],
}

LAST_NAMES = {
    'us': ['Smith','Johnson','Williams','Brown','Jones','Garcia','Miller','Davis','Rodriguez','Martinez','Hernandez','Lopez','Gonzalez','Wilson','Anderson','Thomas','Taylor','Moore','Jackson','Martin','Lee','Perez','Thompson','White','Harris','Sanchez','Clark','Ramirez','Lewis','Robinson','Walker','Young','Allen','King','Wright','Scott','Torres','Nguyen','Hill','Flores','Green','Adams','Nelson','Baker','Hall','Rivera','Campbell','Mitchell','Carter','Roberts','Diaz','Chen','Patel','Khan','Singh','Kim','Jackson','Xu','Wong','Bennett'],
    'uk': ['Smith','Jones','Williams','Brown','Taylor','Davies','Wilson','Evans','Thomas','Roberts','Walker','Wright','Clark','Cooper','Hill','Green','Edwards','Butler','Baker','Phillips','James','Bennett','Miller','Davis','Price','Wood','Harris','Martin','Thompson','Johnson'],
    'fr': ['Martin','Bernard','Dubois','Thomas','Robert','Richard','Petit','Durand','Leroy','Moreau','Simon','Laurent','Lefebvre','Michel','Garcia','David','Bertrand','Roux','Vincent','Fournier','Morel','Girard','Andre','Mercier','Dupont','Lambert','Bonnet','Francois','Martinez','Legrand'],
    'de': ['Mueller','Schmidt','Schneider','Fischer','Weber','Meyer','Wagner','Becker','Schulz','Hoffmann','Schafer','Koch','Bauer','Richter','Klein','Wolf','Schroder','Neumann','Schwarz','Zimmermann','Braun','Kruger','Hofmann','Hartmann','Lange','Werner','Krause','Lehmann','Kohler','Herrmann'],
    'ru': ['Ivanov','Smirnov','Kuznetsov','Popov','Vasilyev','Petrov','Sokolov','Mikhailov','Novikov','Fyodorov','Morozov','Volkov','Alekseyev','Lebedev','Semyonov','Yegorov','Pavlov','Kozlov','Stepanov','Nikolayev','Orlov','Makarov','Zakharov','Zaytsev','Solovyov','Borisov','Yakovlev','Grigoryev','Romanov','Vorobyov'],
    'ar': ['Al-Farsi','Al-Saud','Al-Rashid','Al-Ahmad','Haddad','Nasser','Mansour','Hakim','Abbas','Saad','Hussein','Abdullah','Ali','Khalil','Rahman','Karim','Jabir','Aziz','Salim','Youssef','Al-Masri','Al-Ansari','Al-Qahtani','Al-Harbi','Al-Otaibi','Al-Ghamdi','Al-Shammari','Al-Dosari','Al-Malik','Al-Abdul'],
    'jp': ['Sato','Suzuki','Takahashi','Tanaka','Watanabe','Ito','Yamamoto','Nakamura','Kobayashi','Kato','Yoshida','Yamada','Sasaki','Yamaguchi','Matsumoto','Inoue','Kimura','Shimizu','Hayashi','Saito','Yamashita','Ishikawa','Nakajima','Ogawa','Fujita','Okada','Hashimoto','Ono','Yamazaki','Ishii'],
    'br': ['Silva','Santos','Oliveira','Souza','Lima','Pereira','Costa','Ferreira','Rodrigues','Almeida','Nascimento','Araujo','Ribeiro','Carvalho','Gomes','Martins','Barbosa','Rocha','Dias','Mendes','Moreira','Correia','Cardoso','Teixeira','Cavalcanti','Melo','Cruz','Nunes','Monteiro','Freitas'],
    'in': ['Sharma','Verma','Patel','Singh','Kumar','Gupta','Reddy','Rao','Joshi','Desai','Mehta','Nair','Menon','Agarwal','Bhat','Shah','Das','Banerjee','Chatterjee','Mukherjee','Iyer','Pillai','Naidu','Choudhury','Bose','Sen','Saxena','Sethi','Mishra','Srivastava'],
}

# ─────────────────────────────────────────────────────────────────────────────
# Per-country email domains, weighted like real registration distributions
# ─────────────────────────────────────────────────────────────────────────────
COUNTRY_DOMAINS = {
    'us': [('gmail.com',50),('yahoo.com',18),('hotmail.com',10),('outlook.com',10),('aol.com',4),('icloud.com',4),('protonmail.com',2),('mail.com',1),('live.com',1)],
    'uk': [('gmail.com',45),('outlook.com',20),('hotmail.com',12),('btinternet.com',5),('virginmedia.com',4),('sky.com',3),('talktalk.net',2),('icloud.com',4),('yahoo.com',5)],
    'fr': [('gmail.com',35),('orange.fr',15),('free.fr',12),('sfr.fr',8),('wanadoo.fr',6),('laposte.net',4),('hotmail.fr',8),('outlook.fr',7),('yahoo.fr',5)],
    'de': [('gmail.com',35),('web.de',15),('gmx.de',12),('t-online.de',9),('freenet.de',5),('1und1.de',3),('hotmail.de',9),('outlook.de',8),('yahoo.de',4)],
    'ru': [('mail.ru',35),('yandex.ru',25),('rambler.ru',8),('bk.ru',6),('list.ru',4),('inbox.ru',4),('gmail.com',12),('hotmail.com',3),('yahoo.com',3)],
    'ar': [('gmail.com',40),('outlook.com',20),('hotmail.com',10),('yahoo.com',10),('outlook.sa',5),('icloud.com',5),('protonmail.com',4),('mail.com',6)],
    'jp': [('yahoo.co.jp',30),('gmail.com',28),('docomo.ne.jp',8),('ezweb.ne.jp',7),('softbank.ne.jp',7),('hotmail.co.jp',6),('icloud.com',8),('outlook.jp',6)],
    'br': [('gmail.com',45),('hotmail.com',12),('bol.com.br',10),('uol.com.br',8),('ig.com.br',5),('globo.com',4),('terra.com.br',3),('yahoo.com.br',6),('outlook.com',7)],
    'in': [('gmail.com',55),('outlook.com',10),('hotmail.com',6),('yahoo.co.in',6),('yahoo.com',5),('rediffmail.com',5),('indiatimes.com',3),('sify.com',2),('protonmail.com',4),('mail.com',4)],
}
CORP_DOMAINS = ['company.com','corp.net','enterprise.org','business.io','group.co','industries.net','global.org','solutions.com','systems.io','techcorp.net']

# ─────────────────────────────────────────────────────────────────────────────
# Breach-weighted password model
# Top real-world passwords (frequency order) + weighted bases + patterns
# ─────────────────────────────────────────────────────────────────────────────
TOP_PASSWORDS = [
    # (password, weight) — frequency order from real breach statistics
    ('123456',1000),('password',950),('12345678',900),('qwerty',850),('123456789',820),
    ('12345',800),('1234',780),('111111',760),('1234567',740),('dragon',700),
    ('123123',680),('baseball',660),('abc123',650),('football',640),('monkey',620),
    ('letmein',600),('shadow',580),('master',560),('666666',540),('qwertyuiop',520),
    ('123321',500),('mustang',490),('1234567890',480),('michael',460),('654321',450),
    ('superman',440),('1qaz2wsx',430),('7777777',420),('121212',410),('000000',400),
    ('qazwsx',390),('123qwe',380),('killer',370),('trustno1',360),('jordan',350),
    ('jennifer',340),('zxcvbnm',330),('asdfgh',320),('hunter',310),('buster',300),
    ('soccer',295),('harley',290),('batman',285),('andrew',280),('tigger',275),
    ('sunshine',270),('iloveyou',265),('charlie',260),('robert',255),('thomas',250),
    ('hockey',245),('ranger',240),('daniel',235),('starwars',230),('computer',225),
    ('george',220),('michelle',215),('jessica',210),('pepper',205),('1111',200),
    ('zxcvbn',195),('555555',190),('11111111',185),('131313',180),('freedom',175),
    ('777777',170),('pass',165),('maggie',160),('159753',155),('aaa111',150),
    ('qwerty123',145),('abcdef',140),('password1',138),('password123',136),
    ('welcome',134),('welcome1',132),('qwerty1',130),('1q2w3e4r',128),
    ('1234qwer',126),('admin',124),('administrator',120),('login',115),
    ('passw0rd',110),('p@ssw0rd',105),('p@55w0rd',100),('princess',95),
    ('diamond',90),('phoenix',85),('samsung',80),('nokia',75),('motorola',70),
    ('redsox',68),('yankees',66),('cowboys',64),('packers',62),('viking',60),
    ('summer',58),('winter',56),('spring',54),('autumn',52),('october',50),
    ('november',48),('december',46),('jasmine',44),('lovely',42),('sweet',40),
    ('secret',38),('liverpool',36),('chelsea',34),('arsenal',32),('rangers',30),
    ('chelsea1',28),('passw0rd1',26),('welcome123',24),('admin123',22),
    ('letmein1',20),('dragon1',18),('monkey1',16),('shadow1',14),('master1',12),
    ('qwerty1234',10),('abc12345',8),('iloveyou1',6),('trustno1!',5),
]

PASSWORD_BASES = [
    # (base, weight) — common bases that humans bolt digits/symbols onto
    ('password',100),('passw0rd',60),('Password',55),('Passw0rd',50),('P@ssw0rd',45),
    ('p@ssw0rd',40),('P@55w0rd',35),('welcome',50),('Welcome',45),('iloveyou',40),
    ('letmein',35),('admin',35),('Admin',30),('administrator',25),('root',20),
    ('master',25),('qwerty',30),('abc123',28),('sunshine',25),('dragon',24),
    ('monkey',22),('football',22),('baseball',20),('soccer',18),('hunter',16),
    ('mustang',15),('starwars',15),('batman',14),('superman',13),('shadow',12),
    ('trustno1',12),('jordan',11),('michael',10),('jennifer',10),('charlie',9),
    ('computer',8),('michelle',8),('pepper',7),('maggie',7),('secret',7),
    ('tigger',6),('george',6),('andrew',6),('thomas',6),('robert',5),
    ('daniel',5),('hockey',5),('ranger',5),('arizona',5),('america',5),
    ('usa',4),('boston',4),('florida',4),('dallas',4),('houston',4),
    ('chicago',4),('miami',4),('phoenix',4),('atlanta',3),('eagle',3),
    ('lion',3),('tiger',3),('wolf',3),('king',3),('queen',3),('star',3),
    ('moon',3),('sun',3),('sky',3),('red',3),('blue',3),('gold',3),
    ('fire',3),('ice',3),('rain',3),('snow',3),('wind',3),('dark',3),
    ('light',3),('love',3),('life',3),('hope',3),('god',3),('angel',3),
    ('devil',2),('rock',2),('roll',2),('party',2),('pizza',2),('coffee',2),
    ('beer',2),('smoke',2),('diesel',2),('racing',2),('nascar',2),('ferrari',2),
    ('porsche',2),('mercedes',2),('bmw',2),('yamaha',2),('honda',2),('toyota',2),
    ('ford',2),('chevy',2),('liverpool',2),('chelsea',2),('arsenal',2),
    ('manchester',2),('united',2),('redsox',2),('yankees',2),('cowboys',2),
    ('packers',2),('viking',2),('blink182',2),('metallica',2),('nirvana',2),
    ('panthers',2),('pirates',2),('buddy',2),('snoopy',2),('garfield',2),
]

KEYBOARD_PATTERNS = ['qwerty','qwertyuiop','asdfgh','asdfghjkl','zxcvbn','zxcvbnm','1qaz2wsx','1q2w3e4r','1234qwer','q1w2e3r4','1qazxsw2','qazwsxedc','poiuyt','lkjhgf','mnbvcxz','12qwaszx','123456qwerty','qwerty123','asdf1234','zxcv1234','1q2w3e4r5t','qweasd','qweasdzxc','zaq12wsx','!QAZ2wsx','qazwsx','1234asdf','asdfqwer']

SEASONS = ['Summer','Winter','Spring','Autumn']
MONTHS = ['January','February','March','April','May','June','July','August','September','October','November','December']
SPECIAL_CHARS = ['!','@','#','$','%','&','*']

# ── Security questions ──
SECURITY_QUESTIONS = [
    ("What is your mother's maiden name?", lambda: random.choice(LAST_NAMES['us'])),
    ("What was the name of your first pet?", lambda: random.choice(['Fluffy','Max','Bella','Charlie','Rocky','Luna','Simba','Milo','Lucky','Oscar','Buddy','Molly','Coco','Ruby','Jack'])),
    ("What city were you born in?", lambda: random.choice(['New York','Los Angeles','Chicago','Houston','London','Manchester','Paris','Berlin','Moscow','Dubai','Tokyo','Sydney','Mumbai'])),
    ("What is your favorite movie?", lambda: random.choice(['The Shawshank Redemption','The Godfather','Inception','The Matrix','Pulp Fiction','Fight Club','Forrest Gump','Star Wars','The Dark Knight','Goodfellas','Avatar','Titanic'])),
    ("What is the name of your elementary school?", lambda: f"{random.choice(['Lincoln','Washington','Jefferson','Roosevelt','Kennedy','Madison','Monroe','Adams','Jackson','Franklin'])} Elementary"),
    ("What was the make of your first car?", lambda: random.choice(['Toyota','Honda','Ford','Chevrolet','BMW','Mercedes','Audi','Volkswagen','Nissan','Mazda','Subaru','Hyundai','Kia','Lexus'])),
    ("What is your favorite food?", lambda: random.choice(['Pizza','Sushi','Burgers','Tacos','Pasta','Steak','Salad','Curry','Ramen','BBQ'])),
    ("What is the name of your best childhood friend?", lambda: random.choice(FIRST_NAMES['us'])),
]

# Output format identifiers
FMT_EMAIL_PASS = 1        # email:password
FMT_USER_PASS = 2         # username:password
FMT_EMAIL_PASS_NAME = 3   # email:password:fullname
FMT_PII = 4               # full PII + SSN
FMT_PII_CC = 5            # full PII + SSN + CC
FMT_PASS_ONLY = 6         # password only (wordlist / hashcat / spraying)


def weighted(pairs):
    """Weighted choice from [(item, weight), ...] pairs."""
    items = [p[0] for p in pairs]
    w = [p[1] for p in pairs]
    return random.choices(items, weights=w, k=1)[0]


def weighted_bases():
    return weighted(PASSWORD_BASES)


def generate_ssn():
    return f"{random.randint(1,899):03d}-{random.randint(1,99):02d}-{random.randint(1,9999):04d}"


def luhn_checksum(n):
    d = [int(x) for x in str(n)]
    for i in range(len(d)-2, -1, -2):
        d[i] = d[i] * 2
        if d[i] > 9: d[i] -= 9
    return sum(d)


def generate_card(bin_prefix):
    n = str(bin_prefix)
    while len(n) < 15: n += str(random.randint(0,9))
    check = 10 - (luhn_checksum(int(n+'0')) % 10)
    if check == 10: check = 0
    return n + str(check)


def card_expiry():
    y = datetime.now().year + random.randint(0,5)
    return f"{random.randint(1,12):02d}/{y % 100:02d}"


def card_cvv():
    return f"{random.randint(100,999)}"


class CredForge:
    def __init__(self):
        self.countries = list(FIRST_NAMES.keys())
        self.weights = {'us':0.25,'uk':0.08,'fr':0.07,'de':0.07,'ru':0.08,'ar':0.08,'jp':0.07,'br':0.10,'in':0.20}

    def pick_country(self):
        r = random.random()
        cum = 0
        for c, p in self.weights.items():
            cum += p
            if r <= cum: return c
        return 'us'

    def pick_birth_year(self):
        # Age-weighted: 1975-1995 heavy, 1960-2005 tail
        r = random.random()
        if r < 0.55:
            return random.randint(1975, 1995)
        if r < 0.80:
            return random.randint(1996, 2005)
        return random.randint(1960, 1974)

    def pick_domain(self, country):
        # 82% country-specific pool, 18% generic corporates
        if random.random() < 0.18:
            return random.choice(CORP_DOMAINS)
        return weighted(COUNTRY_DOMAINS.get(country, COUNTRY_DOMAINS['us']))

    def generate_person(self, country=None, pii=False, cc=False):
        country = country or self.pick_country()
        first = random.choice(FIRST_NAMES[country])
        last = random.choice(LAST_NAMES[country])
        birth_year = self.pick_birth_year()
        birth_month = random.randint(1,12)

        person = {
            'first': first,
            'last': last,
            'name': f"{first} {last}",
            'country': country,
            'birth_year': birth_year,
            'birth_month': birth_month,
        }

        # Email — realistic patterns, country-weighted domains
        fmt = random.randint(0,4)
        dom = self.pick_domain(country)
        if fmt == 0:
            person['email'] = f"{first.lower()}.{last.lower()}{random.randint(1,99)}@{dom}"
        elif fmt == 1:
            person['email'] = f"{first.lower()}{last.lower()}{birth_year}@{dom}"
        elif fmt == 2:
            person['email'] = f"{first[0].lower()}{last.lower()}{birth_month:02d}{str(birth_year)[-2:]}@{dom}"
        elif fmt == 3:
            person['email'] = f"{first.lower()}{last[0].lower()}{str(birth_year)[-2:]}@{dom}"
        else:
            person['email'] = f"{last.lower()}.{first.lower()}{random.randint(1,99)}@{dom}"

        person['username'] = random.choice([
            f"{first[0].lower()}{last.lower()}",
            f"{last.lower()}{first[0].lower()}{birth_year}",
            f"{first.lower()}.{last.lower()}",
            f"{first.lower()}{last[0].lower()}{str(birth_year)[-2:]}",
            f"{last.lower()}_{first.lower()}",
            f"{first.lower()}{birth_year}",
            f"{first[0].lower()}{last.lower()}{birth_month:02d}",
        ])

        person['password'] = self.gen_password(first, last, birth_year, birth_month)
        person['phone'] = f"+1-{random.randint(200,999)}-{random.randint(100,999)}-{random.randint(1000,9999)}"

        if pii:
            cities = ['New York','Los Angeles','Chicago','Houston','Phoenix','San Antonio','San Diego','Dallas','San Jose','Miami']
            person['address'] = f"{random.randint(1,9999)} {random.choice(['Main St','Oak Ave','Elm St','Park Ave','Maple Dr','Cedar Ln','Pine St','Lake Rd','Forest Dr','Hill Rd'])}, {random.choice(cities)}, {random.choice(['NY','CA','IL','TX','AZ','FL','WA','CO','MA','GA'])} {random.randint(10000,99999)}"
            if country == 'us':
                person['ssn'] = generate_ssn()

        if cc:
            ct, pxs = random.choice([('Visa',[4]),('MC',[51,52,53,54,55]),('Amex',[34,37]),('Disc',[6011,644,645,646,647,648,649,65])])
            p = random.choice(pxs)
            person['cc'] = {
                'type': ct,
                'number': generate_card(p),
                'exp': card_expiry(),
                'cvv': card_cvv(),
            }

        # Security Q (full PII formats only)
        if (pii or cc) and random.random() < 0.3:
            q, fn = random.choice(SECURITY_QUESTIONS)
            person['security_q'] = q
            person['security_a'] = fn()

        return person

    def gen_password(self, first, last, birth_year, birth_month):
        patterns = [
            # (pattern, weight) — higher = more common in the wild
            (lambda: weighted(TOP_PASSWORDS), 26),                    # real top passwords verbatim
            (lambda: f"{weighted_bases()}{birth_year}", 14),          # base+full year
            (lambda: f"{weighted_bases()}{str(birth_year)[-2:]}", 12),# base+2-digit year
            (lambda: f"{weighted_bases()}{random.choice(SPECIAL_CHARS)}", 8),
            (lambda: f"{weighted_bases()}{random.randint(1,999)}", 10),
            (lambda: f"{first}{birth_year}", 8),                      # name+year
            (lambda: f"{first}{random.choice(SPECIAL_CHARS)}{str(birth_year)[-2:]}", 6),
            (lambda: f"{first}{random.randint(1,999)}", 5),
            (lambda: f"{first[0]}.{last}{birth_year}", 3),
            (lambda: f"{first}{birth_month:02d}{str(birth_year)[-2:]}", 4),
            (lambda: f"{last}{first[0]}{birth_year}", 3),
            (lambda: f"{random.choice(SEASONS)}{birth_year}", 5),
            (lambda: f"{random.choice(MONTHS)}{str(birth_year)[-2:]}", 3),
            (lambda: f"P@ssw0rd{birth_year}", 4),
            (lambda: f"{first}1{birth_year}", 2),
            (lambda: f"{last}123{birth_year % 100}", 2),
            (lambda: f"{first.lower()}{last.lower()}{random.randint(10,99)}", 3),
            (lambda: f"{last.capitalize()}{random.randint(100,999)}", 2),
            (lambda: f"{first[:4].lower()}{last[:4].lower()}{birth_year}", 2),
            (lambda: random.choice(KEYBOARD_PATTERNS), 4),
            (lambda: random.choice(KEYBOARD_PATTERNS) + str(birth_year)[-2:], 2),
            (lambda: ''.join(random.choice(string.ascii_letters + string.digits + ''.join(SPECIAL_CHARS)) for _ in range(random.randint(8,12))), 5),
        ]
        return weighted(patterns)()

    def format_person(self, p, fmt):
        """Render a person dict as a combolist line for the given format."""
        if fmt == FMT_EMAIL_PASS:
            return f"{p['email']}:{p['password']}"
        if fmt == FMT_USER_PASS:
            return f"{p['username']}:{p['password']}"
        if fmt == FMT_EMAIL_PASS_NAME:
            return f"{p['email']}:{p['password']}:{p['name']}"
        if fmt == FMT_PASS_ONLY:
            return p['password']
        # PII formats
        parts = [p['email'], p['password'], p['name'], p.get('phone','N/A'), p.get('address','N/A')]
        if p.get('ssn'): parts.append(p['ssn'])
        if fmt == FMT_PII_CC and p.get('cc'):
            parts.extend([p['cc']['number'], p['cc']['exp'], p['cc']['cvv']])
        if p.get('security_q'): parts.append(f"Q:{p['security_q']} A:{p['security_a']}")
        return ':'.join(str(x) for x in parts)

    def generate(self, count, country=None, fmt=FMT_EMAIL_PASS, unique=True, min_length=0):
        pii = fmt in (FMT_PII, FMT_PII_CC)
        cc = fmt == FMT_PII_CC
        entries = []
        seen = set()
        attempts = 0
        while len(entries) < count and attempts < count * 50:
            attempts += 1
            p = self.generate_person(country, pii, cc)
            line = self.format_person(p, fmt)
            if min_length and len(p['password']) < min_length:
                continue
            if unique and line in seen:
                continue
            seen.add(line)
            entries.append(line)
        return entries


def run_cli(args):
    if args.seed is not None:
        random.seed(args.seed)
    if args.count < 1:
        print(f"  {Rc}Count must be >= 1{R}")
        sys.exit(1)
    if args.format not in (1,2,3,4,5,6):
        print(f"  {Rc}Format must be 1-6{R}")
        sys.exit(1)
    country = args.country.lower() if args.country else None
    if country and country not in FIRST_NAMES:
        print(f"  {Y}Unknown country '{args.country}', using worldwide{R}")
        country = None
    forge = CredForge()
    entries = forge.generate(args.count, country, args.format, unique=args.unique, min_length=args.min_length)
    with open(args.output, 'w') as f:
        for e in entries: f.write(e+'\n')
    sz = os.path.getsize(args.output)
    if not args.quiet:
        print(f"  {G}✔ Saved {K}{args.output}{R} ({sz:,} bytes, {len(entries):,} lines)")
        print(f"  {D}Sample:{R}")
        for e in entries[:5]:
            print(f"    {D}{e[:80]}{R}")
    return 0


def run_interactive():
    os.system('clear')
    print(BANNER)

    count = input(f"  {A}Lines to generate{R} [{K}100{R}]: ").strip() or '100'
    try: count = int(count)
    except: count = 100

    print(f"\n  {D}Output format:{R}")
    print(f"  {K}1{R}) email:password")
    print(f"  {K}2{R}) username:password")
    print(f"  {K}3{R}) email:password:fullname")
    print(f"  {K}4{R}) Full PII + SSN {Rc}⚠{R}")
    print(f"  {K}5{R}) Full PII + SSN + CC {Rc}⚠⚠{R}")
    print(f"  {K}6{R}) password only (wordlist)")

    fc = input(f"\n  {A}Format{R} [{K}1{R}]: ").strip() or '1'
    try:
        fc = int(fc)
        if fc not in (1,2,3,4,5,6): fc = 1
    except:
        fc = 1

    c = input(f"  {A}Country (blank=worldwide){R} [{K}all{R}]: ").strip().lower() or None
    if c and c not in FIRST_NAMES:
        print(f"  {Y}Unknown country, using worldwide{R}")
        c = None

    fn = input(f"  {A}Output file{R} [{K}combolist.txt{R}]: ").strip() or 'combolist.txt'

    print(f"\n  {C}═══════════════════════════════════{R}")
    print(f"  {B}Generating {K}{count}{R}{B} credentials...{R}")
    print(f"  {C}═══════════════════════════════════{R}\n")

    forge = CredForge()
    entries = forge.generate(count, c, fc)

    with open(fn, 'w') as f:
        for e in entries: f.write(e+'\n')

    sz = os.path.getsize(fn)
    print(f"  {G}✔ Saved {K}{fn}{R} ({sz:,} bytes)\n")
    print(f"  {D}Sample:{R}")
    for e in entries[:5]:
        print(f"    {D}{e[:80]}{R}")
    print(f"\n  {G}✓ Complete{R}")
    print(f"{D}© Adam-ZS — For authorized testing only{R}")


def main():
    parser = argparse.ArgumentParser(
        prog='credforge',
        description='Realistic synthetic credential generator for red team operations.',
        epilog='No args = interactive mode. For authorized testing only.',
    )
    parser.add_argument('-n', '--count', type=int, default=100, help='lines to generate (default: 100)')
    parser.add_argument('-f', '--format', type=int, default=1, choices=[1,2,3,4,5,6],
                        help='1=email:pass 2=user:pass 3=email:pass:name 4=PII+SSN 5=PII+SSN+CC 6=password-only (default: 1)')
    parser.add_argument('-c', '--country', default=None,
                        help='country code (us, uk, fr, de, ru, ar, jp, br, in). Blank=worldwide')
    parser.add_argument('-o', '--output', default='combolist.txt', help='output file (default: combolist.txt)')
    parser.add_argument('--seed', type=int, default=None, help='random seed for reproducible output')
    parser.add_argument('--unique', action='store_true', default=True, help='deduplicate entries (default: on)')
    parser.add_argument('--no-unique', dest='unique', action='store_false', help='allow duplicate entries')
    parser.add_argument('--min-length', type=int, default=0, help='minimum password length (default: 0)')
    parser.add_argument('-q', '--quiet', action='store_true', help='suppress sample output')
    parser.add_argument('--version', action='version', version=f'credforge {VERSION}')
    args = parser.parse_args()

    if args.count != 100 or args.format != 1 or args.country is not None or args.output != 'combolist.txt':
        sys.exit(run_cli(args))
    run_interactive()


if __name__ == '__main__':
    main()
