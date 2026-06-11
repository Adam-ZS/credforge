#!/usr/bin/env python3
"""
CredForge — Realistic credential generator for red team operations.
Generates combolist-style data that passes real validation checks.
"""

import random
import string
import re
import os
import sys
import json
from datetime import datetime

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
 {C}║{R}      {D}Realistic Cred Generator v2.0{R}          {C}║{R}
 {C}║{R}            {D}by Adam-ZS{R}                      {C}║{R}
 {C}║{R}                                             {C}║{R}
 {C}╚═══════════════════════════════════════════════╝{R}
"""

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

DOMAINS = {
    'free': ['gmail.com','yahoo.com','hotmail.com','outlook.com','aol.com','icloud.com','protonmail.com','mail.com','zoho.com','yandex.com','gmx.com','tutanota.com','fastmail.com','live.com','msn.com','ymail.com','inbox.com','rediffmail.com'],
    'corp': ['company.com','corp.net','enterprise.org','business.io','group.co','industries.net','global.org','solutions.com','systems.io','techcorp.net'],
}

COMMON_BASES = ['Password','Passw0rd','password','pass123','P@ssword','P@55w0rd','Welcome','welcome','Welcome1','Welcome123','Admin','admin','Admin123','administrator','Master','master','Master123','Qwerty','qwerty','Qwerty123','Letmein','letmein','Summer','Winter','Spring','Autumn','Sunshine','Dragon','dragon','Monkey','Shadow','Starwars','Batman','Superman','Iloveyou','Trustno1','Football','football','baseball','soccer','Mustang','mustang']

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
    
    def generate_person(self, country=None, pii=False, cc=False):
        country = country or self.pick_country()
        first = random.choice(FIRST_NAMES[country])
        last = random.choice(LAST_NAMES[country])
        birth_year = random.randint(1960, 2005)
        birth_month = random.randint(1,12)
        
        person = {
            'first': first,
            'last': last,
            'name': f"{first} {last}",
            'country': country,
            'birth_year': birth_year,
            'birth_month': birth_month,
        }
        
        # Email
        fmt = random.randint(0,3)
        if fmt == 0:
            person['email'] = f"{first.lower()}.{last.lower()}{random.randint(1,99)}@{random.choice(DOMAINS['free'])}"
        elif fmt == 1:
            person['email'] = f"{first.lower()}{last.lower()}{birth_year}@{random.choice(DOMAINS['free'])}"
        elif fmt == 2:
            person['email'] = f"{first[0].lower()}{last.lower()}{birth_month:02d}{str(birth_year)[-2:]}@{random.choice(DOMAINS['free'])}"
        else:
            person['email'] = f"{first[0].lower()}{last.lower()}@{random.choice(DOMAINS['corp'])}"
        
        person['username'] = random.choice([
            f"{first[0].lower()}{last.lower()}",
            f"{last.lower()}{first[0].lower()}{birth_year}",
            f"{first.lower()}.{last.lower()}",
            f"{first.lower()}{last[0].lower()}{str(birth_year)[-2:]}",
            f"{last.lower()}_{first.lower()}",
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
        
        # Security Q
        if random.random() < 0.3:
            q, fn = random.choice(SECURITY_QUESTIONS)
            person['security_q'] = q
            person['security_a'] = fn()
        
        return person
    
    def gen_password(self, first, last, birth_year, birth_month):
        patterns = [
            lambda: f"{random.choice(COMMON_BASES)}{birth_year}",
            lambda: f"{random.choice(COMMON_BASES)}{str(birth_year)[-2:]}",
            lambda: f"{random.choice(COMMON_BASES)}{random.choice(SPECIAL_CHARS)}{birth_year}",
            lambda: f"{first}{birth_year}",
            lambda: f"{first}{random.choice(SPECIAL_CHARS)}{str(birth_year)[-2:]}",
            lambda: f"{first[0]}.{last}{birth_year}",
            lambda: f"{first}{birth_month:02d}{str(birth_year)[-2:]}",
            lambda: f"{last}{first[0]}{birth_year}",
            lambda: f"{random.choice(['Summer','Winter','Spring','Autumn'])}{birth_year}",
            lambda: f"P@ssw0rd{birth_year}",
            lambda: f"{first}1{birth_year}",
            lambda: f"{last}123{birth_year % 100}",
            lambda: f"{first.lower()}{last.lower()}{random.randint(10,99)}",
            lambda: f"{last.capitalize()}{random.randint(100,999)}",
            lambda: f"{first[:4].lower()}{last[:4].lower()}{birth_year}",
            lambda: f"{random.choice(['Love','God','Life','Hope','King','Queen','Star','Moon','Sun','Sky','Red','Blue','Gold','Fire','Ice','Rain','Snow','Wind','Dark','Light'])}{random.randint(1,999)}",
            lambda: ''.join(random.choice(string.ascii_letters + string.digits + ''.join(SPECIAL_CHARS)) for _ in range(8)),
        ]
        pw = random.choice(patterns)()
        if random.random() < 0.3:
            pw += random.choice(SPECIAL_CHARS)
        return pw
    
    def generate(self, count, country=None, pii=False, cc=False):
        entries = []
        for _ in range(count):
            p = self.generate_person(country, pii, cc)
            fmt = random.randint(0,3)
            if fmt == 0:
                entries.append(f"{p['email']}:{p['password']}")
            elif fmt == 1:
                entries.append(f"{p['username']}:{p['password']}")
            elif fmt == 2:
                entries.append(f"{p['email']}:{p['password']}:{p['name']}")
            else:
                parts = [p['email'], p['password'], p['name'], p.get('phone','N/A'), p.get('address','N/A')]
                if p.get('ssn'): parts.append(p['ssn'])
                if p.get('cc'): parts.extend([p['cc']['number'], p['cc']['exp'], p['cc']['cvv']])
                if p.get('security_q'): parts.append(f"Q:{p['security_q']} A:{p['security_a']}")
                entries.append(':'.join(str(x) for x in parts))
        return entries


def main():
    os.system('clear')
    print(BANNER)
    
    count = input(f"  {A}Lines to generate{R} [{K}100{R}]: ").strip() or '100'
    try: count = int(count)
    except: count = 100
    
    print(f"\n  {D}Output format:{R}")
    print(f"  {K}1{R}) email:password")
    print(f"  {K}2{R}) email:password:fullname")
    print(f"  {K}3{R}) Full PII + SSN {Rc}⚠{R}")
    print(f"  {K}4{R}) Full PII + SSN + CC {Rc}⚠⚠{R}")
    
    fc = input(f"\n  {A}Format{R} [{K}1{R}]: ").strip() or '1'
    pii = fc in ('3','4')
    cc = fc == '4'
    
    c = input(f"  {A}Country (blank=worldwide){R} [{K}all{R}]: ").strip().lower() or None
    if c and c not in FIRST_NAMES:
        print(f"  {Y}Unknown country, using worldwide{R}")
        c = None
    
    fn = input(f"  {A}Output file{R} [{K}combolist.txt{R}]: ").strip() or 'combolist.txt'
    
    print(f"\n  {C}═══════════════════════════════════{R}")
    print(f"  {B}Generating {K}{count}{R}{B} credentials...{R}")
    print(f"  {C}═══════════════════════════════════{R}\n")
    
    forge = CredForge()
    entries = forge.generate(count, c, pii, cc)
    
    with open(fn, 'w') as f:
        for e in entries: f.write(e+'\n')
    
    sz = os.path.getsize(fn)
    print(f"  {G}✔ Saved {K}{fn}{R} ({sz:,} bytes)\n")
    print(f"  {D}Sample:{R}")
    for e in entries[:5]:
        print(f"    {D}{e[:80]}{R}")
    print(f"\n  {G}✓ Complete{R}")
    print(f"{D}© Adam-ZS — For authorized testing only{R}")

if __name__ == '__main__':
    main()
