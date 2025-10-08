tokenTable = {
    # булеві константи
    'true': 'boolval',
    'false': 'boolval',

    # ключові слова (Rocket)
    'int': 'keyword', 'float': 'keyword', 'bool': 'keyword', 'string': 'keyword',
    'print': 'keyword',
    'inputInt': 'keyword', 'inputFloat': 'keyword', 'inputBool': 'keyword', 'inputString': 'keyword',
    'if': 'keyword', 'elif': 'keyword', 'else': 'keyword',
    'while': 'keyword', 'do': 'keyword', 'for': 'keyword',
    'switch': 'keyword', 'case': 'keyword', 'default': 'keyword',

    # логічні оператори
    '&&': 'logic_op', '||': 'logic_op', '!': 'logic_op',

    # арифметичні оператори
    '+': 'add_op', '-': 'add_op', '*': 'mult_op', '/': 'mult_op',

    # оператори відношення
    '=': 'assign_op',
    '==': 'rel_op', '!=': 'rel_op', '<': 'rel_op', '>': 'rel_op', '<=': 'rel_op', '>=': 'rel_op',

    # степеневий оператор
    '^': 'pow_op',

    # оператори присвоєння зі скороченням
    '+=': 'add_ass_op', '-=': 'add_ass_op',
    '*=': 'mult_ass_op', '/=': 'mult_ass_op',

    # тернарний
    '?': 'tern_op', ':': 'tern_op',

    # дужки
    '(': 'brackets_op', ')': 'brackets_op',
    '{': 'brackets_op', '}': 'brackets_op',
    '[': 'brackets_op', ']': 'brackets_op',

    # пунктуація
    ',': 'punct', ';': 'punct', '.': 'punct',

    # лапки
    '"': 'quote',

    # коментарі
    '//': 'comment', '/*': 'comment', '*/': 'comment',

    # пропуски і перенесення
    ' ': 'ws', '\t': 'ws',
    '\n': 'eol', '\r': 'eol'
}

# Решту токенів визначаємо за заключним станом
tokStateTable = {
    6: 'id',
    2: 'intnum',
    4: 'floatnum',
    15: 'assign',
    18: 'rel_op',
    20: 'str',
    25: 'spec_sign',
    29: 'comment',
    31: 'comment',
    32: 'comment',
    34: 'newline'
}

# ---------------- Діаграма станів ----------------
stf = {
    (0, 'WhiteSpace'): 0,
    (0, 'Digit'): 1,
    (1, 'Digit'): 1,
    (1, 'other'): 2,
    (1, 'dot'): 35,         # крапка після цілої частини -> очікуємо цифру
    (35, 'Digit'): 3,       # в дробову частину
    (35, 'other'): 7,       # помилка: немає цифри після крапки
    (3, 'Digit'): 3,
    (3, 'other'): 4,        # floatnum

    (0, 'Letter'): 5,
    (5, 'Letter'): 5,
    (5, 'other'): 6,        # id/keyword/boolval

    (0, 'other'): 7,        # error

    (0, 'OrP'): 11, (11, 'OrP'): 12,  # ||
    (11, 'other'): 9,                 # помилка "одинарна |"

    (0, 'AndP'): 8, (8, 'AndP'): 10,  # &&
    (8, 'other'): 9,                  # помилка "одинарний &"

    (0, 'Quote'): 19, (19, 'other'): 19, (19, 'Quote'): 20,  # " ... "
    (19, 'NewLine'): 21,                                     # заборона переносу рядка в string

    (0, 'Equal'): 13, (13, 'other'): 15,  # =
    (13, 'More'): 16,                     # =>
    (13, 'Equal'): 14,                    # ==

    # відношення / логічні / плюс-мінус / ! тощо
    (0, 'Less'): 17, (0, 'More'): 17, (0, 'Am'): 17, (0, 'Exclam'): 17, (17, 'Equal'): 14,
    (17, 'other'): 18,

    # зірочка: *, **, *=
    (0, 'Star'): 22, (22, 'other'): 18,
    (22, 'Star'): 23,      # **
    (22, 'Equal'): 33,     # *=

    # коментарі: /* ... */ і //...
    (0, 'FSlash'): 26,
    (26, 'Star'): 27,      # початок блочного
    (27, 'other'): 27, (27, 'NewLine'): 27, (27, 'Star'): 28,
    (28, 'FSlash'): 29,    # кінець блочного
    (28, 'Star'): 28, (28, 'NewLine'): 27, (28, 'WhiteSpace'): 27, (28, 'other'): 27,

    (26, 'FSlash'): 30,    # початок однорядкового
    (30, 'other'): 30, (30, 'NewLine'): 31,

    (26, 'Equal'): 33,     # /=

    (26, 'other'): 32,     # сам по собі '/'

    # спецсимволи, дужки, тернарні, ^, крапка як пунктуація
    (0, 'SpecialSigns'): 24, (24, 'other'): 25,

    (0, 'NewLine'): 34,

    # крапка як пунктуація, якщо НЕ всередині числа
    (0, 'dot'): 24
}

initState = 0
F = {2, 4, 6, 7, 12, 9, 10, 21, 20, 15, 16, 14, 18, 23, 33, 32, 31, 29, 25, 34}
Fstar = {2, 4, 6, 15, 18, 32, 25}
Ferror = {7, 9, 21}

tableOfId = {}
tableOfConst = {}
tableOfSymb = {}

state = initState

# ---------------- Ввід програми ----------------
f = open('test.my_lang', 'r', encoding="utf-8")
sourceCode = f.read()
f.close()

FSuccess = ('Lexer', False)

lenCode = len(sourceCode) - 1
numLine = 1
numChar = -1
char = ''
lexeme = ''

# ---------------- Основний цикл ----------------
def lex():
  global state, numLine, char, lexeme, numChar, FSuccess
  try:
    while numChar < lenCode:
      char = nextChar()
      classCh = classOfChar(char)
      state = nextState(state, classCh)
      if is_final(state):
        processing()
      elif state == initState:
        lexeme = ''
      else:
        if char == "\n":
            numLine += 1
        lexeme += char
    print('Lexer: Lexical analysis completed successfully')
    FSuccess = ('Lexer', True)
  except SystemExit as e:
    print('Lexer: Program terminated with code {0}'.format(e))

# ---------------- Обробка фінальних станів ----------------
def processing():
    global state, lexeme, char, numLine, numChar, tableOfSymb

    # --- числа та ідентифікатори ---
    if state in (2, 4, 6):  # intnum, floatnum, id / keyword / boolval
        token = getToken(state, lexeme)

        # якщо це булева константа (true/false) — заносимо в tableOfConst
        if token == 'boolval':
            index = indexIdConst_for_bool_or_str('boolval', lexeme)
            print(f"{numLine:<3d} {lexeme:<10s} {token:<10s} {index:<5d}")
            tableOfSymb[len(tableOfSymb)+1] = (numLine, lexeme, token, index)
        elif token != 'keyword':  # id або число
            index = indexIdConst(state, lexeme)
            print(f"{numLine:<3d} {lexeme:<10s} {token:<10s} {index:<5d}")
            tableOfSymb[len(tableOfSymb)+1] = (numLine, lexeme, token, index)
        else:  # ключове слово
            print(f"{numLine:<3d} {lexeme:<10s} {token:<10s}")
            tableOfSymb[len(tableOfSymb)+1] = (numLine, lexeme, token, '')
        lexeme = ''
        numChar = putCharBack(numChar)  # зірочка
        state = initState
        return

    # --- оператор "=" ---
    if state == 15:
        token = getToken(state, lexeme)
        print(f"{numLine:<3d} {lexeme:<10s} {token:<10s}")
        tableOfSymb[len(tableOfSymb)+1] = (numLine, lexeme, token, '')
        lexeme = ''
        state = initState
        return

    # --- оператори з двох символів  ---
    if state in (10, 12, 14, 16, 23, 33):
        lexeme += char
        token = getToken(state, lexeme)
        print(f"{numLine:<3d} {lexeme:<10s} {token:<10s}")
        tableOfSymb[len(tableOfSymb)+1] = (numLine, lexeme, token, '')
        lexeme = ''
        state = initState
        return

    # --- дужки, тернарні, ^, пунктуація, інші спецсимволи ---
    if state == 25:
        token = getToken(state, lexeme)
        print(f'{numLine:<3d} {lexeme:<10s} {token:<10s}')
        tableOfSymb[len(tableOfSymb) + 1] = (numLine, lexeme, token, '')
        lexeme = ''
        numChar = putCharBack(numChar)
        state = initState
        return

    # --- рядкові константи ---
    if state == 20:
        token = getToken(state, lexeme)

        # Нормалізуємо: якщо випадково містить початкову лапку — знімемо її
        inner = lexeme[1:] if lexeme.startswith('"') else lexeme
        display_lexeme = '"' + inner + '"'

        # у tableOfConst зберігаємо ВНУТРІШНЄ значення без лапок
        index = indexIdConst_for_bool_or_str('str', inner)

        print(f"{numLine:<3d} {display_lexeme:<10s} {token:<10s} {index:<5d}")
        # у tableOfSymb покладемо маркер лапок, як у прикладі
        tableOfSymb[len(tableOfSymb)+1] = (numLine, '""', token, index)
        lexeme = ''
        state = initState
        return

    # --- коментарі однорядкові ---
    if state == 31:
        token = getToken(state, lexeme.strip())
        print(f"{numLine:<3d} {lexeme.strip():<10s} {token:<10s}")
        tableOfSymb[len(tableOfSymb) + 1] = (numLine, '//', token, '')
        lexeme = ''
        state = initState
        numLine += 1  # підвищуємо рядок саме тут
        return

    # --- кінець блочного коментаря ---
    if state == 29:
        lexeme += char  # додаємо '*/'
        token = getToken(state, lexeme)
        print(f"{numLine:<3d} {lexeme.strip():<10s} {token:<10s}")
        tableOfSymb[len(tableOfSymb) + 1] = (numLine, '/*/', token, '')
        lexeme = ''
        state = initState
        return

    # --- перенос строки ---
    if state == 34:
        lexeme = ''
        state = initState
        numLine = numLine + 1
        return

    # --- одиничні оператори (+, -, *, /, <, >, !, тощо) ---
    if state in (18, 32):
        token = getToken(state, lexeme)
        print(f"{numLine:<3d} {lexeme:<10s} {token:<10s}")
        tableOfSymb[len(tableOfSymb) + 1] = (numLine, lexeme, token, '')
        lexeme = ''
        numChar = putCharBack(numChar)
        state = initState
        return

    # --- помилки ---
    if state in Ferror:
        fail()

# ---------------- Помилки ----------------
def fail():
  global state, numLine, char
  print(numLine)
  if state == 7:
    print(f'ERROR 7: in line {numLine}  unexpected character  was met -> "{char}"')
    exit(7)
  if state == 9:
    print(f'ERROR 9: unexpected character  was met -> "{char}" in line {numLine}. SUGGESTED CORRECTION: might be symbols || or &&')
    exit(9)
  if state == 21:
    print(f'ERROR 21: unexpected character  was met -> "{char}" in line {numLine}. Multiline strings are not allowed.')
    exit(21)

# ---------------- Службові ----------------
def is_final(state):
  return state in F

def nextState(state, classCh):
  try:
    return stf[(state, classCh)]
  except KeyError:
    return stf[(state, 'other')]

def nextChar():
  global numChar
  numChar += 1
  return sourceCode[numChar]

def putCharBack(numChar):
  return numChar - 1

def classOfChar(char):
    # '_' дозволено у ідентифікаторах
    if char == '.':
        res = "dot"
    elif char.isalpha() or char == '_':
        res = "Letter"
    elif char.isdigit():
        res = "Digit"
    elif char == "\t" or char == " ":
        res = "WhiteSpace"
    elif char == "\n" or char == "\r":
        res = "NewLine"
    elif char == '=':
        res = "Equal"
    elif char == '>':
        res = "More"
    elif char == '<':
        res = "Less"
    elif char == '&':
        res = "AndP"
    elif char == '|':
        res = "OrP"
    elif char == '"':
        res = "Quote"
    elif char == '!':
        res = "Exclam"
    elif char == '*':
        res = "Star"
    elif char == '/':
        res = "FSlash"
    # спецсимволи: дужки, коми, двокрапка, крапка з комою, тернарний '?', степінь '^'
    elif char in '(){}[],:;?^':
        res = "SpecialSigns"
    elif char in '+-':
        res = 'Am'
    else:
        res = "other"
    return res

def getToken(state, lexeme):
  try:
    return tokenTable[lexeme]
  except KeyError:
    return tokStateTable[state]

def indexIdConst(state, lexeme):
  """Заносить id або числові константи у відповідні таблиці."""
  indx = 0
  if state == 6:  # ідентифікатор
    indx = tableOfId.get(lexeme)
    if indx is None:
      indx = len(tableOfId) + 1
      tableOfId[lexeme] = indx
  if state in (2, 4):  # числа
    obj = tableOfConst.get(lexeme)
    if obj is not None:
        indx = obj[1]
    else:
        indx = len(tableOfConst) + 1
        tableOfConst[lexeme] = (tokStateTable[state], indx)
  return indx

def indexIdConst_for_bool_or_str(ctype, value_lexeme):
  """Заносить true/false та рядки у tableOfConst (типи: 'boolval' або 'str')."""
  obj = tableOfConst.get(value_lexeme)
  if obj is not None:
      return obj[1]
  idx = len(tableOfConst) + 1
  tableOfConst[value_lexeme] = (ctype, idx)
  return idx

# ---------------- Запуск ----------------
lex()

# ---------------- Друк таблиць ----------------
print('-' * 100)
print('--- Lexical analysis tables ---')

def format_table_of_symb_tabular(symb_table):
    header = f"| {'Line':<10} | {'Lexeme':<35} | {'Token':<15} | {'Index':<5}"
    separator = "-" * len(header)
    output = f"{header}\n{separator}\n"
    for k, v in symb_table.items():
        line, lexeme, token, index = v
        index_str = str(index) if index != '' else ''
        row = f"| {str(line):<10} | {lexeme:<35} | {token:<15} | {index_str:<5}"
        output += f"{row}\n"
    return output

def format_id_const_tabular(data_table, name):
    if name == 'tableOfId':
        header = f"| {'Identifier':<15} | {'Index':<5}"
    else:  # tableOfConst
        header = f"| {'Constant':<15} | {'Type':<10} | {'Index':<5}"
    separator = "-" * len(header)
    output = f"\n{name}:\n{header}\n{separator}\n"
    k_list = list(data_table.keys())
    for k in k_list:
        v = data_table[k]
        if name == 'tableOfId':
            row = f"| {k:<15} | {v:<5}"
        else:
            c_type, c_index = v
            row = f"| {k:<15} | {c_type:<10} | {c_index:<5}"
        output += f"{row}\n"
    return output

print("\ntableOfSymb:")
print(format_table_of_symb_tabular(tableOfSymb))
print(format_id_const_tabular(tableOfId, 'tableOfId'))
print(format_id_const_tabular(tableOfConst, 'tableOfConst'))